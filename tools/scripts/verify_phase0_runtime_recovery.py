from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _run_backend_python(code: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-c",
            (
                "import sys; "
                f"sys.path.insert(0, r'{BACKEND_ROOT}'); "
                + code
            ),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )


def verify_backend_entry_file() -> list[str]:
    errors: list[str] = []
    entry_file = BACKEND_ROOT / "zuno" / "main.py"
    if not entry_file.exists():
        errors.append("missing backend entry file: src/backend/zuno/main.py")
        return errors

    result = _run_backend_python("import zuno.main; print(zuno.main.__file__)")
    if result.returncode != 0:
        errors.append(f"failed to import zuno.main from backend root: {result.stderr.strip()}")
    elif "src\\backend\\zuno\\main.py" not in result.stdout:
        errors.append(f"zuno.main did not resolve to src/backend entry: {result.stdout.strip()}")
    return errors


def verify_high_value_imports() -> list[str]:
    result = _run_backend_python(
        (
            "from zuno.core.graphs.domain_qa_graph import DomainQAGraph; "
            "from zuno.services.retrieval.orchestrator import RetrievalOrchestrator; "
            "from zuno.services.graphrag.retriever import GraphRetriever; "
            "from zuno.services.domain_pack.loader import DomainPackLoader; "
            "print(DomainQAGraph.__name__, RetrievalOrchestrator.__name__, GraphRetriever.__name__, DomainPackLoader.__name__)"
        )
    )
    if result.returncode != 0:
        return [f"high-value runtime import check failed: {result.stderr.strip()}"]
    if "DomainQAGraph RetrievalOrchestrator GraphRetriever DomainPackLoader" not in result.stdout:
        return [f"unexpected high-value import output: {result.stdout.strip()}"]
    return []


def verify_local_start_script() -> list[str]:
    start_script = (REPO_ROOT / "tools" / "scripts" / "start.py").read_text(encoding="utf-8")
    errors: list[str] = []
    if 'BACKEND_DIR = PROJECT_ROOT' not in start_script:
        errors.append("tools/scripts/start.py no longer starts from repo root")
    if '"--app-dir", "src/backend", "zuno.main:app"' not in start_script:
        errors.append("tools/scripts/start.py does not use the src/backend startup path")
    return errors


def verify_docker_startup_path() -> list[str]:
    dockerfile = (REPO_ROOT / "infra" / "docker" / "Dockerfile").read_text(encoding="utf-8")
    errors: list[str] = []
    if "ENV PYTHONPATH=/app/src/backend:/app" not in dockerfile:
        errors.append("infra/docker/Dockerfile does not expose the Phase 0 backend import path")
    if 'CMD ["uvicorn", "--app-dir", "src/backend", "zuno.main:app"' not in dockerfile:
        errors.append("infra/docker/Dockerfile does not use the Phase 0 backend startup path")
    return errors


def main() -> int:
    errors = [
        *verify_backend_entry_file(),
        *verify_high_value_imports(),
        *verify_local_start_script(),
        *verify_docker_startup_path(),
    ]

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Phase 0 runtime recovery verification failed.")
        return 1

    print("Phase 0 runtime recovery verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
