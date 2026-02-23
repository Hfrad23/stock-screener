from typing import Optional, Tuple

from config.settings import (
    StockFundamentals, StockPrice,
    WACC, TERMINAL_GROWTH, PROJECTION_YEARS,
    MAX_FCF_GROWTH, MIN_FCF_GROWTH,
)


def compute_dcf(
    fund: StockFundamentals,
    price: StockPrice,
    wacc: float = WACC,
    terminal_growth: float = TERMINAL_GROWTH,
    projection_years: int = PROJECTION_YEARS,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Returns (dcf_intrinsic_value, margin_of_safety).
    Returns (None, None) if inputs are invalid or equity value is non-positive.
    """
    fcf = fund.ttm_fcf
    shares = fund.shares_outstanding
    current_price = price.price

    if fcf is None or shares is None or current_price is None:
        return None, None
    if shares <= 0 or current_price <= 0 or fcf <= 0:
        return None, None

    cash = fund.total_cash or 0.0
    debt = fund.total_debt or 0.0

    g = fund.fcf_growth_rate if fund.fcf_growth_rate is not None else 0.05
    g = max(MIN_FCF_GROWTH, min(MAX_FCF_GROWTH, g))

    pv = sum(
        fcf * (1 + g) ** yr / (1 + wacc) ** yr
        for yr in range(1, projection_years + 1)
    )
    tv = (
        fcf * (1 + g) ** projection_years
        * (1 + terminal_growth)
        / (wacc - terminal_growth)
    )
    equity = pv + tv / (1 + wacc) ** projection_years + cash - debt

    if equity <= 0:
        return None, None

    intrinsic_value = equity / shares
    margin_of_safety = (intrinsic_value - current_price) / intrinsic_value
    return round(intrinsic_value, 2), round(margin_of_safety, 4)
