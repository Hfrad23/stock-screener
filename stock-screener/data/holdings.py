import yfinance as yf
import streamlit as st
from config.settings import HOLDINGS_CACHE_TTL

SPY_TOP25_FALLBACK = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META",
    "GOOGL", "GOOG",  "BRK-B", "LLY",  "TSLA",
    "AVGO", "JPM",   "V",     "UNH",  "XOM",
    "MA",   "COST",  "HD",    "ORCL", "NFLX",
    "PG",   "JNJ",   "CRM",   "ABBV", "WMT",
]

QQQ_TOP25_FALLBACK = [
    "AAPL", "MSFT", "NVDA", "AMZN", "META",
    "GOOGL", "GOOG", "TSLA", "AVGO", "COST",
    "NFLX", "AMD",  "QCOM", "INTU", "TXN",
    "AMGN", "BKNG", "AMAT", "MU",   "ADI",
    "LRCX", "KLAC", "PANW", "CDNS", "ADP",
]


@st.cache_data(ttl=HOLDINGS_CACHE_TTL, show_spinner=False)
def get_spy_top25() -> list:
    try:
        spy = yf.Ticker("SPY")
        fdata = spy.funds_data
        if hasattr(fdata, "top_holdings") and fdata.top_holdings is not None:
            holdings = fdata.top_holdings
            if len(holdings) >= 25:
                return list(holdings.index[:25])
    except Exception:
        pass
    return SPY_TOP25_FALLBACK


@st.cache_data(ttl=HOLDINGS_CACHE_TTL, show_spinner=False)
def get_qqq_top25() -> list:
    try:
        qqq = yf.Ticker("QQQ")
        fdata = qqq.funds_data
        if hasattr(fdata, "top_holdings") and fdata.top_holdings is not None:
            holdings = fdata.top_holdings
            if len(holdings) >= 25:
                return list(holdings.index[:25])
    except Exception:
        pass
    return QQQ_TOP25_FALLBACK


def get_all_tickers() -> list:
    spy = get_spy_top25()
    qqq = get_qqq_top25()
    return sorted(set(spy + qqq))
