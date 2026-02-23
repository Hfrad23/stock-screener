# Onboarding

Everything needed to get a new session (or new developer) productive in this workspace.

---

## System Requirements

- macOS (developed on Darwin 25.3.0)
- Python 3.9+
- pip
- Git
- A terminal with bash or zsh

---

## First-Time Setup

### 1. Clone the Workspace

```bash
git clone https://github.com/Hfrad23/electrical-estimator.git ~/ClaudeWorkspace/electrical-estimator
# stock-screener is local only — copy from existing machine or recreate
```

### 2. Set Up the electrical-estimator

```bash
cd ~/ClaudeWorkspace/electrical-estimator
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create the `.env` file:
```bash
echo "ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE" > .env
```

Get your API key from [console.anthropic.com](https://console.anthropic.com).

Verify it works:
```bash
streamlit run app.py
```

### 3. Set Up the stock-screener

```bash
cd ~/ClaudeWorkspace/stock-screener
pip install -r requirements.txt
python run_screener.py
```

No API key needed for the screener.

### 4. Set Up Shell Aliases

Add to `~/.bash_profile` or `~/.zshrc`:

```bash
# Launch Claude Code from workspace
alias claude-code='cd ~/ClaudeWorkspace && claude'

# Launch the electrical estimator
alias estimator='cd ~/ClaudeWorkspace/electrical-estimator && source .venv/bin/activate && streamlit run app.py'
```

Reload your shell:
```bash
source ~/.bash_profile
# or
source ~/.zshrc
```

---

## Understanding the Workspace

### Read These First
1. **`ARCHITECTURE.md`** — How each project is structured and why
2. **`DECISIONS.md`** — Key technical choices and their rationale
3. **`PATTERNS.md`** — Coding patterns to follow in this codebase
4. **`memory/MEMORY.md`** — Persistent notes from previous sessions

### Key Files to Know

**electrical-estimator:**
| File | Why It Matters |
|---|---|
| `config/bom_schema.py` | The data contract for everything — read this first |
| `config/settings.py` | All constants. Change behavior here, not inline |
| `ai/extractor.py` | The main orchestration logic |
| `bom/excel_writer.py` | The final output — 10-tab Excel BOM |

**stock-screener:**
| File | Why It Matters |
|---|---|
| `run_screener.py` | Everything is here — single-file tool |
| `METRICS_GUIDE.md` | Explains the financial metrics used |

---

## Common First Tasks

- Run the electrical estimator end-to-end with a sample document from `tests/sample_docs/`
- Read `ARCHITECTURE.md` to understand the pipeline
- Run `python run_screener.py` and inspect `output/top_20_stocks.csv`
- Review `DECISIONS.md` to understand why the codebase is structured the way it is

---

## GitHub Access

- **Repository:** `https://github.com/Hfrad23/electrical-estimator`
- **Auth:** Personal Access Token (classic), scopes: `repo`, `workflow`
- **Current status:** Token expired 2026-02-22. Generate a new one at [github.com/settings/tokens](https://github.com/settings/tokens).

```bash
# After getting a new token:
cd electrical-estimator
git remote set-url origin https://YOUR-TOKEN@github.com/Hfrad23/electrical-estimator.git
git push origin main
```

---

## Project Phase Roadmap (electrical-estimator)

| Phase | Status | Description |
|---|---|---|
| Phase 1: MVP | Complete | Text-based extraction, 10-tab BOM, Streamlit UI |
| Phase 2: Vision | Planned | Enable image/page-as-image extraction for scanned docs |
| Phase 3: NEC + DXF | Planned | Full derating validator, DXF parser integration |
| Phase 4: Pricing | Future | Material pricing integration with distributor data |

---

## Who to Ask

This is a solo workspace owned by **Hil** (industrial electrical contractor, oil & gas, US Central timezone). If you're Claude Code helping in a session, check `memory/MEMORY.md` and `WIP.md` for current context before starting work.
