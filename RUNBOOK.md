# Runbook

Operational playbook for running, debugging, and recovering from failures.

---

## electrical-estimator

### Starting the App

```bash
cd ~/ClaudeWorkspace/electrical-estimator
source .venv/bin/activate
streamlit run app.py
# or just:
estimator
```

App opens at `http://localhost:8501` in your browser.

### Normal Workflow

1. Enter project info (name, number, customer, location, estimator, date)
2. Upload bid package files (PDF, DOCX, XLSX, PNG/JPG, DXF)
3. Click **Process** — watch the extraction log and cost tracker
4. Download the Excel BOM when complete
5. Optionally: **Save Session** to resume later

### Stopping the App

`Ctrl+C` in the terminal running Streamlit.

---

### Resetting the Cache

If prompts have changed and you're getting stale AI responses:

```bash
rm -rf electrical-estimator/.cache/
```

This forces fresh AI calls on the next run. Cache rebuilds automatically.

### Clearing Uploads / Output

```bash
rm -rf electrical-estimator/uploads/*
rm -rf electrical-estimator/output/*
```

### Loading a Saved Session

In the Streamlit sidebar, click **Load Session** and select the `.json` file from `sessions/`.

---

### Common Failures

#### App won't start — `ANTHROPIC_API_KEY not set`
```
KeyError: 'ANTHROPIC_API_KEY'
```
**Fix:** Check that `.env` exists and contains a valid key.
```bash
cat electrical-estimator/.env
# Should show: ANTHROPIC_API_KEY=sk-ant-...
```

#### Pydantic validation error during extraction
```
pydantic_core.ValidationError: X validation errors for WireCableItem
```
**Cause:** AI returned a field value that doesn't match the schema (e.g., non-numeric AWG, invalid confidence string).
**Fix:** Check the extraction log for the raw JSON. Update the field validator in `config/bom_schema.py` if the AI's format is legitimate but unhandled.

#### Rate limit error from Anthropic
```
anthropic.RateLimitError: 429
```
**Cause:** Too many concurrent API calls.
**Fix:** Reduce `MAX_WORKERS` in `config/settings.py` from 4 to 2. The tenacity retry logic handles transient rate limits automatically.

#### Excel file won't open — `openpyxl` error
**Cause:** Usually a None value where a string is expected in the BOM data.
**Fix:** Check `bom/excel_writer.py` for the failing tab's write method. Add a `or ""` fallback for optional fields.

#### Streamlit `Session State` errors after code changes
**Cause:** Streamlit caches session state; a schema change can make old state incompatible.
**Fix:** Clear browser storage or open a private window. In dev, add `st.session_state.clear()` temporarily.

#### DXF files produce no output
**Status:** DXF parser is partially implemented. Entity extraction works but the AI prompt for DXF is not yet connected.
**Workaround:** Convert DXF to PDF (via AutoCAD or an online tool) and upload the PDF instead.

---

### Updating the Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com) → API Keys
2. Create a new key
3. Update `.env`:
```bash
echo "ANTHROPIC_API_KEY=sk-ant-YOUR-NEW-KEY" > electrical-estimator/.env
```
4. Restart the app

### Pushing to GitHub (when token expires)

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens) → Generate new token (classic)
2. Scopes: `repo`, `workflow`
3. Copy the token
4. Push:
```bash
cd electrical-estimator
git remote set-url origin https://YOUR-TOKEN@github.com/Hfrad23/electrical-estimator.git
git push origin main
```

---

## stock-screener

### Running the Screener

```bash
cd ~/ClaudeWorkspace/stock-screener
python run_screener.py
```

Output files are written to `output/`.

### Forcing a Fresh Data Fetch

By default, the screener uses cached data from `data/raw_data.pkl`. To force fresh data:

```python
# In run_screener.py, set:
FORCE_REFRESH = True
```

Or delete the cache:
```bash
rm stock-screener/data/raw_data.pkl
```

### Running the Notebook

```bash
cd ~/ClaudeWorkspace/stock-screener
jupyter notebook sp500_value_screener.ipynb
```

---

### Common Failures

#### `yfinance` returns empty data for some tickers
**Cause:** Yahoo Finance occasionally drops or renames tickers.
**Fix:** The screener drops rows with missing required fields. Check `output/top_20_stocks.csv` — if it's much shorter than expected, some tickers failed silently. Add logging to diagnose.

#### `KeyError` on a fundamental metric column
**Cause:** yfinance API changed a field name.
**Fix:** Check yfinance release notes. Update the column name in `run_screener.py`.

#### `ModuleNotFoundError`
**Fix:**
```bash
pip install -r stock-screener/requirements.txt
```
