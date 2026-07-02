# Zuno Production Readiness Baseline

## 状态

更新时间：2026-07-02。

本文是正式架构文档的生产成熟度基线，不替代 `docs/architecture/architecture.md`。它只回答一个问题：Zuno 当前哪些能力已经是 Current Local Slice，哪些是 Launchable Prototype Target，哪些仍然只是 Production Scale Target。企业知识库文档入口的展开契约由 `docs/architecture/document-ingestion-foundation.md` 维护，本文只维护成熟度边界。

## 核心判断

Zuno 已完成第一版 runtime-first vertical slice 和本轮生产成熟化本地 baseline，但尚未接入完整外部生产平台。新的近期目标不是把目标降成 toy demo，也不是继续把验收卡在“完整分布式企业平台还差一步”。近期目标改为 **Zuno Launchable Enterprise KB Agent Prototype / Zuno 可上线企业知识库 Agent 雏形架构**。

定义：

> Zuno 是一个前后端分离、本地优先 / 私有部署优先的企业知识库 Agent Workspace。当前目标不是完整分布式企业平台，而是一个可以部署给个人、小团队、实验室或内网试用的企业级雏形：账号体系、workspace、文件上传、文档解析、索引、Agent 问答、引用、artifact、trace、反馈和基础权限都由后端持久化管理。生产级分布式队列、外部 OCR / VLM、外部向量库 / 图数据库、企业 SSO、在线评测和大规模运维作为 Production Scale Target。

Current Local Slice 可以表述为：

```text
第一版 in-process runtime slice
  + Web workspace Agent 产品闭环
  + Web / Desktop shared task lifecycle、artifact 下载和 recoverable failure surface
  + 本地 deterministic parse / index / retrieval / tool / trace / eval surface
  + 本地 parser queue snapshot、index adapter boundary 和 manifest provenance evidence
  + 文档输入层 SQLite / local file store durable ingestion baseline
  + source object、workspace file、parse job、document version、index manifest、index chunk、task、event、artifact、feedback 和 restart recovery focused tests
  + local durable store round-trip、restart resume、failure snapshot 和 exactly-once tool id boundary
  + local semantic memory fallback、scoped privacy delete、sensitive context exclusion 和 memory eval baseline
  + local network policy decision、credential-ref-only broker、redacted approval ledger 和 sandbox audit context
  + local evidence provenance、citation source tracing、local RRF/rerank trace、deterministic graph extraction / community report trace 和 unsupported claim metrics
  + local Model Gateway、chat / embedding / reranker / VLM / eval judge mock provider、budget verdict、timeout fallback reason 和 redacted model trace
  + local deterministic Strategy Selector、PlannerOutput、PlanState、RetrievalPlan、CapabilityPlan、planning trace 和 budget/security blocked verdict
  + local AgentControlRuntime、ReAct observation step runner、Reflection gate、Dynamic Replan trajectory change、ReflexionLesson pending review path 和 answer_finalized trace
  + input / retrieval / tool / output gates、redaction、ZunoSpan、release baseline、trace replay surface 和 no-active archive
  + focused tests、repo verifiers 和 full release closure evidence
```

不能表述为 Current，但可以分别作为 Launchable Prototype Target 或 Production Scale Target：

```text
完整生产 parser 平台
  + 真实 Docling / PyMuPDF PDF worker
  + 真实 Unstructured / MarkItDown Office worker
  + 真实 MinerU / PaddleOCR / VLM OCR worker
  + binary ObjectStore adapter、queue / outbox / worker pool
  + 生产级 LangGraph persistence
  + 生产级 semantic/vector Memory DB
  + 真实隔离 sandbox
  + 外部 credential vault
  + 真实外部 model provider 路由和在线成本账单
  + 外部 trace / eval 平台
  + production Desktop 闭环
```

## 成熟度三层

| 层级 | 定义 | 当前状态 |
| --- | --- | --- |
| Current Local Slice | 代码、focused tests、trace / eval 或 verifier 已证明的本地 runtime 事实。 | Program 1 已完成 `workspace file -> ParseGateway -> CanonicalDocumentIR -> index handoff -> IndexJobManifest -> retrieval / citation provenance`；Program 2 已完成 local durable ingestion baseline：`/workspace/file` source object、`/workspace/ingest` parse / document / index persistence、task / event / artifact / feedback persistence 和 restart recovery；Program 3 Mega 已完成 PHASE03-PHASE10 的本地 ingestion async、retrieval profile、Memory & Context、Capability / Skill / Tool / MCP、Security / Governance、Model Gateway / Cost / Latency、Planning Contract / Strategy Selector 和 AgentControlRuntime / Reflection / Dynamic Replan / Reflexion baseline。 |
| Launchable Prototype Target | 一两天内可由 Codex 真实补到闭环、可给个人 / 小团队 / 实验室 / 内网试用的企业级雏形。 | Program 3 Mega 当前 active，目标是 launchable enterprise Agentic GraphRAG product baseline：enterprise ingestion async infrastructure、标准检索 / 深度检索 profile、Memory & Context Engine、Capability / Skill / Tool / MCP、Security / Governance、Model Gateway / Cost、Planning & Control Runtime、Eval / Trace / Benchmark、KnowledgeSpaceConfig / Change Impact Preview、Product API / Frontend 最小同步、E2E 用户可感知 scenario summary 和 closure archive。 |
| Production Scale Target | 多租户、可恢复、可扩展、可审计、可运维、可灰度、可评测的完整企业级平台。 | 真实 PostgreSQL 集群、MinIO / S3 生产对象存储、RabbitMQ / Kafka 集群、Redis 集群、external OCR / VLM、external index、SSO / RBAC / DLP / Vault、OTel / LangSmith、online eval 和大规模运维仍是后续扩展，只有接入真实 provider 并测试后才能升为 Current。 |

## Current 证据

当前 Current 来自以下可复现仓库证据：

- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/closure-summary.md`：记录 PHASE01-PHASE12 已完成，并说明 release gate 结果。
- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/closure-summary.md`：记录 PHASE01-PHASE12 已完成，四大总交付物和八类 runtime-first 交付物均有 Current 证据或明确 Remaining Target。
- `README.md` 和 `.agent/programs/current.md`：记录当前 `.agent/programs/` 处于 Program 3 active 状态，最近完成 program 是 `zuno-enterprise-document-ingestion-platform-v2`，归档位置是 `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`。
- `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/closure-summary.md`：记录 PHASE01-PHASE08 已完成，并说明 workspace ingest -> ParseGateway -> parser snapshot -> index manifest -> citation lineage 的本地闭环证据。
- `docs/architecture/architecture.md`：记录 Current / Target 边界、九个目标平面和第一版 runtime 落点。
- `docs/architecture/document-ingestion-foundation.md`：记录企业知识库文档入口的 Program 1 local runtime slice、Program 2 durable ingestion Current、workspace ingest -> ParseGateway lineage、Document IR 版本、parser job 幂等、防丢、index manifest lineage、ACL 和 OCR / VLM enrichment 边界。
- `src/backend/zuno/api/services/workspace_task_runtime.py`、`src/backend/zuno/api/dto/workspace.py`、`apps/web/src/apis/workspace.ts`、`src/backend/zuno/agent/durable_runtime.py`、`src/backend/zuno/agent/planning.py`、`src/backend/zuno/agent/control_runtime.py`、`src/backend/zuno/agent/contracts.py`、`src/backend/zuno/knowledge/ingestion/`、`src/backend/zuno/knowledge/indexing/`、`src/backend/zuno/knowledge/storage/`、`src/backend/zuno/capability/runtime.py`、`src/backend/zuno/memory/store.py`、`src/backend/zuno/memory/retrieval.py`、`src/backend/zuno/memory/engine.py`、`src/backend/zuno/platform/model_gateway.py`：提供第一版 runtime surfaces；PHASE07 已补 parser queue snapshot / retry、adapter target-blocked boundary、index adapter contract 和 manifest provenance / ACL；Program 2 已补 source object、workspace file、parse job / snapshot、document version / blocks、index manifest / chunks、citation lineage、workspace task、events、artifact content/ref、feedback 和 restart recovery 的 SQLite / local file store durable baseline；PHASE08 已补 local durable store JSON round-trip、restart resume、failure snapshot linkage 和 exactly-once tool id boundary；PHASE09 已补 local semantic fallback、scoped privacy delete、sensitive context exclusion、GeneralAgent semantic memory read 和 memory eval baseline；PHASE10 已补 local network policy decision、credential-ref-only broker、redacted approval ledger 和 sandbox audit context；PHASE11 已补 local evidence provenance、citation source tracing、local RRF/rerank trace、deterministic graph extraction / community report trace、external graph index target-blocked evidence 和 unsupported claim metrics；Program 3 Mega PHASE08 已补 local Model Gateway、mock provider categories、budget verdict、timeout fallback reason、cost / latency / token metrics 和 redacted model trace；Program 3 Mega PHASE09 已补 local deterministic Strategy Selector、PlannerOutput、PlanState、RetrievalPlan、CapabilityPlan、security / budget blocked verdict 和 planning trace events；Program 3 Mega PHASE10 已补 local AgentControlRuntime、ReAct observation runner、Reflection gate、Dynamic Replan trajectory change、ReflexionLesson pending review path 和 answer_finalized trace events；Program 3 Mega PHASE11 已补 per-knowledge-space standard/deep request contract、Workspace Product API task summaries、artifact citation refs、file status、KnowledgeSpaceConfig / ChangeImpactPreview DTO 和 frontend API types。
- `src/backend/zuno/api/dto/workspace.py`、`src/backend/zuno/api/v1/workspace.py`、`apps/web/src/apis/workspace.ts`、`apps/web/src/pages/workspace/defaultPage/defaultPage.vue` 和 `apps/desktop/preload.cjs`：提供 PHASE06 产品面 task lifecycle、artifact download、recoverable failure、feedback / trace 串联和 Desktop 共享契约 surface。
- `tests/api/`、`tests/agent/`、`tests/knowledge/`、`tests/frontend/`、`tests/repo/`：提供 focused tests 和结构防漂移 tests。

## 当前四大总交付物

Zuno 的剩余工作不只是一组 runtime feature。当前正式交付物按四个总方向管理，第四项再展开为八类 runtime-first 交付物。

| 编号 | 总交付物 | Current Local Slice | Launchable / Production Scale Target |
| --- | --- | --- | --- |
| 1 | 工作流自洽与自我维护 | `AGENTS.md`、`.agent/references/`、`.agent/templates/`、`.agent/programs/`、workflow verifier 和 closure checklist 已形成基础闭环；用户长期规则已有写回路径。 | 用户新规则能被及时分类、写回、模板化并进入机器检查；program open / phase closure / archive / docs sync 能持续自我审查，不靠对话记忆。 |
| 2 | 文档系统清晰无冗余 | `architecture.md` 负责目标架构，`production-readiness.md` 负责成熟度和交付物，`document-ingestion-foundation.md` 负责企业文档入口契约，README / AGENTS / current program 只做入口摘要，History 保存旧材料。 | 前台文档持续少而精，架构描述和代码事实同步；旧 roadmap、deliverables、current / target 拆分文档不再回流成第二事实源。 |
| 3 | 文件夹和代码 ownership 清晰 | 后端顶层六层、ownership matrix、legacy alias guard、compat / vendor guard 和 repo structure verifier 已存在。 | 代码文件分工清楚，`platform/services`、compatibility、vendor、legacy alias 和 provider tree 不再显得零碎或凑合；兼容层只做临时桥，不承担新 runtime owner。 |
| 4 | 架构功能完整实现 | 第一版 runtime-first vertical slice 和生产成熟化本地 baseline 已完成：Web 产品闭环、Web / Desktop 共享 task lifecycle、artifact 下载、recoverable failure surface、本地 parse / index / retrieval / tool / trace / eval surface、本地 parser queue snapshot、index adapter boundary、local durable restart/resume 和 exactly-once id boundary、local semantic memory fallback、scoped privacy delete、memory eval baseline、local network policy decision、credential-ref-only broker、redacted approval ledger、sandbox audit context、local evidence provenance、citation source tracing、local RRF/rerank trace、deterministic graph extraction / community report trace、unsupported claim metrics、Security / Trace / Eval / Release local baseline、focused tests、full verification 和 release evidence。 | 生产级目标架构完整落地：生产 parser worker queue、深度解析、外部索引、LangGraph / DB persistence、生产级 semantic/vector memory DB、真实 rootless / gVisor / Firecracker sandbox、外部 vault / OAuth broker、真实网络代理、持久 approval DB、外部 trace/eval、online eval、完整 Desktop 包装和 CI release gate。 |

## Target 分层

以下能力仍是 Target，不得因为有 contract、local deterministic runtime、fixture 或 README 就写成 Current。这里保留 `Production Target` 术语作为兼容说法，但正式分层使用 Launchable Prototype Target 和 Production Scale Target。

| 平面 | Current Local Slice | Launchable Prototype Target | Production Scale Target |
| --- | --- | --- | --- |
| Document Ingestion | Parser capability matrix 已覆盖 `pdf / docx / pptx / xlsx / txt / md / csv / json / html / image / scanned / code`；Current 稳定解析能力是 `native` deterministic parser 支持 `txt / md / csv / json / html / code`。Program 1 已完成 Parse Gateway runtime、adapter registry、Document IR、parser golden fixtures、本地 parser queue snapshot / retry / metrics、workspace ingest -> ParseGateway -> index manifest lineage、external parser adapter target-blocked boundary；Program 2 已完成 `/workspace/file` durable registry、parse job / snapshot persistence、document version / block persistence、index manifest / chunk persistence、blocked diagnostics persistence 和 restart recovery focused tests。PDF / Office / OCR / VLM 目前只有 adapter contract、dependency probe、target-blocked diagnostics 和 fixture/fallback evidence，不是 Current 生产能力。 | Program 3 正在推进本地可验证 async ingestion infrastructure：Binary ObjectStore interface、local object bytes save / read / verify、LocalQueueBackend、ParserWorker / IndexWorker local runner、runtime state、outbox、dead letter、reconciler、ingest status / retry / cancel / replay、file-level status UI / API、PDF / Office / image / scanned source object persistence、OCR / VLM blocked diagnostics 和 dependency probe。 | 生产级 Docling / PyMuPDF PDF worker、Unstructured / MarkItDown Office worker、MinerU / PaddleOCR / VLM runtime、OCR / layout / table / code 深度抽取、真实 Postgres、MinIO / S3、RabbitMQ / Kafka、Redis、external index、worker pool / autoscaling、outbox / dead letter / reconciler operations 和 parser operations metrics。 |
| Index / GraphRAG | 本地 BM25 / vector / graph index job runtime、manifest、retry、replay、retrieval payload、index adapter contract、manifest provenance / ACL / adapter status、local evidence provenance、citation source tracing、local RRF / rerank trace、deterministic graph extraction / community report trace、external graph index target-blocked evidence；Program 2 已证明 index manifest、index chunks 和 `citation_lineage` 可从 durable store rehydrate 并用于 cited artifact。 | 知识库级标准检索 / 深度检索 profile contract、`deep_without_graph` 降级 trace、更完整 GraphRAG eval baseline、external index adapter dry-run 和跨 workspace ACL 压测。 | 外部 Elasticsearch / Milvus / Neo4j、生产 LLM GraphRAG extraction、真实 community report pipeline、生产 reranker 服务、index service operations。 |
| Agent Runtime | Controller-node durable runtime surface、checkpoint、interrupt、resume、cancel、failure snapshot、local JSON persistence payload、restart resume contract、exactly-once tool boundary ids；Program 2 已证明 workspace task、events、artifact content/ref 和 feedback 可 rehydrate；Program 3 Mega PHASE09 已提供 local deterministic Strategy Selector、PlannerOutput、PlanState、RetrievalPlan、CapabilityPlan、ReflectionVerdict、ReplanDecision、Reflexion candidate 和 planning trace events；Program 3 Mega PHASE10 已提供 local AgentControlRuntime，可消费 planner output 与 governed observations，执行 step trace、reflection gate、dynamic replan trajectory change、tool_failed / security_blocked stop path、ReflexionLesson pending review path 和 answer_finalized trace；Program 3 Mega PHASE11 已把 product retrieval profile、plan/reflection/replan summary、artifact citation refs、file status 和 frontend API types 接入 Workspace Product API。 | PHASE12 当前目标是用真实 local runtime path 证明 E2E scenario summary；产品面只暴露标准检索 / 深度检索，不暴露内部 basic/local/global/drift。 | 生产级 LangGraph-compatible DB persistence、跨进程 / 跨 worker 恢复、分布式 exactly-once tool execution。 |
| Model Gateway | Program 3 Mega PHASE08 已提供 `ModelGateway`、五类 local mock provider、token / latency / cost estimate、budget verdict、timeout fallback reason、redacted prompt preview 和 prompt hash trace。 | Planning、retrieval、reflection 和 eval judge 消费同一 budget / cost / latency contract；本地实验可替换 provider adapter 但不依赖真实外部服务通过 tests。 | 多 provider 路由、真实外部模型供应商、在线账单、SLA / quota 管理、生产级模型可观测性和模型治理。 |
| Memory | SQLModel-backed memory store、governance ledger、promotion、decay、consolidation、GeneralAgent 接入、local deterministic semantic fallback、scoped privacy delete、sensitive context exclusion、memory eval baseline。 | Program 3 Mega 建立 Memory & Context Engine：working / session / episodic / semantic / procedural / reflexion / governance memory、ContextPack、Structured Extraction、Hierarchical Summary、Evidence-bound Summary、Budget-aware Packing、Reflexion lesson review / scope / expiry。 | 生产级 semantic / vector Memory DB、后台 scheduler、企业隐私删除平台、nightly memory eval、Reflexion lesson governance 和深度 PII / secret 检测。 |
| Capability Layer | 当前有 capability / ToolCard foundation 和本地 deterministic Tool Control Plane runtime，但还没有统一 Capability Router，也没有独立 SkillCard runtime；Skill 不能写成 Tool，也不能写成 Knowledge。 | Program 3 Mega 应建立 Skill Registry、SkillCard、CapabilityPolicy、CapabilityRiskProfile、CapabilityAuditEvent、Knowledge / Tool / MCP / External API / File / Code / Browser / Artifact capability routing、recommended retrieval profile、required evidence、allowed tools、required memory scopes、output contract、safety policy、eval rubric 和 trace requirements，并让 Planner 自动选择或消费 pinned skill。 | 生产级 capability governance、版本化 skill marketplace / registry、MCP connector governance、跨租户 capability isolation、skill-specific online eval 和运营监控。 |
| Tool / Sandbox | deterministic Tool Control Plane、approval wait / approve、credential-ref-only broker、network policy decision、redacted approval ledger、sandbox context、audit trace。 | Program 2 不扩 Tool；只保留文档输入 worker 的 network / privacy / budget gate blocked diagnostics。 | rootless / gVisor / Firecracker sandbox、外部 vault / OAuth broker、真实网络代理、持久 approval DB。 |
| Security | input / retrieval / tool / output gates、redaction、policy decision trace、local release archive 中的 blocked evidence 边界。 | 文档输入层 ACL / sensitivity 贯穿 source object、document version、block、index chunk 和 citation lineage；OCR / VLM blocked reason 落库。 | 生产 DLP、跨 workspace leakage 压测、真实隔离执行、企业审计策略平台、SSO / RBAC / DLP / Vault。 |
| Observability / Eval | `ZunoSpan`、release baseline、local eval runner、trace replay surface、no-active release archive 和 full verification evidence。 | parse / index / ingest status、attempt diagnostics、dead letter、restart recovery evidence 可查询；IngestionMetrics 记录 files_uploaded、files_indexed、files_failed、files_blocked、parse / index duration、parser format、dependency status、blocked reason、retry、dead letter、reconciler findings、OCR / VLM pages / cost estimate 和 binary bytes processed。 | 外部 LangSmith / OTel sink、Prometheus dashboard、online eval、持久 trace store、CI release gate operations。 |
| Product Surface | Web workspace Agent file / ingest / task / SSE / approval / artifact / trace-eval / feedback 闭环；PHASE06 已提供 Web / Desktop 共享 task lifecycle contract、artifact download endpoint / UI、recoverable failure actions、feedback / trace 串联。 | Program 3 Mega 补 KnowledgeSpaceConfig、创建 Wizard、Settings tabs、文件级 parse/index 状态、标准检索 / 深度检索选择、Change Impact Preview、task trace summary、artifact citation summary 和 E2E 用户可感知 scenario summary；前端刷新或后端 service rehydrate 后仍能查询 file / ingest / task / artifact / feedback；前端不是业务事实源。 | production Desktop 打包 / e2e 闭环、进程重启后的长任务恢复、运维级错误恢复、多租户 admin / ops。 |

## 第四交付物展开：当前 runtime-first 八类交付物

本文是唯一成熟度与 runtime-first 交付物口径事实源。`README.md`、`AGENTS.md`、`.agent/programs/current.md` 和 `.agent/references/current-program.md` 只保留状态摘要并链接到本文，不重复 phase 清单、Production Target 清单或八类交付物展开。

第四项“架构功能完整实现”展开为当前 runtime-first 八类交付物：

| 编号 | 交付物 | Current 验收边界 | Production Target |
| --- | --- | --- | --- |
| 1 | 产品闭环 | Web workspace Agent 已接通 file / ingest / task / SSE / approval / artifact / trace-eval / feedback；Web / Desktop 已共享 task lifecycle contract，artifact 下载和 recoverable failure / feedback / trace 关联有 focused tests。 | Desktop 生产打包/e2e、进程重启后的长任务恢复、运维级错误恢复。 |
| 2 | 文档解析与索引 | Parse Gateway、Document IR、adapter registry、本地 parser queue snapshot / metrics / retry、workspace ingest -> ParseGateway、本地 BM25 / vector / graph index job、manifest provenance / ACL / adapter status、retry、replay。 | 生产 parser worker queue、深度 OCR / layout / table / code 抽取、外部索引服务运维。 |
| 3 | Agent Runtime | controller-node 级 checkpoint、interrupt、resume、cancel、failure snapshot、local JSON persistence payload、restart resume contract、exactly-once tool request / approval / execution / result id，并接入 workspace task。 | 生产级 LangGraph-compatible DB persistence、跨进程/跨 worker 恢复、分布式 exactly-once tool execution。 |
| 4 | Memory 与 Context | SQLModel-backed memory store、governance ledger、promotion、decay、consolidation、GeneralAgent 接入、local semantic fallback、scoped privacy delete、sensitive context exclusion、memory eval baseline。 | 生产级 semantic / vector Memory DB、后台 consolidation scheduler、企业隐私删除平台、nightly memory eval、冲突检测和深度 PII/secret 检测。 |
| 5 | Capability Layer / Tool Control Plane 与 Sandbox | Current 已有 deterministic executor、approval wait / approve、credential-ref-only broker、network policy decision、redacted approval ledger、sandbox context、audit trace；统一 Capability Router 和独立 SkillCard runtime 仍是 Target。 | Skill Registry、SkillCard、MCP connector governance、skill-specific eval rubric、真实 rootless / gVisor / Firecracker 隔离 sandbox、外部 vault / OAuth broker、真实网络代理、持久 approval DB。 |
| 6 | Knowledge / GraphRAG / Evidence / Citation | Agentic retrieval、EvidenceBundle、CitationBuilder、citation source tracing、local RRF/rerank trace、deterministic graph extraction / community report trace、unsupported claim metrics、cited artifact 闭环。 | 知识库级标准检索 / 深度检索 profile、Agentic Retrieval Planner、生产 LLM GraphRAG extraction、真实 community report pipeline、生产 reranker 服务、外部图索引服务和完整 evidence eval baseline。 |
| 7 | Security / Trace / Eval / Release | input / retrieval / tool / output gates、redaction、ZunoSpan、release baseline、trace replay surface、local release archive 和 full verification evidence。 | Program 3 Mega 的近期目标是 ConversationRunMetrics、StageMetrics、RetrievalMetrics、PlanningMetrics、SecurityMetrics、CostMetric 和 EvalComparisonReport；长期目标是外部 LangSmith / OTel sink、online eval、持久 trace store、CI release gate operations。 |
| 8 | 仓库治理与一致性 | 架构 Markdown / HTML 镜像、program no-active 状态、repo verifiers、focused tests、history archive 和 latest completed archive guard。 | 持续发布治理、跨线程合并策略、生产运维证据自动归档。 |

## History 边界

`zuno-eight-deliverables-full-realization-v1` 是历史治理口径，重心是 Agent 工作流、元工作流、模板、正式架构文档、HTML 展示、目标架构、代码目录和验证系统。历史治理交付物只保留在 History，不再作为当前前台交付物分类。

`zuno-production-architecture-and-deliverables-completion-v1` 是最近完成的生产成熟化 program，当前成熟度、八类交付物、Launchable Prototype Target 和 Production Scale Target 边界以本文为准；执行证据保留在 `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`。

`zuno-target-architecture-runtime-full-implementation-v1` 是上一轮 runtime-first program，第一版 vertical slice 证据保留在 `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`。

## 更新规则

- 如果某个 Launchable Prototype Target 或 Production Scale Target 要升为 Current，必须同时有代码、focused tests、trace / eval 或 verifier 证据。
- 修改成熟度边界时，同步更新 `docs/architecture/architecture.md`、本文、入口摘要和相关 verifier / repo tests。
- 修改文档入口成熟度时，同步更新 `docs/architecture/document-ingestion-foundation.md`；source object store、durable job store、queue adapter、worker、生产 DB、object store、queue / outbox、worker lease、external OCR / VLM 或 external index 没有代码和测试证据前不能写成 Current。
- 前台摘要不得重复 phase 目录、Production Target 目录、四大总交付物或八类 runtime 交付物展开；需要展开时链接本文。
- 不要恢复已退休的拆分架构文档作为当前前台入口。
