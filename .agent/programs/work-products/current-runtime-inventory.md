# PHASE01 Current Runtime Inventory

phase_id: PHASE01
task_id: P01-T01
start_commit: 688a50fa5730f8815b2f09050f01eeb42633ae1d
audit_baseline_commit: 688a50fa5730f8815b2f09050f01eeb42633ae1d
branch: codex/P01-T01-runtime-call-chain-inventory
status: completion_candidate
status_boundary: "本文件只记录当前代码、测试和静态搜索能证明的 Runtime 调用链事实；Target 文档、类名、目录和历史 Phase 结论不能提升为 Current。"

## Current

- FastAPI 产品入口集中在 `src/backend/zuno/api/v1/**`，由 `src/backend/zuno/api/router.py` 聚合。
- Completion 默认链路仍是 `CompletionService -> GeneralAgent`，同时暴露 unified runtime metadata/test hooks。
- Workspace Task 默认链路是 `workspace.py -> WorkspaceTaskRuntimeService`，服务层当前直接编排 ingestion、durable runtime、unified runtime、retrieval、tool approval、artifact、event stream。
- Agent Core Current 是本地轻量实现：`GeneralAgent` single loop、`UnifiedAgentRuntimeService`、`SingleControllerDurableRuntime`、SQLite runtime store、local checkpointer、step executor registry。
- Knowledge Current 是 local GraphRAG/Agentic retrieval surface：`KnowledgeQueryService`、`GraphRAGQueryService`、`AgenticRetrievalRuntime`、`CorrectiveAgenticRetrievalRuntime`。
- Model Current 是 `zuno.platform.model_gateway.ModelGateway`，默认 factory 使用 `MockModelProvider` 和 `SimpleEchoProvider`，真实 provider 统一化仍是后续迁移范围。
- Capability/Tool Current 是 capability registry、default tool cards、`ToolControlPlaneRuntime`、system/user-defined tool adapters 和 MCP server surfaces。
- Memory/Observability Current 是 ContextOrchestrator、memory foundation、RuntimeTurnLedger、local trace/eval helpers；不是完整 PostgreSQL Memory/Eval Current。
- Web/Desktop Current 通过 Vue/Electron 调用 HTTP/SSE/bridge surface，不拥有后端领域事实。

## Gap

- Product routes 当前仍包含业务编排入口，未全部降为 thin Command/Query/Projection ports。
- PostgreSQL domain facts、RabbitMQ outbox/inbox、S3/MinIO object store、LangGraph PostgreSQL checkpointer 和 server recovery evidence 不是 P01-T01 Current。
- Security gate 主要是 FastAPI dependency/JWT、middleware 和 local tool approval policy；Target 的 EffectiveSecurityEpoch、PolicyVersion、ActionToken 和 server-side Authorized Projection 尚未完整 Current。
- MCP、CLI、eval、legacy alias、dynamic registry/factory 仍是活跃入口或旁路，需要 P01-T05 做迁移/删除 allowlist。
- Web/Desktop 仍通过旧 DTO、fetchEventSource 和 local bridge 消费产品 surface；断线恢复、撤权、Authorized Projection 等由 P01-T04 继续盘点。

## Plan

- 本任务只修改 PHASE01 work product、evidence、readiness、verifier 和 focused repo test。
- Expand：补齐 runtime inventory 固定字段和动态入口覆盖。
- Verify：让 verifier 检查 P01-T01 必填字段、覆盖类别和 evidence 文件存在。
- Contract：将 P01-T01 readiness 提升为 `completion_candidate`，不关闭 PHASE01，不打开 PHASE02。

## Required Field Legend

每条链必须包含以下字段，字段为空时必须写明 `none_current`、`not_current`、`blocked` 或 `P01-T05` 等边界：

```text
entrypoint
caller
callee
factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker
default implementation
feature flag
state owner
transaction boundary
external side effect
security gate
test evidence
target phase
legacy/removal task
```

## Runtime Chains

### RC-001 Completion HTTP Streaming

| field | value |
| --- | --- |
| entrypoint | `POST /api/v1/completion` in `src/backend/zuno/api/v1/completion.py` |
| caller | Web/API clients and `tests/api/test_completion_unified_runtime.py` |
| callee | `CompletionService` -> `GeneralAgent.astream()`; unified runtime metadata hook for tests |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | FastAPI `@router.post`, string route `/completion`; `CompletionService.configure_unified_runtime_store_for_tests` test hook |
| default implementation | local `GeneralAgent` single loop with model gateway default factory |
| feature flag | no product cutover flag; runtime store hook is test-only |
| state owner | Product Surface owns request/response surface; Agent Core owns run loop behavior |
| transaction boundary | no canonical PostgreSQL transaction; current path streams from in-process service |
| external side effect | model/provider call if configured; stream chunks to HTTP client |
| security gate | API dependency/JWT surface where route applies current `login_user`; no EffectiveSecurityEpoch Current |
| test evidence | `tests/api/test_completion_unified_runtime.py`, `tests/agent/test_generalagent_context_memory_runtime.py` |
| target phase | PHASE08, PHASE09 |
| legacy/removal task | P01-T05 direct provider/tool bypass allowlist; PHASE22 legacy removal |

### RC-002 Workspace Simple Chat Stream

| field | value |
| --- | --- |
| entrypoint | `POST /api/v1/workspace/simple/chat` in `src/backend/zuno/api/v1/workspace.py` |
| caller | `apps/web/src/apis/workspace.ts::workspaceSimpleChatStreamAPI`, workspace default page |
| callee | `WorkspaceService.simple_chat_stream` / `build_direct_image_response` -> legacy workspace simple agent surfaces |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | FastAPI `@router.post`, string route `/workspace/simple/chat`, Web `fetchEventSource` |
| default implementation | current local streaming workspace chat surface |
| feature flag | request fields `workspace_mode`, `execution_mode`, `product_mode`, selected tool/MCP/knowledge ids |
| state owner | Product Surface current route/service; Agent Core target not fully owns this path |
| transaction boundary | in-process stream; no canonical domain transaction |
| external side effect | model/tool/search depending on selected mode and service path |
| security gate | current `login_user` dependency and client token; no Target action token Current |
| test evidence | `tests/api/test_workspace_product_loop_contract.py`, `tests/legacy_guards/test_phase5_workspace_real_runtime_flow.py` |
| target phase | PHASE09, PHASE16 |
| legacy/removal task | P01-T05 legacy workspace simple agent mapping |

### RC-003 Workspace Task Command

| field | value |
| --- | --- |
| entrypoint | `POST /api/v1/workspace/task` in `src/backend/zuno/api/v1/workspace.py` |
| caller | Web workspace task API, E2E tests |
| callee | `WorkspaceTaskRuntimeService.create_task` |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | FastAPI `@router.post`, route prefix `/workspace`, string route `/task` |
| default implementation | `WorkspaceTaskRuntimeService` local product orchestrator |
| feature flag | request-level product mode, retrieval profile, tool/MCP selections; no global runtime cutover flag |
| state owner | Product Surface currently owns task snapshot/events; Agent Core target owns AgentRun/Plan/Outcome |
| transaction boundary | local in-memory/SQLite/durable ingestion stores; no canonical PostgreSQL domain transaction |
| external side effect | may register files, dispatch retrieval, create artifact, prepare tool approval |
| security gate | current `login_user` dependency and route-level ownership; Target Security approval not fully Current |
| test evidence | `tests/api/test_workspace_task_runtime.py`, `tests/e2e/test_unified_agent_product_scenario.py` |
| target phase | PHASE08, PHASE09, PHASE15 |
| legacy/removal task | PHASE02 cutover controller; P01-T05 Product orchestration bypass |

### RC-004 Workspace Task Event Stream

| field | value |
| --- | --- |
| entrypoint | `GET /api/v1/workspace/task/{task_id}/events/stream` in `src/backend/zuno/api/v1/workspace.py` |
| caller | `apps/web/src/apis/workspace.ts::workspaceTaskEventsStreamAPI` |
| callee | `WorkspaceTaskRuntimeService.stream_task_events` -> Starlette `StreamingResponse` |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | FastAPI `@router.get`, Web `fetchEventSource`, string route `/events/stream` |
| default implementation | local event generator over service-owned task event store |
| feature flag | none_current |
| state owner | Product Surface projection/event delivery current; Agent Core/Observability target split incomplete |
| transaction boundary | in-memory/local store stream; no cursor store transaction |
| external side effect | SSE delivery to browser |
| security gate | route user dependency; no reauthorization cursor Current |
| test evidence | `tests/api/test_workspace_runtime_recovery.py`, `tests/frontend/test_workspace_product_loop_types.py` |
| target phase | PHASE09, PHASE16 |
| legacy/removal task | P01-T04 frontend SSE cursor/resume inventory |

### RC-005 Workspace Approval and Cancel Signal

| field | value |
| --- | --- |
| entrypoint | `POST /api/v1/workspace/task/{task_id}/approve`, `POST /api/v1/workspace/task/{task_id}/cancel` |
| caller | Web approval card and API helpers |
| callee | `WorkspaceTaskRuntimeService.approve_task`, `cancel_task` |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | FastAPI decorators; Web click handlers; string routes `/approve`, `/cancel` |
| default implementation | service updates local task/interrupt/tool state |
| feature flag | selected tool approval policy from runtime request/tool config |
| state owner | Security target owns ApprovalDecision; Product/Tool service owns current local approximation |
| transaction boundary | local service state mutation, not canonical append-only command journal |
| external side effect | approval can resume tool execution; cancel can stop future local work |
| security gate | `login_user` plus service validation; no single-use scoped action token Current |
| test evidence | `tests/api/test_workspace_task_runtime.py`, `tests/agent/runtime/test_runtime_interrupt_resume.py` |
| target phase | PHASE09, PHASE15 |
| legacy/removal task | PHASE15 Tool Runtime approval migration; P01-T04 multi-interrupt UI gap |

### RC-006 Workspace Ingestion/File Registration

| field | value |
| --- | --- |
| entrypoint | `POST /api/v1/workspace/file`, `POST /api/v1/workspace/ingest` |
| caller | Web attachment registration, workspace default page |
| callee | `WorkspaceTaskRuntimeService.register_file`, `create_ingest_job` |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | FastAPI decorators; route strings `/file`, `/ingest`; Web `registerRuntimeAttachments` |
| default implementation | durable local ingestion store/object store if configured, otherwise local fallback |
| feature flag | `configure_durable_ingestion` test hook; request product mode/profile |
| state owner | Input/Ingestion target; Product service current owns orchestration |
| transaction boundary | local durable ingestion store; no canonical PostgreSQL/Object transaction pair |
| external side effect | local object/file writes and parse/index job records |
| security gate | route user dependency; no complete upload authorization Current |
| test evidence | `tests/api/test_workspace_durable_ingest_runtime.py`, `tests/knowledge/test_document_ingestion_contract.py` |
| target phase | PHASE10, PHASE11 |
| legacy/removal task | P01-T02 persistence inventory; P01-T05 direct parser/storage bypass |

### RC-007 Unified Runtime Service

| field | value |
| --- | --- |
| entrypoint | `WorkspaceTaskRuntimeService._unified_runtime_service`, direct runtime tests |
| caller | Workspace task execution and `tests/agent/runtime/**` |
| callee | `RuntimeDependencyFactory.for_workspace_task` -> `UnifiedAgentRuntimeService.start` |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | Factory `RuntimeDependencyFactory`; config dataclass `RuntimeFactoryConfig` |
| default implementation | SQLite store + local dependencies + fixed graph node executor |
| feature flag | `enable_memory`, `enable_local_tool_runtime`, `enable_default_model_gateway` |
| state owner | Agent Core current local runtime; Infrastructure owns physical store target |
| transaction boundary | SQLiteAgentRunStore writes runs/checkpoints/events/interrupts/plan/observations/tool claims |
| external side effect | dispatches model/knowledge/tool steps via local dependency ports |
| security gate | preflight fields in step execution are local placeholders; Target Security gate not complete |
| test evidence | `tests/agent/runtime/test_runtime_plan_execution.py`, `tests/agent/runtime/test_runtime_restart_persistence.py`, `tests/api/test_workspace_runtime_recovery.py` |
| target phase | PHASE08, PHASE04 |
| legacy/removal task | PHASE04 PostgreSQL/checkpointer replacement; PHASE08 single controller completion |

### RC-008 Step Executor Registry

| field | value |
| --- | --- |
| entrypoint | `src/backend/zuno/agent/runtime/nodes/core.py::_STEP_EXECUTORS` |
| caller | `UnifiedAgentRuntimeService` graph/node execution |
| callee | model, knowledge, tool, react step executors |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | `StepExecutorRegistry` static registry |
| default implementation | local executor mapping, no plugin loader |
| feature flag | dependency availability decides missing-dependency observations |
| state owner | Agent Core |
| transaction boundary | executor returns observation; store persistence handled by runtime service/store |
| external side effect | model/tool executors may call gateway/tool runtime |
| security gate | local executor validation; no Target EffectiveSecurityEpoch Current |
| test evidence | `tests/agent/runtime/test_runtime_graph_routes.py`, `tests/agent/runtime/test_runtime_real_execution.py` |
| target phase | PHASE08 |
| legacy/removal task | none_current; expand in PHASE08 |

### RC-009 GeneralAgent Loop

| field | value |
| --- | --- |
| entrypoint | `GeneralAgent.astream()` and API services importing `GeneralAgent` |
| caller | Completion service, legacy workspace services, tests |
| callee | `ContextOrchestrator.prepare`, `KnowledgeQueryService.query`, model gateway, tool bridge, `RuntimeTurnLedger.from_runtime` |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | lazy imports via `zuno.agent.runtime`, legacy aliases via `platform/compatibility/legacy_aliases.py`; capability registry in setup |
| default implementation | single GeneralAgent ReAct loop |
| feature flag | `AgentConfig.enable_memory`, selected tools/MCP/knowledge ids |
| state owner | Agent Core current local loop; Memory/Knowledge/Tool owners consumed through local facades |
| transaction boundary | no canonical run transaction; local memory/raw event writes when enabled |
| external side effect | model call, knowledge query, tool setup/execution candidates |
| security gate | local tool approval/permissions surfaces; no full server security decision Current |
| test evidence | `tests/agent/test_generalagent_context_memory_runtime.py`, `tests/legacy_guards/test_phase11b_single_generalagent_cutover.py` |
| target phase | PHASE08, PHASE13, PHASE15 |
| legacy/removal task | PHASE22 legacy alias/import retirement |

### RC-010 Knowledge Query and Agentic Retrieval

| field | value |
| --- | --- |
| entrypoint | `KnowledgeQueryService.query`, `AgenticRetrievalRuntime.answer`, `CorrectiveAgenticRetrievalRuntime.retrieve` |
| caller | GeneralAgent, WorkspaceTaskRuntimeService, runtime knowledge step, tests |
| callee | GraphRAG query service, retrieval planner/orchestrator, local knowledge index runtime, EvidenceLedger |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | lazy facades in `zuno.knowledge.__init__`, compatibility alias `zuno.services.application.knowledge`, runtime dependency factory knowledge adapter |
| default implementation | local deterministic Agentic GraphRAG/retrieval surfaces |
| feature flag | product profile STANDARD/DEEP, graph/rerank settings in knowledge config |
| state owner | Knowledge current local service; Agent Core decides task-level progression target |
| transaction boundary | local index/runtime artifacts; no canonical KnowledgeVersion transaction Current |
| external side effect | none by default beyond local retrieval/index reads |
| security gate | local scope/filter fields; no ACL prefilter proof for all adapters Current |
| test evidence | `tests/agent/test_knowledge_graphrag_runtime_contracts.py`, `tests/knowledge/test_corrective_retrieval_runtime.py`, `tests/e2e/test_pdf_agent_answer.py` |
| target phase | PHASE12, PHASE18 |
| legacy/removal task | P01-T05 GraphRAG alias and direct query bypass inventory |

### RC-011 Model Gateway

| field | value |
| --- | --- |
| entrypoint | `ModelGateway.invoke`, `build_default_model_gateway` |
| caller | GeneralAgent, runtime model step, ReAct runner, tests |
| callee | `MockModelProvider`, `SimpleEchoProvider`, configured provider implementations |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | factory `build_default_model_gateway`; provider list inside gateway |
| default implementation | mock/echo provider set when no real provider injected |
| feature flag | runtime factory `enable_default_model_gateway`; app model settings determine provider availability |
| state owner | Model Gateway |
| transaction boundary | no PostgreSQL ModelCall/Attempt Current; in-memory result/trace objects |
| external side effect | real provider call only when configured; otherwise local mock/echo |
| security gate | local request fields and budget policy; Target residency/redaction/credential gate incomplete |
| test evidence | `tests/platform/test_model_gateway.py`, `tests/evals/test_model_gateway_cost_latency.py`, `tests/agent/runtime/test_runtime_model_roles.py` |
| target phase | PHASE07 |
| legacy/removal task | P01-T05 direct SDK/provider bypass inventory; PHASE07 gateway adoption |

### RC-012 Capability and Tool Runtime

| field | value |
| --- | --- |
| entrypoint | `build_default_capability_layer_registry`, `build_default_tool_control_plane_runtime`, `ToolControlPlaneRuntime.execute` |
| caller | planning/runtime tests, WorkspaceTaskRuntimeService, GeneralAgent tool setup |
| callee | system tool adapters, user-defined tool runtime, MCP tool surfaces |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | capability/tool registries, system tool metadata, MCP server registration |
| default implementation | local tool control plane with approval policy and adapter registry |
| feature flag | request selected tool ids/MCP ids; tool approval policy |
| state owner | Capability owns selection; Tool Runtime owns prepare/attempt/effect target; current code combines some surfaces |
| transaction boundary | local tool claim/idempotency store in runtime tests; no canonical ToolAttempt PostgreSQL Current |
| external side effect | CLI/openapi/email/delivery/weather/user-defined adapters can call external systems when configured |
| security gate | local approval-required state and credential broker; Target Security prepare/execute gate incomplete |
| test evidence | `tests/capability/test_capability_skill_layer.py`, `tests/agent/runtime/test_runtime_tool_control_plane.py`, `tests/tools/test_cli_tool_adapter.py` |
| target phase | PHASE14, PHASE15 |
| legacy/removal task | P01-T05 direct tool execute and external HTTP bypass allowlist |

### RC-013 MCP Servers and MCP API

| field | value |
| --- | --- |
| entrypoint | FastAPI MCP routes, `src/backend/zuno/capability/mcp/servers/**/main.py`, FastMCP `@mcp.tool` surfaces |
| caller | Web MCP settings, MCP tests, external MCP clients for local servers |
| callee | MCP server service, stdio server service, Lark/weather/arxiv/qa_echo/remote_proxy tools |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | FastAPI decorators; MCP protocol; FastMCP tool decorators; stdio server configs |
| default implementation | local MCP management plus bundled local MCP servers |
| feature flag | configured MCP server ids and user config |
| state owner | Capability/Tool target; Product Surface current config routes |
| transaction boundary | service/database config writes where supported; no canonical Tool Runtime transaction |
| external side effect | MCP tools can call external provider APIs or local tool functions |
| security gate | current user dependency/config validation; Target OAuth/approval/security epoch incomplete |
| test evidence | `tests/agent/test_mcp_server_route.py`, `tests/agent/test_mcp_chat_runtime.py` |
| target phase | PHASE14, PHASE15 |
| legacy/removal task | P01-T05 MCP bypass and removal/guard mapping |

### RC-014 Security and Middleware Current

| field | value |
| --- | --- |
| entrypoint | FastAPI dependencies, JWT helpers, `platform/middleware/white_list_middleware.py`, local tool approval policy |
| caller | API routes and tool runtime |
| callee | JWT/user resolution, whitelist path middleware, credential broker/approval checks |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | FastAPI `Depends`; middleware registration; app settings whitelist |
| default implementation | current JWT/whitelist/local approval surfaces |
| feature flag | whitelist paths and tool config settings |
| state owner | Security target; current implementation is distributed across API/platform/tool |
| transaction boundary | no canonical Security decision/audit transaction Current |
| external side effect | may release credentials to tool adapter through broker |
| security gate | this is the current gate; Target fail-closed epoch/action-token model incomplete |
| test evidence | `tests/security/test_security_governance_contract.py`, `tests/api/test_fastapi_jwt_auth_compat.py`, `tests/api/test_workspace_security_observability_runtime.py` |
| target phase | PHASE06, PHASE15, PHASE16 |
| legacy/removal task | PHASE06 security foundation; P01-T05 bypass guard |

### RC-015 Observability/Eval Runtime

| field | value |
| --- | --- |
| entrypoint | `RuntimeTurnLedger`, workspace retrieval observability route, eval CLI runners |
| caller | GeneralAgent post-turn, workspace API, eval scripts |
| callee | local trace/eval helpers, EnterpriseRAG/rag_eval runners |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | CLI `argparse` scripts under `tools/evals/zuno/**`; route `/workspace/retrieval-observability` |
| default implementation | local evidence/trace summary and eval file artifacts |
| feature flag | eval profile settings, local embedding/rerank server config |
| state owner | Observability/Eval target; current local projection artifacts |
| transaction boundary | file/local trace outputs; no canonical append-only ingest store Current |
| external side effect | eval scripts may call local/remote model endpoints if configured |
| security gate | no production export gate Current; eval config controls local endpoints |
| test evidence | `tests/evals/test_enterprise_rag_paired_benchmark.py`, `tests/evals/test_observability_trace_contract.py`, `docs/evidence/unified-agent-runtime-phase13-release-gate.md` |
| target phase | PHASE19, PHASE20 |
| legacy/removal task | PHASE20 fixed benchmark and evidence registry |

### RC-016 Queue/Worker and Async Entrypoints

| field | value |
| --- | --- |
| entrypoint | `asyncio.create_task` in WeChat route; ingestion/eval/rebuild CLI scripts; local queue tests |
| caller | WeChat webhook, developer/eval operators, test suite |
| callee | WeChat agent task, rebuild/eval ingestion functions, storage queue helpers |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | FastAPI `/wechat`; Python `argparse`; `if __name__ == "__main__"`; local worker scripts |
| default implementation | in-process task or CLI runner; RabbitMQ not Current |
| feature flag | app settings for RabbitMQ in some eval ingestion scripts; usually disabled locally |
| state owner | Infrastructure target; current local async helpers |
| transaction boundary | no durable queue/inbox/outbox transaction Current |
| external side effect | WeChat response/send, local index rebuild, eval corpus ingestion |
| security gate | route signature/config where implemented; no universal worker lease/fencing Current |
| test evidence | `tests/storage/test_queue.py`, `tests/tools/test_launcher_scripts.py`, eval runner tests |
| target phase | PHASE04, PHASE10, PHASE20 |
| legacy/removal task | P01-T02 infrastructure inventory; P01-T05 subprocess/CLI bypass inventory |

### RC-017 Web Product Surface

| field | value |
| --- | --- |
| entrypoint | Vue routes in `apps/web/src/router/index.ts`, API clients in `apps/web/src/apis/*.ts` |
| caller | browser user |
| callee | `/api/v1/agent`, `/workspace`, `/knowledge`, `/tool`, `/mcp_server`, `/config`, `/usage` HTTP/SSE routes |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | Vue Router route table; `fetchEventSource`; shared request utility |
| default implementation | browser client consumes current backend DTOs and streams |
| feature flag | UI mode, workspace mode, execution mode, selected knowledge/tool/MCP/agent skill ids |
| state owner | Product Surface UI projection only; frontend is not source fact |
| transaction boundary | browser local state only; no domain transaction |
| external side effect | HTTP/SSE calls, file upload |
| security gate | browser token plus backend route checks; client values untrusted |
| test evidence | `tests/frontend/test_workspace_product_loop_types.py`, `tests/frontend/test_product_wiring_v1_api_contract.py` |
| target phase | PHASE16 |
| legacy/removal task | P01-T04 frontend and desktop inventory |

### RC-018 Desktop Bridge

| field | value |
| --- | --- |
| entrypoint | `apps/desktop/main.cjs`, `preload.cjs`, `bridge.cjs` |
| caller | Electron desktop shell |
| callee | Web app and local bridge runtime surfaces |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | Electron main/preload bridge |
| default implementation | desktop shell wraps Web product surface |
| feature flag | desktop package/runtime settings |
| state owner | Product Surface channel; not domain owner |
| transaction boundary | local IPC/window state; no backend domain transaction |
| external side effect | opens local windows, may call backend HTTP through web app |
| security gate | Electron preload/bridge isolation current; Target typed IPC security not proven |
| test evidence | `tests/tools/test_launcher_scripts.py`, P01-T04 pending desktop smoke evidence |
| target phase | PHASE16 |
| legacy/removal task | P01-T04 Desktop smoke and contract parity |

### RC-019 Compatibility Legacy Alias and Lazy Facade Entrypoints

| field | value |
| --- | --- |
| entrypoint | `src/backend/zuno/__init__.py`, `platform/compatibility/legacy_aliases.py`, module `__getattr__` lazy exports |
| caller | legacy imports in tests and compatibility code |
| callee | target physical modules under `agent`, `knowledge`, `capability`, `platform` |
| factory/registry/decorator/plugin loader/env flag/string route/MCP/CLI/worker | legacy alias registry and lazy facade maps |
| default implementation | compatibility import bridge |
| feature flag | none_current |
| state owner | Repository governance/compatibility; target owners remain physical modules |
| transaction boundary | import-time side effect only |
| external side effect | mutates `sys.modules` alias registry |
| security gate | none_current |
| test evidence | `tests/legacy_guards/test_zuno_alias_imports.py`, `tests/repo/test_lazy_facade_static_exports.py` |
| target phase | PHASE02, PHASE22 |
| legacy/removal task | PHASE22 alias removal; P01-T05 allowlist |

## Dynamic Entrypoint Coverage

| surface | code anchor | current finding | target phase | removal/next task |
| --- | --- | --- | --- | --- |
| FastAPI Decorator | `src/backend/zuno/api/v1/**/*.py` | Product/API routes are active runtime entrypoints; Workspace routes still orchestrate runtime service directly. | PHASE09/16 | P01-T04/P01-T05 |
| Registry | `StepExecutorRegistry`, capability registry, tool registry | Local static registries choose step/tool/capability behavior. | PHASE08/14/15 | PHASE14/15 |
| Factory | `RuntimeDependencyFactory`, `build_default_model_gateway`, `build_default_tool_control_plane_runtime` | Factories select local SQLite/model/tool/memory/knowledge defaults. | PHASE04/07/08/15 | PHASE02 cutover |
| Plugin Loader | MCP stdio/server config and user-defined tools | MCP/tool loading exists; Product runtime ownership remains split. | PHASE14/15 | P01-T05 |
| Env Flag | `ZUNO_CONFIG`, `AGENTCHAT_CONFIG`, app settings, runtime config booleans | Config decides DB/model/rag/rabbitmq/tool defaults; not a full cutover controller. | PHASE02/04/07 | P01-T02 |
| String Route | Web API clients and FastAPI route literals | Web/Desktop depend on hard-coded `/api/v1/**` routes. | PHASE16 | P01-T04 |
| MCP | `src/backend/zuno/capability/mcp/servers/**` | Local MCP protocol/tool surfaces are active entrypoints. | PHASE14/15 | P01-T05 |
| CLI | `tools/evals/zuno/**`, `tools/scripts/**`, `tools/migrations/**` | Eval, migration, cleanup and rebuild scripts can enter runtime/data paths. | PHASE20/P01-T02 | P01-T05 |
| Worker | `asyncio.create_task`, eval ingestion/rebuild scripts, local queue tests | In-process/CLI async exists; RabbitMQ worker Target not Current. | PHASE04/10/20 | P01-T02 |

## Evidence Summary

- Static route/factory/registry search command is recorded in `docs/evidence/phase01-runtime-call-chain-inventory.md`.
- Focused runtime evidence remains local/unit/integration evidence, not full production recovery proof.
- P01-T01 is a `completion_candidate`; PHASE01 remains open until P01-T02..T06 and Coordinator closure complete.
