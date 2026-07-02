# Program Roadmap

state: no-active
active_program: none
current_phase: none
latest_completed_program: `zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`

## 总套件

本轮套件名：

`zuno-enterprise-agentic-graphrag-production-suite-v1`

当前执行形态已收口为三个 completed / archived program：

1. Program 1：Document Ingestion Foundation，completed / archived。
2. Program 2：Durable Ingestion Product V1，completed / archived。
3. Program 3 Mega：Launchable Enterprise Agentic GraphRAG Full Closure，completed / archived。

## Program 1：Document Ingestion Foundation

Program ID：`zuno-production-document-ingestion-and-thread-foundation-v1`

状态：completed / archived。

归档位置：

- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`

完成边界：`ParseGateway`、`CanonicalDocumentIR`、parser job snapshot、adapter boundary、native parser fixtures、index manifest lineage 和 citation lineage 已形成本地可验证地基。

## Program 2：Durable Ingestion Product V1

Program ID：`zuno-enterprise-document-ingestion-platform-v2`

状态：completed / archived。

归档位置：

- `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`

完成边界：SQLite durable store、local source object、workspace file metadata、parse job / snapshot、document version / blocks、index manifest / chunks、citation lineage、task / events / artifact / feedback rehydrate 和 restart recovery。

## Program 3 Mega：Launchable Enterprise Agentic GraphRAG Full Closure

Program ID：`zuno-launchable-enterprise-agentic-graphrag-full-closure-v1`

状态：completed / archived。

归档位置：

- `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`

完成边界：输入异步基础设施、Knowledge / Retrieval / GraphRAG、Memory & Context、Capability / Skill / Tool / MCP、Security / Governance、Model Gateway / Cost、Planning & Control Runtime、Eval / Trace / Benchmark、Product API / Frontend 最小同步、E2E、文档和归档已统一收口成本地 launchable product baseline。

完成结论：

```text
Launchable enterprise Agentic GraphRAG product baseline completed.
Production scale external deployments remain replaceable targets.
```

## 后续规则

- 当前没有 active program，也没有 queued program。
- 新 program 只能从 archived closure summary 和 no-active state 出发。
- 不得把历史 Target 或 Production Scale Target 写成 Current。
- 不得把 Codex 多线程执行写成 Zuno 产品 runtime 多 Agent 架构。
- 下一轮如要进入生产级外部服务部署，必须先新建 program、定义 PHASE01 truth source / dependency probe / verification gate，再改代码。
