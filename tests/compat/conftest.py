from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
SERVICE_API_ROOT = ROOT / "services" / "api" / "src"

if str(SERVICE_API_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_API_ROOT))
