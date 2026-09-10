"""Adapter entry point for run-governed-product-workflow task records."""
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from collector_core import canonicalize_task  # noqa: E402


def collect(task_dir: str | Path, *, secret: bytes | None = None):
    return canonicalize_task(task_dir, secret=secret)

