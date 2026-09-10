"""Local, append-only practice telemetry collector."""

from .collector_core import collect_task, canonicalize_task

__all__ = ["collect_task", "canonicalize_task"]
