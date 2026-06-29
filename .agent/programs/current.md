# 当前程序

当前没有 active program。

state: no-active

## 当前状态

`zuno-six-layer-internalization-v1` 已完成并归档到：

- `docs/history/programs/zuno-six-layer-internalization-v1/`

`.agent/programs/` 当前只保留等待状态、通用路线入口和收口清单，不再保留任何 `PHASE*.md` active phase 文件。

## 已完成事实

Program 3 已完成 `src/backend/zuno` 顶层目录和 root alias surface closure；Program 3 固定的六层顶层仍是 `api / agent / memory / capability / knowledge / platform`。`src/backend/zuno` 顶层目录仍只允许：

- `api/`
- `agent/`
- `memory/`
- `capability/`
- `knowledge/`
- `platform/`
- `__init__.py`
- `main.py`

`zuno-six-layer-internalization-v1` 在不改 API 行为、DB schema、frontend、eval baseline 或 `GeneralAgent` 主循环的前提下，完成了六层内部无副作用薄入口：

- `agent/`：`runtime.py`、`context.py`、`post_turn.py`、`state.py`、`streaming.py`、`tool_bridge.py`
- `memory/`：`contracts.py`、`store.py`、`policy.py`、`review.py`、`retrieval.py`、`rendering.py`、`engine.py`
- `capability/`：`contracts.py`、`registry.py`、`selector.py`、`policy.py`、`execution.py`、`trace.py`
- `knowledge/`：`contracts.py`、`query_service.py`、`evidence.py`、`citation.py`、`trace.py`、`retrieval/`、`fusion/`、`graphrag/`
- `platform/`：`model_gateway.py`、`security/`、`observability/`、`storage/`

这些入口复用现有 runtime owner 或 compatibility owner，不表示 production-grade memory extraction、dynamic capability orchestration、完整 retrieval fusion、DB-backed memory、model gateway 默认行为或 Runtime Architecture Upgrade 已完成。

## 等待打开

queued draft / not active：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`：target blueprint 已刷新为任务到交付物主链路；`overview.html` / Mermaid 生成展示仍是 queued follow-up。
