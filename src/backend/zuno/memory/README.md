# Memory 层边界

分类：`target-layer`

## 当前角色

`src/backend/zuno/memory/` 目前是 memory foundation 与 PHASE07 memory runtime 的目标层入口，已经提供 `contracts.py`、`store.py`、`policy.py`、`review.py`、`retrieval.py`、`rendering.py` 和 `engine.py`。PHASE06 已在 `engine.py` 固定九类 memory taxonomy、MemoryEngine read/write/manage API、Context Pack renderer、敏感候选过滤和 memory eval policy。PHASE07 进一步在 `store.py` 和 `engine.py` 提供 `DurableMemoryStore`、`MemoryStoreSnapshot`、`MemoryGovernanceLedgerEntry`、跨 task snapshot/replay、approved durable memory、promotion、decay、consolidation、敏感候选治理记录和 Context Pack include/exclude reason。

当前底层对象仍复用 legacy-compatible foundation：`zuno.services.memory.layers`；物理基础位于 `src/backend/zuno/platform/services/memory/layers.py`。PHASE07 的 Current 是可导出、可重建、可审查的本地 memory runtime surface；它不是 production-grade Memory DB，也不是外部向量记忆库、长期后台 consolidation job 或隐私删除平台的物理迁移完成。

## Target role

目标状态下，Memory 层负责上下文前的可检索记忆、对话后的 raw event 追加、summary compression、structured extraction 和 source event 追踪。它不等同于聊天历史拼接，也不拥有外部知识检索本体。

## 允许新增内容

- 无副作用的 memory contract、scope、policy、trace 类型。
- 指向 `platform/services/memory` foundation owner 的薄入口和 README 边界说明。
- 不触碰持久化和 runtime 行为的小型 wrapper。

## 禁止事项

- 禁止直接迁移 DB-backed memory、事件存储、summary 写入或 GeneralAgent memory runtime。
- 禁止破坏 `zuno.services.memory.*` 旧 import path。
- 禁止把成熟记忆提取、检索、合并能力写成已经完成的 Current runtime。

## Focused tests

- `tests/repo/test_backend_facade_layers.py`
- `tests/agent/test_memory_layer_surfaces.py`
- `tests/agent/test_memory_layers.py`
- `tests/agent/test_memory_system_contract.py`
- `tests/agent/test_generalagent_context_memory_runtime.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/repo/test_static_target_layer_imports.py`
