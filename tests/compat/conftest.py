from pathlib import Path
import os
import sys


ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = ROOT / "src" / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# These files are historical/manual probes that require network, local private files,
# or optional third-party tools. They are not part of the default hermetic release gate.
MANUAL_COMPAT_PROBES = [
    "test_React.py",
    "test_chat.py",
    "test_config.py",
    "test_craw.py",
    "test_delivery.py",
    "test_docling.py",
    "test_docx.py",
    "test_pymupdf4llm.py",
    "test_rag.py",
    "test_tool.py",
    "test_weather.py",
]

if os.getenv("ZUNO_RUN_MANUAL_COMPAT") == "1":
    collect_ignore_glob: list[str] = []
else:
    collect_ignore_glob = MANUAL_COMPAT_PROBES
