from pathlib import Path
import importlib.util


ROOT = Path(__file__).resolve().parents[2]
VERIFIER = ROOT / "tools/scripts/verify_architecture_interview_program.py"


def _module():
    spec = importlib.util.spec_from_file_location("architecture_interview_program", VERIFIER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_lightweight_architecture_interview_program():
    assert _module().verify(ROOT) == []


def test_archive_execution_mode_is_strict():
    module = _module()
    archive = ROOT / "docs/history/red-blue/manual-round-01-overall-architecture.md"
    metadata = module._metadata(archive)
    assert metadata["execution_mode"] == "MANUAL"
    assert (ROOT / "docs/history/red-blue/legacy-automated-rounds.md").exists()
    assert not list((ROOT / "docs/history/red-blue").glob("automated-*.md"))


def test_local_skills_are_explicit_only_and_manual_workflow_owns_judgment():
    system = (ROOT / ".agent/system.yaml").read_text(encoding="utf-8")
    workflow = (ROOT / "project-reconstruction-lab/WORKFLOW.md").read_text(encoding="utf-8")
    skills_readme = (ROOT / "project-reconstruction-lab/skills/README.md").read_text(encoding="utf-8")
    assert "discovery: \"EXPLICIT_ONLY\"" in system
    assert "PATH_TRIGGERED" not in system
    assert "DEFAULT_MODE: MANUAL_CHATGPT" in workflow
    assert "Architecture Decision Owner" in workflow
    assert "Codex 不负责" in workflow
    assert "NOT AUTO-EXECUTED" in skills_readme
