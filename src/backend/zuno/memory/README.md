# Memory 层边界

## 当前角色

`src/backend/zuno/memory/` 承载 memory contract、scope、policy、review、retrieval、rendering 和 `MemoryEngine`。底层持久化能力由 `platform/services/memory/` 与数据库 owner 提供。

Memory 负责上下文前的受控检索、对话后的事件追加、summary compression、structured extraction 和 source event 追踪；它不拥有外部 Knowledge retrieval，也不拥有 Product API。

## 规则

- 当前实现、Target 设计和外部存储能力必须分开声明。
- 敏感候选、租户 scope、review 状态、删除和 governance ledger 必须可追踪。
- 不把 local deterministic adapter 宣称为生产级外部向量记忆库。
- 新的 memory 行为必须通过 `MemoryEngine` 与对应 store/port 进入。

## 验证入口

- `tests/agent/test_memory_layer_surfaces.py`
- `tests/agent/test_memory_layers.py`
- `tests/memory/test_context_pack_engine.py`
- `tests/agent/test_memory_system_contract.py`
