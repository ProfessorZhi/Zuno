from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    errors: list[str] = []
    references = ROOT / ".agent" / "references"
    expected_references = {
        "README.md",
        "current-program.md",
        "docs-map.md",
        "code-map.md",
        "task-routing.md",
        "workflow.md",
        "verification-map.md",
        "debugging.md",
        "known-pitfalls.md",
    }
    actual_references = {path.name for path in references.glob("*.md")}
    if actual_references != expected_references:
        errors.append(f"references mismatch: expected {sorted(expected_references)}, got {sorted(actual_references)}")

    expected_program_files = {"README.md", "current.md"}
    program_root = ROOT / ".agent" / "programs"
    actual_program_files = {path.name for path in program_root.glob("*.md")}
    if actual_program_files != expected_program_files:
        errors.append(f"program front mismatch: {sorted(actual_program_files)}")
    queued = program_root / "queued-programs"
    if {path.name for path in queued.glob("*.md")} != {"README.md"}:
        errors.append("queued program directory must contain only its README")

    current = (program_root / "current.md").read_text(encoding="utf-8")
    for phrase in ("state: `no-active`", "active_program: `none`", "queued_program: `none`", "SUPERSEDED / RETIRED"):
        if phrase not in current:
            errors.append(f"current program missing: {phrase}")

    for relative in (
        "AGENTS.md",
        ".agent/system.yaml",
        ".agent/README.md",
        ".agent/scripts/verify_doc_boundaries.py",
        ".agent/scripts/verify_repo_hygiene.py",
        "docs/history/README.md",
        "docs/evidence/README.md",
    ):
        if not (ROOT / relative).exists():
            errors.append(f"missing required path: {relative}")

    if errors:
        print("AGENT_SYSTEM_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AGENT_SYSTEM_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
