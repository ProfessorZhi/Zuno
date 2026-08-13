# Red / Blue Workflow Status

```text
RED_BLUE_STATE: RESET
ACTIVE_PROTOCOL: NONE
ACTIVE_ROUND: NONE
ROUND_007: CANCELLED_BEFORE_START
NEXT_ROUND: NOT_SCHEDULED
ARCHITECTURE_READABILITY_GATE: IN_PROGRESS
FINAL_MODULE_COUNT: NOT_DECIDED
```

## 本轮边界

- V2–V4.2 协议和 Round-001–Round-006 是历史，不再是 active protocol。
- Round-007 在启动前取消；没有新的 Red Session、Blue Session、Question Set 或 Candidate Branch。
- 不修改不可变会话、历史分数、历史严重度、历史回答和历史收口结论。
- 不通过 Red/Blue 增加 Canonical Architecture 复杂度。

## Architecture Readability Gate

下一代对攻前，Canonical Architecture 至少应让一名第一次阅读的高级工程师理解：

- 产品为什么存在，以及什么仍只是 Target/Hypothesis；
- Domain State、Knowledge、Memory、Runtime State 和 Tool Effect 的边界；
- 谁拥有每类状态，失败如何恢复，替代方案是什么；
- 逻辑能力、物理服务、Worker、数据存储和团队边界为什么不一一映射；
- 如何用 Benchmark、Security Evidence 和运行证据证明或删除复杂度。

这是一项可读性门，不是新的架构决策，也不是 Production Readiness 证明。

## 入口规则

需要考古时先读 [`history/README.md`](history/README.md)，需要看不可变执行记录时读
[`../sessions/`](../sessions/)。新的 Protocol 尚未设计；任何启动、题集、Session 或
Candidate 行为都必须等待用户明确激活。
