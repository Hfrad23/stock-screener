import json
from pathlib import Path
from config.settings import WATCHLIST_PATH


def load_watchlist() -> list[str]:
    """Read JSON file; return sorted, deduplicated list. Returns [] on missing/corrupt file."""
    path = Path(WATCHLIST_PATH)
    if not path.exists():
        return []
    try:
        return sorted(set(json.loads(path.read_text())))
    except Exception:
        return []


def add_ticker(ticker: str) -> tuple[list[str], str]:
    """
    Add ticker to watchlist. Returns (updated_list, status).
    status = "added" | "duplicate" | "empty"
    Does NOT validate that ticker is a real symbol — same as Stock Lookup.
    """
    ticker = ticker.strip().upper()
    if not ticker:
        return load_watchlist(), "empty"
    current = load_watchlist()
    if ticker in current:
        return current, "duplicate"
    updated = sorted(current + [ticker])
    _save(updated)
    return updated, "added"


def remove_ticker(ticker: str) -> list[str]:
    """Remove ticker from watchlist. No-op if not present."""
    updated = [t for t in load_watchlist() if t != ticker]
    _save(updated)
    return updated


def _save(tickers: list[str]) -> None:
    path = Path(WATCHLIST_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(set(tickers))))
