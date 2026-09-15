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
    ".agent/red-blue/defense-model.md",
    ".agent/red-blue/judge.md",
    ".agent/red-blue/templates/round.md",
    ".agent/red-blue/templates/turn.md",
}
ROUND_CORE_FILES = {
    "00_manifest.yaml",
    "01_simulated_resume.md",
    "02_red_questions.md",
    "03_blue_answers.md",
    "04_red_evaluation.md",
    "05_blue_architecture_reflection.md",
    "06_workflow_retrospective.md",
    "07_user_feedback.md",
    "08_session_transcript.md",
    "09_improvement_ledger.md",
    "10_next_resume_candidate.md",
}
ROUND_BATCH_FILES = {
    "03_blue_architecture_notes.md",
    "04_red_wave2_review_and_questions.md",
    "04_blue_wave2_answers.md",
    "04_blue_wave2_architecture_notes.md",
    "09_round_report.md",
}


def _relative_files(root: Path, directory: Path) -> set[str]:
    return {path.relative_to(root).as_posix() for path in directory.rglob("*") if path.is_file()}


def _require(content: str, markers: tuple[str, ...], prefix: str) -> list[str]:
    return [f"{prefix} missing marker: {marker}" for marker in markers if marker not in content]


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

    for required in (
        root / "docs" / "red-blue" / "workspace" / "README.md",
        root / "docs" / "red-blue" / "rounds" / "README.md",
        root / "docs" / "red-blue" / "interview-behavior-evidence-2026-09.md",
    ):
        if not required.exists():
            errors.append(f"missing {required.relative_to(root)}")

    current = (red_blue_root / "current.md").read_text(encoding="utf-8")
    inactive = all(phrase in current for phrase in ("state: `no-active`", "active_round: `none`"))
    active = False if inactive else (
        "state: `active-red-blue`" in current
        and re.search(r"active_round: `(?!none`)[^`]+`", current) is not None
    )
    if not (inactive or active):
        errors.append("red-blue current state is neither recognized inactive nor active-red-blue")

    errors.extend(_require(current, (
        "execution_mode: `BATCH_DUEL`",
        "red_wave_1_question_target: `100`",
        "blue_wave_1_answer_target: `100`",
        "red_wave_2_question_target: `100`",
        "blue_wave_2_answer_target: `100`",
        "batch_checkpoint_policy: `LINK_ONLY_PAUSE`",
        "red_wave_1_status:",
        "blue_wave_1_status:",
        "red_wave_2_status:",
        "blue_wave_2_status:",
        "red_evaluation_status:",
        "blue_reflection_status:",
        "workflow_retrospective_status:",
        "improvement_ledger_status:",
        "round_report_status:",
        "next_resume_candidate_status:",
        "commit-then-reread",
    ), "red-blue current contract"))

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
    errors.extend(_require(protocol, (
        "GitHub 是运行时状态总线",
        "BATCH_DUEL",
        "BUILD_SIMULATED_RESUME",
        "USER_RESUME_REVIEW",
        "RED_WAVE_1",
        "BLUE_WAVE_1",
        "RED_WAVE_2",
        "BLUE_WAVE_2",
        "BATCH_CHECKPOINT_RED_1",
        "BATCH_CHECKPOINT_BLUE_1",
        "BATCH_CHECKPOINT_RED_2",
        "BATCH_CHECKPOINT_BLUE_2",
        "RED_EVALUATION",
        "BLUE_ARCHITECTURE_REFLECTION",
        "WORKFLOW_RETROSPECTIVE",
        "IMPROVEMENT_SYNTHESIS",
        "ROUND_REPORT",
        "USER_IMPROVEMENT_REVIEW",
        "BUILD_NEXT_RESUME_CANDIDATE",
        "03_blue_architecture_notes.md",
        "04_red_wave2_review_and_questions.md",
        "04_blue_wave2_answers.md",
        "04_blue_wave2_architecture_notes.md",
        "09_round_report.md",
        "Exactly 100 Targeted Follow-ups",
        "BATCH_CHECKPOINT_*",
        "LIVE_INTERVIEW",
        "Context Firewall",
    ), "red-blue protocol"))

    attack = (red_blue_root / "attack-model.md").read_text(encoding="utf-8")
    errors.extend(_require(attack, (
        "精品思维",
        "BATCH_DUEL",
        "每一波固定 100 问",
        "一问一个主要意图",
        "Red Wave 2：评价 + 追杀",
        "Answer-driven handles",
        "KILL_SWITCH: CLAIM_IMPLEMENTATION_NOT_ESTABLISHED",
        "全链路追踪",
        "Build / Buy / Extend / Defer",
        "Multi-Agent 不是正确答案",
        "Red Final Evaluation",
        "Red 自我质量检查",
        "Skill 也必须接受审判",
    ), "red-blue attack model"))

    defense = (red_blue_root / "defense-model.md").read_text(encoding="utf-8")
    errors.extend(_require(defense, (
        "Candidate Mode",
        "Architecture Reviewer Mode",
        "HISTORICAL_OWNERSHIP",
        "CURRENT_SYSTEM",
        "TARGET_DESIGN",
        "OPEN_DESIGN",
        "FUNDAMENTAL",
        "Ownership",
        "Evidence",
        "Unknown 与边界",
        "Failure / Recovery",
        "Build / Buy / Delete",
        "Multi-Agent 的回答框架",
        "03_blue_answers.md",
        "04_blue_wave2_answers.md",
        "03_blue_architecture_notes.md",
        "04_blue_wave2_architecture_notes.md",
        "Architecture Gap 的高门槛",
        "Final Architecture Reflection",
        "Blue 自检",
        "Blue Skill 也必须接受审判",
    ), "red-blue defense model"))

    round_template = (red_blue_root / "templates" / "round.md").read_text(encoding="utf-8")
    errors.extend(_require(round_template, (
        "execution_mode: BATCH_DUEL | LIVE_INTERVIEW",
        "red_wave_1_question_count: 0..100",
        "blue_wave_1_answer_count: 0..100",
        "red_wave_2_question_count: 0..100",
        "blue_wave_2_answer_count: 0..100",
        "Blue Wave 1",
        "Red Wave 2",
        "Blue Wave 2",
        "blue_wave_1_blind_evaluation_present",
        "RED_WAVE_2 allowlist",
        "Workflow Retrospective",
        "Improvement Ledger / Round Report",
        "BATCH_DUEL 额外要求",
        "Red Wave 1 == 100 questions",
        "Blue Wave 1 == 100 answers",
        "Red Wave 2 contains Blue-1 blind evaluation + exactly 100 new questions",
        "Blue Wave 2 == 100 answers",
        "LIVE_INTERVIEW State",
        *sorted(ROUND_CORE_FILES),
        *sorted(ROUND_BATCH_FILES),
    ), "red-blue round template"))

    turn = (red_blue_root / "templates" / "turn.md").read_text(encoding="utf-8")
    errors.extend(_require(turn, (
        "Red Wave 1",
        "Blue Wave 1 Candidate Answers",
        "Sealed Wave 1 Diagnosis",
        "Red Wave 2",
        "Blue Wave 2 Candidate Answers",
        "Sealed Wave 2 Diagnosis",
        "Final Blind Evaluation",
        "Final Architecture Reflection",
        "Red Thinking Framework Reflection",
        "Blue Candidate Framework Reflection",
        "Blue Architecture Framework Reflection",
        "Harness Reflection",
        "BATCH_CHECKPOINT 用户输出",
        "09_round_report.md",
        "NEXT_ROUND_ONLY",
        *sorted(ROUND_CORE_FILES),
        *sorted(ROUND_BATCH_FILES),
    ), "red-blue stage template"))

    judge = (red_blue_root / "judge.md").read_text(encoding="utf-8")
    errors.extend(_require(judge, (
        "Red Wave 2 Blind Review",
        "Red Final Evaluation",
        "Blue Architecture Reflection",
        "Architecture Revision 的评审框架",
        "Workflow Retrospective",
        "Red Thinking Framework",
        "Blue Thinking Framework",
        "Harness",
        "Improvement Classification",
        "Round Report",
        "NEXT_ROUND_ONLY",
        "RED_SKILL_GAP",
        "BLUE_SKILL_GAP",
        "HARNESS_GAP",
        "ARCHITECTURE_GAP",
        "FUNDAMENTAL_GAP",
    ), "red-blue evaluation rules"))

    return errors


def verify_system_yaml(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / ".agent" / "system.yaml"
    if not path.exists():
        return ["missing .agent/system.yaml"]
    content = path.read_text(encoding="utf-8")

    required = (
        "version:",
        "system_identity:",
        "runtime_boundary:",
        "truth_rules:",
        "view_rules:",
        "program_rules:",
        "module_rules:",
        "complexity_rules:",
        "skill_routes:",
        "red_blue_requires_explicit_activation: true",
        'red_blue_modes: ["CHATGPT_AUTO", "AGENT_AUTO"]',
        'red_blue_default_execution_mode: "BATCH_DUEL"',
        'red_blue_optional_execution_mode: "LIVE_INTERVIEW"',
        "red_blue_resume_first: true",
        "red_reads_zuno_docs: false",
        "resume_must_freeze_before_red: true",
        "red_batch_wave_question_count: 100",
        "blue_batch_wave_answer_count: 100",
        "red_wave_1_exact_question_count_required: true",
        "blue_wave_1_exact_answer_count_required: true",
        "red_wave_2_exact_question_count_required: true",
        "blue_wave_2_exact_answer_count_required: true",
        "red_wave_2_requires_blue_1_blind_evaluation: true",
        "red_wave_2_must_be_answer_driven: true",
        "red_wave_2_cannot_read_blue_architecture_notes: true",
        "red_final_cannot_read_blue_architecture_notes: true",
        "blue_architecture_notes_sealed_from_red: true",
        "blue_wave_2_candidate_cannot_read_wave_1_architecture_notes: true",
        "blue_architecture_reflection_after_blue_2_required: true",
        'red_blue_batch_checkpoint_policy: "link_only_pause"',
        "red_blue_user_does_not_answer_batch_questions: true",
        "red_blue_round_report_required: true",
        "red_blue_red_thinking_framework_retrospective_required: true",
        "red_blue_blue_candidate_framework_retrospective_required: true",
        "red_blue_blue_architecture_framework_retrospective_required: true",
        "red_blue_harness_retrospective_required: true",
        "red_blue_architecture_can_be_revised_after_user_gate: true",
        "red_blue_current_round_verdict_immutable_after_reflection: true",
        "red_blue_post_round_changes_next_round_only: true",
        "red_blue_next_resume_candidate_required: true",
        "red_blue_next_round_revalidates_resume: true",
        "red_blue_github_state_bus: true",
        'red_blue_stage_handoff: "commit_then_reread"',
        "red_blue_round_branch_required: true",
        "red_blue_draft_pr_required: true",
        "human_candidate_mode_removed: true",
        "module_count_is_documentation_invariant: false",
        "research_is_upstream_only: true",
        "red_blue_findings_are_non_authoritative: true",
    )
    errors.extend(_require(content, required, "system.yaml"))

    for relative in (
        "AGENTS.md",
        ".agent/programs/current.md",
        ".agent/red-blue/README.md",
        ".agent/red-blue/current.md",
        ".agent/red-blue/protocol.md",
        ".agent/red-blue/attack-model.md",
        ".agent/red-blue/defense-model.md",
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
        "docs/red-blue/interview-behavior-evidence-2026-09.md",
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
        if f'human: "docs/modules/{name}/README.md"' not in content:
            errors.append(f"system.yaml missing human module route: {name}")
        if f'engineering: "docs/modules/{name}/reference.md"' not in content:
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
            if not (path.parent / target).resolve().exists():
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