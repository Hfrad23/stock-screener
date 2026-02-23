# Architecture

## Workspace Overview

This workspace contains two independent Python tools, each living in its own directory and git repo. There is no shared library or monorepo build system — they are co-located for convenience.

```
ClaudeWorkspace/
├── electrical-estimator/   # Production AI-powered BOM tool
├── stock-screener/         # S&P 500 value analysis tool
└── memory/                 # Session & project notes
```

---

## Project 1: electrical-estimator

### Purpose
A local Streamlit desktop app for industrial electrical estimators (oil & gas focus). Users upload bid package documents; Claude AI extracts electrical data and outputs a professional 10-tab Excel Bill of Materials with confidence labeling and NEC 2023 derating calculations.

### Architecture: Layered Pipeline

```
[ User (Streamlit UI) ]
        │
        ▼
[ Pipeline Layer ]
   ingestor → classifier → chunker → context_builder
        │
        ▼
[ AI Layer ]
   client (Anthropic SDK + retry) → prompts/ → extractor (parallel, cached)
        │
        ▼
[ BOM Layer ]
   builder → deduplicator → validator (NEC) → excel_writer
        │
        ▼
[ Output: 10-tab Excel BOM ]
```

### Key Design Decisions
- **Separation of concerns:** parsing, AI extraction, BOM assembly, and rendering are fully decoupled layers.
- **Parallel extraction:** `ThreadPoolExecutor` with 4 workers processes document chunks concurrently.
- **MD5 disk cache:** AI responses are cached by hash of (prompt + content) to avoid redundant API calls across sessions.
- **Pydantic v2 models:** All data flowing between layers is validated against a strict schema (`config/bom_schema.py`). No raw dicts cross layer boundaries.
- **Confidence labeling:** Every BOM line item carries a confidence level (`Confirmed`, `Estimated`, `Assumed`) propagated through to the Excel output as color coding.
- **Fail-loud flags:** Items with uncertainty are flagged with `AssumptionFlag` records rather than silently accepted.

### Directory Structure
```
electrical-estimator/
├── app.py                  # Streamlit UI entry point
├── requirements.txt
├── .env                    # ANTHROPIC_API_KEY (not committed)
├── config/
│   ├── settings.py         # All constants (paths, model, token budgets, colors)
│   ├── bom_schema.py       # 15 Pydantic v2 models (the data contract)
│   └── nec_tables.py       # NEC 2023 ampacity tables + derating factors
├── pipeline/
│   ├── ingestor.py         # Routes files to parsers → IngestedDocument
│   ├── classifier.py       # Identifies document type (7 types)
│   ├── chunker.py          # Splits docs into ~6k-token chunks (1k overlap)
│   ├── context_builder.py  # Builds project context dict for AI calls
│   └── parsers/
│       ├── pdf_parser.py
│       ├── docx_parser.py
│       ├── xlsx_parser.py
│       ├── image_parser.py
│       └── dxf_parser.py
├── ai/
│   ├── client.py           # AnthropicClient + CostTracker + retry logic
│   ├── extractor.py        # Orchestrator: parallel extraction + caching
│   └── prompts/
│       ├── base_system.py
│       ├── panel_schedule.py
│       ├── one_line.py
│       ├── area_classification.py
│       ├── scope_of_work.py
│       └── motor_list.py
├── bom/
│   ├── builder.py          # Merges ExtractionResults → BillOfMaterials
│   ├── deduplicator.py
│   ├── validator.py        # NEC compliance + derating calculations
│   └── excel_writer.py     # Renders 10-tab Excel workbook
├── .cache/                 # MD5-keyed AI response cache (gitignored)
├── uploads/                # User-uploaded files (gitignored)
├── output/                 # Generated Excel BOMs (gitignored)
└── sessions/               # Saved session JSON files (gitignored)
```

### Data Contract: Core Models
| Model | Purpose |
|---|---|
| `IngestedDocument` | Normalized output from any parser |
| `ExtractionResult` | AI output for one chunk, validated by Pydantic |
| `BillOfMaterials` | Merged, deduplicated, validated final BOM |
| `WireCableItem` | Wire/cable line item with confidence + flags |
| `PanelItem` | Panel/MCC with nested `CircuitItem` list |
| `AssumptionFlag` | Flagged uncertainty with impact level + action |

### Supported File Types
| Extension | Parser | Notes |
|---|---|---|
| `.pdf` | PyMuPDF | Text + page images |
| `.docx` | python-docx | Paragraphs + tables |
| `.xlsx` | openpyxl | Sheet data |
| `.png/.jpg/.tiff` | Pillow | Vision pipeline |
| `.dxf` | ezdxf | Entity extraction (partial) |

---

## Project 2: stock-screener

### Purpose
S&P 500 value stock screener using fundamental metrics and DCF valuation. Identifies undervalued companies based on P/E, P/FCF, EV/EBITDA, P/B, PEG, ROE, and ROIC.

### Architecture: Single-Pass Script

```
[ Wikipedia ] → fetch S&P 500 tickers
      │
      ▼
[ yfinance ] → download fundamentals (cached in data/raw_data.pkl)
      │
      ▼
[ pandas ] → compute metrics + composite score
      │
      ▼
[ DCF Engine ] → 5-year FCF projection + terminal value
      │
      ▼
[ Output ] → CSV files + matplotlib charts
```

### Directory Structure
```
stock-screener/
├── run_screener.py         # Standalone entry point (~620 lines)
├── sp500_value_screener.ipynb  # Interactive Jupyter version
├── METRICS_GUIDE.md        # Plain-English metric explanations
├── requirements.txt
├── data/
│   └── raw_data.pkl        # yfinance cache (gitignored)
└── output/
    ├── top_20_stocks.csv
    ├── top_10_dcf_undervalued.csv
    └── stock_charts/       # Per-stock price + metrics charts
```

### Scoring Weights
| Component | Weight |
|---|---|
| DCF valuation | 40% |
| Fundamental metrics | 35% |
| Quality (ROE, ROIC) | 25% |

---

## What's Not Here (Yet)
- **No shared library:** If a utility is needed in both projects, copy it. Abstract only when the duplication is painful.
- **No CI/CD:** Both tools are local-only. No GitHub Actions, no Docker.
- **No tests:** Both projects lack automated test suites (see TESTING.md for the plan).
- **No pricing integration:** Electrical estimator pricing module is a future phase.
