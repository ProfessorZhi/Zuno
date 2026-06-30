# PHASE05 Agent Runtime LangGraph Harness

status: pending

## 目标

把当前 `GeneralAgent` single loop 推进为 Single Controller Agent Runtime 的产品级 harness，目标链路为 `prepare_context -> plan -> ReAct -> observe -> reflect -> replan -> post_turn_commit`。

## 步骤

- [ ] 定义 runtime state model，包含 thread、workspace、goal、context pack、plan、current step、observations、tool calls、retrieval events、approval interrupts、trace id、memory candidates 和 artifact refs。
- [ ] 写最小 state graph / harness contract。
- [ ] 接入 streaming、checkpoint、interrupt/resume 和 failure handling。
- [ ] 保持 LangGraph 是 runtime orchestration candidate，不是“规划模块本身”。
- [ ] 写 focused runtime tests，证明单控制器循环和 post-turn commit。

## 验收

- Runtime loop 可被测试、可追踪、可中断、可恢复。
- Planning、ReAct、Reflection、Replan 是 Agent Core Runtime 内部控制能力。
- 不引入默认产品级多 Agent runtime。

## 验证

```powershell
pytest -q tests/agent/test_*runtime*.py tests/agent/test_generalagent_context_memory_runtime.py -p no:cacheprovider
```
