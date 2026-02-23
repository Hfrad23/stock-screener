from typing import Optional, Literal, List

from config.settings import (
    StockFundamentals, StockPrice, ValuationResult,
    WACC, TERMINAL_GROWTH, PROJECTION_YEARS,
    W_DCF, W_FUND, W_QUAL,
    PE_GREEN, PE_YELLOW,
    FWD_PE_GREEN, FWD_PE_YELLOW,
    P_FCF_GREEN, P_FCF_YELLOW,
    EV_EBITDA_GREEN, EV_EBITDA_YELLOW,
    PEG_GREEN, PEG_YELLOW,
    MOS_GREEN, MOS_YELLOW,
    ANALYST_GREEN, ANALYST_YELLOW,
    ROE_GREEN, ROE_YELLOW,
    DE_GREEN, DE_YELLOW,
    GROWTH_CAP_5YR, EXIT_MULTIPLE_CAP,
)
from analysis.dcf import compute_dcf


def signal_for_metric(
    value: Optional[float],
    green_threshold: float,
    yellow_threshold: float,
    higher_is_better: bool = False,
) -> Literal["green", "yellow", "red", "na"]:
    if value is None:
        return "na"
    if higher_is_better:
        if value >= green_threshold:
            return "green"
        elif value >= yellow_threshold:
            return "yellow"
        else:
            return "red"
    else:
        if value <= green_threshold:
            return "green"
        elif value <= yellow_threshold:
            return "yellow"
        else:
            return "red"


def _signal_to_score(signal: str) -> Optional[float]:
    return {"green": 1.0, "yellow": 0.5, "red": 0.0}.get(signal)


def compute_5yr_estimate(
    fund: StockFundamentals,
    price: StockPrice,
) -> tuple:
    """
    5-year price estimate via EPS projection.

    Formula:
      projected_eps   = (price / trailing_PE) × (1 + capped_growth)^5
      five_yr_price   = projected_eps × exit_multiple
      five_yr_cagr    = (five_yr_price / price)^(1/5) − 1

    Growth rate: earnings_growth → revenue_growth → fcf_growth_rate → 7% default.
    Capped at GROWTH_CAP_5YR (25%) to avoid compounding a single exceptional year
    over a full 5-year horizon.

    Exit multiple: forward_PE (capped at EXIT_MULTIPLE_CAP).
    Falls back to min(trailing_PE, 20) if no forward PE.
    """
    if not fund.pe_ratio or fund.pe_ratio <= 0:
        return None, None, None
    if not price.price or price.price <= 0:
        return None, None, None

    eps = price.price / fund.pe_ratio

    # Pick best available growth rate
    raw_growth = fund.earnings_growth or fund.revenue_growth or fund.fcf_growth_rate
    growth = float(raw_growth) if raw_growth is not None else 0.07
    growth = max(-0.05, min(GROWTH_CAP_5YR, growth))

    # Exit multiple: forward PE preferred, capped; fallback to conservative trailing PE
    if fund.forward_pe and 5.0 < fund.forward_pe <= EXIT_MULTIPLE_CAP:
        exit_multiple = fund.forward_pe
    elif fund.forward_pe and fund.forward_pe > EXIT_MULTIPLE_CAP:
        exit_multiple = EXIT_MULTIPLE_CAP
    else:
        exit_multiple = min(fund.pe_ratio, 20.0)

    projected_eps = eps * (1 + growth) ** 5
    five_yr_price = round(projected_eps * exit_multiple, 2)

    if five_yr_price <= 0:
        return None, None, growth

    five_yr_cagr = (five_yr_price / price.price) ** (1.0 / 5) - 1
    return five_yr_price, round(five_yr_cagr, 4), round(growth, 4)


def build_valuation_result(
    fund: StockFundamentals,
    price: StockPrice,
    dcf_val: Optional[float],
    mos: Optional[float],
) -> ValuationResult:
    # P/FCF: market cap (shares * price) / TTM FCF
    p_fcf = None
    if fund.shares_outstanding and price.price and fund.ttm_fcf and fund.ttm_fcf > 0:
        market_cap = fund.shares_outstanding * price.price
        p_fcf = market_cap / fund.ttm_fcf

    # Analyst consensus upside vs current price
    analyst_upside = None
    if fund.analyst_target is not None and price.price > 0:
        analyst_upside = (fund.analyst_target - price.price) / price.price

    # ── Per-metric signals ────────────────────────────────────────────────────
    metric_signals: dict = {
        # Valuation
        "pe":             signal_for_metric(fund.pe_ratio,       PE_GREEN,        PE_YELLOW),
        "forward_pe":     signal_for_metric(fund.forward_pe,     FWD_PE_GREEN,    FWD_PE_YELLOW),
        "p_fcf":          signal_for_metric(p_fcf,               P_FCF_GREEN,     P_FCF_YELLOW),
        "ev_ebitda":      signal_for_metric(fund.ev_ebitda,      EV_EBITDA_GREEN, EV_EBITDA_YELLOW),
        "peg":            signal_for_metric(fund.peg_ratio,      PEG_GREEN,       PEG_YELLOW),
        # DCF
        "mos":            signal_for_metric(mos, MOS_GREEN, MOS_YELLOW, higher_is_better=True),
        # Quality
        "analyst_upside": signal_for_metric(analyst_upside,      ANALYST_GREEN,   ANALYST_YELLOW,  higher_is_better=True),
        "roe":            signal_for_metric(fund.roe,             ROE_GREEN,       ROE_YELLOW,      higher_is_better=True),
        "debt_equity":    signal_for_metric(fund.debt_to_equity, DE_GREEN,        DE_YELLOW),
    }

    # ── Composite score ───────────────────────────────────────────────────────
    # DCF pillar (40%)
    dcf_score = _signal_to_score(metric_signals["mos"]) or 0.5

    # Fundamental pillar (35%): valuation multiples
    fund_keys = ["pe", "forward_pe", "p_fcf", "ev_ebitda", "peg"]
    fund_scores = [s for s in (_signal_to_score(metric_signals[k]) for k in fund_keys) if s is not None]
    fund_score = sum(fund_scores) / len(fund_scores) if fund_scores else 0.5

    # Quality pillar (25%): analyst upside + ROE + debt discipline
    qual_keys = ["analyst_upside", "roe", "debt_equity"]
    qual_scores = [s for s in (_signal_to_score(metric_signals[k]) for k in qual_keys) if s is not None]
    qual_score = sum(qual_scores) / len(qual_scores) if qual_scores else 0.5

    composite = W_DCF * dcf_score + W_FUND * fund_score + W_QUAL * qual_score

    # ── Overall signal ────────────────────────────────────────────────────────
    # Based on fraction of green signals across valuation + DCF + quality metrics
    scored = [s for s in metric_signals.values() if s != "na"]
    if len(scored) < 3:
        overall_signal: Literal["undervalued", "fair", "overvalued", "insufficient_data"] = "insufficient_data"
    else:
        green_pct = sum(1 for s in scored if s == "green") / len(scored)
        if green_pct >= 0.55:
            overall_signal = "undervalued"
        elif green_pct < 0.25:
            overall_signal = "overvalued"
        else:
            overall_signal = "fair"

    five_yr_price, five_yr_cagr, five_yr_growth = compute_5yr_estimate(fund, price)

    return ValuationResult(
        ticker=fund.ticker,
        company_name=fund.company_name,
        sector=fund.sector,
        price=price.price,
        dcf_value=dcf_val,
        margin_of_safety=mos,
        p_fcf=p_fcf,
        pe_ratio=fund.pe_ratio,
        forward_pe=fund.forward_pe,
        peg_ratio=fund.peg_ratio,
        ev_ebitda=fund.ev_ebitda,
        analyst_upside=analyst_upside,
        roe=fund.roe,
        revenue_growth=fund.revenue_growth,
        earnings_growth=fund.earnings_growth,
        debt_to_equity=fund.debt_to_equity,
        beta=fund.beta,
        operating_margins=fund.operating_margins,
        profit_margins=fund.profit_margins,
        five_yr_price=five_yr_price,
        five_yr_cagr=five_yr_cagr,
        five_yr_growth_used=five_yr_growth,
        composite_score=round(composite, 4),
        signal=overall_signal,
        metric_signals=metric_signals,
    )


def run_valuation(
    fundamentals: List[StockFundamentals],
    prices: List[StockPrice],
    wacc: float = WACC,
    terminal_growth: float = TERMINAL_GROWTH,
    projection_years: int = PROJECTION_YEARS,
) -> List[ValuationResult]:
    """Match fundamentals + prices, run DCF, assemble results sorted by composite score."""
    price_map = {p.ticker: p for p in prices}
    results = []
    for fund in fundamentals:
        price = price_map.get(fund.ticker)
        if price is None:
            continue
        dcf_val, mos = compute_dcf(fund, price, wacc, terminal_growth, projection_years)
        results.append(build_valuation_result(fund, price, dcf_val, mos))
    return sorted(results, key=lambda r: r.composite_score, reverse=True)
