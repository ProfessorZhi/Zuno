from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

ACTIVE_PROGRAM_NAME = "zuno-eight-deliverables-full-realization-v1"
ACTIVE_CURRENT_PHASE = "PHASE05_context-builder-memory-system.md"
COMPLETED_PROGRAM_PHASE_FILES = [
    "PHASE01_program-boot-baseline.md",
    "PHASE02_workflow-self-maintenance-system.md",
    "PHASE03_architecture-docs-html-system.md",
    "PHASE04_query-router-mode-policy.md",
]
ACTIVE_PROGRAM_PHASE_FILES = [
    "PHASE01_program-boot-baseline.md",
    "PHASE02_workflow-self-maintenance-system.md",
    "PHASE03_architecture-docs-html-system.md",
    "PHASE04_query-router-mode-policy.md",
    "PHASE05_context-builder-memory-system.md",
    "PHASE06_capability-toolcard-mcp-system.md",
    "PHASE07_hooks-evidence-trace-artifact-system.md",
    "PHASE08_graphrag-knowledge-runtime-system.md",
    "PHASE09_runtime-upgrade-integration.md",
    "PHASE10_validation-release-closure.md",
]

ARCHIVED_PROGRAM_NAMES = [
    "official-graphrag-cleanup-v1",
    "zuno-architecture-surface-cleanup-v1",
    "zuno-repo-layout-cleanup-v1",
    "zuno-six-layer-internalization-v1",
    "zuno-target-architecture-migration-v1",
    "zuno-target-architecture-refresh-v1",
    "zuno-target-runtime-v2",
    "zuno-workflow-doc-system-v1",
]


REQUIRED_PATHS = [
    "AGENTS.md",
    "apps/web/AGENTS.md",
    "tools/evals/zuno/AGENTS.md",
    ".agent/README.md",
    ".agent/system.yaml",
    ".agent/references/README.md",
    ".agent/references/project-map.md",
    ".agent/references/task-routing.md",
    ".agent/references/workflow.md",
    ".agent/references/code-map.md",
    ".agent/references/runtime-call-chain.md",
    ".agent/references/verification-map.md",
    ".agent/references/zuno-repo-hygiene.md",
    ".agent/references/docs-map.md",
    ".agent/references/architecture-docs-map.md",
    ".agent/references/documentation-governance.md",
    ".agent/references/architecture-update-policy.md",
    ".agent/references/diagram-inventory.md",
    ".agent/references/current-target-future-rules.md",
    ".agent/references/workflow-governance.md",
    ".agent/references/workflow-update-policy.md",
    ".agent/references/workflow-requirements.md",
    ".agent/references/workflow-change-log.md",
    ".agent/references/workflow-maintenance-checklist.md",
    ".agent/references/current-program.md",
    ".agent/references/command-catalog.md",
    ".agent/references/known-pitfalls.md",
    ".agent/templates/architecture-doc-template.md",
    ".agent/templates/mermaid-diagram-template.md",
    ".agent/templates/architecture-change-note-template.md",
    ".agent/templates/verification-report-template.md",
    ".agent/templates/workflow-change-note-template.md",
    ".agent/scripts/verify_module_boundaries.py",
    ".agent/architecture/README.md",
    ".agent/architecture/decisions/README.md",
    ".agent/architecture/future/README.md",
    ".agent/architecture/near-term/README.md",
    ".agent/architecture/near-term/00-architecture-index.md",
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
    "docs/history/programs/zuno-six-layer-internalization-v1/README.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/current.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE01_six-layer-current-inventory.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE02_memory-layer-foundation-surfaces.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE03_capability-layer-foundation-surfaces.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE04_knowledge-layer-foundation-surfaces.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE05_agent-runtime-boundary-surfaces.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE06_platform-boundary-hardening.md",
    "docs/history/programs/zuno-six-layer-internalization-v1/PHASE07_docs-verifier-and-closure.md",
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


def _extract_named_route_block(content: str, route_name: str) -> str:
    lines = content.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == f'- name: "{route_name}"':
            start = index
            break
    if start is None:
        return ""

    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith("  - name: "):
            end = index
            break
        if line and not line.startswith(" ") and not line.startswith("-"):
            end = index
            break
    return "\n".join(lines[start:end])


def _extract_route_entries(route_block: str, section: str) -> list[str]:
    entries: list[str] = []
    lines = route_block.splitlines()
    section_indent = None
    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if stripped == f"{section}:":
            section_indent = indent
            continue
        if section_indent is None:
            continue
        if stripped and indent <= section_indent:
            section_indent = None
            continue
        if stripped.startswith("- "):
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
        "## 多 agent 工作组结果",
        "## 自维护审查",
        "## 剩余风险",
        "## PR 信息",
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
    "architecture-doc-template.md": [
        "## Status",
        "## Purpose",
        "## Scope",
        "## Related Code",
        "## Related Tests",
        "## Related Diagrams",
        "## Current Behavior",
        "## Target Design",
        "## Open Questions",
        "## Validation",
    ],
    "mermaid-diagram-template.md": [
        "## Diagram Name",
        "## Diagram Type",
        "## Source of Truth",
        "## Mermaid Block",
        "## Explanation",
        "## Update Triggers",
        "## Validation",
    ],
    "architecture-change-note-template.md": [
        "## Change Summary",
        "## Affected Areas",
        "## Docs Updated",
        "## Diagrams Updated",
        "## Validation",
        "## Remaining Gaps",
    ],
    "verification-report-template.md": [
        "## Scope",
        "## Commands",
        "## Results",
        "## Failure Analysis",
        "## Evidence",
        "## Remaining Risk",
    ],
    "workflow-change-note-template.md": [
        "## Change Summary",
        "## Trigger",
        "## Requirement Type",
        "## Affected Workflow Files",
        "## Affected Human Docs",
        "## Templates Updated",
        "## Validation",
        "## Remaining Gaps",
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


def verify_workflow_rule_writeback_route(repo_root: Path = REPO_ROOT) -> list[str]:
    system_yaml = (repo_root / ".agent" / "system.yaml").read_text(encoding="utf-8")
    route_block = _extract_named_route_block(system_yaml, "docs-agent-system-history")
    if not route_block:
        return ['.agent/system.yaml missing route: docs-agent-system-history']

    errors: list[str] = []
    required_by_section = {
        "skills": [
            ".agent/references/workflow.md",
            ".agent/references/workflow-governance.md",
            ".agent/references/workflow-update-policy.md",
            ".agent/references/workflow-requirements.md",
            ".agent/references/workflow-change-log.md",
            ".agent/references/workflow-maintenance-checklist.md",
            ".agent/references/verification-map.md",
        ],
        "templates": [
            ".agent/templates/requirement-intake.md",
            ".agent/templates/phase-plan.md",
            ".agent/templates/phase-closure-report.md",
            ".agent/templates/verification-report-template.md",
            ".agent/templates/workflow-change-note-template.md",
        ],
        "docs_sync": [
            "AGENTS.md",
            ".agent/system.yaml",
            ".agent/references/workflow.md",
            ".agent/references/workflow-update-policy.md",
            ".agent/references/workflow-requirements.md",
            ".agent/references/workflow-change-log.md",
            ".agent/references/workflow-maintenance-checklist.md",
            ".agent/templates/README.md",
            ".agent/templates/verification-report-template.md",
            ".agent/programs/current.md",
            ".agent/programs/implementation-roadmap.md",
            ".agent/programs/closure-checklist.md",
            "docs/architecture/roadmap.md",
        ],
        "verify": [
            "git diff --check",
            "python tools/scripts/verify_repo_structure.py",
            "python .agent/scripts/verify_agent_system.py",
            "python .agent/scripts/verify_doc_boundaries.py",
            "powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1",
            "pytest -q tests/repo/test_agent_system.py -p no:cacheprovider",
        ],
    }
    for section, required_values in required_by_section.items():
        entries = _extract_route_entries(route_block, section)
        for value in required_values:
            if value not in entries:
                errors.append(f"docs-agent-system-history route missing {section} entry: {value}")

    for section in ["skills", "templates", "docs_sync"]:
        for relative_path in _extract_route_entries(route_block, section):
            if "*" in relative_path:
                continue
            if not _repo_path(repo_root, relative_path).exists():
                errors.append(
                    f"docs-agent-system-history route references missing {section} path: {relative_path}"
                )

    for command in _extract_route_entries(route_block, "verify"):
        path = _command_path(command)
        if path and not _repo_path(repo_root, path).exists():
            errors.append(
                f"docs-agent-system-history route references missing verify command path: {path}"
            )

    return errors


def verify_templates_are_skeletons(repo_root: Path = REPO_ROOT) -> list[str]:
    templates_root = repo_root / ".agent" / "templates"
    if not templates_root.exists():
        return ["missing .agent/templates"]

    errors: list[str] = []
    system_yaml = _read(".agent/system.yaml")
    phase_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted((repo_root / ".agent" / "programs").glob("PHASE*.md"))
    )
    route_reference_text = system_yaml + "\n" + phase_text
    forbidden_markers = [
        "C:\\",
        "F:\\",
        ACTIVE_PROGRAM_NAME,
        "state: active",
        "current_phase",
        "GeneralAgent",
        "Domain Pack",
        "src/backend/zuno",
        "## Current Truth",
        "## Debug Playbooks",
        "## Lessons Learned",
    ]

    for path in sorted(templates_root.glob("*.md")):
        if path.name == "README.md":
            continue
        content = path.read_text(encoding="utf-8")
        for marker in forbidden_markers:
            if marker in content:
                errors.append(
                    f".agent/templates/{path.name} contains project truth marker, not skeleton content: {marker}"
                )
        if path.name not in route_reference_text:
            errors.append(
                f".agent/templates/{path.name} must be referenced by .agent/system.yaml or active phase files"
            )

    return errors


def verify_program_lifecycle_surfaces(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    surfaces = {
        ".agent/programs/current.md": [ACTIVE_PROGRAM_NAME, "state: active", ACTIVE_CURRENT_PHASE],
        ".agent/references/current-program.md": [
            ACTIVE_PROGRAM_NAME,
            "state: active",
            ACTIVE_CURRENT_PHASE,
        ],
        ".agent/programs/implementation-roadmap.md": [ACTIVE_PROGRAM_NAME, "state: active"],
        "docs/architecture/roadmap.md": [ACTIVE_PROGRAM_NAME, "active"],
        "AGENTS.md": [ACTIVE_PROGRAM_NAME, ".agent/programs/"],
    }
    for relative_path, phrases in surfaces.items():
        content = _read(relative_path)
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"{relative_path} missing program lifecycle phrase: {phrase}")

    for phase_name in COMPLETED_PROGRAM_PHASE_FILES:
        content = _read(f".agent/programs/{phase_name}")
        if "status: completed" not in content:
            errors.append(f"{phase_name} must be completed in active lifecycle")

    current_phase = _read(f".agent/programs/{ACTIVE_CURRENT_PHASE}")
    if "status: active" not in current_phase:
        errors.append(f"{ACTIVE_CURRENT_PHASE} must be active in active lifecycle")

    active_programs_root = repo_root / ".agent" / "programs"
    for program_name in ARCHIVED_PROGRAM_NAMES:
        history_path = repo_root / "docs" / "history" / "programs" / program_name
        if not history_path.exists():
            errors.append(f"archived program missing history directory: {program_name}")
        if (active_programs_root / program_name).exists():
            errors.append(f"archived program must not remain in .agent/programs: {program_name}")

    return errors


def verify_workflow_change_log_entries(repo_root: Path = REPO_ROOT) -> list[str]:
    content = _read(".agent/references/workflow-change-log.md")
    heading_pattern = re.compile(r"^### \d{4}-\d{2}-\d{2}: .+$", re.MULTILINE)
    matches = list(heading_pattern.finditer(content))
    if not matches:
        return [".agent/references/workflow-change-log.md must contain dated change log entries"]

    errors: list[str] = []
    required_labels = ["Summary:", "Reason:", "Affected files:", "Status:", "Validation:"]
    for index, match in enumerate(matches):
        entry_start = match.end()
        entry_end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        entry = content[entry_start:entry_end]
        heading = match.group(0)
        for label in required_labels:
            if label not in entry:
                errors.append(f"{heading} missing workflow change log label: {label}")

        affected_match = re.search(
            r"Affected files:\s*(?P<body>.*?)(?:\nStatus:|\nValidation:|\n### |\n## |\Z)",
            entry,
            re.DOTALL,
        )
        if not affected_match:
            errors.append(f"{heading} missing affected file list")
            continue
        affected_paths = re.findall(r"`([^`]+)`", affected_match.group("body"))
        if not affected_paths:
            errors.append(f"{heading} affected file list must use backticked repo paths")
            continue
        for affected_path in affected_paths:
            if "*" in affected_path:
                continue
            if not _repo_path(repo_root, affected_path).exists():
                errors.append(f"{heading} references missing affected file: {affected_path}")

    return errors


def main() -> int:
    errors: list[str] = []
    errors.extend(verify_programs_flat())
    errors.extend(verify_system_yaml())
    errors.extend(verify_skill_links())
    errors.extend(verify_templates_have_required_sections())
    errors.extend(verify_workflow_rule_writeback_route())
    errors.extend(verify_templates_are_skeletons())
    errors.extend(verify_program_lifecycle_surfaces())
    errors.extend(verify_workflow_change_log_entries())

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
        ".agent/references/architecture-docs-map.md",
        ".agent/references/workflow-governance.md",
        ".agent/system.yaml",
        ".agent/programs/",
        "00-architecture-index.md",
        "前台文档默认中文",
        "Architecture Documentation Governance",
        "Agent Workflow Self-Maintenance",
        "八大交付物",
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

    index = _read(".agent/architecture/near-term/00-architecture-index.md")
    for phrase in [
        "目标架构设计工作集索引",
        "Summary Compression",
        "Structured Extraction",
        "ToolCard",
        "Native BM25",
        "RRF",
        "docs/architecture.md",
        "docs/architecture.html",
        "00-architecture-index.md",
    ]:
        if phrase not in index:
            errors.append(f"near-term architecture index missing canonical phrase: {phrase}")

    for relative_path in [
        "AGENTS.md",
        ".agent/README.md",
        ".agent/architecture/README.md",
        ".agent/architecture/near-term/README.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
    ]:
        content = _read(relative_path)
        if "00-architecture-index.md" not in content:
            errors.append(f"{relative_path} missing near-term architecture index reference")
        if "zuno-ideal-architecture-and-repo-layout.html" in content:
            errors.append(f"{relative_path} still references retired target architecture HTML")

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
            "project-map.md",
            "current-program.md",
            "docs-map.md",
            "architecture-docs-map.md",
            "documentation-governance.md",
            "architecture-update-policy.md",
            "diagram-inventory.md",
            "current-target-future-rules.md",
            "workflow-governance.md",
            "workflow-update-policy.md",
            "workflow-requirements.md",
            "workflow-change-log.md",
            "workflow-maintenance-checklist.md",
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
            *ACTIVE_PROGRAM_PHASE_FILES,
        ]
    )
    if active_program_files != expected_program_files:
        errors.append(
            f".agent/programs files do not match active program set: {active_program_files}"
        )
    current_program_text = _read(".agent/programs/current.md")
    for phrase in [
        ACTIVE_PROGRAM_NAME,
        "state: active",
        ACTIVE_CURRENT_PHASE,
        "八个交付物",
        "默认开启线程内多 agent",
        "Codex 执行协作",
        "不是 Zuno runtime 架构",
        "不是多线程模式",
    ]:
        if phrase not in current_program_text:
            errors.append(f".agent/programs/current.md missing active program phrase: {phrase}")
    for phase_name in COMPLETED_PROGRAM_PHASE_FILES:
        phase_text = _read(f".agent/programs/{phase_name}")
        if "status: completed" not in phase_text:
            errors.append(f"{phase_name} must be marked completed before current phase advances")
    current_phase_text = _read(f".agent/programs/{ACTIVE_CURRENT_PHASE}")
    if "status: active" not in current_phase_text:
        errors.append(f"{ACTIVE_CURRENT_PHASE} must be marked active")
    for phase_name in ACTIVE_PROGRAM_PHASE_FILES:
        if phase_name == ACTIVE_CURRENT_PHASE or phase_name in COMPLETED_PROGRAM_PHASE_FILES:
            continue
        phase_text = _read(f".agent/programs/{phase_name}")
        if "status: planned" not in phase_text:
            errors.append(f"{phase_name} must remain planned until it is current")
    for relative_path in [
        ".agent/programs/current.md",
        ".agent/references/current-program.md",
        "docs/architecture/roadmap.md",
    ]:
        content = _read(relative_path)
        for phrase in ["Codex 执行协作", "不是 Zuno runtime 架构"]:
            if phrase not in content:
                errors.append(f"{relative_path} missing Codex execution boundary phrase: {phrase}")

    roadmap = _read(".agent/programs/implementation-roadmap.md")
    for phrase in [
        ACTIVE_PROGRAM_NAME,
        "state: active",
        "zuno-six-layer-internalization-v1",
        "每次新 program 都从 `PHASE01` 开始编号",
        "zuno-repo-layout-cleanup-v1",
        "zuno-runtime-architecture-upgrade-v1",
        "zuno-architecture-visuals-v1",
    ]:
        if phrase not in roadmap:
            errors.append(f"program roadmap missing phrase: {phrase}")

    future_programs_readme = _read(".agent/architecture/future/programs/README.md")
    for phrase in [
        ACTIVE_PROGRAM_NAME,
        "吸收为参考输入",
        "不是 active 执行入口",
        "zuno-six-layer-internalization-v1",
    ]:
        if phrase not in future_programs_readme:
            errors.append(f"future programs README missing active program boundary phrase: {phrase}")
    if "当前没有 active program" in future_programs_readme:
        errors.append("future programs README must not claim there is no active program")

    repo_hygiene = _read(".agent/references/zuno-repo-hygiene.md")
    for phrase in [
        "zuno-six-layer-internalization-v1",
        ACTIVE_PROGRAM_NAME,
        "runtime architecture upgrade",
        "不是当前独立 queued program",
    ]:
        if phrase not in repo_hygiene:
            errors.append(f"zuno-repo-hygiene.md missing current Program 4 boundary phrase: {phrase}")
    if "Program 4 runtime architecture upgrade 保持 queued / not active" in repo_hygiene:
        errors.append("zuno-repo-hygiene.md keeps stale Program 4 queued runtime-upgrade wording")

    archived_program4 = _read("docs/history/programs/zuno-six-layer-internalization-v1/README.md")
    for phrase in [
        "completed / archived",
        "Capability tools 不按 CLI / API 拆成两棵顶层目录",
        "PHASE01-07",
    ]:
        if phrase not in archived_program4:
            errors.append(f"archived Program 4 README missing phrase: {phrase}")

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
        ".agent/references/architecture-docs-map.md",
        ".agent/references/workflow-governance.md",
        ".agent/templates/workflow-change-note-template.md",
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
        "Architecture Documentation Governance",
        "Agent Workflow Self-Maintenance",
        "八大交付物",
    ]:
        if phrase not in references_readme:
            errors.append(f".agent/references/README.md missing skill-system phrase: {phrase}")

    for relative_path in [
        ".agent/references/project-map.md",
        ".agent/references/task-routing.md",
        ".agent/references/workflow.md",
        ".agent/references/docs-map.md",
        ".agent/references/architecture-docs-map.md",
        ".agent/references/documentation-governance.md",
        ".agent/references/architecture-update-policy.md",
        ".agent/references/diagram-inventory.md",
        ".agent/references/current-target-future-rules.md",
        ".agent/references/workflow-governance.md",
        ".agent/references/workflow-update-policy.md",
        ".agent/references/workflow-requirements.md",
        ".agent/references/workflow-change-log.md",
        ".agent/references/workflow-maintenance-checklist.md",
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
        "architecture-doc-template.md",
        "workflow-change-note-template.md",
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
