from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FORMAL = ROOT / "docs/modules/10-observability-eval.md"
MIRROR = ROOT / ".agent/modules/10-observability-eval.md"
RAG_FORMAL = ROOT / "docs/modules/10-observability-eval-rag-agent-evaluation.md"
RAG_MIRROR = ROOT / ".agent/modules/10-observability-eval-rag-agent-evaluation.md"
VERIFIER = ROOT / "tools/scripts/verify_observability_eval_target_protocols.py"
TESTS = ROOT / "tests/repo/test_observability_eval_target_protocols.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, got {count}")
    return text.replace(old, new, 1)


def alignment_section() -> str:
    return r'''### 3.1 Wave 1 共享 Contract 与服务端产品边界

规范基线：

```text
docs/decisions/0003-wave1-cross-module-contract-freeze.md
docs/governance/wave1-cross-module-contract-registry.md
```

上述文件已经合并为 `CONFIRMED_TARGET`，但仍不是 Current 或实现证据。

产品运行边界固定为：

```text
Web / Desktop Frontend
→ Server-hosted Product API
→ Domain Fact Owners
→ Transactional Outbox
→ Observability Ingest / Eval Workers
→ PostgreSQL / Object Store / Queue / External Sink Adapter
```

前端只消费经过授权和脱敏的 Projection，不保存权威 Trace、Audit、Eval、Evidence 或 Release Gate 事实。SQLite、本地文件和 in-process queue 仅是 Developer / CI Adapter，不是多用户产品部署 Target。

共享事实 Ownership：

```text
Security owns
    SecurityAuditRequirementV1
    DataClassification
    RedactionDecision
    ExternalSinkPolicy

Infrastructure owns
    AuditDurabilityRequirement
    AuditPersistenceReceiptV1
    local append / outbox / queue / storage physical receipts

Observability & Eval owns
    TelemetryEnvelopeV1 ingest semantics
    accepted immutable AuditEvent
    Trace / Metric / Log projections
    ExternalSinkDelivery
    Eval / Evidence / Benchmark / ReleaseGateEvaluation
```

Canonical Envelope：

```yaml
CrossModuleEnvelopeV1:
  contract_name: string
  contract_version: string
  contract_bundle_version: string
  message_id: string
  producer_module: string
  consumer_module: string
  tenant_id: string
  workspace_id: string | null
  run_id: string | null
  step_run_id: string | null
  correlation_id: string
  causation_id: string | null
  idempotency_key: string | null
  aggregate_type: string | null
  aggregate_id: string | null
  aggregate_version: int | null
  expected_generation: int | null
  effective_security_epoch_ref: string | null
  effective_security_epoch_hash: string | null
  principal_context_ref: string | null
  security_context_ref: string | null
  authorization_decision_ref: string | null
  deadline_at: datetime | null
  trace_id: string
  data_classification: string
  redaction_decision_ref: string | null
  audit_requirement_ref: string | null
  occurred_at: datetime
  created_at: datetime
  payload: object | null
  payload_ref: string | null
  payload_hash: string
  payload_schema_hash: string

TelemetryEnvelopeV1:
  envelope: CrossModuleEnvelopeV1
  producer_instance_id: string
  producer_sequence: int | null
  stream_key: string
  category: DOMAIN_FACT | CONTROL_DECISION | OPERATION | POINT_EVENT | SECURITY_AUDIT | EVAL | INFRASTRUCTURE
  observed_at: datetime
  retention_policy_ref: string
```

`TelemetryEnvelopeV1` 不能删减 Canonical Envelope 的 Tenant、Workspace、Security Epoch、Authorization、Classification、Payload Hash 或 Schema Hash。旧字段 `producer`、`schema_hash`、`payload_inline` 只作为迁移 Alias，分别映射 `producer_module`、`payload_schema_hash`、`payload`。

Mandatory Audit 顺序：

```text
SecurityAuditRequirementV1
→ Infrastructure AuditDurabilityRequirement
→ local durable AuditPersistenceReceiptV1
→ source effect may execute when policy requires MANDATORY_BEFORE_EFFECT
→ TelemetryEnvelopeV1
→ Observability accepts immutable AuditEvent
→ optional ExternalSinkDelivery
```

强制不变量：

```text
AuditPersistenceReceipt != accepted AuditEvent
accepted AuditEvent != Tool Effect success
ExternalSinkDelivery != source-domain success
Queue ACK != accepted AuditEvent
StructuredLog != AuditEvent
Trace Projection != immutable Audit fact
```

Canonical failure codes：

```text
OBS_ENVELOPE_SCHEMA_UNSUPPORTED
OBS_INGEST_GAP
OBS_AUDIT_ACCEPTANCE_FAILED
OBS_EXTERNAL_SINK_DELIVERY_FAILED
```

Observability 可以 Retry ingest、Projection 和 External Sink Delivery，但不能 Retry 原领域副作用、重新批准安全决策或修改源领域终态。

'''


def main() -> None:
    formal = FORMAL.read_text(encoding="utf-8")
    formal = formal.replace("status: normative-target-module-design", "status: normative-target-module-architecture", 1)
    formal = replace_once(
        formal,
        "5. 支持本地事实存储，并通过经 Security Redaction 的 vendor-neutral adapter 导出到 OpenTelemetry/LangSmith-compatible sink。",
        "5. 使用服务端权威事实存储，并通过经 Security Redaction 的 vendor-neutral adapter 导出到 OpenTelemetry/LangSmith-compatible sink；本地存储只作为 Developer / CI Adapter。",
        "server product target",
    )
    if "### 3.1 Wave 1 共享 Contract 与服务端产品边界" not in formal:
        formal = replace_once(formal, "## 4. 总体运行流程", alignment_section() + "## 4. 总体运行流程", "alignment section")

    old_envelope = '''TelemetryEnvelope:
  envelope_id: string
  message_id: string
  contract_name: string
  contract_version: string
  schema_hash: string
  producer: string
  producer_instance_id: string
  producer_sequence: int | null
  stream_key: string
  correlation_id: string
  causation_id: string | null
  trace_context: TraceContext
  category: DOMAIN_FACT | CONTROL_DECISION | OPERATION | POINT_EVENT | SECURITY_AUDIT | EVAL | INFRASTRUCTURE
  occurred_at: datetime
  observed_at: datetime
  payload_ref: string | null
  payload_inline: object | null
  payload_hash: string
  redaction_decision_ref: string
  authorization_decision_ref: string
  retention_policy_ref: string
  idempotency_key: string'''
    new_envelope = '''TelemetryEnvelope:
  envelope: CrossModuleEnvelopeV1
  envelope_id: string
  producer_instance_id: string
  producer_sequence: int | null
  stream_key: string
  trace_context: TraceContext
  category: DOMAIN_FACT | CONTROL_DECISION | OPERATION | POINT_EVENT | SECURITY_AUDIT | EVAL | INFRASTRUCTURE
  observed_at: datetime
  retention_policy_ref: string'''
    formal = replace_once(formal, old_envelope, new_envelope, "Telemetry envelope mapping")

    FORMAL.write_text(formal.rstrip() + "\n", encoding="utf-8", newline="\n")
    MIRROR.write_text(formal.rstrip() + "\n", encoding="utf-8", newline="\n")

    rag = RAG_FORMAL.read_text(encoding="utf-8")
    rag = rag.replace("`ALIGNED_PENDING_FIELDS`", "`CONFIRMED_TARGET`")
    rag = rag.replace(
        "未合并 PR 仍是 Parallel Proposal；字段、枚举和 failure code 在 Wave 1 集中审计前为 `CONFIRMED_TARGET`，不是 Confirmed Target。",
        "ADR 0003 与 Wave 1 Registry 已合并；共享字段、枚举、Owner 和 Failure Code 为 `CONFIRMED_TARGET`，但仍不是 Current 或工程完成证据。",
    )
    RAG_FORMAL.write_text(rag.rstrip() + "\n", encoding="utf-8", newline="\n")
    RAG_MIRROR.write_text(rag.rstrip() + "\n", encoding="utf-8", newline="\n")

    verifier = VERIFIER.read_text(encoding="utf-8")
    verifier = replace_once(
        verifier,
        '    "TraceContext",\n',
        '    "CrossModuleEnvelopeV1",\n    "TelemetryEnvelopeV1",\n    "SecurityAuditRequirementV1",\n    "AuditDurabilityRequirement",\n    "AuditPersistenceReceiptV1",\n    "TraceContext",\n',
        "required shared contracts",
    )
    verifier = replace_once(
        verifier,
        'CROSS_MODULE_TERMS = [\n',
        'CROSS_MODULE_TERMS = [\n    "Server-hosted Product API",\n    "CONFIRMED_TARGET",\n    "effective_security_epoch_ref",\n    "effective_security_epoch_hash",\n    "payload_schema_hash",\n    "OBS_ENVELOPE_SCHEMA_UNSUPPORTED",\n    "OBS_INGEST_GAP",\n    "OBS_AUDIT_ACCEPTANCE_FAILED",\n    "OBS_EXTERNAL_SINK_DELIVERY_FAILED",\n    "AuditPersistenceReceipt != accepted AuditEvent",\n    "ExternalSinkDelivery != source-domain success",\n',
        "cross-module alignment terms",
    )
    verifier = verifier.replace('            "ALIGNED_PENDING_FIELDS",', '            "CONFIRMED_TARGET",', 1)
    verifier = replace_once(
        verifier,
        '''    forbidden_claims = [
        "quality is proven",
        "production ready now",
        "full CI passed",
    ]''',
        '''    forbidden_claims = [
        "quality is proven",
        "production ready now",
        "full CI passed",
        "ALIGNED_PENDING_FIELDS",
        "支持本地事实存储，并通过",
    ]''',
        "forbidden stale alignment",
    )
    VERIFIER.write_text(verifier, encoding="utf-8", newline="\n")

    tests = TESTS.read_text(encoding="utf-8")
    tests = tests.replace("def test_parallel_wave_contracts_remain_pending_fields() -> None:", "def test_wave1_contracts_are_confirmed_target() -> None:")
    tests = tests.replace('    assert "ALIGNED_PENDING_FIELDS" in content\n    assert "未合并 PR 仍是 Parallel Proposal" in content', '    assert "CONFIRMED_TARGET" in content\n    assert "ALIGNED_PENDING_FIELDS" not in content')
    if "test_server_authoritative_observability_contract_alignment" not in tests:
        tests += '''\n\ndef test_server_authoritative_observability_contract_alignment() -> None:\n    content = _formal()\n    for term in [\n        "Server-hosted Product API",\n        "CrossModuleEnvelopeV1",\n        "TelemetryEnvelopeV1",\n        "SecurityAuditRequirementV1",\n        "AuditDurabilityRequirement",\n        "AuditPersistenceReceiptV1",\n        "effective_security_epoch_ref",\n        "payload_schema_hash",\n        "OBS_AUDIT_ACCEPTANCE_FAILED",\n        "AuditPersistenceReceipt != accepted AuditEvent",\n        "ExternalSinkDelivery != source-domain success",\n    ]:\n        assert term in content\n'''
    TESTS.write_text(tests, encoding="utf-8", newline="\n")
    print("Observability Wave 1 alignment applied.")


if __name__ == "__main__":
    main()
