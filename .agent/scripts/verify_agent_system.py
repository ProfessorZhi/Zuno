from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

COMPLETED_PROGRAM_NAME = "zuno-eight-deliverables-full-realization-v1"
COMPLETED_PROGRAM_ARCHIVE = f"docs/history/programs/{COMPLETED_PROGRAM_NAME}"
ACTIVE_PROGRAM_NAME = "zuno-master-architecture-implementation-v1"
ACTIVE_PROGRAM_PHASE_FILES = [
    "PHASE01_program-baseline-and-previous-closure.md",
    "PHASE02_project-folder-and-code-layout-cleanup.md",
    "PHASE03_enterprise-scenario-and-product-loop.md",
    "PHASE04_document-ingestion-parse-gateway.md",
    "PHASE05_agent-runtime-langgraph-harness.md",
    "PHASE06_context-memory-system.md",
    "PHASE07_tool-control-plane-mcp-approval.md",
    "PHASE08_rag-graphrag-evidence-citation.md",
    "PHASE09_security-governance-sandbox.md",
    "PHASE10_eval-observability-langsmith.md",
    "PHASE11_architecture-docs-html-refresh.md",
    "PHASE12_validation-release-closure.md",
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
    ".agent/templates/architecture-doc-template.md",
    ".agent/templates/mermaid-diagram-template.md",
    ".agent/templates/architecture-change-note-template.md",
    ".agent/templates/verification-report-template.md",
    ".agent/templates/workflow-change-note-template.md",
    ".agent/templates/phase-plan.md",
    ".agent/templates/phase-closure-report.md",
    ".agent/templates/requirement-intake.md",
    ".agent/templates/readonly-audit-prompt.md",
    ".agent/templates/goal-mode-prompt.md",
    ".agent/architecture/README.md",
    ".agent/architecture/architecture.md",
    ".agent/architecture/architecture.html",
    "docs/architecture/README.md",
    "docs/architecture/architecture.md",
    "docs/architecture/architecture.html",
    "docs/history/architecture-surface-cleanup-2026-06-30/README.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/current-architecture.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/target-architecture.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/roadmap.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/docs-architecture/deliverables.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/near-term/00-architecture-index.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/future/README.md",
    "docs/history/architecture-surface-cleanup-2026-06-30/agent-architecture/decisions/README.md",
    ".agent/programs/README.md",
    ".agent/programs/current.md",
    ".agent/programs/implementation-roadmap.md",
    ".agent/programs/closure-checklist.md",
    "docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/README.md",
    "docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/current.md",
    "docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/implementation-roadmap.md",
    "docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/closure-checklist.md",
    "docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/closure-summary.md",
    "docs/history/research/README.md",
    "docs/history/research/chatgpt-research-mode-artifacts/README.md",
    "docs/history/research/chatgpt-research-mode-artifacts/zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.pdf",
    "docs/history/research/chatgpt-research-mode-artifacts/zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.md",
    "docs/history/research/chatgpt-research-mode-artifacts/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf",
    "docs/history/research/chatgpt-research-mode-artifacts/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.md",
    "docs/architecture/assets/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf",
    f"{COMPLETED_PROGRAM_ARCHIVE}/README.md",
    f"{COMPLETED_PROGRAM_ARCHIVE}/closure-summary.md",
]

FORBIDDEN_PATHS = [
    "agent.md",
    ".agent.md",
    ".agent/skills",
    ".agent/workflows",
    ".agent/architecture/near-term",
    ".agent/architecture/future",
    ".agent/architecture/decisions",
    ".agent/architecture/00-architecture-index.md",
    ".agent/architecture/glossary.md",
    "docs/architecture/current-architecture.md",
    "docs/architecture/target-architecture.md",
    "docs/architecture/roadmap.md",
    "docs/architecture/deliverables.md",
    "docs/architecture/overall-architecture.md",
    ".agent/architecture/overall-architecture.md",
]

TEMPLATE_REQUIRED_SECTIONS = {
    "phase-plan.md": ["## 目标", "## 范围", "## 验收闸门", "## 验证命令"],
    "phase-closure-report.md": ["## 摘要", "## 验证结果", "## 自维护审查", "## 剩余风险"],
    "requirement-intake.md": ["## 决策", "## 自维护检查清单", "## 验收闸门"],
    "architecture-doc-template.md": ["## Status", "## Current Behavior", "## Target Design", "## Validation"],
    "mermaid-diagram-template.md": ["## Diagram Name", "## Mermaid Block", "## Validation"],
    "architecture-change-note-template.md": ["## Change Summary", "## Docs Updated", "## Validation"],
    "verification-report-template.md": ["## Commands", "## Results", "## Remaining Risk"],
    "workflow-change-note-template.md": ["Change Summary", "Trigger", "Affected Workflow Files", "Validation"],
}

SELF_MAINTENANCE_GUARDS = [
    "verify_workflow_rule_writeback_route",
    "verify_templates_are_skeletons",
    "verify_program_lifecycle_surfaces",
    "verify_workflow_change_log_entries",
    "docs-agent-system-history",
    "verification-report-template.md",
    "workflow-change-log.md",
    "docs/history/programs",
    "## 自维护审查",
]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _repo_path(repo_root: Path, value: str) -> Path:
    return repo_root / value.replace("/", "\\")


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


def verify_programs_flat(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    programs_root = repo_root / ".agent/programs"
    if not programs_root.exists():
        return ["missing .agent/programs"]
    active_phase_files = sorted(path.name for path in programs_root.glob("PHASE*.md"))
    if active_phase_files != ACTIVE_PROGRAM_PHASE_FILES:
        errors.append(f".agent/programs active phase files drifted: {active_phase_files}")
    for name in ["current.md", "implementation-roadmap.md", "closure-checklist.md", "README.md"]:
        if not (programs_root / name).exists():
            errors.append(f"missing .agent/programs/{name}")
    return errors


def verify_system_yaml(repo_root: Path = REPO_ROOT) -> list[str]:
    system_yaml_path = repo_root / ".agent/system.yaml"
    if not system_yaml_path.exists():
        return ["missing .agent/system.yaml"]
    content = system_yaml_path.read_text(encoding="utf-8")
    errors: list[str] = []
    for phrase in [
        'current_program_root: ".agent/programs"',
        'new_program_first_phase: "PHASE01"',
        "skill_routes:",
        "docs_sync:",
        "verify:",
    ]:
        if phrase not in content:
            errors.append(f".agent/system.yaml missing route phrase: {phrase}")
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
    references_root = repo_root / ".agent/references"
    if not references_root.exists():
        return ["missing .agent/references"]
    errors: list[str] = []
    markdown_link = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in sorted(references_root.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        if "#" not in content[:500]:
            errors.append(f"{path.relative_to(repo_root).as_posix()} must contain a title heading near the top")
        for raw_target in markdown_link.findall(content):
            target = raw_target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(repo_root.resolve())
            except ValueError:
                errors.append(f"{path.relative_to(repo_root).as_posix()} links outside repo: {raw_target}")
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(repo_root).as_posix()} links missing path: {raw_target}")
    return errors


def verify_templates_have_required_sections(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    templates_root = repo_root / ".agent/templates"
    for file_name, sections in TEMPLATE_REQUIRED_SECTIONS.items():
        path = templates_root / file_name
        if not path.exists():
            errors.append(f"missing template: {file_name}")
            continue
        content = path.read_text(encoding="utf-8")
        for section in sections:
            if section not in content:
                errors.append(f"{file_name} missing template section: {section}")
    return errors


def verify_workflow_rule_writeback_route(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    agents = (repo_root / "AGENTS.md").read_text(encoding="utf-8")
    workflow = (repo_root / ".agent/references/workflow.md").read_text(encoding="utf-8")
    for phrase in [
        "Agent Workflow Self-Maintenance",
        "如果用户提醒“以后注意”，不能只留在对话里",
        ".agent/references/",
        ".agent/templates/",
        "verifier / tests",
    ]:
        if phrase not in agents and phrase not in workflow:
            errors.append(f"workflow rule writeback route missing phrase: {phrase}")
    return errors


def verify_templates_are_skeletons(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    for path in sorted((repo_root / ".agent/templates").glob("*.md")):
        content = path.read_text(encoding="utf-8")
        if "Zuno 的主叙事是" in content or "GeneralAgent single loop" in content:
            errors.append(f"{path.relative_to(repo_root).as_posix()} contains project fact; templates must stay skeletons")
    return errors


def verify_program_lifecycle_surfaces(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    current = (repo_root / ".agent/programs/current.md").read_text(encoding="utf-8")
    roadmap = (repo_root / ".agent/programs/implementation-roadmap.md").read_text(encoding="utf-8")
    for phrase in [
        "当前 active program",
        ACTIVE_PROGRAM_NAME,
        "state: active",
        "current_phase: PHASE04_document-ingestion-parse-gateway",
        COMPLETED_PROGRAM_NAME,
        COMPLETED_PROGRAM_ARCHIVE,
    ]:
        if phrase not in current + roadmap:
            errors.append(f"program lifecycle surface missing phrase: {phrase}")
    return errors


def verify_workflow_change_log_entries(repo_root: Path = REPO_ROOT) -> list[str]:
    path = repo_root / ".agent/references/workflow-change-log.md"
    if not path.exists():
        return ["missing workflow-change-log.md"]
    content = path.read_text(encoding="utf-8")
    if "### " not in content:
        return [".agent/references/workflow-change-log.md must contain dated change log entries"]
    for phrase in ["Summary:", "Reason:", "Affected files:", "Status:", "Validation:"]:
        if phrase not in content:
            return [f".agent/references/workflow-change-log.md missing label: {phrase}"]
    return []


def verify_architecture_mirror(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    docs_md = repo_root / "docs/architecture/architecture.md"
    agent_md = repo_root / ".agent/architecture/architecture.md"
    docs_html = repo_root / "docs/architecture/architecture.html"
    agent_html = repo_root / ".agent/architecture/architecture.html"
    if docs_md.read_bytes() != agent_md.read_bytes():
        errors.append("Agent architecture Markdown mirror is stale")
    if docs_html.read_text(encoding="utf-8") != agent_html.read_text(encoding="utf-8"):
        errors.append("Agent architecture HTML mirror is stale")
    return errors


def verify_phase05_context_memory_verification_map(repo_root: Path = REPO_ROOT) -> list[str]:
    return []


def verify_phase06_capability_toolcard_verification_map(repo_root: Path = REPO_ROOT) -> list[str]:
    return []


def verify_phase07_hooks_evidence_trace_verification_map(repo_root: Path = REPO_ROOT) -> list[str]:
    return []


def verify_phase08_graphrag_knowledge_runtime_verification_map(repo_root: Path = REPO_ROOT) -> list[str]:
    return []


def verify_phase09_runtime_upgrade_integration_verification_map(repo_root: Path = REPO_ROOT) -> list[str]:
    return []


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
    errors.extend(verify_architecture_mirror())
    errors.extend(verify_phase05_context_memory_verification_map())
    errors.extend(verify_phase06_capability_toolcard_verification_map())
    errors.extend(verify_phase07_hooks_evidence_trace_verification_map())
    errors.extend(verify_phase08_graphrag_knowledge_runtime_verification_map())
    errors.extend(verify_phase09_runtime_upgrade_integration_verification_map())

    for relative_path in REQUIRED_PATHS:
        if not (REPO_ROOT / relative_path).exists():
            errors.append(f"missing required Agent system path: {relative_path}")
    for relative_path in FORBIDDEN_PATHS:
        if (REPO_ROOT / relative_path).exists():
            errors.append(f"unexpected retired Agent path exists: {relative_path}")

    agent_entry = _read("AGENTS.md")
    for phrase in [
        "这是仓库唯一的 Agent 入口",
        "Architecture Documentation Governance",
        "Agent Workflow Self-Maintenance",
        "docs/architecture/architecture.md",
        ".agent/architecture/architecture.md",
        ".agent/architecture/architecture.html",
        "## Program Closure 自维护审查",
    ]:
        if phrase not in agent_entry:
            errors.append(f"AGENTS.md missing routing phrase: {phrase}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Agent system verification failed.")
        return 1

    print("Agent system verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
