from __future__ import annotations

import sys
from pathlib import Path


def _find_legacy_backend_root() -> Path | None:
    # During Phase 2 startup migration, `zuno.main` still resolves to `src/backend/zuno/main.py`.
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / "src" / "backend"
        if (candidate / "zuno" / "main.py").exists():
            return candidate
    return None


_LEGACY_BACKEND_ROOT = _find_legacy_backend_root()
if _LEGACY_BACKEND_ROOT is not None:
    legacy_root_str = str(_LEGACY_BACKEND_ROOT)
    if legacy_root_str not in sys.path:
        sys.path.insert(0, legacy_root_str)

    legacy_package_root = _LEGACY_BACKEND_ROOT / "zuno"
    if legacy_package_root.exists():
        __path__.append(str(legacy_package_root))
