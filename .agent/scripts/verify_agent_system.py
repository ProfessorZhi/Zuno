from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]


def verify_programs_flat(root: Path) -> list[str]:
    errors: list[str] = []
    program_root = root / ".agent" / "programs"
    expected_front = {"README.md", "current.md"}
    actual_front = {path.name for path in program_root.glob("*.md")}
    if actual_front != expected_front:
        errors.append(f"program front mismatch: expected {sorted(expected_front)}, got {sorted(actual_front)}")
    queued = program_root / "queued-programs"
    if {path.name for path in queued.glob("*.md")} != {"README.md"}:
        errors.append("queued program directory must contain only its README")

    current = program_root / "current.md"
    if not current.exists():
        errors.append("missing current program")
    return errors


def verify_system_yaml(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / ".agent" / "system.yaml"
    if not path.exists():
        return ["missing .agent/system.yaml"]
    content = path.read_text(encoding="utf-8")
    for marker in ("version:", "system_identity:", "runtime_boundary:", "program_rules:", "skill_routes:"):
        if marker not in content:
            errors.append(f"system.yaml missing section: {marker}")
    for relative in ("AGENTS.md", ".agent/programs/current.md", "docs/project/README.md"):
        if not (root / relative).exists():
            errors.append(f"system.yaml route target missing: {relative}")
    return errors


def verify_skill_links(root: Path) -> list[str]:
    errors: list[str] = []
    link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for path in (root / ".agent").rglob("*.md"):
        if "local" in path.parts:
            continue
        for raw_target in link_pattern.findall(path.read_text(encoding="utf-8")):
            target = raw_target.strip().split("#", 1)[0]
            if not target or target.startswith(("http://", "https://", "mailto:", "<")):
                continue
            target_path = (path.parent / target).resolve()
            if not target_path.exists():
                errors.append(f"broken agent link: {path.relative_to(root)} -> {raw_target}")
    return errors


def verify_templates_have_required_sections(root: Path) -> list[str]:
    errors: list[str] = []
    template_root = root / ".agent" / "templates"
    for path in template_root.glob("*.md"):
        if path.name == "README.md":
            continue
        content = path.read_text(encoding="utf-8")
        if not content.lstrip().startswith("#"):
            errors.append(f"template missing title: {path.relative_to(root)}")
        if "##" not in content:
            errors.append(f"template missing section: {path.relative_to(root)}")
    return errors


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

    errors.extend(verify_programs_flat(ROOT))
    errors.extend(verify_system_yaml(ROOT))
    errors.extend(verify_skill_links(ROOT))
    errors.extend(verify_templates_have_required_sections(ROOT))

    current = (ROOT / ".agent" / "programs" / "current.md").read_text(encoding="utf-8")
    has_no_active_state = all(phrase in current for phrase in ("state: `no-active`", "active_program: `none`"))
    has_design_state = "state: `active-design-program`" in current and re.search(
        r"active_program: `(?!none`)[^`]+`", current
    ) is not None
    if not (has_no_active_state or has_design_state):
        errors.append("current program has no recognized design/implementation state")
    for phrase in ("queued_program: `none`", "SUPERSEDED / RETIRED"):
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
