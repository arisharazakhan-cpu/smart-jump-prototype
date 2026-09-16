"""Browser interface for the Smart Jump digital-twin demonstration."""

from pathlib import Path


DEMO_PATH = Path(__file__).resolve().parents[1] / "docs" / "index.html"
DIGITAL_TWIN_HTML = DEMO_PATH.read_text(encoding="utf-8")
