from __future__ import annotations

import ast
import re
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def _python_files(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if path.is_file())


def _purge_retired_services_api_tree() -> None:
    shutil.rmtree(REPO_ROOT / "services", ignore_errors=True)


def _has_zuno_bridge_reference(content: str) -> bool:
    return bool(
        re.search(r'_AGENTCHAT_MODULE\s*=\s*["\']zuno', content)
        or re.search(r"from\s+zuno\b", content)
        or re.search(r"import\s+zuno\b", content)
    )


def _ast_zuno_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "zuno" or alias.name.startswith("zuno."):
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "zuno" or module.startswith("zuno."):
                hits.append(module)
    return sorted(set(hits))


def test_phase25_docs_mark_legacy_zuno_as_compatibility_only() -> None:
    _purge_retired_services_api_tree()
    current_architecture = _read("docs/architecture/current-architecture.md")
    transition_strategy = _read("docs/architecture/transition-strategy.md")

    assert "legacy/zuno" in current_architecture
    assert "compatibility-only" in current_architecture
    assert "not runtime truth" in current_architecture
    assert "There is no active root-level `services/` tree in current truth." in current_architecture
    assert "Any future service-root move must reopen as a new phase with fresh verification and a newly created root." in transition_strategy
    assert not (REPO_ROOT / "services").exists()


def test_phase25_phase2_runtime_mainline_files_do_not_import_zuno() -> None:
    mainline_files = [
        "src/backend/zuno/core/graphs/domain_qa_graph.py",
        "src/backend/zuno/core/graphs/states.py",
        "src/backend/zuno/services/retrieval/orchestrator.py",
        "src/backend/zuno/services/retrieval/planner.py",
        "src/backend/zuno/services/retrieval/retrievers.py",
        "src/backend/zuno/services/graphrag/retriever.py",
        "src/backend/zuno/services/rag/handler.py",
    ]

    offending = [
        relative_path
        for relative_path in mainline_files
        if _has_zuno_bridge_reference(_read(relative_path))
    ]
    assert offending == []


def test_phase25_only_explicit_compat_bridges_reference_zuno_outside_legacy_tree() -> None:
    allowed = {
        "src/backend/zuno/core/agents/general_agent.py",
        "src/backend/zuno/services/memory/client.py",
        "src/backend/zuno/services/workspace/simple_agent.py",
        "src/backend/zuno/services/workspace/wechat_agent.py",
    }
    observed: set[str] = set()
    for root in [REPO_ROOT / "src" / "backend" / "zuno"]:
        for path in _python_files(root):
            if "legacy" in path.parts:
                continue
            relative_path = path.relative_to(REPO_ROOT).as_posix()
            if _has_zuno_bridge_reference(path.read_text(encoding="utf-8")):
                observed.add(relative_path)

    assert observed == allowed


def test_phase25_non_compat_tests_do_not_import_zuno_modules() -> None:
    observed: set[str] = set()
    for path in _python_files(REPO_ROOT / "tests"):
        if "compat" in path.parts:
            continue
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        if _ast_zuno_imports(path):
            observed.add(relative_path)

    assert observed == set()


def test_phase25_docker_and_launcher_runtime_surfaces_do_not_reference_legacy_paths() -> None:
    forbidden = [
        "legacy/zuno",
        "legacy_backend",
        "src/backend/zuno",
        "zuno/legacy/zuno",
    ]
    runtime_surface_files = [
        "infra/docker/docker-compose.yml",
        "infra/docker/README.md",
        "tools/launchers/windows/Zuno-Phase0-Backend-Start.cmd",
        "tools/launchers/windows/_Zuno-Desktop-Common.cmd",
    ]
    offending: dict[str, list[str]] = {}
    for relative_path in runtime_surface_files:
        content = _read(relative_path)
        hits = [pattern for pattern in forbidden if pattern in content]
        if hits:
            offending[relative_path] = hits

    assert offending == {}


def test_phase25_services_root_is_fully_retired() -> None:
    _purge_retired_services_api_tree()
    assert not (REPO_ROOT / "services").exists()


def test_phase25_remaining_zuno_script_imports_are_isolated_to_known_compat_surfaces() -> None:
    allowed = {
        "infra/db/alembic/versions/20260417_01_init_postgresql.py",
        "tools/evals/zuno/contract_review_eval/run_contract_eval.py",
        "tools/evals/zuno/rag_eval/ingest_prepared_corpus.py",
        "tools/evals/zuno/rag_eval/prepare_python_notes_corpus.py",
        "tools/evals/zuno/rag_eval/run_eval.py",
        "tools/evals/zuno/rag_eval/run_local_embedding_eval.py",
        "tools/evals/zuno/rag_eval/run_stackless_compare_matrix.py",
        "tools/evals/zuno/rag_eval/run_stackless_local_eval.py",
        "tools/scripts/rebuild_rag_indexes.py",
        "tools/scripts/verify_public_demo_runtime.py",
        "tools/scripts/verify_public_demo_strict_grounding.py",
    }
    observed: set[str] = set()
    for root in [REPO_ROOT / "tools", REPO_ROOT / "infra"]:
        for path in _python_files(root):
            relative_path = path.relative_to(REPO_ROOT).as_posix()
            if _ast_zuno_imports(path):
                observed.add(relative_path)

    assert observed == allowed
