from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
FORMAL = ROOT / "docs/modules/04-model-gateway.md"
MIRROR = ROOT / ".agent/modules/04-model-gateway.md"
DOCS_INDEX = ROOT / "docs/modules/README.md"
AGENT_INDEX = ROOT / ".agent/modules/README.md"
SYSTEM = ROOT / ".agent/system.yaml"
WORKFLOW = ROOT / ".github/workflows/model-gateway-target-docs.yml"
ADR = ROOT / "docs/decisions/0003-wave1-cross-module-contract-freeze.md"

REMOVED = [
    "docs/modules/04-model-gateway-contract-freeze.md",
    ".agent/modules/04-model-gateway-contract-freeze.md",
    "docs/modules/04-model-gateway-operations-conformance.md",
    ".agent/modules/04-model-gateway-operations-conformance.md",
    "tools/scripts/verify_model_gateway_contract_freeze.py",
    "tools/scripts/verify_model_gateway_operations_conformance.py",
    "tests/repo/test_model_gateway_contract_freeze.py",
    "tests/repo/test_model_gateway_operations_conformance.py",
]

PARTS = [
    "# Part I：定位、问题与跨模块模型使用地图",
    "# Part II：概念架构、Role、Operation 与配置模型",
    "# Part III：完整运行流程与 Operation 协议",
    "# Part IV：聚合、状态机与生命周期",
    "# Part V：故障、恢复、幂等、安全与事件",
    "# Part VI：多租户、缓存、运维、SLO 与兼容",
    "# Part VII：目标实现规格",
    "# Part VIII：Requirement、测试与完成证据",
]

ROLES = [
    "TASK_ANALYZER", "PLANNER", "PLAN_REPAIR", "EXECUTOR_FAST",
    "EXECUTOR_REASONING", "QUERY_REWRITER", "EXTRACTOR", "CRITIC",
    "SYNTHESIZER", "FINAL_CRITIC", "TOOL_CALL",
]

OPERATIONS = [
    "TEXT_GENERATION", "STRUCTURED_GENERATION", "EMBEDDING", "RERANK",
    "VISION_EXTRACTION", "TRANSCRIPTION", "CLASSIFICATION", "JUDGE",
]

REQUIRED_TERMS = [
    "唯一的正式 Target 架构主设计",
    "docs/decisions/0003-wave1-cross-module-contract-freeze.md",
    "accepted-target",
    "十一个模块的模型使用地图",
    "VLM / 多模态模型 OCR",
    "Chunk/Query Embedding",
    "Context Compression",
    "Memory Extraction",
    "Prompt Injection",
    "Judge 调用也必须经过 Gateway",
    "CrossModuleEnvelopeV1",
    "EffectiveSecurityEpochRefV1",
    "CredentialVersionRefV1",
    "ProviderConnectionRequestV1",
    "ModelQuotaReservationV1",
    "ModelUsageReceiptV1",
    "ModelCancellationReceiptV1",
    "ModelRoleDefinition",
    "ModelOperationKind",
    "ModelCapabilityProfile",
    "PromptArtifact",
    "PromptExecutionBinding",
    "ModelGatewayConfigSnapshot",
    "ProviderAdapterContract",
    "ProviderAdapterResult",
    "ModelFeasibilityAssessment",
    "ModelCallRequest",
    "ModelRoutingDecision",
    "EmbeddingRequest",
    "EmbeddingResult",
    "RerankRequest",
    "RerankResult",
    "VisionExtractionRequest",
    "VisionExtractionResult",
    "JudgeRequest",
    "JudgeResult",
    "ModelCallAttempt",
    "ModelResponseSelection",
    "AdapterConformanceProfile",
    "TenantAdmissionPolicy",
    "LoadSheddingDecision",
    "GatewayResultCachePolicy",
    "ModelCacheReuseReceipt",
    "ModelGatewayOperationalCommand",
    "ModelDataRetentionBinding",
    "ModelGatewayServiceLevelProfile",
    "GatewayReadinessSnapshot",
    "ModelGatewayCompatibilityEntry",
    "ModelRoutingExperimentAssignment",
    "ModelFailure",
    "# 29. ModelCallAttempt 状态机",
    "# 31. Streaming Session 状态机",
    "# 32. Structured Output 状态机",
    "# 33. ModelQuotaReservationV1 状态机",
    "# 34. ModelUsageReceiptV1 生命周期",
    "# 36. Adapter Conformance 生命周期",
    "# 37. Config Activation 状态机",
    "# 39. Admission Queue 状态机",
    "# 40. Overload 状态机",
    "# 41. Result Cache 状态机",
    "# 42. Deletion 状态机",
    "Agent Core 拥有最终 `StepFeasibilityDecision`",
    "Gateway 不得激活 PlanVersion",
    "Gateway 不直接修改 AgentRun 终态",
    "Gateway 不得自行扩大 Run Budget",
    "Gateway 不执行外部副作用",
    "模型不能直接写长期 Memory",
    "最终 Security Decision 必须由 Security 模块",
    "模型输出永远是 `Proposal`、`Candidate`、`Score` 或 `Model Result`",
    "不得直接批准、激活、发布或提交长期事实",
    "Mock-only、单次成功调用或文档完成不能证明生产 Readiness",
    "src/backend/zuno/platform/model_gateway/",
    "model_calls",
    "model_routing_decisions",
    "model_call_attempts",
    "model_response_selections",
    "model_embedding_batches",
    "model_rerank_batches",
    "model_vision_results",
    "model_stream_sessions",
    "model_usage_receipts",
    "model_quota_reservations",
    "model_admission_queue_items",
    "model_provider_health_snapshots",
    "model_circuit_breaker_states",
    "model_reconciliation_records",
    "model_result_validity_records",
    "model_cache_reuse_receipts",
    "model_operational_commands",
    "model_data_deletion_records",
    "model_readiness_snapshots",
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
    "Config Activation Failure",
    "Cache Isolation Mismatch",
    "Deletion Partial Failure",
    "Judge Unavailable",
    "Overload",
]

FORBIDDEN_CLAIMS = [
    "status: production-ready",
    "status: implementation_available",
    "所有真实模型调用已经统一进入 Gateway",
    "Model Gateway 已 production ready",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []
    for path in [FORMAL, MIRROR, DOCS_INDEX, AGENT_INDEX, SYSTEM, WORKFLOW, ADR]:
        if not path.exists():
            errors.append(f"missing required path: {path.relative_to(ROOT)}")
    for relative in REMOVED:
        if (ROOT / relative).exists():
            errors.append(f"obsolete split Gateway artifact still exists: {relative}")
    if errors:
        return errors

    doc = read(FORMAL)
    if FORMAL.read_bytes() != MIRROR.read_bytes():
        errors.append("Gateway formal document and Agent mirror must be byte-identical")

    for term in [
        "status: normative-target-module-architecture",
        "dependency_baseline_sha: `140128fa7352094cac5a7a58f247090d0b451753`",
        "confirmed_wave1_contract_sha: `849820d2c52d36abebee8c3d4a974bf035524e0a`",
        *ROLES,
        *OPERATIONS,
        *REQUIRED_TERMS,
    ]:
        if term not in doc:
            errors.append(f"Gateway document missing required term: {term}")

    if "src/backend/zuno/model_gateway/" in doc:
        errors.append("Gateway document proposes forbidden top-level zuno/model_gateway package")

    positions: list[int] = []
    for part in PARTS:
        if doc.count(part) != 1:
            errors.append(f"Gateway document must contain part exactly once: {part}")
        else:
            positions.append(doc.index(part))
    if positions != sorted(positions):
        errors.append("Gateway document parts are not in canonical order")

    for claim in FORBIDDEN_CLAIMS:
        if claim in doc:
            errors.append(f"Gateway Target document contains unsupported Current claim: {claim}")

    expected = list(range(1, 89))
    requirements = [int(value) for value in re.findall(r"ARCH-MODEL-(\d{3})", doc)]
    controls = [int(value) for value in re.findall(r"RC-MODEL-(\d{3})", doc)]
    if sorted(requirements) != expected:
        errors.append("Gateway document must define ARCH-MODEL-001 through ARCH-MODEL-088 exactly once")
    if sorted(controls) != expected:
        errors.append("Gateway document must define RC-MODEL-001 through RC-MODEL-088 exactly once")
    for number in expected:
        for suffix in ["UT", "IT", "FT", "E2E"]:
            test_id = f"MODEL-{number:03d}-{suffix}"
            if doc.count(test_id) != 1:
                errors.append(f"Gateway requirement must map test exactly once: {test_id}")
        evidence_id = f"EV-MODEL-{number:03d}"
        if doc.count(evidence_id) != 1:
            errors.append(f"Gateway requirement must map evidence exactly once: {evidence_id}")

    for path in [DOCS_INDEX, AGENT_INDEX]:
        content = read(path)
        for term in ["04-model-gateway.md", "单一完整 Target", "verify_model_gateway_target_protocols.py"]:
            if term not in content:
                errors.append(f"{path.relative_to(ROOT)} missing unified Gateway route: {term}")
        for removed in [Path(item).name for item in REMOVED]:
            if removed in content:
                errors.append(f"{path.relative_to(ROOT)} references removed Gateway artifact: {removed}")

    system = read(SYSTEM)
    for term in [
        'formal: "docs/modules/04-model-gateway.md"',
        'mirror: ".agent/modules/04-model-gateway.md"',
        'verifier: "python tools/scripts/verify_model_gateway_target_protocols.py"',
        'test: "pytest -q tests/repo/test_model_gateway_target_protocols.py -p no:cacheprovider"',
    ]:
        if term not in system:
            errors.append(f".agent/system.yaml missing unified Gateway registration: {term}")
    for removed in [Path(item).name for item in REMOVED]:
        if removed in system:
            errors.append(f".agent/system.yaml references removed Gateway artifact: {removed}")

    workflow = read(WORKFLOW)
    for term in [
        "Model Gateway Target Documentation",
        "verify_model_gateway_target_protocols.py",
        "test_model_gateway_target_protocols.py",
        "verify_model_gateway_boundaries.py",
        "verify_docs_entrypoints.py",
        "verify_agent_system.py",
        "verify_doc_boundaries.py",
    ]:
        if term not in workflow:
            errors.append(f"Gateway workflow missing validation step: {term}")
    for removed in [Path(item).name for item in REMOVED]:
        if removed in workflow:
            errors.append(f"Gateway workflow references removed artifact: {removed}")

    adr = read(ADR)
    for term in [
        "status: accepted-target",
        "CrossModuleEnvelopeV1",
        "EffectiveSecurityEpochRefV1",
        "CredentialVersionRefV1",
        "ProviderConnectionRequestV1",
        "ModelQuotaReservationV1",
        "ModelUsageReceiptV1",
        "ModelCancellationReceiptV1",
        "src/backend/zuno/platform/",
        "platform/model_gateway/**",
    ]:
        if term not in adr:
            errors.append(f"accepted Wave 1 ADR missing expected Gateway contract or ownership term: {term}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Unified Model Gateway target architecture verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
