# Red / Blue Architecture Adversarial Review

```text
status: RESET / PAUSED
active_protocol: NONE
next_protocol: NOT_DESIGNED
architecture_readability_gate: REQUIRED
```

## 这是什么

Red / Blue 用来攻击和防守架构候选：Red 追问必要性、边界、Owner、状态、失败、恢复、
安全、规模、成本、替代方案和证据；Blue 解释最小可行设计，并接受反击。

它不是项目事实源，也不是 Canonical Architecture。事实、Current 证据和正式 Target 仍由
`docs/` 的 Owner 文档维护。

## 为什么暂停

上一代 V2–V4.2 协议和 Round-001–Round-006 都保留为历史证据，但 active 入口已经累积了
题量、配额、Session、Profile 和 Closure 规则。继续沿用它们会把旧假设误当成下一代协议。
当前先完成 Canonical Architecture 的可读性重构，再设计新的 VNext Protocol。

本轮不生成题集、不创建 Red/Blue Session、不启动 Round-007、不修改 Facts、ADR、Runtime、
Schema、Migration、Dependencies 或 Production Infra。

## 当前状态

```text
RED_BLUE_STATE: RESET
ACTIVE_PROTOCOL: NONE
ACTIVE_ROUND: NONE
ROUND_007: CANCELLED_BEFORE_START
NEXT_ROUND: NOT_SCHEDULED
ARCHITECTURE_READABILITY_GATE: IN_PROGRESS
FINAL_MODULE_COUNT: NOT_DECIDED
```

## 下一步

只有在 Architecture Baseline 能被新工程师用普通工程语言解释之后，才设计下一代 Protocol。
下一代的题量、Profile、Session API 和 verifier 不在本入口预设。

稳定原则见 [`principles.md`](principles.md)，当前暂停态见 [`workflow-status.md`](workflow-status.md)。
历史协议和操作材料见 [`history/README.md`](history/README.md)，不可变会话仍在
[`../sessions/`](../sessions/) 中。
