# Debugging Guide

Known gotchas, how to diagnose common failures, and useful commands.

---

## electrical-estimator

### Diagnosing Extraction Failures

The extraction log in the Streamlit UI shows each chunk's status. For a deeper look:

```python
# Temporarily add to ai/extractor.py to see raw AI responses
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# In the extraction loop:
logger.debug(f"Raw AI response:\n{response_text}")
```

**Common extraction failure patterns:**
- AI returns valid JSON but with wrong field names → Update the prompt to be more explicit about field names
- AI returns prose before the JSON → Add `"Return ONLY the JSON object, no preamble"` to the prompt
- Pydantic rejects a field value → Check the raw JSON; the AI may be returning a valid-but-unexpected format

---

### Diagnosing Pydantic Validation Errors

```
pydantic_core.ValidationError: 3 validation errors for WireCableItem
```

1. Find the exact field(s) failing in the traceback
2. Check what the AI actually returned:
   ```python
   import json
   data = json.loads(response_text)
   print(data["wire_items"][0])  # inspect the first item
   ```
3. Check the field validator in `config/bom_schema.py`
4. Add a normalization step in the `@field_validator` if the AI's format is legitimate

**Most common validator issues:**
- Confidence value case mismatch: AI returns `"confirmed"` but enum expects `"Confirmed"` → Add `.lower().capitalize()` normalization
- AWG as integer vs string: AI returns `12` but field expects `"12"` → Cast in validator
- Optional float as string: AI returns `"N/A"` for a float field → Return `None` for non-numeric strings

---

### Diagnosing Cache Issues

If results look stale after prompt changes:

```bash
# View cache size
ls -la electrical-estimator/.cache/ | wc -l

# Clear the cache
rm -rf electrical-estimator/.cache/
```

The cache key is MD5 of (prompt text + chunk content). Any prompt change creates new cache keys automatically — old entries just become orphaned (not incorrect). Clear periodically to reclaim disk space.

---

### Diagnosing Cost Overruns

The sidebar shows running cost. If a run is unexpectedly expensive:

1. Check chunk count: Large PDFs with many pages create many chunks
2. Check `MAX_CHUNK_CHARS` in `settings.py` — lower it to reduce tokens per chunk
3. Check `MAX_WORKERS` — fewer workers = fewer concurrent calls = easier to monitor
4. Check if vision mode is inadvertently active (vision tokens cost more)

---

### Streamlit Session State Debugging

```python
# Add anywhere in app.py to inspect current state:
st.write(st.session_state["session"])
```

If session state becomes corrupt after a code change:
1. Open a new private/incognito browser tab
2. Or in terminal: `Ctrl+C` → restart Streamlit

---

### Excel File Won't Open

1. Check for `None` values in writer methods:
   ```python
   # In excel_writer.py, inspect the failing sheet's write loop
   for item in bom.wire_items:
       print(item.model_dump())  # find which field is None
   ```
2. Check for invalid characters in sheet names (Excel doesn't allow `/ \ ? * [ ]`)
3. Check that `openpyxl` version is >= 3.1.0

---

### DXF Files Producing No Output

**Root cause:** DXF parser in `pipeline/parsers/dxf_parser.py` extracts entities but there is no AI prompt connected to DXF content yet.

**Workaround:** Export DXF to PDF from AutoCAD/LibreCAD and upload the PDF.

**To implement DXF extraction:**
1. Create `ai/prompts/dxf_diagram.py`
2. Route `file_type == "dxf"` in `ai/extractor.py` to the new prompt
3. Parse DXF entity text into a chunk suitable for the prompt

---

## stock-screener

### Empty or Short Output (fewer than 20 stocks)

**Cause:** yfinance returned `NaN` for required fields on many tickers; they were dropped.

**Diagnose:**
```python
# Add to run_screener.py after fetching:
print(f"Tickers with missing PE: {df['trailingPE'].isna().sum()}")
print(f"Tickers with missing FCF: {df['freeCashflow'].isna().sum()}")
```

**Fix options:**
- Relax the `dropna(subset=[...])` to only require the most critical fields
- Add fallback logic for secondary metrics (e.g., use P/E if P/FCF is missing)

---

### yfinance `KeyError` on a Metric Column

**Cause:** Yahoo Finance changed a field name in their API.

**Check current field names:**
```python
import yfinance as yf
ticker = yf.Ticker("AAPL")
print(ticker.info.keys())
```

Update the column reference in `run_screener.py` to match.

---

### Jupyter Notebook Not Updating

If the notebook shows stale output after changing `run_screener.py`:
1. **Kernel → Restart & Run All**
2. Or clear all outputs: **Cell → All Output → Clear**

---

## General Python

### Finding Where a Value Comes From

```python
import traceback

# Add a breakpoint at the suspicious location:
breakpoint()  # drops into pdb

# Or add a print with context:
import inspect
print(f"[{inspect.stack()[0].filename}:{inspect.stack()[0].lineno}] value={value}")
```

### Checking Installed Package Versions

```bash
pip show anthropic pydantic streamlit openpyxl
```

### Resetting the Virtual Environment

```bash
cd electrical-estimator
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
