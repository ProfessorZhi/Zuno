from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FORMAL = REPO_ROOT / "docs/modules/04-model-gateway-operations-conformance.md"
MIRROR = REPO_ROOT / ".agent/modules/04-model-gateway-operations-conformance.md"
PARENT = REPO_ROOT / "docs/modules/04-model-gateway.md"
CONTRACT_FREEZE = REPO_ROOT / "docs/modules/04-model-gateway-contract-freeze.md"
DOCS_INDEX = REPO_ROOT / "docs/modules/README.md"
AGENT_INDEX = REPO_ROOT / ".agent/modules/README.md"
SYSTEM_YAML = REPO_ROOT / ".agent/system.yaml"
WORKFLOW = REPO_ROOT / ".github/workflows/model-gateway-target-docs.yml"

REQUIRED_SECTIONS = [
    "## 0. 文档边界与规范优先级",
    "## 1. 四个运行平面",
    "## 2. Provider Adapter Contract",
    "## 3. Adapter Conformance",
    "## 4. 配置快照与激活生命周期",
    "## 5. Provider 与 Model 生命周期",
    "## 6. 多租户隔离与公平 Admission",
    "## 7. 过载、背压与降级",
    "## 8. Cache 与结果复用",
    "## 9. Operations Command 与人工干预",
    "## 10. Retention、Deletion 与 Legal Hold",
    "## 11. SLI、SLO、Readiness 与 Degradation",
    "## 12. 兼容性、SDK 与 Provider API 升级",
    "## 13. Eval、Judge 与实验治理",
    "## 14. 目标存储扩展",
    "## 15. 目标代码边界扩展",
    "## 16. Operations Failure Decision Matrix",
    "## 17. Requirement Registry",
    "## 18. 强制 Fault / Recovery 场景",
    "## 19. Target 到 Current 的证据",
]

REQUIRED_CONTRACTS = [
    "ProviderAdapterContract",
    "ProviderAdapterResult",
    "AdapterConformanceProfile",
    "ModelGatewayConfigSnapshot",
    "GatewayConfigActivation",
    "ModelLifecycleRecord",
    "TenantAdmissionPolicy",
    "AdmissionQueueItem",
    "LoadSheddingDecision",
    "GatewayResultCachePolicy",
    "ModelCacheReuseReceipt",
    "ModelGatewayOperationalCommand",
    "ModelDataRetentionBinding",
    "ModelDataDeletionRecord",
    "ModelGatewayServiceLevelProfile",
    "GatewayReadinessSnapshot",
    "ModelGatewayCompatibilityEntry",
    "ModelRoutingExperimentAssignment",
]

REQUIRED_PLANES = [
    "Execution Plane",
    "Control Plane",
    "Operations Plane",
    "Evidence Plane",
]

REQUIRED_STATES = [
    "CONFORMANT_WITH_LIMITATIONS",
    "CANARY",
    "ROLLED_BACK",
    "DEPRECATED",
    "DRAINING",
    "SHEDDING",
    "BLOCKED_BY_HOLD",
    "NOT_READY",
    "CANARY_ONLY",
]

REQUIRED_TABLES = [
    "model_provider_adapters",
    "model_adapter_conformance_profiles",
    "model_adapter_conformance_runs",
    "model_gateway_config_snapshots",
    "model_gateway_config_activations",
    "model_lifecycle_records",
    "model_tenant_admission_policies",
    "model_admission_queue_items",
    "model_load_shedding_decisions",
    "model_result_cache_policies",
    "model_cache_reuse_receipts",
    "model_operational_commands",
    "model_data_retention_bindings",
    "model_data_deletion_records",
    "model_service_level_profiles",
    "model_readiness_snapshots",
    "model_compatibility_entries",
    "model_routing_experiment_assignments",
]

REQUIRED_BOUNDARIES = [
    "不要求拆微服务",
    "不允许直接更新数据库行",
    "Gateway Result Cache",
    "默认关闭",
    "跨租户 cache sharing 默认禁止",
    "运维命令是 Command，不是事实成功",
    "Legal Hold 优先于 purge",
    "无证据不得默认 READY",
    "不能因为属于 Eval 就直接构造 Provider SDK",
    "模型 A 判断模型 A 很好",
]

REQUIRED_FAULTS = [
    "SDK hidden retry creates extra provider charge",
    "Config activation CAS race",
    "Security emergency disables a model mid-call",
    "Noisy tenant saturates provider concurrency",
    "Queued call expires before admission",
    "Cross-tenant result-cache key collision attempt",
    "Legal Hold blocks prompt deletion",
    "SDK upgrade breaks stream event ordering",
    "Judge model exhibits position bias",
    "Drain deadline expires with UNKNOWN attempts",
]

FORBIDDEN_CLAIMS = [
    "status: production-ready",
    "status: implementation_available",
    "Model Gateway 已 production ready",
    "Operations 已经实现",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify() -> list[str]:
    errors: list[str] = []
    required_paths = [
        FORMAL,
        MIRROR,
        PARENT,
        CONTRACT_FREEZE,
        DOCS_INDEX,
        AGENT_INDEX,
        SYSTEM_YAML,
        WORKFLOW,
    ]
    for path in required_paths:
        if not path.exists():
            errors.append(f"missing Model Gateway Operations path: {path.relative_to(REPO_ROOT)}")
    if errors:
        return errors

    formal = _read(FORMAL)
    if FORMAL.read_bytes() != MIRROR.read_bytes():
        errors.append("Model Gateway Operations formal document and mirror must be byte-identical")

    for term in [
        "status: normative-target-module-addendum",
        "parent_document: `docs/modules/04-model-gateway.md`",
        "companion_document: `docs/modules/04-model-gateway-contract-freeze.md`",
        "dependency_baseline_sha: `729e439e29deadc101c5687fc47125104e62e2c1`",
        "不包含实施 Program",
    ]:
        if term not in formal:
            errors.append(f"Model Gateway Operations missing metadata or boundary: {term}")

    positions: list[int] = []
    for section in REQUIRED_SECTIONS:
        if formal.count(section) != 1:
            errors.append(f"Model Gateway Operations must contain section exactly once: {section}")
        else:
            positions.append(formal.index(section))
    if positions and positions != sorted(positions):
        errors.append("Model Gateway Operations sections are not in canonical order")

    for label, values in [
        ("plane", REQUIRED_PLANES),
        ("contract", REQUIRED_CONTRACTS),
        ("state", REQUIRED_STATES),
        ("table", REQUIRED_TABLES),
        ("boundary", REQUIRED_BOUNDARIES),
        ("fault", REQUIRED_FAULTS),
    ]:
        for value in values:
            if value not in formal:
                errors.append(f"Model Gateway Operations missing {label}: {value}")

    expected = list(range(1, 29))
    requirements = [int(value) for value in re.findall(r"ARCH-MODEL-OPS-(\d{3})", formal)]
    controls = [int(value) for value in re.findall(r"RC-MODEL-OPS-(\d{3})", formal)]
    if sorted(requirements) != expected:
        errors.append("Operations addendum must define ARCH-MODEL-OPS-001 through 028 exactly once")
    if sorted(controls) != expected:
        errors.append("Operations addendum must define RC-MODEL-OPS-001 through 028 exactly once")
    for requirement_id in expected:
        for suffix in ["UT", "IT", "FT", "E2E"]:
            test_id = f"MODEL-OPS-{requirement_id:03d}-{suffix}"
            if formal.count(test_id) != 1:
                errors.append(f"Operations requirement must map test exactly once: {test_id}")
        evidence_id = f"EV-MODEL-OPS-{requirement_id:03d}"
        if formal.count(evidence_id) != 1:
            errors.append(f"Operations requirement must map evidence exactly once: {evidence_id}")

    for claim in FORBIDDEN_CLAIMS:
        if claim in formal:
            errors.append(f"Operations addendum contains unsupported implementation claim: {claim}")

    for index_path in [DOCS_INDEX, AGENT_INDEX]:
        content = _read(index_path)
        for term in [
            "04-model-gateway-operations-conformance.md",
            "verify_model_gateway_operations_conformance.py",
            "test_model_gateway_operations_conformance.py",
        ]:
            if term not in content:
                errors.append(f"{index_path.relative_to(REPO_ROOT)} missing Operations route: {term}")

    system = _read(SYSTEM_YAML)
    for term in [
        "docs/modules/04-model-gateway-operations-conformance.md",
        ".agent/modules/04-model-gateway-operations-conformance.md",
        "verify_model_gateway_operations_conformance.py",
        "test_model_gateway_operations_conformance.py",
    ]:
        if term not in system:
            errors.append(f".agent/system.yaml missing Model Gateway Operations route: {term}")

    workflow = _read(WORKFLOW)
    for term in [
        "04-model-gateway-operations-conformance.md",
        "verify_model_gateway_operations_conformance.py",
        "test_model_gateway_operations_conformance.py",
    ]:
        if term not in workflow:
            errors.append(f"Model Gateway workflow missing Operations validation: {term}")

    return errors


def main() -> int:
    errors = verify()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Model Gateway Operations and Conformance verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
