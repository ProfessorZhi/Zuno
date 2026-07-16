# PHASE01 P01-T05 Legacy / Bypass Inventory Evidence

phase_id: PHASE01
task_id: P01-T05
status: completed_for_work_package
commit: 688a50fa5730f8815b2f09050f01eeb42633ae1d
start_commit: c01420e915db19a3b0d6f979ca4450c8d5de0c85
working_branch: codex/P01-T05-legacy-bypass-inventory

## Current

本证据只证明 P01-T05 的 legacy / alias / bypass inventory、temporary allowlist、evidence、verifier 和 focused test 已按静态事实补齐。它不证明 PHASE01 全部关闭，不证明 PHASE02 guard 已经实现，也不证明 PHASE07 Model Gateway、PHASE15 Tool Runtime 或 PHASE22 Legacy Removal 已完成。

## Gap

- PHASE02 仍需把 inventory 变成 fail-closed static/dynamic guard，新增未登记旁路必须默认失败。
- 动态 registry / factory / monkey-patch 仍需 runtime sampling；本轮只登记静态可复现发现。
- 各 owner phase 仍需迁移或删除已登记的 Provider SDK、MCP、HTTP、subprocess、DB write、old DTO、old Store、old Runtime 和 legacy alias surface。

## Plan

- PHASE02：以 `.agent/programs/work-products/temporary-allowlist.yaml` 为唯一临时例外源建立 bypass guard。
- PHASE07/12：将 Provider SDK、RAG embedding/rerank 和直接 HTTP provider 接入 Model Gateway / Knowledge owner。
- PHASE09/10：将 route/frontend legacy DTO 和 deprecated endpoint 收口到 Product Contract。
- PHASE15/16：将 Tool execute、MCP、OpenAPI/HTTP、subprocess 和 side effect reconciliation 收口到 Tool Runtime / Security。
- PHASE22：删除 legacy alias、legacy directory 和 temporary allowlist。

## Environment

```text
OS: Windows
Shell: PowerShell without login profile
Repository: F:\internship-work\resume&resume project\02_projects\Zuno
```

## Search Commands

```powershell
rg -n --glob '!docs/history/**' --glob '!node_modules/**' --glob '!*.lock' "from (openai|anthropic|langchain_openai)|import (openai|anthropic|langchain_openai)|AsyncOpenAI|OpenAI\(|ChatOpenAI|DashScope|dashscope" src apps tests tools .agent docs
rg -n --glob '!docs/history/**' --glob '!node_modules/**' --glob '!*.lock' "\.execute\(" src apps tests tools .agent docs
rg -n --glob '!docs/history/**' --glob '!node_modules/**' --glob '!*.lock' "call_tool|list_tools|MCPClient|MultiServerMCPClient" src apps tests tools .agent docs
rg -n --glob '!docs/history/**' --glob '!node_modules/**' --glob '!*.lock' "subprocess|create_subprocess_exec|Popen\(" src apps tests tools .agent docs
rg -n --glob '!docs/history/**' --glob '!node_modules/**' --glob '!*.lock' "legacy|Legacy|deprecated|Deprecated" src apps tests tools .agent docs
rg -n --glob '!docs/history/**' --glob '!node_modules/**' --glob '!*.lock' "Session\(|sessionmaker|\.commit\(|\.add\(|\.delete\(|execute\(.*select|select\(" src/backend/zuno
```

## Result Counts

| Scan | Count | Boundary |
| --- | ---: | --- |
| Provider SDK / provider endpoint | 82 | Broad scan includes tests, docs and config; inventory keeps production or migration-relevant paths. |
| Direct `.execute(` | 77 | Includes runtime executors, tests and SQL execute false positives; inventory records Tool execute and old Store risk. |
| MCP direct call/list | 67 | Includes MCP manager, util, client and generated remote proxy paths. |
| subprocess | 113 | Includes tools/tests; inventory records production tool, sandbox and conversion paths. |
| legacy / deprecated | 854 | Broad compatibility scan; inventory records active alias, legacy directory, old DTO and frontend compatibility paths. |
| Cross-owner DB writes | 352 | Broad SQL/vector-store scan; inventory records active DAO, Memory store, Agent SQLite and RAG vector write surfaces. |

## Sample Findings

- Provider SDK: `src/backend/zuno/agent/core/models/manager.py`, `usage_model.py`, `tool_call.py`, `reason_model.py`, `embedding.py`, `anthropic.py`, `platform/services/rag/embedding.py`, `platform/services/mcp_openai/mcp_manager.py`, `platform/services/autobuild/client.py`, `platform/common/extract.py`, `capability/tools/resume_optimizer/action.py`.
- MCP direct call: `platform/services/mcp/load_mcp/tools.py`, `platform/services/mcp/multi_client.py`, `platform/services/mcp_openai/mcp_client.py`, `mcp_manager.py`, `mcp_util.py`, `capability/mcp/servers/remote_proxy/main.py`.
- HTTP side effect: `platform/services/rag/rerank.py`, `platform/services/rag/vl_embedding.py`, `capability/tools/openapi_tool/adapter.py`, `platform/services/tool_connectivity_service.py`, `platform/services/workspace/attachment_service.py`, `platform/services/simple_api_tool.py`.
- subprocess: `capability/tools/cli_tool/adapter.py`, `platform/services/sandbox/pyodide.py`, `capability/tools/convert_to_pdf/action.py`, `platform/services/convert_files/convert_pdf.py`.
- Legacy / old surface: `platform/compatibility/legacy_aliases.py`, `platform/compatibility/legacy/__init__.py`, `tests/legacy_guards/**`, `api/dto/agent.py`, `api/dto/knowledge.py`, `apps/web/src/utils/retrieval.ts`, `knowledge-config.ts`, `user-avatars.ts`.
- Cross-owner DB writes: `platform/database/dao/**`, `memory/store.py`, `agent/runtime/sqlite_store.py`, `platform/services/rag/vector_db/chroma_client.py`, `milvus_lite_client.py`, `platform/services/memory/vector_stores/chroma.py`.
- Dynamic bypass: `knowledge/{__init__,citation,evidence,trace,retrieval/__init__}.py` and `platform/__init__.py` use lazy import / `import_module` / `getattr` facade patterns.

## Updated Artifacts

```text
.agent/programs/work-products/legacy-bypass-inventory.yaml
.agent/programs/work-products/temporary-allowlist.yaml
.agent/programs/work-products/phase-readiness.yaml
docs/evidence/phase01-legacy-bypass-inventory.md
tools/scripts/verify_phase01_complete_baseline.py
tests/repo/test_phase01_complete_baseline.py
```

## Artifact Hash

```text
legacy-bypass-inventory.yaml SHA256: 0DE8EF0FB7EB1EE1693B2F20C48E660E3EF94343E5FB8905BB133F1D4162A2A7
temporary-allowlist.yaml SHA256: 67C69DE62C6CE1207288050B0D5EFB0EC7AE1DA0550344415FF4C853425DF257
```

## Guard Gaps

- `tools/scripts/verify_phase01_complete_baseline.py` now checks required fields, inventory/allowlist path parity, required bypass categories, placeholder `current_callers`, and P01-T05 evidence fields.
- No runtime fail-closed guard exists yet for newly introduced provider SDK imports, direct `.execute(` calls, direct MCP calls, subprocess calls, legacy directories, old DTO additions or cross-owner DB writes.
- PHASE02 must create that guard before inventory can be treated as enforcement rather than evidence.
