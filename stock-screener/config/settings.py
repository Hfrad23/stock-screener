from datetime import datetime
from typing import Optional, Literal, Dict
from pydantic import BaseModel

# ── DCF Parameters ────────────────────────────────────────────────────────────
WACC             = 0.10
TERMINAL_GROWTH  = 0.03
PROJECTION_YEARS = 5
MAX_FCF_GROWTH   = 0.25
MIN_FCF_GROWTH   = -0.05

# ── Scoring weights ───────────────────────────────────────────────────────────
W_DCF  = 0.40
W_FUND = 0.35
W_QUAL = 0.25

# ── Cache TTLs (seconds) ──────────────────────────────────────────────────────
PRICE_CACHE_TTL        = 300      # 5 minutes
FUNDAMENTALS_CACHE_TTL = 86400    # 24 hours
HOLDINGS_CACHE_TTL     = 604800   # 7 days

# ── Valuation thresholds ──────────────────────────────────────────────────────
# Calibrated for large-cap growth; lower is better unless noted

PE_GREEN        = 20
PE_YELLOW       = 35

FWD_PE_GREEN    = 18
FWD_PE_YELLOW   = 30

P_FCF_GREEN     = 20
P_FCF_YELLOW    = 40

EV_EBITDA_GREEN  = 15
EV_EBITDA_YELLOW = 25

PEG_GREEN       = 1.5
PEG_YELLOW      = 2.5

# Higher is better
MOS_GREEN       = 0.25    # >25% margin of safety → green
MOS_YELLOW      = -0.10   # -10% to 25% → yellow; below -10% → red

ANALYST_GREEN   = 0.15    # >15% analyst upside → green
ANALYST_YELLOW  = 0.0     # 0–15% → yellow; below 0% → red

# Quality thresholds
ROE_GREEN       = 0.15    # >15% ROE → green (higher is better)
ROE_YELLOW      = 0.08    # 8–15% → yellow; below 8% → red

# D/E stored as ratio (yfinance value / 100); lower is better
DE_GREEN        = 0.50    # <0.5x D/E → green
DE_YELLOW       = 2.00    # 0.5–2.0x → yellow; above 2.0x → red

# 5-year price estimate
GROWTH_CAP_5YR      = 0.25   # cap sustained growth at 25%/yr
EXIT_MULTIPLE_CAP   = 40.0   # cap exit P/E multiple at 40x

# ── Colors ────────────────────────────────────────────────────────────────────
COLOR_GREEN  = "#00c853"
COLOR_YELLOW = "#ffd600"
COLOR_RED    = "#ff5252"
COLOR_GRAY   = "#9e9e9e"


# ── Data Models ───────────────────────────────────────────────────────────────
class StockFundamentals(BaseModel):
    ticker: str
    company_name: str
    sector: str
    shares_outstanding: Optional[float] = None
    ttm_fcf: Optional[float] = None
    fcf_growth_rate: Optional[float] = None
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    pb_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    roe: Optional[float] = None
    operating_margins: Optional[float] = None
    total_debt: Optional[float] = None
    total_cash: Optional[float] = None
    analyst_target: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    debt_to_equity: Optional[float] = None   # stored as ratio (e.g. 1.03 = 103% D/E)
    beta: Optional[float] = None
    profit_margins: Optional[float] = None
    fetched_at: datetime


class StockPrice(BaseModel):
    ticker: str
    price: float
    market_cap: Optional[float] = None
    updated_at: datetime


class ValuationResult(BaseModel):
    ticker: str
    company_name: str
    sector: str
    price: float
    dcf_value: Optional[float] = None
    margin_of_safety: Optional[float] = None
    p_fcf: Optional[float] = None
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    peg_ratio: Optional[float] = None
    ev_ebitda: Optional[float] = None
    analyst_upside: Optional[float] = None
    roe: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    debt_to_equity: Optional[float] = None
    beta: Optional[float] = None
    operating_margins: Optional[float] = None
    profit_margins: Optional[float] = None
    five_yr_price: Optional[float] = None    # projected price in 5 years
    five_yr_cagr: Optional[float] = None     # implied annualized return to that target
    five_yr_growth_used: Optional[float] = None  # growth rate applied (for transparency)
    composite_score: float
    signal: Literal["undervalued", "fair", "overvalued", "insufficient_data"]
    metric_signals: Dict[str, Literal["green", "yellow", "red", "na"]]
