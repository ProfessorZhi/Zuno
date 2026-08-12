# Blue Repair Protocol V1

## 定位

Blue Repair 是一个独立于新一轮提问的修复阶段。它处理上一轮已经暴露的根因，不通过继续
增加问题数量制造“进展”。标准顺序是：

```text
Round Discovery
→ Root-Cause Clustering
→ Blue Repair
→ Severity Reclassification
→ P0 Burn-down
→ Counter Retest
→ Round Closure
→ User Architecture Gate
→ Canonical Sync
→ Next Round
```

没有完成 Counter Retest 和 Round Closure，不得启动下一轮 100Q。

## 严重度生命周期

上一轮的 Severity 只表示提问时的初始攻击优先级。Repair 阶段必须增加两个字段：

```text
Question Pre-Severity
  ↓ Blue Answer / Repair
Red Impact Assessment
  ↓
Final Severity
```

`P0` 只用于会直接击穿关键安全或一致性不变量的问题，例如 Canonical State 双 Owner、
不可逆副作用重复执行、审批/安全绕过、PlanVersion 并发冲突、未知 Effect 无法恢复、
证据或 Citation 错绑。Provider 选型、服务数量、技术品牌和一般流程问题默认从 P1/P2
开始，除非答案暴露出上述 Critical Failure。

Severity 重分类不是 Gap Closure。`Final P0` 仍需 Counter Retest 和相应 Evidence 才能关闭。

## 五指标与 Gate

Repair 阶段不制造一个总分。至少报告：

| 指标 | 定义 |
|---|---|
| Answer Quality | Round-001 的回答防守度；没有重新回答时保持基线值 |
| Architecture Fitness | 设计覆盖能力的基线参考；不能解释为质量证明 |
| Evidence Coverage | 需要的 Fact、Benchmark、Runtime、Security 或 Eval Evidence 中已实际获得的比例 |
| Critical Closure | `1 - 未关闭 Final P0 / Final P0 总数`；只有有证据的 Retest 才能关闭 |
| Complexity Justification | 复杂度卡中 Problem、Alternative、Owner、State、Failure、Deletion、Validation 的完成度 |

最终状态由 Gate 决定，而不是由平均分决定：

```text
P0 = 0
Part A 无核心矛盾
Canonical Ownership 闭合
Critical Failure Paths 有可执行 Contract
Counter Retest 完成
User Architecture Gate 通过
```

## Repair 边界

- Blue 可以替换 Provider、收缩 Runtime、改变 Service Boundary 和删掉默认复杂度。
- Blue 必须保留 Domain State、Runtime Control、Knowledge Projection、Memory Policy、Tool Effect
  Receipt 等边界候选，直到更简单方案通过 Kill Test。
- 本阶段只写 Lab Session、候选 Contract、Gap 和 Retest；不修改 Runtime、UI、Schema/Migration、
  生产 Infra 或 Canonical Architecture。
- 没有真实运行证据时，`REOPEN` 或 `WAITING_FOR_EVIDENCE` 是正确结果，不得写成 `PASS`。
