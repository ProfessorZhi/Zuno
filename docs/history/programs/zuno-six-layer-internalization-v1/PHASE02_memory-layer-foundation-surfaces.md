# PHASE02 Memory 层 Foundation Surfaces

状态：completed

## 目标

让 `src/backend/zuno/memory/` 不再只是 `__init__.py` facade，而是拥有一组符合目标架构语言的薄入口，同时不改变现有 memory runtime 行为。

## 完成内容

- `contracts.py`：MemoryLayer、MemoryScope、RawMemoryEvent、TaskMemorySummary、MemoryCandidate、ExternalKnowledgeRecord。
- `store.py`：InMemoryLayerStore。
- `policy.py`：RetentionPolicy。
- `review.py`：ExternalKnowledgeRecord 与 MemoryCandidate 的 promotion / candidate review 入口。
- `retrieval.py`：当前只公开可查询 foundation store 与 candidate / scope 类型。
- `rendering.py`：当前只公开 raw event 与 task summary 渲染所需类型。
- `engine.py`：当前只公开 foundation store、raw event 和 task summary，不声明生产 engine 已完成。

## 边界

Memory foundation objects 仍复用 legacy-compatible 入口 `zuno.services.memory.layers`；物理实现位于 `src/backend/zuno/platform/services/memory/layers.py`。

本 phase 不改 DB-backed memory、`GeneralAgent` memory runtime、API 行为或旧 `zuno.services.memory.*` import path。

## 验证

```powershell
pytest -q tests/agent/test_memory_layer_surfaces.py tests/agent/test_memory_layers.py -p no:cacheprovider
```
