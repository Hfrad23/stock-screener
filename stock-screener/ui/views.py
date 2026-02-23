from typing import List, Optional

import pandas as pd
import streamlit as st

from config.settings import ValuationResult
from ui.components import render_stock_expander

_SIGNAL_EMOJI = {
    "undervalued":       "🟢",
    "fair":              "🟡",
    "overvalued":        "🔴",
    "insufficient_data": "⚪",
}

_ROW_BG = {
    "🟢": "background-color: rgba(0, 200, 83, 0.12);",
    "🟡": "background-color: rgba(255, 214, 0, 0.12);",
    "🔴": "background-color: rgba(255, 82, 82, 0.12);",
    "⚪": "",
}


def _color_row(row: "pd.Series") -> list:
    """Return a list of CSS strings for one row, keyed to its Signal value."""
    bg = _ROW_BG.get(row["Signal"], "")
    return [bg] * len(row)


def _fmt(val, fmt_str: str, prefix: str = "", suffix: str = "") -> str:
    if val is None:
        return "N/A"
    try:
        return f"{prefix}{val:{fmt_str}}{suffix}"
    except (TypeError, ValueError):
        return "N/A"


def render_index_tab(results: List[ValuationResult], index_name: str) -> None:
    if not results:
        st.warning(f"No data available for {index_name}.")
        return

    rows = []
    for i, r in enumerate(results, 1):
        rows.append({
            "Rank":      i,
            "Ticker":    r.ticker,
            "Company":   r.company_name[:30],
            "Sector":    r.sector[:22],
            "Price":     _fmt(r.price, ".2f", "$"),
            "DCF Value": _fmt(r.dcf_value, ".2f", "$"),
            "MoS":       _fmt(r.margin_of_safety, ".1%") if r.margin_of_safety is not None else "N/A",
            "P/E":       _fmt(r.pe_ratio, ".1f"),
            "Fwd P/E":   _fmt(r.forward_pe, ".1f"),
            "P/FCF":     _fmt(r.p_fcf, ".1f"),
            "EV/EBITDA": _fmt(r.ev_ebitda, ".1f"),
            "PEG":       _fmt(r.peg_ratio, ".2f"),
            "Profile":   {"growth": "G", "value": "V", "blend": "B"}.get(r.growth_profile, "B"),
            "5Y Est.":   _fmt(r.five_yr_price, ".2f", "$"),
            "5Y CAGR":   _fmt(r.five_yr_cagr, ".1%") if r.five_yr_cagr is not None else "N/A",
            "Signal":    _SIGNAL_EMOJI.get(r.signal, "⚪"),
            "Score":     f"{r.composite_score:.3f}",
        })

    df = pd.DataFrame(rows)
    styled = df.style.apply(_color_row, axis=1)
    st.dataframe(styled, hide_index=True, use_container_width=True)

    st.markdown("---")
    st.subheader("Stock Details")
    for r in results:
        render_stock_expander(r)
