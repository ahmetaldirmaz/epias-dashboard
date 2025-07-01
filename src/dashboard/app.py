#from __future__ import annotations

"""Streamlit entry point for the EPİAŞ Energy Analysis dashboard.

To run:
    streamlit run src/dashboard/app.py

Features:
    - Sidebar: date & organization filters
    - Main: navigates between generation and market data views

Session-cached DataFetcher ensures one authenticated API client per user session.
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------
import streamlit as st
# --- Streamlit config MUST come first ---
st.set_page_config(
    page_title="EPİAŞ Energy Analysis Dashboard",
    page_icon="⚡",
    layout="wide",
)

#st.write("✅ If you're seeing this, `set_page_config()` succeeded.")


import asyncio
import logging
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import List





# --- Patch import path so both `src` and project root are visible ---
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
for path in [str(ROOT), str(SRC)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Internal modules (now safe to import)
from api.auth import EPIASAuth
from api.client import EPIASClient
from config.settings import settings
from data.fetchers import DataFetcher
from dashboard.components import filters as ui_filters
from dashboard.pages import generation_data, market_data  # overview, bilateral TBD

#


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Session utilities
# ---------------------------------------------------------------------------

def _get_fetcher() -> DataFetcher:
    """Create (or reuse) a singleton DataFetcher bound to session."""
    if "_data_fetcher" not in st.session_state:
        auth = EPIASAuth()
        client = EPIASClient(auth)
        st.session_state["_data_fetcher"] = DataFetcher(client)
    return st.session_state["_data_fetcher"]

async def _load_organizations() -> List[dict]:
    """Fetch organizations for the sidebar picker."""
    fetcher = _get_fetcher()
    try:
        orgs = await fetcher.fetch_organizations()
        return [{"id": o.id, "name": o.name} for o in orgs]
    except Exception as e:
        st.error(f"Failed to fetch organizations: {e}")
        logger.exception("Organization fetch failed")
        return []

# ---------------------------------------------------------------------------
# Sidebar UI
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("⚡ EPİAŞ Analysis")

    # Date filter
    st.subheader("📅 Date range")
    start_d, end_d = ui_filters.render_date_filter(
        key_prefix="main_date_filter",
        default_days_back=7,
    )

    # Organization filter
    st.subheader("🏢 Organizations")
    if st.button("🔄 Load / Refresh list"):
        with st.spinner("Fetching organization list..."):
            st.session_state["_org_list"] = asyncio.run(_load_organizations())

    org_list = st.session_state.get("_org_list", [])
    if org_list:
        names = [o["name"] for o in org_list]
        chosen = st.multiselect("Select organizations", names, key="main_org_filter")
        selected_org_ids = [o["id"] for o in org_list if o["name"] in chosen]
    else:
        st.info("Click the button above to fetch organizations.")
        selected_org_ids = []

    st.markdown("---")
    st.caption("Data pulled from EPİAŞ Transparency Platform")

# Save filters in session state
st.session_state["filters"] = {
    "start": start_d,
    "end": end_d,
    "org_ids": selected_org_ids,
}

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

st.title("EPİAŞ Energy Data Dashboard")

if not selected_org_ids:
    st.warning("Select at least one organization to continue.")
    st.stop()

# Tab navigation
tab_market, tab_generation = st.tabs(["💹 Market Data", "⚡ Generation Data"])

with tab_market:
    market_data.run()

with tab_generation:
    generation_data.run()

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.markdown("---")
st.caption(
    f"Data source: EPİAŞ Transparency Platform — Last refresh: {datetime.now():%Y-%m-%d %H:%M:%S}"
)
