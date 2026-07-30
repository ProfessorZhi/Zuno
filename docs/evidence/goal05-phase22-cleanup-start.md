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
- `src/backend/zuno/api/services/upload.py`、`src/backend/zuno/api/services/knowledge_file.py`、`src/backend/zuno/api/services/workspace_session.py` 与 `src/backend/zuno/api/services/user.py` 继续改为 canonical `zuno.platform` / `zuno.api.dto` / `zuno.platform.common` import。
- `src/backend/zuno/api/services/tool.py`、`src/backend/zuno/api/services/knowledge.py`、`src/backend/zuno/api/services/agent.py`、`src/backend/zuno/api/services/history.py`、`src/backend/zuno/api/services/llm.py` 与 `src/backend/zuno/api/services/mcp_server.py` 继续改为 canonical `zuno.platform` / `zuno.api.dto` / `zuno.platform.common` import。
- `src/backend/zuno/platform/services/cli_tool_discovery.py`、`src/backend/zuno/platform/services/simple_api_tool.py`、`src/backend/zuno/platform/services/tool_creation_service.py`、`src/backend/zuno/platform/services/tool_connectivity_service.py`、`src/backend/zuno/platform/services/user_defined_tool_runtime.py` 与 `src/backend/zuno/platform/database/init_data.py` 继续改为 canonical `zuno.platform` / `zuno.api.dto` / `zuno.capability` / `zuno.platform.common` import。
- `src/backend/zuno/platform/services/mcp/manager.py`、`src/backend/zuno/platform/services/mcp/multi_client.py`、`src/backend/zuno/platform/services/mcp/load_mcp/tools.py`、`src/backend/zuno/platform/services/mcp_openai/mcp_manager.py` 与 `src/backend/zuno/platform/services/mcp_openai/mcp_util.py` 继续改为 canonical `zuno.platform.services.mcp` / `zuno.platform.services.mcp_openai` / `zuno.api.dto.mcp` import。
- `src/backend/zuno/agent/core/agents/*`、`src/backend/zuno/agent/core/callbacks/*` 与 `src/backend/zuno/agent/core/models/*` 的默认链 import 继续改为 canonical `zuno.agent.core` / `zuno.platform` / `zuno.api.dto` / `zuno.capability` import。
- `src/backend/zuno/api/v1/*` 与 `src/backend/zuno/api/errcode/*` 的控制器 DTO import 继续改为 canonical `zuno.api.dto`，并把 context helper 改为 `zuno.platform.common.contexts`。
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
```

## Remaining

- `src/backend/zuno/platform/compatibility/legacy_aliases.py` 仍存在，不能在大量生产 import 仍依赖 `zuno.core` / `zuno.services` / `zuno.schema` / `zuno.database` / `zuno.tools` / `zuno.resources` 时直接删除。
- `tests/legacy_guards/` 仍存在，后续必须迁移为 `tests/repo` canonical boundary guards。
- `legacy_general_agent_completion_rollback` 仍是 PHASE22 cleanup candidate。
- Fixed benchmark、full final verification、production readiness truth 和 Program archive 仍未完成。
