# Testing

Testing strategy, what needs what kind of test, and how to run them.

---

## Current State

Neither project has an automated test suite yet. This file documents the plan and what to add when building tests.

---

## Testing Philosophy

- **Test behavior, not implementation.** Tests should verify outputs given inputs, not assert internal implementation details.
- **Prioritize high-value tests.** Test the things that break silently: data transformations, Pydantic models, NEC calculations.
- **Don't mock the AI.** Use cached responses (`.cache/`) or sample fixtures for AI-dependent tests. Don't mock `anthropic.Client`.

---

## electrical-estimator: Testing Priorities

### Tier 1 — Must Have (test these first)

| What | Why | Test Type |
|---|---|---|
| Pydantic model validators | Validation bugs caused silent failures | Unit |
| NEC ampacity + derating calculations | Wrong values = code violation | Unit |
| BOM builder merge logic | Deduplication must be correct | Unit |
| Chunker output | Chunk overlap must not break JSON boundaries | Unit |
| Excel writer — sheet structure | BOM tabs must have correct column layout | Integration |

### Tier 2 — High Value

| What | Test Type |
|---|---|
| Ingestor routing (correct parser per extension) | Unit |
| Classifier — document type detection | Unit (with fixture filenames + content) |
| Full pipeline with a sample PDF (no AI) | Integration |
| Session save/load round-trip | Integration |

### Tier 3 — Nice to Have

| What | Test Type |
|---|---|
| Cost tracker accumulation | Unit |
| Full end-to-end with a cached AI response | E2E |

---

## electrical-estimator: Sample Test Structures

### Unit Test: Pydantic Model Validator

```python
# tests/test_bom_schema.py
import pytest
from config.bom_schema import WireCableItem, ConfidenceLevel

def test_confidence_normalizes_lowercase():
    item = WireCableItem(confidence="confirmed")
    assert item.confidence == ConfidenceLevel.CONFIRMED

def test_confidence_normalizes_mixed_case():
    item = WireCableItem(confidence="ESTIMATED")
    assert item.confidence == ConfidenceLevel.ESTIMATED

def test_optional_awg_defaults_to_none():
    item = WireCableItem()
    assert item.awg is None
```

### Unit Test: NEC Derating

```python
# tests/test_nec_tables.py
from config.nec_tables import get_derated_ampacity

def test_75c_copper_12awg():
    # NEC Table 310.15(B)(16): 12 AWG Cu 75°C = 20A
    assert get_derated_ampacity("12", "Cu", 75) == 20

def test_ambient_temp_derating_at_40c():
    # 40°C ambient = correction factor 1.0 (no derating from 30°C baseline)
    base = get_derated_ampacity("12", "Cu", 75)
    derated = get_derated_ampacity("12", "Cu", 75, ambient_temp=40)
    assert derated < base
```

### Integration Test: Pipeline (no AI)

```python
# tests/test_pipeline.py
from pathlib import Path
from pipeline.ingestor import ingest_file

def test_pdf_ingestor_returns_content():
    sample = Path("tests/sample_docs/sample_panel_schedule.pdf")
    doc = ingest_file(sample)
    assert doc.content
    assert doc.file_type == "pdf"
```

---

## stock-screener: Testing Priorities

### Tier 1

| What | Test Type |
|---|---|
| Metric computation (P/E, P/FCF, EV/EBITDA) | Unit |
| DCF calculation with known inputs | Unit |
| Composite score weights sum to 1.0 | Unit |

### Tier 1 Example

```python
# tests/test_metrics.py
from run_screener import compute_dcf_value

def test_dcf_positive_fcf():
    # Known input → known output
    value = compute_dcf_value(fcf=1_000_000, growth_rate=0.10, wacc=0.10, terminal_growth=0.03)
    assert value > 0

def test_dcf_zero_fcf_returns_zero():
    value = compute_dcf_value(fcf=0, growth_rate=0.10, wacc=0.10, terminal_growth=0.03)
    assert value == 0
```

---

## Running Tests

```bash
# Install pytest (not yet in requirements.txt)
pip install pytest

# Run all tests
pytest

# Run a specific file
pytest tests/test_bom_schema.py

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x
```

---

## Sample Documents for Integration Tests

Place test fixtures in `electrical-estimator/tests/sample_docs/`:

| File | Purpose |
|---|---|
| `sample_panel_schedule.pdf` | Panel schedule extraction test |
| `sample_one_line.pdf` | One-line diagram test |
| `sample_motor_list.xlsx` | Motor list XLSX extraction |
| `sample_scope.docx` | Scope of work text extraction |

---

## What Not to Test

- Streamlit UI rendering (no good way to unit test Streamlit widgets)
- Anthropic API responses (test against cached fixtures instead)
- yfinance data retrieval (mocking an unofficial API is fragile)
- Excel file visual formatting (test structure, not pixel-level appearance)
