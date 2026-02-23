# Patterns

Approved patterns for this codebase. Follow these. If you find yourself fighting them, update this file rather than silently diverging.

---

## General Python

### Layer Boundaries Use Typed Models, Not Raw Dicts

Data crossing a layer boundary must be a Pydantic model or a typed dataclass. Never pass raw `dict` objects between modules.

```python
# Bad
def process(data: dict) -> dict:
    ...

# Good
def process(doc: IngestedDocument) -> ExtractionResult:
    ...
```

**Why:** Catches type errors and AI hallucinations at the boundary. Models are self-documenting.

---

### Constants Live in `settings.py`

No magic numbers or hardcoded strings in business logic. All tuneable values belong in `config/settings.py`.

```python
# Bad
time.sleep(2)
model = "claude-sonnet-4-6"
max_workers = 4

# Good
from config.settings import RETRY_WAIT_SECONDS, MODEL_NAME, MAX_WORKERS
time.sleep(RETRY_WAIT_SECONDS)
```

---

### Fail Loud with Flags, Not Silent Defaults

When AI extraction is uncertain, create an `AssumptionFlag` and set confidence to `Assumed`. Never silently fill in a value without flagging it.

```python
# Bad
item.voltage = item.voltage or 480  # silent default

# Good
if item.voltage is None:
    item.voltage = 480
    flags.append(AssumptionFlag(
        field="voltage",
        assumed_value="480V",
        impact="medium",
        recommended_action="Verify voltage from one-line diagram"
    ))
    item.confidence = ConfidenceLevel.ASSUMED
```

---

### Retry All External Calls with tenacity

Any call to an external service (Anthropic API, yfinance, web requests) must have retry logic.

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
def call_api(...):
    ...
```

---

## electrical-estimator Specific

### One Prompt File per Document Type

Each document type (panel schedule, one-line, motor list, etc.) has exactly one prompt file in `ai/prompts/`. Do not put multi-type logic in a single prompt.

**Why:** Prompts are large and complex. Keeping them separate makes them easier to iterate on independently.

---

### AI Responses Are Always Parsed and Validated Before Use

Never use an AI response string directly. Always:
1. Parse the JSON
2. Validate against the Pydantic model
3. Use the validated model object

```python
# Bad
response_text = client.complete(prompt)
data = json.loads(response_text)
items = data["wire_items"]

# Good
response_text = client.complete(prompt)
result = ExtractionResult.model_validate_json(response_text)
items = result.wire_items
```

---

### Excel Writer Methods Follow a Consistent Pattern

Each BOM tab has a dedicated `_write_<tab_name>_sheet()` method in `excel_writer.py`. Each method:
1. Gets or creates the sheet
2. Writes a styled header row
3. Iterates over items and writes rows
4. Color-codes by confidence
5. Returns nothing (mutates the workbook)

---

### Session State Is a Single Dict

All Streamlit session state is stored under a single `st.session_state["session"]` dict. Never scatter state across multiple top-level keys.

```python
# Bad
st.session_state["bom"] = bom
st.session_state["cost"] = cost

# Good
st.session_state["session"]["bom"] = bom
st.session_state["session"]["cost"] = cost
```

**Why:** The entire session can be serialized to JSON for save/load by dumping one dict.

---

## stock-screener Specific

### Cache Raw Data, Compute Metrics Fresh

Always cache the raw yfinance data. Never cache computed metrics — they should be re-derived from raw data on each run so the scoring logic can be changed without a re-fetch.

```python
# Cache this:
df_raw.to_pickle("data/raw_data.pkl")

# Always recompute this:
df["pe_score"] = compute_pe_score(df["trailingPE"])
```

---

### Missing Data Is Dropped, Not Filled

If a stock is missing a required fundamental metric, drop it from the screener rather than filling with a default. A stock with missing data is not comparable.

```python
df = df.dropna(subset=["trailingPE", "freeCashflow", "returnOnEquity"])
```
