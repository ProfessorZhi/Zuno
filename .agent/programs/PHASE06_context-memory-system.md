# PHASE06 Context Memory System

status: pending

## 目标

落地 Context / Memory 的 write-manage-read 子系统，让 Agent 不只是读当前对话，而能有可治理的短期、摘要和结构化长期记忆。

## 步骤

- [ ] 定义 Raw Event Log、Working Context、Recent Window、Task Summary、Structured Long-term Memory、Graph Memory candidate。
- [ ] 定义 Context Pack renderer 和 budget policy。
- [ ] 定义 post-turn extraction、dedupe/conflict、review、promotion、decay、discard。
- [ ] 增加敏感信息过滤和 memory eval。
- [ ] 写 memory layer tests。

## 验收

- Memory read path 和 write path 清晰分离。
- 可证明哪些内容会进入下一轮 context，哪些只是 trace。
- 生产级 Memory DB 未完成前不写成 Current。

## 验证

```powershell
pytest -q tests/agent/test_memory_layers.py tests/agent/test_memory_layer_surfaces.py tests/agent/test_context_orchestrator.py -p no:cacheprovider
```
