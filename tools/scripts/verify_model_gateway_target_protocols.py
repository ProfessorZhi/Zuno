from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/04-model-gateway.md"
MIRROR = REPO_ROOT / ".agent/modules/04-model-gateway.md"
DOCS_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_INDEX = REPO_ROOT / ".agent/modules/README.md"
SYSTEM_YAML = REPO_ROOT / ".agent/system.yaml"
WORKFLOW = REPO_ROOT / ".github/workflows/model-gateway-target-docs.yml"

REQUIRED_PARTS = [
    "# Part I：问题、目标与 Ownership",
    "# Part II：概念架构与 Provider-neutral Contract",
    "# Part III：完整调用流程、Routing、Fallback 与 Escalation",
    "# Part IV：规范性状态机",
    "# Part V：Timeout、Cancellation、Usage、Quota、Health 与 Security",
    "# Part VI：Structured Output、Streaming、Failure 与 Observability",
    "# Part VII：Typed Contract、Storage、代码目录与跨模块 Proposal",
    "# Part VIII：Requirement Registry、测试与完成证据",
]

REQUIRED_ROLES = [
    "TASK_ANALYZER",
    "PLANNER",
    "PLAN_REPAIR",
    "EXECUTOR_FAST",
    "EXECUTOR_REASONING",
    "QUERY_REWRITER",
    "EXTRACTOR",
    "CRITIC",
    "SYNTHESIZER",
    "FINAL_CRITIC",
    "TOOL_CALL",
]

REQUIRED_CONTRACTS = [
    "ModelRoleDefinition",
    "ProviderDefinition",
    "ModelDefinition",
    "ModelCapabilityProfile",
    "ModelAvailabilitySnapshot",
    "ModelCallRequest",
    "ModelRoutingDecision",
    "ModelCallAttempt",
    "ModelResponse",
    "ModelStreamChunk",
    "StructuredOutputResult",
    "UsageReceipt",
    "RateLimitState",
    "QuotaReservation",
    "ProviderHealth",
    "CircuitBreakerState",
    "PromptBinding",
    "ModelFailure",
    "ModelFeasibilityAssessment",
]

REQUIRED_STATE_MACHINES = [
    "## 16. ModelCallAttempt 状态机",
    "## 17. ProviderHealth 状态机",
    "## 18. CircuitBreaker 状态机",
    "## 19. QuotaReservation 状态机",
    "## 20. Streaming Session 状态机",
    "## 21. Structured Output Repair 状态机",
]

REQUIRED_FAULTS = [
    "Provider Timeout",
    "Rate Limit",
    "Malformed Structured Output",
    "Stream Disconnect",
    "Usage Receipt Delayed",
    "Provider Success but Response Lost",
    "Circuit Breaker Transition",
    "Fallback Exhausted",
    "Security Revocation",
    "Quota Race",
    "Credential Rotation",
    "Provider SDK Error Mapping",
]

REQUIRED_TABLES = [
    "model_role_definitions",
    "model_provider_definitions",
    "model_definitions",
    "model_capability_profiles",
    "model_availability_snapshots",
    "model_prompt_bindings",
    "model_calls",
    "model_routing_decisions",
    "model_call_attempts",
    "model_responses",
    "model_stream_sessions",
    "model_stream_chunks",
    "model_structured_output_results",
    "model_usage_receipts",
    "model_rate_limit_states",
    "model_quota_reservations",
    "model_provider_health_snapshots",
    "model_circuit_breaker_states",
    "model_failure_records",
    "model_reconciliation_records",
    "model_result_validity_records",
]

REQUIRED_BOUNDARIES = [
    "Agent Core 拥有最终 `StepFeasibilityDecision`",
    "Gateway 不得激活 PlanVersion",
    "Gateway 不直接修改 AgentRun 终态",
    "Gateway 不得自行扩大 Run Budget",
    "模型输出永远是 `Proposal`、`Candidate` 或 `Model Result`",
    "Parallel Proposal",
    "ModelSecurityDecision",
    "SecretRef / CredentialVersionRef",
    "ModelCall Trace Schema",
]

FORBIDDEN_CLAIMS = [
    "status: production-ready",
    "status: implementation_available",
    "Model Gateway 已 production ready",
    "所有真实模型调用已经统一进入 Gateway",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []
    required_paths = [FORMAL, MIRROR, DOCS_INDEX, AGENT_INDEX, SYSTEM_YAML, WORKFLOW]
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing Model Gateway target path: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    formal = _read(FORMAL)
    if FORMAL.read_bytes() != MIRROR.read_bytes():
        errors.append("Model Gateway formal document and mirror must be byte-identical")

    if "status: normative-target-module-architecture" not in formal:
        errors.append("Model Gateway document must declare normative-target-module-architecture")
    if "dependency_baseline_sha: `729e439e29deadc101c5687fc47125104e62e2c1`" not in formal:
        errors.append("Model Gateway document must pin the reviewed dependency baseline SHA")

    positions: list[int] = []
    for part in REQUIRED_PARTS:
        if formal.count(part) != 1:
            errors.append(f"Model Gateway document must contain part exactly once: {part}")
        else:
            positions.append(formal.index(part))
    if positions and positions != sorted(positions):
        errors.append("Model Gateway document parts are not in canonical order I through VIII")

    for role in REQUIRED_ROLES:
        if role not in formal:
            errors.append(f"Model Gateway document missing model role: {role}")
    for contract in REQUIRED_CONTRACTS:
        if contract not in formal:
            errors.append(f"Model Gateway document missing required contract: {contract}")
    for machine in REQUIRED_STATE_MACHINES:
        if machine not in formal:
            errors.append(f"Model Gateway document missing state machine: {machine}")
    for fault in REQUIRED_FAULTS:
        if fault not in formal:
            errors.append(f"Model Gateway document missing required fault test: {fault}")
    for table in REQUIRED_TABLES:
        if table not in formal:
            errors.append(f"Model Gateway document missing storage mapping: {table}")
    for boundary in REQUIRED_BOUNDARIES:
        if boundary not in formal:
            errors.append(f"Model Gateway document missing ownership boundary: {boundary}")
    for claim in FORBIDDEN_CLAIMS:
        if claim in formal:
            errors.append(f"Model Gateway target document contains unsupported Current claim: {claim}")

    requirements = [int(value) for value in re.findall(r"ARCH-MODEL-(\d{3})", formal)]
    controls = [int(value) for value in re.findall(r"RC-MODEL-(\d{3})", formal)]
    expected = list(range(1, 41))
    if sorted(requirements) != expected:
        errors.append("Model Gateway document must define ARCH-MODEL-001 through ARCH-MODEL-040 exactly once")
    if sorted(controls) != expected:
        errors.append("Model Gateway document must define RC-MODEL-001 through RC-MODEL-040 exactly once")

    for requirement_id in expected:
        for suffix in ["UT", "IT", "FT", "E2E"]:
            test_id = f"MODEL-{requirement_id:03d}-{suffix}"
            if formal.count(test_id) != 1:
                errors.append(f"Model Gateway requirement must map test exactly once: {test_id}")
        evidence_id = f"EV-MODEL-{requirement_id:03d}"
        if formal.count(evidence_id) != 1:
            errors.append(f"Model Gateway requirement must map evidence exactly once: {evidence_id}")

    for index_path in [DOCS_INDEX, AGENT_INDEX]:
        content = _read(index_path)
        if "04-model-gateway.md" not in content:
            errors.append(f"{index_path.relative_to(REPO_ROOT)} does not route to Model Gateway target document")
        if "verify_model_gateway_target_protocols.py" not in content:
            errors.append(f"{index_path.relative_to(REPO_ROOT)} does not list Model Gateway verifier")

    system = _read(SYSTEM_YAML)
    for path_text in [
        "docs/modules/04-model-gateway.md",
        ".agent/modules/04-model-gateway.md",
        "python tools/scripts/verify_model_gateway_target_protocols.py",
        "pytest -q tests/repo/test_model_gateway_target_protocols.py -p no:cacheprovider",
    ]:
        if path_text not in system:
            errors.append(f".agent/system.yaml missing Model Gateway route or verification: {path_text}")

    workflow = _read(WORKFLOW)
    for workflow_term in [
        "Model Gateway Target Documentation",
        "verify_model_gateway_target_protocols.py",
        "test_model_gateway_target_protocols.py",
        "verify_model_gateway_boundaries.py",
    ]:
        if workflow_term not in workflow:
            errors.append(f"Model Gateway workflow missing validation step: {workflow_term}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Model Gateway target architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
