"""Contract fixture 11: dynamic legacy import via ``importlib.import_module``."""

from __future__ import annotations

import importlib


def load_legacy_runtime():
    """Dynamic import of a legacy module by string."""
    return importlib.import_module("zuno.core.legacy_runner")