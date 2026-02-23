import numpy as np
import pandas as pd
import yfinance as yf
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Optional

from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import (
    StockFundamentals, StockPrice,
    FUNDAMENTALS_CACHE_TTL, PRICE_CACHE_TTL,
)


# ── FCF helpers ───────────────────────────────────────────────────────────────

def _fcf_cagr(cf) -> Optional[float]:
    """Compute FCF CAGR from cashflow statement. Uses 'Free Cash Flow' row directly."""
    if cf is None or cf.empty:
        return None
    try:
        # yfinance 1.x provides 'Free Cash Flow' row directly
        if "Free Cash Flow" in cf.index:
            fcf_vals = cf.loc["Free Cash Flow"].values.astype(float)
        else:
            # Fallback: Operating Cash Flow + Capital Expenditure (capex is negative)
            ocf = capex = None
            for lbl in ["Operating Cash Flow", "Cash Flow From Continuing Operating Activities"]:
                if lbl in cf.index:
                    ocf = cf.loc[lbl]
                    break
            for lbl in ["Capital Expenditure"]:
                if lbl in cf.index:
                    capex = cf.loc[lbl]
                    break
            if ocf is None or len(ocf) < 2:
                return None
            o = ocf.values.astype(float)
            c = capex.values.astype(float) if capex is not None else np.zeros(len(o))
            fcf_vals = o + c

        n = min(len(fcf_vals), 4)
        # cashflow columns are newest-first
        start, end = fcf_vals[n - 1], fcf_vals[0]
        if start <= 0 or end <= 0 or n < 2:
            return None
        return float((end / start) ** (1.0 / (n - 1)) - 1)
    except Exception:
        return None


# ── Single-ticker fetch with retry ───────────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
def _fetch_one(ticker: str) -> StockFundamentals:
    t = yf.Ticker(ticker)
    info = t.info or {}
    cf = t.cashflow

    def _safe(key) -> Optional[float]:
        val = info.get(key)
        if val is None:
            return None
        try:
            fval = float(val)
            return None if (np.isnan(fval) or np.isinf(fval)) else fval
        except (TypeError, ValueError):
            return None

    # TTM FCF — use freeCashflow from info as primary source (most reliable in yfinance 1.x)
    ttm_fcf = _safe("freeCashflow")
    if ttm_fcf is None:
        # Fallback: compute from cashflow statement
        try:
            if cf is not None and not cf.empty:
                if "Free Cash Flow" in cf.index:
                    ttm_fcf = float(cf.loc["Free Cash Flow"].iloc[0])
                elif "Operating Cash Flow" in cf.index:
                    ocf = float(cf.loc["Operating Cash Flow"].iloc[0])
                    capex = 0.0
                    if "Capital Expenditure" in cf.index:
                        capex = float(cf.loc["Capital Expenditure"].iloc[0])
                    ttm_fcf = ocf + capex
        except Exception:
            ttm_fcf = None
    if ttm_fcf is not None and (np.isnan(ttm_fcf) or np.isinf(ttm_fcf)):
        ttm_fcf = None

    # D/E: yfinance returns as percentage (e.g. 102.63 = 102.63%), store as ratio
    de_raw = _safe("debtToEquity")
    debt_to_equity = de_raw / 100.0 if de_raw is not None else None

    return StockFundamentals(
        ticker=ticker,
        company_name=info.get("shortName") or info.get("longName") or ticker,
        sector=info.get("sector") or "Unknown",
        shares_outstanding=_safe("sharesOutstanding"),
        ttm_fcf=ttm_fcf,
        fcf_growth_rate=_fcf_cagr(cf),
        pe_ratio=_safe("trailingPE"),
        forward_pe=_safe("forwardPE"),
        pb_ratio=_safe("priceToBook"),
        peg_ratio=_safe("trailingPegRatio"),   # pegRatio is None in yfinance 1.x
        ev_ebitda=_safe("enterpriseToEbitda"),
        roe=_safe("returnOnEquity"),
        operating_margins=_safe("operatingMargins"),
        profit_margins=_safe("profitMargins"),
        total_debt=_safe("totalDebt"),
        total_cash=_safe("totalCash"),
        analyst_target=_safe("targetMeanPrice"),
        revenue_growth=_safe("revenueGrowth"),
        earnings_growth=_safe("earningsGrowth"),
        debt_to_equity=debt_to_equity,
        beta=_safe("beta"),
        fetched_at=datetime.now(timezone.utc),
    )


def _fetch_one_safe(ticker: str) -> Optional[StockFundamentals]:
    try:
        return _fetch_one(ticker)
    except Exception:
        return None


# ── Cached batch fetchers ─────────────────────────────────────────────────────

@st.cache_data(ttl=FUNDAMENTALS_CACHE_TTL, show_spinner=False)
def fetch_fundamentals(tickers: tuple) -> list:
    """Fetch fundamentals for all tickers in parallel. Cached 24h."""
    results = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(_fetch_one_safe, t): t for t in tickers}
        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                results.append(result)
    return results


@st.cache_data(ttl=PRICE_CACHE_TTL, show_spinner=False)
def fetch_prices(tickers: tuple) -> list:
    """Batch price fetch via yf.download(). Cached 5 minutes."""
    try:
        ticker_list = list(tickers)
        data = yf.download(
            ticker_list, period="2d", auto_adjust=True,
            progress=False, threads=True,
        )
        if data.empty:
            return []

        # Multi-ticker: MultiIndex columns (field, ticker)
        # Single ticker: flat columns
        if isinstance(data.columns, pd.MultiIndex):
            close_df = data["Close"]
        else:
            close_df = data[["Close"]].rename(columns={"Close": ticker_list[0]})

        latest = close_df.ffill().iloc[-1]
        now = datetime.now(timezone.utc)

        prices = []
        for ticker in tickers:
            try:
                val = float(latest[ticker])
                if not np.isnan(val) and val > 0:
                    prices.append(StockPrice(ticker=ticker, price=val, updated_at=now))
            except (KeyError, TypeError, ValueError):
                pass
        return prices
    except Exception:
        return []
