from pathlib import Path
import importlib.util
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "tools" / "scripts" / "preview_phase6_bundle_scope.py"


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
        "src/backend/agentchat/evals/rag_eval/run_local_embedding_eval.py"
        in module.PHASE6_BUNDLE_GROUPS["logical_phase6_delta"]
    )
    assert (
        "src/backend/zuno/legacy/agentchat/services/runtime_registry.py"
        in module.PHASE6_BUNDLE_GROUPS["runtime_foundations"]
    )
    assert (
        "src/backend/agentchat/test/test_contract_eval_runner.py"
        in module.PHASE6_BUNDLE_GROUPS["verification_tests"]
    )


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
    files = [
        REPO_ROOT / "docs" / "architecture" / "plans" / "current-phase-audit.md",
        REPO_ROOT / "docs" / "architecture" / "plans" / "zuno-refactor-execution-plan.md",
    ]

    required_phrases = [
        "python tools/scripts/preview_phase6_bundle_scope.py --groups",
        "python tools/scripts/preview_phase6_bundle_scope.py --summary",
        "python tools/scripts/preview_phase6_bundle_scope.py --group logical_phase6_delta",
        "python tools/scripts/preview_phase6_bundle_scope.py --group runtime_foundations --stat",
        "python tools/scripts/preview_phase6_bundle_scope.py --dry-run",
        "python tools/scripts/preview_phase6_bundle_scope.py --stage-command",
        "python tools/scripts/verify_phase6_bundle_ready.py",
    ]

    for file in files:
        content = file.read_text(encoding="utf-8")
        for phrase in required_phrases:
            assert phrase in content, f"missing Phase 6 bundle scope doc guidance in {file}: {phrase}"


def test_phase6_bundle_ready_docs_and_script_stay_in_sync() -> None:
    prestage = (
        REPO_ROOT / "docs" / "architecture" / "plans" / "phase6-bundle-prestage.md"
    ).read_text(encoding="utf-8")
    ready = (
        REPO_ROOT / "docs" / "architecture" / "plans" / "phase6-bundle-ready.md"
    ).read_text(encoding="utf-8")
    plans_index = (
        REPO_ROOT / "docs" / "architecture" / "plans" / "README.md"
    ).read_text(encoding="utf-8")
    verifier = (
        REPO_ROOT / "tools" / "scripts" / "verify_phase6_bundle_ready.py"
    ).read_text(encoding="utf-8")

    assert "python tools/scripts/verify_phase6_bundle_ready.py" in prestage
    assert "docs_and_contract = 3" in prestage
    assert "logical_phase6_delta = 5" in prestage
    assert "eval_entrypoints = 4" in prestage
    assert "runtime_foundations = 22" in prestage
    assert "verification_tests = 20" in prestage
    assert "phase6_node_ops = 6" in ready
    assert "total_changed = 60" in ready
    assert "./phase6-bundle-prestage.md" in plans_index
    assert "./phase6-bundle-ready.md" in plans_index
    assert "EXPECTED_GROUP_COUNTS" in verifier
    assert "EXPECTED_TOTAL = 60" in verifier
    assert "EXPECTED_PRIMARY_COMMIT_SUBJECT = \"phase6: solidify eval evidence bundle\"" in verifier
    assert "EXPECTED_FOLLOWUP_COMMIT_SUBJECT = \"phase6: sync local node readiness state\"" in verifier
    assert "mode=head_commit" in verifier
    assert "mode=head_commit_range" in verifier
    assert "mode=worktree" in verifier
    assert "phase6 bundle readiness check passed." in verifier
