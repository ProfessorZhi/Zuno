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
    shutil.rmtree(REPO_ROOT / "services" / "api", ignore_errors=True)


def _has_agentchat_bridge_reference(content: str) -> bool:
    return bool(
        re.search(r'_AGENTCHAT_MODULE\s*=\s*["\']agentchat', content)
        or re.search(r"from\s+agentchat\b", content)
        or re.search(r"import\s+agentchat\b", content)
    )


def _ast_agentchat_imports(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "agentchat" or alias.name.startswith("agentchat."):
                    hits.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module == "agentchat" or module.startswith("agentchat."):
                hits.append(module)
    return sorted(set(hits))


def test_phase25_docs_mark_legacy_agentchat_as_compatibility_only() -> None:
    _purge_retired_services_api_tree()
    current_architecture = _read("docs/architecture/current-architecture.md")
    transition_strategy = _read("docs/architecture/transition-strategy.md")

    assert "legacy/agentchat" in current_architecture
    assert "compatibility-only" in current_architecture
    assert "not runtime truth" in current_architecture
    assert "Any future attempt to move the backend into a root-level `services/` subtree must be treated as a new architecture phase" in current_architecture
    assert "Any future service-root move must reopen as a new phase" in transition_strategy
    assert not (REPO_ROOT / "services" / "api").exists()


def test_phase25_phase2_runtime_mainline_files_do_not_import_agentchat() -> None:
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
        if _has_agentchat_bridge_reference(_read(relative_path))
    ]
    assert offending == []


def test_phase25_only_explicit_compat_bridges_reference_agentchat_outside_legacy_tree() -> None:
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
            if _has_agentchat_bridge_reference(path.read_text(encoding="utf-8")):
                observed.add(relative_path)

    assert observed == allowed


def test_phase25_non_compat_tests_do_not_import_agentchat_modules() -> None:
    observed: set[str] = set()
    for path in _python_files(REPO_ROOT / "tests"):
        if "compat" in path.parts:
            continue
        relative_path = path.relative_to(REPO_ROOT).as_posix()
        if _ast_agentchat_imports(path):
            observed.add(relative_path)

    assert observed == set()


def test_phase25_docker_and_launcher_runtime_surfaces_do_not_reference_legacy_paths() -> None:
    forbidden = [
        "legacy/agentchat",
        "legacy_backend",
        "src/backend/agentchat",
        "zuno/legacy/agentchat",
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


def test_phase25_services_api_tree_is_fully_retired() -> None:
    _purge_retired_services_api_tree()
    assert not (REPO_ROOT / "services" / "api").exists()


def test_phase25_remaining_agentchat_script_imports_are_isolated_to_known_compat_surfaces() -> None:
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
            if _ast_agentchat_imports(path):
                observed.add(relative_path)

    assert observed == allowed
