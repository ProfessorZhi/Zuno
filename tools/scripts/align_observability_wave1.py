from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAIN_DOC = ROOT / "docs/modules/10-observability-eval.md"
MAIN_MIRROR = ROOT / ".agent/modules/10-observability-eval.md"
RAG_DOC = ROOT / "docs/modules/10-observability-eval-rag-agent-evaluation.md"
RAG_MIRROR = ROOT / ".agent/modules/10-observability-eval-rag-agent-evaluation.md"
ADR = ROOT / "docs/decisions/0003-wave1-cross-module-contract-freeze.md"
REGISTRY = ROOT / "docs/governance/wave1-cross-module-contract-registry.md"
MARKER = "## 17.1 Wave 1 Canonical Contract Alignment"
RAG_MARKER = "## 17.1 Wave 1 Metric 与 Receipt 对齐"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        print(f"SKIP {label}: already aligned")
        return text
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, got {count}")
    return text.replace(old, new, 1)


def align_main(text: str) -> str:
    if MARKER in text:
        return text
    section = r'''
## 17.1 Wave 1 Canonical Contract Alignment

本节在跨模块字段、Owner、Receipt、Failure Namespace 与恢复责任上优先于本文早期说明；共享事实源为 `docs/decisions/0003-wave1-cross-module-contract-freeze.md` 与 `docs/governance/wave1-cross-module-contract-registry.md`，状态为 `CONFIRMED_TARGET`。这些决议仍是 Target，不代表 Runtime 已实现。

### 服务端权威产品边界

```text
Web / Desktop Frontend
→ Server-hosted Product API
→ Backend logical modules
→ Infrastructure primitives
```

前端只展示账号、身份、组织、权限、审批、Trace、Eval 和 Evidence 投影。Principal、Tenant、Workspace、Policy、Security Epoch、AgentRun、Usage、Audit 与 Eval 事实均由服务端后端提交；Developer / CI Local Adapter 不构成多用户产品部署 Target。

### CrossModuleEnvelopeV1 与 TelemetryEnvelopeV1

所有跨模块消息先使用共享 `CrossModuleEnvelopeV1`：

```text
contract_name
contract_version
contract_bundle_version
message_id
producer_module
consumer_module
tenant_id
workspace_id
run_id
step_run_id
correlation_id
causation_id
idempotency_key
aggregate_type
aggregate_id
aggregate_version
expected_generation
effective_security_epoch_ref
effective_security_epoch_hash
principal_context_ref
security_context_ref
authorization_decision_ref
deadline_at
trace_id
data_classification
redaction_decision_ref
audit_requirement_ref
occurred_at
created_at
payload
payload_ref
payload_hash
payload_schema_hash
```

本文早期 `TelemetryEnvelope` 字段表是 Observability payload profile，而不是第二套跨模块 Envelope。正式 wire contract 命名为 `TelemetryEnvelopeV1`，放入 `CrossModuleEnvelopeV1.payload` 或 `payload_ref`，并补充 producer sequence、stream key、category、observed/ingested time、retention 与 projection metadata。未知 Contract/Enum、Hash 不一致、Scope 缺失或 stale epoch 使用稳定失败码：

```text
OBS_ENVELOPE_SCHEMA_UNSUPPORTED
OBS_INGEST_GAP
```

### Audit 三层事实

```text
SecurityAuditRequirementV1
    Owner: Security

AuditDurabilityRequirement
AuditPersistenceReceiptV1
    Owner: Infrastructure execution fact

AuditEvent
    Owner: Observability accepted immutable fact
```

`AuditEvent` 必须引用 source event、`SecurityAuditRequirementV1` 和 `AuditPersistenceReceiptV1`。Mandatory Audit 不能由 Observability 降级；接受失败使用 `OBS_AUDIT_ACCEPTANCE_FAILED`。

```text
AuditPersistenceReceipt != accepted AuditEvent
AuditEvent accepted != source-domain success
ExternalSinkDelivery != source-domain success
StructuredLog != AuditEvent
```

外部交付失败使用 `OBS_EXTERNAL_SINK_DELIVERY_FAILED`，不得反向覆盖 Security、Agent、Model 或 Tool 领域事实。

### Model、Security 与 Infrastructure 对齐

Observability 消费但不拥有：`ModelCallAttempt`、`RoutingDecision`、`UsageReceipt`、`ProviderHealth`、`StructuredOutputFailure`、`EffectiveSecurityEpochRefV1`、`RedactionDecision`、`DataClassification`、`ExternalSinkPolicy`、`AuditRetentionPolicy`、`BreakGlassDecision`。

Infrastructure 提供 Trace Store、Append-only Ingest、Outbox-Inbox、Eval Job Queue、Backup/Restore、Retention 与 Legal Hold primitive；Observability 拥有其 Projection、Eval、Evidence、Benchmark、Release Gate 和 accepted Audit 语义。

### Recovery 与 Receipt 规则

```text
Producer domain commit
→ transactional Outbox
→ Infrastructure AuditPersistenceReceipt（适用时）
→ Observability ingest/dedup
→ accepted AuditEvent 或 rebuildable Projection
→ ExternalSinkDelivery attempt
```

Queue ACK、Object Store Receipt、Transport Receipt、Audit Persistence、External Sink Delivery 都只能证明各自 Owner 的物理事实，不得冒充 ModelCall、Tool Effect、AgentRun、Publication 或 Eval 成功。

'''
    return replace_once(text, "## 18. Requirement Enforcement Matrix", section + "## 18. Requirement Enforcement Matrix", "main alignment section")


def align_rag(text: str) -> str:
    if RAG_MARKER in text:
        return text
    section = r'''
## 17.1 Wave 1 Metric 与 Receipt 对齐

RAG Core Five 与 Agent Efficiency 使用 Wave 1 已确认的源事实：Model 调用成本读取 Model Gateway `UsageReceipt` 的 `ESTIMATED / OBSERVED / SETTLED / CORRECTION` 版本；Security 范围读取 `effective_security_epoch_ref/hash`；运行对象引用 Agent Core `PlanVersion / StepRun / ActionRun / RunOutcome / BudgetSettlement`。Observability 不重定义这些领域事实。

现有 Release Gate 阈值继续保留；RAG Core Five 是新增一级质量维度，不自动替换、降低或重新解释 Recall、Citation、Unsupported Claim 等现有门槛。阈值变化必须由独立 Policy/ADR 完成。Core Five 任一必需输入 `BLOCKED / UNAVAILABLE / INCOMPARABLE` 时，不得通过单一效率分或成本下降补偿。

Judge 调用必须经过 Model Gateway，具有独立 ModelCallAttempt、UsageReceipt、Security、Budget 和 Trace；模型自评不能单独证明自身质量。Agent Efficiency 保持质量优先的向量，不选择不透明综合分。

'''
    return text.rstrip() + "\n\n" + section


def main() -> None:
    main_doc = align_main(MAIN_DOC.read_text(encoding="utf-8"))
    MAIN_DOC.write_text(main_doc.rstrip() + "\n", encoding="utf-8", newline="\n")
    MAIN_MIRROR.write_text(main_doc.rstrip() + "\n", encoding="utf-8", newline="\n")

    rag_doc = align_rag(RAG_DOC.read_text(encoding="utf-8"))
    RAG_DOC.write_text(rag_doc.rstrip() + "\n", encoding="utf-8", newline="\n")
    RAG_MIRROR.write_text(rag_doc.rstrip() + "\n", encoding="utf-8", newline="\n")

    adr = ADR.read_text(encoding="utf-8")
    adr = replace_once(adr, "status: accepted-target-pending-merge", "status: accepted-target", "ADR status")
    adr = replace_once(
        adr,
        "> 本 ADR 是 Target 设计决议，不是 Current 或实现证据。它只有合并到 `main` 后才成为正式共享 Target Contract；合并前仍是 Draft PR 中已冻结的设计决议。",
        "> 本 ADR 已合并到 `main`，是 Wave 1 正式共享 Target Contract；它仍不是 Current、Runtime 实现或生产证据。",
        "ADR activation note",
    )
    ADR.write_text(adr, encoding="utf-8", newline="\n")

    registry = REGISTRY.read_text(encoding="utf-8")
    registry = registry.replace("status: field-frozen-pending-merge", "status: confirmed-target")
    registry = registry.replace("`FIELD_FROZEN_PENDING_MERGE`", "`CONFIRMED_TARGET`")
    registry = registry.replace("FIELD_FROZEN_PENDING_MERGE", "CONFIRMED_TARGET")
    registry = registry.replace(
        "> 本文件是 Wave 1 跨模块共享 Contract 的合并前 Registry。字段、Owner、Failure Namespace 和恢复责任已完成集中审计并冻结；由于本文件仍位于未合并 Draft PR，当前状态只能是 `CONFIRMED_TARGET`。PR #17 合并后才提升为 `CONFIRMED_TARGET`，仍不代表 Runtime 已实现或成为 Current。",
        "> 本文件已随 PR #17 合并到 `main`，字段、Owner、Failure Namespace 和恢复责任为 `CONFIRMED_TARGET`；仍不代表 Runtime 已实现、质量已证明或成为 Current。",
    )
    REGISTRY.write_text(registry, encoding="utf-8", newline="\n")

    print("Wave 1 Observability alignment and governance activation applied.")


if __name__ == "__main__":
    main()
