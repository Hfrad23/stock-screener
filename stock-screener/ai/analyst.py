"""
AI analyst: builds a context string from live valuation data and calls Claude
to answer natural-language questions about the stocks in the universe.
"""
from typing import List
from datetime import date

from anthropic import Anthropic

from config.settings import ValuationResult

_SYSTEM_PROMPT = """You are a professional financial analyst assistant. You have access to \
real-time valuation data for the top 25 holdings of the S&P 500 (SPY) and QQQ (NASDAQ-100), \
fetched today and shown below.

RULES:
- Use only the data provided. Never invent prices, ratios, or estimates.
- If a metric shows N/A, say so — do not guess.
- If asked about a stock not in the dataset, say it is not in the current universe.
- Be direct, specific, and reference actual numbers from the data.
- When comparing stocks, use the actual metrics — don't rely on memory.
- This is for informational purposes only, not investment advice.

SCORING METHODOLOGY:
- Composite score ranges 0–1 (higher = more attractive on the criteria below).
- Growth stocks (G): DCF 25% | Fundamentals 35% | Quality 40% (includes revenue & earnings growth as scored signals).
- Value/Blend stocks (V/B): DCF 40% | Fundamentals 35% | Quality 25%.
- Signal: ≥55% of metrics green → Undervalued | <25% green → Overvalued | else → Fair.
- Growth thresholds are more lenient on multiples (P/E green <35 vs <20 for value).
- PEG is the tightest growth filter: green <1.0 for growth stocks, <1.5 for value.

TODAY'S DATE: {today}

VALUATION DATA:
{context}"""


def build_context(results: List[ValuationResult]) -> str:
    """Format all ValuationResult objects into a compact text context for the LLM."""
    lines = []
    for r in results:
        sig = r.metric_signals
        mos_str   = f"{r.margin_of_safety:.1%}" if r.margin_of_safety is not None else "N/A"
        dcf_str   = f"${r.dcf_value:.2f}"       if r.dcf_value       is not None else "N/A"
        pfcf_str  = f"{r.p_fcf:.1f}"            if r.p_fcf           is not None else "N/A"
        fpe_str   = f"{r.forward_pe:.1f}"        if r.forward_pe      is not None else "N/A"
        pe_str    = f"{r.pe_ratio:.1f}"          if r.pe_ratio        is not None else "N/A"
        peg_str   = f"{r.peg_ratio:.2f}"         if r.peg_ratio       is not None else "N/A"
        eveb_str  = f"{r.ev_ebitda:.1f}"         if r.ev_ebitda       is not None else "N/A"
        roe_str   = f"{r.roe:.1%}"               if r.roe             is not None else "N/A"
        de_str    = f"{r.debt_to_equity:.2f}x"   if r.debt_to_equity  is not None else "N/A"
        revg_str  = f"{r.revenue_growth:.1%}"    if r.revenue_growth  is not None else "N/A"
        epsg_str  = f"{r.earnings_growth:.1%}"   if r.earnings_growth is not None else "N/A"
        au_str    = f"{r.analyst_upside:.1%}"    if r.analyst_upside  is not None else "N/A"
        beta_str  = f"{r.beta:.2f}"              if r.beta            is not None else "N/A"
        opm_str   = f"{r.operating_margins:.1%}" if r.operating_margins is not None else "N/A"
        npm_str   = f"{r.profit_margins:.1%}"    if r.profit_margins  is not None else "N/A"
        p5y_str   = f"${r.five_yr_price:.2f}"    if r.five_yr_price   is not None else "N/A"
        cagr_str  = f"{r.five_yr_cagr:.1%}"      if r.five_yr_cagr    is not None else "N/A"
        g_str     = (f"{r.five_yr_growth_used:.1%} growth used"
                     if r.five_yr_growth_used is not None else "")

        profile_label = {"growth": "Growth (G)", "value": "Value (V)", "blend": "Blend (B)"}.get(
            r.growth_profile, "Blend (B)")

        lines.append(
            f"{r.ticker} — {r.company_name} | {r.sector} | {profile_label}\n"
            f"  Signal: {r.signal.upper()} | Score: {r.composite_score:.3f} | Price: ${r.price:.2f}\n"
            f"  DCF Value: {dcf_str} | Margin of Safety: {mos_str}\n"
            f"  P/E: {pe_str} [{sig.get('pe','na')}] | Fwd P/E: {fpe_str} [{sig.get('forward_pe','na')}] | "
            f"P/FCF: {pfcf_str} [{sig.get('p_fcf','na')}]\n"
            f"  EV/EBITDA: {eveb_str} [{sig.get('ev_ebitda','na')}] | PEG: {peg_str} [{sig.get('peg','na')}]\n"
            f"  ROE: {roe_str} [{sig.get('roe','na')}] | D/E: {de_str} [{sig.get('debt_equity','na')}]\n"
            f"  Op. Margin: {opm_str} | Net Margin: {npm_str} | Beta: {beta_str}\n"
            f"  Revenue Growth: {revg_str} | Earnings Growth: {epsg_str}\n"
            f"  Analyst Upside: {au_str} [{sig.get('analyst_upside','na')}]\n"
            f"  5Y Est: {p5y_str} | 5Y CAGR: {cagr_str}{' | ' + g_str if g_str else ''}"
        )
    return "\n\n".join(lines)


def ask_analyst(
    question: str,
    context: str,
    history: list,
) -> str:
    """
    Call Claude with the question, valuation context, and conversation history.
    history: list of {"role": "user"|"assistant", "content": str}
    """
    client = Anthropic()

    system = _SYSTEM_PROMPT.format(
        today=date.today().isoformat(),
        context=context,
    )

    messages = []
    for msg in history[-12:]:   # keep last 6 exchanges (12 messages)
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system,
        messages=messages,
    )
    return response.content[0].text
