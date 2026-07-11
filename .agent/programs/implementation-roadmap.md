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

当前没有 active program。当前 queued candidate 是：

- `.agent/programs/queued-programs/PROGRAM01_real-unified-runtime-cutover.md`

它适合作为下一轮实现 program，但必须先从 PHASE01 激活为 active truth source，不能直接按 queued 文档跳到 runtime 大改。

下一轮如果要继续真实统一 runtime cutover，应从 PHASE01 开始冻结：

1. 当前 runtime 主路径事实：compiled graph、manual loop、deterministic executor、canned answer、sidecar workspace、blocked benchmark。
2. `verify_real_runtime_cutover.py` guardrail。
3. LangGraph 是否真正成为唯一执行引擎。
4. RuntimeDependencyFactory、Model Gateway、Memory、Knowledge、Tool 的真实依赖装配。
5. Completion / Workspace 默认路径和 rollback flag。
6. benchmark pass / fail / blocked 输出位置。

## 不变关闭定义

1. 目标代码进入唯一 owner。
2. focused unit/integration tests 通过。
3. 至少一个真实或 deterministic vertical scenario 通过。
4. trace 能说明关键决策和失败。
5. 需要 restart 证明的 Phase 必须重建进程后读取。
6. Current/Target 文档按事实更新。
7. `git diff --check` 通过。
8. 不以 mock/fixture/prepared/partial profile 结果冒充 measured quality。
