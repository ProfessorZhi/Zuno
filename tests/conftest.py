from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "src" / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Dynamic bridge for tests to resolve zuno.evals namespace cleanly
import types
TOOLS_EVALS_ZUNO = ROOT / "tools" / "evals" / "zuno"
evals_module = types.ModuleType("zuno.evals")
evals_module.__path__ = [str(TOOLS_EVALS_ZUNO)]
sys.modules["zuno.evals"] = evals_module
