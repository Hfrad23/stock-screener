"""Stock Screener — S&P 500 + QQQ Top 25 Valuation Dashboard"""

import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from config.settings import WACC, TERMINAL_GROWTH, PROJECTION_YEARS
from data.holdings import get_spy_top25, get_qqq_top25, get_all_tickers
from data.fetcher import fetch_fundamentals, fetch_prices
from analysis.valuation import run_valuation
from ui.views import render_index_tab
from ai.analyst import build_context, ask_analyst

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
spy_tickers   = get_spy_top25()
qqq_tickers   = get_qqq_top25()
all_tickers   = get_all_tickers()
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
price_ts = max((p.updated_at for p in prices),        default=None) if prices       else None

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

# ── Valuation ─────────────────────────────────────────────────────────────────
all_results      = run_valuation(fundamentals, prices, wacc, terminal_growth, projection_years)
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
tab_spy, tab_qqq, tab_lookup, tab_ask = st.tabs(["S&P 500 Top 25", "QQQ Top 25", "Stock Lookup", "Ask the Analyst"])

with tab_spy:
    render_index_tab(spy_results, "S&P 500 Top 25")

with tab_qqq:
    render_index_tab(qqq_results, "QQQ Top 25")

with tab_lookup:
    st.subheader("Stock Lookup")
    st.caption(
        "Enter any ticker symbol traded on US markets to get the full valuation analysis — "
        "same metrics, same DCF methodology, and same refresh controls as the index tabs."
    )

    col_input, col_btn = st.columns([4, 1])
    with col_input:
        raw_input = st.text_input(
            "Ticker",
            placeholder="e.g. TSLA, JPM, BRK-B",
            label_visibility="collapsed",
            key="lookup_input",
        )
    with col_btn:
        search_clicked = st.button("Search", use_container_width=True, key="lookup_search")

    if search_clicked and raw_input.strip():
        st.session_state.lookup_ticker = raw_input.strip().upper()

    lookup_ticker = st.session_state.get("lookup_ticker", "")

    if lookup_ticker:
        # If already in the main universe, reuse the already-computed result
        if lookup_ticker in ticker_to_result:
            st.info(f"{lookup_ticker} is part of the index universe — showing data fetched with the main lists.")
            render_index_tab([ticker_to_result[lookup_ticker]], lookup_ticker)
        else:
            lookup_tuple = (lookup_ticker,)
            with st.spinner(f"Fetching data for {lookup_ticker}…"):
                lookup_fund  = fetch_fundamentals(lookup_tuple)
                lookup_price = fetch_prices(lookup_tuple)

            if not lookup_fund or not lookup_price:
                st.error(f"No data found for '{lookup_ticker}'. Verify the ticker symbol and try again.")
            else:
                lookup_results = run_valuation(
                    lookup_fund, lookup_price, wacc, terminal_growth, projection_years
                )
                if not lookup_results:
                    st.error(f"Could not compute valuation for '{lookup_ticker}'.")
                else:
                    lf_ts = lookup_fund[0].fetched_at
                    lp_ts = lookup_price[0].updated_at

                    rc1, rc2, rb1, rb2 = st.columns([3, 3, 1.5, 2])
                    with rc1:
                        st.caption(f"Fundamentals as of: {lf_ts.strftime('%Y-%m-%d %H:%M UTC')}")
                    with rc2:
                        st.caption(f"Prices as of: {lp_ts.strftime('%Y-%m-%d %H:%M UTC')}")
                    with rb1:
                        if st.button("Refresh Prices", key="lookup_ref_prices"):
                            fetch_prices.clear()
                            st.rerun()
                    with rb2:
                        if st.button("Refresh Fundamentals", key="lookup_ref_fund"):
                            fetch_fundamentals.clear()
                            st.rerun()

                    render_index_tab(lookup_results, lookup_ticker)

with tab_ask:
    _api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not _api_key:
        st.warning(
            "No API key found. Add `ANTHROPIC_API_KEY=your_key` to a `.env` file "
            "in the stock-screener directory, then restart the app."
        )
        st.stop()

    st.subheader("Ask the Analyst")
    st.caption(
        "Ask anything about the stocks in this universe. "
        "The analyst has access to all of today's fetched data — prices, multiples, "
        "DCF values, growth rates, signals, and scores."
    )
    st.caption("Examples: *Is NVDA overvalued?* · *Which stock has the best PEG?* · *Compare AAPL vs MSFT* · *What are the highest-quality growth stocks here?*")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if st.button("Clear conversation", key="clear_chat"):
        st.session_state.chat_history = []
        st.rerun()

    # Build context once per session (all stocks, all metrics)
    analyst_context = build_context(all_results)

    # Render existing messages
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # New question
    if question := st.chat_input("Ask about a stock or the universe…"):
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing…"):
                try:
                    answer = ask_analyst(
                        question,
                        analyst_context,
                        st.session_state.chat_history[:-1],
                    )
                except Exception as e:
                    answer = f"Error calling the API: {e}"
            st.markdown(answer)

        st.session_state.chat_history.append({"role": "assistant", "content": answer})
