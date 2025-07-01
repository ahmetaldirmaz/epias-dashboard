from __future__ import annotations

"""Streamlit page: Market Data

Shows day‑ahead (GÖP/PTF), imbalance (SMF / SMP), and bilateral contract prices
for the selected organisations and date range.

Relies on:
    • api.auth.EPIASAuth – to fetch / refresh TGTs
    • api.client.EPIASClient – low‑level HTTP wrapper
    • data.fetchers.DataFetcher – high‑level async data retrieval
    • data.processors.DataProcessor – helper analytics (stats, aggregations)
    • dashboard.components.filters – reusable sidebar widgets
    • dashboard.components.charts – Plotly chart helpers

Assumptions
-----------
▪ DataFetcher exposes async methods:
        async fetch_market_data(org_id: int, start: date, end: date) -> pd.DataFrame
  returning a tidy DataFrame with at least these columns:
        ['date', 'ptf', 'smp']

▪ components.charts provides:
        line_chart(df, x, y, title, y_axis_title=None, legend=True)
        bar_chart(df, x, y, title, y_axis_title=None, legend=True)
  that gracefully handle empty dataframes.

If any of these assumptions diverge from reality, tweak accordingly.
"""

from datetime import date, timedelta
import asyncio
from typing import Dict, List

import pandas as pd
import streamlit as st

from src.api.auth import EPIASAuth
from src.api.epias import EPIASClient
from src.data.fetchers import DataFetcher
from src.data.processors import DataProcessor
from src.dashboard.components import filters as ui_filters
from src.dashboard.components import charts as ui_charts

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_data_fetcher() -> DataFetcher:
    """Return a cached **DataFetcher** instance stored in Streamlit session state."""

    if "_data_fetcher" not in st.session_state:
        auth = EPIASAuth()
        client = EPIASClient(auth=auth)
        st.session_state["_data_fetcher"] = DataFetcher(client=client)

    return st.session_state["_data_fetcher"]


async def _fetch_market_data_for_orgs(
    fetcher: DataFetcher, org_ids: List[int], start: date, end: date
) -> Dict[int, pd.DataFrame]:
    """Fetch market data concurrently for all selected organisations."""

    async def _fetch(org_id: int):
        try:
            return org_id, await fetcher.fetch_market_data(org_id, start, end)
        except Exception as exc:  # noqa: BLE001 – surface every failure
            st.error(f"Failed to fetch data for org {org_id}: {exc}")
            return org_id, pd.DataFrame()

    tasks = [_fetch(oid) for oid in org_ids]
    results = await asyncio.gather(*tasks)
    return {oid: df for oid, df in results}


# ---------------------------------------------------------------------------
# Page logic
# ---------------------------------------------------------------------------

def run():  # Streamlit will call this from **dashboard/app.py**
    st.title("📈 Market Data – GÖP / SMF / Bilateral Prices")

    # Sidebar filters --------------------------------------------------------
    with st.sidebar:
        st.header("Filters ▾")
        org_ids = ui_filters.organization_filter(key="market_org_filter")
        start_date, end_date = ui_filters.date_range_filter(
            key="market_date_filter",
            default_start=date.today() - timedelta(days=30),
            default_end=date.today(),
        )

        if start_date > end_date:
            st.error("Start date must be ≤ end date.")
            st.stop()

    if not org_ids:
        st.info("Select at least one organisation to display data.")
        st.stop()

    # Retrieve / cache data ---------------------------------------------------
    fetcher = _get_data_fetcher()

    with st.spinner("Fetching market data …"):
        data_by_org = asyncio.run(
            _fetch_market_data_for_orgs(fetcher, org_ids, start_date, end_date)
        )

    # Merge into a single DataFrame with a column multi‑index: (org_id, metric)
    frames: List[pd.DataFrame] = []
    for oid, df in data_by_org.items():
        if df.empty:
            continue
        df = df.set_index("date").sort_index()
        # Prefix columns with the organisation ID to avoid collisions
        df = df.add_prefix(f"{oid}::")
        frames.append(df)

    if not frames:
        st.warning("No market data returned for the chosen inputs.")
        st.stop()

    merged = pd.concat(frames, axis=1, join="outer")
    merged.index.name = "Date"

    # ---------------------------------------------------------------------
    # Visualisations
    # ---------------------------------------------------------------------

    st.subheader("Average PTF (Day‑Ahead) Price")
    ptf_cols = [c for c in merged.columns if c.endswith("::ptf")]
    if ptf_cols:
        chart_df = merged[ptf_cols].rename(columns=lambda c: c.split("::")[0])
        ui_charts.line_chart(
            chart_df.reset_index(),
            x="Date",
            y=chart_df.columns.tolist(),
            title="PTF (TL/MWh)",
            y_axis_title="TL/MWh",
        )
    else:
        st.info("PTF columns not found in dataset.")

    st.subheader("Average SMP (Imbalance) Price")
    smp_cols = [c for c in merged.columns if c.endswith("::smp")]
    if smp_cols:
        chart_df = merged[smp_cols].rename(columns=lambda c: c.split("::")[0])
        ui_charts.line_chart(
            chart_df.reset_index(),
            x="Date",
            y=chart_df.columns.tolist(),
            title="SMP (TL/MWh)",
            y_axis_title="TL/MWh",
        )
    else:
        st.info("SMP columns not found in dataset.")

    # Basic statistics ------------------------------------------------------
    st.subheader("Price Statistics")
    stats_df = (
        merged[[*ptf_cols, *smp_cols]]
        .describe(percentiles=[0.25, 0.5, 0.75])
        .T
        .sort_index()
    )
    st.dataframe(stats_df, use_container_width=True)


# When Streamlit executes `streamlit run dashboard/app.py`, the parent
# bootstraps the page registry. But allowing module‑level execution lets us
# debug quickly via `python -m dashboard.pages.market_data`.
if __name__ == "__main__":
    import sys

    # Quick‑and‑dirty CLI for standalone testing ---------------------------
    if len(sys.argv) >= 3:
        org_id_arg = int(sys.argv[1])
        days = int(sys.argv[2])
        _fetcher = _get_data_fetcher()
        _start = date.today() - timedelta(days=days)
        _end = date.today()
        df_demo = asyncio.run(
            _fetcher.fetch_market_data(org_id_arg, _start, _end)  # type: ignore[arg-type]
        )
        print(df_demo.head())
    else:
        print("Usage: python -m dashboard.pages.market_data <ORG_ID> <DAYS>")
