import importlib
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def test_phase4_high_value_runtime_boundary_imports_still_load() -> None:
    backend_root = str(BACKEND_ROOT)
    if backend_root not in sys.path:
        sys.path.insert(0, backend_root)

    modules = [
        "zuno.main",
        "zuno.core.callbacks.usage_metadata",
        "zuno.database.init_data",
        "zuno.services.capability_registry",
    ]

    for module_name in modules:
        module = importlib.import_module(module_name)
        assert module is not None, f"failed to import {module_name}"
