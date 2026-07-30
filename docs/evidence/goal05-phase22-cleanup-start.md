# Goal05 PHASE22 Cleanup Start Evidence

status: in_progress
date: 2026-07-30
branch: codex/goal05-phase15-sandbox-repair

## Scope

本证据记录 PHASE22 的第一个 cleanup 切口：冻结 PHASE21 removal candidates 输入，并将 Product Runtime 默认路径中的两个 legacy alias import 改为 canonical import。

本证据不声明 PHASE22 completed，不声明 legacy-free tree，不声明 fixed benchmark completed，不声明 production ready。

## Implemented

- 新增 `.agent/programs/work-products/phase22-removal-candidates.yaml`，把 PHASE21/PHASE22 startup 发现的 mandatory cleanup 输入冻结为 PHASE22 删除候选。
- `src/backend/zuno/product/runtime_batch.py` 从 `zuno.schema.workspace` 改为 `zuno.api.dto.workspace`。
- `src/backend/zuno/api/services/product/command_service.py` 从 `zuno.database import engine` 改为 `zuno.platform.database import engine`。
- `src/backend/zuno/api/services/workspace.py`、`src/backend/zuno/platform/services/workspace/attachment_service.py`、`src/backend/zuno/platform/services/storage/__init__.py` 与 `src/backend/zuno/capability/tools/text2image/action.py` 的默认链 import 继续改为 canonical `zuno.api.dto` / `zuno.platform` / `zuno.capability`。
- `src/backend/zuno/platform/services/workspace/` 默认 workspace simple/wechat agent 继续改为 canonical `zuno.agent.core` / `zuno.platform.services` / `zuno.api.dto` / `zuno.platform.database` / `zuno.platform.resources` / `zuno.capability` / `zuno.platform.common` import。
- `src/backend/zuno/api/services/upload.py`、`src/backend/zuno/api/services/knowledge_file.py`、`src/backend/zuno/api/services/workspace_session.py` 与 `src/backend/zuno/api/services/user.py` 继续改为 canonical `zuno.platform` / `zuno.api.dto` / `zuno.platform.common` import。
- `src/backend/zuno/api/services/tool.py`、`src/backend/zuno/api/services/knowledge.py`、`src/backend/zuno/api/services/agent.py`、`src/backend/zuno/api/services/history.py`、`src/backend/zuno/api/services/llm.py` 与 `src/backend/zuno/api/services/mcp_server.py` 继续改为 canonical `zuno.platform` / `zuno.api.dto` / `zuno.platform.common` import。
- `src/backend/zuno/platform/services/cli_tool_discovery.py`、`src/backend/zuno/platform/services/simple_api_tool.py`、`src/backend/zuno/platform/services/tool_creation_service.py`、`src/backend/zuno/platform/services/tool_connectivity_service.py`、`src/backend/zuno/platform/services/user_defined_tool_runtime.py` 与 `src/backend/zuno/platform/database/init_data.py` 继续改为 canonical `zuno.platform` / `zuno.api.dto` / `zuno.capability` / `zuno.platform.common` import。
- `src/backend/zuno/platform/services/tool_creation_service.py` 创建用户工具时直接调用 canonical `zuno.platform.database.dao.tool.ToolDao`，拆除 `ToolService` 模块导入期间回跳 `ToolCreationService` 的循环依赖。
- `src/backend/zuno/platform/services/mcp/manager.py`、`src/backend/zuno/platform/services/mcp/multi_client.py`、`src/backend/zuno/platform/services/mcp/load_mcp/tools.py`、`src/backend/zuno/platform/services/mcp_openai/mcp_manager.py` 与 `src/backend/zuno/platform/services/mcp_openai/mcp_util.py` 继续改为 canonical `zuno.platform.services.mcp` / `zuno.platform.services.mcp_openai` / `zuno.api.dto.mcp` import。
- `src/backend/zuno/agent/core/agents/*`、`src/backend/zuno/agent/core/callbacks/*` 与 `src/backend/zuno/agent/core/models/*` 的默认链 import 继续改为 canonical `zuno.agent.core` / `zuno.platform` / `zuno.api.dto` / `zuno.capability` import。
- `src/backend/zuno/api/v1/*` 与 `src/backend/zuno/api/errcode/*` 的控制器 DTO import 继续改为 canonical `zuno.api.dto`，并把 context helper 改为 `zuno.platform.common.contexts`。
- `src/backend/zuno/api/services/message.py`、`src/backend/zuno/api/services/dialog.py`、`src/backend/zuno/api/services/message_events.py`、`src/backend/zuno/api/services/mcp_user_config.py`、`src/backend/zuno/api/services/mcp_stdio_server.py` 与 `src/backend/zuno/api/services/usage_stats.py` 继续改为 canonical `zuno.platform.database` import。
- `src/backend/zuno/platform/database/**/*.py` 内部 DAO、Model、metadata 与默认聚合入口不再通过 `zuno.database.models`、`zuno.services.pipeline` 或 `zuno.utils` 回跳，统一改为 `zuno.platform.database.models`、`zuno.platform.services.pipeline` 与 `zuno.platform.common`。
- `src/backend/zuno/platform/settings.py` 的配置 DTO 类型从 `zuno.schema.common` 改为 `zuno.api.dto.common`。
- `src/backend/zuno/api/services/mcp_agent.py`、`src/backend/zuno/api/services/capability.py` 与 `src/backend/zuno/api/services/agent_skill.py` 继续改为 canonical `zuno.platform.database` / `zuno.platform.services` / `zuno.agent.core` / `zuno.platform.resources` / `zuno.api.dto` import。
- `src/backend/zuno/main.py`、`src/backend/zuno/memory/feedback_consumer.py`、`src/backend/zuno/agent/product_baseline.py`、`src/backend/zuno/api/services/workspace_task_runtime.py` 与 `src/backend/zuno/api/dto/knowledge.py` 继续改为 canonical `zuno.platform.common` / `zuno.platform.database` / `zuno.api.dto` / `zuno.platform.services` import。
- `src/backend/zuno/api/services/completion.py`、`src/backend/zuno/api/services/wechat.py` 与 `src/backend/zuno/api/services/mcp_chat.py` 继续改为 canonical `zuno.agent.core` / `zuno.platform.services` / `zuno.platform.resources` / `zuno.platform.common` / `zuno.api.dto` import。
- `src/backend/zuno/platform/services/application/knowledge/`、`src/backend/zuno/platform/services/rewrite/`、`src/backend/zuno/platform/services/queue/workers.py` 与 `src/backend/zuno/platform/services/queue/messages.py` 继续改为 canonical `zuno.platform.services` / `zuno.agent.core` / `zuno.platform.resources` import。
- `src/backend/zuno/platform/services/queue/runner.py` worker 启动入口继续改为 canonical `zuno.platform.database` / `zuno.platform.services.pipeline` / `zuno.platform.services.queue` import。
- `src/backend/zuno/platform/services/deepsearch/` graph 与 streaming graph 入口继续改为 canonical `zuno.agent.core.models` / `zuno.platform.services.deepsearch` import。
- `src/backend/zuno/platform/services/autobuild/` build、manager 与 client 默认入口继续改为 canonical `zuno.platform.services.autobuild` / `zuno.platform.common` / `zuno.platform.resources` / `zuno.capability` import，并用本地 function schema adapter 替代已消失的 legacy `ChatService.function_to_json` / `action_Function_call`。
- `src/backend/zuno/agent/runtime/factory.py` 默认 local tool control plane assembly 继续改为 canonical `zuno.platform.database` engine import。
- `src/backend/zuno/platform/services/application/__init__.py` 的 application service 入口示例继续改为 canonical `zuno.platform.services.application` 路径，避免文档入口继续引导 legacy alias。
- `src/backend/zuno/platform/common/` 与 `src/backend/zuno/platform/middleware/` 基础层入口继续改为 canonical `zuno.platform.common` / `zuno.platform.services` / `zuno.api.dto` import，并纳入 PHASE22 cleanup verifier 扫描。
- `src/backend/zuno/platform/model_gateway.py` 与 `src/backend/zuno/platform/model_gateway_adapters.py` lazy ModelManager factory 继续改为 canonical `zuno.agent.core.models.manager` import，并纳入 PHASE22 cleanup verifier 扫描。
- `tools/evals/zuno/` fixed benchmark、contract review、stackless/local RAG eval 与 multihop runtime runner 继续改为 canonical `zuno.agent.core` / `zuno.platform` / `zuno.api.dto` import，并纳入 PHASE22 cleanup verifier 扫描。
- `tests/tools/` active Tool Runtime 测试继续改为 canonical `zuno.platform` / `zuno.api.dto` / `zuno.capability` import；`src/backend/zuno/capability/tools/send_email/manifest.yaml` CLI entry 继续改为 canonical `zuno.capability.tools.send_email.cli`，并纳入 PHASE22 cleanup verifier 扫描。
- `tests/storage/` active storage / pipeline / RAG / memory runtime 测试继续改为 canonical `zuno.platform.services` / `zuno.platform.database` / `zuno.api.dto` / `zuno.platform.common` import 和 monkeypatch 路径，并纳入 PHASE22 cleanup verifier 扫描。
- `tests/agent/test_agent_layer_surfaces.py`、`tests/agent/test_memory_layer_surfaces.py` 与 `tests/agent/test_memory_layers.py` 的 Agent / Memory layer active tests 继续改为 canonical `zuno.agent` / `zuno.memory` / `zuno.platform.services` import，并纳入 PHASE22 cleanup verifier 扫描。
- `src/backend/zuno/agent/__init__.py` 顶层 `AgentConfig` / `GeneralAgent` lazy facade 改为直接指向 canonical `zuno.agent.core.agents`，避免继续指向与 `zuno.agent.runtime/` package 冲突的旧 facade 模块名。
- `tests/agent/test_capability_registry.py` active Capability Registry 测试继续改为 canonical `zuno.platform.services.capability_registry` / `zuno.api.dto.capability` import 和 monkeypatch 路径，并纳入 PHASE22 cleanup verifier 扫描。
- `src/backend/zuno/platform/services/pipeline/`、`src/backend/zuno/platform/services/embedding/__init__.py`、`src/backend/zuno/platform/services/llm/__init__.py` 与 `src/backend/zuno/platform/services/convert_files/__init__.py` 继续改为 canonical `zuno.platform.database` / `zuno.platform.services` / `zuno.platform.common` import。
- `src/backend/zuno/platform/services/graphrag/community/`、`src/backend/zuno/platform/services/graphrag/extractors/`、`src/backend/zuno/platform/services/graphrag/graph_store/__init__.py`、`src/backend/zuno/platform/services/graphrag/prompts/__init__.py`、`src/backend/zuno/platform/services/graphrag/retrievers/` 与 `src/backend/zuno/platform/services/graphrag/project/loader.py` 继续改为 canonical `zuno.platform.services.graphrag` import。
- `src/backend/zuno/platform/services/graphrag/query_service.py`、`src/backend/zuno/platform/services/graphrag/orchestrator.py` 与 `src/backend/zuno/platform/services/graphrag/retriever.py` 继续改为 canonical `zuno.platform.services.retrieval` / `zuno.platform.services.graphrag` / `zuno.platform.services.rag` import。
- `src/backend/zuno/platform/services/retrieval/` 默认检索编排、规划、融合和 adapter 入口继续改为 canonical `zuno.platform.services.retrieval` / `zuno.platform.services.graphrag` / `zuno.platform.services.rag` / `zuno.platform.services.rewrite` / `zuno.platform.common` import。
- `src/backend/zuno/platform/services/rag/` 默认 RAG handler、parser、rerank、vector DB 与 doc parser 入口继续改为 canonical `zuno.platform.services.rag` / `zuno.platform.services.retrieval` / `zuno.platform.services.graphrag` / `zuno.api.dto` / `zuno.agent.core` / `zuno.platform.common` import。
- `src/backend/zuno/platform/services/memory/` 默认 Memory client、utils 与 vector store 入口继续改为 canonical `zuno.agent.core` / `zuno.platform.services.memory` / `zuno.platform.database` import。
- `src/backend/zuno/platform/services/sandbox/__init__.py`、`src/backend/zuno/platform/services/capability_registry.py`、`src/backend/zuno/knowledge/ingestion/legacy_cutover.py`、`src/backend/zuno/capability/mcp/servers/remote_proxy/main.py`、`src/backend/zuno/capability/tools/image2text/__init__.py`、`src/backend/zuno/capability/tools/text2image/__init__.py` 与 `src/backend/zuno/capability/tools/send_email/cli.py` 继续改为 canonical `zuno.platform.services` / `zuno.api.dto` / `zuno.capability` import。
- `tools/scripts/verify_repo_structure.py` 的 active program 结构断言推进到 `current_phase: PHASE22`。
- 新增 `tools/scripts/verify_phase22_cleanup_boundary.py` 和 `tests/repo/test_phase22_cleanup_boundary.py`，防止 Product Runtime 重新引入这两个 legacy alias import，并确保 removal candidates 文件存在。
- 新增 `tests/api/test_layered_api_boundaries.py::test_capability_tool_actions_use_canonical_imports`，防止四个 capability tool action 回退到 `zuno.services` / `zuno.resources` / `zuno.utils`。
- `tests/api/test_layered_api_boundaries.py::test_api_service_layer_uses_canonical_platform_imports` 覆盖 API service layer 的 storage、knowledge file、workspace session 和 user canonical import 收口。

## Verification

```text
python tools/scripts/verify_phase22_cleanup_boundary.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_phase22_cleanup_boundary.py tests/repo/test_repo_structure_consistency.py tests/api/test_product_runtime_batch.py tests/api/test_goal03_product_route.py -p no:cacheprovider
pytest -q tests/api/test_layered_api_boundaries.py tests/api/test_workspace_task_runtime.py tests/api/test_workspace_runtime_recovery.py tests/agent/test_workspace_usage_agent_name.py -p no:cacheprovider
pytest -q tests/api/test_layered_api_boundaries.py tests/repo/test_phase22_cleanup_boundary.py -p no:cacheprovider
rg -n "from zuno\.schema\.workspace|from zuno\.database import engine" src/backend/zuno/product src/backend/zuno/api/services/product
rg -n "from zuno\.(services|resources|utils)\.|import zuno\.(services|resources|utils)\." src/backend/zuno/capability/tools/convert_to_docx/action.py src/backend/zuno/capability/tools/convert_to_pdf/action.py src/backend/zuno/capability/tools/get_weather/action.py src/backend/zuno/capability/tools/delivery/action.py src/backend/zuno/api/services/workspace.py src/backend/zuno/platform/services/workspace/attachment_service.py src/backend/zuno/platform/services/storage/__init__.py src/backend/zuno/capability/tools/text2image/action.py
rg -n "from zuno\.(services|schema|utils)\.|import zuno\.(services|schema|utils)\." src/backend/zuno/api/services/upload.py src/backend/zuno/api/services/knowledge_file.py src/backend/zuno/api/services/workspace_session.py src/backend/zuno/api/services/user.py
python tools/scripts/verify_phase22_cleanup_boundary.py
pytest -q tests/api/test_layered_api_boundaries.py tests/repo/test_phase22_cleanup_boundary.py -p no:cacheprovider
```

## Result

```text
PHASE22 cleanup boundary verification passed.
Repository structure verification passed.
27 passed, 1 warning in 69.58s
13 passed in 0.29s
26 passed, 1 warning in 38.70s
14 passed in 0.21s
48 passed, 1 warning in 36.20s
rg returned no matches
PHASE22 cleanup boundary verification passed.
14 passed in 0.16s
PHASE22 cleanup boundary verification passed.
16 passed in 0.23s
python -m compileall -q src/backend/zuno/agent/core src/backend/zuno/api/services/mcp_server.py passed
PHASE22 cleanup boundary verification passed.
16 passed in 0.32s
python -m compileall -q src/backend/zuno/api/v1 src/backend/zuno/api/errcode passed
PHASE22 cleanup boundary verification passed.
16 passed in 0.35s
python -m compileall -q src/backend/zuno/api/services/message.py src/backend/zuno/api/services/dialog.py src/backend/zuno/api/services/message_events.py src/backend/zuno/api/services/mcp_user_config.py src/backend/zuno/api/services/mcp_stdio_server.py src/backend/zuno/api/services/usage_stats.py passed
PHASE22 cleanup boundary verification passed.
16 passed in 0.23s
python -m compileall -q src/backend/zuno/platform/database src/backend/zuno/platform/settings.py passed
PHASE22 cleanup boundary verification passed.
16 passed in 0.38s
python -m compileall -q src/backend/zuno/api/services/mcp_agent.py src/backend/zuno/api/services/capability.py src/backend/zuno/api/services/agent_skill.py passed
PHASE22 cleanup boundary verification passed.
17 passed in 0.33s
python -m compileall -q src/backend/zuno/main.py src/backend/zuno/memory/feedback_consumer.py src/backend/zuno/agent/product_baseline.py src/backend/zuno/api/services/workspace_task_runtime.py src/backend/zuno/api/dto/knowledge.py passed
PHASE22 cleanup boundary verification passed.
17 passed in 0.43s
python -m compileall -q src/backend/zuno/api/services/completion.py src/backend/zuno/api/services/wechat.py src/backend/zuno/api/services/mcp_chat.py passed
PHASE22 cleanup boundary verification passed.
18 passed in 0.99s
python -m compileall -q src/backend/zuno/platform/services/application/knowledge src/backend/zuno/platform/services/rewrite src/backend/zuno/platform/services/queue/workers.py src/backend/zuno/platform/services/queue/messages.py passed
PHASE22 cleanup boundary verification passed.
19 passed in 0.52s
python -m compileall -q src/backend/zuno/platform/services/pipeline src/backend/zuno/platform/services/embedding/__init__.py src/backend/zuno/platform/services/llm/__init__.py src/backend/zuno/platform/services/convert_files/__init__.py passed
PHASE22 cleanup boundary verification passed.
20 passed in 0.60s
python -m compileall -q src/backend/zuno/platform/services/graphrag/community src/backend/zuno/platform/services/graphrag/extractors src/backend/zuno/platform/services/graphrag/graph_store/__init__.py src/backend/zuno/platform/services/graphrag/prompts/__init__.py src/backend/zuno/platform/services/graphrag/retrievers src/backend/zuno/platform/services/graphrag/project/loader.py passed
PHASE22 cleanup boundary verification passed.
21 passed in 0.69s
python -m compileall -q src/backend/zuno/platform/services/graphrag/query_service.py src/backend/zuno/platform/services/graphrag/orchestrator.py src/backend/zuno/platform/services/graphrag/retriever.py passed
PHASE22 cleanup boundary verification passed.
22 passed in 0.63s
python -m compileall -q src/backend/zuno/platform/services/retrieval passed
rg no matches in src/backend/zuno/platform/services/retrieval for legacy alias imports
PHASE22 cleanup boundary verification passed.
23 passed in 0.80s
python -m compileall -q src/backend/zuno/platform/services/rag passed
rg no matches in src/backend/zuno/platform/services/rag for legacy alias imports
PHASE22 cleanup boundary verification passed.
23 passed in 0.33s
python -m compileall -q sandbox init, capability registry, knowledge legacy cutover, remote MCP proxy, image2text/text2image init and send_email cli passed
rg no matches in entrypoint bridge cleanup files for legacy alias imports
PHASE22 cleanup boundary verification passed.
24 passed in 0.54s
python -m compileall -q src/backend/zuno/platform/services/memory passed
rg no matches in src/backend/zuno/platform/services/memory for legacy alias imports
PHASE22 cleanup boundary verification passed.
24 passed in 0.87s
python -m compileall -q src/backend/zuno/platform/services/workspace passed
rg no matches in src/backend/zuno/platform/services/workspace for legacy alias imports
PHASE22 cleanup boundary verification passed.
24 passed in 0.56s
python -m compileall -q src/backend/zuno/platform/services/queue/runner.py passed
rg no matches in src/backend/zuno/platform/services/queue/runner.py for legacy alias imports
PHASE22 cleanup boundary verification passed.
25 passed in 0.24s
python -m compileall -q src/backend/zuno/platform/services/deepsearch passed
rg no matches in src/backend/zuno/platform/services/deepsearch for legacy alias imports
PHASE22 cleanup boundary verification passed.
26 passed in 0.63s
python -m compileall -q src/backend/zuno/platform/services/autobuild src/backend/zuno/platform/services/tool_creation_service.py src/backend/zuno/api/services/tool.py passed
rg no matches in src/backend/zuno/platform/services/autobuild for legacy alias imports
python -c "import zuno.api.services.tool as t; print(t.ToolService.__name__)" passed
autobuild tool schema smoke passed: 14 schemas
PHASE22 cleanup boundary verification passed.
28 passed in 0.47s
python -m compileall -q src/backend/zuno/agent/runtime/factory.py src/backend/zuno/platform/services/application/__init__.py passed
rg no matches in src/backend/zuno/agent/runtime/factory.py src/backend/zuno/platform/services/application/__init__.py for legacy alias imports
PHASE22 cleanup boundary verification passed.
29 passed in 0.50s
python -m compileall -q src/backend/zuno/platform/common src/backend/zuno/platform/middleware src/backend/zuno/platform/config passed
rg no matches in src/backend/zuno/platform/common src/backend/zuno/platform/middleware src/backend/zuno/platform/config for legacy alias imports
PHASE22 cleanup boundary verification passed.
30 passed in 0.52s
python -m compileall -q src/backend/zuno/platform/model_gateway.py src/backend/zuno/platform/model_gateway_adapters.py passed
rg no matches in src/backend/zuno for legacy alias imports outside legacy guards and eval tools
PHASE22 cleanup boundary verification passed.
python -m compileall -q tools/evals/zuno passed
32 passed in 26.26s
rg no matches in tools/evals/zuno for legacy alias imports
PHASE22 cleanup boundary verification passed.
python -m compileall -q tests/tools passed
79 passed in 17.21s
rg no matches in tests/tools and send_email manifest for legacy alias imports
PHASE22 cleanup boundary verification passed.
python -m compileall -q tests/storage passed
27 passed in 46.76s
rg no matches in tests/storage for legacy alias imports
PHASE22 cleanup boundary verification passed.
python -m compileall -q src/backend/zuno/agent/__init__.py tests/agent/test_agent_layer_surfaces.py tests/agent/test_memory_layer_surfaces.py tests/agent/test_memory_layers.py passed
20 passed in 17.43s
rg no matches in selected Agent / Memory layer tests and agent facade for legacy alias references
PHASE22 cleanup boundary verification passed.
python -m compileall -q tests/agent/test_capability_registry.py passed
5 passed in 21.34s
rg no matches in tests/agent/test_capability_registry.py for legacy alias references
```

## Remaining

- `src/backend/zuno/platform/compatibility/legacy_aliases.py` 仍存在，不能在大量生产 import 仍依赖 `zuno.core` / `zuno.services` / `zuno.schema` / `zuno.database` / `zuno.tools` / `zuno.resources` 时直接删除。
- `tests/legacy_guards/` 仍存在，后续必须迁移为 `tests/repo` canonical boundary guards。
- `legacy_general_agent_completion_rollback` 仍是 PHASE22 cleanup candidate。
- Fixed benchmark、full final verification、production readiness truth 和 Program archive 仍未完成。
