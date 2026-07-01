# Zuno Production Readiness Baseline

## 状态

更新时间：2026-07-01。

本文是正式架构文档的生产成熟度基线，不替代 `docs/architecture/architecture.md`。它只回答一个问题：Zuno 当前哪些能力已经是 Current，哪些仍然只是生产化 Target。

## 核心判断

Zuno 已完成第一版 runtime-first vertical slice，但尚未完成生产级目标架构。

Current 可以表述为：

```text
第一版 in-process runtime slice
  + Web workspace Agent 产品闭环
  + 本地 deterministic parse / index / retrieval / tool / trace / eval surface
  + focused tests、repo verifiers 和 release closure evidence
```

不能表述为：

```text
完整生产 parser 平台
  + 生产级 LangGraph persistence
  + 生产级 semantic/vector Memory DB
  + 真实隔离 sandbox
  + 外部 credential vault
  + 外部 trace / eval 平台
  + production Desktop 闭环
```

## Current 证据

当前 Current 来自以下可复现仓库证据：

- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/closure-summary.md`：记录 PHASE01-PHASE12 已完成，并说明 release gate 结果。
- `README.md` 和 `.agent/programs/current.md`：记录当前 no-active，最近完成 program 是 `zuno-target-architecture-runtime-full-implementation-v1`。
- `docs/architecture/architecture.md`：记录 Current / Target 边界、九个目标平面和第一版 runtime 落点。
- `src/backend/zuno/api/services/workspace_task_runtime.py`、`src/backend/zuno/agent/durable_runtime.py`、`src/backend/zuno/knowledge/ingestion/`、`src/backend/zuno/knowledge/indexing/`、`src/backend/zuno/capability/runtime.py`、`src/backend/zuno/memory/store.py`：提供第一版 runtime surfaces。
- `tests/api/`、`tests/agent/`、`tests/knowledge/`、`tests/frontend/`、`tests/repo/`：提供 focused tests 和结构防漂移 tests。

## Production Target

以下能力仍是 Target，不得因为有 contract、local deterministic runtime、fixture 或 README 就写成 Current：

| 平面 | Current | Production Target |
| --- | --- | --- |
| Document Ingestion | Parse Gateway runtime、adapter registry、Document IR、parser golden fixtures。 | 生产级 Docling / MinerU / Unstructured adapter、OCR/layout/table/code 深度抽取、parser queue、parser metrics。 |
| Index / GraphRAG | 本地 BM25 / vector / graph index job runtime、manifest、retry、replay、retrieval payload。 | 外部 Elasticsearch / Milvus / Neo4j、GraphRAG extraction、community report、RRF / rerank、index service operations。 |
| Agent Runtime | Controller-node durable runtime surface、checkpoint、interrupt、resume、cancel、failure snapshot。 | 生产级 LangGraph-compatible persistence、进程重启恢复、exactly-once tool boundary。 |
| Memory | SQLModel-backed memory store、governance ledger、promotion、decay、consolidation、GeneralAgent 接入。 | 生产级 semantic/vector memory、后台 scheduler、隐私删除平台、memory eval baseline。 |
| Tool / Sandbox | deterministic Tool Control Plane、approval wait / approve、credential ref、sandbox context、audit trace。 | rootless / gVisor / Firecracker sandbox、外部 vault / OAuth broker、真实网络代理、持久 approval DB。 |
| Security | input / retrieval / tool / output gates、redaction、policy decision trace。 | 生产 DLP、跨 workspace leakage 压测、真实隔离执行、企业审计策略平台。 |
| Observability / Eval | `ZunoSpan`、release baseline、local eval runner、trace replay surface。 | 外部 LangSmith / OTel sink、online eval、持久 trace store、CI release gate operations。 |
| Product Surface | Web workspace Agent file / ingest / task / SSE / approval / artifact / trace-eval / feedback 闭环。 | production Desktop 闭环、下载体验、长任务恢复提示、运维级错误恢复。 |

## 八类交付物口径

仓库历史上有两套八类交付物口径，它们不应并行竞争：

- `zuno-eight-deliverables-full-realization-v1` 是历史治理口径，重心是 Agent 工作流、元工作流、模板、正式架构文档、HTML 展示、目标架构、代码目录和验证系统。
- `zuno-target-architecture-runtime-full-implementation-v1` 是当前最近完成的 runtime-first 口径，重心是产品闭环、解析索引、Agent Runtime、Memory、Tool / Sandbox、GraphRAG / Evidence / Citation、Security / Trace / Eval 和仓库治理。

当前前台采用 runtime-first 口径；历史治理口径只作为 `docs/history/programs/zuno-eight-deliverables-full-realization-v1/` 的完成证据保留。

## 更新规则

- 如果某个 Production Target 要升为 Current，必须同时有代码、focused tests、trace / eval 或 verifier 证据。
- 修改成熟度边界时，同步更新 `docs/architecture/architecture.md`、本文、`README.md`、`AGENTS.md` 和相关 verifier / repo tests。
- 不要恢复已退休的拆分架构文档作为当前前台入口。
