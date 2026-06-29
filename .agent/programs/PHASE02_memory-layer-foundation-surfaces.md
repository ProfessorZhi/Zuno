# PHASE02 Memory 层 Foundation Surfaces

状态：in progress

## 目标

让 `src/backend/zuno/memory/` 不再只是 `__init__.py` facade，而是拥有一组符合目标架构语言的薄入口，同时不改变现有 memory runtime 行为。

## 范围

允许新增或修改：

- `src/backend/zuno/memory/contracts.py`
- `src/backend/zuno/memory/store.py`
- `src/backend/zuno/memory/policy.py`
- `src/backend/zuno/memory/review.py`
- `src/backend/zuno/memory/retrieval.py`
- `src/backend/zuno/memory/rendering.py`
- `src/backend/zuno/memory/engine.py`
- `src/backend/zuno/memory/__init__.py`
- `src/backend/zuno/memory/README.md`
- memory focused tests
- current program docs

## 禁止范围

- 不改 DB-backed memory。
- 不改 `GeneralAgent` memory runtime。
- 不改 API 行为。
- 不删除 `zuno.services.memory.*`。
- 不把 production-grade extraction / retrieval / consolidation 写成已完成。

## 设计

Memory 当前 foundation objects 仍来自 `zuno.services.memory.layers`；物理实现位于 `src/backend/zuno/platform/services/memory/layers.py`。

本 phase 只建立目标层入口：

- `contracts.py`：MemoryLayer、MemoryScope、RawMemoryEvent、TaskMemorySummary、MemoryCandidate、ExternalKnowledgeRecord。
- `store.py`：InMemoryLayerStore。
- `policy.py`：RetentionPolicy。
- `review.py`：ExternalKnowledgeRecord 与 MemoryCandidate 的 promotion / candidate review 入口。
- `retrieval.py`：当前只公开可查询 foundation store 与 candidate/scope 类型。
- `rendering.py`：当前只公开 raw event 与 task summary 渲染所需类型。
- `engine.py`：当前只公开 foundation store、raw event 和 task summary，不声明生产 engine 已完成。

## 验收

- `zuno.memory.*` 新模块可导入。
- 新模块导出的对象与 `zuno.services.memory.layers` 对象一致。
- 导入 `zuno.services.memory.layers` 不 eager load `zuno.services.memory.client`。
- `src/backend/zuno/memory/README.md` 不再指向不存在的 `src/backend/zuno/services/memory/` 物理路径。

## 验证

```powershell
pytest -q tests/agent/test_memory_layer_surfaces.py tests/agent/test_memory_layers.py -p no:cacheprovider
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
git diff --check
```
