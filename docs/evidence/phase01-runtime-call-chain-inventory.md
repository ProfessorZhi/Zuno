# PHASE01 Runtime Call-chain Inventory Evidence

task_id: P01-T01
phase_id: PHASE01
branch: codex/P01-T01-runtime-call-chain-inventory
commit: 688a50fa5730f8815b2f09050f01eeb42633ae1d
environment: Windows PowerShell, repository worktree `C:\Users\Administrator\.codex\worktrees\5fa7\Zuno`
result: completion_candidate

## Scope

本证据只证明 P01-T01 runtime call-chain inventory 已按当前代码和测试补齐。它不证明 PHASE01 completed，不证明 Runtime 行为已迁移，不证明 PostgreSQL/RabbitMQ/Object Store/LangGraph PostgreSQL Checkpointer 已成为 Current。

## Commands

| command | result |
| --- | --- |
| `git status --short --branch` | passed; branch `codex/P01-T01-runtime-call-chain-inventory`, clean before edits |
| `git rev-parse HEAD` | passed; `688a50fa5730f8815b2f09050f01eeb42633ae1d` |
| `rg -n "APIRouter\|@router\.\|include_router\|add_api_route\|EventSourceResponse\|StreamingResponse\|BackgroundTasks\|asyncio\.create_task\|ThreadPoolExecutor\|subprocess\|click\.command\|argparse\|if __name__ == .__main__.\|FastMCP\|@mcp\.tool\|register\|Registry\|Factory\|build_default\|from_env\|os\.getenv\|settings\.\|enable_\|feature" src/backend apps/desktop apps/web/src tools -g "*.py" -g "*.ts" -g "*.vue" -g "*.cjs" -g "*.ps1"` | passed; sampled static routes, dynamic registries/factories, env/config flags, CLI/worker/MCP surfaces |
| `rg -n "CompletionService\|WorkspaceTaskRuntimeService\|UnifiedAgentRuntimeService\|RuntimeDependencyFactory\|GeneralAgent\|SingleControllerDurableRuntime\|AgenticRetrievalRuntime\|ToolControlPlaneRuntime\|ModelGateway\|ContextOrchestrator\|RuntimeTurnLedger\|KnowledgeQueryService\|GraphRAGQueryService" src/backend tests` | passed; sampled core runtime anchors and focused test evidence |
| `rg -n "get\(\|post\(\|put\(\|delete\(\|patch\(\|EventSource\|fetch\(\|request\(\|axios\|workspace\|completion\|knowledge\|mcp\|tool\|agent" apps/web/src apps/desktop` | passed; sampled Web/Desktop API and stream entrypoints |

## Sampled Code Paths

- `src/backend/zuno/api/v1/completion.py` -> `src/backend/zuno/api/services/completion.py` -> `src/backend/zuno/agent/core/agents/general_agent.py`.
- `src/backend/zuno/api/v1/workspace.py` -> `src/backend/zuno/api/services/workspace_task_runtime.py` -> `src/backend/zuno/agent/runtime/service.py`.
- `src/backend/zuno/agent/runtime/factory.py` -> `RuntimeDependencyFactory` -> SQLite store, memory, model gateway, corrective retrieval, tool runtime.
- `src/backend/zuno/agent/runtime/nodes/core.py` -> `StepExecutorRegistry` -> model/knowledge/tool/react executors.
- `src/backend/zuno/platform/model_gateway.py` -> `ModelGateway.invoke` and `build_default_model_gateway`.
- `src/backend/zuno/capability/runtime.py` -> `ToolControlPlaneRuntime` and default runtime factory.
- `src/backend/zuno/knowledge/agentic_graphrag.py` and `src/backend/zuno/knowledge/agentic/runtime.py`.
- `apps/web/src/apis/workspace.ts` -> workspace command/query/SSE routes.
- `apps/desktop/main.cjs`, `apps/desktop/preload.cjs`, `apps/desktop/bridge.cjs`.

## Dynamic Registry / Factory Findings

- Registry: `StepExecutorRegistry`, capability registry, tool registry, GraphRAG prompt/runtime registries.
- Factory: `RuntimeDependencyFactory`, `build_default_model_gateway`, `build_default_tool_control_plane_runtime`, strategy selector factory.
- Decorator: FastAPI `@router.*` routes and FastMCP tool decorators.
- Plugin Loader: MCP stdio/server and user-defined tool surfaces.
- Env Flag / Config: `ZUNO_CONFIG`, `AGENTCHAT_CONFIG`, runtime booleans `enable_memory`, `enable_local_tool_runtime`, `enable_default_model_gateway`, app settings for RabbitMQ/RAG/model/tool.
- MCP: bundled arxiv, weather, qa_echo, remote proxy and Lark MCP server trees.
- CLI / Worker: eval runners, migrations, launchers, rebuild scripts, `asyncio.create_task` WeChat path.

## Artifact Hash

```text
current-runtime-inventory.md sha256: 7ED7D08CAB1725C0FC8BD4F8155E0758CF4A3B659EF47F8326E89AE31C785BC7
```

## Not-run Commands

- Full backend/web/desktop CI was not run because P01-T01 scope is inventory and focused verifier/test update only.
- Real PostgreSQL/RabbitMQ/Object Store/Checkpointer integration was not run; those are P01-T02/PHASE04 scope and are not claimed Current here.
