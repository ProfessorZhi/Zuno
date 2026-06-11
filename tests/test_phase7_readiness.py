from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_phase7_readiness_script_exists_and_covers_final_gate() -> None:
    script = (
        REPO_ROOT / "tools" / "scripts" / "verify_phase7_readiness.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "verify_docs_surface.py",
        "verify_repo_structure.py",
        "tests/test_docs_surface_consistency.py",
        "tests/test_repo_structure_consistency.py",
        "tests/test_publish_boundary.py",
        "tests/test_zuno_public_entrypoints.py",
        "src/backend/agentchat/test/test_zuno_alias_imports.py",
        "tests/test_zuno_runtime_chain_guard.py",
        "phase7-zuno-main-smoke-ok",
        "Phase 7 readiness verification passed.",
    ]

    for phrase in required_phrases:
        assert phrase in script, f"missing phase7 readiness phrase: {phrase}"


def test_phase7_docs_and_readme_reference_final_readiness_entry() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    current_phase_audit = (
        REPO_ROOT / "docs" / "architecture" / "plans" / "current-phase-audit.md"
    ).read_text(encoding="utf-8")
    prestage = (
        REPO_ROOT / "docs" / "architecture" / "plans" / "phase7-final-prestage.md"
    ).read_text(encoding="utf-8")
    ready = (
        REPO_ROOT / "docs" / "architecture" / "plans" / "phase7-final-ready.md"
    ).read_text(encoding="utf-8")

    required_phrase = "python tools/scripts/verify_phase7_readiness.py"

    assert required_phrase in readme
    assert required_phrase in current_phase_audit
    assert required_phrase in prestage
    assert required_phrase in ready
