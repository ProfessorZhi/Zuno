from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend"


def _run_backend_python(code: str) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        "-c",
        (
            "import sys; "
            f"sys.path.insert(0, r'{BACKEND_ROOT}'); "
            f"{code}"
        ),
    ]
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def verify_backend_import_root() -> list[str]:
    errors: list[str] = []
    result = _run_backend_python("import zuno.main; print(zuno.main.__file__)")
    if result.returncode != 0:
        errors.append(f"failed to import zuno.main from backend root: {result.stderr.strip()}")
    return errors


def verify_high_value_imports() -> list[str]:
    result = _run_backend_python(
        (
            "from zuno.platform.services.application.knowledge import KnowledgeQueryService; "
            "from zuno.platform.services.graphrag.query_service import GraphRAGProjectSnapshot, GraphRAGQueryService; "
            "from zuno.platform.services.retrieval.orchestrator import RetrievalOrchestrator; "
            "from zuno.platform.services.graphrag.retriever import GraphRetriever; "
            "print(KnowledgeQueryService.__name__, GraphRAGQueryService.__name__, "
            "GraphRAGProjectSnapshot.__name__, RetrievalOrchestrator.__name__, GraphRetriever.__name__)"
        )
    )
    if result.returncode != 0:
        return [f"high-value runtime import check failed: {result.stderr.strip()}"]
    if (
        "KnowledgeQueryService GraphRAGQueryService GraphRAGProjectSnapshot "
        "RetrievalOrchestrator GraphRetriever"
    ) not in result.stdout:
        return [f"unexpected high-value import output: {result.stdout.strip()}"]
    return []


def verify_dockerfile_pythonpath() -> list[str]:
    dockerfile = REPO_ROOT / "infra" / "docker" / "Dockerfile"
    errors: list[str] = []
    if not dockerfile.exists():
        return ["infra/docker/Dockerfile does not exist"]
    content = dockerfile.read_text(encoding="utf-8")
    if "PYTHONPATH=/app/src/backend" not in content and "PYTHONPATH=/app/src/backend:${PYTHONPATH}" not in content:
        errors.append("infra/docker/Dockerfile does not expose the Phase 0 backend import path")
    return errors


def main() -> int:
    errors = [
        *verify_backend_import_root(),
        *verify_high_value_imports(),
        *verify_dockerfile_pythonpath(),
    ]

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        print("Phase 0 runtime recovery verification failed.")
        return 1

    print("Phase 0 runtime recovery verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
