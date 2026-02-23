import streamlit as st
from config.settings import (
    ValuationResult,
    COLOR_GREEN, COLOR_YELLOW, COLOR_RED, COLOR_GRAY,
)

_SIGNAL_COLORS = {
    "green":  COLOR_GREEN,
    "yellow": COLOR_YELLOW,
    "red":    COLOR_RED,
    "na":     COLOR_GRAY,
}

_BADGE_CONFIG = {
    "undervalued":       ("UNDERVALUED", COLOR_GREEN),
    "fair":              ("FAIR VALUE",  COLOR_YELLOW),
    "overvalued":        ("OVERVALUED",  COLOR_RED),
    "insufficient_data": ("INSUFFICIENT DATA", COLOR_GRAY),
}


def signal_badge(signal: str) -> str:
    label, color = _BADGE_CONFIG.get(signal, ("N/A", COLOR_GRAY))
    return f'<span style="color:{color}; font-weight:bold; font-size:0.95em;">&#9679; {label}</span>'


def _dot(signal: str) -> str:
    color = _SIGNAL_COLORS.get(signal, COLOR_GRAY)
    return f'<span style="color:{color};">&#9679;</span>'


def _row(label: str, value, signal: str, fmt: str = "") -> str:
    """Format a single labeled metric row with a colored signal dot."""
    dot = _dot(signal)
    if value is None:
        display = "N/A"
    elif fmt == "pct":
        display = f"{value:.1%}"
    elif fmt == "pct2":
        display = f"{value:.2%}"
    elif fmt == "x1":
        display = f"{value:.1f}x"
    elif fmt == "x2":
        display = f"{value:.2f}x"
    elif fmt == "dollar":
        display = f"${value:.2f}"
    elif fmt == "dollar_large":
        display = f"${value:,.0f}"
    elif fmt == "2f":
        display = f"{value:.2f}"
    elif fmt == "1f":
        display = f"{value:.1f}"
    else:
        display = str(value)
    return f"{dot} <b>{label}:</b> {display}"


def _plain(label: str, value, fmt: str = "") -> str:
    """Format a metric row without a signal dot (informational only)."""
    if value is None:
        display = "N/A"
    elif fmt == "pct":
        display = f"{value:.1%}"
    elif fmt == "pct2":
        display = f"{value:.2%}"
    elif fmt == "x1":
        display = f"{value:.1f}x"
    elif fmt == "x2":
        display = f"{value:.2f}x"
    elif fmt == "dollar":
        display = f"${value:.2f}"
    elif fmt == "2f":
        display = f"{value:.2f}"
    elif fmt == "1f":
        display = f"{value:.1f}"
    else:
        display = str(value)
    return f"<b>{label}:</b> {display}"


def render_stock_expander(result: ValuationResult) -> None:
    signal_emoji = {"undervalued": "🟢", "fair": "🟡", "overvalued": "🔴"}.get(result.signal, "⚪")
    header = (
        f"{signal_emoji}  {result.ticker} — {result.company_name}"
        f"  |  Score: {result.composite_score:.3f}"
        f"  |  {result.sector}"
    )

    with st.expander(header):
        sig = result.metric_signals

        col1, col2, col3 = st.columns(3)

        # ── Column 1: Valuation Multiples ─────────────────────────────────────
        with col1:
            st.markdown("**Valuation Multiples**")
            for html in [
                _row("P/E (TTM)",    result.pe_ratio,   sig.get("pe", "na"),         "1f"),
                _row("Forward P/E",  result.forward_pe, sig.get("forward_pe", "na"), "1f"),
                _row("P/FCF",        result.p_fcf,      sig.get("p_fcf", "na"),      "1f"),
                _row("EV/EBITDA",    result.ev_ebitda,  sig.get("ev_ebitda", "na"),  "1f"),
                _row("PEG Ratio",    result.peg_ratio,  sig.get("peg", "na"),        "2f"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

            st.markdown("<br>**Margins**", unsafe_allow_html=True)
            for html in [
                _plain("Operating Margin", result.operating_margins, "pct"),
                _plain("Net Margin",       result.profit_margins,    "pct"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

        # ── Column 2: DCF & Quality ───────────────────────────────────────────
        with col2:
            st.markdown("**DCF Analysis**")
            for html in [
                _plain("Current Price", result.price,         "dollar"),
                _plain("DCF Value",     result.dcf_value,     "dollar"),
                _row("Margin of Safety",
                     result.margin_of_safety, sig.get("mos", "na"), "pct"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

            st.markdown("<br>**5-Year Estimate**", unsafe_allow_html=True)
            growth_note = (
                f"{result.five_yr_growth_used:.1%} growth, "
                f"{result.forward_pe:.1f}x exit P/E"
                if result.five_yr_growth_used is not None and result.forward_pe
                else "EPS projection"
            )
            for html in [
                _plain(f"Est. Price ({growth_note})", result.five_yr_price, "dollar"),
                _plain("Implied 5Y CAGR",             result.five_yr_cagr,  "pct"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

            st.markdown("<br>**Quality**", unsafe_allow_html=True)
            for html in [
                _row("Return on Equity", result.roe,           sig.get("roe", "na"),         "pct"),
                _row("Debt / Equity",    result.debt_to_equity, sig.get("debt_equity", "na"), "x2"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

        # ── Column 3: Growth & Outlook ────────────────────────────────────────
        with col3:
            st.markdown("**Growth (YoY)**")
            for html in [
                _plain("Revenue Growth",  result.revenue_growth,  "pct"),
                _plain("Earnings Growth", result.earnings_growth, "pct"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

            st.markdown("<br>**Analyst Consensus**", unsafe_allow_html=True)
            for html in [
                _row("Analyst Upside", result.analyst_upside, sig.get("analyst_upside", "na"), "pct"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

            st.markdown("<br>**Risk**", unsafe_allow_html=True)
            for html in [
                _plain("Beta (vs S&P 500)", result.beta, "2f"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

            st.markdown("<br>**Overall Signal**", unsafe_allow_html=True)
            st.markdown(signal_badge(result.signal), unsafe_allow_html=True)
