# Zuno

Zuno 是本地优先的 Agent Workspace，也是企业私有知识库与多功能 Agent 助手，不是普通 RAG 问答 demo。它把 Vue Web、Electron Desktop、FastAPI 后端、当前 `GeneralAgent` 单循环主线、Knowledge / RAG / GraphRAG、工具能力、MCP 语境和本地 Eval 放在一个 monorepo 里，目标是让企业私有文档从“可搜索”升级为“可理解、可追溯、可执行、可评测、可治理”。

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

## 5 分钟首读

1. [总架构文档](./docs/architecture/architecture.md)：文字说明 Current / Target 边界、企业知识库主叙事、运行时分层、文档解析、Memory、工具、安全、评测和实施落点；同一文件也维护 Mermaid 图源。
2. [架构 HTML](./docs/architecture/architecture.html)：图形化查看十类架构图，支持展开全屏查看。
3. [公开演示证据](./docs/evidence/public-demo.md)：可公开引用的证据入口。
4. [术语表](./docs/reference/terminology.md)：当前公开术语。
5. [Agent 入口](./AGENTS.md)：Codex / Agent 执行任务前必须遵守的工作流契约。

已归档的旧拆分架构文档在 `docs/history/architecture-surface-cleanup-2026-06-30/`，不再作为当前前台入口。

## 当前事实

- `apps/web` 是 Vue Web 工作区。
- `apps/desktop` 是 Electron Desktop 工作区。
- `src/backend/zuno` 是唯一当前 Python 后端 runtime 边界。
- 当前知识回答主线是 `Completion API -> CompletionService -> GeneralAgent single loop -> search_knowledge_base -> KnowledgeQueryService -> GraphRAGQueryService -> RetrievalPlanner / RetrievalOrchestrator -> Evidence / Citation / Trace -> GeneralAgent answer`。
- 当前已有 Query Router、Context / Memory、ToolCard、GraphRAG、Evidence / Citation / Trace / Eval foundation。
- 当前不是完整产品级 LangGraph runtime，不是生产级 Memory DB，不是成熟安全沙箱，也不是默认多 Agent runtime。
- Phase 0-6 架构收口仍是已完成的历史事实。

## 当前 program 状态

当前 active Agent program 是 `zuno-target-architecture-runtime-full-implementation-v1`，阶段是 `PHASE04_document-ingestion-parse-runtime`。

本轮 program 不再继续做架构细化或 contract foundation，而是把目标架构推进到第一版真实 runtime 闭环：

```text
上传文档 -> parse -> index -> ask -> Agentic retrieval -> cited answer -> trace/eval -> artifact/feedback
```

最近完成并归档的 foundation program 是 `zuno-master-architecture-implementation-v1`：

- `docs/history/programs/zuno-master-architecture-implementation-v1/`

它已完成 PHASE01-PHASE12，覆盖项目文件夹与代码布局治理、企业知识库产品闭环、Document Ingestion、Single Controller runtime harness、Memory、Tool Control Plane、Agentic GraphRAG / Evidence / Citation、Security Governance、Eval / Observability、Architecture Markdown / HTML refresh 和 release closure。

执行状态入口在 `.agent/programs/`。本轮每个 phase 只有在真实 API / runtime / UI 路径、focused tests、trace / eval 或 verifier 证明后才能关闭；只写 contract、schema 或 README 不能关闭 runtime phase。

PHASE03 已完成 workspace / session / file / ingest / task / approval / event / artifact / feedback 后端 API 与 SSE runtime surface；当前 PHASE04 进入 Document Ingestion / Parse Gateway runtime。

本轮大型 program 的八个方面产物：

1. 项目文件夹与代码布局治理。
2. 企业私有知识库场景与产品闭环。
3. Document Ingestion / Parse Gateway。
4. Single Controller Agent Runtime。
5. Context / Memory 系统。
6. Tool Control Plane。
7. RAG / GraphRAG 知识系统。
8. 安全、评测、观测、文档展示闭环。

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
│  ├─ architecture/        # 当前架构、目标架构、路线图、正式决策
│  ├─ evidence/            # 精选证据
│  ├─ reference/           # 当前术语
│  └─ history/             # 过时或已完成材料归档
├─ .agent/                # Agent 工作流库
└─ AGENTS.md              # 仓库级 Agent 入口
```
