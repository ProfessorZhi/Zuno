from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

FORMAL_MIRROR_PAIRS = [
    (
        REPO_ROOT / "docs/modules/06-agent-core-planning-control.md",
        REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md",
    ),
    (
        REPO_ROOT / "docs/modules/06-agent-core-control-protocols.md",
        REPO_ROOT / ".agent/modules/06-agent-core-control-protocols.md",
    ),
    (
        REPO_ROOT / "docs/modules/06-agent-core-consistency-lifecycle-protocols.md",
        REPO_ROOT / ".agent/modules/06-agent-core-consistency-lifecycle-protocols.md",
    ),
]

DOCS_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_INDEX = REPO_ROOT / ".agent/modules/README.md"
AGENTS = REPO_ROOT / "AGENTS.md"
SYSTEM_YAML = REPO_ROOT / ".agent/system.yaml"

MAIN_REQUIRED = [
    "Single Controller Agent Runtime",
    "AgentRunGraph",
    "StepExecutionGraph",
    "TaskContract",
    "GoalVersion",
    "pending_interrupt_refs",
    "create_final_candidate",
    "prepare_publication",
    "DeliveryReceipt",
    "controller_epoch",
    "execution_epoch",
    "domain_generation",
    "checkpoint_generation",
    "Result Validity",
    "Orphan Recovery",
    "时间语义",
    "agent_prepared_actions",
    "agent_publications",
    "agent_delivery_receipts",
]

CONTROL_REQUIRED = [
    "# 2. 架构不变量",
    "# 3. AgentRun 状态机",
    "WAITING_CONDITION",
    "CANCELLING",
    "# 4. PlanVersion 状态机",
    "# 5. StepRun 与 ActionRun 状态机",
    "# 6. DAG、Condition 与 Disposition",
    "# 8. Dispatch、Fencing 与 Reducer",
    "# 9. Replan Barrier",
    "一个 Run 可以同时存在多个 Pending Interrupt",
    "PreparedAction",
    "FinalCandidate",
    "Publication",
    "Failure Taxonomy",
    "Cross-module Ownership",
]

CONSISTENCY_REQUIRED = [
    "# 1. TaskContract、GoalVersion 与 Objective",
    "# 2. 控制命令仲裁与 Policy Precedence",
    "# 3. Domain Store 与 LangGraph Checkpoint 一致性",
    "# 4. ResultValidity 与污染传播",
    "# 5. Domain Event、Outbox 与交付语义",
    "# 6. Artifact 生命周期",
    "# 7. Orphan Recovery 与后台 Reconciler",
    "# 8. 时间语义",
    "RecoveryWatermark",
    "PublicationCorrectionDecision",
    "RunOrphanReconciler",
    "数据库时间",
]

FORBIDDEN_TARGET_PATTERNS = [
    "# 35. Current Baseline",
    "# 36. 实现阶段",
    "pending_interrupt_id: str | None",
    "pending_interrupt_id UUID",
    "同一 Run 默认只允许一个 PENDING Interrupt",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []

    required_paths = [path for pair in FORMAL_MIRROR_PAIRS for path in pair]
    required_paths.extend([DOCS_INDEX, AGENT_INDEX, AGENTS, SYSTEM_YAML])

    for path in required_paths:
        if not path.exists():
            errors.append(f"missing Agent Core target path: {path.relative_to(REPO_ROOT)}")

    if errors:
        return errors

    for formal, mirror in FORMAL_MIRROR_PAIRS:
        if formal.read_bytes() != mirror.read_bytes():
            errors.append(
                f"mirror mismatch: {mirror.relative_to(REPO_ROOT)} must match "
                f"{formal.relative_to(REPO_ROOT)}"
            )

    main = _read(FORMAL_MIRROR_PAIRS[0][0])
    control = _read(FORMAL_MIRROR_PAIRS[1][0])
    consistency = _read(FORMAL_MIRROR_PAIRS[2][0])
    indexes = {
        "docs/modules/README.md": _read(DOCS_INDEX),
        ".agent/modules/README.md": _read(AGENT_INDEX),
        "AGENTS.md": _read(AGENTS),
        ".agent/system.yaml": _read(SYSTEM_YAML),
    }

    if "本文只描述理想目标架构" not in main:
        errors.append("Agent Core main design must explicitly state Target-only scope")
    if "本文只定义 Target" not in control:
        errors.append("Agent Core control protocol must explicitly state Target-only scope")
    if "本文只描述理想 Target" not in consistency:
        errors.append("Agent Core consistency protocol must explicitly state Target-only scope")

    for term in MAIN_REQUIRED:
        if term not in main:
            errors.append(f"Agent Core main design missing required term: {term}")

    for term in CONTROL_REQUIRED:
        if term not in control:
            errors.append(f"Agent Core control protocol missing required term: {term}")

    for term in CONSISTENCY_REQUIRED:
        if term not in consistency:
            errors.append(f"Agent Core consistency protocol missing required term: {term}")

    combined = "\n".join([main, control, consistency])
    for term in FORBIDDEN_TARGET_PATTERNS:
        if term in combined:
            errors.append(f"Agent Core Target docs contain obsolete contract: {term}")

    ids = re.findall(r"ARCH-AGENT-(\d{3})", combined)
    counts: dict[int, int] = {}
    for value in ids:
        number = int(value)
        counts[number] = counts.get(number, 0) + 1

    missing = [number for number in range(1, 81) if number not in counts]
    if missing:
        errors.append(f"Agent Core requirements missing IDs: {missing}")

    duplicates = [number for number, count in counts.items() if count > 1]
    if duplicates:
        errors.append(f"Agent Core requirements duplicated across normative docs: {duplicates}")

    for index_name, content in indexes.items():
        for filename in [
            "06-agent-core-planning-control.md",
            "06-agent-core-control-protocols.md",
            "06-agent-core-consistency-lifecycle-protocols.md",
        ]:
            if filename not in content:
                errors.append(f"{index_name} does not route to {filename}")

    for index_name in ["docs/modules/README.md", ".agent/modules/README.md", "AGENTS.md"]:
        if "verify_agent_core_target_protocols.py" not in indexes[index_name]:
            errors.append(f"{index_name} does not expose Agent Core verifier")

    if "Single Controller Agent Runtime" not in indexes[".agent/system.yaml"]:
        errors.append(".agent/system.yaml must use Single Controller Agent Runtime terminology")

    if "pending_interrupt_refs" not in main or "prepare_publication" not in main:
        errors.append("AgentRunGraph target must include multi-interrupt and Publication flow")

    if "WAITING_CONDITION" not in control or "BLOCKED" not in control:
        errors.append("control protocol must distinguish waiting from terminal blocked")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("agent core target protocol verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
