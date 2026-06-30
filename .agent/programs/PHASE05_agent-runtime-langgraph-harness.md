# PHASE05 Agent Runtime LangGraph Harness

status: completed

## 目标

把当前 `GeneralAgent` single loop 推进为 Single Controller Agent Runtime 的产品级 harness，目标链路为 `prepare_context -> plan -> ReAct -> observe -> reflect -> replan -> post_turn_commit`。

## 步骤

- [x] 定义 runtime state model，包含 thread、workspace、goal、context pack、plan、current step、observations、tool calls、retrieval events、approval interrupts、trace id、memory candidates 和 artifact refs。
- [x] 定义节点表：`prepare_context`、`intent_and_policy_route`、`plan`、`act_react_loop`、`observe`、`evidence_check`、`reflect`、`replan_if_needed`、`answer_or_artifact`、`post_turn_commit`。
- [x] 为每个节点写输入、输出、trace span、失败处理和 checkpoint 行为。
- [x] 写最小 state graph / harness contract。
- [x] 接入 streaming、checkpoint、interrupt/resume 和 failure handling。
- [x] 保持 LangGraph 是 runtime orchestration candidate，不是“规划模块本身”。
- [x] 定义 model gateway 使用点：planner、executor、critic、embedding、rerank、vision/OCR，只把已实现部分写 Current。
- [x] 写 focused runtime tests，证明单控制器循环和 post-turn commit。

## 输入 / 输出文件

输入：

- `src/backend/zuno/agent/**`
- `src/backend/zuno/api/**`
- `src/backend/zuno/memory/**`
- `src/backend/zuno/knowledge/**`
- `src/backend/zuno/capability/**`

输出：

- runtime state contract。
- state graph / harness entrypoint。
- streaming event bridge。
- checkpoint / interrupt / resume contract。
- focused runtime tests。

## 依赖与阻塞

- 依赖 PHASE03 的 `Task` / `Session` / event contract。
- PHASE06 Memory、PHASE07 Tool、PHASE08 Retrieval、PHASE09 Security 都必须挂到本 phase 的 runtime state。
- 未完成 checkpoint / interrupt / resume 前，不能把 runtime 写成 production-grade LangGraph Current。

## 验收

- Runtime loop 可被测试、可追踪、可中断、可恢复。
- Planning、ReAct、Reflection、Replan 是 Agent Core Runtime 内部控制能力。
- 不引入默认产品级多 Agent runtime。
- 只有 focused runtime tests 通过并产生 trace/evidence 证据后，才允许把对应节点写入 Current；LangGraph 依赖存在不等于深度使用完成。

## 验证

```powershell
pytest -q tests/agent/test_*runtime*.py tests/agent/test_generalagent_context_memory_runtime.py -p no:cacheprovider
```

## 完成证据

- `src/backend/zuno/agent/harness.py` 定义 `ControllerRuntimeState`、`RuntimeNodeContract`、`RuntimeCheckpoint`、`RuntimeInterrupt` 和 `SingleControllerRuntimeHarness`。
- Runtime node order 固定为 `prepare_context -> intent_and_policy_route -> plan -> act_react_loop -> observe -> evidence_check -> reflect -> replan_if_needed -> answer_or_artifact -> post_turn_commit`。
- Checkpoint、interrupt / resume 和 stream event bridge 都绑定 `trace_id`、`task_id`、`thread_id` 与 `workspace_id`。
- `tests/agent/test_single_controller_runtime_harness.py` 覆盖 node contract、edge order、checkpoint、interrupt、stream event 和 resume。
- `tests/agent/test_generalagent_context_memory_runtime.py` 继续证明现有 `GeneralAgent` single loop、context trace、post-turn memory commit 和 RuntimeTurnLedger 没有被破坏。
- Current 边界：PHASE05 完成 runtime harness contract，不表示生产级 durable LangGraph runtime 已经替换主循环。
