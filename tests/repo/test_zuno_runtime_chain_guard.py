from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "src" / "backend" / "zuno"


PHASE0_RUNTIME_TRUTH_FILES = [
    "main.py",
    "api/router.py",
    "api/v1/__init__.py",
    "api/v1/workspace.py",
    "platform/database/init_data.py",
    "platform/database/session.py",
    "platform/database/metadata.py",
    "platform/services/retrieval/orchestrator.py",
    "platform/services/retrieval/planner.py",
    "platform/services/application/knowledge/query_service.py",
    "platform/services/graphrag/query_service.py",
    "platform/services/graphrag/project/loader.py",
    "platform/services/graphrag/retriever.py",
    "settings.py",
]


def test_phase0_runtime_truth_lives_under_src_backend_zuno() -> None:
    for relative_path in PHASE0_RUNTIME_TRUTH_FILES:
        assert (BACKEND_ROOT / relative_path).exists(), relative_path


def test_phase0_runtime_truth_no_longer_depends_on_services_api_import_bridge() -> None:
    zuno_package_init = (BACKEND_ROOT / "__init__.py").read_text(encoding="utf-8")
    zuno_services_init = (BACKEND_ROOT / "platform" / "services" / "__init__.py").read_text(
        encoding="utf-8"
    )

    assert "services/api/src" not in zuno_package_init
    assert "_find_service_api_root" not in zuno_package_init
    assert "services/api/src" not in zuno_services_init
    assert "service_api_root_str" not in zuno_services_init


def test_agent_runtime_facade_no_longer_part_of_current_runtime_truth() -> None:
    assert not (BACKEND_ROOT / "agent/core/runtime/agent_runtime.py").exists()


def test_phase0_runtime_truth_avoids_service_api_runtime_paths_in_active_tests() -> None:
    phase0_test = (
        REPO_ROOT / "tests" / "legacy_guards" / "test_phase0_runtime_recovery.py"
    ).read_text(
        encoding="utf-8"
    )
    banned_phrase = "/".join(["services", "api", "src", "zuno"])

    assert banned_phrase not in phase0_test


def test_phase0_recovery_tests_use_project_query_runtime_truth() -> None:
    phase0_test = (
        REPO_ROOT / "tests" / "legacy_guards" / "test_phase0_runtime_recovery.py"
    ).read_text(
        encoding="utf-8"
    )

    assert "KnowledgeQueryService" in phase0_test
    assert "GraphRAGQueryService" in phase0_test
    assert "DomainQAGraph" not in phase0_test
    assert "DomainPackLoader" not in phase0_test


def test_phase0_recovery_verifier_uses_project_query_runtime_truth() -> None:
    phase0_verifier = (
        REPO_ROOT / "tools" / "scripts" / "verify_phase0_runtime_recovery.py"
    ).read_text(encoding="utf-8")

    assert "KnowledgeQueryService" in phase0_verifier
    assert "GraphRAGQueryService" in phase0_verifier
    assert "GraphRAGProjectSnapshot" in phase0_verifier
    assert "DomainQAGraph" not in phase0_verifier
    assert "DomainPackLoader" not in phase0_verifier


def test_phase5_import_tests_use_project_query_runtime_truth() -> None:
    phase5_import_test = (
        REPO_ROOT / "tests" / "legacy_guards" / "test_phase5_langgraph_runtime_imports.py"
    ).read_text(encoding="utf-8")

    assert "KnowledgeQueryService" in phase5_import_test
    assert "GraphRAGQueryService" in phase5_import_test
    assert "DomainQAGraph" not in phase5_import_test
    assert "DomainPackLoader" not in phase5_import_test


def test_legacy_graph_runtime_retirement_guards_live_in_legacy_guard_tests() -> None:
    legacy_root_tests = [
        "tests/legacy_guards/test_phase1_langgraph_runtime_deepening.py",
        "tests/legacy_guards/test_phase5_domain_qa_graph_runtime.py",
        "tests/legacy_guards/test_phase5_multi_agent_supervisor_runtime.py",
    ]
    for relative_path in legacy_root_tests:
        assert not (REPO_ROOT / relative_path).exists(), relative_path

    assert not (REPO_ROOT / "tests/compat").exists()

    root_guard_tests = [
        "tests/legacy_guards/test_phase11c_agent_runtime_retirement.py",
        "tests/legacy_guards/test_phase11c_graph_public_export_retirement.py",
    ]
    for relative_path in root_guard_tests:
        assert (REPO_ROOT / relative_path).exists(), relative_path


def test_domain_pack_retirement_guards_live_in_legacy_guard_tests() -> None:
    legacy_root_tests = [
        "tests/legacy_guards/test_phase3_domain_pack_formalization.py",
        "tests/legacy_guards/test_phase5_contract_review_domain_pack.py",
    ]
    for relative_path in legacy_root_tests:
        assert not (REPO_ROOT / relative_path).exists(), relative_path

    assert not (REPO_ROOT / "tests/compat").exists()

    root_tests = [
        "tests/graphrag/test_contract_review_project_payload.py",
    ]
    for relative_path in root_tests:
        assert (REPO_ROOT / relative_path).exists(), relative_path

    assert (REPO_ROOT / "tests/legacy_guards/test_phase11c_agent_runtime_retirement.py").exists()


def test_phase5_domain_runtime_paths_stays_on_current_general_agent_path() -> None:
    phase5_paths_test = (
        REPO_ROOT / "tests" / "legacy_guards" / "test_phase5_domain_runtime_paths.py"
    ).read_text(encoding="utf-8")

    assert "KnowledgeQueryService" in phase5_paths_test
    assert "DomainQAGraph" not in phase5_paths_test
    assert "MultiAgentSupervisorGraph" not in phase5_paths_test
