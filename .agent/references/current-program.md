# 当前 Program 状态

## Current Truth

当前没有 active program。

state: no-active

`.agent/programs/` 当前保留：

- `README.md`
- `current.md`
- `implementation-roadmap.md`
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

## 最近完成事实

Program 4 / `zuno-six-layer-internalization-v1` 已完成并归档到：

- `docs/history/programs/zuno-six-layer-internalization-v1/`

它让六层内部拥有第一批清晰、可测试、无副作用的目标层入口：

- `agent/`：runtime、context、post_turn、state、streaming、tool_bridge。
- `memory/`：contracts、store、policy、review、retrieval、rendering、engine。
- `capability/`：contracts、registry、selector、policy、execution、trace。
- `knowledge/`：contracts、query_service、evidence、citation、trace、retrieval、fusion、graphrag。
- `platform/`：model_gateway、security、observability、storage。

这些入口复用现有 runtime owner 或 compatibility owner。这不表示 production-grade memory extraction、retrieval、consolidation、Memory DB、dynamic capability orchestration、retrieval fusion 或 Runtime Architecture Upgrade 已完成。

## 等待打开

queued draft / not active：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`：target blueprint 已刷新为任务到交付物主链路；`overview.html` / Mermaid 生成展示仍是 queued follow-up。
