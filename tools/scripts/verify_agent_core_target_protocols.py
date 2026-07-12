from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/06-agent-core-control-protocols.md"
MIRROR = REPO_ROOT / ".agent/modules/06-agent-core-control-protocols.md"
DOCS_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_INDEX = REPO_ROOT / ".agent/modules/README.md"

REQUIRED_SECTIONS = [
    "# 3. 架构不变量",
    "# 4. 三套核心状态机",
    "# 5. DAG 依赖、条件、Disposition 与 Join",
    "# 6. Dispatch、Reducer、Fencing 与 Replan Barrier",
    "# 7. Interrupt、Signal 与 Side Effect Protocol",
    "# 8. AnswerPolicy、Final Gate 与 Publication",
    "# 9. Failure Taxonomy、Budget 与 No-progress",
    "# 10. Cross-module Ownership 与 Contract Versioning",
]

REQUIRED_TERMS = [
    "INV-AGENT-001",
    "INV-AGENT-024",
    "AgentRun 状态机",
    "PlanVersion 状态机",
    "StepRun 状态机",
    "ALL_SUCCESS",
    "StepDisposition",
    "PlanLivenessFinding",
    "JoinPolicy",
    "controller_epoch",
    "execution_epoch",
    "BranchResultRef",
    "Replan Barrier",
    "PreparedAction",
    "IdempotencyClaim",
    "UNKNOWN 与 Reconcile",
    "Final Candidate",
    "Publication Contract",
    "FailureClass",
    "Budget Reservation",
    "NO_PROGRESS",
    "事实 Ownership Matrix",
    "Contract Envelope",
    "Checkpoint 与领域事实边界",
    "design available",
    "contract-ready",
    "program-ready",
]

FORBIDDEN_TARGET_SCOPE_TERMS = [
    "GeneralAgent",
    "Legacy Adapter",
    "Shadow 模式",
    "Canary",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []

    for path in [FORMAL, MIRROR, DOCS_INDEX, AGENT_INDEX]:
        if not path.exists():
            errors.append(f"missing Agent Core target protocol path: {path.relative_to(REPO_ROOT)}")

    if errors:
        return errors

    formal = _read(FORMAL)
    mirror = _read(MIRROR)
    docs_index = _read(DOCS_INDEX)
    agent_index = _read(AGENT_INDEX)

    if formal != mirror:
        errors.append("Agent Core control protocol mirror must be byte-identical to the formal document")

    if "status: normative-target-protocols" not in formal:
        errors.append("Agent Core control protocol must declare normative-target-protocols status")

    if "本文只定义 Target" not in formal:
        errors.append("Agent Core control protocol must explicitly state its Target-only scope")

    for section in REQUIRED_SECTIONS:
        if section not in formal:
            errors.append(f"Agent Core control protocol missing section: {section}")

    for term in REQUIRED_TERMS:
        if term not in formal:
            errors.append(f"Agent Core control protocol missing required term: {term}")

    for requirement_no in range(33, 61):
        requirement_id = f"ARCH-AGENT-{requirement_no:03d}"
        if requirement_id not in formal:
            errors.append(f"Agent Core control protocol missing requirement: {requirement_id}")

    for term in FORBIDDEN_TARGET_SCOPE_TERMS:
        if term in formal:
            errors.append(f"Target-only Agent Core protocol contains migration-specific term: {term}")

    for index_name, content in [
        ("docs/modules/README.md", docs_index),
        (".agent/modules/README.md", agent_index),
    ]:
        if "06-agent-core-control-protocols.md" not in content:
            errors.append(f"{index_name} does not route to the Agent Core control protocol")
        if "verify_agent_core_target_protocols.py" not in content:
            errors.append(f"{index_name} does not expose the Agent Core protocol verifier")

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
