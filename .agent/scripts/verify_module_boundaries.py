from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

RETIRED_RUNTIME_PATHS = [
    "src/backend/zuno/core/graphs/domain_qa_graph.py",
    "src/backend/zuno/core/graphs/multi_agent_supervisor_graph.py",
    "src/backend/zuno/core/runtime/agent_runtime.py",
    "src/backend/zuno/services/domain_pack",
]

CONCRETE_RETRIEVAL_IMPORTS = [
    "zuno.services.retrieval",
    "zuno.services.graphrag.retriever",
    "zuno.services.graphrag.retrievers",
    "zuno.services.rag.handler",
    "zuno.services.rag.retrieval",
]

VAGUE_NEW_PACKAGE_NAMES = {"common", "helpers"}
ALLOWED_EXISTING_VAGUE_PATHS = {
    "src/backend/zuno/utils",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _python_files(root: str) -> list[Path]:
    base = REPO_ROOT / root
    if not base.exists():
        return []
    return sorted(path for path in base.rglob("*.py") if path.is_file())


def _git_added_paths() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=A", "HEAD"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return [line.replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def verify_retired_runtime_absent(errors: list[str]) -> None:
    for relative_path in RETIRED_RUNTIME_PATHS:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"retired runtime path returned: {relative_path}")


def verify_api_routes_do_not_import_concrete_retrieval(errors: list[str]) -> None:
    for path in _python_files("src/backend/zuno/api/v1"):
        content = _read(path)
        for import_path in CONCRETE_RETRIEVAL_IMPORTS:
            if f"from {import_path}" in content or f"import {import_path}" in content:
                errors.append(
                    f"api route imports concrete retrieval boundary: {path.relative_to(REPO_ROOT)} -> {import_path}"
                )


def verify_core_does_not_import_api_routes(errors: list[str]) -> None:
    for path in _python_files("src/backend/zuno/core"):
        content = _read(path)
        forbidden = [
            "from zuno.api.v1",
            "import zuno.api.v1",
            "from zuno.api.router",
            "import zuno.api.router",
        ]
        for phrase in forbidden:
            if phrase in content:
                errors.append(f"core imports API route boundary: {path.relative_to(REPO_ROOT)} -> {phrase}")


def verify_new_modules_do_not_add_vague_packages(errors: list[str]) -> None:
    for relative_path in _git_added_paths():
        if not relative_path.startswith("src/backend/zuno/"):
            continue
        parts = relative_path.split("/")
        for index, part in enumerate(parts):
            if part not in VAGUE_NEW_PACKAGE_NAMES:
                continue
            package_path = "/".join(parts[: index + 1])
            if package_path not in ALLOWED_EXISTING_VAGUE_PATHS:
                errors.append(f"new backend module uses vague package name: {relative_path}")


def verify_knowledge_query_boundary(errors: list[str]) -> None:
    audit_path = REPO_ROOT / "docs/history/programs/zuno-target-runtime-v2/evidence/module-boundary-audit.md"
    if not audit_path.exists():
        errors.append("module boundary audit is missing")
        return
    audit = _read(audit_path)
    required = [
        "Phase 03 migration result",
        "src/backend/zuno/api/services/knowledge_query.py",
        "src/backend/zuno/services/application/knowledge/query_service.py",
    ]
    for phrase in required:
        if phrase not in audit:
            errors.append(f"module boundary audit missing compatibility phrase: {phrase}")

    old_path = REPO_ROOT / "src/backend/zuno/api/services/knowledge_query.py"
    if old_path.exists():
        errors.append("old KnowledgeQueryService API-service path still exists")

    for root in ["src", "tests", "tools"]:
        for path in _python_files(root):
            content = _read(path)
            if "zuno.api.services.knowledge_query" in content:
                errors.append(f"old KnowledgeQueryService import remains: {path.relative_to(REPO_ROOT)}")


def main() -> int:
    errors: list[str] = []
    verify_retired_runtime_absent(errors)
    verify_api_routes_do_not_import_concrete_retrieval(errors)
    verify_core_does_not_import_api_routes(errors)
    verify_new_modules_do_not_add_vague_packages(errors)
    verify_knowledge_query_boundary(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Module boundary verification failed.")
        return 1

    print("Module boundary verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
