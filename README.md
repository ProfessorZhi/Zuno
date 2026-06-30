# Zuno

Zuno 是本地优先的企业私有知识库与多功能 Agent 助手。它把 Vue Web、Electron Desktop、FastAPI 后端、当前 `GeneralAgent` 单循环主线、Knowledge / RAG / GraphRAG、工具能力、MCP 语境和本地 Eval 放在一个 monorepo 里，目标是让企业私有文档从“可搜索”升级为“可理解、可追溯、可执行”。

一句话目标：

```text
Local-first Enterprise Private Knowledge Agent Workspace
= Single Controller Agent
+ Context / Memory Engine
+ Capability / Tool Retrieval
+ Knowledge / GraphRAG Retrieval
+ Evidence / Citation / Trace / Eval
+ Typed API + Web/Desktop
```

这里的 Single Controller Agent 是目标架构角色；当前实现主线是 `GeneralAgent` single loop。

## Zuno 是什么

Zuno 的主场景不是普通 RAG 问答，而是企业内部文档知识库 + 多功能 Agent 助手。它面向企业内部文档、合同、制度、项目资料、技术文档、HR / 简历资料等私有数据场景，提供可引用问答、文档分析、合同审查、项目知识整理、报告生成和受控工具调用能力。

Zuno 通过 Basic RAG、GraphRAG Local / Global / DRIFT、Evidence、Citation、Trace、Eval、Memory 和 Tool Governance 提升回答可信度与工具调用可控性。Security、Approval 和 Sandbox 是目标治理层；当前不能把成熟沙箱、credential broker、完整 DLP 或生产级工具审批写成 Current。

## 5 分钟首读

1. 先看 [当前架构](./docs/architecture/current-architecture.md)：只写当前代码和测试已经证明的事实。
2. 看 [企业私有知识库主叙事](./docs/architecture/product-scenario-enterprise-kb.md)：确认 Zuno 为什么不是普通 RAG demo。
3. 再看 [目标架构](./docs/architecture/target-architecture.md)：写近期目标，不代表已经完成。
4. 看 [安全与沙箱目标](./docs/architecture/security-and-sandbox.md)：确认 Policy Sandbox、Workspace Sandbox、Execution Sandbox 和 Network / Credential Sandbox 的边界。
5. 看 [路线图](./docs/architecture/roadmap.md)：确认当前 program、下一步和非目标。
6. 看 [交付物清单](./docs/deliverables.md)：确认八大交付物、十类架构视图和根目录清洁期望。
7. 看 [架构总览 HTML](./docs/architecture.html) 或 [架构图源](./docs/architecture.md)：完整页面按 4+1 五类图、View & Beyond 四类图和 Agent Loop 专题图组织。
8. 需要证据时看 [公开演示证据](./docs/evidence/public-demo.md)、[Eval Baseline](./docs/evidence/eval-baselines.md) 和 [术语表](./docs/reference/terminology.md)。
9. Agent 执行任务先读 [AGENTS.md](./AGENTS.md)。

## 当前是什么

当前事实：

- `apps/web` 是 Vue Web 工作区。
- `apps/desktop` 是 Electron Desktop 工作区。
- `src/backend/zuno` 是唯一当前 Python 后端 runtime 边界。
- 当前知识回答主线是 Single GeneralAgent Runtime。
- 当前 GraphRAG / Knowledge 主线已经包含 `KnowledgeQueryService`、`GraphRAGQueryService`、`GraphRAGProjectSnapshot` 和 `KnowledgeQueryResult`。
- 当前 Query Router foundation 已贯通 `product_mode = normal | enhanced | auto` 与 `query_method = auto | basic | local | global | drift` 的请求、路由和 trace；`auto` 只表示 router，最终 `resolved_query_method` 不落到 `auto`。
- 当前 Context / Memory foundation 已证明 Context Pack policy、source id coverage、五类记忆 taxonomy、review contract，以及 `GeneralAgent` 对同 scope task summary 和 approved structured memory 的轻量 readback；这不是 production-grade Memory DB 或成熟 memory retrieval / consolidation。
- 当前 Capability foundation 已证明 ToolCard compact metadata、Native BM25 ToolCard retrieval、MCP/local tool policy trace、facade compatibility，以及 `GeneralAgent` 内部 capability selection trace bridge；这不是生产级动态工具编排或完整 runtime tool filtering。
- 当前 Hooks / Evidence / Trace / Artifact foundation 已证明 hook event schema、evidence verdict、artifact manifest、`GeneralAgent` additive trace event、tool pre/post hook payload 和 eval diagnostics；这不是完整 artifact storage、frontend trace panel 或 production-grade hooks governance。
- 当前 GraphRAG Knowledge Runtime foundation 已证明 LLM-first extractor config contract、GraphRAG snapshot 传播、query method / citation / retrieval fusion trace contract、global community-only prior 边界、GeneralAgent query method contract 文本和旧 import path 兼容；这不是生产级 LLM extraction、完整 RRF/rerank 治理或前端 trace 面板。
- 当前 Runtime Upgrade Integration foundation 已证明 `RuntimeTurnLedger`、当前轮 trace reset、`prepare_context -> agent_loop -> post_turn_commit` 的最小证据链、knowledge/tool/post-turn trace evidence、六层目标入口 import guard 和 eval diagnostics；这不是完整产品级 runtime upgrade。
- Phase 0-6 架构收口仍是已完成的历史事实。
- Phase 0-6 架构收口、Target Architecture Migration V1、Phase 11A / 11B / 11C 和 Phase 12 closure 都是已完成历史事实。
- Phase 11A 已完成：项目查询 runtime 已引入 Knowledge / GraphRAG 查询边界。
- Phase 11B 已完成：知识回答已经统一到 single `GeneralAgent` path。
- Phase 11C 已完成：Domain Pack active runtime cleanup 已关闭。
- Phase 12 已完成：closure evidence 已闭合。
- 当前 active Agent program 是 `zuno-architecture-detail-and-execution-plan-v1`，当前阶段是 `PHASE04_execution-roadmap-from-architecture`；它只细化架构文档、十类架构图、HTML 展示和后续执行计划，不实施 runtime feature。最近完成的 `zuno-eight-deliverables-full-realization-v1` 已归档到 `docs/history/programs/`。下一轮实现优先级是 Document Ingestion、Runtime + Memory + Tool Plane、Eval / Observability、安全与企业场景。

当前主要调用链：

`Completion API -> CompletionService -> GeneralAgent single loop -> search_knowledge_base -> KnowledgeQueryService -> GraphRAGQueryService -> RetrievalPlanner / RetrievalOrchestrator -> Evidence / Citation / Trace -> GeneralAgent answer`

```text
Completion API
  -> CompletionService
  -> GeneralAgent single loop
  -> search_knowledge_base
  -> KnowledgeQueryService
  -> GraphRAGQueryService
  -> RetrievalPlanner / RetrievalOrchestrator
  -> Evidence / Citation / Trace
  -> GeneralAgent answer
```

## 当前不是什么

这些不能写成 Current：

- 完整产品级 `prepare_context -> agent_loop -> post_turn_commit` LangGraph runtime，包括成熟 model-visible context injection、动态工具编排和跨前后端 trace UI。
- production-grade memory extraction / retrieval / consolidation。
- mature Context Orchestrator product behavior。
- product-level dynamic capability orchestration。
- production-grade LLM-first GraphRAG extraction、完整 RRF/rerank 治理和多套 extractor 编排。
- 完整 frontend trace 面板。
- Java 服务、微服务、事件 worker、产品级多 Agent 模式或 Coding Agent mode。

## 目标关键词

- Memory 目标策略是 Summary Compression + Structured Extraction。
- Capability 目标是 ToolCard Registry、keyword / alias lookup、Native BM25、optional vector search、permission / health / cost filter 和 capability selection trace。
- Enhanced retrieval 目标包含 multi-query、multi-retriever recall、RRF coarse fusion `k=60`、optional rerank、evidence check、citation 和 trace。
- GraphRAG query method 是 `basic`、`local`、`global`、`drift`；`auto` 是 router，不是第五种 query mode。
- 产品模式是 `normal`、`enhanced`、`auto`；trace 中分开记录 product mode、router decision 和 query method。

## 受限历史兼容

`graphrag_project_id` 是 Agent 与 Knowledge public DTO 的目标身份字段。

`domain_pack_id` 只可能出现在 migration alias、既有数据库字段兼容、eval CLI 兼容、retirement/history tests 和归档材料中。Domain Pack 不再是公开主线；Contract Review 资产已归档到 `docs/history/domain-packs/root-contract-review/`。

## 怎么运行

后端示例：

```powershell
uvicorn --app-dir src/backend zuno.main:app --host 0.0.0.0 --port 7860
```

前端示例：

```powershell
npm run frontend:dev
```

Windows 启动器：

```powershell
.\tools\launchers\windows\Zuno-Web-Start.cmd
.\tools\launchers\windows\Zuno-Desktop-Start.cmd
```

## 怎么验证

本次文档和仓库边界常用验证：

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_doc_boundaries.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```

常用聚焦命令：

```powershell
pytest -q tests/legacy_guards/test_phase0_runtime_recovery.py
pytest -q tests/repo/test_repo_structure_consistency.py
pytest -q tests/repo/test_publish_boundary.py
```

更完整的 Agent / repo hygiene 验证见 `.agent/references/workflow.md`。

## 目录结构

```text
Zuno/
├─ apps/
│  ├─ web/                 # Vue Web 工作区
│  └─ desktop/             # Electron Desktop 工作区
├─ src/backend/zuno/       # 当前后端 runtime truth
├─ tools/                  # 启动器、维护脚本和 eval 工具
├─ tests/                  # 仓库级验证和聚焦回归测试
├─ infra/                  # Docker 和基础设施配置
├─ examples/               # GraphRAG Project 示例
├─ docs/                   # 正式文档
│  ├─ architecture/        # 当前架构、目标架构、路线图、正式决策
│  ├─ evidence/            # 精选证据
│  ├─ reference/           # 当前术语
│  └─ history/             # 过时或已完成材料归档
├─ .agent/                 # Agent 工作流库
└─ AGENTS.md               # 仓库级 Agent 入口
```
