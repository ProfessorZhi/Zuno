from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "src" / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Add ROOT directory to sys.path so we can import tools.evals.zuno... directly
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
