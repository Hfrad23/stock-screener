# Contributing

Guidelines for working on any project in this workspace.

---

## Getting Started

### Prerequisites
- Python 3.9+
- pip
- An Anthropic API key (for electrical-estimator)

### electrical-estimator Setup

```bash
cd electrical-estimator
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Create your .env file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Launch the app
streamlit run app.py
# or use the alias:
estimator
```

### stock-screener Setup

```bash
cd stock-screener
pip install -r requirements.txt

# Run the screener
python run_screener.py

# Or launch the Jupyter notebook
jupyter notebook sp500_value_screener.ipynb
```

---

## Branching Strategy

This workspace uses a simple trunk-based approach:

- **`main`** — Always stable. Never commit broken code directly.
- **Feature branches** — `feature/short-description` (e.g., `feature/dxf-parser`)
- **Bug fixes** — `fix/short-description` (e.g., `fix/pydantic-validator`)
- **Experiments** — `experiment/short-description` — may be abandoned

```bash
git checkout -b feature/my-feature
# ... make changes ...
git add specific-files
git commit -m "Add clear description of what and why"
git push origin feature/my-feature
# Open a PR on GitHub
```

---

## Commit Style

Write commit messages in the imperative mood. Focus on **why**, not just what.

```
# Good
Add MD5 cache to avoid redundant AI extraction calls
Fix Pydantic v2 field_validator for confidence normalization
Increase thread pool to 6 workers for faster parallel extraction

# Bad
fix bug
update extractor
changes
```

One logical change per commit. Don't bundle unrelated fixes.

---

## Pull Request Process

1. Branch off `main`
2. Make your changes
3. Self-review: read your own diff before opening a PR
4. Write a PR description explaining *why* the change was made, not just what changed
5. Request review if working with others

---

## Code Style

- **Python:** Follow PEP 8. Use Black-compatible formatting (88 char line length).
- **Imports:** Standard library → third-party → local. Separated by blank lines.
- **Type hints:** Use them on function signatures. Not required on internal variables.
- **Docstrings:** On public functions and classes. One-line for simple cases.
- **No magic numbers:** Put constants in `config/settings.py`, not inline.

---

## Adding a New BOM Tab (electrical-estimator)

1. Add a new Pydantic model to `config/bom_schema.py`
2. Add extraction fields to the relevant prompt in `ai/prompts/`
3. Update `bom/builder.py` to merge the new items
4. Add a new sheet renderer method in `bom/excel_writer.py`
5. Add the tab name to `settings.py`

---

## Adding a New Document Type (electrical-estimator)

1. Add the type label to `settings.py` → `DOCUMENT_TYPES`
2. Add classification keywords to `pipeline/classifier.py`
3. Create a new prompt file in `ai/prompts/`
4. Update `ai/extractor.py` to route the new type to the new prompt

---

## Environment Variables

| Variable | Required By | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | electrical-estimator | API key from console.anthropic.com |

Never commit `.env` files. They are gitignored.

---

## What Not To Do

- Don't add new dependencies without a clear reason. Both projects keep their `requirements.txt` lean.
- Don't commit `.cache/`, `uploads/`, `output/`, or `sessions/` directories.
- Don't put business logic in `app.py`. The Streamlit file is UI only.
- Don't modify the Pydantic models without checking that all validators and downstream consumers are updated.
