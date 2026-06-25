from pathlib import Path
import importlib.util
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
ACTIVE_PREVIEW_SCRIPT = REPO_ROOT / "tools" / "scripts" / "preview_phase6_bundle_scope.py"
ACTIVE_VERIFIER_SCRIPT = REPO_ROOT / "tools" / "scripts" / "verify_phase6_bundle_ready.py"
ARCHIVED_SCRIPT_DIR = (
    REPO_ROOT
    / "docs"
    / "architecture"
    / "history"
    / "programs"
    / "knowledge-product-refactor-deep-graphrag-v1"
    / "scripts"
)
SCRIPT_PATH = ARCHIVED_SCRIPT_DIR / "preview_phase6_bundle_scope.py"
VERIFIER_PATH = ARCHIVED_SCRIPT_DIR / "verify_phase6_bundle_ready.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("phase6_bundle_scope", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["phase6_bundle_scope"] = module
    spec.loader.exec_module(module)
    return module


def test_phase6_bundle_scope_groups_cover_expected_boundaries() -> None:
    module = _load_module()

    expected_groups = [
        "docs_and_contract",
        "logical_phase6_delta",
        "eval_entrypoints",
        "runtime_foundations",
        "verification_tests",
        "phase6_node_ops",
    ]

    assert list(module.PHASE6_BUNDLE_GROUPS) == expected_groups
    assert (
        "tools/evals/zuno/rag_eval/run_local_embedding_eval.py"
        in module.PHASE6_BUNDLE_GROUPS["logical_phase6_delta"]
    )
    assert (
        "src/backend/zuno/services/runtime_registry.py"
        in module.PHASE6_BUNDLE_GROUPS["runtime_foundations"]
    )
    assert (
        "tests/test_contract_eval_runner.py"
        in module.PHASE6_BUNDLE_GROUPS["verification_tests"]
    )


def test_phase6_bundle_helpers_are_archived_out_of_active_tools() -> None:
    assert not ACTIVE_PREVIEW_SCRIPT.exists()
    assert not ACTIVE_VERIFIER_SCRIPT.exists()
    assert SCRIPT_PATH.exists()
    assert VERIFIER_PATH.exists()


def test_phase6_bundle_scope_script_mentions_grouped_cli() -> None:
    content = SCRIPT_PATH.read_text(encoding="utf-8")

    required_phrases = [
        "PHASE6_BUNDLE_GROUPS",
        "GROUP_DESCRIPTIONS",
        "\"docs_and_contract\"",
        "\"logical_phase6_delta\"",
        "\"eval_entrypoints\"",
        "\"runtime_foundations\"",
        "\"verification_tests\"",
        "\"phase6_node_ops\"",
        "\"--groups\"",
        "\"--group\"",
        "\"--summary\"",
        "\"--dry-run\"",
        "\"--stage-command\"",
        "[phase6_bundle_summary]",
        "[phase6_bundle_dry_run]",
        "[recommended_sequence]",
        "[phase6_bundle_scope:",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing Phase 6 bundle scope rule: {phrase}"


def test_phase6_docs_reference_grouped_bundle_scope_commands() -> None:
    plans_index = (
        REPO_ROOT / "docs" / "architecture" / "history" / "plans" / "README.md"
    ).read_text(encoding="utf-8")

    assert "stable-baseline-recovery-and-runtime-deepening-plan.md" in plans_index
    assert "retrieval-governance-upgrade-plan.md" in plans_index
    assert "current-phase-audit.md" not in plans_index
    assert "zuno-refactor-execution-plan.md" not in plans_index


def test_phase6_bundle_ready_docs_and_script_stay_in_sync() -> None:
    plans_index = (
        REPO_ROOT / "docs" / "architecture" / "history" / "plans" / "README.md"
    ).read_text(encoding="utf-8")
    preview_script = SCRIPT_PATH.read_text(encoding="utf-8")
    verifier = VERIFIER_PATH.read_text(encoding="utf-8")

    assert "stable-baseline-recovery-and-runtime-deepening-plan.md" in plans_index
    assert "phase6-bundle-prestage.md" not in plans_index
    assert "phase6-bundle-ready.md" not in plans_index
    assert "PHASE6_BUNDLE_GROUPS" in preview_script
    assert "EXPECTED_GROUP_COUNTS" in verifier
    assert "EXPECTED_TOTAL" in verifier
    assert "mode=head_commit" in verifier
    assert "mode=head_commit_range" in verifier
    assert "mode=worktree" in verifier
    assert "phase6 bundle readiness check passed." in verifier
