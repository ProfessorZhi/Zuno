from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/06-agent-core-planning-control.md"
MIRROR = REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md"
DOCS_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_INDEX = REPO_ROOT / ".agent/modules/README.md"
AGENTS = REPO_ROOT / "AGENTS.md"
SYSTEM_YAML = REPO_ROOT / ".agent/system.yaml"

REMOVED_PATHS = [
    REPO_ROOT / "docs/modules/06-agent-core-control-protocols.md",
    REPO_ROOT / "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
    REPO_ROOT / ".agent/modules/06-agent-core-control-protocols.md",
    REPO_ROOT / ".agent/modules/06-agent-core-consistency-lifecycle-protocols.md",
]

REQUIRED_PARTS = [
    "# Part I：定位与概念架构",
    "# Part II：智能机制与运行流程",
    "# Part III：状态、恢复与一致性概览",
    "# Part IV：目标实现表面与规范索引",
    "# Part V：领域模型、状态转换与决策闭环",
    "# Part VI：规范性控制协议",
    "# Part VII：一致性与生命周期协议",
    "# Part VIII：验证与完成证据",
]

REQUIRED_TERMS = [
    "Single Controller Agent Runtime",
    "AgentRunGraph",
    "StepExecutionGraph",
    "TaskContract",
    "GoalVersion",
    "EffectivePolicySnapshot",
    "ActionLifecycleStatus",
    "ActionOutcome",
    "command_sequence_no",
    "ResourceClaim",
    "PlanPatchOperation",
    "BudgetSettlement",
    "Requirement Enforcement Matrix",
    "Transition Matrix",
    "PlanVersion Transition Matrix",
    "Final Gate Routing",
    "RunOutcome Contract",
    "LangGraph Adapter Contract",
    "InfrastructureDrainProtocol",
    "RunStreamEvent",
    "ModelCapabilityProfile",
    "StepFeasibilityDecision",
    "Resource Conflict Matrix",
    "CONTROL_REPLAY",
    "SIMULATION_FORK",
    "StateMigrationRecord",
    "逐条 Requirement Control Registry",
    "pending_interrupt_refs",
    "WAITING_CONDITION",
    "CANCELLING",
    "PreparedAction",
    "RecoveryWatermark",
    "ResultValidity",
    "RunOrphanReconciler",
    "prepare_publication",
    "DeliveryReceipt",
    "PostgreSQL",
    "本文是 Agent Core / Planning & Control 模块唯一的正式 Target 架构文档",
    ".agent/programs/",
]

REQUIRED_TABLES = [
    "agent_objective_outcomes",
    "agent_run_commands",
    "agent_control_decisions",
    "agent_effective_policy_snapshots",
    "agent_resource_claims",
    "agent_domain_commit_markers",
    "agent_recovery_watermarks",
    "agent_artifact_candidates",
    "agent_publication_artifact_bindings",
    "agent_publication_correction_decisions",
    "agent_budget_consumptions",
    "agent_budget_adjustments",
    "agent_budget_settlements",
    "agent_step_feasibility_decisions",
    "agent_graph_bundles",
    "agent_run_stream_events",
    "agent_state_migration_records",
    "agent_outcome_corrections",
]

FORBIDDEN_TERMS = [
    "# 35. Current Baseline",
    "# 36. 实现阶段",
    "pending_interrupt_id: str | None",
    "同一 Run 默认只允许一个 PENDING Interrupt",
    "Agent Core Target 由三份正式文档共同构成",
    "未来 Program 必须以本文及配套规范为目标约束",
    "状态：DRAFT、VALIDATING、VALID、INVALID、SUPERSEDED、PUBLISHED、WITHDRAWN。",
    "SUCCEEDED\nFAILED\nUNKNOWN\nRECONCILING\nRECONCILED",
    "状态：CLAIMED、EXECUTING、SUCCEEDED、FAILED、UNKNOWN、RECONCILED。",
]

OBJECT_TABLE_PAIRS = {
    "ObjectiveOutcome": "agent_objective_outcomes",
    "RunCommand": "agent_run_commands",
    "ControlDecision": "agent_control_decisions",
    "EffectivePolicySnapshot": "agent_effective_policy_snapshots",
    "ResourceClaim": "agent_resource_claims",
    "DomainCommitMarker": "agent_domain_commit_markers",
    "RecoveryWatermark": "agent_recovery_watermarks",
    "ArtifactCandidate": "agent_artifact_candidates",
    "PublicationArtifactBinding": "agent_publication_artifact_bindings",
    "PublicationCorrectionDecision": "agent_publication_correction_decisions",
    "BudgetConsumption": "agent_budget_consumptions",
    "BudgetAdjustment": "agent_budget_adjustments",
    "BudgetSettlement": "agent_budget_settlements",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []
    for path in [FORMAL, MIRROR, DOCS_INDEX, AGENT_INDEX, AGENTS, SYSTEM_YAML]:
        if not path.exists():
            errors.append(f"missing Agent Core target path: {path.relative_to(REPO_ROOT)}")
    for path in REMOVED_PATHS:
        if path.exists():
            errors.append(f"retired split Agent Core document still exists: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    formal = _read(FORMAL)
    if FORMAL.read_bytes() != MIRROR.read_bytes():
        errors.append("Agent Core formal document and mirror must be byte-identical")

    if "status: normative-target-module-architecture" not in formal:
        errors.append("Agent Core document must declare normative-target-module-architecture")

    positions: list[int] = []
    for part in REQUIRED_PARTS:
        if formal.count(part) != 1:
            errors.append(f"Agent Core document must contain part exactly once: {part}")
        else:
            positions.append(formal.index(part))
    if positions and positions != sorted(positions):
        errors.append("Agent Core document parts are not in canonical order I through VIII")

    for term in REQUIRED_TERMS:
        if term not in formal:
            errors.append(f"Agent Core document missing required term: {term}")
    for table in REQUIRED_TABLES:
        if table not in formal:
            errors.append(f"Agent Core document missing target table: {table}")
    for term in FORBIDDEN_TERMS:
        if term in formal:
            errors.append(f"Agent Core document contains obsolete or conflicting contract: {term}")

    for object_name, table_name in OBJECT_TABLE_PAIRS.items():
        if object_name not in formal or table_name not in formal:
            errors.append(f"Agent Core object/storage mapping incomplete: {object_name} -> {table_name}")

    for transition in [
        "VALIDATING_INPUT` | `INPUT_INVALID",
        "RUNNING` | `REPLAN_REQUIRED",
        "FINALIZING` | `FINAL_GATE_PASS",
        "PUBLISHING` | `DELIVERY_CONFIRMED",
        "CANCELLING` | `DRAIN_COMPLETE",
    ]:
        if transition not in formal:
            errors.append(f"AgentRun Transition Matrix missing transition: {transition}")

    for policy_term in [
        "System Default",
        "Tenant Policy",
        "Security Override",
        "Runtime Emergency Override",
        "AcceptancePolicy",
        "ReflectionPolicy",
    ]:
        if policy_term not in formal:
            errors.append(f"Agent Core Policy Contract missing term: {policy_term}")

    ids = [int(value) for value in re.findall(r"ARCH-AGENT-(\d{3})", formal)]
    if sorted(ids) != list(range(1, 81)):
        errors.append("Agent Core document must define ARCH-AGENT-001 through ARCH-AGENT-080 exactly once")

    controls = [int(value) for value in re.findall(r"RC-AG-(\d{3})", formal)]
    if sorted(controls) != list(range(1, 81)):
        errors.append("Agent Core document must map RC-AG-001 through RC-AG-080 exactly once")

    for matrix in [
        "### 39.1 PlanVersion",
        "### 39.2 StepRun Attempt",
        "### 39.3 ActionLifecycleStatus × ActionOutcome",
        "### 39.4 Interrupt",
        "### 39.5 Publication 与 PublicationAttempt",
    ]:
        if matrix not in formal:
            errors.append(f"Agent Core document missing state matrix: {matrix}")

    for route in [
        "`PASS` | `ArtifactValidation → Publication`",
        "`REWRITE` | `FinalSynthesis`",
        "`RETRIEVE_MORE` | `SupplementalRetrieval`",
        "`REPLAN` | `ReplanBarrier`",
        "`ABSTAIN` | `OutcomeCommit`",
    ]:
        if route not in formal:
            errors.append(f"Final Gate routing missing: {route}")

    for adapter_term in [
        "每个 Node invocation 最多调用一次 interrupt()",
        "Resume 从包含 interrupt() 的 Node 开头重新执行",
        "LangGraph Node Retry",
        "Infrastructure Drain",
        "thread_id = stable opaque UUID/hash, length < 255",
        "Checkpoint Retention",
    ]:
        if adapter_term not in formal:
            errors.append(f"LangGraph Adapter Contract missing: {adapter_term}")

    for index_name, content in {
        "docs/modules/README.md": _read(DOCS_INDEX),
        ".agent/modules/README.md": _read(AGENT_INDEX),
        "AGENTS.md": _read(AGENTS),
        ".agent/system.yaml": _read(SYSTEM_YAML),
    }.items():
        if "06-agent-core-planning-control.md" not in content:
            errors.append(f"{index_name} does not route to the unified Agent Core target document")
        for retired in [
            "06-agent-core-control-protocols.md",
            "06-agent-core-consistency-lifecycle-protocols.md",
        ]:
            if retired in content:
                errors.append(f"{index_name} still references retired split document: {retired}")

    if ".agent/programs" not in formal or ".agent/programs" not in _read(DOCS_INDEX):
        errors.append("Target architecture and execution Program boundary is not explicit")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("refined Agent Core target architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
