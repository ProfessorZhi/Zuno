"""Top-level package marker for zuno."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_legacy_alias_registry():
    registry_path = (
        Path(__file__).resolve().parent
        / "platform"
        / "compatibility"
        / "legacy_aliases.py"
    )
    spec = importlib.util.spec_from_file_location(
        "_zuno_legacy_aliases",
        registry_path,
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load legacy alias registry from {registry_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_load_legacy_alias_registry().register_legacy_aliases(__name__)

__all__: list[str] = []
