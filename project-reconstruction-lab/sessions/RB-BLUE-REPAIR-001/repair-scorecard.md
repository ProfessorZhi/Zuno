# RB-BLUE-REPAIR-001 Scorecard

## 评分解释

Round-001 的两个基线分数不因一次文档修复而重算：

| 指标 | Round-001 基线 | Repair 后状态 | 解释 |
|---|---:|---:|---|
| Answer Quality | 72.2 | 72.2 | 没有重新回答 100 题，不伪造分数变化 |
| Architecture Fitness | 91.4 | 91.4 | 仅作设计覆盖基线，不是架构质量证明 |
| Evidence Coverage | 未计算 | 0% closure-grade | 本 Repair 未新增 Fact/Benchmark/Runtime/Security/Eval Evidence |
| Critical Closure | 未计算 | 0/12 = 0% | Final P0 全部等待 Counter Retest；无 P0 被证据关闭 |
| Complexity Justification | 未计算 | 10/10 structural = 100%；0/10 measured | 10 个 Cluster 都有 Repair Card，但没有实验测量 |
| Round Pass | NOT_PASSED | NOT_PASSED | Critical Gate、User Gate 和 Counter Retest 仍未通过 |

“Architecture Fitness 91.4”不能被解释为“架构 91 分”。本表新增指标是为了避免两个基线
平均值掩盖 Critical Gap。

## Severity Reclassification

| 级别 | Round-001 原始 | Repair 后 Final | 含义 |
|---|---:|---:|---|
| P0 | 58 | 12 | 可能击穿关键安全/一致性不变量，必须有 Evidence 才能关闭 |
| P1 | 42 | 46 | 重要架构、产品或工程风险，未必立即杀死架构 |
| P2 | 0 | 32 | 需要设计澄清、替代比较或成本/质量验证 |
| P3 | 0 | 10 | 较低风险的 Provider、流程或表达问题 |

Severity 变化是攻击优先级校准，不是 Closure。Final P0 的关闭数仍为 `0`。

```text
Final severity: P0=12 / P1=46 / P2=32 / P3=10
```

## Final P0 Registry

| Question | Critical reason | Required closure evidence | Status |
|---|---|---|---|
| Q005 | Canonical Domain State Owner | Owner/Proposal/Version mutation test | OPEN |
| Q016 | Domain State 与 Runtime State 混淆 | crash/recovery reconciliation trace | OPEN |
| Q033 | HITL / Approval Gate 可绕过 | revoked/stale approval test | OPEN |
| Q039 | Evidence/Citation 错绑 | citation provenance and sufficiency eval | OPEN |
| Q053 | Plan/Domain concurrency conflict | generation/version conflict test | OPEN |
| Q061 | Tool authorization boundary | policy/secret/tenant enforcement test | OPEN |
| Q063 | Irreversible Effect duplicate risk | idempotency/effect receipt test | OPEN |
| Q064 | Unknown Effect cannot reconcile | provider operation/reconcile fault test | OPEN |
| Q066 | Sandbox boundary failure | escape/egress/secret isolation test | OPEN |
| Q067 | Agent Context / Tool security | injection/revocation/cross-scope test | OPEN |
| Q070 | Tool security path incomplete | end-to-end approval/audit test | OPEN |
| Q097 | Recovery state ownership | four-state crash matrix | OPEN |

## Closure Formula

```text
Critical Closure = closed final P0 / total final P0
                 = 0 / 12
                 = 0%
```

```text
Round Pass = FALSE
Reason = P0 open + evidence coverage 0% + counter retest reopened + User Gate pending
```
