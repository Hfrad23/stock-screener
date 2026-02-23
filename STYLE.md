# Style Guide

Project-specific conventions beyond what a linter enforces.

---

## Python

### Formatting
- Line length: **88 characters** (Black default)
- Indentation: **4 spaces** (never tabs)
- Strings: **double quotes** preferred

### Imports
Group in this order, separated by blank lines:
1. Standard library
2. Third-party packages
3. Local imports

```python
import json
import os
from pathlib import Path

import anthropic
import streamlit as st
from pydantic import BaseModel

from config.settings import MODEL_NAME
from config.bom_schema import ExtractionResult
```

### Naming Conventions
| Thing | Convention | Example |
|---|---|---|
| Variables / functions | `snake_case` | `wire_items`, `build_prompt()` |
| Classes | `PascalCase` | `WireCableItem`, `AnthropicClient` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_WORKERS`, `MODEL_NAME` |
| Private methods | `_leading_underscore` | `_write_header_row()` |
| File names | `snake_case.py` | `excel_writer.py` |

### Type Hints
- **Always** annotate public function signatures
- Return type annotation is required
- Skip annotations on obvious one-liners inside functions

```python
# Good
def extract_chunks(doc: IngestedDocument, max_tokens: int) -> list[str]:
    ...

# Fine for internal use
chunks = doc.content.split("\n\n")
```

### Docstrings
- Use for all public functions and classes
- One line for simple functions; multi-line for anything with non-obvious behavior
- Don't document what the code already says clearly

```python
def build_context(project: ProjectInfo) -> dict:
    """Build the project context dict passed to all AI extraction calls."""
    ...

def deduplicate_wire_items(items: list[WireCableItem]) -> list[WireCableItem]:
    """
    Remove duplicate wire items by AWG + insulation + voltage combination.

    Items with the same key are merged, summing their footage estimates.
    Confidence is downgraded to the lowest confidence among merged items.
    """
    ...
```

### Error Handling
- Catch specific exceptions, not bare `except:`
- Let unexpected errors propagate — don't swallow them silently
- Log the error before re-raising or handling

```python
# Bad
try:
    result = json.loads(response)
except:
    result = {}

# Good
try:
    result = ExtractionResult.model_validate_json(response)
except ValidationError as e:
    logger.error(f"Pydantic validation failed: {e}")
    raise
```

---

## Streamlit (`app.py`)

- **No business logic in `app.py`.** It calls functions from other modules; it does not implement them.
- Each major UI section is a clearly named function: `render_project_info()`, `render_upload()`, etc.
- `st.session_state["session"]` is the single source of truth for all session data.
- Use `st.expander()` for optional/detail content to keep the main view clean.
- Progress indicators (`st.progress`, `st.spinner`) on any operation over ~1 second.

---

## Pydantic Models (`bom_schema.py`)

- All models inherit from `BaseModel`
- Optional fields use `Optional[T] = None`, never `T = None`
- Enum fields are actual Python `Enum` classes, not string literals
- Field validators use `@field_validator` (Pydantic v2), never `@validator` (v1 style)
- Normalizers go in the model (e.g., strip whitespace, lowercase for comparison), not in callers

```python
# Good
class WireCableItem(BOMItemBase):
    awg: Optional[str] = None
    voltage_rating: Optional[int] = None
    confidence: ConfidenceLevel = ConfidenceLevel.ESTIMATED

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, v):
        if isinstance(v, str):
            return v.lower().capitalize()
        return v
```

---

## Prompts (`ai/prompts/`)

- Each prompt file exports exactly two things: `SYSTEM_PROMPT` and `build_user_prompt(context, chunk)`
- System prompts establish persona and rules once. User prompts provide the specific document chunk.
- Prompts always end with an explicit instruction to return **only valid JSON** matching a defined schema.
- Include the target JSON schema in the prompt (embedded as a code block or described field-by-field).

---

## Excel Output (`bom/excel_writer.py`)

- Header rows: bold, background color from `settings.py` palette
- Data rows: alternating white / light gray for readability
- Confidence color coding:
  - `Confirmed` → Green (`#C6EFCE`)
  - `Estimated` → Yellow (`#FFEB9C`)
  - `Assumed` → Red (`#FFC7CE`)
- Column widths: set explicitly, never use auto-fit (it's slow and inconsistent)
- Sheet names match `settings.py` → `BOM_TAB_NAMES` exactly

---

## Git

- Commit messages: imperative mood, present tense ("Add", not "Added")
- Max ~72 characters for the subject line
- Body (if needed) explains *why*, not *what*
- Never commit: `.env`, `.cache/`, `uploads/`, `output/`, `sessions/`, `data/raw_data.pkl`
