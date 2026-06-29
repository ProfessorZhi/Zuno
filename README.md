# Zuno

Zuno 是本地优先的 Agent Workspace。它把 Vue Web、Electron Desktop、FastAPI 后端、当前 `GeneralAgent` 单循环主线、Knowledge / RAG / GraphRAG、工具能力、MCP 语境和本地 Eval 放在一个 monorepo 里。

一句话目标：

```text
Local-first Agent Workspace
= Single Controller Agent
+ Context / Memory Engine
+ Capability / Tool Retrieval
+ Knowledge / GraphRAG Retrieval
+ Evidence / Citation / Trace / Eval
+ Typed API + Web/Desktop
```

这里的 Single Controller Agent 是目标架构角色；当前实现主线是 `GeneralAgent` single loop。

## 5 分钟首读

1. 先看 [当前架构](./docs/architecture/current-architecture.md)：只写当前代码和测试已经证明的事实。
2. 再看 [目标架构](./docs/architecture/target-architecture.md)：写近期目标，不代表已经完成。
3. 看 [路线图](./docs/architecture/roadmap.md)：确认当前 program、下一步和非目标。
4. 看 [交付物清单](./docs/deliverables.md)：确认八大交付物、十类架构视图和根目录清洁期望。
5. 看 [架构总览 HTML](./docs/architecture.html) 或 [架构图源](./docs/architecture.md)：完整页面按 4+1 五类图、View & Beyond 四类图和 Agent Loop 专题图组织。
6. 需要证据时看 [公开演示证据](./docs/evidence/public-demo.md)、[Eval Baseline](./docs/evidence/eval-baselines.md) 和 [术语表](./docs/reference/terminology.md)。
7. Agent 执行任务先读 [AGENTS.md](./AGENTS.md)。

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
- Phase 0-6 架构收口仍是已完成的历史事实。
- Phase 0-6 架构收口、Target Architecture Migration V1、Phase 11A / 11B / 11C 和 Phase 12 closure 都是已完成历史事实。
- Phase 11A 已完成：项目查询 runtime 已引入 Knowledge / GraphRAG 查询边界。
- Phase 11B 已完成：知识回答已经统一到 single `GeneralAgent` path。
- Phase 11C 已完成：Domain Pack active runtime cleanup 已关闭。
- Phase 12 已完成：closure evidence 已闭合。
- 当前 active Agent 执行计划在 `.agent/programs/`，完成或替换后的 program 归档到 `docs/history/programs/`。

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

- 完整 `prepare_context -> agent_loop -> post_turn_commit` LangGraph runtime。
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
