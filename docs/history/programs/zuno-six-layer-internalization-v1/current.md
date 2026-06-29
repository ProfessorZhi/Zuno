# 归档时 Program 状态

> 归档说明：此文件是 `zuno-six-layer-internalization-v1` 关闭时保存的历史状态面，不代表当前 active program。

## Program

```text
zuno-six-layer-internalization-v1
```

状态：completed / archived。

## 完成事实

`src/backend/zuno` 顶层仍只保留 `api / agent / memory / capability / knowledge / platform`、`__init__.py` 和 `main.py`。

六层内部第一批 thin surfaces 已完成：

- `agent/`：runtime、context、post_turn、state、streaming、tool_bridge。
- `memory/`：contracts、store、policy、review、retrieval、rendering、engine。
- `capability/`：contracts、registry、selector、policy、execution、trace。
- `knowledge/`：contracts、query_service、evidence、citation、trace、retrieval、fusion、graphrag。
- `platform/`：model_gateway、security、observability、storage。

旧 public import path 仍由 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 保护。

## 未完成边界

这些仍是后续 runtime architecture upgrade 的候选，不是本 program 的完成事实：

- production-grade memory extraction / retrieval / consolidation
- DB-backed Memory runtime
- Native BM25 capability search
- production-grade dynamic capability orchestration
- full evidence fusion / RRF / rerank runtime
- GraphRAG LLM entity / relation extraction production path
- model gateway 默认 provider 行为改造
