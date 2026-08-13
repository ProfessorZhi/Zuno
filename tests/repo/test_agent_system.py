from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_agent_system_exposes_only_current_workflow_sources() -> None:
    references = {
        path.name
        for path in (REPO_ROOT / ".agent" / "references").iterdir()
        if path.is_file()
    }
    assert references == {
        "README.md",
        "current-program.md",
        "docs-map.md",
        "code-map.md",
        "task-routing.md",
        "workflow.md",
        "debugging.md",
        "known-pitfalls.md",
        "verification-map.md",
    }

    programs = {
        path.name
        for path in (REPO_ROOT / ".agent" / "programs").iterdir()
        if path.is_file()
    }
    assert programs == {"README.md", "current.md"}
    assert not (REPO_ROOT / ".agent/programs/queued-programs/PROGRAM01_real-unified-runtime-cutover.md").exists()


def test_agent_system_has_no_archived_runtime_facades_or_phase_verifiers() -> None:
    assert not (REPO_ROOT / "src/backend/zuno/api/services/workspace_task_runtime.py").exists()
    assert not (REPO_ROOT / "src/backend/zuno/agent/runtime/phase08_cutover.py").exists()
    assert not any(
            path.is_file()
            and "__pycache__" not in path.parts
            and any(token in path.name.lower() for token in ("phase", "legacy", "cutover"))
        for root in (REPO_ROOT / "tools/scripts", REPO_ROOT / "tests")
        for path in root.rglob("*")
    )


def test_agent_entrypoint_routes_to_current_sources() -> None:
    agents = (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for path in (
        "docs/architecture/architecture.md",
        "docs/history/",
        "docs/facts/current-state.md",
        ".agent/system.yaml",
        ".agent/references/current-program.md",
        ".agent/references/workflow.md",
        ".agent/references/verification-map.md",
    ):
        assert path in agents
    assert "Multi-Agent" in agents or "Coordinator" in agents
