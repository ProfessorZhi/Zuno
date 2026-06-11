from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_readme_declares_first_read_path() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        "## First-Read Path",
        "./docs/README.md",
        "./docs/architecture/README.md",
        "./docs/architecture/specs/README.md",
        "./docs/architecture/plans/README.md",
        "./docs/architecture/plans/current-phase-audit.md",
    ]

    for phrase in required_phrases:
        assert phrase in readme, f"missing readme docs path phrase: {phrase}"


def test_docs_indexes_define_public_and_maintainer_paths() -> None:
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    dev_readme = (
        REPO_ROOT / "docs" / "development" / "README.md"
    ).read_text(encoding="utf-8")

    assert "## First-Read Path" in docs_index
    assert "./architecture/README.md" in docs_index
    assert "./architecture/specs/README.md" in docs_index
    assert "./architecture/plans/README.md" in docs_index
    assert "./development/README.md" in docs_index
    assert "It is not part of the first-read public project path." in dev_readme
    assert "It should explain maintenance rules, not replace the public architecture path." in dev_readme


def test_architecture_entrypoints_match_phase7_serial_status() -> None:
    architecture_index = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    refactor_plan = (
        REPO_ROOT / "docs" / "architecture" / "zuno_refactor_plan.md"
    ).read_text(encoding="utf-8")
    execution_plan = (
        REPO_ROOT
        / "docs"
        / "architecture"
        / "plans"
        / "zuno-refactor-execution-plan.md"
    ).read_text(encoding="utf-8")

    assert "`Phase 5`: completed" in architecture_index
    assert "`Phase 6`: completed" in architecture_index
    assert "`Phase 7`: current serial phase" in architecture_index
    assert "`Phase 5`：已完成" in refactor_plan
    assert "`Phase 6`：已完成" in refactor_plan
    assert "`Phase 7`：当前串行阶段" in refactor_plan
    assert "`Phase 5` is completed and already merged to `main`." in execution_plan
    assert "### Phase 3：GraphRAG 重构" not in refactor_plan
    assert "### Phase 7：包名收口 `agentchat -> zuno`" not in refactor_plan
    assert "`Phase 1-4` 已完成并已有最小验收证据" not in execution_plan


def test_phase3_verifier_and_tests_are_documented() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    execution_plan = (
        REPO_ROOT
        / "docs"
        / "architecture"
        / "plans"
        / "zuno-refactor-execution-plan.md"
    ).read_text(encoding="utf-8")
    verifier = (
        REPO_ROOT / "tools" / "scripts" / "verify_docs_surface.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "python tools/scripts/verify_docs_surface.py",
        "pytest tests/test_docs_surface_consistency.py",
        "pytest tests/test_publish_boundary.py",
    ]

    for phrase in required_phrases:
        assert phrase in readme, f"missing readme phase3 verification phrase: {phrase}"
        assert phrase in execution_plan, f"missing execution plan phase3 verification phrase: {phrase}"

    assert "DOC_REQUIRED_PHRASES" in verifier
    assert "DISALLOWED_PHRASES" in verifier
    assert "Docs surface verification passed." in verifier


def test_architecture_readme_no_longer_routes_first_readers_to_public_demo_docs() -> None:
    architecture_index = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")

    disallowed_phrases = [
        "docs/development/public-demo-evidence.md",
        "docs/development/public-demo-runbook.md",
        "docs/development/public-demo-acceptance.md",
    ]

    for phrase in disallowed_phrases:
        assert phrase not in architecture_index, f"stale public demo path still exposed: {phrase}"
