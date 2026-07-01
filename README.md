# Zuno

Zuno 是 AgentChat 驱动的企业知识库 Agentic GraphRAG Workspace，不是普通 RAG 问答 demo。用户在聊天里提出目标，系统通过统一输入层、知识库层、模型层、记忆层、工具层、安全层和规划层协作，由 Single Controller Agent 自动决定如何检索、是否使用 GraphRAG、是否调用工具、是否重查或反思，最后生成带引用、可追溯、可评测的回答或 artifact。

它继承“企业私有知识库与多功能 Agent 助手”的定位，把 Vue Web、Electron Desktop、FastAPI 后端、当前 `GeneralAgent` 单循环主线、Agentic Retrieval Planner、Knowledge / RAG / GraphRAG、工具能力、MCP 语境和本地 Eval 放在一个 monorepo 里，目标是让企业私有文档从“可搜索”升级为“可由 Agent 主动规划检索、可理解、可追溯、可执行、可评测、可治理”。

```text
Local-first Enterprise Private Knowledge Agent Workspace
= Single Controller Agent
+ Context / Memory Engine
+ Capability / Tool Retrieval
+ Agentic Retrieval Planner
+ Knowledge / GraphRAG as Agent Tool
+ Evidence / Citation / Trace / Eval
+ Typed API + Web/Desktop
```

这里的 Single Controller Agent 是目标架构角色；当前实现主线是 `GeneralAgent` single loop。

## 5 分钟首读

1. [总架构文档](./docs/architecture/architecture.md)：文字说明 Current / Target 边界、企业知识库主叙事、运行时分层、文档解析、Memory、工具、安全、评测和实施落点；同一文件也维护 Mermaid 图源。
2. [Production Readiness Baseline](./docs/architecture/production-readiness.md)：明确四大总交付物、Current Local Slice、Launchable Prototype Target 与 Production Scale Target 的边界。
3. [Document Ingestion Foundation](./docs/architecture/document-ingestion-foundation.md)：企业知识库文档入口契约，说明 ParseGateway、Document IR、index handoff、版本、幂等、防丢、ACL、citation lineage 和多模态解析边界。
4. [架构 HTML](./docs/architecture/architecture.html)：图形化查看十类架构图，支持展开全屏查看。
5. [公开演示证据](./docs/evidence/public-demo.md)：可公开引用的证据入口。
6. [术语表](./docs/reference/terminology.md)：当前公开术语。
7. [Agent 入口](./AGENTS.md)：Codex / Agent 执行任务前必须遵守的工作流契约。

已归档的旧拆分架构文档在 `docs/history/architecture-surface-cleanup-2026-06-30/`，不再作为当前前台入口。

## 当前事实

- `apps/web` 是 Vue Web 工作区。
- `apps/desktop` 是 Electron Desktop 工作区。
- `src/backend/zuno` 是唯一当前 Python 后端 runtime 边界。
- 当前知识回答主线是 `Completion API -> CompletionService -> GeneralAgent single loop -> search_knowledge_base -> KnowledgeQueryService -> GraphRAGQueryService -> RetrievalPlanner / RetrievalOrchestrator -> Evidence / Citation / Trace -> GeneralAgent answer`；目标产品主线是用户只在 AgentChat 提目标，并在勾选知识库时选择标准检索或深度检索，由 Single Controller Agent 内部的 Agentic Retrieval Planner 决定 query rewrite、retriever selection、GraphRAG expansion、reflection 和 re-query。
- 当前已有 Query Router、Context / Memory、ToolCard、GraphRAG、Evidence / Citation / Trace / Eval foundation。
- 当前已有第一版 runtime-first vertical slice 和 Web workspace Agent 产品闭环。
- 当前不是完整产品级 LangGraph runtime，不是生产级 Memory DB，不是成熟安全沙箱，也不是默认多 Agent runtime。
- Phase 0-6 架构收口仍是已完成的历史事实。

## 当前 program 状态

当前 `.agent/programs/` 处于 active 状态：

- `active_program: zuno-enterprise-ingestion-async-infrastructure-v1`
- `current_phase: PHASE01_truth-source-and-async-gap-audit.md`
- `latest_completed_program: zuno-enterprise-document-ingestion-platform-v2`

当前 Program 3 是 Enterprise Ingestion Async Infrastructure：承接 Program 2 已完成的 Product V1 local durable ingestion baseline，补齐企业文档输入层的异步基础设施 baseline，包括 PostgreSQL-compatible fact store boundary、ObjectStore binary support、QueueBackend / LocalQueueBackend、RabbitMQ boundary、Redis runtime state boundary、ParserWorker / IndexWorker、outbox、dead letter、reconciler、OCR / VLM worker boundary 和 ingest status / retry / cancel / replay contract。后续 queued program 依次是 Program 4 `zuno-runtime-subsystems-parallel-v1`、Program 5 `zuno-agent-planning-integration-v1` 和 Program 6 `zuno-enterprise-knowledge-eval-benchmark-v1`。Basic RAG 与静态 GraphRAG 只作为评测对照组；最终产品目标是 AgentChat 驱动的 Single Controller Agentic GraphRAG 企业知识库 Agent。用户在知识库选择处只看到标准检索 / 深度检索，GraphRAG 是 Agent 可调用的检索工具，不是用户手动选择的主产品模式。

最近完成并归档的 program 是 `zuno-production-architecture-and-deliverables-completion-v1`：

- `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`

它完成 PHASE01-PHASE12，把 Zuno 从“第一版 runtime-first vertical slice 已完成”推进到“成熟目标架构和四大总交付物完成”的本地可验证 baseline。PHASE08 已关闭 local durable store round-trip、restart resume、failure snapshot 和 exactly-once tool id boundary；PHASE09 已关闭 local semantic fallback、privacy delete、sensitive context exclusion 和 memory eval baseline；PHASE10 已关闭 local network policy decision、credential-ref-only broker、redacted approval ledger 和 sandbox audit context；PHASE11 已关闭 local evidence provenance、citation source tracing、local RRF/rerank trace、deterministic graph extraction / community report trace 和 unsupported claim metrics；PHASE12 已完成 release closure、full verification、archive 和 no-active state。

上一轮 runtime-first program 是 `zuno-target-architecture-runtime-full-implementation-v1`：

- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`

这些 program 的 closure evidence 保留在归档目录；README 不重复闭环链路细节。

上一轮 foundation program 是 `zuno-master-architecture-implementation-v1`：

- `docs/history/programs/zuno-master-architecture-implementation-v1/`

它已完成 PHASE01-PHASE12，覆盖项目文件夹与代码布局治理、企业知识库产品闭环、Document Ingestion、Single Controller runtime harness、Memory、Tool Control Plane、Agentic GraphRAG / Evidence / Citation、Security Governance、Eval / Observability、Architecture Markdown / HTML refresh 和 release closure。

执行状态入口在 `.agent/programs/`。成熟度和 runtime-first 交付物口径以 `docs/architecture/production-readiness.md` 为准。phase 级执行证据保留在 completed program 归档中，README 只保留当前状态摘要。

## 运行示例

```powershell
uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860
npm run frontend:dev
```

Windows 启动器：

```powershell
.\tools\launchers\windows\Zuno-Web-Start.cmd
.\tools\launchers\windows\Zuno-Desktop-Start.cmd
```

## 验证

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/legacy_guards/test_phase0_runtime_recovery.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider
```

## 目录结构

```text
Zuno/
├─ apps/                  # Web / Desktop 工作区
├─ src/backend/zuno/       # 当前后端 runtime truth
├─ tools/                 # 启动器、维护脚本和 eval 工具
├─ tests/                 # 仓库级验证和回归测试
├─ infra/                 # Docker 和基础设施配置
├─ examples/              # GraphRAG Project 示例
├─ docs/                  # 正式文档
│  ├─ architecture/        # 总架构、生产成熟度基线、文档入口契约、HTML、正式决策
│  ├─ evidence/            # 精选证据
│  ├─ reference/           # 当前术语
│  └─ history/             # 过时或已完成材料归档
├─ .agent/                # Agent 工作流库
└─ AGENTS.md              # 仓库级 Agent 入口
```
