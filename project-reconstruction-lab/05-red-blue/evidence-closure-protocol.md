# Evidence Closure Protocol V1

## 目的

本协议用于把 Red/Blue 发现的关键架构风险转化为可执行、可审计、可反驳的证据闭合任务。
它不是新的架构事实源，也不把静态文档、计划、类名或复杂度卡当作运行证据。

适用范围：

- Blue Repair 后仍未闭合的 P0/P1 风险；
- Domain State、Runtime State、审批、证据引用、Tool Effect、Sandbox、Recovery 等高风险边界；
- 不改变产品 Runtime 行为的 focused spike、contract test、fault-injection test、recovery test、benchmark harness 或模型验证。

## 事实与状态边界

事实状态与架构状态不能互换：

```text
USER_CONFIRMED / USER_PARTIAL_RECALL / ARTIFACT_EVIDENCE
PARTIAL_REPOSITORY_EVIDENCE / PUBLIC_CONTEXT
RECONSTRUCTED_CANDIDATE / CONTRADICTED / UNKNOWN
TARGET_ONLY / FUTURE
```

架构状态：

```text
PROPOSED → UNDER_ATTACK → SURVIVED / REJECTED / DEFERRED
         → ACCEPTED_TARGET → IMPLEMENTED → MEASURED → PRODUCTION_PROVEN
```

`ACCEPTED_TARGET` 不等于 `IMPLEMENTED`，`MEASURED` 不等于 `PRODUCTION_PROVEN`。

## Evidence Ladder

| 等级 | 含义 | 本轮可否单独闭合 P0 |
|---|---|---|
| V0 | 设计 prose、论证、ADR | 否 |
| V1 | Claim 到 Owner/Requirement 的可追溯性 | 否 |
| V2 | 静态检查、契约模型、状态模型 | 否 |
| V3 | 可执行 focused spike/contract/recovery test | 通常否，只能证明窄命题 |
| V4 | 集成、并发、故障注入、跨边界恢复 | 可作为 Target closure 输入 |
| V5 | 代表性 benchmark、质量/效率/安全对照 | 可作为能力或收益 closure 输入 |
| V6 | 生产运行证据 | 本 Program 不要求，但生产声明需要 |

本轮没有 V3–V5 证据的 P0 不能声称闭合；即使有 V3，也必须标明它没有覆盖分布式、生产或真实法院环境。

## P0 Closure Gate

一个 P0 只有同时满足以下条件才允许 `CLOSED`：

1. Verification 已实际执行，而不是只写计划；
2. 原始输出、测试结果或可复现 Artifact 已保存；
3. Red Evidence Review 接受证据范围，或明确收窄 Claim；
4. Counter Retest 已执行并通过；
5. 没有未解决的事实、集成、权限、恢复或环境阻塞。

允许的证据会话状态：

```text
UNPLANNED
PLAN_READY
READY_TO_EXECUTE
EXECUTED_PASS
EXECUTED_FAIL
BLOCKED_EXTERNAL
BLOCKED_FACT
USER_GATE_REQUIRED
RED_REVIEW_PENDING
COUNTER_RETEST_PENDING
CLOSED
```

`EXECUTED_PASS` 只表示命令或测试通过，不表示 P0 已闭合。

## Evidence Matrix Contract

每一个最终 P0 必须在同一张矩阵中具有唯一行，字段固定为：

```text
Evidence ID
Root Cause ID
P0 ID
Architecture Claim
Risk
Closure Condition
Required Evidence
Evidence Strength Target
Verification Method
Environment
Inputs
Expected Result
Failure Result
Artifact Path
Owner
Status
Red Review
Blue Action
Counter Retest
Final Closure
```

矩阵中的 `Plan`、`Expected Result`、`Mermaid` 和 `ADR` 只能说明如何验证，不能替代 `Artifact Path` 指向的实际结果。

## 工作规则

1. 沿用 `RC-001` 到 `RC-010`，不因证据战役创建平行根因分类；
2. 复杂度卡只能提出要测什么，不能把“存在一个组件”当作收益证据；
3. 运行测试必须明确环境、输入、预期、失败判定和限制；
4. 失败和阻塞同样是有效结果，必须保存原始原因；
5. 本轮不修改业务 Runtime、UI、Schema/Migration、依赖或生产 Infra；
6. Canonical Docs 只有在全部最终 P0 通过 User Architecture Gate 后才允许同步；
7. 历史事实缺口回到 Facts / Evidence Ledger，不由架构证据包填空。

## 会话输出

每次 Evidence Closure Session 至少包含：

- 会话 README 与 manifest；
- P0 Evidence Closure Matrix；
- 每个 P0 的证据包；
- Verification Plan 与命令日志；
- Evidence Level 统计；
- Red Evidence Review；
- Blue Actions；
- Counter Retest；
- Scorecard 与 Closure Report。
