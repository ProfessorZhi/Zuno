from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


REQUIRED_PATHS = [
    "AGENTS.md",
    "apps/web/AGENTS.md",
    "tools/evals/zuno/AGENTS.md",
    ".agent/README.md",
    ".agent/system.yaml",
    ".agent/references/README.md",
    ".agent/references/task-routing.md",
    ".agent/references/workflow.md",
    ".agent/references/code-map.md",
    ".agent/references/runtime-call-chain.md",
    ".agent/references/verification-map.md",
    ".agent/references/zuno-repo-hygiene.md",
    ".agent/references/docs-map.md",
    ".agent/references/current-program.md",
    ".agent/references/command-catalog.md",
    ".agent/references/known-pitfalls.md",
    ".agent/scripts/verify_module_boundaries.py",
    ".agent/architecture/README.md",
    ".agent/architecture/decisions/README.md",
    ".agent/architecture/future/README.md",
    ".agent/architecture/near-term/README.md",
    ".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html",
    ".agent/architecture/near-term/01-target-runtime-architecture.md",
    ".agent/architecture/near-term/02-context-memory-architecture.md",
    ".agent/architecture/near-term/03-capability-tool-retrieval-architecture.md",
    ".agent/architecture/near-term/04-knowledge-graphrag-retrieval-fusion.md",
    ".agent/architecture/near-term/05-repository-boundaries-and-acceptance-gates.md",
    ".agent/programs/README.md",
    ".agent/programs/current.md",
    ".agent/programs/implementation-roadmap.md",
    ".agent/programs/closure-checklist.md",
    ".agent/architecture/future/programs/README.md",
    ".agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md",
    ".agent/architecture/future/programs/zuno-architecture-visuals-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-workflow-doc-system-v1/README.md",
    "docs/history/programs/zuno-workflow-doc-system-v1/PHASE03_skill-template-program-system.md",
    "docs/history/programs/zuno-target-architecture-refresh-v1/README.md",
    "docs/history/programs/zuno-target-architecture-refresh-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-target-architecture-refresh-v1/PHASE03_graphrag-llm-entity-knowledge-config.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/README.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE01_repo-layout-audit.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE02_root-docs-hygiene.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE03_backend-six-layer-migration-plan.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE04_small-boundary-cleanups.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE05_hygiene-verifier-closure.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE06_backend-directory-clarity-audit.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE07_fastapi-jwt-auth-compat-retirement-plan.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE08_backend-physical-cleanup-slices.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE09_target-layout-visual-compat-shell-retirement.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE10_alias-inventory-and-target-contract.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE11_import-smoke-and-compat-registry-design.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE12_low-risk-alias-surface-cleanup.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE13_medium-risk-alias-surface-cleanup.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE14_high-risk-core-services-settings-cleanup.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/PHASE15_final-root-surface-guard-and-closure.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/thread-prompts/THREAD_A_root-docs-agent-hygiene-prompt.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/thread-prompts/THREAD_B_backend-six-layer-audit-prompt.md",
    "docs/history/programs/zuno-repo-layout-cleanup-v1/thread-prompts/THREAD_C_tools-tests-generated-artifacts-prompt.md",
    "docs/history/programs/zuno-target-runtime-v2/README.md",
    "docs/history/programs/zuno-target-architecture-migration-v1/README.md",
    "docs/history/programs/zuno-target-architecture-migration-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-target-architecture-migration-v1/implementation-phases/README.md",
    "docs/history/programs/zuno-architecture-surface-cleanup-v1/README.md",
    "docs/history/programs/README.md",
]

FORBIDDEN_PATHS = [
    "agent.md",
    ".agent.md",
    ".agentmd",
    ".agents",
    ".agent/skills",
    ".agent/workflows",
    ".agent/programs/context-memory-agent-runtime-v1",
    ".agent/programs/zuno-target-runtime-v2",
    ".agent/programs/implementation-phases",
    ".agent/programs/evidence",
    ".agent/programs/phase-05-memory-engine.md",
    ".agent/programs/phase-06-capability-tool-retrieval.md",
    ".agent/programs/phase-07-graphrag-llm-entity-extraction.md",
    ".agent/programs/phase-08-langgraph-runtime.md",
    ".agent/programs/phase-09-product-trace-eval-closure.md",
    ".agent/programs/PHASE01_workflow-doc-audit.md",
    ".agent/programs/PHASE02_agent-bootloader-routing.md",
    ".agent/programs/PHASE03_skill-template-program-system.md",
    ".agent/programs/PHASE04_workflow-verifiers-drift-tests.md",
    ".agent/programs/PHASE05_closure-history-archive.md",
    ".agent/notes",
    ".agent/tmp",
    ".agent/logs",
    ".agent/secrets",
]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


SKILL_SECTIONS = [
    "When To Use",
    "Mental Model",
    "Current Truth",
    "Target Direction",
    "Must Preserve",
    "Before Editing",
    "Allowed Changes",
    "Forbidden Changes",
    "Common Failure Patterns",
    "Debug Playbooks",
    "Focused Tests",
    "Docs Sync",
    "Lessons Learned",
]


def _repo_path(repo_root: Path, value: str) -> Path:
    return repo_root / value.replace("/", "\\")


def verify_programs_flat(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    programs_root = repo_root / ".agent" / "programs"
    if not programs_root.exists():
        return ["missing .agent/programs"]

    directories = sorted(path.name for path in programs_root.iterdir() if path.is_dir())
    allowed_directories = ["thread-prompts"]
    unexpected_directories = [name for name in directories if name not in allowed_directories]
    if unexpected_directories:
        errors.append(
            f".agent/programs only allows thread-prompts as a helper directory; found: {unexpected_directories}"
        )

    phase_files = sorted(
        path.name for path in programs_root.iterdir() if path.is_file() and path.name.startswith("PHASE")
    )
    if not phase_files:
        current_path = programs_root / "current.md"
        if not current_path.exists() or "当前没有 active program" not in current_path.read_text(
            encoding="utf-8"
        ):
            errors.append(".agent/programs has no PHASE files but current.md does not declare no active program")
        return errors

    phase_numbers: list[int] = []
    for name in phase_files:
        match = re.fullmatch(r"PHASE(\d{2})_[A-Za-z0-9_-]+\.md", name)
        if not match:
            errors.append(f"active phase filename does not match PHASENN_name.md: {name}")
            continue
        phase_numbers.append(int(match.group(1)))

    current_text = ""
    current_path = programs_root / "current.md"
    if current_path.exists():
        current_text = current_path.read_text(encoding="utf-8")
    continuation_mode = (
        "Program 3 continuation" in current_text
        or "Program 3 definition 修正" in current_text
        or "Program 3 定义修正" in current_text
    )
    expected_start = 6 if continuation_mode and "Directory Surface Alignment" not in current_text else 1
    if phase_numbers and min(phase_numbers) != expected_start:
        errors.append(
            f"active program must start at PHASE{expected_start:02d}; found first PHASE{min(phase_numbers):02d}"
        )
    if phase_numbers:
        expected = list(range(expected_start, max(phase_numbers) + 1))
        if phase_numbers != expected:
            errors.append(
                f"active phase numbers must be contiguous from PHASE{expected_start:02d}: {phase_numbers}"
            )

    retired_active_patterns = [
        "phase-05-memory-engine.md",
        "phase-06-capability-tool-retrieval.md",
        "phase-07-graphrag-llm-entity-extraction.md",
        "phase-08-langgraph-runtime.md",
        "phase-09-product-trace-eval-closure.md",
    ]
    for name in retired_active_patterns:
        if (programs_root / name).exists():
            errors.append(f"retired active phase file remains in .agent/programs: {name}")

    roadmap = programs_root / "implementation-roadmap.md"
    if roadmap.exists() and "每次新 program 都从 `PHASE01` 开始编号" not in roadmap.read_text(
        encoding="utf-8"
    ):
        errors.append("implementation-roadmap.md must document that new programs start at PHASE01")

    return errors


def _extract_system_yaml_entries(content: str, section: str) -> list[str]:
    entries: list[str] = []
    lines = content.splitlines()
    in_section = False
    for line in lines:
        stripped = line.strip()
        if stripped == f"{section}:":
            in_section = True
            continue
        if in_section and stripped and not line.startswith(" ") and not line.startswith("-"):
            in_section = False
        if in_section and stripped.startswith("- "):
            value = stripped[2:].strip().strip('"').strip("'")
            if value:
                entries.append(value)
    return entries


def _command_path(command: str) -> str | None:
    parts = command.split()
    if not parts:
        return None
    if parts[0] in {"python", "py"} and len(parts) > 1:
        return parts[1]
    if parts[0] == "pytest":
        for part in parts[1:]:
            if not part.startswith("-"):
                return part
    if parts[0].lower() in {"powershell", "pwsh"} and "-File" in parts:
        index = parts.index("-File")
        if index + 1 < len(parts):
            return parts[index + 1]
    return None


def verify_system_yaml(repo_root: Path = REPO_ROOT) -> list[str]:
    system_yaml_path = repo_root / ".agent" / "system.yaml"
    if not system_yaml_path.exists():
        return ["missing .agent/system.yaml"]

    content = system_yaml_path.read_text(encoding="utf-8")
    errors: list[str] = []
    for phrase in [
        'current_program_root: ".agent/programs"',
        'phase_filename_pattern: "PHASE[0-9][0-9]_<name>.md"',
        'new_program_first_phase: "PHASE01"',
    ]:
        if phrase not in content:
            errors.append(f".agent/system.yaml missing program rule: {phrase}")

    for section in ["skills", "templates"]:
        for relative_path in _extract_system_yaml_entries(content, section):
            if relative_path.startswith(".") and not _repo_path(repo_root, relative_path).exists():
                errors.append(f".agent/system.yaml references missing {section[:-1]} path: {relative_path}")

    for command in _extract_system_yaml_entries(content, "verify"):
        path = _command_path(command)
        if path and not _repo_path(repo_root, path).exists():
            errors.append(f".agent/system.yaml references missing verify command path: {path}")

    return errors


def verify_skill_links(repo_root: Path = REPO_ROOT) -> list[str]:
    references_root = repo_root / ".agent" / "references"
    if not references_root.exists():
        return ["missing .agent/references"]

    errors: list[str] = []
    markdown_link = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in sorted(references_root.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        if not content.lstrip().startswith("# "):
            errors.append(f"{path.relative_to(repo_root).as_posix()} must start with a title heading")
        for raw_target in markdown_link.findall(content):
            target = raw_target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(repo_root.resolve())
            except ValueError:
                errors.append(
                    f"{path.relative_to(repo_root).as_posix()} links outside repo: {raw_target}"
                )
                continue
            if not resolved.exists():
                errors.append(
                    f"{path.relative_to(repo_root).as_posix()} links missing path: {raw_target}"
                )
    return errors


TEMPLATE_REQUIRED_SECTIONS = {
    "phase-plan.md": [
        "## 目标",
        "## 范围",
        "## 需要修改的文件",
        "## 禁止修改的文件",
        "## 验收闸门",
        "## 验证命令",
    ],
    "phase-closure-report.md": [
        "## 摘要",
        "## 修改文件",
        "## 关键决策",
        "## 验证结果",
        "## 剩余风险",
        "## Git 同步",
    ],
    "requirement-intake.md": [
        "## 决策",
        "## 自维护检查清单",
        "## 验收闸门",
    ],
    "spec-coding-checklist.md": [
        "## 任务开始前",
        "## 执行前",
        "## 执行中",
        "## 收口前",
        "## 完成标准",
    ],
    "target-mode-prompt.md": [
        "## 规则",
    ],
}


def verify_templates_have_required_sections(repo_root: Path = REPO_ROOT) -> list[str]:
    templates_root = repo_root / ".agent" / "templates"
    if not templates_root.exists():
        return ["missing .agent/templates"]

    errors: list[str] = []
    for name, sections in TEMPLATE_REQUIRED_SECTIONS.items():
        path = templates_root / name
        if not path.exists():
            errors.append(f"missing required template: .agent/templates/{name}")
            continue
        content = path.read_text(encoding="utf-8")
        for section in sections:
            if section not in content:
                errors.append(f".agent/templates/{name} missing required section: {section}")

    readme = templates_root / "README.md"
    if readme.exists():
        readme_text = readme.read_text(encoding="utf-8")
        for phrase in ["templates/", "新增模板必须能被 `.agent/system.yaml` 或 phase 文件引用"]:
            if phrase not in readme_text:
                errors.append(f".agent/templates/README.md missing template boundary: {phrase}")

    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(verify_programs_flat())
    errors.extend(verify_system_yaml())
    errors.extend(verify_skill_links())
    errors.extend(verify_templates_have_required_sections())

    for relative_path in REQUIRED_PATHS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing required Agent system path: {relative_path}")

    for relative_path in FORBIDDEN_PATHS:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"unexpected retired Agent path exists: {relative_path}")

    gitignore = _read(".gitignore")
    if "apps/web/AGENTS.md" in gitignore:
        errors.append(".gitignore must not ignore apps/web/AGENTS.md")
    if ".agent/local/*" not in gitignore:
        errors.append(".gitignore must ignore .agent/local/*")

    agent_entry = _read("AGENTS.md")
    for phrase in [
        "这是仓库唯一的 Agent 入口",
        "## 任务路由",
        "apps/web/AGENTS.md",
        ".agent/references/code-map.md",
        "tools/evals/zuno/AGENTS.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/system.yaml",
        ".agent/programs/",
        "zuno-ideal-architecture-and-repo-layout.html",
        "前台文档默认中文",
        "## 工作模式",
        "### 挂机模式",
        "### 多线程模式",
        "提示词里写“目标模式”不等于 UI 目标模式",
        "粗粒度",
        "用户在 UI 里手动创建目标模式线程",
        "线程内开启多 agent 模式",
        "主线程先盘点可复用 Codex 线程和 git worktree",
        "主线程必须在生成、改写或投递线程提示词之前完成线程盘点",
        "不能先写一堆提示词再回头找线程",
        "不能在主对话里直接粘贴完整子线程提示词",
        "有合适可复用线程就复用；没有合适线程才创建新线程",
        "复用或新建线程后必须改线程标题",
        "子线程目标模式提示词默认要求线程内开启多 agent 模式",
        "Single GeneralAgent",
        "## Program Closure 自维护审查",
        "如果用户提醒“以后注意”，不能只留在对话里",
        "verifier / tests 是否覆盖新规则",
    ]:
        if phrase not in agent_entry:
            errors.append(f"AGENTS.md missing routing phrase: {phrase}")

    html = _read(".agent/architecture/near-term/zuno-ideal-architecture-and-repo-layout.html")
    if "<html" not in html.lower() or "</html>" not in html.lower():
        errors.append("target architecture HTML is not valid HTML")
    for phrase in [
        "Target / Proposed",
        "Summary Compression",
        "Structured Extraction",
        "ToolCard",
        "Native BM25",
        "RRF",
        "auto 是 router",
        "Phase 05",
        "Execution Contract",
        "Query Journey",
        "产品入口层",
        "RAG / GraphRAG 层",
    ]:
        if phrase not in html:
            errors.append(f"target architecture HTML missing canonical phrase: {phrase}")

    for relative_path in [
        "AGENTS.md",
        ".agent/README.md",
        ".agent/architecture/README.md",
        ".agent/architecture/near-term/README.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
    ]:
        if "zuno-ideal-architecture-and-repo-layout.html" not in _read(relative_path):
            errors.append(f"{relative_path} missing target architecture HTML reference")

    agent_readme = _read(".agent/README.md")
    for phrase in [
        ".agent/references/",
        ".agent/programs/",
        ".agent/architecture/",
        "本地 Agent Skill System",
        "新写或重写的 Agent 文档默认使用中文",
        "挂机模式由主线程",
        "多线程模式由主线程",
        "提示词目标模式不等于 Codex UI 目标模式",
        "粗粒度",
        "用户在 UI 里手动创建真正的目标模式子线程",
    ]:
        if phrase not in agent_readme:
            errors.append(f".agent/README.md missing system phrase: {phrase}")

    reference_files = sorted(
        path.name for path in (REPO_ROOT / ".agent/references").iterdir() if path.is_file()
    )
    expected_references = sorted(
        [
            "README.md",
            "current-program.md",
            "docs-map.md",
            "code-map.md",
            "runtime-call-chain.md",
            "verification-map.md",
            "command-catalog.md",
            "known-pitfalls.md",
            "zuno-repo-hygiene.md",
            "task-routing.md",
            "workflow.md",
        ]
    )
    if reference_files != expected_references:
        errors.append(f".agent/references files are not slim canonical set: {reference_files}")

    active_program_files = sorted(
        path.name for path in (REPO_ROOT / ".agent/programs").iterdir() if path.is_file()
    )
    expected_program_files = sorted(
        [
            "README.md",
            "current.md",
            "implementation-roadmap.md",
            "closure-checklist.md",
        ]
    )
    if active_program_files != expected_program_files:
        errors.append(
            f".agent/programs files are not canonical no-active-program set: {active_program_files}"
        )

    roadmap = _read(".agent/programs/implementation-roadmap.md")
    for phrase in [
        "当前没有 active program",
        "每次新 program 都从 `PHASE01` 开始编号",
        "zuno-repo-layout-cleanup-v1",
        "zuno-runtime-architecture-upgrade-v1",
        "zuno-architecture-visuals-v1",
    ]:
        if phrase not in roadmap:
            errors.append(f"active Program 3 roadmap missing phrase: {phrase}")

    phase03 = _read("docs/history/programs/zuno-workflow-doc-system-v1/PHASE03_skill-template-program-system.md")
    for phrase in [
        "本地 skill system",
        "skill / lesson / playbook",
        "queued program",
    ]:
        if phrase not in phase03:
            errors.append(f"archived Program 1 PHASE03 missing skill/template/program phrase: {phrase}")

    archived_program2 = _read("docs/history/programs/zuno-target-architecture-refresh-v1/README.md")
    for phrase in [
        "LLM extraction",
        "知识库支持多套 extractor / config 选择",
        "Memory approval",
    ]:
        if phrase not in archived_program2:
            errors.append(f"archived Program 2 README missing phrase: {phrase}")

    future_program2 = REPO_ROOT / ".agent/architecture/future/programs/zuno-target-architecture-refresh-v1"
    if future_program2.exists():
        errors.append("Program 2 must not remain queued after archive: .agent/architecture/future/programs/zuno-target-architecture-refresh-v1")

    archived_program3 = _read("docs/history/programs/zuno-repo-layout-cleanup-v1/README.md")
    for phrase in [
        "root/docs hygiene",
        "backend 六层迁移计划",
        "repo hygiene verifier",
    ]:
        if phrase not in archived_program3:
            errors.append(f"archived Program 3 README missing phrase: {phrase}")

    for queued_path in sorted((REPO_ROOT / ".agent/architecture/future/programs").glob("*/*.md")):
        content = queued_path.read_text(encoding="utf-8")
        if "queued draft / not active" not in content:
            errors.append(f"queued program file missing not-active banner: {queued_path.relative_to(REPO_ROOT).as_posix()}")

    system_yaml = _read(".agent/system.yaml")
    for phrase in [
        "Zuno Local Agent Skill System",
        "system_identity:",
        "new_program_first_phase: \"PHASE01\"",
        "skill_file_contract:",
        "template_rules:",
        "skill_routes:",
        "docs_sync:",
        "verify:",
        "work_modes:",
        "hangup_mode:",
        "multi_thread_mode:",
        "main_thread_goal_mode: true",
        "persistent_thread_slots: true",
        "task_isolation_unit: \"worktree + codex branch, not thread title\"",
        "main_thread_can_self_execute: true",
        "main_thread_can_delegate: true",
        "child_threads_are_reusable_slots: true",
        "require_fresh_or_confirmed_worktree_branch_per_task: true",
        "prefer_reuse_existing_thread_slots: true",
        "create_new_threads_when_no_reusable_slot: true",
        "rename_thread_after_assignment: true",
        "child_prompt_must_default_multi_agent: true",
        "thread_prompt_root: \".agent/programs/thread-prompts\"",
        "thread_prompts_separate_from_phase_files: true",
        "thread_prompts_replace_on_next_plan: true",
        "cleanup_old_thread_prompts_by_default: true",
        "archive_thread_prompts_only_when_requested: true",
        "temporary_thread_execution_plans_default_cleanup: true",
        "coarse_grained_child_tasks: true",
        "child_threads_allow_multi_agent: true",
        "prompt_only_is_not_goal_mode: true",
        "提示词目标模式不等于 Codex UI 目标模式",
        "require_disjoint_write_scope: true",
        "runtime target remains Single GeneralAgent",
        ".agent/references/workflow.md",
    ]:
        if phrase not in system_yaml:
            errors.append(f".agent/system.yaml missing route phrase: {phrase}")

    workflow_skill = _read(".agent/references/workflow.md")
    for phrase in [
        "挂机模式由主线程作为真正的 Codex UI 目标模式",
        "线程可以常驻",
        "每轮任务必须重新确认或切换独立 worktree 和独立 `codex/` 分支",
        "粗粒度",
        "用户在 UI 里手动创建目标模式线程",
        "提示词目标模式不等于 Codex UI 目标模式",
        "主线程先盘点可复用 Codex 线程和 git worktree",
        "主线程必须在生成、改写或投递线程提示词之前完成线程盘点",
        "主线程不能在主对话里直接粘贴完整子线程提示词",
        "有合适可复用线程就复用；没有合适线程才创建新线程",
        "复用或新建线程后必须改线程标题",
        "子线程目标模式提示词默认要求线程内开启多 agent 模式",
        "不把执行工作流里的多 agent 写成 Zuno runtime 的当前架构",
        "### 挂机模式",
        "### 多线程模式",
        "### Program Closure 自维护审查",
        "如果用户提醒“以后注意”，不能只留在对话里",
        "能机器检查的规则是否已进入脚本或 repo tests",
    ]:
        if phrase not in workflow_skill:
            errors.append(f".agent/references/workflow.md missing parallel workflow phrase: {phrase}")

    closure_checklist = _read(".agent/programs/closure-checklist.md")
    for phrase in [
        "## Program Closure 自维护审查",
        "completed program 是否已归档到 `docs/history/programs/`",
        "如果用户提醒“以后注意”，不能只留在对话里",
        "verifier / tests 是否覆盖新规则",
    ]:
        if phrase not in closure_checklist:
            errors.append(f".agent/programs/closure-checklist.md missing self-review phrase: {phrase}")

    references_readme = _read(".agent/references/README.md")
    for phrase in [
        "本地项目 skill library",
        "skills、lessons、playbooks",
        ".agent/templates/",
        "一次性调查流水账",
    ]:
        if phrase not in references_readme:
            errors.append(f".agent/references/README.md missing skill-system phrase: {phrase}")

    for relative_path in [
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/references/docs-map.md",
        ".agent/references/verification-map.md",
        ".agent/references/known-pitfalls.md",
    ]:
        content = _read(relative_path)
        for section in SKILL_SECTIONS:
            if section not in content:
                errors.append(f"{relative_path} missing local skill section: {section}")

    templates_readme = _read(".agent/templates/README.md")
    for phrase in [
        "只保存 skill 执行模板和报告骨架",
        "不保存项目知识",
        "Forbidden Content",
        "Lessons Learned",
    ]:
        if phrase not in templates_readme:
            errors.append(f".agent/templates/README.md missing template-boundary phrase: {phrase}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Agent system verification failed.")
        return 1

    print("Agent system verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
