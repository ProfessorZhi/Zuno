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
    archive = ROOT / "docs/history/red-blue/automated-round-002-architecture-v3.md"
    metadata = module._metadata(archive)
    assert metadata["execution_mode"] == "AUTOMATED"
    assert module._metadata(ROOT / "docs/history/red-blue/manual-round-01-overall-architecture.md")["execution_mode"] == "MANUAL"
