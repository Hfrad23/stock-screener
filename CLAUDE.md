# Claude Code Instructions

## On Every Session Start

Read the following files before doing any work:

1. **`ARCHITECTURE.md`** — How the projects are structured. Read this to understand the codebase before touching any code.
2. **`DECISIONS.md`** — Why key technical choices were made. Never relitigate these without good reason.
3. **`PATTERNS.md`** — Required coding patterns for this workspace. Follow these strictly.
4. **`WIP.md`** — Current working state. What's in progress, what's next.

Read these on-demand when relevant:

- **`DEBUGGING.md`** — When diagnosing a failure or unexpected behavior
- **`SECURITY.md`** — Before handling API keys, file uploads, or any external data
- **`STYLE.md`** — Before writing new code or reviewing existing code
- **`GLOSSARY.md`** — When electrical or finance domain terms are unclear
- **`TESTING.md`** — Before writing tests or assessing test coverage
- **`POSTMORTEMS.md`** — Before making changes to an area that has previously failed

## Behavior Rules

- Do not commit code unless explicitly asked.
- Do not push to GitHub unless explicitly asked.
- Do not generate or guess URLs.
- Keep `memory/MEMORY.md` updated with stable facts after each session. Do not write session-specific context there.
- Update `WIP.md` at the end of each session to reflect current state.
- Update `POSTMORTEMS.md` when a significant bug is diagnosed and fixed.
- Update `DECISIONS.md` when a significant architectural choice is made.
- Update `CHANGELOG.md` when features are completed or significant changes are made.

## Project Context

This workspace belongs to **Hil** — industrial electrical contractor, oil & gas, US Central timezone.

**Active projects:**
- `electrical-estimator/` — Production Streamlit app. Primary focus.
- `stock-screener/` — S&P 500 value analysis tool. Secondary.

**Preferred style:** Direct, no fluff. No emojis unless asked. Concise responses.
