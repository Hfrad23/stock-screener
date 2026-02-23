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

_PROFILE_BADGE = {
    "growth": '<span style="background:#1a3a5c; color:#60b4ff; font-size:0.78em; padding:2px 7px; border-radius:4px; font-weight:bold;">GROWTH</span>',
    "value":  '<span style="background:#1a3a2a; color:#60d48a; font-size:0.78em; padding:2px 7px; border-radius:4px; font-weight:bold;">VALUE</span>',
    "blend":  '<span style="background:#2a2a2a; color:#aaaaaa; font-size:0.78em; padding:2px 7px; border-radius:4px; font-weight:bold;">BLEND</span>',
}

# ── Metric definitions (used as hover tooltips on every labeled row) ──────────
METRIC_DEFS = {
    "P/E (TTM)": (
        "Price-to-Earnings (Trailing 12 Months). Current stock price divided by the past "
        "12 months of earnings per share. A lower P/E means you're paying less for each "
        "dollar of profit. Value threshold: green <20, yellow 20–35. "
        "Growth threshold: green <35, yellow 35–60."
    ),
    "Forward P/E": (
        "Price divided by next 12 months of estimated earnings (analyst forecasts). "
        "A forward P/E lower than the trailing P/E signals expected earnings growth. "
        "Generally more useful than trailing P/E for fast-growing companies."
    ),
    "P/FCF": (
        "Price-to-Free-Cash-Flow. Market cap divided by trailing twelve month free cash flow "
        "(operating cash flow minus capital expenditures). Many investors prefer FCF over "
        "earnings because it's harder to manipulate and shows actual cash generation. "
        "Value threshold: green <20. Growth threshold: green <30."
    ),
    "EV/EBITDA": (
        "Enterprise Value divided by Earnings Before Interest, Taxes, Depreciation & "
        "Amortization. EV includes debt and cash, making it useful for comparing companies "
        "with very different capital structures. Lower is cheaper. "
        "Value threshold: green <15. Growth threshold: green <25."
    ),
    "PEG Ratio": (
        "Price/Earnings-to-Growth. The P/E ratio divided by the earnings growth rate. "
        "Accounts for the fact that fast-growing companies deserve higher P/E ratios. "
        "A PEG below 1.0 is considered undervalued relative to growth (Peter Lynch's rule). "
        "Value threshold: green <1.5. Growth threshold: green <1.0 (tighter — growth "
        "investors expect this discipline)."
    ),
    "Operating Margin": (
        "Operating income as a percentage of revenue. Measures how much profit a company "
        "makes from its core business operations before interest and taxes. "
        "Higher margins indicate a stronger competitive position or pricing power."
    ),
    "Net Margin": (
        "Net income as a percentage of revenue — the bottom line after all expenses, "
        "interest, and taxes. Shows how much of every dollar in revenue becomes profit."
    ),
    "Current Price": (
        "The most recent market price per share. Refreshes every 5 minutes via the "
        "Refresh Prices button."
    ),
    "DCF Value": (
        "Discounted Cash Flow intrinsic value per share. Projects free cash flow forward "
        "5 years at the company's historical FCF growth rate (capped at 25%), calculates "
        "a terminal value, then discounts everything back to today using the WACC "
        "(cost of capital, default 10%). This is an estimate — small changes in growth "
        "rate or WACC produce large changes in the output. Adjust in the sidebar."
    ),
    "Margin of Safety": (
        "The percentage discount between the DCF intrinsic value and the current price. "
        "A 25% margin of safety means the stock trades 25% below its estimated intrinsic "
        "value, providing a buffer against estimation error. Popularized by Benjamin Graham. "
        "Green >25%, yellow -10% to 25%, red below -10% (stock trading above DCF value)."
    ),
    "5-Year Estimate": (
        "Projected stock price in 5 years using EPS projection. Formula: current EPS × "
        "(1 + growth rate)^5 × exit P/E multiple. Growth rate = earnings growth capped at "
        "25%/yr to avoid compounding one exceptional year. Exit multiple = forward P/E "
        "(capped at 40x). This is a rough scenario estimate, not a price target."
    ),
    "Implied 5Y CAGR": (
        "The annualized compound return you would earn if the stock hits the 5-year "
        "price estimate. Useful for comparing opportunity cost across different stocks. "
        "Formula: (5Y estimate / current price)^(1/5) - 1."
    ),
    "Return on Equity": (
        "Net income divided by shareholders' equity. Measures how efficiently management "
        "generates profit from the capital shareholders have invested. Warren Buffett looks "
        "for companies with sustained ROE above 15%. Green >15%, yellow 8–15%, red <8%."
    ),
    "Debt / Equity": (
        "Total debt divided by shareholders' equity (stored as a ratio; e.g. 1.0x = "
        "equal debt and equity). Higher ratios mean more financial leverage and risk, "
        "though acceptable levels vary by industry. Financial companies naturally carry "
        "high D/E and should be interpreted differently. Green <0.5x, yellow 0.5–2.0x, "
        "red >2.0x."
    ),
    "Revenue Growth": (
        "Year-over-year revenue growth rate. For growth-classified stocks, this is a "
        "scored quality metric — sustained high revenue growth is a key indicator of "
        "competitive strength and market share gains. Green >20%, yellow 10–20%, red <10%."
    ),
    "Earnings Growth": (
        "Year-over-year earnings per share growth rate. Alongside revenue growth, "
        "strong earnings growth with expanding margins signals operating leverage. "
        "For growth stocks: green >20%, yellow 10–20%, red <10%."
    ),
    "Analyst Upside": (
        "The percentage difference between the Wall Street consensus 12-month price target "
        "and the current price. Represents the average of analyst estimates — useful as a "
        "sentiment signal but treat it as one data point, not a forecast. "
        "Green >15%, yellow 0–15%, red <0% (analysts see downside)."
    ),
    "Beta": (
        "Measures a stock's volatility relative to the S&P 500. Beta of 1.0 moves in "
        "line with the market. Beta of 2.0 is twice as volatile. Beta of 0.5 is half "
        "as volatile. High-beta stocks amplify both gains and losses. Not scored — "
        "displayed for risk context only."
    ),
    "Composite Score": (
        "Weighted average of three pillars scored 0–1. Value/Blend stocks: DCF 40%, "
        "Fundamentals 35%, Quality 25%. Growth stocks: DCF 25%, Fundamentals 35%, "
        "Quality 40% (with revenue and earnings growth included). A score near 1.0 means "
        "cheap on all measures; near 0 means expensive on all measures. Use for ranking "
        "within this universe, not as an absolute buy/sell signal."
    ),
}


def signal_badge(signal: str) -> str:
    label, color = _BADGE_CONFIG.get(signal, ("N/A", COLOR_GRAY))
    return f'<span style="color:{color}; font-weight:bold; font-size:0.95em;">&#9679; {label}</span>'


def _dot(signal: str) -> str:
    color = _SIGNAL_COLORS.get(signal, COLOR_GRAY)
    return f'<span style="color:{color};">&#9679;</span>'


def _fmt_value(value, fmt: str) -> str:
    if value is None:
        return "N/A"
    if fmt == "pct":
        return f"{value:.1%}"
    if fmt == "pct2":
        return f"{value:.2%}"
    if fmt == "x1":
        return f"{value:.1f}x"
    if fmt == "x2":
        return f"{value:.2f}x"
    if fmt == "dollar":
        return f"${value:.2f}"
    if fmt == "dollar_large":
        return f"${value:,.0f}"
    if fmt == "2f":
        return f"{value:.2f}"
    if fmt == "1f":
        return f"{value:.1f}"
    return str(value)


def _row(label: str, value, signal: str, fmt: str = "", tooltip_key: str = "") -> str:
    """Colored signal dot + labeled metric. Hover tooltip from METRIC_DEFS."""
    dot = _dot(signal)
    display = _fmt_value(value, fmt)
    tip = METRIC_DEFS.get(tooltip_key or label, "")
    title = f' title="{tip}"' if tip else ""
    return f'<span{title} style="cursor:help;">{dot} <b>{label}:</b> {display}</span>'


def _plain(label: str, value, fmt: str = "", tooltip_key: str = "") -> str:
    """No signal dot — informational metric. Hover tooltip from METRIC_DEFS."""
    display = _fmt_value(value, fmt)
    tip = METRIC_DEFS.get(tooltip_key or label, "")
    title = f' title="{tip}"' if tip else ""
    return f'<span{title} style="cursor:help;"><b>{label}:</b> {display}</span>'


def render_metric_legend() -> None:
    """Collapsible metric definitions reference panel."""
    with st.expander("Metric Definitions", expanded=False):
        col1, col2 = st.columns(2)
        items = list(METRIC_DEFS.items())
        mid = len(items) // 2 + len(items) % 2
        for col, chunk in ((col1, items[:mid]), (col2, items[mid:])):
            with col:
                for name, definition in chunk:
                    st.markdown(f"**{name}**")
                    st.caption(definition)


def render_stock_expander(result: ValuationResult) -> None:
    signal_emoji = {"undervalued": "🟢", "fair": "🟡", "overvalued": "🔴"}.get(result.signal, "⚪")
    header = (
        f"{signal_emoji}  {result.ticker} — {result.company_name}"
        f"  |  Score: {result.composite_score:.3f}"
        f"  |  {result.sector}"
    )

    with st.expander(header):
        sig = result.metric_signals
        profile_badge = _PROFILE_BADGE.get(result.growth_profile, "")
        scoring_note = {
            "growth": "Scored as <b>growth stock</b>: adjusted multiple thresholds, revenue &amp; earnings growth included in quality pillar (DCF 25% / Fundamentals 35% / Quality 40%)",
            "value":  "Scored as <b>value stock</b>: traditional multiple thresholds (DCF 40% / Fundamentals 35% / Quality 25%)",
            "blend":  "Scored as <b>blend</b>: traditional multiple thresholds (DCF 40% / Fundamentals 35% / Quality 25%)",
        }.get(result.growth_profile, "")
        st.markdown(
            f"{profile_badge} &nbsp; <small style='color:#888;'>{scoring_note}</small>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        col1, col2, col3 = st.columns(3)

        # ── Column 1: Valuation Multiples ─────────────────────────────────────
        with col1:
            st.markdown("**Valuation Multiples**")
            for html in [
                _row("P/E (TTM)",   result.pe_ratio,   sig.get("pe", "na"),         "1f"),
                _row("Forward P/E", result.forward_pe, sig.get("forward_pe", "na"), "1f"),
                _row("P/FCF",       result.p_fcf,      sig.get("p_fcf", "na"),      "1f"),
                _row("EV/EBITDA",   result.ev_ebitda,  sig.get("ev_ebitda", "na"),  "1f"),
                _row("PEG Ratio",   result.peg_ratio,  sig.get("peg", "na"),        "2f"),
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
                _plain("Current Price",    result.price,         "dollar"),
                _plain("DCF Value",        result.dcf_value,     "dollar"),
                _row("Margin of Safety",   result.margin_of_safety, sig.get("mos", "na"), "pct"),
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
                _plain(f"Est. Price ({growth_note})", result.five_yr_price, "dollar",
                       tooltip_key="5-Year Estimate"),
                _plain("Implied 5Y CAGR", result.five_yr_cagr, "pct"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

            st.markdown("<br>**Quality**", unsafe_allow_html=True)
            for html in [
                _row("Return on Equity", result.roe,            sig.get("roe", "na"),         "pct"),
                _row("Debt / Equity",    result.debt_to_equity, sig.get("debt_equity", "na"), "x2"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

        # ── Column 3: Growth & Outlook ────────────────────────────────────────
        with col3:
            st.markdown("**Growth (YoY)**")
            is_growth = result.growth_profile == "growth"
            rev_sig = sig.get("revenue_growth", "na") if is_growth else "na"
            eps_sig = sig.get("earnings_growth", "na") if is_growth else "na"
            for html in [
                _row("Revenue Growth",  result.revenue_growth,  rev_sig, "pct") if is_growth
                    else _plain("Revenue Growth",  result.revenue_growth,  "pct"),
                _row("Earnings Growth", result.earnings_growth, eps_sig, "pct") if is_growth
                    else _plain("Earnings Growth", result.earnings_growth, "pct"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

            st.markdown("<br>**Analyst Consensus**", unsafe_allow_html=True)
            for html in [
                _row("Analyst Upside", result.analyst_upside,
                     sig.get("analyst_upside", "na"), "pct"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

            st.markdown("<br>**Risk**", unsafe_allow_html=True)
            for html in [
                _plain("Beta (vs S&P 500)", result.beta, "2f", tooltip_key="Beta"),
            ]:
                st.markdown(html, unsafe_allow_html=True)

            st.markdown("<br>**Overall Signal**", unsafe_allow_html=True)
            st.markdown(signal_badge(result.signal), unsafe_allow_html=True)
