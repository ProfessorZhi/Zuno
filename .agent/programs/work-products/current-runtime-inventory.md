# PHASE01 Current Runtime Inventory

phase_id: PHASE01
task_id: P01-T01
start_commit: 9d10f71cc10ea1880a4a738f4500982d6684ede7
status_boundary: "本文件记录最新 main 的 Current 调用链事实，不把 Target 文档或历史 Program 结论写成 Runtime Current。"

## 1. Completion 默认链路

| path | symbol | caller | callee | default_or_legacy | state_owner | side_effect | test_evidence | target_phase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `src/backend/zuno/api/services/completion.py` | `CompletionService` | API completion route / tests | `GeneralAgent` and unified runtime metadata projection | current default surface with local runtime hooks | Product Surface / Agent Core split not yet complete | streams response chunks and reports runtime evidence | `tests/api/test_completion_unified_runtime.py` | PHASE09 |
| `src/backend/zuno/agent/core/agents/general_agent.py` | `GeneralAgent.__init__` | `CompletionService`, direct runtime tests | `build_default_model_gateway()` unless injected | current local Agent loop | Agent Core | constructs model gateway and tool setup surfaces | `tests/agent/runtime/test_runtime_model_roles.py` | PHASE08 |
| `src/backend/zuno/agent/core/agents/general_agent.py` | `GeneralAgent.setup_plugin_tools` | GeneralAgent setup | AgentToolsWithName / user-defined tool surfaces | legacy-compatible tool bridge | Agent Core / Tool Runtime | prepares tool execution candidates | static inventory; bypass registered in P01-T05 | PHASE15 |

## 2. Workspace Task / Product Runtime 链路

| path | symbol | caller | callee | default_or_legacy | state_owner | side_effect | test_evidence | target_phase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `src/backend/zuno/api/v1/workspace.py` | `create_workspace_task`, `approve_workspace_task`, `cancel_workspace_task` | Workspace HTTP routes | `WorkspaceTaskRuntimeService` | current Product API route directly orchestrates runtime service | Product Surface | creates tasks, approves tools, cancels tasks | `tests/api/test_workspace_task_runtime.py`, `tests/e2e/test_unified_agent_product_scenario.py` | PHASE09 |
| `src/backend/zuno/api/services/workspace_task_runtime.py` | `WorkspaceTaskRuntimeService` | Workspace routes/tests | durable ingestion store, durable runtime, unified runtime, retrieval runtime, tool runtime | current local product orchestrator, not final thin Product Command Port | Product Surface currently owns orchestration that Target moves behind ports | writes SQLite/local stores and emits task events | `tests/api/test_workspace_durable_ingest_runtime.py`, `tests/api/test_workspace_runtime_recovery.py` | PHASE09 |
| `src/backend/zuno/api/services/workspace_task_runtime.py` | `_unified_runtime_service` | Workspace task execution | `RuntimeDependencyFactory.for_workspace_task` -> `UnifiedAgentRuntimeService` | current default for workspace unified runtime | Agent Core / Infrastructure | opens SQLite runtime store | `tests/e2e/test_pdf_agent_answer.py` | PHASE08 |
| `src/backend/zuno/api/services/workspace_task_runtime.py` | `_run_workspace_tools_until_interrupt`, `approve_task` | workspace task execution / signal | `_tool_runtime.execute` | current direct service-owned tool execution path | Tool Runtime target, Product Surface current bypass | may execute local tool adapter or create approval interrupt | `tests/api/test_workspace_task_runtime.py` | PHASE15 |

## 3. Unified Runtime / Durable Runtime

| path | symbol | caller | callee | default_or_legacy | state_owner | side_effect | test_evidence | target_phase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `src/backend/zuno/agent/runtime/service.py` | `UnifiedAgentRuntimeService.start` | Workspace runtime / tests | plan selector, step executors, reflection/replan, SQLite store | current local unified runtime | Agent Core | persists run/checkpoint/event/interrupt/plan/observation rows | `tests/agent/runtime/test_runtime_plan_execution.py`, `tests/agent/runtime/test_runtime_restart_persistence.py` | PHASE08 |
| `src/backend/zuno/agent/runtime/sqlite_store.py` | `SQLiteAgentRunStore` | runtime service/factory | SQLite tables for runs/checkpoints/events/interrupts/plan_versions/observations/tool_claims | Developer/CI current adapter | Infrastructure / Agent Core local store | local SQLite writes | `tests/agent/runtime/test_runtime_store.py` | PHASE04 |
| `src/backend/zuno/agent/runtime/checkpointer.py` | `RuntimeGraphCheckpointer` | runtime service | `AgentRunStore` checkpoint/event APIs | local checkpointer bridge, not LangGraph PostgreSQL checkpointer | Agent Core / Infrastructure | writes runtime node and interrupt/complete/cancel checkpoints | `tests/agent/runtime/test_runtime_restart_persistence.py` | PHASE04 |
| `src/backend/zuno/agent/durable_runtime.py` | `SingleControllerDurableRuntime` | workspace service/tests | `InMemoryDurableRuntimeStore` | local in-memory durable surface | Agent Core | stores task state/checkpoint/interrupt/events in memory | `tests/agent/test_single_controller_durable_runtime.py` | PHASE08 |

## 4. Knowledge / Retrieval 链路

| path | symbol | caller | callee | default_or_legacy | state_owner | side_effect | test_evidence | target_phase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `src/backend/zuno/api/services/workspace_task_runtime.py` | `_run_agentic_retrieval` | workspace task execution | `AgenticRetrievalRuntime.answer` | current workspace retrieval path | Knowledge | reads local index runtime | `tests/e2e/test_pdf_agent_answer.py` | PHASE12 |
| `src/backend/zuno/knowledge/agentic_graphrag.py` | `AgenticRetrievalRuntime` | workspace and tests | `KnowledgeIndexRuntime.to_retrieval_payload` | current deterministic local Agentic retrieval surface | Knowledge | no external provider by default | `tests/agent/test_agentic_retrieval_runtime.py` | PHASE12 |
| `src/backend/zuno/knowledge/agentic/runtime.py` | `CorrectiveAgenticRetrievalRuntime.retrieve` | runtime knowledge step / tests | `EvidenceLedger`, quality gate | current corrective retrieval helper | Knowledge | in-memory evidence ledger | `tests/knowledge/test_corrective_retrieval_runtime.py` | PHASE18 |
| `src/backend/zuno/agent/runtime/execution/knowledge_step.py` | knowledge step executor | unified runtime | corrective retrieval runtime | current local runtime hook | Agent Core consumes Knowledge | records retrieval observation | `tests/knowledge/test_corrective_retrieval_runtime.py` | PHASE08 |

## 5. Memory / Capability / Tool / Model 链路

| path | symbol | caller | callee | default_or_legacy | state_owner | side_effect | test_evidence | target_phase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `src/backend/zuno/agent/context.py` | `ContextOrchestrator.prepare` | GeneralAgent/runtime context preparation | Knowledge and memory context helpers | current local context assembly | Agent Core consumes Memory/Knowledge | no durable memory commit by itself | `tests/memory/test_context_pack_engine.py`, runtime tests | PHASE13 |
| `src/backend/zuno/agent/post_turn.py` | `RuntimeTurnLedger` | GeneralAgent post turn | memory/retrieval/tool trace summary | current local post-turn ledger | Agent Core / Observability | records local ledger object | runtime and eval tests | PHASE19 |
| `src/backend/zuno/capability/layer.py` | `CapabilityRouter`, `build_default_capability_layer_registry` | planning/runtime tests | capability registry/tool cards | current capability selection surface | Capability / Skill | no external side effect by selection | `tests/capability/test_capability_skill_layer.py` | PHASE14 |
| `src/backend/zuno/capability/runtime.py` | `ToolControlPlaneRuntime.execute` | workspace service/runtime tests | tool approval policy, executor registry | current local tool control plane | Tool Runtime | executes read/write adapters or returns approval required | `tests/capability/*`, `tests/agent/runtime/test_runtime_store.py` | PHASE15 |
| `src/backend/zuno/platform/model_gateway.py` | `ModelGateway.invoke` | GeneralAgent, runtime model step, ReAct runner | provider selection, budget, fallback trace | current local gateway surface; direct SDK bypasses still exist | Model Gateway | provider invocation when non-mock provider wired | `tests/platform/test_model_gateway.py`, `tests/evals/test_model_gateway_cost_latency.py` | PHASE07 |
| `src/backend/zuno/agent/runtime/execution/model_step.py` | `ModelStepExecutor.execute` | unified runtime | `deps.model_gateway.invoke` | current runtime path uses gateway if dependency exists | Agent Core consumes Model Gateway | model call via gateway | `tests/agent/runtime/test_runtime_real_execution.py` | PHASE08 |

## 6. Rollback / Feature Flags / Default Boundaries

- `src/backend/zuno/agent/runtime/configuration.py` defines `enable_default_model_gateway: bool = True`; disabling it creates an explicit missing dependency observation in runtime model steps.
- Workspace runtime test hooks in `CompletionService.configure_unified_runtime_store_for_tests` and `WorkspaceTaskRuntimeService.configure_unified_runtime_store_for_tests` switch SQLite paths for tests, not product cutover flags.
- `src/backend/zuno/platform/compatibility/legacy_aliases.py` keeps legacy import aliases active and must be carried into PHASE02 compatibility matrix and PHASE22 removal.

## Current / Gap

Current:
- A local vertical runtime exists for Completion and Workspace tasks.
- Agent Core has a local unified runtime, SQLite runtime store, model gateway hook, retrieval observations, reflection/replan tests and tool claim idempotency tests.
- Product Surface still contains orchestration logic in API service layer.

Gap:
- Product routes are not yet thin Command/Query/Projection ports.
- PostgreSQL domain facts, LangGraph PostgreSQL checkpointer, RabbitMQ outbox/inbox and real server integration evidence are not Current.
- Direct model/tool/provider bypasses remain and are registered in `legacy-bypass-inventory.yaml`.
