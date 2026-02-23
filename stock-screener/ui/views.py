from typing import List

import pandas as pd
import streamlit as st

from config.settings import ValuationResult
from ui.components import render_stock_expander, render_metric_legend

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

# Column header tooltip definitions for the main table
_COL_HELP = {
    "Rank":      "Rank by composite score within this index (highest score = rank 1).",
    "Ticker":    "Stock ticker symbol.",
    "Company":   "Company name.",
    "Sector":    "GICS sector classification.",
    "Price":     "Current stock price (refreshes every 5 minutes).",
    "DCF Value": "Discounted Cash Flow intrinsic value per share. Projects 5 years of free cash flow and discounts back at WACC. Adjust WACC and growth rate in the sidebar.",
    "MoS":       "Margin of Safety — how far the current price is below the DCF intrinsic value. Positive = trading below intrinsic value (good). Green >25%, yellow -10% to 25%, red below -10%.",
    "P/E":       "Price-to-Earnings (trailing 12 months). Lower = cheaper relative to profits. Value: green <20. Growth: green <35.",
    "Fwd P/E":   "Forward Price-to-Earnings based on next 12 months analyst earnings estimates. A falling forward P/E (vs trailing) indicates expected earnings growth.",
    "P/FCF":     "Price-to-Free-Cash-Flow. Market cap divided by trailing FCF. Often more reliable than P/E. Value: green <20. Growth: green <30.",
    "EV/EBITDA": "Enterprise Value / EBITDA. Accounts for debt in the valuation — useful for comparing companies with different balance sheets. Value: green <15. Growth: green <25.",
    "PEG":       "Price/Earnings-to-Growth. P/E divided by earnings growth rate. Accounts for the fact that fast growers deserve higher P/E. Below 1.0 = potentially undervalued vs growth.",
    "Profile":   "Growth / Value / Blend classification. G = growth stock (adjusted scoring), V = value stock (traditional scoring), B = blend. Based on revenue growth, earnings growth, and P/E level.",
    "5Y Est.":   "5-year price estimate. Projects EPS forward at the earnings growth rate (capped 25%/yr) and applies the forward P/E as an exit multiple.",
    "5Y CAGR":   "Implied compound annual return from today's price to the 5-year estimate. Useful for comparing opportunity cost across names.",
    "Signal":    "Overall valuation signal based on the fraction of metrics that score green. ≥55% green = Undervalued, <25% green = Overvalued, otherwise Fair.",
    "Score":     "Composite score 0–1. Weighted average of DCF, Fundamentals, and Quality pillars. Growth stocks use adjusted weights and include revenue/earnings growth in quality. Higher = more attractive.",
}


def _color_row(row: "pd.Series") -> list:
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

    col_config = {
        col: st.column_config.TextColumn(col, help=help_text)
        for col, help_text in _COL_HELP.items()
        if col in df.columns
    }

    st.dataframe(styled, column_config=col_config, hide_index=True, use_container_width=True)

    st.markdown("---")
    st.subheader("Stock Details")
    for r in results:
        render_stock_expander(r)

    st.markdown("---")
    render_metric_legend()
