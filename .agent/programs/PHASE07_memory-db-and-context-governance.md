# PHASE07 memory-db-and-context-governance

status: pending

## 目标

把 MemoryEngine 从 in-memory foundation 升级为持久 memory runtime，支持跨任务读写、审查、脱敏和可追责。

## 范围

- 实现 raw event log、task summary、approved durable memory、promotion、decay、consolidation。
- 维护 source_event_ids、task_id、trace_id、workspace_id 的持续可追溯关系。
- 接入敏感信息隔离和 memory eval policy。

## 禁止范围

- 不把 InMemoryLayerStore 写成 production Memory DB。
- 不把未经 review 的敏感 candidate 写入长期记忆。
- 不让 memory 绕过 Context Pack renderer。

## 验收闸门

- tests 能跨 task 写入、审批、检索和解释 memory。
- 敏感 candidate 默认排除，除非显式 approval。
- Context Pack 能说明每条 memory 被包含或排除的原因。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_memory_system_contract.py tests/agent/test_memory_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py -p no:cacheprovider
```

