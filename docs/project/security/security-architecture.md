# Security Architecture：谁可以做什么？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 身份、权限、Secret、Sandbox、网络和副作用如何形成可验证边界？
owner: Security Decision Owner
replaces: `docs/project/modules/09-security.md`（Superseded）

## Boundary

Security owns Principal/Tenant/Workspace/Grant/Policy/SecurityEpoch/Approval decisions and audit authority. Platform Domain stores business authorization references; Tool/Sandbox enforces action gates; Agent Runtime cannot mint permission or access plaintext Secret.

## Required gates

```text
Principal / Tenant / Scope
  → Agent / Task downscope
  → PreparedAction canonical hash
  → Security decision + current epoch
  → optional human approval
  → Sandbox / Network / Secret enforcement
  → EffectReceipt + durable audit
```

Read-only/reversible/irreversible effects have different policy. Unknown effect is not success and not safe retry. Prompt injection is untrusted data; it cannot expand tool grants or bypass approval.

Approval 必须绑定 Subject、Tenant、Tool、ToolVersion、Arguments、Effect Scope、SecurityEpoch 和
Expiry。任何 revoke、Secret revoke、Tool version、Arguments 或 SecurityEpoch 变化都必须重新授权。
Tool/Sandbox 的 Target Effect 状态包括 `proposed`、`validated`、`authorized`、
`approval_required`、`ready`、`executing`、`succeeded`、`failed_known`、`outcome_unknown`、
`reconciling` 和 `manual_review`；timeout 不等于 failed，未知结果必须先对账。

## Verifiability target

不声称开源天然安全或外部 Host 天然不安全。Target/Hypothesis 是可提供 Source Audit、Build Reproducibility、SBOM、Signed Artifact、No-egress/Allowlist evidence、Secret/Model/Tool/Domain/Human trace、Sandbox boundary test 和 cross-tenant proof。

## Current / Target / Gap

- Current：repository has security modules, grants/epochs/audit target and Docker controls；完整多服务安全证据未建立。
- Target：security decision authority + enforcement in every service and worker；保留独立 Sandbox
  Boundary，但 Docker/Deno 或其他执行 Provider 仍待外部资格测试。
- Gap：offline egress、secret leakage、tenant isolation、revocation、sandbox escape、duplicate side effect、artifact attestation。
