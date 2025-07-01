from __future__ import annotations

"""Reusable UI filter components for the EPİAŞ Streamlit dashboard."""

from datetime import date, timedelta
from typing import List, Tuple, Optional, Dict

import streamlit as st


def render_date_filter(
    key_prefix: str = "date",
    default_days_back: int = 7,
    show_presets: bool = True
) -> Tuple[date, date]:
    """Render a date range selector with optional preset buttons."""
    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "Start Date",
            value=date.today() - timedelta(days=default_days_back),
            max_value=date.today(),
            key=f"{key_prefix}_start"
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=date.today(),
            max_value=date.today(),
            key=f"{key_prefix}_end"
        )

    if show_presets:
        st.markdown("**Quick Select:**")
        col1, col2, col3, col4 = st.columns(4)
        if col1.button("Today", key=f"{key_prefix}_today"):
            start_date, end_date = date.today(), date.today()
        if col2.button("Last 7 Days", key=f"{key_prefix}_7days"):
            start_date, end_date = date.today() - timedelta(days=7), date.today()
        if col3.button("Last 30 Days", key=f"{key_prefix}_30days"):
            start_date, end_date = date.today() - timedelta(days=30), date.today()
        if col4.button("This Month", key=f"{key_prefix}_month"):
            start_date = date.today().replace(day=1)
            end_date = date.today()

    if start_date > end_date:
        st.error("Start date must be before end date.")
        return date.today() - timedelta(days=default_days_back), date.today()

    return start_date, end_date


def render_organization_filter(
    organizations: List[Dict[str, any]],
    key: str = "org_filter",
    multi_select: bool = True,
    show_all_option: bool = True
) -> List[int]:
    """Render a dynamic organization filter with optional multi-select."""
    if not organizations:
        st.warning("No organizations available.")
        return []

    org_map = {org["name"]: org["id"] for org in organizations}
    org_names = list(org_map.keys())

    if show_all_option and multi_select:
        select_all = st.checkbox("Select All Organizations", key=f"{key}_all")
        selected_names = org_names if select_all else st.multiselect(
            "Select Organizations", options=org_names, key=key)
    elif multi_select:
        selected_names = st.multiselect(
            "Select Organizations", options=org_names, key=key)
    else:
        selected = st.selectbox("Select Organization", options=org_names, key=key)
        selected_names = [selected] if selected else []

    return [org_map[name] for name in selected_names]


def render_generation_type_filter(
    key: str = "gen_type",
    multi_select: bool = True
) -> List[str]:
    """Filter for generation types."""
    types = [
        "Rüzgar", "Güneş", "Barajlı", "Akarsu", "Doğal Gaz",
        "Linyit", "İthal Kömür", "Nükleer", "Jeotermal",
        "Biyokütle", "Diğer"
    ]
    if multi_select:
        return st.multiselect("Generation Types", options=types, default=types[:3], key=key)
    else:
        selected = st.selectbox("Generation Type", options=types, key=key)
        return [selected] if selected else []


def render_market_filter(
    key: str = "market",
    show_all: bool = True
) -> List[str]:
    """Filter for market types."""
    markets = {
        "GÖP": "Gün Öncesi Piyasası (Day Ahead Market)",
        "GİP": "Gün İçi Piyasası (Intraday Market)",
        "DGP": "Dengeleme Güç Piyasası (Balancing Power Market)"
    }

    if show_all and st.checkbox("All Markets", value=True, key=f"{key}_all"):
        return list(markets.keys())

    return st.multiselect(
        "Select Markets",
        options=list(markets.keys()),
        format_func=lambda x: f"{x} - {markets[x]}",
        default=list(markets.keys()),
        key=key
    )


def render_period_filter(
    key: str = "period",
    include_hourly: bool = True
) -> str:
    """Filter for aggregation period (Hourly/Daily/Weekly/Monthly)."""
    options = ["Hourly", "Daily", "Weekly", "Monthly"] if include_hourly else ["Daily", "Weekly", "Monthly"]
    return st.radio("Aggregation Period", options=options, horizontal=True, key=key)


def render_export_options(
    data_name: str,
    key: str = "export"
) -> Optional[str]:
    """Export format selector wrapped in expandable section."""
    with st.expander("Export Options"):
        col1, col2 = st.columns([3, 1])

        with col1:
            export_format = st.selectbox(
                "Export Format",
                options=["Excel", "CSV", "JSON"],
                key=f"{key}_format"
            )

        with col2:
            if st.button("Export", key=f"{key}_button"):
                return export_format

    return None
