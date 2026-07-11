# Program Roadmap

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-unified-agent-runtime-closure-v1

## 最近完成 Program

`zuno-unified-agent-runtime-closure-v1` 已归档到：

- `docs/history/programs/zuno-unified-agent-runtime-closure-v1/`

关闭状态：

```text
implementation_complete_measurement_blocked
```

PHASE01-PHASE13 已完成本地 implementation baseline。PHASE13 没有获得 fixed benchmark measured pass，原因是 sample-8 profile runner 配置不可用且 sample-80 没有 tracked fixed set。

## 后续 Program 入口

当前没有 active program。下一轮如果要继续质量闭环，应新开短 program，从 PHASE01 开始冻结：

1. local embedding / model profile runner 配置。
2. tracked fixed sample-80 case set。
3. standard/deep/agentic 同 case set resume 策略。
4. release gate pass/fail/block 输出位置。

## 不变关闭定义

1. 目标代码进入唯一 owner。
2. focused unit/integration tests 通过。
3. 至少一个真实或 deterministic vertical scenario 通过。
4. trace 能说明关键决策和失败。
5. 需要 restart 证明的 Phase 必须重建进程后读取。
6. Current/Target 文档按事实更新。
7. `git diff --check` 通过。
8. 不以 mock/fixture/prepared/partial profile 结果冒充 measured quality。
