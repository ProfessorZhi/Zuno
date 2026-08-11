# Security Architecture：谁可以做什么？

status: normative-target
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

## Verifiability target

不声称开源天然安全或外部 Host 天然不安全。Target/Hypothesis 是可提供 Source Audit、Build Reproducibility、SBOM、Signed Artifact、No-egress/Allowlist evidence、Secret/Model/Tool/Domain/Human trace、Sandbox boundary test 和 cross-tenant proof。

## Current / Target / Gap

- Current：repository has security modules, grants/epochs/audit target and Docker controls；完整多服务安全证据未建立。
- Target：security decision authority + enforcement in every service and worker。
- Gap：offline egress、secret leakage、tenant isolation、revocation、sandbox escape、duplicate side effect、artifact attestation。
