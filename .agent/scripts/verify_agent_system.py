from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


REQUIRED_PATHS = [
    "AGENTS.md",
    "apps/web/AGENTS.md",
    "src/backend/zuno/AGENTS.md",
    "tools/evals/zuno/AGENTS.md",
    ".agent/README.md",
    ".agent/system.yaml",
    ".agent/references/README.md",
    ".agent/references/task-routing.md",
    ".agent/references/workflow.md",
    ".agent/references/code-map.md",
    ".agent/references/runtime-call-chain.md",
    ".agent/references/verification-map.md",
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
    ".agent/programs/PHASE01_workflow-doc-audit.md",
    ".agent/programs/PHASE02_agent-bootloader-routing.md",
    ".agent/programs/PHASE03_skill-template-program-system.md",
    ".agent/programs/PHASE04_workflow-verifiers-drift-tests.md",
    ".agent/programs/PHASE05_closure-history-archive.md",
    ".agent/programs/closure-checklist.md",
    ".agent/architecture/future/programs/README.md",
    ".agent/architecture/future/programs/zuno-target-architecture-refresh-v1/implementation-roadmap.md",
    ".agent/architecture/future/programs/zuno-repo-layout-cleanup-v1/implementation-roadmap.md",
    ".agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md",
    ".agent/architecture/future/programs/zuno-architecture-visuals-v1/implementation-roadmap.md",
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
    if directories:
        errors.append(f".agent/programs must be flat; found directories: {directories}")

    phase_files = sorted(
        path.name for path in programs_root.iterdir() if path.is_file() and path.name.startswith("PHASE")
    )
    if not phase_files:
        errors.append(".agent/programs has no PHASE files")
        return errors

    phase_numbers: list[int] = []
    for name in phase_files:
        match = re.fullmatch(r"PHASE(\d{2})_[A-Za-z0-9_-]+\.md", name)
        if not match:
            errors.append(f"active phase filename does not match PHASENN_name.md: {name}")
            continue
        phase_numbers.append(int(match.group(1)))

    if phase_numbers and min(phase_numbers) != 1:
        errors.append(f"active program must start at PHASE01; found first PHASE{min(phase_numbers):02d}")
    if phase_numbers:
        expected = list(range(1, max(phase_numbers) + 1))
        if phase_numbers != expected:
            errors.append(f"active phase numbers must be contiguous from PHASE01: {phase_numbers}")

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
        "src/backend/zuno/AGENTS.md",
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
        "Single GeneralAgent",
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
            "PHASE01_workflow-doc-audit.md",
            "PHASE02_agent-bootloader-routing.md",
            "PHASE03_skill-template-program-system.md",
            "PHASE04_workflow-verifiers-drift-tests.md",
            "PHASE05_closure-history-archive.md",
            "closure-checklist.md",
        ]
    )
    if active_program_files != expected_program_files:
        errors.append(f"active program files are not flat canonical set: {active_program_files}")

    roadmap = _read(".agent/programs/implementation-roadmap.md")
    for phrase in [
        "zuno-workflow-doc-system-v1",
        "PHASE01：工作流与文档系统只读审计",
        "PHASE02：Agent bootloader 与 routing 收口",
        "PHASE03：Skill / Template / Program 系统收口",
        "PHASE04：Workflow verifier 与漂移测试",
        "PHASE05：Program closure 与 history 归档",
        "每次新 program 都从 `PHASE01` 开始编号",
        "zuno-target-architecture-refresh-v1",
        "zuno-repo-layout-cleanup-v1",
        "zuno-runtime-architecture-upgrade-v1",
        "zuno-architecture-visuals-v1",
    ]:
        if phrase not in roadmap:
            errors.append(f"active architecture surface roadmap missing phrase: {phrase}")

    phase03 = _read(".agent/programs/PHASE03_skill-template-program-system.md")
    for phrase in [
        "本地 skill system",
        "skill / lesson / playbook",
        "queued program",
    ]:
        if phrase not in phase03:
            errors.append(f"PHASE03 missing skill/template/program phrase: {phrase}")

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
        "每个线程使用独立 `codex/` 分支",
        "粗粒度",
        "用户在 UI 里手动创建目标模式线程",
        "提示词目标模式不等于 Codex UI 目标模式",
        "不把执行工作流里的多 agent 写成 Zuno runtime 的当前架构",
        "### 挂机模式",
        "### 多线程模式",
    ]:
        if phrase not in workflow_skill:
            errors.append(f".agent/references/workflow.md missing parallel workflow phrase: {phrase}")

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
