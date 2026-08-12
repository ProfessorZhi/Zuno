# Security Architecture：谁可以做什么？

status: normative-target
architecture_state: ACCEPTED_TARGET
canonical_question: 身份、权限、Secret、Sandbox、网络和副作用如何形成可验证边界？
owner: Security Decision Owner
replaces: `docs/project/modules/09-security.md`（Superseded）

## Part A — Architecture Narrative

法律场景的安全目标不是拥有最多的安全名词，而是让每一次读取、模型调用和外部动作都能说明
谁在什么 Matter/Scope 下、以哪一版权限、对哪个对象做了什么。Prompt Injection 属于不可信内容，
不能改变 Grant；Agent 可以提出 Action，但不能自己扩展 Tool 权限、读取 plaintext Secret 或批准
不可逆副作用。

以“案件文档诱导 Agent 调用外部 API”为例，系统先把任务和权限 downscope，生成绑定参数和范围
的 PreparedAction，执行前按当前 SecurityEpoch 重新授权，必要时等待人工 Approval，最后由 Sandbox
执行并记录 EffectReceipt。撤权、参数、ToolVersion 或 Secret 变化会使旧批准失效。timeout 不能
直接视为失败或安全重试，因为 provider 可能已经执行。

这条链会增加授权检查和审计成本，但比“模型输出一段调用参数，服务直接执行”更可验证。安全
差异的目标是 Source Audit、Build Reproducibility、No-egress、Secret Trace、Sandbox Boundary
和 Cross-tenant Evidence；在这些证据出现前，不能宣称当前系统已经安全或生产合规。

## Part B — Detailed Architecture Specification

### Authorization and effect contract

`PreparedAction` 必须绑定 canonical action hash、Subject、Tenant、Scope、ToolVersion、Arguments、
EffectScope、SecurityEpoch、Approval 和 Expiry。执行前重新授权，执行后写 EffectReceipt、provider
operation ID 和 durable audit。任何 revoke、参数/版本/Secret 变化都使旧批准失效；timeout 进入
outcome_unknown/reconciling/manual_review，不直接 retry 不可逆动作。所有服务和 worker 都执行同一
策略，Prompt Injection 永远不能改变 policy decision。

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
