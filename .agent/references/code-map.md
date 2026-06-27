# 代码地图

## 目的

帮助 Agent 找到当前代码 owner，不复制目标架构设计，也不单独授权代码修改。

## 主要表面

- `apps/web/`：Vue Web 工作区。
- `apps/desktop/`：Electron 桌面壳。
- `src/backend/zuno/`：当前 Python 后端 runtime 真相。
- `src/backend/zuno/api/`：HTTP routes、DTO、auth、response envelope、SSE。
- `src/backend/zuno/services/application/`：应用用例边界。
- `src/backend/zuno/core/`：单一 GeneralAgent runtime 和编排。
- `src/backend/zuno/services/graphrag/`：GraphRAG Project 查询和索引概念。
- `src/backend/zuno/services/retrieval/`：检索规划和 retriever adapters。
- `src/backend/zuno/services/memory/`：记忆基础。
- `src/backend/zuno/database/`：持久化模型和数据库 wiring。
- `tools/`：脚本、启动器、eval 和维护工具。
- `tests/`：仓库级验证和聚焦回归测试。
- `docs/`：正式人类文档。
- `.agent/`：Agent 工作流库和目标设计工作区。

## 当前 Runtime 路径

```text
Completion API
  -> CompletionService
  -> GeneralAgent single loop
  -> prepare_context
  -> ContextOrchestrator.prepare
  -> search_knowledge_base
  -> KnowledgeQueryService
  -> GraphRAGQueryService
  -> RetrievalPlanner / RetrievalOrchestrator
  -> Evidence / Citation / Trace
  -> post_turn_commit
```

## 任务路由

- 后端变更：读 `src/backend/zuno/AGENTS.md`。
- 前端变更：读 `apps/web/AGENTS.md`。
- Eval 变更：读 `tools/evals/zuno/AGENTS.md`。
- 文档或 Agent 工作流变更：读 `AGENTS.md`、`.agent/references/task-routing.md` 和 `.agent/references/workflow.md`。

文档和工作流整理任务不得修改 runtime 代码。如果验证需要修改 runtime，先停止并返回证据。

## 受保护边界

- `src/backend/zuno/`
- `apps/web/`
- `infra/`
- `tools/evals/zuno/*runner*`
- 依赖文件

如果任务授权不包含这些路径，不要触碰它们。
