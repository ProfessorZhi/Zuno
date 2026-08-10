from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = ROOT / "src" / "backend"

if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

# Add ROOT directory to sys.path so we can import tools.evals.zuno... directly
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(scope="session", autouse=True)
def _repository_root_has_no_sqlite_artifacts():
    """Prevent tests from leaving persistent SQLite files in the repository root."""
    yield
    leftovers = sorted(
        path.name
        for path in ROOT.iterdir()
        if path.is_file() and path.suffix.lower() in {".db", ".sqlite", ".sqlite3"}
    )
    assert not leftovers, (
        "tests must not leave SQLite artifacts in the repository root: "
        + ", ".join(leftovers)
    )
