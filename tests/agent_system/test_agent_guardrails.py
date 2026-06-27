from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_AGENT_SYSTEM = REPO_ROOT / ".agent" / "scripts" / "verify_agent_system.py"


def _load_verifier():
    spec = spec_from_file_location("verify_agent_system", VERIFY_AGENT_SYSTEM)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_active_programs_are_flat_and_start_at_phase01() -> None:
    verifier = _load_verifier()
    assert verifier.verify_programs_flat(REPO_ROOT) == []


def test_system_yaml_references_existing_skills_templates_and_verify_commands() -> None:
    verifier = _load_verifier()
    assert verifier.verify_system_yaml(REPO_ROOT) == []


def test_skill_files_keep_links_inside_existing_repo_paths() -> None:
    verifier = _load_verifier()
    assert verifier.verify_skill_links(REPO_ROOT) == []


def test_agent_templates_keep_required_sections() -> None:
    verifier = _load_verifier()
    assert verifier.verify_templates_have_required_sections(REPO_ROOT) == []
