from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/04-model-gateway-contract-freeze.md"
MIRROR = REPO_ROOT / ".agent/modules/04-model-gateway-contract-freeze.md"
PARENT = REPO_ROOT / "docs/modules/04-model-gateway.md"
DOCS_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_INDEX = REPO_ROOT / ".agent/modules/README.md"
WORKFLOW = REPO_ROOT / ".github/workflows/model-gateway-target-docs.yml"

REQUIRED_SECTIONS = [
    "## 0. 规范优先级与适用范围",
    "## 1. Wave 1 协调快照",
    "## 2. Canonical Ownership 收口",
    "## 3. Model Role、Model Operation、Provider 和 Model 四维分离",
    "## 4. Prompt Ownership 再拆分",
    "## 5. ModelCall 聚合与 Attempt 的关系",
    "## 6. Budget、Quota、Usage 与崩溃语义",
    "## 7. Model Gateway 领域事件目录",
    "## 8. 三层 Streaming Contract",
    "## 9. Routing 可解释与确定性重放",
    "## 10. Capability Profile 生命周期",
    "## 11. ResultValidity 传播",
    "## 12. Failure Code 对齐",
    "## 13. 实现前 Contract Freeze Gate",
    "## 14. Requirement Registry",
    "## 15. 强制 Fault / Recovery 场景",
    "## 16. Target 到 Current 的证据",
]

REQUIRED_OPERATIONS = [
    "TEXT_GENERATION",
    "STRUCTURED_GENERATION",
    "EMBEDDING",
    "RERANK",
    "VISION_EXTRACTION",
    "AUDIO_TRANSCRIPTION",
    "CLASSIFICATION",
    "JUDGE",
]

REQUIRED_CALL_STATES = [
    "CREATED",
    "VALIDATING",
    "ROUTING",
    "WAITING_ADMISSION",
    "ACTIVE",
    "WAITING_QUOTA",
    "RECONCILING",
    "SUCCEEDED",
    "FAILED",
    "EXHAUSTED",
    "CANCELLED",
    "UNKNOWN",
]

REQUIRED_CONTRACTS = [
    "ModelSecurityDecision",
    "ModelRoleContract",
    "ModelRoleRoutingProfile",
    "ModelOperationKind",
    "PromptExecutionBinding",
    "ModelCall",
    "ModelResponseSelectionDecision",
    "AttemptBudgetAllocation",
    "UsageReceipt",
    "TelemetryEnvelope",
    "ModelResultValidityChanged",
]

REQUIRED_EVENTS = [
    "ModelCallRequested",
    "ModelRoutingDecided",
    "ModelAttemptDispatched",
    "ModelAttemptUnknown",
    "ModelAttemptReconciled",
    "ModelFallbackSelected",
    "ModelResponseSelected",
    "ModelResultValidityChanged",
    "ModelStreamDisconnected",
    "StructuredOutputRejected",
    "UsageSettlementPending",
    "UsageCorrected",
    "ProviderHealthChanged",
    "CircuitBreakerChanged",
]

REQUIRED_FAILURES = [
    "MODEL_SECURITY_DECISION_EXPIRED",
    "SECURITY_EPOCH_STALE",
    "MODEL_OPERATION_UNSUPPORTED",
    "MODEL_CAPABILITY_STALE",
    "MODEL_NO_ROUTABLE_CANDIDATE",
    "MODEL_PROVIDER_RESULT_UNKNOWN",
    "MODEL_STRUCTURED_OUTPUT_REPAIR_EXHAUSTED",
    "MODEL_STREAM_SEQUENCE_GAP",
    "MODEL_QUOTA_RESERVATION_CONFLICT",
    "MODEL_USAGE_SETTLEMENT_CONFLICT",
    "MODEL_RECONCILIATION_PROOF_UNAVAILABLE",
    "MODEL_FALLBACK_EXHAUSTED",
    "MODEL_CALL_EXHAUSTED",
]

REQUIRED_OWNERSHIP = [
    "`ModelSecurityDecision` 是 Security 拥有",
    "Infrastructure 只拥有物理能力和执行 Receipt",
    "Observability 不成为调用事实 Owner",
    "Role 回答“为什么调用”；Operation 回答“执行何种模型操作”",
    "Gateway 不直接修改 Step、Plan、FinalCandidate、Publication 或 RunOutcome",
]

REQUIRED_FAULTS = [
    "Security Decision expired between Routing and Dispatch",
    "Quota reserved but Routing commit fails",
    "Two late valid responses race for selection",
    "Response committed but UsageReceipt commit fails",
    "Batch embedding partial failure",
    "Gateway restart during stream checkpoint",
    "Capability profile becomes stale after SDK upgrade",
    "Unknown event version reaches Observability",
    "Fallback Exhausted with settlement pending",
]

FORBIDDEN_CLAIMS = [
    "status: production-ready",
    "status: implementation_available",
    "Model Gateway 已 production ready",
    "Contract Freeze 已经实现",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []
    required_paths = [FORMAL, MIRROR, PARENT, DOCS_INDEX, AGENT_INDEX, WORKFLOW]
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing Model Gateway Contract Freeze path: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    formal = _read(FORMAL)
    if FORMAL.read_bytes() != MIRROR.read_bytes():
        errors.append("Model Gateway Contract Freeze formal document and mirror must be byte-identical")

    required_metadata = [
        "status: normative-target-module-addendum",
        "parent_document: `docs/modules/04-model-gateway.md`",
        "dependency_baseline_sha: `729e439e29deadc101c5687fc47125104e62e2c1`",
        "#17",
        "#19",
        "#20",
        "Parallel Proposal",
    ]
    for term in required_metadata:
        if term not in formal:
            errors.append(f"Model Gateway Contract Freeze missing metadata or proposal marker: {term}")

    positions: list[int] = []
    for section in REQUIRED_SECTIONS:
        if formal.count(section) != 1:
            errors.append(f"Model Gateway Contract Freeze must contain section exactly once: {section}")
        else:
            positions.append(formal.index(section))
    if positions and positions != sorted(positions):
        errors.append("Model Gateway Contract Freeze sections are not in canonical order")

    for collection_name, values in [
        ("operation", REQUIRED_OPERATIONS),
        ("ModelCall state", REQUIRED_CALL_STATES),
        ("contract", REQUIRED_CONTRACTS),
        ("event", REQUIRED_EVENTS),
        ("failure", REQUIRED_FAILURES),
        ("ownership boundary", REQUIRED_OWNERSHIP),
        ("fault scenario", REQUIRED_FAULTS),
    ]:
        for value in values:
            if value not in formal:
                errors.append(f"Model Gateway Contract Freeze missing {collection_name}: {value}")

    requirements = [int(value) for value in re.findall(r"ARCH-MODEL-CF-(\d{3})", formal)]
    controls = [int(value) for value in re.findall(r"RC-MODEL-CF-(\d{3})", formal)]
    expected = list(range(1, 21))
    if sorted(requirements) != expected:
        errors.append("Contract Freeze must define ARCH-MODEL-CF-001 through 020 exactly once")
    if sorted(controls) != expected:
        errors.append("Contract Freeze must define RC-MODEL-CF-001 through 020 exactly once")
    for requirement_id in expected:
        for suffix in ["UT", "IT", "FT", "E2E"]:
            test_id = f"MODEL-CF-{requirement_id:03d}-{suffix}"
            if formal.count(test_id) != 1:
                errors.append(f"Contract Freeze requirement must map test exactly once: {test_id}")
        evidence_id = f"EV-MODEL-CF-{requirement_id:03d}"
        if formal.count(evidence_id) != 1:
            errors.append(f"Contract Freeze requirement must map evidence exactly once: {evidence_id}")

    for claim in FORBIDDEN_CLAIMS:
        if claim in formal:
            errors.append(f"Contract Freeze contains unsupported implementation claim: {claim}")

    for index_path in [DOCS_INDEX, AGENT_INDEX]:
        content = _read(index_path)
        for term in [
            "04-model-gateway-contract-freeze.md",
            "verify_model_gateway_contract_freeze.py",
            "test_model_gateway_contract_freeze.py",
        ]:
            if term not in content:
                errors.append(f"{index_path.relative_to(REPO_ROOT)} missing Contract Freeze route: {term}")

    workflow = _read(WORKFLOW)
    for term in [
        "04-model-gateway-contract-freeze.md",
        "verify_model_gateway_contract_freeze.py",
        "test_model_gateway_contract_freeze.py",
    ]:
        if term not in workflow:
            errors.append(f"Model Gateway workflow missing Contract Freeze validation: {term}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Model Gateway Contract Freeze verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
