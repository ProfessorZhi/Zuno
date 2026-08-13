from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]


def _files(directory: Path) -> set[str]:
    return {path.relative_to(ROOT).as_posix() for path in directory.rglob("*") if path.is_file()}


def main() -> int:
    errors: list[str] = []
    expected_history = {
        "docs/history/README.md",
        "docs/history/architecture-evolution.md",
        "docs/history/program-history.md",
    }
    expected_evidence = {
        "docs/evidence/README.md",
        "docs/evidence/repository-closure.md",
        "docs/evidence/local-workspace-closure.md",
        "docs/evidence/current-runtime-baseline.md",
        "docs/evidence/current-test-baseline.md",
        "docs/evidence/current-eval-baseline.md",
    }
    history_front = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "docs/history").iterdir()
        if path.is_file()
    }
    if history_front != expected_history:
        errors.append("docs/history front must contain only the three approved files")
    if _files(ROOT / "docs/evidence") != expected_evidence:
        errors.append("docs/evidence must contain only current evidence entries")

    expected_project_history = {
        "docs/project/history/README.md",
        "docs/project/history/project-background.md",
        "docs/project/history/requirements-and-workflows.md",
        "docs/project/history/team-and-ownership.md",
        "docs/project/history/development-history.md",
        "docs/project/history/incidents-and-improvements.md",
        "docs/project/history/delivery-and-usage.md",
        "docs/project/history/technology-history.md",
    }
    expected_project_status = {
        "docs/project/status/README.md",
        "docs/project/status/current-reality.md",
        "docs/project/status/target-status.md",
        "docs/project/status/production-readiness.md",
    }
    if _files(ROOT / "docs/project/history") != expected_project_history:
        errors.append("docs/project/history must contain the approved history entrypoints")
    if _files(ROOT / "docs/project/status") != expected_project_status:
        errors.append("docs/project/status must contain the approved status entrypoints")
    if (ROOT / "docs/project/facts").exists() or (ROOT / "docs/project/modules").exists():
        errors.append("old docs/project/facts or docs/project/modules active paths must be absent")
    for directory in ("product", "domain", "agents", "knowledge", "services", "data", "security", "eval", "deployment"):
        if (ROOT / "docs/project" / directory).exists():
            errors.append(f"old docs/project/{directory} topic path must be absent")

    program_root = ROOT / ".agent" / "programs"
    if {path.name for path in program_root.glob("*.md")} != {"README.md", "current.md"}:
        errors.append(".agent/programs front must contain README.md and current.md")
    current = (program_root / "current.md").read_text(encoding="utf-8")
    has_no_active_state = all(phrase in current for phrase in ("state: `no-active`", "active_program: `none`"))
    has_design_state = "state: `active-design-program`" in current and re.search(
        r"active_program: `(?!none`)[^`]+`", current
    ) is not None
    has_implementation_evidence_state = "state: `active-implementation-evidence-program`" in current and re.search(
        r"active_program: `(?!none`)[^`]+`", current
    ) is not None
    if not (has_no_active_state or has_design_state or has_implementation_evidence_state):
        errors.append("current program has no recognized design/implementation state")
    if "SUPERSEDED / RETIRED" not in current:
        errors.append("current program missing SUPERSEDED / RETIRED")

    architecture = ROOT / "docs" / "project" / "architecture"
    if {path.name for path in architecture.iterdir() if path.is_file()} != {
        "README.md", "architecture.md", "architecture-views.md", "architecture.html"
    }:
        errors.append("docs/project/architecture must contain its four canonical files")

    if (ROOT / "src/backend/zuno/api/services/workspace_task_runtime.py").exists():
        errors.append("retired workspace runtime module still exists")
    if (ROOT / "src/backend/zuno/agent/runtime/phase08_cutover.py").exists():
        errors.append("retired cutover module still exists")
    for directory in (ROOT / "tools/scripts", ROOT / "tests"):
        for path in directory.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and re.search(r"(?:phase|legacy|cutover)", path.name, re.IGNORECASE):
                errors.append(f"retired phase/legacy/cutover file: {path.relative_to(ROOT)}")

    if errors:
        print("REPO_STRUCTURE_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("REPO_STRUCTURE_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
