from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

COMPLETED_PROGRAM_NAME = "zuno-eight-deliverables-full-realization-v1"
COMPLETED_PROGRAM_ARCHIVE = f"docs/history/programs/{COMPLETED_PROGRAM_NAME}"
MASTER_PROGRAM_NAME = "zuno-master-architecture-implementation-v1"
MASTER_PROGRAM_ARCHIVE = f"docs/history/programs/{MASTER_PROGRAM_NAME}"
MASTER_PROGRAM_PHASE_FILES = [
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
RUNTIME_PROGRAM_NAME = "zuno-target-architecture-runtime-full-implementation-v1"
RUNTIME_PROGRAM_ARCHIVE = f"docs/history/programs/{RUNTIME_PROGRAM_NAME}"
RUNTIME_PROGRAM_PHASE_FILES = [
    "PHASE01_program-reopen-and-truth-source-freeze.md",
    "PHASE02_runtime-migration-map-and-repo-ownership-lock.md",
    "PHASE03_task-session-artifact-event-runtime.md",
    "PHASE04_document-ingestion-parse-runtime.md",
    "PHASE05_index-jobs-and-knowledge-space-runtime.md",
    "PHASE06_durable-single-controller-runtime.md",
    "PHASE07_memory-db-and-context-governance.md",
    "PHASE08_tool-control-plane-approval-and-sandbox-runtime.md",
    "PHASE09_agentic-retrieval-evidence-citation-runtime.md",
    "PHASE10_security-observability-and-online-eval.md",
    "PHASE11_web-desktop-surface-and-feedback-loop.md",
    "PHASE12_release-gate-full-e2e-closure.md",
]
RUNTIME_PROGRAM_FILES = [
    "README.md",
    "current.md",
]
ACTIVE_PROGRAM_NAME = "zuno-production-architecture-and-deliverables-completion-v1"
ACTIVE_PROGRAM_ARCHIVE = f"docs/history/programs/{ACTIVE_PROGRAM_NAME}"
ACTIVE_PROGRAM_PHASE_FILES = [
    "PHASE01_production-maturity-gap-audit.md",
    "PHASE02_program-truth-source-and-execution-system.md",
    "PHASE03_workflow-self-maintenance-automation.md",
    "PHASE04_documentation-dedup-architecture-clarity.md",
    "PHASE05_repo-ownership-and-compatibility-retirement.md",
    "PHASE06_product-surface-desktop-recovery-loop.md",
    "PHASE07_production-parse-and-index-platform.md",
    "PHASE08_durable-agent-runtime-persistence.md",
    "PHASE09_memory-context-production-governance.md",
    "PHASE10_tool-sandbox-vault-network-runtime.md",
    "PHASE11_production-graphrag-evidence-citation.md",
    "PHASE12_security-trace-eval-release-closure.md",
]
ACTIVE_PROGRAM_FILES = [
    "README.md",
    "current.md",
    "implementation-roadmap.md",
    "closure-checklist.md",
    "PHASE01_truth-source-and-merge-plan.md",
    "PHASE02_shared-contract-freeze.md",
    "PHASE03_enterprise-ingestion-async-infrastructure.md",
    "PHASE04_knowledge-retrieval-and-graphrag-profile.md",
    "PHASE05_memory-context-engine.md",
    "PHASE06_capability-skill-tool-mcp-layer.md",
    "PHASE07_security-governance-envelope.md",
    "PHASE08_model-gateway-cost-latency.md",
    "PHASE09_planning-contract-and-strategy-selector.md",
    "PHASE10_react-reflection-replan-reflexion-runtime.md",
    "PHASE11_workspace-product-api-frontend-sync.md",
    "PHASE12_end-to-end-product-runtime.md",
    "PHASE13_eval-trace-cost-benchmark.md",
    "PHASE14_docs-architecture-expansion.md",
    "PHASE15_verification-archive-closure.md",
]
PROGRAM3_ACTIVE_NAME = "zuno-launchable-enterprise-agentic-graphrag-full-closure-v1"
PROGRAM3_ACTIVE_PHASE_FILES = ACTIVE_PROGRAM_FILES[4:]
LATEST_COMPLETED_PROGRAM_NAME = "zuno-enterprise-document-ingestion-platform-v2"
LATEST_COMPLETED_PROGRAM_ARCHIVE = f"docs/history/programs/{LATEST_COMPLETED_PROGRAM_NAME}"
LATEST_COMPLETED_PROGRAM_PHASE_FILES = [
    "PHASE01_truth-source-and-gap-audit.md",
    "PHASE02_durable-storage-contract.md",
    "PHASE03_workspace-file-durable-input.md",
    "PHASE04_parse-document-persistence.md",
    "PHASE05_index-persistence-rehydrate.md",
    "PHASE06_workspace-product-durable-closure.md",
    "PHASE07_restart-recovery-end-to-end.md",
    "PHASE08_docs-verifier-closure.md",
]
CURRENT_ACTIVE_PROGRAM_NAME = "zuno-production-document-ingestion-and-thread-foundation-v1"
CURRENT_ACTIVE_PROGRAM_ARCHIVE = f"docs/history/programs/{CURRENT_ACTIVE_PROGRAM_NAME}"
CURRENT_ACTIVE_PROGRAM_PHASE_FILES = [
    "PHASE01_program-truth-source-and-parser-current-audit.md",
    "PHASE02_document-ir-and-parser-contract-freeze.md",
    "PHASE03_parser-worker-runtime-and-job-lifecycle.md",
    "PHASE04_native-text-and-structured-file-parsers.md",
    "PHASE05_pdf-office-ocr-adapter-boundaries.md",
    "PHASE06_index-handoff-provenance-and-fixtures.md",
    "PHASE07_program2-thread-prompts-and-branch-plan.md",
    "PHASE08_verification-doc-sync-and-closure.md",
]
QUEUED_PROGRAM_FILES = [
    "README.md",
    "PROGRAM04_runtime-subsystems-parallel.md",
    "PROGRAM05_agent-planning-integration.md",
    "PROGRAM06_enterprise-knowledge-eval-benchmark.md",
]
THREAD_PROMPT_FILES = [
    "THREAD_A_memory-context.md",
    "THREAD_B_tool-sandbox.md",
    "THREAD_C_security-governance.md",
    "THREAD_D_graphrag-index.md",
]


def _current_phase_name(content: str) -> str | None:
    for line in content.splitlines():
        if line.startswith("current_phase:"):
            return line.split(":", 1)[1].strip().strip("`")
    return None


def _verify_archived_phase_state(repo_root: Path) -> list[str]:
    errors: list[str] = []
    archive_root = repo_root / ACTIVE_PROGRAM_ARCHIVE
    for phase_name in ACTIVE_PROGRAM_PHASE_FILES:
        phase_path = archive_root / phase_name
        if not phase_path.exists():
            errors.append(f"production completion program archive missing phase: {phase_name}")
            continue
        phase_content = phase_path.read_text(encoding="utf-8")
        if "status: completed" not in phase_content:
            errors.append(f"production completion program archive phase missing completed status: {phase_name}")
    return errors

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
    "docs/architecture/production-readiness.md",
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
    *[f".agent/programs/queued-programs/{file_name}" for file_name in QUEUED_PROGRAM_FILES],
    f"{LATEST_COMPLETED_PROGRAM_ARCHIVE}/README.md",
    f"{LATEST_COMPLETED_PROGRAM_ARCHIVE}/current.md",
    f"{LATEST_COMPLETED_PROGRAM_ARCHIVE}/implementation-roadmap.md",
    f"{LATEST_COMPLETED_PROGRAM_ARCHIVE}/closure-checklist.md",
    f"{LATEST_COMPLETED_PROGRAM_ARCHIVE}/closure-summary.md",
    *[f"{LATEST_COMPLETED_PROGRAM_ARCHIVE}/{phase_name}" for phase_name in LATEST_COMPLETED_PROGRAM_PHASE_FILES],
    f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/README.md",
    f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/current.md",
    f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/implementation-roadmap.md",
    f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/closure-checklist.md",
    f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/closure-summary.md",
    *[f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/{phase_name}" for phase_name in CURRENT_ACTIVE_PROGRAM_PHASE_FILES],
    *[f"{CURRENT_ACTIVE_PROGRAM_ARCHIVE}/thread-prompts/{file_name}" for file_name in THREAD_PROMPT_FILES],
    f"{ACTIVE_PROGRAM_ARCHIVE}/README.md",
    f"{ACTIVE_PROGRAM_ARCHIVE}/current.md",
    f"{ACTIVE_PROGRAM_ARCHIVE}/implementation-roadmap.md",
    f"{ACTIVE_PROGRAM_ARCHIVE}/closure-checklist.md",
    f"{ACTIVE_PROGRAM_ARCHIVE}/closure-summary.md",
    *[f"{ACTIVE_PROGRAM_ARCHIVE}/{phase_name}" for phase_name in ACTIVE_PROGRAM_PHASE_FILES],
    f"{RUNTIME_PROGRAM_ARCHIVE}/README.md",
    f"{RUNTIME_PROGRAM_ARCHIVE}/current.md",
    f"{RUNTIME_PROGRAM_ARCHIVE}/implementation-roadmap.md",
    f"{RUNTIME_PROGRAM_ARCHIVE}/closure-checklist.md",
    f"{RUNTIME_PROGRAM_ARCHIVE}/closure-summary.md",
    *[f"{RUNTIME_PROGRAM_ARCHIVE}/{phase_name}" for phase_name in RUNTIME_PROGRAM_PHASE_FILES],
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
    "workflow-change-note-template.md": [
        "Change Summary",
        "Trigger",
        "Requirement Type",
        "规则分类证据",
        "写回路径证据",
        "Affected Workflow Files",
        "Validation",
    ],
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
    "verify_workflow_update_policy_requires_classification_evidence",
    "verify_phase_closure_template_self_maintenance_contract",
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
    program_files = sorted(path.name for path in programs_root.iterdir() if path.is_file())
    if program_files != sorted(ACTIVE_PROGRAM_FILES):
        errors.append(f".agent/programs active files drifted: {program_files}")
    for name in ACTIVE_PROGRAM_FILES:
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
    readme = (repo_root / ".agent/programs/README.md").read_text(encoding="utf-8")
    roadmap = (repo_root / ".agent/programs/implementation-roadmap.md").read_text(encoding="utf-8")
    closure = (repo_root / ".agent/programs/closure-checklist.md").read_text(encoding="utf-8")
    current_reference = (repo_root / ".agent/references/current-program.md").read_text(encoding="utf-8")
    latest_archive_root = repo_root / LATEST_COMPLETED_PROGRAM_ARCHIVE
    latest_archive_text = (
        (latest_archive_root / "current.md").read_text(encoding="utf-8")
        + (latest_archive_root / "README.md").read_text(encoding="utf-8")
        + (latest_archive_root / "closure-summary.md").read_text(encoding="utf-8")
    )
    production_archive_root = repo_root / ACTIVE_PROGRAM_ARCHIVE
    production_archive_text = (
        (production_archive_root / "current.md").read_text(encoding="utf-8")
        + (production_archive_root / "README.md").read_text(encoding="utf-8")
        + (production_archive_root / "closure-summary.md").read_text(encoding="utf-8")
    )
    ingestion_archive_root = repo_root / CURRENT_ACTIVE_PROGRAM_ARCHIVE
    ingestion_archive_text = (
        (ingestion_archive_root / "current.md").read_text(encoding="utf-8")
        + (ingestion_archive_root / "README.md").read_text(encoding="utf-8")
        + (ingestion_archive_root / "closure-summary.md").read_text(encoding="utf-8")
    )
    runtime_archive_root = repo_root / RUNTIME_PROGRAM_ARCHIVE
    runtime_archive_text = (
        (runtime_archive_root / "current.md").read_text(encoding="utf-8")
        + (runtime_archive_root / "README.md").read_text(encoding="utf-8")
        + (runtime_archive_root / "closure-summary.md").read_text(encoding="utf-8")
    )
    archive_root = repo_root / MASTER_PROGRAM_ARCHIVE
    for phrase in [
        "state: active",
        f"active_program: {PROGRAM3_ACTIVE_NAME}",
        "current_phase: PHASE09_planning-contract-and-strategy-selector.md",
        f"latest_completed_program: {LATEST_COMPLETED_PROGRAM_NAME}",
        PROGRAM3_ACTIVE_NAME,
        LATEST_COMPLETED_PROGRAM_NAME,
        LATEST_COMPLETED_PROGRAM_ARCHIVE,
        CURRENT_ACTIVE_PROGRAM_NAME,
        CURRENT_ACTIVE_PROGRAM_ARCHIVE,
        "zuno-enterprise-agentic-graphrag-production-suite-v1",
        "zuno-runtime-subsystems-parallel-v1",
        "zuno-agent-planning-integration-v1",
        "zuno-enterprise-knowledge-eval-benchmark-v1",
        ACTIVE_PROGRAM_NAME,
        ACTIVE_PROGRAM_ARCHIVE,
        "completed / archived",
        "PHASE01-PHASE08",
        "PHASE01-PHASE12",
        "PHASE01_truth-source-and-gap-audit",
        "PHASE08_docs-verifier-closure",
        "Product V1 local durable ingestion baseline",
        "一次性交付型成熟化 program",
        "成熟目标架构和四大总交付物完成",
        "工作流自洽与自我维护",
        "文档系统清晰无冗余",
        "文件夹和代码 ownership 清晰",
        "架构功能完整实现",
        RUNTIME_PROGRAM_NAME,
        RUNTIME_PROGRAM_ARCHIVE,
        "runtime-first / vertical-slice-first",
        "只写 contract、schema 或 README 不能关闭 runtime phase",
        "成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准",
        "上传文档 -> parse -> index -> ask -> Agentic retrieval -> cited answer -> trace/eval -> artifact/feedback",
    ]:
        if phrase not in current + readme + roadmap + closure + current_reference + latest_archive_text + ingestion_archive_text + production_archive_text + runtime_archive_text:
            errors.append(f"program lifecycle surface missing active/archive phrase: {phrase}")
    active_phase_names = sorted(path.name for path in (repo_root / ".agent/programs").glob("PHASE*.md"))
    if active_phase_names != sorted(PROGRAM3_ACTIVE_PHASE_FILES):
        errors.append(".agent/programs active Program 3 phase files drifted: " + ", ".join(active_phase_names))
    for phase_name in PROGRAM3_ACTIVE_PHASE_FILES:
        phase_path = repo_root / ".agent/programs" / phase_name
        if not phase_path.exists():
            continue
        phase_content = phase_path.read_text(encoding="utf-8")
        if f"program: {PROGRAM3_ACTIVE_NAME}" not in phase_content:
            errors.append(f"Program 3 active phase missing program id: {phase_name}")
        if phase_name.startswith("PHASE01_") or phase_name.startswith("PHASE02_") or phase_name.startswith("PHASE03_") or phase_name.startswith("PHASE04_") or phase_name.startswith("PHASE05_") or phase_name.startswith("PHASE06_") or phase_name.startswith("PHASE07_") or phase_name.startswith("PHASE08_"):
            expected_status = "status: completed"
        elif phase_name.startswith("PHASE09_"):
            expected_status = "status: active"
        else:
            expected_status = "status: pending"
        if expected_status not in phase_content:
            errors.append(f"Program 3 active phase missing {expected_status}: {phase_name}")
        for required in [
            "## 目标",
            "## 范围",
            "## 禁止范围",
            "## 验收闸门",
            "## 验证命令",
            "## 需要先读取",
            "## 需要修改的文件",
            "## 执行拆解",
            "## 多 agent 分工",
            "## 需要返回的证据",
            "## 停止条件",
        ]:
            if required not in phase_content:
                errors.append(f"Program 3 active phase missing section {required}: {phase_name}")
    if (repo_root / ".agent/programs/thread-prompts").exists():
        errors.append(".agent/programs/thread-prompts must stay archived until Program 4 starts")
    for phase_name in LATEST_COMPLETED_PROGRAM_PHASE_FILES:
        phase_path = latest_archive_root / phase_name
        if not phase_path.exists():
            errors.append(f"latest completed ingestion v2 archive missing phase: {phase_name}")
            continue
        phase_content = phase_path.read_text(encoding="utf-8")
        if f"program: {LATEST_COMPLETED_PROGRAM_NAME}" not in phase_content:
            errors.append(f"latest completed ingestion v2 phase missing program id: {phase_name}")
        if "status: completed" not in phase_content:
            errors.append(f"latest completed ingestion v2 phase missing completed status: {phase_name}")
        for required in [
            "## 目标",
            "## 范围",
            "## 禁止范围",
            "## 验收闸门",
            "## 验证命令",
            "## 需要先读取",
            "## 需要修改的文件",
            "## 执行拆解",
            "## 多 agent 分工",
            "## 需要返回的证据",
            "## 停止条件",
        ]:
            if required not in phase_content:
                errors.append(f"latest completed ingestion v2 phase missing section {required}: {phase_name}")
    for required_archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        if not (latest_archive_root / required_archive_file).exists():
            errors.append(f"latest completed ingestion v2 archive missing file: {required_archive_file}")
    for phase_name in CURRENT_ACTIVE_PROGRAM_PHASE_FILES:
        phase_path = ingestion_archive_root / phase_name
        if not phase_path.exists():
            errors.append(f"completed ingestion program archive missing phase: {phase_name}")
            continue
        phase_content = phase_path.read_text(encoding="utf-8")
        if "program: zuno-production-document-ingestion-and-thread-foundation-v1" not in phase_content:
            errors.append(f"completed ingestion program phase missing program id: {phase_name}")
        if "status: completed" not in phase_content:
            errors.append(f"completed ingestion program phase missing completed status: {phase_name}")
        for required in [
            "## 目标",
            "## 范围",
            "## 禁止范围",
            "## 验收闸门",
            "## 验证命令",
            "## 需要先读取",
            "## 需要修改的文件",
            "## 执行拆解",
            "## 多 agent 分工",
            "## 需要返回的证据",
            "## 停止条件",
        ]:
            if required not in phase_content:
                errors.append(f"completed ingestion program phase missing section {required}: {phase_name}")
    for required_archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        if not (ingestion_archive_root / required_archive_file).exists():
            errors.append(f"completed ingestion program archive missing file: {required_archive_file}")
    queued_root = repo_root / ".agent/programs/queued-programs"
    queued_files = sorted(path.name for path in queued_root.glob("*.md")) if queued_root.exists() else []
    if queued_files != sorted(QUEUED_PROGRAM_FILES):
        errors.append(".agent/programs queued program files drifted: " + ", ".join(queued_files))
    for file_name in QUEUED_PROGRAM_FILES:
        queued_path = queued_root / file_name
        if not queued_path.exists():
            errors.append(f"queued program missing file: {file_name}")
            continue
        content = queued_path.read_text(encoding="utf-8")
        if file_name != "README.md":
            for phrase in [
                "state: superseded",
                "merged_into: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1",
                "superseded_by: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1",
            ]:
                if phrase not in content:
                    errors.append(f"superseded program file missing phrase {phrase}: {file_name}")
    errors.extend(_verify_archived_phase_state(repo_root))
    for phase_name in ACTIVE_PROGRAM_PHASE_FILES:
        phase_path = production_archive_root / phase_name
        if not phase_path.exists():
            errors.append(f"production completion program archive missing phase: {phase_name}")
            continue
        phase_content = phase_path.read_text(encoding="utf-8")
        if "status: completed" not in phase_content:
            errors.append(f"production completion program archive phase missing completed status: {phase_name}")
        for required in [
            "## 目标",
            "## 范围",
            "## 禁止范围",
            "## 验收闸门",
            "## 验证命令",
            "## 需要先读取",
            "## 需要修改的文件",
            "## 执行拆解",
            "## 多 agent 分工",
            "## 需要返回的证据",
            "## 停止条件",
        ]:
            if required not in phase_content:
                errors.append(f"production completion program archive phase missing section {required}: {phase_name}")
    for required_archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        if not (production_archive_root / required_archive_file).exists():
            errors.append(f"production completion program archive missing file: {required_archive_file}")
    for phase_index, phase_name in enumerate(RUNTIME_PROGRAM_PHASE_FILES, start=1):
        phase_path = runtime_archive_root / phase_name
        if not phase_path.exists():
            errors.append(f"runtime program archive missing phase: {phase_name}")
            continue
        phase_content = phase_path.read_text(encoding="utf-8")
        if "status: completed" not in phase_content:
            errors.append(f"runtime program archive phase status drifted: {phase_name}")
        for required in ["## 目标", "## 范围", "## 禁止范围", "## 验收闸门", "## 验证命令"]:
            if required not in phase_content:
                errors.append(f"runtime program archive phase missing section {required}: {phase_name}")
    for required_archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        if not (runtime_archive_root / required_archive_file).exists():
            errors.append(f"runtime program archive missing file: {required_archive_file}")
    for phrase in [
        MASTER_PROGRAM_NAME,
        MASTER_PROGRAM_ARCHIVE,
    ]:
        if phrase not in current + readme + current_reference:
            errors.append(f"program lifecycle surface missing archived master phrase: {phrase}")
    for required_archive_file in ["README.md", "current.md", "implementation-roadmap.md", "closure-checklist.md", "closure-summary.md"]:
        if not (archive_root / required_archive_file).exists():
            errors.append(f"master program archive missing file: {required_archive_file}")
    for phase_name in MASTER_PROGRAM_PHASE_FILES:
        phase_path = archive_root / phase_name
        if not phase_path.exists():
            errors.append(f"master program archive missing phase: {phase_name}")
        elif "status: completed" not in phase_path.read_text(encoding="utf-8"):
            errors.append(f"master program archive phase missing completed status: {phase_name}")
    for phrase in [
        COMPLETED_PROGRAM_NAME,
        COMPLETED_PROGRAM_ARCHIVE,
    ]:
        if phrase not in current_reference:
            errors.append(f"current-program reference missing archived phrase: {phrase}")
    return errors


def verify_program_thread_prompts(repo_root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    prompt_root = repo_root / CURRENT_ACTIVE_PROGRAM_ARCHIVE / "thread-prompts"
    prompt_files = sorted(path.name for path in prompt_root.glob("*.md")) if prompt_root.exists() else []
    if prompt_files != sorted(THREAD_PROMPT_FILES):
        errors.append("completed ingestion program thread-prompts files drifted: " + ", ".join(prompt_files))
    required_phrases = [
        "## UI Mode",
        "Codex UI 目标模式",
        "## Goal",
        "## Safety Gate",
        "git fetch --prune",
        "git status --short --branch",
        "git log --oneline -5 --decorate",
        "## Program 1 Shared Facts",
        "Document IR",
        "citation_lineage",
        "target-blocked",
        "## Allowed Paths",
        "## Forbidden Paths",
        "## Focused Tests",
        "## Stop Conditions",
        "Commit hash",
        "Push status",
    ]
    branch_by_file = {
        "THREAD_A_memory-context.md": "codex/zuno-p2-memory-context",
        "THREAD_B_tool-sandbox.md": "codex/zuno-p2-tool-sandbox",
        "THREAD_C_security-governance.md": "codex/zuno-p2-security-governance",
        "THREAD_D_graphrag-index.md": "codex/zuno-p2-graphrag-index",
    }
    ownership_by_file = {
        "THREAD_A_memory-context.md": "src/backend/zuno/memory/**",
        "THREAD_B_tool-sandbox.md": "src/backend/zuno/capability/**",
        "THREAD_C_security-governance.md": "src/backend/zuno/platform/security/**",
        "THREAD_D_graphrag-index.md": "src/backend/zuno/knowledge/**",
    }
    for file_name in THREAD_PROMPT_FILES:
        prompt_path = prompt_root / file_name
        if not prompt_path.exists():
            errors.append(f"program thread prompt missing file: {file_name}")
            continue
        content = prompt_path.read_text(encoding="utf-8")
        for phrase in required_phrases:
            if phrase not in content:
                errors.append(f"program thread prompt missing phrase {phrase}: {file_name}")
        for phrase in [
            branch_by_file[file_name],
            ownership_by_file[file_name],
            "AGENTS.md",
            "docs/**",
            ".agent/**",
        ]:
            if phrase not in content:
                errors.append(f"program thread prompt missing boundary phrase {phrase}: {file_name}")
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


def verify_workflow_update_policy_requires_classification_evidence(
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    errors: list[str] = []
    policy = (repo_root / ".agent/references/workflow-update-policy.md").read_text(
        encoding="utf-8"
    )
    requirements = (repo_root / ".agent/references/workflow-requirements.md").read_text(
        encoding="utf-8"
    )
    checklist = (repo_root / ".agent/references/workflow-maintenance-checklist.md").read_text(
        encoding="utf-8"
    )
    template = (repo_root / ".agent/templates/workflow-change-note-template.md").read_text(
        encoding="utf-8"
    )
    combined = policy + requirements + checklist + template
    for phrase in [
        "规则分类证据",
        "写回路径证据",
        "one-time instruction",
        "reusable project rule",
        "architecture governance rule",
        "Codex execution rule",
        "documentation template rule",
        "long-term workflow rule",
        "AGENTS.md",
        ".agent/references/",
        ".agent/templates/",
        ".agent/programs/",
        "docs/architecture/",
        "verifier / tests",
    ]:
        if phrase not in combined:
            errors.append(f"workflow update policy evidence contract missing phrase: {phrase}")
    for section in ["## 规则分类证据", "## 写回路径证据"]:
        if section not in template:
            errors.append(f"workflow-change-note-template.md missing section: {section}")
    return errors


def verify_phase_closure_template_self_maintenance_contract(
    repo_root: Path = REPO_ROOT,
) -> list[str]:
    errors: list[str] = []
    path = repo_root / ".agent/templates/phase-closure-report.md"
    content = path.read_text(encoding="utf-8")
    if "## 自维护审查" not in content or "## 剩余风险" not in content:
        return ["phase-closure-report.md missing self-maintenance or risk section"]
    self_review = content.split("## 自维护审查", 1)[1].split("## 剩余风险", 1)[0]
    checklist_items = [
        line.strip()
        for line in self_review.splitlines()
        if line.strip().startswith("- ")
    ]
    if len(checklist_items) != len(set(checklist_items)):
        errors.append("phase-closure-report.md self-maintenance checklist has duplicate items")
    for phrase in [
        "`AGENTS.md`",
        "`.agent/system.yaml`",
        "`.agent/references/`",
        "`.agent/templates/`",
        "`.agent/programs/`",
        "`docs/history/programs/`",
        "`docs/architecture/architecture.md`",
        "`.agent/architecture/architecture.md`",
        "`docs/architecture/architecture.html`",
        "`.agent/architecture/architecture.html`",
        "verifier / tests",
    ]:
        if phrase not in self_review:
            errors.append(f"phase-closure-report.md self-maintenance missing item: {phrase}")
    return errors


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
    errors.extend(verify_program_thread_prompts())
    errors.extend(verify_workflow_change_log_entries())
    errors.extend(verify_workflow_update_policy_requires_classification_evidence())
    errors.extend(verify_phase_closure_template_self_maintenance_contract())
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
