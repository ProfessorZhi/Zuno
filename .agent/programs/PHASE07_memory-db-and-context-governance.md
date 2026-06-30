# PHASE07 memory-db-and-context-governance

status: completed

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

## 完成证据

- `src/backend/zuno/memory/store.py` 新增 `DurableMemoryStore`、`DatabaseMemoryStore`、`MemoryStoreSnapshot` 和 `MemoryGovernanceLedgerEntry`。
- `src/backend/zuno/platform/database/models/memory_runtime.py` 新增 raw event、task summary、memory candidate、review decision 和 governance ledger 五张 SQLModel 表。
- `MemoryEngine` 已支持 snapshot/replay、DB-backed store、approved durable memory、sensitive candidate exclusion、review ledger、external knowledge promotion、decay、consolidation 和 Context Pack include/exclude reasons。
- `GeneralAgent` 已通过 `MemoryEngine` 写入 post-turn memory，并可通过 DB-backed store 跨 agent instance 读取 task summary 与 approved memory。
- `tests/agent/test_memory_durable_runtime.py` 覆盖 snapshot round-trip、DB-backed cross-instance persistence、sensitive exclusion、promotion、decay、consolidation。
- `tests/agent/test_generalagent_context_memory_runtime.py` 覆盖 GeneralAgent 跨实例 DB-backed memory read/write。
- `tests/storage/test_database_schema.py` 证明 PHASE07 memory runtime 表已注册到 SQLModel metadata。

## Current / Target 边界

Current 是本地 snapshot/replay 与 SQLModel-backed memory runtime adapter；不是 production-grade vector/semantic Memory DB、后台 decay/consolidation scheduler、深度 PII/secret detection、隐私删除平台或完整 memory eval baseline。

## 验证命令

```powershell
git diff --check
pytest -q tests/agent/test_memory_system_contract.py tests/agent/test_memory_layer_surfaces.py tests/agent/test_generalagent_context_memory_runtime.py -p no:cacheprovider
```
