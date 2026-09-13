from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
MODULE_NAMES = (
    "application",
    "domain",
    "knowledge",
    "runtime",
    "capability",
    "effects",
    "model-gateway",
    "security",
    "evaluation",
)
MODULE_FILES = tuple(
    f"docs/modules/{name}/{filename}"
    for name in MODULE_NAMES
    for filename in ("README.md", "reference.md")
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
ROUND_REQUIRED_FILES = {
    "00_manifest.yaml",
    "01_simulated_resume.md",
    "02_red_questions.md",
    "03_blue_answers.md",
    "04_red_evaluation.md",
    "05_blue_architecture_reflection.md",
    "06_workflow_retrospective.md",
    "07_user_feedback.md",
    "08_session_transcript.md",
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
    if not (program_root / "current.md").exists():
        errors.append("missing current program")
    return errors


def verify_red_blue_harness(root: Path) -> list[str]:
    errors: list[str] = []
    red_blue_root = root / ".agent" / "red-blue"
    if not red_blue_root.exists():
        return ["missing .agent/red-blue harness"]

    actual_files = _relative_files(root, red_blue_root)
    if actual_files != RED_BLUE_FILES:
        errors.append(f"red-blue harness mismatch: expected {sorted(RED_BLUE_FILES)}, got {sorted(actual_files)}")
        return errors

    workspace_readme = root / "docs" / "red-blue" / "workspace" / "README.md"
    if not workspace_readme.exists():
        errors.append("missing docs/red-blue/workspace/README.md")

    current = (red_blue_root / "current.md").read_text(encoding="utf-8")
    inactive = all(phrase in current for phrase in ("state: `no-active`", "active_round: `none`"))
    active = False if inactive else (
        "state: `active-red-blue`" in current
        and re.search(r"active_round: `(?!none`)[^`]+`", current) is not None
    )
    if not (inactive or active):
        errors.append("red-blue current state is neither recognized inactive nor active-red-blue")
    for marker in (
        "CHATGPT_AUTO", "AGENT_AUTO", "stage:", "workspace_path:", "simulated_resume:",
        "question_count", "full-observable-role-io", "archive_live",
    ):
        if marker not in current:
            errors.append(f"red-blue current contract missing marker: {marker}")
    if "human-candidate" in current:
        errors.append("human-candidate must not remain an active red-blue mode")

    if active:
        workspace_match = re.search(r"workspace_path: `([^`]+)`", current)
        if workspace_match is None:
            errors.append("active red-blue round missing workspace_path")
        else:
            workspace = root / workspace_match.group(1)
            if not workspace.exists():
                errors.append(f"active red-blue workspace missing: {workspace_match.group(1)}")
            elif not (workspace / "00_manifest.yaml").exists():
                errors.append("active red-blue workspace must start with 00_manifest.yaml")

    protocol = (red_blue_root / "protocol.md").read_text(encoding="utf-8")
    for marker in (
        "Context Firewall", "CHATGPT_AUTO", "AGENT_AUTO", "Resume Builder",
        "BUILD_SIMULATED_RESUME", "RED_QUESTIONS", "BLUE_ANSWERS", "RED_EVALUATION",
        "BLUE_ARCHITECTURE_REFLECTION", "WORKFLOW_RETROSPECTIVE",
        "01_simulated_resume.md", "禁止输入", "docs/project/",
        "Zuno 源码 / PR / commit diff", "08_session_transcript.md",
    ):
        if marker.lower() not in protocol.lower():
            errors.append(f"red-blue protocol missing required execution marker: {marker}")

    attack_model = (red_blue_root / "attack-model.md").read_text(encoding="utf-8")
    for marker in (
        "精品思维", "全链路追踪", "不重复造轮子", "Ownership", "Build / Buy",
        "100 问", "Red 自我质量检查", "Skill 也必须接受审判",
    ):
        if marker not in attack_model:
            errors.append(f"red-blue attack model missing required marker: {marker}")

    round_template = (red_blue_root / "templates" / "round.md").read_text(encoding="utf-8")
    for marker in (
        "Simulated Resume Build", "Red Input Allowlist", "Explicit denylist",
        "Red Evaluation Input", "Blue Architecture Reflection Input", "Workflow Retrospective Input",
        *sorted(ROUND_REQUIRED_FILES),
    ):
        if marker not in round_template:
            errors.append(f"red-blue round template missing resume-first marker: {marker}")

    stage_template = (red_blue_root / "templates" / "turn.md").read_text(encoding="utf-8")
    for marker in (
        "01_simulated_resume.md", "02_red_questions.md", "03_blue_answers.md",
        "04_red_evaluation.md", "05_blue_architecture_reflection.md",
        "06_workflow_retrospective.md", "07_user_feedback.md", "08_session_transcript.md",
    ):
        if marker not in stage_template:
            errors.append(f"red-blue stage template missing marker: {marker}")

    judge = (red_blue_root / "judge.md").read_text(encoding="utf-8")
    for marker in (
        "Red Evaluation", "Blue Architecture Reflection", "SIMULATED_RESUME_GAP",
        "ARCHITECTURE_GAP", "FUNDAMENTAL_GAP", "Workflow Retrospective",
    ):
        if marker not in judge:
            errors.append(f"red-blue evaluation rules missing required marker: {marker}")

    return errors


def verify_system_yaml(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / ".agent" / "system.yaml"
    if not path.exists():
        return ["missing .agent/system.yaml"]
    content = path.read_text(encoding="utf-8")
    for marker in (
        "version:",
        "system_identity:",
        "runtime_boundary:",
        "truth_rules:",
        "view_rules:",
        'human_filename: "README.md"',
        'engineering_filename: "reference.md"',
        "human_and_engineering_must_preserve_same_authority_semantics: true",
        "program_rules:",
        "module_rules:",
        "complexity_rules:",
        "skill_routes:",
        'project_root: "docs/project"',
        'architecture_root: "docs/architecture"',
        'modules_root: "docs/modules"',
        'red_blue_docs_root: "docs/red-blue"',
        'red_blue_workspace_root: "docs/red-blue/workspace"',
        'red_blue_rounds_root: "docs/red-blue/rounds"',
        'research_root: "docs/research"',
        'decisions_root: "docs/decisions"',
        'evidence_root: "docs/evidence"',
        'governance_root: "docs/governance"',
        'terminology: "docs/governance/terminology.md"',
        'red_blue_runtime_root: ".agent/red-blue"',
        'red_blue_current_owner: ".agent/red-blue/current.md"',
        "red_blue_requires_explicit_activation: true",
        "blue_closed_book: true",
        'red_blue_modes: ["CHATGPT_AUTO", "AGENT_AUTO"]',
        "red_blue_resume_first: true",
        "red_reads_zuno_docs: false",
        "red_reads_only_simulated_resume_and_attack_skill: true",
        "simulated_resume_built_from_current_docs_before_red: true",
        "red_question_count_default: 100",
        "red_blue_one_round_one_question_batch: true",
        "red_blue_retest_requires_new_round: true",
        "red_blue_user_feedback_required: true",
        "red_blue_workflow_retrospective_required: true",
        "human_candidate_mode_removed: true",
        "module_count_is_documentation_invariant: false",
        "research_is_upstream_only: true",
        "red_blue_findings_are_non_authoritative: true",
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
        "docs/project/reference.md",
        "docs/architecture/README.md",
        "docs/architecture/reference.md",
        "docs/modules/README.md",
        "docs/modules/reference.md",
        "docs/red-blue/README.md",
        "docs/red-blue/workspace/README.md",
        "docs/red-blue/rounds/README.md",
        "docs/research/README.md",
        "docs/decisions/README.md",
        "docs/evidence/README.md",
        "docs/governance/README.md",
        "docs/governance/terminology.md",
        "docs/governance/workflows/agent-workflow.md",
        "docs/governance/operations/postgresql-migration-runbook.md",
        *MODULE_FILES,
    ):
        if not (root / relative).exists():
            errors.append(f"system.yaml route target missing: {relative}")

    for name in MODULE_NAMES:
        human = f'human: "docs/modules/{name}/README.md"'
        engineering = f'engineering: "docs/modules/{name}/reference.md"'
        if human not in content:
            errors.append(f"system.yaml missing human module route: {name}")
        if engineering not in content:
            errors.append(f"system.yaml missing engineering module route: {name}")

    for obsolete in ("docs/maintenance", "docs/terminology.md"):
        if (root / obsolete).exists():
            errors.append(f"obsolete route target must be absent: {obsolete}")
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
    for template_root in (root / ".agent" / "templates", root / ".agent" / "red-blue" / "templates"):
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
    has_design_state = "state: `active-design-program`" in current and re.search(r"active_program: `(?!none`)[^`]+`", current) is not None
    has_implementation_evidence_state = "state: `active-implementation-evidence-program`" in current and re.search(r"active_program: `(?!none`)[^`]+`", current) is not None
    if not (has_no_active_state or has_design_state or has_implementation_evidence_state):
        errors.append("current program has no recognized design/implementation state")

    if errors:
        print("AGENT_SYSTEM_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1
    print("AGENT_SYSTEM_VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
