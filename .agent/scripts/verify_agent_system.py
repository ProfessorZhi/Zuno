from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
MODULE_FILES = (
    "docs/modules/01-application-integration.md",
    "docs/modules/02-legal-domain-work-product.md",
    "docs/modules/03-knowledge-evidence.md",
    "docs/modules/04-agent-runtime-control.md",
    "docs/modules/05-capability-skill.md",
    "docs/modules/06-tool-runtime-effects.md",
    "docs/modules/07-model-gateway.md",
    "docs/modules/08-security-governance.md",
    "docs/modules/09-observability-evaluation.md",
)
RED_BLUE_FILES = {
    ".agent/red-blue/README.md",
    ".agent/red-blue/current.md",
    ".agent/red-blue/protocol.md",
    ".agent/red-blue/attack-model.md",
    ".agent/red-blue/judge.md",
    ".agent/red-blue/templates/round.md",
    ".agent/red-blue/templates/turn.md",
}


def _relative_files(root: Path, directory: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in directory.rglob("*") if path.is_file()}


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


def verify_red_blue_harness(root: Path) -> list[str]:
    errors: list[str] = []
    red_blue_root = root / ".agent" / "red-blue"
    if not red_blue_root.exists():
        return ["missing .agent/red-blue harness"]

    actual_files = _relative_files(root, red_blue_root)
    if actual_files != RED_BLUE_FILES:
        errors.append(
            f"red-blue harness mismatch: expected {sorted(RED_BLUE_FILES)}, got {sorted(actual_files)}"
        )
        return errors

    current = (red_blue_root / "current.md").read_text(encoding="utf-8")
    inactive = all(phrase in current for phrase in ("state: `no-active`", "active_round: `none`"))
    active = "state: `active-red-blue`" in current and re.search(
        r"active_round: `(?!none`)[^`]+`", current
    ) is not None
    if not (inactive or active):
        errors.append("red-blue current state is neither recognized inactive nor active-red-blue")

    protocol = (red_blue_root / "protocol.md").read_text(encoding="utf-8")
    for marker in ("Context Firewall", "ChatGPT Duel", "Autonomous Agent", "Closed-book"):
        if marker not in protocol:
            errors.append(f"red-blue protocol missing required execution marker: {marker}")

    attack_model = (red_blue_root / "attack-model.md").read_text(encoding="utf-8")
    for marker in ("Ownership Claim", "Build / Buy", "面经校准", "一次只"):
        if marker not in attack_model:
            errors.append(f"red-blue attack model missing required marker: {marker}")

    judge = (red_blue_root / "judge.md").read_text(encoding="utf-8")
    for marker in ("UNSUPPORTED_CLAIM", "NARRATIVE_GAP", "ARCHITECTURE_GAP", "OWNERSHIP_GAP"):
        if marker not in judge:
            errors.append(f"red-blue judge missing required marker: {marker}")

    return errors


def verify_system_yaml(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / ".agent" / "system.yaml"
    if not path.exists():
        return ["missing .agent/system.yaml"]
    content = path.read_text(encoding="utf-8")
    for marker in (
        "version:", "system_identity:", "runtime_boundary:", "program_rules:", "skill_routes:",
        "project_narrative:", "research_root:", "maintenance_root:",
        'red_blue_runtime_root: ".agent/red-blue"',
        'red_blue_workflow_root: "docs/maintenance/red-blue"',
        'red_blue_current_owner: ".agent/red-blue/current.md"',
        "red_blue_requires_explicit_activation: true",
        "blue_closed_book: true",
        "red_blue_harness:", "red_blue_workflow:", "red_blue_interview:",
        'module_design_state: "deep-design-v2"',
        'module_detail_design_candidate: "candidate-v1"',
        'module_detail_design_candidate_modules: ["01", "02", "03", "04", "05", "06", "07", "08", "09"]',
        "research_does_not_equal_canonical_truth: true",
        "detail_candidate_does_not_equal_freeze: true",
        "module_freeze_precedes_implementation_planning: true",
        "detail_design_candidates:", "detail_design_review:",
    ):
        if marker not in content:
            errors.append(f"system.yaml missing section/route: {marker}")
    for relative in (
        "AGENTS.md",
        ".agent/programs/current.md",
        ".agent/red-blue/README.md",
        ".agent/red-blue/current.md",
        ".agent/red-blue/protocol.md",
        ".agent/red-blue/attack-model.md",
        ".agent/red-blue/judge.md",
        "docs/README.md",
        "docs/project/README.md",
        "docs/project/project.md",
        "docs/research/README.md",
        "docs/maintenance/README.md",
        "docs/maintenance/agent-workflow/README.md",
        "docs/maintenance/red-blue/README.md",
        "docs/maintenance/history/README.md",
        *MODULE_FILES,
    ):
        if not (root / relative).exists():
            errors.append(f"system.yaml route target missing: {relative}")
    registry = re.search(r"local_skill_registry:\n(?P<body>.*?)(?=\n\S|\Z)", content, re.DOTALL)
    if not registry:
        errors.append("system.yaml missing local_skill_registry")
    else:
        for skill_path in re.findall(r"^\s+path:\s+\"([^\"]+)\"$", registry.group("body"), re.MULTILINE):
            if not (root / skill_path).exists():
                errors.append(f"local skill route target missing: {skill_path}")
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
    template_roots = (root / ".agent" / "templates", root / ".agent" / "red-blue" / "templates")
    for template_root in template_roots:
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
        "README.md", "current-program.md", "docs-map.md", "code-map.md", "task-routing.md",
        "workflow.md", "verification-map.md", "debugging.md", "known-pitfalls.md",
    }
    actual_references = {path.name for path in references.glob("*.md")}
    if actual_references != expected_references:
        errors.append(f"references mismatch: expected {sorted(expected_references)}, got {sorted(actual_references)}")

    errors.extend(verify_programs_flat(ROOT))
    errors.extend(verify_red_blue_harness(ROOT))
    errors.extend(verify_system_yaml(ROOT))
    errors.extend(verify_skill_links(ROOT))
    errors.extend(verify_templates_have_required_sections(ROOT))

    current = (ROOT / ".agent" / "programs" / "current.md").read_text(encoding="utf-8")
    has_no_active_state = all(phrase in current for phrase in ("state: `no-active`", "active_program: `none`"))
    has_design_state = "state: `active-design-program`" in current and re.search(
        r"active_program: `(?!none`)[^`]+`", current
    ) is not None
    has_implementation_evidence_state = "state: `active-implementation-evidence-program`" in current and re.search(
        r"active_program: `(?!none`)[^`]+`", current
    ) is not None
    if not (has_no_active_state or has_design_state or has_implementation_evidence_state):
        errors.append("current program has no recognized design/implementation state")
    for phrase in ("queued_program: `none`", "SUPERSEDED / RETIRED"):
        if phrase not in current:
            errors.append(f"current program missing: {phrase}")

    for relative in (
        "AGENTS.md", ".agent/system.yaml", ".agent/README.md",
        ".agent/scripts/verify_doc_boundaries.py", ".agent/scripts/verify_repo_hygiene.py",
        ".agent/red-blue/README.md", ".agent/red-blue/current.md", ".agent/red-blue/protocol.md",
        ".agent/red-blue/attack-model.md", ".agent/red-blue/judge.md",
        "docs/project/README.md", "docs/project/project.md", "docs/research/README.md",
        "docs/governance/project-fact-provenance.md",
        "docs/governance/human-first-documentation-standard.md",
        "docs/maintenance/README.md", "docs/maintenance/agent-workflow/README.md",
        "docs/maintenance/red-blue/README.md", "docs/maintenance/history/README.md",
        "docs/evidence/README.md",
        *MODULE_FILES,
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
