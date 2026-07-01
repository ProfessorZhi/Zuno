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
  + Web / Desktop shared task lifecycle、artifact 下载和 recoverable failure surface
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
- `README.md` 和 `.agent/programs/current.md`：记录当前 active program 是 `zuno-production-architecture-and-deliverables-completion-v1`，最近完成 program 是 `zuno-target-architecture-runtime-full-implementation-v1`。
- `docs/architecture/architecture.md`：记录 Current / Target 边界、九个目标平面和第一版 runtime 落点。
- `src/backend/zuno/api/services/workspace_task_runtime.py`、`src/backend/zuno/agent/durable_runtime.py`、`src/backend/zuno/knowledge/ingestion/`、`src/backend/zuno/knowledge/indexing/`、`src/backend/zuno/capability/runtime.py`、`src/backend/zuno/memory/store.py`：提供第一版 runtime surfaces。
- `src/backend/zuno/api/dto/workspace.py`、`src/backend/zuno/api/v1/workspace.py`、`apps/web/src/apis/workspace.ts`、`apps/web/src/pages/workspace/defaultPage/defaultPage.vue` 和 `apps/desktop/preload.cjs`：提供 PHASE06 产品面 task lifecycle、artifact download、recoverable failure、feedback / trace 串联和 Desktop 共享契约 surface。
- `tests/api/`、`tests/agent/`、`tests/knowledge/`、`tests/frontend/`、`tests/repo/`：提供 focused tests 和结构防漂移 tests。

## 当前四大总交付物

Zuno 的剩余工作不只是一组 runtime feature。当前正式交付物按四个总方向管理，第四项再展开为八类 runtime-first 交付物。

| 编号 | 总交付物 | Current 验收边界 | Production Target |
| --- | --- | --- | --- |
| 1 | 工作流自洽与自我维护 | `AGENTS.md`、`.agent/references/`、`.agent/templates/`、`.agent/programs/`、workflow verifier 和 closure checklist 已形成基础闭环；用户长期规则已有写回路径。 | 用户新规则能被及时分类、写回、模板化并进入机器检查；program open / phase closure / archive / docs sync 能持续自我审查，不靠对话记忆。 |
| 2 | 文档系统清晰无冗余 | `architecture.md` 负责目标架构，`production-readiness.md` 负责成熟度和交付物，README / AGENTS / current program 只做入口摘要，History 保存旧材料。 | 前台文档持续少而精，架构描述和代码事实同步；旧 roadmap、deliverables、current / target 拆分文档不再回流成第二事实源。 |
| 3 | 文件夹和代码 ownership 清晰 | 后端顶层六层、ownership matrix、legacy alias guard、compat / vendor guard 和 repo structure verifier 已存在。 | 代码文件分工清楚，`platform/services`、compatibility、vendor、legacy alias 和 provider tree 不再显得零碎或凑合；兼容层只做临时桥，不承担新 runtime owner。 |
| 4 | 架构功能完整实现 | 第一版 runtime-first vertical slice 已完成：Web 产品闭环、Web / Desktop 共享 task lifecycle、artifact 下载、recoverable failure surface、本地 parse / index / retrieval / tool / trace / eval surface、focused tests 和 release evidence。 | 生产级目标架构完整落地：parser queue、深度解析、外部索引、LangGraph persistence、semantic/vector memory、真实 sandbox、vault、外部 trace/eval、完整 Desktop 包装和 CI release gate。 |

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
| Product Surface | Web workspace Agent file / ingest / task / SSE / approval / artifact / trace-eval / feedback 闭环；PHASE06 已提供 Web / Desktop 共享 task lifecycle contract、artifact download endpoint / UI、recoverable failure actions、feedback / trace 串联。 | production Desktop 打包/e2e 闭环、进程重启后的长任务恢复、运维级错误恢复。 |

## 第四交付物展开：当前 runtime-first 八类交付物

本文是唯一成熟度与 runtime-first 交付物口径事实源。`README.md`、`AGENTS.md`、`.agent/programs/current.md` 和 `.agent/references/current-program.md` 只保留状态摘要并链接到本文，不重复 phase 清单、Production Target 清单或八类交付物展开。

第四项“架构功能完整实现”展开为当前 runtime-first 八类交付物：

| 编号 | 交付物 | Current 验收边界 | Production Target |
| --- | --- | --- | --- |
| 1 | 产品闭环 | Web workspace Agent 已接通 file / ingest / task / SSE / approval / artifact / trace-eval / feedback；Web / Desktop 已共享 task lifecycle contract，artifact 下载和 recoverable failure / feedback / trace 关联有 focused tests。 | Desktop 生产打包/e2e、进程重启后的长任务恢复、运维级错误恢复。 |
| 2 | 文档解析与索引 | Parse Gateway、Document IR、adapter registry、本地 BM25 / vector / graph index job、manifest、retry、replay。 | 生产 parser queue、深度 OCR / layout / table / code 抽取、外部索引服务运维。 |
| 3 | Agent Runtime | controller-node 级 checkpoint、interrupt、resume、cancel、failure snapshot，并接入 workspace task。 | 生产级 LangGraph-compatible persistence、进程重启恢复、exactly-once tool boundary。 |
| 4 | Memory 与 Context | SQLModel-backed memory store、governance ledger、promotion、decay、consolidation、GeneralAgent 接入。 | semantic / vector memory、后台 consolidation scheduler、隐私删除平台、memory eval baseline。 |
| 5 | Tool Control Plane 与 Sandbox | deterministic executor、approval wait / approve、credential ref、sandbox context、audit trace。 | 真实隔离 sandbox、外部 vault / OAuth broker、网络代理、持久 approval DB。 |
| 6 | Knowledge / GraphRAG / Evidence / Citation | Agentic retrieval、EvidenceBundle、CitationBuilder、unsupported claim metrics、cited artifact 闭环。 | 生产 GraphRAG extraction、community report、RRF / rerank、外部图索引服务。 |
| 7 | Security / Trace / Eval / Release | input / retrieval / tool / output gates、redaction、ZunoSpan、release baseline、trace replay surface。 | 外部 LangSmith / OTel sink、online eval、持久 trace store、CI release gate operations。 |
| 8 | 仓库治理与一致性 | 架构 Markdown / HTML 镜像、program no-active 状态、repo verifiers、focused tests、history archive。 | 持续发布治理、跨线程合并策略、生产运维证据自动归档。 |

## History 边界

`zuno-eight-deliverables-full-realization-v1` 是历史治理口径，重心是 Agent 工作流、元工作流、模板、正式架构文档、HTML 展示、目标架构、代码目录和验证系统。历史治理交付物只保留在 History，不再作为当前前台交付物分类。

`zuno-target-architecture-runtime-full-implementation-v1` 是最近完成的 runtime-first program，当前成熟度、八类交付物和 Production Target 边界以本文为准；执行证据保留在 `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`。

## 更新规则

- 如果某个 Production Target 要升为 Current，必须同时有代码、focused tests、trace / eval 或 verifier 证据。
- 修改成熟度边界时，同步更新 `docs/architecture/architecture.md`、本文、入口摘要和相关 verifier / repo tests。
- 前台摘要不得重复 phase 目录、Production Target 目录、四大总交付物或八类 runtime 交付物展开；需要展开时链接本文。
- 不要恢复已退休的拆分架构文档作为当前前台入口。
