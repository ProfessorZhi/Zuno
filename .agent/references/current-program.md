# 当前 Program 状态

## Current Truth

当前 active program：

```text
zuno-six-layer-internalization-v1
```

state: active

当前 active phase：

- `.agent/programs/PHASE02_memory-layer-foundation-surfaces.md`

`.agent/programs/` 当前保留：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
- `PHASE01_six-layer-current-inventory.md`
- `PHASE02_memory-layer-foundation-surfaces.md`
- `closure-checklist.md`

## 最近完成事实

Program 3 / `zuno-repo-layout-cleanup-v1` 已完成六层顶层目录收口和 final alias surface closure：`src/backend/zuno` 顶层目录已经收敛为：

- `api/`
- `agent/`
- `memory/`
- `capability/`
- `knowledge/`
- `platform/`

根目录只保留：

- `__init__.py`
- `main.py`

旧 public import path 由 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 注册兼容。

## 当前 Program 目标

`zuno-six-layer-internalization-v1` 负责让六层内部逐步拥有清晰、可测试、无副作用的目标层入口。

当前先处理 `memory/`：

- `contracts.py`
- `store.py`
- `policy.py`
- `review.py`
- `retrieval.py`
- `rendering.py`
- `engine.py`

这些入口复用 `zuno.services.memory.layers` foundation objects；物理实现位于 `src/backend/zuno/platform/services/memory/layers.py`。这不表示 production-grade memory extraction、retrieval、consolidation 或 Memory DB 已完成。

## 等待打开

queued draft / not active：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`
