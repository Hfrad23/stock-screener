"""
S&P 500 Value Screener — standalone runner
Outputs top 20 stocks to console + saves CSVs and charts.
"""

import warnings
warnings.filterwarnings('ignore')

import os, time, pickle, requests
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib
matplotlib.use('Agg')   # non-interactive backend for script mode
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from bs4 import BeautifulSoup
from datetime import datetime

# ── Plot style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#0f1117', 'axes.facecolor': '#0f1117',
    'axes.edgecolor': '#333',      'axes.labelcolor': '#ccc',
    'xtick.color': '#aaa',         'ytick.color': '#aaa',
    'text.color': '#eee',          'grid.color': '#222',
    'grid.linestyle': '--',        'figure.dpi': 120,
})

# ── Parameters ───────────────────────────────────────────────────────────────
WACC            = 0.10
TERMINAL_GROWTH = 0.03
PROJECTION_YEARS= 5
MAX_FCF_GROWTH  = 0.25
MIN_FCF_GROWTH  = -0.05
MIN_ROE         = 0.05
MIN_ROIC        = 0.04
MAX_DEBT_EQUITY = 5.0
W_DCF, W_FUND, W_QUAL = 0.40, 0.35, 0.25

os.makedirs('data',   exist_ok=True)
os.makedirs('output', exist_ok=True)

CACHE_FILE    = 'data/raw_data.pkl'
FORCE_REFRESH = False

# ════════════════════════════════════════════════════════════════════════════
# 1. S&P 500 tickers
# ════════════════════════════════════════════════════════════════════════════
def get_sp500_tickers():
    url     = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/120.0.0.0 Safari/537.36'}
    resp    = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    import io
    tables  = pd.read_html(io.StringIO(resp.text), attrs={'id': 'constituents'})
    if not tables:
        tables = pd.read_html(io.StringIO(resp.text))
    df = tables[0]
    df.columns = df.columns.str.strip()
    # Identify columns flexibly (Wikipedia occasionally renames them)
    sym_col  = next(c for c in df.columns if any(k in c.lower() for k in ['symbol','ticker']))
    name_col = next(c for c in df.columns if any(k in c.lower() for k in ['security','company','name']))
    sec_col  = next(c for c in df.columns if 'sector' in c.lower())
    ind_col  = next(c for c in df.columns if any(k in c.lower() for k in ['industry','sub-industry','sub industry']))
    df = df[[sym_col, name_col, sec_col, ind_col]].copy()
    df.columns = ['ticker','name','sector','industry']
    df['ticker'] = df['ticker'].str.replace('.', '-', regex=False)
    return df

print("Fetching S&P 500 constituent list …")
sp500 = get_sp500_tickers()
print(f"  → {len(sp500)} companies across {sp500['sector'].nunique()} sectors\n")

# ════════════════════════════════════════════════════════════════════════════
# 2. Data helpers
# ════════════════════════════════════════════════════════════════════════════
def safe_get(d, *keys, default=np.nan):
    for k in keys:
        try:
            d = d.get(k, default) if isinstance(d, dict) else d[k]
        except Exception:
            return default
    return d if d is not None else default

def extract_ttm_fcf(cf):
    if cf is None or cf.empty: return np.nan
    try:
        ocf = capex = None
        for lbl in ['Operating Cash Flow','Total Cash From Operating Activities']:
            if lbl in cf.index: ocf = cf.loc[lbl]; break
        for lbl in ['Capital Expenditure','Capital Expenditures']:
            if lbl in cf.index: capex = cf.loc[lbl]; break
        if ocf is None: return np.nan
        return float(ocf.iloc[0]) + (float(capex.iloc[0]) if capex is not None else 0)
    except Exception:
        return np.nan

def fcf_cagr(cf):
    if cf is None or cf.empty: return np.nan
    try:
        ocf = capex = None
        for lbl in ['Operating Cash Flow','Total Cash From Operating Activities']:
            if lbl in cf.index: ocf = cf.loc[lbl]; break
        for lbl in ['Capital Expenditure','Capital Expenditures']:
            if lbl in cf.index: capex = cf.loc[lbl]; break
        if ocf is None or len(ocf) < 2: return np.nan
        o = ocf.values.astype(float)
        c = capex.values.astype(float) if capex is not None else np.zeros(len(o))
        fcf = o + c
        n   = min(len(fcf), 4)
        s, e = fcf[n-1], fcf[0]
        if s <= 0 or e <= 0: return np.nan
        return (e / s) ** (1 / (n - 1)) - 1
    except Exception:
        return np.nan

def fetch_one(ticker):
    try:
        t    = yf.Ticker(ticker)
        info = t.info or {}
        cf   = t.cashflow

        price       = safe_get(info,'currentPrice') or safe_get(info,'regularMarketPrice')
        market_cap  = safe_get(info,'marketCap')
        shares      = safe_get(info,'sharesOutstanding')
        ttm_fcf     = extract_ttm_fcf(cf)
        p_fcf       = market_cap / ttm_fcf if (market_cap and ttm_fcf and ttm_fcf > 0) else np.nan

        return {
            'ticker':         ticker,
            'price':          price,
            'market_cap':     market_cap,
            'shares':         shares,
            'pe':             safe_get(info,'trailingPE'),
            'pb':             safe_get(info,'priceToBook'),
            'peg':            safe_get(info,'pegRatio'),
            'ev_ebitda':      safe_get(info,'enterpriseToEbitda'),
            'p_fcf':          p_fcf,
            'roe':            safe_get(info,'returnOnEquity'),
            'roa':            safe_get(info,'returnOnAssets'),
            'debt_equity':    safe_get(info,'debtToEquity'),
            'total_debt':     safe_get(info,'totalDebt'),
            'cash':           safe_get(info,'totalCash'),
            'ttm_fcf':        ttm_fcf,
            'fcf_growth':     fcf_cagr(cf),
            'op_margins':     safe_get(info,'operatingMargins'),
            'profit_margins': safe_get(info,'profitMargins'),
        }
    except Exception as e:
        return {'ticker': ticker}

# ════════════════════════════════════════════════════════════════════════════
# 3. Fetch (with cache)
# ════════════════════════════════════════════════════════════════════════════
if os.path.exists(CACHE_FILE) and not FORCE_REFRESH:
    with open(CACHE_FILE,'rb') as f:
        records = pickle.load(f)
    print(f"Loaded cached data ({len(records)} records). Delete data/raw_data.pkl to refresh.\n")
else:
    tickers = sp500['ticker'].tolist()
    print(f"Fetching {len(tickers)} tickers from Yahoo Finance …")
    print("  (≈0.8s per ticker — estimated 7–10 min total)\n")
    records = []
    for i, tk in enumerate(tickers):
        records.append(fetch_one(tk))
        time.sleep(0.8)
        if (i + 1) % 25 == 0:
            pct = (i + 1) / len(tickers) * 100
            print(f"  {i+1:>3}/{len(tickers)}  [{pct:5.1f}%]  last: {tk}", flush=True)
            with open(CACHE_FILE,'wb') as f:
                pickle.dump(records, f)
    with open(CACHE_FILE,'wb') as f:
        pickle.dump(records, f)
    print("\n✓ Fetch complete — data cached.\n")

# ════════════════════════════════════════════════════════════════════════════
# 4. Build DataFrame
# ════════════════════════════════════════════════════════════════════════════
df = pd.DataFrame(records).merge(sp500, on='ticker', how='left')
df = df[df['price'].notna() & df['market_cap'].notna()]

num_cols = ['pe','pb','peg','ev_ebitda','p_fcf','roe','roa',
            'debt_equity','ttm_fcf','fcf_growth','op_margins','profit_margins',
            'price','market_cap','total_debt','cash','shares']
for c in num_cols:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors='coerce')

# yfinance reports debtToEquity as a percentage (e.g. 74.3 = 74.3% D/E)
# Always normalise to ratio form for consistent thresholds
df['debt_equity'] = df['debt_equity'] / 100

print(f"Universe after cleaning: {len(df)} stocks\n")

# ════════════════════════════════════════════════════════════════════════════
# 5. DCF
# ════════════════════════════════════════════════════════════════════════════
def dcf_row(row):
    fcf, shares, price = row.get('ttm_fcf'), row.get('shares'), row.get('price')
    cash   = row.get('cash') or 0
    debt   = row.get('total_debt') or 0
    fcf_g  = row.get('fcf_growth')
    if any(pd.isna(x) for x in [fcf, shares, price]) or shares<=0 or price<=0 or fcf<=0:
        return pd.Series({'dcf_value': np.nan, 'margin_of_safety': np.nan})
    g = np.clip(fcf_g if not pd.isna(fcf_g) else 0.05, MIN_FCF_GROWTH, MAX_FCF_GROWTH)
    pv = sum(fcf*(1+g)**yr / (1+WACC)**yr for yr in range(1, PROJECTION_YEARS+1))
    tv = fcf*(1+g)**PROJECTION_YEARS*(1+TERMINAL_GROWTH) / (WACC - TERMINAL_GROWTH)
    eq = pv + tv/(1+WACC)**PROJECTION_YEARS + cash - debt
    if eq <= 0:
        return pd.Series({'dcf_value': np.nan, 'margin_of_safety': np.nan})
    iv  = eq / shares
    mos = (iv - price) / iv
    return pd.Series({'dcf_value': round(iv,2), 'margin_of_safety': round(mos,4)})

print("Running DCF on all stocks …")
df = pd.concat([df, df.apply(dcf_row, axis=1)], axis=1)
print(f"  DCF computed for {df['margin_of_safety'].notna().sum()} stocks\n")

# ════════════════════════════════════════════════════════════════════════════
# 6. Scoring
# ════════════════════════════════════════════════════════════════════════════
def pct_rank(series, sector, ascending=True):
    result = pd.Series(np.nan, index=series.index)
    for sec in sector.unique():
        mask  = sector == sec
        sub   = series[mask]
        valid = sub.notna()
        if valid.sum() < 3: continue
        ranked = sub[valid].rank(pct=True, ascending=ascending)
        result[valid & mask] = 1 - ranked + ranked.min() if ascending else ranked
    mn, mx = result.min(), result.max()
    if mx > mn:
        result = (result - mn) / (mx - mn)
    return result

sec = df['sector'].fillna('Unknown')

df['s_pe']       = pct_rank(df['pe'].clip(0,100),       sec, True)
df['s_pfcf']     = pct_rank(df['p_fcf'].clip(0,150),    sec, True)
df['s_ev_ebitda']= pct_rank(df['ev_ebitda'].clip(0,60), sec, True)
df['s_pb']       = pct_rank(df['pb'].clip(0,20),        sec, True)
df['s_peg']      = pct_rank(df['peg'].clip(0,5),        sec, True)
df['fund_score'] = df[['s_pe','s_pfcf','s_ev_ebitda','s_pb','s_peg']].mean(axis=1, skipna=True)

df['s_roe']      = pct_rank(df['roe'].clip(-0.5, 1),      sec, False)
df['s_roa']      = pct_rank(df['roa'].clip(-0.5, 1),      sec, False)
df['s_margin']   = pct_rank(df['op_margins'].clip(-1, 1),  sec, False)
df['s_debt']     = pct_rank(df['debt_equity'].clip(0, 10), sec, True)
df['s_fcf_pos']  = (df['ttm_fcf'] > 0).astype(float)
df['qual_score'] = df[['s_roe','s_roa','s_margin','s_debt','s_fcf_pos']].mean(axis=1, skipna=True)

mos_c = df['margin_of_safety'].clip(-1, 1)
df['dcf_score'] = ((mos_c + 1) / 2).fillna(0.5)

df['composite'] = W_DCF*df['dcf_score'] + W_FUND*df['fund_score'] + W_QUAL*df['qual_score']

# ════════════════════════════════════════════════════════════════════════════
# 7. Quality gate + rank
# ════════════════════════════════════════════════════════════════════════════
gate = (
    (df['roe'].fillna(0)          >= MIN_ROE)  &
    (df['debt_equity'].fillna(99) <= MAX_DEBT_EQUITY) &
    (df['ttm_fcf'].fillna(-1)     > 0) &
    (df['pe'].fillna(0)           > 0)
)
qualified = df[gate].copy()
print(f"Stocks passing quality gate: {len(qualified)} / {len(df)}\n")

ranked  = qualified.sort_values('composite', ascending=False).reset_index(drop=True)
ranked['rank'] = ranked.index + 1
top20   = ranked.head(20).copy()

# ════════════════════════════════════════════════════════════════════════════
# 8. Console output
# ════════════════════════════════════════════════════════════════════════════
DIVIDER = '─' * 110
print(DIVIDER)
print(f"  S&P 500 VALUE SCREENER — TOP 20 STOCKS  |  5-Year Horizon  |  {datetime.today().strftime('%B %d, %Y')}")
print(DIVIDER)
print(f"  {'#':<4} {'Ticker':<7} {'Company':<28} {'Sector':<26} "
      f"{'Price':>7} {'DCF Val':>8} {'MoS':>6} "
      f"{'P/E':>6} {'P/FCF':>6} {'EV/EBITDA':>10} {'ROE':>6} {'Score':>7}")
print(DIVIDER)

for _, r in top20.iterrows():
    mos   = f"{r['margin_of_safety']:.1%}"  if pd.notna(r.get('margin_of_safety')) else '  N/A'
    dcfv  = f"${r['dcf_value']:.0f}"         if pd.notna(r.get('dcf_value'))        else '   N/A'
    pe    = f"{r['pe']:.1f}"                 if pd.notna(r.get('pe'))               else '  N/A'
    pfcf  = f"{r['p_fcf']:.1f}"             if pd.notna(r.get('p_fcf'))            else '  N/A'
    eveb  = f"{r['ev_ebitda']:.1f}"          if pd.notna(r.get('ev_ebitda'))        else '  N/A'
    roe   = f"{r['roe']:.1%}"               if pd.notna(r.get('roe'))              else '  N/A'
    name  = str(r.get('name',''))[:27]
    sec_s = str(r.get('sector',''))[:25]
    print(f"  {int(r['rank']):<4} {r['ticker']:<7} {name:<28} {sec_s:<26} "
          f"${r['price']:>6.2f} {dcfv:>8} {mos:>6} "
          f"{pe:>6} {pfcf:>6} {eveb:>10} {roe:>6} {r['composite']:>7.4f}")

print(DIVIDER)
print(f"\n  Weights: DCF {W_DCF:.0%}  |  Fundamentals {W_FUND:.0%}  |  Quality {W_QUAL:.0%}")
print(f"  DCF: WACC={WACC:.0%}, terminal growth={TERMINAL_GROWTH:.0%}, {PROJECTION_YEARS}-yr horizon\n")

# ════════════════════════════════════════════════════════════════════════════
# 9. Save CSV
# ════════════════════════════════════════════════════════════════════════════
top20.to_csv('output/top20_value_stocks.csv', index=False)
ranked.to_csv('output/full_ranking.csv', index=False)
print("✓ CSVs saved to output/\n")

# ════════════════════════════════════════════════════════════════════════════
# 10. Charts
# ════════════════════════════════════════════════════════════════════════════
print("Generating charts …")

# Chart 1: Composite scores
fig, ax = plt.subplots(figsize=(12, 7))
colors = plt.cm.YlOrRd(np.linspace(0.4, 0.9, len(top20)))
ax.barh(top20['ticker'][::-1], top20['composite'][::-1],
        color=colors[::-1], edgecolor='none', height=0.7)
for i, (_, r) in enumerate(top20[::-1].iterrows()):
    ax.text(r['composite'] + 0.002, i, f"{r['composite']:.4f}",
            va='center', ha='left', fontsize=8, color='#aaa')
ax.set_xlabel('Composite Score')
ax.set_title('Top 20 S&P 500 Value Stocks — 5-Year Horizon', fontsize=14, pad=15)
ax.spines[['top','right']].set_visible(False)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('output/top20_scores.png', dpi=150, bbox_inches='tight')
plt.close()

# Chart 2: Stacked score breakdown
fig, ax = plt.subplots(figsize=(13, 7))
x = np.arange(len(top20))
w = 0.65
b1 = ax.bar(x, top20['dcf_score']*W_DCF,  width=w, label=f'DCF ({W_DCF:.0%})',          color='#e67e22')
b2 = ax.bar(x, top20['fund_score']*W_FUND, width=w, bottom=top20['dcf_score']*W_DCF,
            label=f'Fundamentals ({W_FUND:.0%})', color='#3498db')
bot = top20['dcf_score']*W_DCF + top20['fund_score']*W_FUND
b3 = ax.bar(x, top20['qual_score']*W_QUAL, width=w, bottom=bot,
            label=f'Quality ({W_QUAL:.0%})', color='#2ecc71')
ax.set_xticks(x)
ax.set_xticklabels(top20['ticker'], rotation=45, ha='right', fontsize=9)
ax.set_ylabel('Weighted Score')
ax.set_title('Score Breakdown by Pillar — Top 20', fontsize=13, pad=12)
ax.legend(loc='upper right', framealpha=0.2)
ax.spines[['top','right']].set_visible(False)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('output/score_breakdown.png', dpi=150, bbox_inches='tight')
plt.close()

# Chart 3: Price vs DCF
p_df = top20[top20['dcf_value'].notna()].copy()
fig, ax = plt.subplots(figsize=(12, 6))
x = np.arange(len(p_df)); w = 0.35
ax.bar(x-w/2, p_df['price'],     width=w, label='Current Price',        color='#3498db', alpha=0.85)
ax.bar(x+w/2, p_df['dcf_value'], width=w, label='DCF Intrinsic Value',  color='#e67e22', alpha=0.85)
ax.set_xticks(x)
ax.set_xticklabels(p_df['ticker'], rotation=45, ha='right', fontsize=9)
ax.set_ylabel('Price ($)')
ax.set_title('Current Price vs. DCF Intrinsic Value — Top 20', fontsize=13, pad=12)
ax.legend(framealpha=0.2)
ax.spines[['top','right']].set_visible(False)
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('output/price_vs_dcf.png', dpi=150, bbox_inches='tight')
plt.close()

# Chart 4: Valuation heatmap
hm_cols     = ['pe','p_fcf','ev_ebitda','pb','peg']
hm_col_lbls = ['P/E','P/FCF','EV/EBITDA','P/B','PEG']
hm_df = top20.set_index('ticker')[hm_cols].apply(pd.to_numeric, errors='coerce').dropna(how='all')
if not hm_df.empty:
    nm_df = hm_df.copy()
    for c in hm_cols:
        mn, mx = nm_df[c].min(), nm_df[c].max()
        if pd.notna(mn) and pd.notna(mx) and mx > mn:
            nm_df[c] = 1 - (nm_df[c] - mn) / (mx - mn)
    fig, ax = plt.subplots(figsize=(10, 9))
    sns.heatmap(nm_df, annot=hm_df.round(1), fmt='.1f', cmap='RdYlGn',
                linewidths=0.5, linecolor='#222', ax=ax, cbar=False, annot_kws={'size':9})
    ax.set_title('Valuation Ratios — Top 20 (Green = Cheaper)', fontsize=12, pad=10)
    ax.set_xticklabels(hm_col_lbls, fontsize=10)
    plt.tight_layout()
    plt.savefig('output/ratios_heatmap.png', dpi=150, bbox_inches='tight')
    plt.close()

print("✓ Charts saved to output/")
print("\nDone.")
