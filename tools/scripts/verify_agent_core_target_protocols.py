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
    "# Part III：状态、恢复与一致性",
    "# Part IV：目标 Contract 与实施规格",
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

FORBIDDEN_TERMS = [
    "# 35. Current Baseline",
    "# 36. 实现阶段",
    "pending_interrupt_id: str | None",
    "同一 Run 默认只允许一个 PENDING Interrupt",
    "Agent Core Target 由三份正式文档共同构成",
]


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

    for part in REQUIRED_PARTS:
        if part not in formal:
            errors.append(f"Agent Core document missing part: {part}")
    for term in REQUIRED_TERMS:
        if term not in formal:
            errors.append(f"Agent Core document missing required term: {term}")
    for term in FORBIDDEN_TERMS:
        if term in formal:
            errors.append(f"Agent Core document contains obsolete contract: {term}")

    ids = [int(value) for value in re.findall(r"ARCH-AGENT-(\d{3})", formal)]
    if sorted(ids) != list(range(1, 81)):
        errors.append("Agent Core document must define ARCH-AGENT-001 through ARCH-AGENT-080 exactly once")

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
    print("unified Agent Core target architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
