from __future__ import annotations

from pathlib import Path
from pkgutil import extend_path


__path__ = extend_path(__path__, __name__)


def _find_backend_root() -> Path | None:
    # During Phase 2, compat imports still resolve to the legacy package tree.
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidates = [
            parent / "legacy_backend",
            parent / "src" / "backend",
        ]
        for candidate in candidates:
            if (candidate / "agentchat" / "__init__.py").exists():
                return candidate
    return None


_BACKEND_ROOT = _find_backend_root()
if _BACKEND_ROOT is not None:
    compat_roots = [
        _BACKEND_ROOT / "agentchat",
        _BACKEND_ROOT / "zuno" / "legacy" / "agentchat",
    ]
    for compat_root in compat_roots:
        if compat_root.exists():
            compat_root_str = str(compat_root)
            if compat_root_str not in __path__:
                __path__.append(compat_root_str)
