# Zuno

Zuno 是本地优先的 Agent Workspace。它把 Vue Web、Electron Desktop、FastAPI 后端、LangGraph 编排、RAG / GraphRAG、工具、MCP 集成和本地 Eval 放在一个 monorepo 里。

## 当前状态

当前事实：

- `apps/web` 是 Vue Web 工作区。
- `apps/desktop` 是 Electron Desktop 工作区。
- `src/backend/zuno` 是唯一当前 Python 后端 runtime 边界。
- Phase 0-6 架构收口仍是已完成的历史事实。
- Target Architecture Migration V1 已关闭并归档。
- 当前可执行 Agent 程序是 `.agent/programs/` 平铺计划包。
- Phase 11A 已完成：当前 runtime 已包含 `KnowledgeQueryService`、`GraphRAGQueryService`、`GraphRAGProjectSnapshot` 和 `KnowledgeQueryResult`。
- Phase 11B 已完成：当前知识回答调用链是 `Completion API -> CompletionService -> GeneralAgent single loop -> search_knowledge_base -> KnowledgeQueryService -> GraphRAGQueryService -> RetrievalPlanner / RetrievalOrchestrator -> Evidence / Citation / Trace -> GeneralAgent answer`。

目标方向：

- 保持稳定 monorepo 基线。
- 目标架构保持为：Single GeneralAgent Runtime + Context / Memory Engine + Capability / Tool Retrieval + Knowledge / GraphRAG Retrieval + Evidence / Citation / Trace / Eval + Typed API + Web/Desktop。
- Memory 目标策略是 Summary Compression + Structured Extraction。
- Capability 目标是 ToolCard Registry、keyword / alias lookup、Native BM25、optional vector search、permission / health / cost filter 和 capability selection trace。
- Native BM25 是本地排序算法；Elasticsearch 是 optional external adapter，不是 BM25 算法本身。
- enhanced path 使用 multi-query、multi-retriever retrieval、RRF coarse fusion `k=60`、optional rerank、evidence check、citation 和 trace。
- GraphRAG query method 是 `basic`、`local`、`global`、`drift`；`auto` 是 router，不是第五种 query mode。
- Java 服务、微服务、事件 worker、产品级多 Agent 模式和 Coding Agent 方向都只属于 Future。

## Phase 11C / 受限历史兼容

- Phase 11C active runtime cleanup 已完成。当前 FastAPI router 不再挂载 `/api/v1/domain-packs`；active Vue knowledge routes/pages 不再打开 Domain Pack builder/list/detail flow；旧 frontend Domain Pack API/page 文件已经从 `apps/web/src` 当前树移除。
- `graphrag_project_id` 是 Agent 与 Knowledge public DTO 的目标身份字段。兼容输入可映射到既有 storage column，但前台架构不再把 `domain_pack_id` 写成 active mainline。
- `DomainQAGraph`、`MultiAgentSupervisorGraph`、`AgentRuntime` facade、legacy graph states 和 `src/backend/zuno/services/domain_pack/` runtime service package 已从当前后端移除。
- Contract Review 资产已归档到 `docs/history/domain-packs/root-contract-review/`。Docker 不再复制或挂载 `/app/domain-packs`。
- `domain_pack_id` 只可能出现在 migration alias、既有数据库字段兼容、eval CLI 兼容、retirement/history tests 和归档材料中。
- Phase 12 closure evidence 已完成：full pytest、formal Contract Review eval、stackless baseline comparison、trace closure、legacy grep classification 和 `docs/evidence` 同步已闭合。

## 首读路径

1. [当前架构](./docs/architecture/current-architecture.md)
2. [目标架构](./docs/architecture/target-architecture.md)
3. [路线图](./docs/architecture/roadmap.md)
4. [公开演示证据](./docs/evidence/public-demo.md)
5. [Eval Baseline](./docs/evidence/eval-baselines.md)
6. [术语表](./docs/reference/terminology.md)
7. [Agent 入口](./AGENTS.md)

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

## 本地启动

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

## 验证

常用文档和仓库边界验证：

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python .agent/scripts/verify_module_boundaries.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py tests/repo/test_agent_system.py tests/repo/test_repo_hygiene.py -p no:cacheprovider
```

常用聚焦命令：

```powershell
pytest -q tests/repo/test_repo_structure_consistency.py
pytest -q tests/repo/test_publish_boundary.py
pytest -q tests/legacy_guards/test_phase0_runtime_recovery.py
```

完整 pytest 和 eval 只在对应 phase 或 closure 明确要求时运行。
