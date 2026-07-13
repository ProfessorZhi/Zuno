from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INFRA = ROOT / "docs/modules/11-infrastructure.md"
INFRA_MIRROR = ROOT / ".agent/modules/11-infrastructure.md"
ADR = ROOT / "docs/decisions/0003-wave1-cross-module-contract-freeze.md"
REGISTRY = ROOT / "docs/governance/wave1-cross-module-contract-registry.md"
CORE = ROOT / "docs/modules/06-agent-core-planning-control.md"
CORE_MIRROR = ROOT / ".agent/modules/06-agent-core-planning-control.md"
CORE_VERIFIER = ROOT / "tools/scripts/verify_agent_core_target_protocols.py"
AGENT_SYSTEM_VERIFIER = ROOT / ".agent/scripts/verify_agent_system.py"
INFRA_VERIFIER = ROOT / "tools/scripts/verify_infrastructure_target_protocols.py"
WAVE_VERIFIER = ROOT / "tools/scripts/verify_wave1_contract_freeze.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one occurrence, got {count}")
    return text.replace(old, new, 1)


def replace_regex_once(text: str, pattern: str, replacement: str, label: str) -> str:
    result, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"{label}: expected one regex occurrence, got {count}")
    return result


def canonical_envelope_block() -> str:
    return '''class CrossModuleEnvelopeV1(BaseModel):
    contract_name: str
    contract_version: str
    contract_bundle_version: str
    message_id: str
    producer_module: str
    consumer_module: str
    tenant_id: str
    workspace_id: str | None
    run_id: str | None
    step_run_id: str | None
    correlation_id: str
    causation_id: str | None
    idempotency_key: str | None
    aggregate_type: str | None
    aggregate_id: str | None
    aggregate_version: int | None
    expected_generation: int | None
    effective_security_epoch_ref: str | None
    effective_security_epoch_hash: str | None
    principal_context_ref: str | None
    security_context_ref: str | None
    authorization_decision_ref: str | None
    deadline_at: datetime | None
    trace_id: str
    data_classification: str
    redaction_decision_ref: str | None
    audit_requirement_ref: str | None
    occurred_at: datetime
    created_at: datetime
    payload: dict | None
    payload_ref: str | None
    payload_hash: str
    payload_schema_hash: str'''


def canonical_envelope_text() -> str:
    return '''contract_name
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
payload_schema_hash'''


def update_infrastructure() -> None:
    text = INFRA.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "- Local-first 与 Enterprise deployment 共用 typed contract，不让业务模块绑定厂商。",
        "- 服务端统一后端是产品 Target；浏览器或桌面前端只通过 Product API 访问。SQLite、本地对象存储和本地队列仅作为开发、测试与 CI Adapter，共用同一 typed contract。",
        "infrastructure deployment quality goal",
    )
    text = replace_once(
        text,
        "| Capability | Local-first Target | Enterprise Target | 理由 |",
        "| Capability | Developer / CI Adapter | Canonical Server Product Target | 理由 |",
        "infrastructure target table header",
    )
    text = replace_once(
        text,
        "Target 选择不等于 Current 提升；迁移必须进入独立 Program。",
        """Target 选择不等于 Current 提升；迁移必须进入独立 Program。

产品部署边界固定为：

```text
Web / Desktop Frontend
    只持有短期客户端会话和展示状态
    → Server-hosted Product API
        → Principal / Tenant / Workspace resolution
        → Security Control Plane
        → Agent / Knowledge / Memory / Model / Tool backends
        → PostgreSQL / Object Store / Queue / Checkpoint
```

前端不得直连数据库、对象存储、Queue、Checkpointer、模型 Provider 或 Secret Store。每个用户请求必须在服务端解析可信 `PrincipalAccount`、Tenant、Workspace、Policy 与 Effective Security Epoch。本地 Adapter 只用于开发、单元测试、集成测试和离线演示，不是多用户产品部署模式。""",
        "server authoritative deployment boundary",
    )
    text = replace_once(text, "## 7. Local-first Topology", "## 7. Developer / CI Local Adapter Topology", "local topology heading")
    text = replace_once(text, "  UI --> API[FastAPI + Controller]", "  DevClient[Developer / Test Client] --> API[FastAPI + Controller]", "local topology client")
    text = replace_once(
        text,
        "- Local backup/restore 可以轻量，但不得称为 enterprise production ready。",
        "- Local backup/restore 可以轻量，但不得称为 server product deployment 或 production ready。\n- 不在该拓扑承载正式多用户账号、组织委派、生产 Secret 或生产权限事实。",
        "local topology constraints",
    )
    text = replace_once(text, "## 8. Enterprise Topology", "## 8. Canonical Server Product Topology", "server topology heading")
    text = replace_once(
        text,
        "flowchart TB\n  LB --> API[API Role]",
        "flowchart TB\n  Frontend[Web / Desktop Frontend] --> LB\n  IdP[Trusted Identity Provider] --> API\n  LB --> API[Product API Role]",
        "server topology boundary",
    )
    text = replace_once(
        text,
        "推荐部署单位是 role，不是默认微服务。相同 backend image 可以按 role 启动；只有隔离、扩缩容或安全要求出现时才拆镜像。",
        """推荐部署单位是 role，不是默认微服务。相同 backend image 可以按 role 启动；只有隔离、扩缩容或安全要求出现时才拆镜像。

该拓扑是 Zuno 产品 Target：后端部署在受控服务器或云运行环境，前端只是 API Client。所有账号、组织、权限、知识、Memory、AgentRun、Usage、Audit 与配置事实均由后端权威存储和校验；客户端缓存不能成为授权或业务事实源。""",
        "server topology semantics",
    )
    text = replace_once(
        text,
        'deployment_class: Literal["LOCAL", "ENTERPRISE"]',
        'deployment_class: Literal["DEV_LOCAL", "SERVER"]',
        "deployment class",
    )
    INFRA.write_text(text, encoding="utf-8", newline="\n")
    INFRA_MIRROR.write_text(text, encoding="utf-8", newline="\n")


def update_adr() -> None:
    text = ADR.read_text(encoding="utf-8")
    deployment = '''## 1.1 协调决议：服务端权威产品边界

Zuno 产品 Target 不是“每个用户本机运行一套后端”。正式产品形态固定为前后端分离：

```text
Web / Desktop Frontend
→ Server-hosted Product API
→ Security / Agent Core / Knowledge / Memory / Model Gateway / Tool Runtime
→ Infrastructure data and execution services
```

每个自然人或服务主体拥有服务端 `PrincipalAccount`，所有 Tenant、Workspace、OrgUnit、ResourceGrant、Policy、Security Epoch、AgentRun、Knowledge、Memory、Usage 和 Audit 事实由后端权威计算与保存。前端输入、缓存的角色、资源列表和 `allowed` 标志均不可信。

SQLite、本地对象存储、本地 Checkpoint 和 in-process Queue 仅作为 Developer / CI Adapter；它们必须复用同一 typed port，但不构成产品部署 Target，也不能证明多用户隔离、并发、恢复或生产安全。

'''
    if "## 1.1 协调决议：服务端权威产品边界" not in text:
        text = replace_once(text, "## 2. 决议一：Infrastructure 是逻辑模块", deployment + "## 2. 决议一：Infrastructure 是逻辑模块", "ADR deployment decision")

    old_envelope = '''class CrossModuleEnvelopeV1(BaseModel):
    contract_name: str
    contract_version: str
    message_id: str
    producer_module: str
    tenant_id: str
    workspace_id: str | None
    correlation_id: str
    causation_id: str | None
    idempotency_key: str | None
    aggregate_type: str | None
    aggregate_id: str | None
    aggregate_version: int | None
    expected_generation: int | None
    effective_security_epoch_ref: str | None
    effective_security_epoch_hash: str | None
    principal_context_ref: str | None
    deadline_at: datetime | None
    trace_id: str
    data_classification: str
    redaction_decision_ref: str | None
    audit_requirement_ref: str | None
    occurred_at: datetime
    payload_ref: str | None
    payload_hash: str'''
    text = replace_once(text, old_envelope, canonical_envelope_block(), "ADR canonical envelope")
    text = replace_once(
        text,
        "- `message_id` 只用于 Envelope 去重；业务幂等使用 `idempotency_key`。",
        """- `message_id` 只用于 Envelope 去重；业务幂等使用 `idempotency_key`。
- `contract_bundle_version` 固定一次 Run 或工作流使用的跨模块 Contract 集；`producer_module` 与 `consumer_module` 必须显式。
- `payload` 与 `payload_ref` 至少存在一个；无论使用内联或对象引用，都必须验证 `payload_hash` 与 `payload_schema_hash`。
- `run_id`、`step_run_id` 在非 Agent 流程可为空，但不得用 `trace_id` 代替领域标识。""",
        "ADR envelope rules",
    )
    text = replace_once(
        text,
        "4. Agent Core 后续文档维护把旧 `PreparedAction` Aggregate 改为 `ActionProposal` + `ActionExecutionBinding` Ref；",
        "4. 本协调 PR 同步把 Agent Core 的旧 `PreparedAction` Aggregate 改为 `ActionProposal` + `ActionExecutionBinding`，并只引用 Tool Runtime `PreparedToolAction`；",
        "ADR core synchronization",
    )
    ADR.write_text(text, encoding="utf-8", newline="\n")


def update_registry() -> None:
    text = REGISTRY.read_text(encoding="utf-8")
    text = text.replace("#18 Model Gateway @ a78f718ac8002ba2c602f922187bb155484ef5c4", "#18 Model Gateway @ 3bd9b3e4437314c376a5b1b767ef052e3c74db53")
    text = text.replace("#20 Observability & Eval @ 600f1101dbf0c0e8bc9591e5dddc7a4b2ba4d81d", "#20 Observability & Eval @ 4a91953799cd0bae7f3ca441cccabffbce1271f9")
    boundary = '''## 2.1 产品部署边界

状态：`FIELD_FROZEN_PENDING_MERGE`。

```text
Frontend Client
→ Server-hosted Product API
→ Backend logical modules
→ Infrastructure primitives
```

- `PrincipalAccount`、Tenant、Workspace、OrgUnit、Grant、Policy、Epoch 和业务事实只在后端成为权威事实。
- 前端不得直连数据服务、Provider、Queue、Checkpoint 或 Secret Store。
- Developer / CI Local Adapter 不得冒充产品部署模式或多用户安全证据。

'''
    if "## 2.1 产品部署边界" not in text:
        text = replace_once(text, "## 3. 通用 CrossModuleEnvelope", boundary + "## 3. 通用 CrossModuleEnvelope", "registry deployment boundary")
    old_envelope = '''class CrossModuleEnvelopeV1(BaseModel):
    contract_name: str
    contract_version: str
    message_id: str
    producer_module: str
    tenant_id: str
    workspace_id: str | None
    correlation_id: str
    causation_id: str | None
    idempotency_key: str | None
    aggregate_type: str | None
    aggregate_id: str | None
    aggregate_version: int | None
    expected_generation: int | None
    effective_security_epoch_ref: str | None
    effective_security_epoch_hash: str | None
    principal_context_ref: str | None
    deadline_at: datetime | None
    trace_id: str
    data_classification: str
    redaction_decision_ref: str | None
    audit_requirement_ref: str | None
    occurred_at: datetime
    payload_ref: str | None
    payload_hash: str'''
    text = replace_once(text, old_envelope, canonical_envelope_block(), "registry canonical envelope")
    text = replace_once(
        text,
        "- `message_id` 只用于 Envelope 去重；业务幂等使用 `idempotency_key`。",
        """- `message_id` 只用于 Envelope 去重；业务幂等使用 `idempotency_key`。
- `contract_bundle_version`、`producer_module`、`consumer_module` 是强制路由与兼容字段。
- `payload` / `payload_ref` 至少一个存在，并同时校验 payload hash 与 schema hash。
- Agent 相关消息保留 `run_id` / `step_run_id`；非 Agent 工作流可以为空。""",
        "registry envelope rules",
    )
    REGISTRY.write_text(text, encoding="utf-8", newline="\n")


def update_core() -> None:
    text = CORE.read_text(encoding="utf-8")
    text = replace_once(
        text,
        "SignalConsumption\nPreparedAction\nApprovalDecision\nIdempotencyClaim",
        "SignalConsumption\nActionProposal\nActionExecutionBinding\nPreparedToolActionRef\nApprovalDecision\nIdempotencyClaimRef",
        "core object list",
    )
    text = replace_once(
        text,
        "domain/{task_contract,run,plan,step,action,dispatch,interrupt,signal,prepared_action,approval,idempotency,result_validity,artifact,publication,failure,outcome}.py",
        "domain/{task_contract,run,plan,step,action,dispatch,interrupt,signal,action_proposal,action_execution_binding,approval,result_validity,artifact,publication,failure,outcome}.py",
        "core target directory",
    )
    text = replace_once(
        text,
        "├── agent_prepared_actions\n├── agent_approval_decisions\n├── agent_idempotency_claims",
        "├── agent_action_proposals\n├── agent_action_execution_bindings\n├── agent_approval_decisions\n├── agent_idempotency_claim_refs",
        "core action tables",
    )
    text = replace_once(
        text,
        "事务 A 提交 PreparedAction、ActionRun、IdempotencyClaim；事务外执行；事务 B 提交 Observation 和 Outcome。",
        "事务 A 提交 ActionProposal、ActionExecutionBinding、ActionRun，并保存 Tool Runtime PreparedToolAction 与 Infrastructure IdempotencyClaim Ref；事务外执行；事务 B 提交 Observation 和 Outcome。",
        "core side effect transaction",
    )
    old_env = '''contract_name
contract_version
contract_bundle_version
message_id
correlation_id
causation_id
tenant_id
workspace_id
run_id
step_run_id
producer
consumer
security_context_ref
authorization_decision_ref
data_classification
created_at
payload
payload_schema_hash'''
    text = text.replace(old_env, canonical_envelope_text())
    text = replace_once(
        text,
        "| Aggregate Root | `TaskContract`、`AgentRun`、`PlanVersion`、`StepRun`、`PreparedAction`、`ArtifactVersion`、`Publication` |",
        "| Aggregate Root | `TaskContract`、`AgentRun`、`PlanVersion`、`StepRun`、`ArtifactVersion`、`Publication` |",
        "core aggregate roots",
    )
    text = replace_once(
        text,
        "| Entity | `GoalVersion`、`ObjectiveDefinition`、`ObjectiveOutcome`、`ActionRun`、`Interrupt`、`DispatchGroup`、`DispatchItem`、`FinalCandidate`、`DeliveryReceipt` |",
        "| Entity | `GoalVersion`、`ObjectiveDefinition`、`ObjectiveOutcome`、`ActionProposal`、`ActionExecutionBinding`、`ActionRun`、`Interrupt`、`DispatchGroup`、`DispatchItem`、`FinalCandidate`、`DeliveryReceipt` |",
        "core entities",
    )
    text = replace_once(
        text,
        "| Value Object / Policy Snapshot | `DependencyRule`、`ActivationCondition`、`JoinPolicy`、`ResourceClaim`、`EffectivePolicySnapshot`、`ResultValidityRecord` |",
        "| Value Object / Policy Snapshot | `DependencyRule`、`ActivationCondition`、`JoinPolicy`、`ResourceClaim`、`PreparedToolActionRef`、`IdempotencyClaimRef`、`EffectivePolicySnapshot`、`ResultValidityRecord` |",
        "core value objects",
    )
    text = replace_once(
        text,
        "| Infrastructure Record | `DomainCommitMarker`、`RecoveryWatermark`、`OutboxEvent`、`ReconciliationRecord`、`IdempotencyClaim`、Lease |",
        "| Infrastructure Record | `DomainCommitMarker`、`RecoveryWatermark`、`OutboxEvent`、`ReconciliationRecord`、Lease |",
        "core infrastructure records",
    )
    mapping_anchor = "| `ControlDecision` | Agent Core | Immutable Result | `agent_control_decisions` | 引用 Command 与 applied generation |"
    mapping_add = mapping_anchor + "\n| `ActionProposal` | Agent Core | Relational Entity | `agent_action_proposals` | 只表达目标、能力、参数 Ref 与期望结果，不含可执行 Secret/Payload |\n| `ActionExecutionBinding` | Agent Core | Relational Entity | `agent_action_execution_bindings` | 绑定 Step/Plan、PreparedToolAction Ref、Approval/Claim Ref 与控制状态 |"
    text = replace_once(text, mapping_anchor, mapping_add, "core storage mapping")

    old_side_effect = r'''PreparedAction：

```text
prepared_action_id
run_id
step_run_id
action_type
tool_id
normalized_arguments
arguments_hash
target_resources
credential_scope
side_effect_class
security_policy_version
approval_policy_version
idempotency_key
expires_at
status
```'''
    new_side_effect = '''Canonical side-effect split：

```text
Agent Core owns
    ActionProposal
    ActionExecutionBinding

Tool Runtime owns
    PreparedToolAction
    ToolAttempt
    EffectReceipt
    EffectReconciliation

Security owns
    ActionAuthorizationDecision
    SecurityApprovalDecision
    EffectiveSecurityEpoch

Infrastructure owns
    IdempotencyClaim
    Queue / Lease / Fencing / Outbox / AuditPersistenceReceipt
```

```text
ActionProposal
    action_proposal_id
    run_id
    step_run_id
    proposed_capability_ref
    proposed_operation
    proposed_args_ref
    proposed_args_hash
    expected_result_contract_ref
    side_effect_class
    proposal_source_ref
    status

ActionExecutionBinding
    action_execution_binding_id
    action_proposal_ref
    prepared_tool_action_ref
    prepared_action_hash
    approval_decision_ref
    idempotency_claim_ref
    tool_attempt_ref
    effect_receipt_ref
    effect_reconciliation_ref
    controller_epoch
    execution_epoch
    status
```

`PreparedAction` 是旧文档术语；规范名称为 Tool Runtime `PreparedToolAction`。Agent Core 只保存 Ref、Hash 与控制绑定，不持有 canonical arguments、Credential Material 或可执行 Payload。'''
    text = replace_once(text, old_side_effect, new_side_effect, "core prepared action section")
    text = replace_once(text, "prepared_action_id\narguments_hash", "prepared_tool_action_ref\nprepared_action_hash", "core approval binding")
    old_claim = r'''IdempotencyClaim：

```text
idempotency_claim_id
idempotency_key
action_run_id
scope
status
claimed_at
completed_at
external_receipt_ref
```

状态：CLAIMED、EXECUTING、SUCCEEDED、FAILED、UNKNOWN、CLOSED。`CLOSED` 只表示 Claim 生命周期关闭，Action 业务结果仍以 ActionOutcome 为准。'''
    new_claim = '''IdempotencyClaimRef：

```text
idempotency_claim_ref
idempotency_key_hash
owner_module = INFRASTRUCTURE
scope
fencing_epoch
status
external_receipt_ref
```

Claim 生命周期和条件写由 Infrastructure 拥有；Agent Core 只保存 Ref 并消费结构化结果。Claim 成功、Queue ACK 或 Lease Release 均不等于 Tool Effect 成功。'''
    text = replace_once(text, old_claim, new_claim, "core idempotency ownership")
    text = replace_once(
        text,
        "UNKNOWN 时禁止盲目重试。Compensation 是新的受治理副作用，需要新的 PreparedAction、Security、Approval 和 IdempotencyClaim；不可补偿操作标记 NON_COMPENSATABLE。",
        "UNKNOWN 时禁止盲目重试。Compensation 是新的受治理副作用，需要新的 ActionProposal、Tool Runtime PreparedToolAction、Security/Approval 和 Infrastructure IdempotencyClaim；不可补偿操作标记 NON_COMPENSATABLE。",
        "core compensation",
    )
    CORE.write_text(text, encoding="utf-8", newline="\n")
    CORE_MIRROR.write_text(text, encoding="utf-8", newline="\n")


def update_verifiers() -> None:
    text = CORE_VERIFIER.read_text(encoding="utf-8")
    text = replace_once(text, '    "PreparedAction",\n', '    "ActionProposal",\n    "ActionExecutionBinding",\n    "PreparedToolAction",\n', "core required terms")
    text = replace_once(text, '    "agent_outcome_corrections",\n', '    "agent_outcome_corrections",\n    "agent_action_proposals",\n    "agent_action_execution_bindings",\n', "core required tables")
    text = replace_once(
        text,
        '    "状态：CLAIMED、EXECUTING、SUCCEEDED、FAILED、UNKNOWN、RECONCILED。",\n',
        '    "状态：CLAIMED、EXECUTING、SUCCEEDED、FAILED、UNKNOWN、RECONCILED。",\n    "`PreparedAction`、`ArtifactVersion`",\n    "agent_prepared_actions",\n',
        "core forbidden legacy",
    )
    object_anchor = '    "ControlDecision": "agent_control_decisions",\n'
    text = replace_once(text, object_anchor, object_anchor + '    "ActionProposal": "agent_action_proposals",\n    "ActionExecutionBinding": "agent_action_execution_bindings",\n', "core object table pairs")
    CORE_VERIFIER.write_text(text, encoding="utf-8", newline="\n")

    text = AGENT_SYSTEM_VERIFIER.read_text(encoding="utf-8")
    text = replace_once(text, '            "PreparedAction",\n', '            "ActionProposal",\n            "ActionExecutionBinding",\n            "PreparedToolAction",\n', "agent system core phrases")
    AGENT_SYSTEM_VERIFIER.write_text(text, encoding="utf-8", newline="\n")

    text = INFRA_VERIFIER.read_text(encoding="utf-8")
    text = replace_once(text, '        "Local-first Topology",\n        "Enterprise Topology",\n', '        "Developer / CI Local Adapter Topology",\n        "Canonical Server Product Topology",\n        "服务端统一后端是产品 Target",\n', "infra topology verifier")
    INFRA_VERIFIER.write_text(text, encoding="utf-8", newline="\n")

    text = WAVE_VERIFIER.read_text(encoding="utf-8")
    text = text.replace('AGENT_MODULES_INDEX = REPO_ROOT / ".agent/modules/README.md"\n', 'AGENT_MODULES_INDEX = REPO_ROOT / ".agent/modules/README.md"\nCORE = REPO_ROOT / "docs/modules/06-agent-core-planning-control.md"\nCORE_MIRROR = REPO_ROOT / ".agent/modules/06-agent-core-planning-control.md"\n')
    text = replace_once(text, '    "CrossModuleEnvelopeV1",\n', '    "CrossModuleEnvelopeV1",\n    "服务端权威产品边界",\n    "contract_bundle_version",\n    "consumer_module",\n    "payload_schema_hash",\n', "wave ADR terms")
    text = replace_once(text, '    "CrossModuleEnvelopeV1",\n    "SecurityConditionalWrite",\n', '    "CrossModuleEnvelopeV1",\n    "产品部署边界",\n    "contract_bundle_version",\n    "consumer_module",\n    "payload_schema_hash",\n    "SecurityConditionalWrite",\n', "wave registry terms")
    path_anchor = '        (AGENT_MODULES_INDEX, "XMOD_AGENT_INDEX_MISSING"),\n'
    text = replace_once(text, path_anchor, path_anchor + '        (CORE, "XMOD_CORE_MISSING"),\n        (CORE_MIRROR, "XMOD_CORE_MIRROR_MISSING"),\n', "wave core paths")
    read_anchor = '    agent_index = _read(AGENT_MODULES_INDEX)\n'
    text = replace_once(text, read_anchor, read_anchor + '    core = _read(CORE)\n', "wave core read")
    check_anchor = '    for term in ADR_TERMS:\n'
    core_checks = '''    if CORE.read_bytes() != CORE_MIRROR.read_bytes():
        findings.append(Finding("XMOD_CORE_MIRROR_DRIFT", "Agent Core formal document and mirror differ"))
    for term in [
        "ActionProposal",
        "ActionExecutionBinding",
        "PreparedToolAction",
        "agent_action_proposals",
        "agent_action_execution_bindings",
        "contract_bundle_version",
        "consumer_module",
        "effective_security_epoch_ref",
        "payload_schema_hash",
    ]:
        _require(core, term, "XMOD_CORE_ALIGNMENT", findings)
    for forbidden in [
        "`PreparedAction`、`ArtifactVersion`",
        "agent_prepared_actions",
    ]:
        if forbidden in core:
            findings.append(Finding("XMOD_CORE_LEGACY_OWNERSHIP", f"legacy Agent Core ownership remains: {forbidden}"))

'''
    text = replace_once(text, check_anchor, core_checks + check_anchor, "wave core checks")
    WAVE_VERIFIER.write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    update_infrastructure()
    update_adr()
    update_registry()
    update_core()
    update_verifiers()
    print("Wave 1 shared architecture coordination applied.")


if __name__ == "__main__":
    main()
