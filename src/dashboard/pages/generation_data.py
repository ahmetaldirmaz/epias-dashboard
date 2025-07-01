from __future__ import annotations

"""Streamlit page: Generation Data

Visualises *Realtime Generation* and *KGÜP* (Confirmed Day-Ahead Generation
Plan) figures for the selected organisations and date range.

Architecture assumptions (consistent with market_data.py):
---------------------------------------------------------
• **DataFetcher** exposes two async methods:
      - fetch_generation_data(org_id: int, start: date, end: date) -> pd.DataFrame
      - fetch_kgup_data(org_id: int, start: date, end: date) -> pd.DataFrame

  Each returns a tidy DataFrame with at minimum:
      ['date', 'value', 'generationType']
  plus optional ['powerPlantName', 'uevcbName'] cols for drill‑down.

• `dashboard.components.charts` provides:
      area_chart(df, x, y, color, title, y_axis_title=None)
      line_chart(df, x, y, title, y_axis_title=None, legend=True)
  (area_chart is a thin wrapper around Plotly Express stacked‑area.)

If the actual helper names differ, map them accordingly in **charts.py** or
update imports below.
"""

from datetime import date, timedelta
import asyncio
from typing import Dict, List

import pandas as pd
import streamlit as st

from api.auth import EPIASAuth
from api.client import EPIASClient
from data.fetchers import DataFetcher
from dashboard.components import filters as ui_filters
from dashboard.components import charts as ui_charts

# ---------------------------------------------------------------------------
# Session helpers
# ---------------------------------------------------------------------------

def _get_fetcher() -> DataFetcher:
    if "_data_fetcher" not in st.session_state:
        auth = EPIASAuth()
        client = EPIASClient(auth=auth)
        st.session_state["_data_fetcher"] = DataFetcher(client)
    return st.session_state["_data_fetcher"]


async def _gather_generation(
    fetcher: DataFetcher,
    org_ids: List[int],
    start: date,
    end: date,
    dataset: str,  # "realtime" | "kgup"
) -> Dict[int, pd.DataFrame]:
    """Concurrent downloads for each organisation."""

    async def _one(oid: int):
        try:
            if dataset == "realtime":
                df = await fetcher.fetch_generation_data(oid, start, end)
            else:
                df = await fetcher.fetch_kgup_data(oid, start, end)  # type: ignore[attr-defined]
            return oid, df
        except Exception as exc:  # noqa: BLE001
            st.error(f"{dataset.title()} fetch failed for org {oid}: {exc}")
            return oid, pd.DataFrame()

    tasks = [_one(oid) for oid in org_ids]
    results = await asyncio.gather(*tasks)
    return {oid: df for oid, df in results}


# ---------------------------------------------------------------------------
# Main page
# ---------------------------------------------------------------------------

def run():
    st.title("⚡ Generation Data (Realtime & KGÜP)")

    # Sidebar filters --------------------------------------------------------
    with st.sidebar:
        st.header("Filters ▾")
        org_ids = ui_filters.organization_filter(key="gen_org_filter")
        start_d, end_d = ui_filters.date_range_filter(
            key="gen_date_filter",
            default_start=date.today() - timedelta(days=7),
            default_end=date.today(),
        )
        dataset = st.radio(
            "Dataset",
            options={"Realtime": "realtime", "KGÜP": "kgup"},
            horizontal=True,
            index=0,
            key="gen_dataset_sel",
        )

        agg_choice = st.selectbox(
            "Aggregation level",
            options=["Hourly", "Daily"],
            index=0,
            key="gen_agg_level",
        )

    if not org_ids:
        st.info("Select at least one organisation.")
        st.stop()

    if start_d > end_d:
        st.error("Start date must be ≤ end date.")
        st.stop()

    fetcher = _get_fetcher()

    with st.spinner("Fetching generation data …"):
        data_by_org = asyncio.run(
            _gather_generation(fetcher, org_ids, start_d, end_d, dataset)
        )

    frames = []
    for oid, df in data_by_org.items():
        if df.empty:
            continue
        # Ensure datetime index & rename value column by org id
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], utc=True)
        if agg_choice == "Daily":
            df = df.groupby([pd.Grouper(key="date", freq="D"), "generationType"], as_index=False)[
                "value"
            ].sum()
        df = df.rename(columns={"value": f"{oid}"})
        frames.append(df)

    if not frames:
        st.warning("No data received for the chosen filters.")
        st.stop()

    merged = pd.concat(frames, axis=0)

    # ---------------------------------------------------------------------
    # Visual‑isations
    # ---------------------------------------------------------------------

    # 1. Stacked area – generation mix per org (aggregated across types)
    st.subheader("Generation Mix (Stacked by Type)")

    # Build a DataFrame: date x generationType -> sum across orgs
    mix_df = (
        merged.groupby(["date", "generationType"])[merged.columns.difference(["date", "generationType"])].sum()
        .reset_index()
    )

    if mix_df.empty:
        st.info("No mix data to display.")
    else:
        ui_charts.area_chart(
            mix_df,
            x="date",
            y="value" if "value" in mix_df.columns else merged.columns[-1],
            color="generationType",
            title="Stacked Generation by Type (MWh)",
            y_axis_title="MWh",
        )

    # 2. Line chart – total generation per org
    st.subheader("Total Generation per Organisation")
    total_df = (
        merged.set_index("date")
        .groupby(pd.Grouper(freq="H" if agg_choice == "Hourly" else "D"))[merged.columns.difference(["generationType"])]
        .sum()
    )
    total_df.index.name = "Date"

    ui_charts.line_chart(
        total_df.reset_index(),
        x="Date",
        y=total_df.columns.tolist(),
        title="Total Generation (MWh)",
        y_axis_title="MWh",
        legend=True,
    )

    # 3. Statistics --------------------------------------------------------
    st.subheader("Generation Statistics")
    stats = total_df.describe(percentiles=[0.25, 0.5, 0.75]).T
    st.dataframe(stats, use_container_width=True)


# Stand‑alone CLI entry -------------------------------------------------------
if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 4:
        _org_id = int(sys.argv[1])
        _days = int(sys.argv[2])
        _ds = sys.argv[3]  # realtime|kgup
        _fch = _get_fetcher()
        _s = date.today() - timedelta(days=_days)
        _e = date.today()
        _dfout = asyncio.run(
            _fch.fetch_generation_data(_org_id, _s, _e)
            if _ds == "realtime"
            else _fch.fetch_kgup_data(_org_id, _s, _e)  # type: ignore[attr-defined]
        )
        print(_dfout.head())
    else:
        print("Usage: python -m dashboard.pages.generation_data <ORG_ID> <DAYS> <realtime|kgup>")
