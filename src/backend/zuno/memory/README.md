# Memory 层边界

分类：`target-layer`

## 当前角色

`src/backend/zuno/memory/` 目前是 memory foundation、PHASE09 memory runtime 与 Program 3 Mega PHASE05 Memory & Context Engine baseline 的目标层入口，已经提供 `contracts.py`、`store.py`、`policy.py`、`review.py`、`retrieval.py`、`rendering.py` 和 `engine.py`。PHASE06 已在 `engine.py` 固定 memory taxonomy、MemoryEngine read/write/manage API、Context Pack renderer、敏感候选过滤和 memory eval policy。PHASE07 进一步在 `store.py` 和 `engine.py` 提供 `DurableMemoryStore`、`MemoryStoreSnapshot`、`MemoryGovernanceLedgerEntry`、跨 task snapshot/replay、approved durable memory、promotion、decay、consolidation、敏感候选治理记录和 Context Pack include/exclude reason。PHASE09 已补 `DeterministicSemanticMemoryAdapter` local semantic fallback、GeneralAgent semantic memory read、scoped privacy delete、redacted governance ledger、sensitive context exclusion 和 memory eval baseline。Program 3 Mega PHASE05 已补 `MemoryEngine.build_context_pack()`、structured extraction、hierarchical summary、evidence-bound summary、budget-aware packing、stale / conflict / revoked / sensitive exclusion reason 和 ReflexionLesson pending review path。

当前底层对象仍复用 legacy-compatible foundation：`zuno.services.memory.layers`；物理基础位于 `src/backend/zuno/platform/services/memory/layers.py`。PHASE09 的 Current 是可导出、可重建、可审查、可按 scope 删除的本地 memory runtime surface，并带 deterministic semantic fallback；它不是 production-grade Memory DB，也不是外部向量记忆库、长期后台 consolidation job、跨备份隐私删除平台或 nightly memory eval 平台。

## Target role

目标状态下，Memory 层负责上下文前的可检索记忆、对话后的 raw event 追加、summary compression、structured extraction 和 source event 追踪。它不等同于聊天历史拼接，也不拥有外部知识检索本体。

## 允许新增内容

- 无副作用的 memory contract、scope、policy、trace 类型。
- 指向 `platform/services/memory` foundation owner 的薄入口和 README 边界说明。
- local deterministic semantic fallback、privacy delete 和 memory eval baseline 的小步增强；外部 DB / vector / scheduler 必须保持 adapter 或 Target 边界。

## 禁止事项

- 禁止把 local fallback 写成生产级外部向量记忆库或企业隐私删除平台。
- 禁止破坏 `zuno.services.memory.*` 旧 import path。
- 禁止把成熟记忆提取、检索、合并能力写成已经完成的 Current runtime。

## Focused tests

- `tests/repo/test_backend_facade_layers.py`
- `tests/agent/test_memory_layer_surfaces.py`
- `tests/agent/test_memory_layers.py`
- `tests/memory/test_context_pack_engine.py`
- `tests/agent/test_memory_system_contract.py`
- `tests/agent/test_generalagent_context_memory_runtime.py`
- `tests/legacy_guards/test_zuno_alias_imports.py`
- `tests/repo/test_static_target_layer_imports.py`
