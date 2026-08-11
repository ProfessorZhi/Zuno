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
    if _files(ROOT / "docs/history") != expected_history:
        errors.append("docs/history must contain only the three approved files")
    if _files(ROOT / "docs/evidence") != expected_evidence:
        errors.append("docs/evidence must contain only current evidence entries")

    program_root = ROOT / ".agent" / "programs"
    if {path.name for path in program_root.glob("*.md")} != {"README.md", "current.md"}:
        errors.append(".agent/programs front must contain README.md and current.md")
    current = (program_root / "current.md").read_text(encoding="utf-8")
    for phrase in ("state: `no-active`", "active_program: `none`", "SUPERSEDED / RETIRED"):
        if phrase not in current:
            errors.append(f"current program missing {phrase}")

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
