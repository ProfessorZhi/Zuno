# Security Runtime Batch Evidence

状态：`implementation_available` 证据

时间：2026-07-18

覆盖需求：

- `ARCH-SEC-001` 到 `ARCH-SEC-060`

范围说明：

- 已证明 PrincipalContext、WorkloadIdentity、tenant/workspace 隔离和 SecurityContext 权限交集可机器验证。
- 已证明 OrgUnit 无环、Membership 与资源授权分离、DelegatedAdminScope 限定管理范围、三档 UI 权限映射到细粒度 ActionSet。
- 已证明 explicit deny 优先、默认拒绝、禁止委派放大、父 Grant 撤销级联、Agent/Task/Session 临时授权和 effective action intersection。
- 已证明 PolicyVersion schema hash 与不可变激活，PAP/PDP/PEP/PIP 分离，validation、simulation 和 shadow evaluation 存在。
- 已证明 AuthorizationDecision 带 explanation、policy version 和 epoch，EffectiveSecurityEpoch 绑定 policy/grant/revocation/credential generation cache hash。
- 已证明 input/output detection、data classification、redaction decision、redaction adapter failure fail-closed、不可信 instruction trust label、information flow、protected sink 和 declassification。
- 已证明 ambiguous action intent 不能由模型自行授权，Memory、Multimodal、Knowledge retrieval、Citation 和 Model provider/residency gate 独立记录授权。
- 已证明 PreparedToolAction hash、SecurityApprovalDecision 防重放、execute-time epoch review、UNKNOWN Tool Effect 必须 reconciliation 后才能 retry。
- 已证明 MCP audience validation、禁止 token passthrough、On-Behalf-Of binding、CredentialVersionRef、SecretRef/short lease 和 secret 不进入 prompt/trace/memory。
- 已证明 Sandbox tier、NetworkEgressPolicy、SSRF fail-closed、SupplyChainArtifact provenance、SupplyChainTrustDecision quarantine、Break-glass 限时限域、SecurityIncident owner。
- 已证明 Security facts 与 outbox 同事务，mandatory audit before effect，audit 不转移领域 ownership，retry/idempotency/recovery 拒绝 stale epoch。
- 已证明 PostgreSQL security facts 是安全事实源，checkpointer 只保存控制状态，前端只展示后端有效结果。
- 已证明 Adaptive Security Eval、utility release gate 和 Target 转 Current 的工程证据 gate。

未覆盖：

- Security 模块 `ARCH-SEC-001` 到 `ARCH-SEC-060` 已由本批 evidence 覆盖；其他模块仍需后续批次证明。
- 本证据不声明 PHASE05 或全 Program 关闭。

验证命令：

```powershell
python -m py_compile src/backend/zuno/platform/security/runtime_batch.py tools/scripts/verify_security_runtime_batch.py
pytest -q tests/security/test_security_runtime_batch.py tests/security/test_security_governance_contract.py -p no:cacheprovider
python tools/scripts/verify_security_runtime_batch.py
python tools/scripts/verify_requirement_ledger_evidence_gate.py
python tools/scripts/verify_docs_entrypoints.py
git diff --check
pytest -q tests/security/test_security_runtime_batch.py tests/security/test_security_governance_contract.py tests/api/test_workspace_security_observability_runtime.py tests/api/test_fastapi_jwt_auth_compat.py tests/integration/test_phase04_secret_rotation_tenant_hit.py -p no:cacheprovider
```

结果：

```text
10 passed in 0.17s
Security runtime batch verifier passed for ARCH-SEC-001..060
Requirement ledger evidence gate passed.
documentation entrypoint verification passed.
17 passed, 1 warning in 53.30s
```
