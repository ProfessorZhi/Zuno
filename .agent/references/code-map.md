# 代码地图

## 目的

帮助 Agent 找到当前代码 owner，不复制目标架构设计，也不单独授权代码修改。

## 主要表面

- `apps/web/`：Vue Web 工作区。
- `apps/desktop/`：Electron 桌面壳。
- `src/backend/zuno/`：当前 Python 后端 runtime 真相。
- `src/backend/zuno/api/`：HTTP routes、DTO、auth、response envelope、SSE。
- `src/backend/zuno/agent/`：单一 GeneralAgent runtime 入口和 runtime / context / post_turn / state / streaming / tool_bridge 薄入口；旧 `zuno.core.*` 由 legacy alias registry 兼容。
- `src/backend/zuno/memory/`：Memory contracts / store / policy / review / retrieval / rendering / engine 薄入口。
- `src/backend/zuno/capability/`：Tool、Skill、MCP、capability registry / selector / policy / execution / trace 薄入口。
- `src/backend/zuno/knowledge/`：RAG / GraphRAG / Evidence / Citation / retrieval / fusion 薄入口。
- `src/backend/zuno/platform/`：配置、数据库、兼容、资源、middleware、model gateway、security、observability、storage 和旧 services 的物理归属。
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

- 后端变更：读本文和 `.agent/references/runtime-call-chain.md`。
- 前端变更：读 `apps/web/AGENTS.md`。
- Eval 变更：读 `tools/evals/zuno/AGENTS.md`。
- 文档或 Agent 工作流变更：读 `AGENTS.md`、`.agent/references/task-routing.md` 和 `.agent/references/workflow.md`。

文档和工作流整理任务不得修改 runtime 代码。如果验证需要修改 runtime，先停止并返回证据。

## 后端包根规则

`src/backend/zuno` 顶层目录只允许六层：

```text
api / agent / memory / capability / knowledge / platform
```

旧入口不允许继续以根级 `.py` alias 文件留在顶层；`zuno.services`、`zuno.core`、`zuno.schema`、`zuno.database`、`zuno.config`、`zuno.resources`、`zuno.tools`、`zuno.utils`、`zuno.compatibility`、`zuno.settings`、`zuno.mcp_servers`、`zuno.middleware`、`zuno.evals` 由 `platform/compatibility/legacy_aliases.py` 注册兼容。

后端实现规则：

- 路由层不拥有业务逻辑或检索策略。
- Application Service 负责用例编排。
- Agent runtime 不能反向依赖 API 层。
- 公共契约变化必须同步 DTO、前端类型和测试。
- 检索、Agent、记忆和 GraphRAG 变更必须对齐对应参考文档和目标架构说明。
- 目标层新入口内部必须优先引用物理 owner，不从 `zuno.services`、`zuno.core` 等 legacy alias 路径反向取对象。

## 受保护边界

- `src/backend/zuno/`
- `apps/web/`
- `infra/`
- `tools/evals/zuno/*runner*`
- 依赖文件

如果任务授权不包含这些路径，不要触碰它们。
