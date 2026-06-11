from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_phase2_required_paths_exist() -> None:
    required_paths = [
        "apps/desktop",
        "docs/architecture",
        "docs/development",
        "infra/docker",
        "src/backend",
        "src/backend/zuno/api",
        "src/backend/zuno/core",
        "src/backend/zuno/database",
        "src/backend/zuno/database/dao",
        "src/backend/zuno/services",
        "src/frontend",
        "tests",
        "tools",
        "tools/launchers/windows",
    ]

    for relative_path in required_paths:
        assert (REPO_ROOT / relative_path).exists(), f"missing required path: {relative_path}"


def test_structure_docs_link_current_phase_audit_and_layering_spec() -> None:
    architecture_index = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    plans_index = (
        REPO_ROOT / "docs" / "architecture" / "plans" / "README.md"
    ).read_text(encoding="utf-8")
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    assert "./plans/current-phase-audit.md" in architecture_index
    assert "./specs/layered-backend-and-service-evolution.md" in architecture_index
    assert "./current-phase-audit.md" in plans_index
    assert "./zuno-refactor-execution-plan.md" in plans_index
    assert "./architecture/README.md" in docs_index
    assert "./development/README.md" in docs_index


def test_current_phase_audit_matches_phase2_structure_governance_status() -> None:
    content = (
        REPO_ROOT / "docs" / "architecture" / "plans" / "current-phase-audit.md"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "`Phase 1` 已完成",
        "`Phase 2` 已完成",
        "`Phase 6`: completed",
        "`Phase 7`: current default phase",
        "verify_repo_structure.py",
        "tests/test_repo_structure_consistency.py",
        "tests/test_publish_boundary.py",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing current phase audit phrase: {phrase}"


def test_readme_verification_mentions_phase2_structure_checks() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        "python tools/scripts/verify_repo_structure.py",
        "pytest tests/test_repo_structure_consistency.py",
        "pytest tests/test_publish_boundary.py",
    ]

    for phrase in required_phrases:
        assert phrase in readme, f"missing Phase 2 verification command: {phrase}"


def test_repo_structure_verifier_covers_phase2_layout_contract() -> None:
    content = (
        REPO_ROOT / "tools" / "scripts" / "verify_repo_structure.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "REQUIRED_PATHS",
        "docs/architecture/plans/current-phase-audit.md",
        "src/backend/zuno/database/dao",
        "docs/development/backend-layering-guidelines.md",
        "Repository structure verification passed.",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing repository structure verifier phrase: {phrase}"
