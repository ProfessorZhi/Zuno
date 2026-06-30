# PHASE05 Agent Runtime LangGraph Harness

status: pending

## 目标

把当前 `GeneralAgent` single loop 推进为 Single Controller Agent Runtime 的产品级 harness，目标链路为 `prepare_context -> plan -> ReAct -> observe -> reflect -> replan -> post_turn_commit`。

## 步骤

- [ ] 定义 runtime state model，包含 thread、workspace、goal、context pack、plan、current step、observations、tool calls、retrieval events、approval interrupts、trace id、memory candidates 和 artifact refs。
- [ ] 定义节点表：`prepare_context`、`intent_and_policy_route`、`plan`、`act_react_loop`、`observe`、`evidence_check`、`reflect`、`replan_if_needed`、`answer_or_artifact`、`post_turn_commit`。
- [ ] 为每个节点写输入、输出、trace span、失败处理和 checkpoint 行为。
- [ ] 写最小 state graph / harness contract。
- [ ] 接入 streaming、checkpoint、interrupt/resume 和 failure handling。
- [ ] 保持 LangGraph 是 runtime orchestration candidate，不是“规划模块本身”。
- [ ] 定义 model gateway 使用点：planner、executor、critic、embedding、rerank、vision/OCR，只把已实现部分写 Current。
- [ ] 写 focused runtime tests，证明单控制器循环和 post-turn commit。

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
