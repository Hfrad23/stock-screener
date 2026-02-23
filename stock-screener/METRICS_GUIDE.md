# Metrics Reference Guide — S&P 500 Value Screener

A plain-English explanation of every metric used in the screener,
what it measures, and what to look for when evaluating a stock.

---

## VALUATION METRICS
*(Lower is generally better — you're paying less for what the company produces)*

---

### 1. P/E — Price-to-Earnings Ratio
**What it is:** Current share price divided by earnings per share (EPS).
It tells you how many dollars you're paying for every $1 of profit.

**Formula:** `Share Price ÷ Earnings Per Share`

| Range | What it signals |
|---|---|
| < 10 | Very cheap — possible deep value or a struggling business |
| 10–15 | Cheap to fair — classic value territory |
| 15–20 | Fair — roughly in line with the long-run S&P 500 average |
| 20–30 | Moderately expensive — growth is being priced in |
| > 30 | Expensive — requires strong growth to justify |

**Favorable for a 5-year horizon:** Under 15, ideally under 12.
**Sector caveat:** Banks and insurers often trade at 8–12×; tech at 20–35× is normal.

---

### 2. P/FCF — Price-to-Free Cash Flow
**What it is:** Share price divided by free cash flow per share.
Free cash flow (FCF) = operating cash flow minus capital expenditures.
This is often considered MORE reliable than P/E because earnings can be
manipulated with accounting, but cash in the bank is real.

**Formula:** `Market Cap ÷ Free Cash Flow`

| Range | What it signals |
|---|---|
| < 10 | Very cheap — generating a lot of cash relative to price |
| 10–15 | Attractive — solid cash generation |
| 15–20 | Fair |
| 20–30 | Pricey — growth expectations baked in |
| > 30 | Expensive — need high FCF growth to justify |

**Favorable for a 5-year horizon:** Under 15.
**Why it matters more than P/E:** Companies can show accounting profits
while burning cash. P/FCF cuts through that.

---

### 3. EV/EBITDA — Enterprise Value to EBITDA
**What it is:** The total cost to acquire the entire business (equity + debt - cash)
divided by operating earnings before interest, taxes, depreciation & amortization.
This is the metric used most often in M&A because it's capital-structure neutral
— it doesn't matter how the company is financed.

**Formula:** `(Market Cap + Debt - Cash) ÷ EBITDA`

| Range | What it signals |
|---|---|
| < 6 | Very cheap — common in commodities, financials |
| 6–10 | Attractive — value territory for most sectors |
| 10–14 | Fair — average for the S&P 500 |
| 14–20 | Pricey |
| > 20 | Expensive — tech/growth premium |

**Favorable for a 5-year horizon:** Under 10.
**Why it's useful:** Works across sectors because it ignores debt and taxes.

---

### 4. P/B — Price-to-Book Ratio
**What it is:** Share price divided by book value per share.
Book value = total assets minus total liabilities — essentially what the
company would be worth if it liquidated everything today.

**Formula:** `Share Price ÷ (Total Assets - Total Liabilities) per share`

| Range | What it signals |
|---|---|
| < 1.0 | Trading below liquidation value — rare, often a red flag OR deep value |
| 1–2 | Cheap — paying close to asset value |
| 2–3 | Fair |
| 3–5 | Pricey — intangibles or brand value not on balance sheet |
| > 5 | Expensive for asset-heavy companies; normal for capital-light tech |

**Favorable for a 5-year horizon:** Under 2.5 (sector-adjusted — banks at 1×, tech at 5× is fine).
**Best for:** Banks, insurers, industrials, real estate. Less useful for software.

---

### 5. PEG — Price/Earnings-to-Growth Ratio
**What it is:** P/E divided by expected earnings growth rate.
It adjusts the P/E for growth — a company growing at 20% deserves a
higher P/E than one growing at 2%. PEG makes that comparison fair.

**Formula:** `P/E Ratio ÷ Expected Annual Earnings Growth Rate (%)`

| Range | What it signals |
|---|---|
| < 0.5 | Potentially very undervalued relative to growth |
| 0.5–1.0 | Attractive — growth not fully priced in |
| 1.0 | Fair value — paying exactly for the growth you get |
| 1–1.5 | Slightly elevated |
| > 1.5 | Overpaying for growth |

**Favorable for a 5-year horizon:** Under 1.0, ideally under 0.75.
**Rule of thumb:** PEG < 1 = good deal. Peter Lynch popularised this metric.

---

## QUALITY METRICS
*(Higher is generally better — measuring how well the business performs)*

---

### 6. ROE — Return on Equity
**What it is:** Net income divided by shareholders' equity.
Measures how efficiently a company uses shareholder money to generate profit.
A high ROE means management is good at compounding your investment.

**Formula:** `Net Income ÷ Shareholders' Equity`

| Range | What it signals |
|---|---|
| < 5% | Weak — barely covering cost of equity |
| 5–10% | Below average |
| 10–15% | Solid — decent business |
| 15–20% | Good — competitive advantage likely |
| > 20% | Excellent — strong moat (think Apple, Visa, MSFT) |

**Favorable for a 5-year horizon:** 15%+ consistently over multiple years.
**Caveat:** Very high ROE (>50%) can be inflated by heavy debt — check D/E too.

---

### 7. ROA — Return on Assets
**What it is:** Net income divided by total assets.
Unlike ROE, this isn't affected by how much debt a company carries.
It shows how efficiently assets are deployed regardless of financing.

**Formula:** `Net Income ÷ Total Assets`

| Range | What it signals |
|---|---|
| < 2% | Poor — asset-intensive business with thin margins |
| 2–5% | Below average |
| 5–10% | Good |
| > 10% | Excellent — capital-light business with strong returns |

**Favorable for a 5-year horizon:** 5%+.
**Best for:** Comparing companies within the same sector.

---

### 8. Operating Margin
**What it is:** Operating income as a percentage of revenue.
Measures how much profit the company keeps from each dollar of sales
after paying operating costs — but before interest and taxes.

**Formula:** `Operating Income ÷ Revenue`

| Range | What it signals |
|---|---|
| < 5% | Thin margins — vulnerable to cost shocks |
| 5–10% | Low but acceptable in some industries (retail, airlines) |
| 10–20% | Healthy |
| 20–30% | Strong — pricing power or cost efficiency |
| > 30% | Exceptional — classic moat indicator (software, pharma) |

**Favorable for a 5-year horizon:** 15%+, and stable or expanding over time.
**Sector norms:** Grocery retail: 2–4%. Software: 20–40%. Pharma: 15–30%.

---

### 9. Debt-to-Equity (D/E) Ratio
**What it is:** Total debt divided by total shareholders' equity.
Measures financial leverage — how much of the business is funded by
borrowed money vs. owner money. High debt = higher risk, especially in
rising interest rate environments.

**Formula:** `Total Debt ÷ Total Shareholders' Equity`

| Range | What it signals |
|---|---|
| < 0.3 | Very conservative — fortress balance sheet |
| 0.3–0.75 | Healthy leverage |
| 0.75–1.5 | Moderate — manageable for most businesses |
| 1.5–3.0 | Elevated — watch interest coverage |
| > 3.0 | High risk — one bad year could cause distress |

**Favorable for a 5-year horizon:** Under 1.0. Under 0.5 is ideal.
**Sector caveat:** Banks and utilities structurally carry high D/E and
that's normal — use sector-adjusted comparisons for those.

---

## DCF METRIC

### 10. Margin of Safety (DCF)
**What it is:** The gap between a stock's estimated intrinsic value
(from our Discounted Cash Flow model) and its current market price.
The larger the gap, the more cushion you have if your assumptions are wrong.

**Formula:** `(Intrinsic Value - Current Price) ÷ Intrinsic Value`

| Range | What it signals |
|---|---|
| Negative | Overvalued — trading above DCF estimate |
| 0–20% | Fairly valued or small discount |
| 20–40% | Attractive — meaningful discount to intrinsic value |
| 40–60% | Very attractive — significant undervaluation |
| > 60% | Deep value or the DCF assumptions may be too optimistic |

**Favorable for a 5-year horizon:** 25%+ margin of safety.
**Important caveat:** A DCF is only as good as its inputs. The model uses
historical FCF growth rates capped at 25%, a 10% discount rate, and 3%
terminal growth. Treat it as a directional signal, not a precise target.

---

## QUICK REFERENCE CHEAT SHEET

| Metric | Ideal Range | What you want |
|---|---|---|
| P/E | < 15 | Low |
| P/FCF | < 15 | Low |
| EV/EBITDA | < 10 | Low |
| P/B | < 2.5 | Low |
| PEG | < 1.0 | Low |
| ROE | > 15% | High |
| ROA | > 5% | High |
| Operating Margin | > 15% | High |
| Debt/Equity | < 1.0 | Low |
| DCF Margin of Safety | > 25% | High |

---

## A NOTE ON SECTOR CONTEXT

These are general benchmarks for the **broad market**. Individual sectors
have very different norms:

| Sector | P/E norm | P/FCF norm | Margin norm |
|---|---|---|---|
| Technology | 20–35 | 20–40 | 20–40% |
| Financials | 8–14 | 5–10 | varies (use ROE instead) |
| Health Care | 15–25 | 15–25 | 10–25% |
| Consumer Staples | 18–25 | 18–25 | 8–15% |
| Industrials | 15–22 | 15–25 | 8–15% |
| Energy | 8–15 | 6–12 | 5–15% |
| Utilities | 14–18 | 10–18 | 15–25% |
| Real Estate (REITs) | use P/FFO | use P/FFO | 30–50% |
| Communication Services | 12–20 | 10–20 | 15–30% |
| Consumer Discretionary | 15–25 | 15–25 | 5–12% |
| Materials | 12–18 | 10–18 | 8–15% |

The screener accounts for this by ranking each stock **within its own sector**
rather than against the full market.

---

*This guide is for educational purposes. Always do your own research before investing.*
