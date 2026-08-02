from pathlib import Path
import sys
import types


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "src" / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Add ROOT directory to sys.path so we can import tools.evals.zuno... directly
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Expose `tools.evals.zuno.*` as `zuno.evals.*` for legacy test imports.
# This is a test-only shim; production code must import from `tools.evals.zuno`.
if "zuno.evals" not in sys.modules:
    try:
        import tools.evals.zuno as _tools_evals_zuno  # noqa: F401

        _evals_module = types.ModuleType("zuno.evals")

        def _evals_getattr(name):
            return getattr(_tools_evals_zuno, name)

        _evals_module.__getattr__ = _evals_getattr  # type: ignore[attr-defined]
        sys.modules["zuno.evals"] = _evals_module
    except ImportError:
        pass
