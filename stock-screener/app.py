"""Stock Screener — S&P 500 + QQQ Top 25 Valuation Dashboard"""

import streamlit as st

from config.settings import WACC, TERMINAL_GROWTH, PROJECTION_YEARS
from data.holdings import get_spy_top25, get_qqq_top25, get_all_tickers
from data.fetcher import fetch_fundamentals, fetch_prices
from analysis.valuation import run_valuation
from ui.views import render_index_tab

st.set_page_config(
    page_title="Stock Screener",
    page_icon="📈",
    layout="wide",
)

# ── Sidebar: DCF parameters ───────────────────────────────────────────────────
with st.sidebar:
    st.header("DCF Parameters")
    wacc = st.slider(
        "WACC", min_value=0.05, max_value=0.20,
        value=WACC, step=0.01, format="%.2f",
    )
    terminal_growth = st.slider(
        "Terminal Growth", min_value=0.01, max_value=0.05,
        value=TERMINAL_GROWTH, step=0.005, format="%.3f",
    )
    projection_years = st.slider(
        "Projection Years", min_value=3, max_value=10,
        value=PROJECTION_YEARS,
    )
    st.markdown("---")
    st.caption(
        "Changing WACC or growth triggers DCF recompute without re-fetching data."
    )

# ── Tickers ───────────────────────────────────────────────────────────────────
spy_tickers  = get_spy_top25()
qqq_tickers  = get_qqq_top25()
all_tickers  = get_all_tickers()
tickers_tuple = tuple(sorted(all_tickers))

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("Stock Screener — Top 25 Holdings Valuation")

# ── Fetch data (cached) ───────────────────────────────────────────────────────
with st.spinner(f"Loading fundamentals for {len(tickers_tuple)} tickers…"):
    fundamentals = fetch_fundamentals(tickers_tuple)

with st.spinner("Loading prices…"):
    prices = fetch_prices(tickers_tuple)

# ── Header row: timestamps + refresh buttons ──────────────────────────────────
fund_ts  = max((f.fetched_at  for f in fundamentals), default=None) if fundamentals else None
price_ts = max((p.updated_at for p in prices),       default=None) if prices       else None

col_f, col_p, col_b1, col_b2 = st.columns([3, 3, 1.5, 2])
with col_f:
    if fund_ts:
        st.caption(f"Fundamentals as of: {fund_ts.strftime('%Y-%m-%d %H:%M UTC')}")
with col_p:
    if price_ts:
        st.caption(f"Prices as of: {price_ts.strftime('%Y-%m-%d %H:%M UTC')}")
with col_b1:
    if st.button("Refresh Prices"):
        fetch_prices.clear()
        st.rerun()
with col_b2:
    if st.button("Refresh Fundamentals"):
        fetch_fundamentals.clear()
        st.rerun()

st.markdown("---")

# ── Error guards ──────────────────────────────────────────────────────────────
if not fundamentals:
    st.error("Failed to fetch fundamentals. Check your connection and click Refresh Fundamentals.")
    st.stop()

if not prices:
    st.error("Failed to fetch prices. Check your connection and click Refresh Prices.")
    st.stop()

# ── Valuation (fast — pure math, reruns on sidebar change) ────────────────────
all_results    = run_valuation(fundamentals, prices, wacc, terminal_growth, projection_years)
ticker_to_result = {r.ticker: r for r in all_results}

spy_results = sorted(
    [ticker_to_result[t] for t in spy_tickers if t in ticker_to_result],
    key=lambda r: r.composite_score, reverse=True,
)
qqq_results = sorted(
    [ticker_to_result[t] for t in qqq_tickers if t in ticker_to_result],
    key=lambda r: r.composite_score, reverse=True,
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_spy, tab_qqq = st.tabs(["S&P 500 Top 25", "QQQ Top 25"])

with tab_spy:
    render_index_tab(spy_results, "S&P 500 Top 25")

with tab_qqq:
    render_index_tab(qqq_results, "QQQ Top 25")
