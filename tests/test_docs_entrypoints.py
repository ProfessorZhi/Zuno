from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_readme_exposes_short_first_reader_path() -> None:
    content = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        "./docs/architecture/plans/current-phase-audit.md",
        "./docs/development/public-demo-evidence.md",
        "./docs/development/public-demo-runbook.md",
        "./docs/development/public-demo-acceptance.md",
        "First-time readers start here:",
        "Maintainer-only release workflow:",
        "First-time readers should stop at the public path below and skip release staging, checklist, and publish-boundary docs on the first pass.",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing README first-reader phrase: {phrase}"


def test_docs_index_prioritizes_public_demo_reading_path() -> None:
    content = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        "./architecture/README.md",
        "./development/public-demo-evidence.md",
        "./development/public-demo-runbook.md",
        "./development/public-demo-acceptance.md",
        "./development/README.md",
        "./development/github-publish-boundary.md",
        "Maintainer entrypoints:",
        "First-time readers should stop after step 7.",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing docs index phrase: {phrase}"


def test_development_docs_are_marked_as_maintainer_only() -> None:
    content = (REPO_ROOT / "docs" / "development" / "README.md").read_text(
        encoding="utf-8"
    )

    required_phrases = [
        "It is not part of the first-read public project path.",
        "## Maintainer Scope",
        "../../README.md",
        "../architecture/README.md",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing development docs maintainer phrase: {phrase}"


def test_verify_docs_entrypoints_script_tracks_phase3_public_entry_surface() -> None:
    content = (
        REPO_ROOT / "tools" / "scripts" / "verify_docs_entrypoints.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "documentation entrypoint verification passed.",
        "./docs/development/public-demo-evidence.md",
        "./development/public-demo-runbook.md",
        "./plans/current-phase-audit.md",
        "First-time readers start here:",
        "Maintainer entrypoints:",
        "It is not part of the first-read public project path.",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing docs entrypoint verifier phrase: {phrase}"
