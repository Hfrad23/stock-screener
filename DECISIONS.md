# Architecture Decision Records (ADRs)

Decisions are recorded here with context and rationale so future sessions don't relitigate them. Add a new entry every time a significant technical choice is made.

---

## ADR-001: Streamlit for the estimator UI

**Status:** Accepted
**Date:** 2026-02-22
**Project:** electrical-estimator

**Context:** Needed a UI layer for a local desktop tool. Options included Flask, FastAPI + React, tkinter, and Streamlit.

**Decision:** Use Streamlit.

**Rationale:**
- Tool is used locally, not deployed to a server. Browser-based but single-user.
- Streamlit requires no frontend code — pure Python. Faster to build and maintain.
- Session state (`st.session_state`) is sufficient for the multi-step workflow.
- Rapid iteration: adding a new UI element is one line.

**Trade-offs:**
- Streamlit reruns the entire script on each interaction — requires careful state management.
- Not suitable if the tool ever becomes multi-user or cloud-hosted (would need FastAPI + proper auth).

---

## ADR-002: Pydantic v2 as the data contract between layers

**Status:** Accepted
**Date:** 2026-02-22
**Project:** electrical-estimator

**Context:** AI responses are JSON strings that need validation before being used downstream. Raw dicts are fragile and lead to silent failures.

**Decision:** All data flowing between pipeline layers is typed with Pydantic v2 models defined in `config/bom_schema.py`.

**Rationale:**
- Validation catches AI hallucinations (e.g., non-numeric AWG, invalid confidence values) at the boundary.
- Models serve as living documentation of the data contract.
- Pydantic v2 is significantly faster than v1.
- Field validators handle normalization (e.g., "confirmed" → `Confirmed`, "16 AWG" → `16`).

**Trade-offs:**
- Pydantic v2 migration from v1 had breaking changes (validators use `@field_validator`, not `@validator`). All bugs fixed as of commit 8291727.
- Model changes require updating multiple layers. Keep models stable; add optional fields rather than removing.

---

## ADR-003: MD5 disk cache for AI responses

**Status:** Accepted
**Date:** 2026-02-22
**Project:** electrical-estimator

**Context:** AI extraction is the slowest and most expensive part of the pipeline. Re-processing the same documents in dev was costly.

**Decision:** Cache AI responses to `.cache/` directory using MD5 hash of (prompt text + chunk content) as the key.

**Rationale:**
- Eliminates redundant API calls when re-running on the same documents.
- Survives Python process restarts (disk-based, not in-memory).
- Zero dependencies — just `hashlib` + file I/O.
- Cache is gitignored to avoid committing API response data.

**Trade-offs:**
- Cache is never invalidated automatically. If prompts change, old cache entries become stale. Clear `.cache/` manually after prompt changes.
- Not suitable for production multi-user use (would need a shared cache store).

---

## ADR-004: Parallel extraction with ThreadPoolExecutor (4 workers)

**Status:** Accepted
**Date:** 2026-02-22
**Project:** electrical-estimator

**Context:** Large bid packages may have 20+ document chunks. Sequential processing was too slow.

**Decision:** Use `ThreadPoolExecutor` with `max_workers=4` in `ai/extractor.py`.

**Rationale:**
- Anthropic API calls are I/O-bound, not CPU-bound. Threads are appropriate (vs. multiprocessing).
- 4 workers balances throughput against rate limits.
- Simple to implement and reason about with `concurrent.futures`.

**Trade-offs:**
- Rate limits: hitting Anthropic API limits will surface as errors. tenacity retry handles transient failures.
- Thread safety: `CostTracker` updates must be thread-safe. Currently uses a simple counter — acceptable for 4 threads.

---

## ADR-005: claude-sonnet-4-6 as the extraction model

**Status:** Accepted
**Date:** 2026-02-22
**Project:** electrical-estimator

**Context:** Needed a model capable of reading technical electrical documents (panel schedules, one-lines, NEC specs) and returning structured JSON.

**Decision:** Use `claude-sonnet-4-6` for all extraction calls.

**Rationale:**
- Sonnet 4.6 has the best balance of accuracy and cost for structured extraction tasks.
- Strong JSON adherence and instruction-following for the base system prompt.
- Vision capability for image-based documents (floor plans, scanned one-lines).

**Trade-offs:**
- Cost: $3/M input tokens, $15/M output tokens. Large documents get expensive. Token budgets in `settings.py` cap each call.
- Opus would be more accurate but 5x the cost — not justified for extraction tasks.

---

## ADR-006: yfinance + Wikipedia as the data source for stock screener

**Status:** Accepted
**Date:** 2026-02-22
**Project:** stock-screener

**Context:** Needed a free, reliable source for S&P 500 constituents and fundamental data.

**Decision:** Fetch S&P 500 tickers from Wikipedia; pull fundamentals from yfinance.

**Rationale:**
- yfinance is free and covers the core fundamental metrics needed.
- Wikipedia's S&P 500 table is regularly maintained and easy to scrape with BeautifulSoup.
- No API key required — zero setup friction.

**Trade-offs:**
- yfinance is unofficial and can break when Yahoo Finance changes its API. Not suitable for production financial systems.
- Data quality varies by ticker. Missing or stale data is handled by dropping rows with `NaN` for required fields.
- No real-time data — all fundamentals are end-of-day.

---

## ADR-007: Composite scoring with weighted DCF

**Status:** Accepted
**Date:** 2026-02-22
**Project:** stock-screener

**Decision:** Score stocks using a composite of DCF (40%), fundamentals (35%), and quality (25%) rather than any single metric.

**Rationale:**
- No single metric reliably identifies undervalued stocks. Combining reduces false positives.
- DCF gets the highest weight because it directly models intrinsic value.
- Quality metrics (ROE, ROIC) prevent picking value traps (cheap for a reason).

**Trade-offs:**
- DCF is sensitive to WACC and growth assumptions. A 10% WACC and 3% terminal growth are reasonable defaults for a 5-year horizon but are not universal.
- Weights are hardcoded. Parameterizing them is a future enhancement.
