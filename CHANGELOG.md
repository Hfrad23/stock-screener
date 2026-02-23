# Changelog

Human-readable history of significant changes. Most recent at the top.

Format: `## [version or date] — Project — Description`

---

## [2026-02-22] — electrical-estimator — Phase 1 MVP Complete

**Commit:** 8291727 (local, not yet pushed to GitHub — auth expired)

### Added
- All 10 BOM tabs implemented end-to-end:
  1. Project Header (metadata + BOM summary)
  2. Wire & Cable
  3. Conduit & Fittings
  4. Boxes & Enclosures
  5. Wiring Devices
  6. Panels, MCCs & Switchgear
  7. Lighting Fixtures
  8. Grounding & Bonding
  9. Instrumentation & Controls
  10. Assumptions & Flags
- BOM summary on Project Header tab: confidence breakdown, flag counts, wire/conduit footage totals, equipment count table
- Parallel extraction with `ThreadPoolExecutor` (4 workers)
- MD5 disk cache in `.cache/` directory
- Session save/load (JSON serialization)

### Fixed
- All Pydantic v2 validation bugs:
  - Field normalizers for `confidence`, `flags`, `material`, `conduit_type`, `panel_type`, `phases`, `RPM`, `wattage`, optional floats
  - Migrated from v1 `@validator` to v2 `@field_validator` throughout

### Architecture
- Layered pipeline: ingestor → classifier → chunker → AI extraction → BOM builder → validator → Excel writer
- 5 document type parsers (PDF, DOCX, XLSX, image, DXF)
- 6 AI prompts (base system, panel schedule, one-line, area classification, scope of work, motor list)
- 15 Pydantic v2 models defining the complete data contract

---

## [2026-02-22] — stock-screener — Initial Implementation

### Added
- S&P 500 constituent fetching from Wikipedia
- Fundamental data via yfinance with pickle cache
- Metrics: P/E, P/FCF, EV/EBITDA, P/B, PEG, dividend yield, ROE, ROIC
- DCF valuation engine (5-year FCF projection, WACC 10%, terminal growth 3%)
- Composite scoring (DCF 40% / Fundamentals 35% / Quality 25%)
- Outputs: top_20_stocks.csv, top_10_dcf_undervalued.csv, per-stock charts, market overview
- Dark-mode matplotlib/seaborn charts
- Jupyter notebook version (sp500_value_screener.ipynb)
- METRICS_GUIDE.md with plain-English explanations

---

## [Upcoming] — electrical-estimator — Phase 2: Vision Pipeline

- Enable page-as-image extraction for scanned PDFs and hand-drawn one-lines
- Vision-enabled prompts for floor plans and area classification maps

## [Upcoming] — electrical-estimator — Phase 3: NEC + DXF

- Full NEC derating validator (ambient temp + bundling)
- DXF parser integration with AI extraction
- Motor ampacity calculations from NEC 430

## [Upcoming] — electrical-estimator — Phase 4: Pricing

- Distributor pricing integration
- Cost estimate column in BOM tabs
- Total project cost estimate on Project Header
