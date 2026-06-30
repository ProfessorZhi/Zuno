# Repository Ownership Matrix

status: current
program: zuno-target-architecture-runtime-full-implementation-v1
phase: PHASE02_runtime-migration-map-and-repo-ownership-lock

## 目标

本文件是当前 runtime-first program 的 PHASE02 代码归属和 runtime 迁移矩阵。它只把当前目录、目标 owner、兼容路径、迁移风险和验证入口说清楚，不把后续 runtime feature 提前写成 Current。

当前事实：

- `src/backend/zuno` 顶层只有 `api / agent / memory / capability / knowledge / platform` 六层。
- `platform/services` 仍是主要 migration source，不能 bulk move。
- `zuno.schema.*`、`zuno.database.*` 和 `zuno.services.*` 是 public legacy import aliases，当前分别指向 `api/dto`、`platform/database` 和 `platform/services`，不能直接删除。
- `platform/compatibility/vendor/fastapi_jwt_auth` 仍是当前兼容路径，`platform/vendor` 只是 PHASE02 建立的目标 owner 和 import guard。
- 新增 runtime 代码不得写入 `platform/compatibility`。compatibility 只保留 legacy import registry 和当前已存在的兼容 vendor 路径。

## Runtime Domain Coverage

| runtime_domain | required current paths | target owner | next runtime phase |
| --- | --- | --- | --- |
| parser | `knowledge/ingestion`; `platform/services/convert_files`; `platform/services/pipeline` | knowledge/ingestion | PHASE04 |
| retrieval | `knowledge`; `platform/services/rag`; `platform/services/retrieval`; `platform/services/deepsearch`; `platform/services/rewrite` | knowledge/retrieval | PHASE09 |
| GraphRAG | `knowledge`; `platform/services/graphrag` | knowledge/graphrag | PHASE05 / PHASE09 |
| memory | `memory`; `platform/services/memory` | memory | PHASE07 |
| tool | `capability`; `platform/services/mcp`; `platform/services/mcp_openai`; `platform/services/sandbox` | capability / platform/security | PHASE08 |
| database | `platform/database`; `zuno.database.*` | platform/database | PHASE03 / PHASE07 |
| workspace | `api`; `platform/services/workspace` | api / agent / platform/workspace | PHASE03 / PHASE06 |
| storage | `platform/storage`; `platform/services/storage` | platform/storage | PHASE03 / PHASE05 |
| queue | `platform/services/queue` | platform/jobs | PHASE05 / PHASE06 |
| sandbox | `platform/security`; `platform/services/sandbox` | platform/security | PHASE08 / PHASE10 |

## Matrix

| current_path | current_role | target_owner | target_path | compat_path | migration_risk | tests | verifier | status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| src/backend/zuno/api | target-layer | api | src/backend/zuno/api | zuno.api.* | medium | tests/api; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current |
| src/backend/zuno/agent | target-layer | agent | src/backend/zuno/agent | zuno.core.* aliases | high | tests/agent; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current |
| src/backend/zuno/memory | target-layer | memory | src/backend/zuno/memory | zuno.services.memory.* during migration | medium | tests/agent; tests/repo/test_backend_facade_layers.py | python tools/scripts/verify_repo_structure.py | current |
| src/backend/zuno/capability | target-layer | capability | src/backend/zuno/capability | zuno.tools.* and zuno.mcp_servers.* aliases | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current |
| src/backend/zuno/knowledge | target-layer | knowledge | src/backend/zuno/knowledge | zuno.services.graphrag.* and zuno.services.retrieval.* aliases | high | tests/graphrag; tests/retrieval; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current |
| src/backend/zuno/platform | target-layer | platform | src/backend/zuno/platform | zuno.services.* zuno.database.* zuno.settings aliases | high | tests/storage; tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current |
| src/backend/zuno/api/dto | physical-dto-owner | api/dto | src/backend/zuno/api/dto | zuno.schema.* | high | tests/api; tests/api/test_workspace_product_loop_contract.py; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/platform/database | physical-database-owner | platform/database | src/backend/zuno/platform/database | zuno.database.* | high | tests/storage; tests/repo/test_repo_structure_consistency.py; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/platform/storage | physical-storage-owner | platform/storage | src/backend/zuno/platform/storage | zuno.services.storage.* during migration | high | tests/storage; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| zuno.schema.* | legacy-public-alias | api/dto | src/backend/zuno/api/dto | src/backend/zuno/platform/compatibility/legacy_aliases.py | high | tests/api; tests/api/test_workspace_product_loop_contract.py; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | legacy-alias-current |
| zuno.database.* | legacy-public-alias | platform/database | src/backend/zuno/platform/database | src/backend/zuno/platform/compatibility/legacy_aliases.py | high | tests/storage; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | legacy-alias-current |
| zuno.services.* | legacy-public-alias | platform/services | src/backend/zuno/platform/services | src/backend/zuno/platform/compatibility/legacy_aliases.py | high | tests/agent; tests/api; tests/retrieval; tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | legacy-alias-current |
| src/backend/zuno/knowledge/ingestion | reserved-import-guard | knowledge/ingestion | src/backend/zuno/knowledge/ingestion | platform/services/convert_files and pipeline remain current | high | tests/repo/test_repo_structure_consistency.py | python tools/scripts/verify_repo_structure.py | target-owner-reserved |
| src/backend/zuno/platform/security | reserved-import-guard | platform/security | src/backend/zuno/platform/security | zuno.services.sandbox and execution_policy remain current | high | tests/tools; tests/repo/test_repo_structure_consistency.py | python tools/scripts/verify_repo_structure.py | target-owner-reserved |
| src/backend/zuno/platform/observability | reserved-import-guard | platform/observability | src/backend/zuno/platform/observability | zuno.utils.runtime_observability alias remains current | medium | tests/agent; tests/repo/test_repo_structure_consistency.py | python tools/scripts/verify_repo_structure.py | target-owner-reserved |
| src/backend/zuno/platform/services/application | migration-source | api / knowledge / workspace | src/backend/zuno/api/services and src/backend/zuno/knowledge | zuno.services.application.* | high | tests/api; tests/agent; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/autobuild | migration-source | capability / platform | src/backend/zuno/capability and src/backend/zuno/platform | zuno.services.autobuild.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/convert_files | migration-source | knowledge/ingestion | src/backend/zuno/knowledge/ingestion | zuno.services.convert_files.* | medium | tests/api; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/deepsearch | migration-source | knowledge/retrieval | src/backend/zuno/knowledge/retrieval | zuno.services.deepsearch.* | medium | tests/retrieval; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/embedding | migration-source | knowledge/retrieval / platform/model_gateway | src/backend/zuno/knowledge/retrieval and src/backend/zuno/platform/model_gateway.py | zuno.services.embedding.* | high | tests/retrieval; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/graphrag | migration-source | knowledge/graphrag | src/backend/zuno/knowledge/graphrag | zuno.services.graphrag.* | high | tests/graphrag; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/lingseek | migration-source | capability/tools | src/backend/zuno/capability/tools | zuno.services.lingseek.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/llm | migration-source | platform/model_gateway | src/backend/zuno/platform/model_gateway.py | zuno.services.llm.* | high | tests/agent; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/mcp | migration-source | capability/mcp | src/backend/zuno/capability/mcp | zuno.services.mcp.* | high | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/mcp_openai | migration-source | capability/mcp | src/backend/zuno/capability/mcp | zuno.services.mcp_openai.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/memory | migration-source | memory | src/backend/zuno/memory | zuno.services.memory.* | medium | tests/agent; tests/repo/test_backend_facade_layers.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/pipeline | migration-source | knowledge/ingestion / platform/jobs | src/backend/zuno/knowledge/ingestion and future platform/jobs | zuno.services.pipeline.* | high | tests/graphrag; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/queue | migration-source | platform/jobs | future src/backend/zuno/platform/jobs | zuno.services.queue.* | high | tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/rag | migration-source | knowledge/retrieval | src/backend/zuno/knowledge/retrieval | zuno.services.rag.* | high | tests/retrieval; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/retrieval | migration-source | knowledge/retrieval | src/backend/zuno/knowledge/retrieval | zuno.services.retrieval.* | high | tests/retrieval; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/rewrite | migration-source | knowledge/retrieval | src/backend/zuno/knowledge/retrieval | zuno.services.rewrite.* | medium | tests/retrieval; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/sandbox | migration-source | platform/security | src/backend/zuno/platform/security | zuno.services.sandbox.* | high | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/storage | migration-source | platform/storage | src/backend/zuno/platform/storage | zuno.services.storage.* | high | tests/storage; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/platform/services/workspace | migration-source | agent / platform/workspace | src/backend/zuno/agent and future platform/workspace | zuno.services.workspace.* | high | tests/agent; tests/api; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | owned-migration-source |
| src/backend/zuno/capability/tools/arxiv | builtin-provider | capability | src/backend/zuno/capability/tools/arxiv | zuno.tools.arxiv.* | low | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/cli_tool | executor-adapter | capability | src/backend/zuno/capability/tools/cli_tool | zuno.tools.cli_tool.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/convert_to_docx | builtin-converter | capability | src/backend/zuno/capability/tools/convert_to_docx | zuno.tools.convert_to_docx.* | low | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/convert_to_pdf | builtin-converter | capability | src/backend/zuno/capability/tools/convert_to_pdf | zuno.tools.convert_to_pdf.* | low | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/crawl_web | builtin-web-provider | capability | src/backend/zuno/capability/tools/crawl_web | zuno.tools.crawl_web.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/delivery | builtin-delivery-provider | capability | src/backend/zuno/capability/tools/delivery | zuno.tools.delivery.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/get_weather | builtin-provider | capability | src/backend/zuno/capability/tools/get_weather | zuno.tools.get_weather.* | low | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/image2text | model-provider-adapter | capability | src/backend/zuno/capability/tools/image2text | zuno.tools.image2text.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/openapi_tool | api-provider-adapter | capability | src/backend/zuno/capability/tools/openapi_tool | zuno.tools.openapi_tool.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/resume_optimizer | builtin-domain-tool | capability | src/backend/zuno/capability/tools/resume_optimizer | zuno.tools.resume_optimizer.* | low | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/send_email | provider-adapter | capability | src/backend/zuno/capability/tools/send_email | zuno.tools.send_email.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/text2image | model-provider-adapter | capability | src/backend/zuno/capability/tools/text2image | zuno.tools.text2image.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/web_reader | builtin-web-provider | capability | src/backend/zuno/capability/tools/web_reader | zuno.tools.web_reader.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/tools/web_search | provider-adapter | capability | src/backend/zuno/capability/tools/web_search | zuno.tools.web_search.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/mcp/servers/arxiv | mcp-provider | capability/mcp | src/backend/zuno/capability/mcp/servers/arxiv | zuno.mcp_servers.arxiv.* | low | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/mcp/servers/lark_mcp | mcp-provider | capability/mcp | src/backend/zuno/capability/mcp/servers/lark_mcp | zuno.mcp_servers.lark_mcp.* | medium | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/mcp/servers/qa_echo | mcp-smoke-server | capability/mcp | src/backend/zuno/capability/mcp/servers/qa_echo | zuno.mcp_servers.qa_echo.* | low | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/mcp/servers/remote_proxy | mcp-compat-proxy | capability/mcp | src/backend/zuno/capability/mcp/servers/remote_proxy | zuno.mcp_servers.remote_proxy.* | high | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/capability/mcp/servers/weather | mcp-provider | capability/mcp | src/backend/zuno/capability/mcp/servers/weather | zuno.mcp_servers.weather.* | low | tests/tools; tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current-owned |
| src/backend/zuno/platform/compatibility/legacy_aliases.py | legacy-import-registry | platform/compatibility | src/backend/zuno/platform/compatibility/legacy_aliases.py | zuno.compatibility and retired public imports | high | tests/legacy_guards/test_zuno_alias_imports.py | python tools/scripts/verify_repo_structure.py | current |
| src/backend/zuno/platform/compatibility/vendor/fastapi_jwt_auth | vendor-shim-current-compat-path | platform/vendor | future src/backend/zuno/platform/vendor/fastapi_jwt_auth | zuno.compatibility.vendor.fastapi_jwt_auth | high | tests/api/test_fastapi_jwt_auth_compat.py | python tools/scripts/verify_repo_structure.py | current-compat-shim |
| src/backend/zuno/platform/vendor | target-vendor-owner | platform/vendor | src/backend/zuno/platform/vendor | no runtime import yet | high | tests/repo/test_repo_structure_consistency.py | python tools/scripts/verify_repo_structure.py | target-owner-reserved |

## Guardrails

- 新增 `platform/services/*` 子目录前，必须先更新 `PLATFORM_SERVICES_TARGET_OWNERS` 和本矩阵。
- 新增 `capability/tools/*` 或 `capability/mcp/servers/*` 前，必须先更新 provider 分类和本矩阵。
- `platform/compatibility` 不接收新 runtime code。只有 `legacy_aliases.py`、`legacy/` 和当前已存在的 `vendor/fastapi_jwt_auth` 兼容路径属于允许范围。
- `platform/vendor` 在 PHASE02 只作为目标 owner 和 import guard；迁移实际 vendor shim 前，必须先更新 `tests/api/test_fastapi_jwt_auth_compat.py` 和 legacy import matrix。
