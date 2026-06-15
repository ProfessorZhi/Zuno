# Phase 2: Service Migration

## Status

This phase is currently paused.

Do not treat it as the active execution path until:

1. `Phase 0: Stable Runtime Recovery` from `../plans/stable-baseline-recovery-and-runtime-deepening-plan.md` is complete
2. the restored stable runtime has been user-checked

Until then, this file remains part of the long-term phase model, not the current execution priority.

## Goal

Move the real backend service boundary from `src/backend` toward `services/api`.

## Why This Phase Exists

The repo cannot close the service migration while startup, implementation, and verification still span both `services/api` and `src/backend`.

## What Changes Here

- backend directory migration
- startup path migration
- Docker and launcher path sync
- import path cleanup
- test and eval path sync

## Current Starting Point

The current repo has already exposed `services/api` as the migration-facing backend startup root.
`services/api/src/zuno/` now contains the migration-facing app entry layer (`main.py`, `settings.py`, `config/`, `config.example.yaml`, `schema/`, `middleware/`, `mcp_servers/`), the API entry layer (`api/__init__.py`, `api/router.py`, `api/v1/__init__.py`), selected thin route controllers (`api/v1/agent.py`, `agent_skill.py`, `capability.py`, `completion.py`, `config.py`, `dialog.py`, `history.py`, `knowledge.py`, `knowledge_file.py`, `llm.py`, `mcp_agent.py`, `mcp_chat.py`, `mcp_server.py`, `mcp_stdio_server.py`, `mcp_user_config.py`, `message.py`, `tool.py`, `upload.py`, `usage_stats.py`, `user.py`, `wechat.py`, `workspace.py`), selected service-layer modules (`api/services/__init__.py`, `agent.py`, `agent_skill.py`, `capability.py`, `completion.py`, `dialog.py`, `history.py`, `knowledge.py`, `knowledge_file.py`, `llm.py`, `mcp_agent.py`, `mcp_chat.py`, `mcp_server.py`, `mcp_stdio_server.py`, `mcp_user_config.py`, `message.py`, `mineru.py`, `tool.py`, `upload.py`, `usage_stats.py`, `user.py`, `wechat.py`, `workspace.py`, `workspace_session.py`), selected runtime support modules (`core/__init__.py`, `core/agents/__init__.py`, `core/agents/general_agent.py`, `core/agents/structured_response_agent.py`, `core/callbacks/__init__.py`, `core/callbacks/usage_metadata.py`, `core/graphs/__init__.py`, `core/graphs/domain_qa_graph.py`, `core/graphs/multi_agent_supervisor_graph.py`, `core/graphs/states.py`, `core/models/__init__.py`, `core/models/anthropic.py`, `core/models/embedding.py`, `core/models/manager.py`, `core/models/reason_model.py`, `core/runtime/__init__.py`, `core/runtime/agent_runtime.py`, `database/__init__.py`, `database/init_data.py`, `database/session.py`, `database/metadata.py`, `database/models/__init__.py`, `database/models/*.py`, `database/dao/__init__.py`, `database/dao/*.py`, `prompts/__init__.py`, `prompts/completion.py`, `prompts/mcp.py`, `prompts/skill.py`, `services/__init__.py`, `services/execution_policy.py`, `services/pipeline/__init__.py`, `services/pipeline/manager.py`, `services/pipeline/models.py`, `services/pipeline/stages.py`, `services/queue/__init__.py`, `services/queue/client.py`, `services/queue/messages.py`, `services/queue/runner.py`, `services/queue/workers.py`, `services/rag/__init__.py`, `services/rag/embedding.py`, `services/rag/es_client.py`, `services/rag/handler.py`, `services/rag/parser.py`, `services/rag/retrieval.py`, `services/rag/rerank.py`, `services/rag/vl_embedding.py`, `services/rag/vector_db/__init__.py`, `services/rag/vector_db/chroma_client.py`, `services/rag/vector_db/milvus_client.py`, `services/rag/vector_db/milvus_lite_client.py`, `services/rag/doc_parser/__init__.py`, `services/rag/doc_parser/chunk_ids.py`, `services/rag/doc_parser/docx.py`, `services/rag/doc_parser/excel.py`, `services/rag/doc_parser/image.py`, `services/rag/doc_parser/markdown.py`, `services/rag/doc_parser/other_file.py`, `services/rag/doc_parser/pdf.py`, `services/rag/doc_parser/pptx.py`, `services/rag/doc_parser/text.py`, `services/redis.py`, `services/retrieval/__init__.py`, `services/retrieval/fusion.py`, `services/retrieval/models.py`, `services/retrieval/orchestrator.py`, `services/retrieval/planner.py`, `services/retrieval/retrievers.py`, `services/rewrite/__init__.py`, `services/rewrite/markdown_rewrite.py`, `services/rewrite/query_write.py`, `services/storage/__init__.py`, `services/storage/minio.py`, `services/storage/oss.py`, `services/workspace/__init__.py`, `services/workspace/attachment_service.py`, `tools/__init__.py`, `tools/image2text/__init__.py`, `tools/image2text/action.py`, `tools/text2image/__init__.py`, `tools/text2image/action.py`, `utils/convert.py`, `utils/helpers.py`, `utils/model_output.py`), plus thin package contracts (`api/JWT.py`, `api/errcode/`, `utils/contexts.py`). `infra/db` now also enters through `services/api/src`, `zuno.database.metadata`, and the migrated `services/api/src/zuno/database/{init_data.py,session.py,metadata.py,models/__init__.py,dao/__init__.py}` plus `services/api/src/zuno/database/{models/*.py,dao/*.py}`, while the broader backend implementation still resolves from `src/backend` through temporary bridges.

Current evidence in the repo:

- `README.md` now tells local backend development to run from `services/api`
- `services/api/src/zuno/main.py` now exists as the canonical backend app entry file for Phase 2 startup
- `services/api/src/zuno/api/router.py` now exists as the canonical Phase 2 API router entry file
- `services/api/src/zuno/api/v1/__init__.py` now exists as the canonical Phase 2 API package entry file
- `services/api/src/zuno/api/v1/agent.py`, `agent_skill.py`, `capability.py`, `completion.py`, `config.py`, `dialog.py`, `history.py`, `knowledge.py`, `knowledge_file.py`, `llm.py`, `mcp_agent.py`, `mcp_chat.py`, `mcp_server.py`, `mcp_stdio_server.py`, `mcp_user_config.py`, `message.py`, `tool.py`, `upload.py`, `usage_stats.py`, `user.py`, `wechat.py`, and `workspace.py` now exist as migrated thin route controllers
- `services/api/src/zuno/api/services/__init__.py`, `agent.py`, `agent_skill.py`, `capability.py`, `completion.py`, `dialog.py`, `history.py`, `knowledge.py`, `knowledge_file.py`, `llm.py`, `mcp_agent.py`, `mcp_chat.py`, `mcp_server.py`, `mcp_stdio_server.py`, `mcp_user_config.py`, `message.py`, `mineru.py`, `tool.py`, `upload.py`, `usage_stats.py`, `user.py`, `wechat.py`, `workspace.py`, and `workspace_session.py` now exist as migrated service-layer modules
- `services/api/src/zuno/prompts/__init__.py`, `completion.py`, `mcp.py`, `skill.py`, `services/__init__.py`, `services/execution_policy.py`, `services/pipeline/__init__.py`, `services/pipeline/manager.py`, `services/pipeline/models.py`, `services/pipeline/stages.py`, `services/queue/__init__.py`, `services/queue/client.py`, `services/queue/messages.py`, `services/queue/runner.py`, `services/queue/workers.py`, `services/rag/__init__.py`, `services/rag/embedding.py`, `services/rag/es_client.py`, `services/rag/handler.py`, `services/rag/parser.py`, `services/rag/retrieval.py`, `services/rag/rerank.py`, `services/rag/vl_embedding.py`, `services/rag/vector_db/__init__.py`, `services/rag/vector_db/chroma_client.py`, `services/rag/vector_db/milvus_client.py`, `services/rag/vector_db/milvus_lite_client.py`, `services/rag/doc_parser/__init__.py`, `services/rag/doc_parser/chunk_ids.py`, `services/rag/doc_parser/docx.py`, `services/rag/doc_parser/excel.py`, `services/rag/doc_parser/image.py`, `services/rag/doc_parser/markdown.py`, `services/rag/doc_parser/other_file.py`, `services/rag/doc_parser/pdf.py`, `services/rag/doc_parser/pptx.py`, `services/rag/doc_parser/text.py`, `services/redis.py`, `services/retrieval/__init__.py`, `services/retrieval/fusion.py`, `services/retrieval/models.py`, `services/retrieval/orchestrator.py`, `services/retrieval/planner.py`, `services/retrieval/retrievers.py`, `services/rewrite/__init__.py`, `services/rewrite/markdown_rewrite.py`, `services/rewrite/query_write.py`, `services/storage/__init__.py`, `services/storage/minio.py`, `services/storage/oss.py`, `services/workspace/__init__.py`, `services/workspace/attachment_service.py`, `tools/__init__.py`, `tools/image2text/__init__.py`, `tools/image2text/action.py`, `tools/text2image/__init__.py`, `tools/text2image/action.py`, `utils/convert.py`, `utils/helpers.py`, and `utils/model_output.py` now exist as migrated runtime support modules
- the duplicated legacy `src/backend/zuno/api/` package root (`__init__.py`, `router.py`, `JWT.py`, `errcode/`), `src/backend/zuno/api/services/`, and `src/backend/zuno/api/v1/` packages have now been removed, while `zuno.api.*`, `zuno.api.services.*`, and `zuno.api.v1.*` resolve only from `services/api/src/zuno/api/`
- the duplicated legacy `src/backend/zuno/middleware/` package has now been removed, while `zuno.middleware.*` resolves only from `services/api/src/zuno/middleware/`
- the duplicated legacy `src/backend/zuno/services/queue/`, `src/backend/zuno/services/retrieval/`, and `src/backend/zuno/services/rewrite/` packages have now been removed, while `zuno.services.queue.*`, `zuno.services.retrieval.*`, and `zuno.services.rewrite.*` resolve only from `services/api/src/zuno/services/`
- the duplicated legacy `src/backend/zuno/services/pipeline/{__init__.py,manager.py,models.py,stages.py}` files have now been removed, while `zuno.services.pipeline.*` resolves only from `services/api/src/zuno/services/pipeline/`
- `services/api/src/zuno/database/{__init__.py,init_data.py,session.py,metadata.py}` now provides the current `zuno.database` package entry plus startup/session/metadata flow, `services/api/src/zuno/database/models/{__init__.py,*.py}` now provides the current full models layer, and `services/api/src/zuno/database/dao/{__init__.py,*.py}` now provides the current full dao layer
- temporary bridges in `src/backend/zuno/__init__.py`, `src/backend/zuno/services/__init__.py`, and `src/backend/agentchat/__init__.py` now extend package lookup into `services/api/src` so legacy-first import order cannot hide migrated `zuno.api.*`, `zuno.database.*`, `zuno.middleware.*`, `zuno.services.*`, or `agentchat.database.*` modules during Phase 2
- `services/api/src/agentchat/database/{__init__.py,models/__init__.py,dao/__init__.py,session.py,metadata.py,init_data.py}` now exists as a temporary compatibility layer that forwards `agentchat.database*` imports to `zuno.database*` without restoring duplicated database model code under `src/backend`
- `domain-packs/contract_review/` now holds the active Domain Pack assets, and both `zuno.services.domain_pack.loader` and `agentchat.services.domain_pack.loader` now resolve packs from the top-level `domain-packs/` surface instead of `src/backend/zuno/domain_packs/`
- `services/api/src/zuno/config/` and `services/api/src/zuno/config.example.yaml` now hold the active `zuno` config assets, while both `zuno.database.init_data` and `agentchat.database.init_data` now resolve config resources through package-root-aware paths instead of depending on the old `src/backend/zuno/config/` location
- `services/api/src/zuno/schema/` now holds the active `zuno` schema package, so FastAPI route schemas, runtime request models, and retrieval data contracts no longer depend on `src/backend/zuno/schema/`
- `services/api/src/zuno/mcp_servers/` now holds the active `zuno` MCP remote proxy package, so system MCP server config now targets the service-rooted proxy entrypoint instead of depending on `src/backend/zuno/mcp_servers/`
- `services/api/src/zuno/core/` now holds the active `zuno` core runtime package, so runtime graphs, agent facades, model manager, and `AgentRuntime` no longer depend on `src/backend/zuno/core/`
- `services/api/src/zuno/main.py`, `settings.py`, `config.yaml`, `fixtures/`, `prompts/`, `tools/`, and `utils/` now hold the active startup entry, runtime sample assets, prompt contracts, tool adapters, and utility contracts, so the duplicated root-side `src/backend/zuno/{main.py,settings.py,config.yaml,prompts/,tools/,utils/,fixtures/}` surfaces no longer shadow the service-rooted package tree
- `infra/db/alembic.ini` now prepends `services/api/src`, and `infra/db/alembic/env.py` now reads metadata from `zuno.database.metadata`
- `services/api/src/zuno/settings.py` and `services/api/src/zuno/middleware/` have been physically migrated into the service package root
- `services/api/src/zuno/api/JWT.py`, `services/api/src/zuno/api/errcode/`, and `services/api/src/zuno/utils/contexts.py` have also been physically migrated as thin contract modules
- `infra/docker/Dockerfile` now copies `services/api/` into `/app/` and keeps `src/backend/` at `/app/legacy_backend/` as an explicit migration bridge
- `tools/scripts/start.py` now sets `BACKEND_DIR = PROJECT_ROOT / "services" / "api"`
- `tools/launchers/windows/` now resolve the repo root correctly and no longer depend on ghost frontend paths
- Docker dev/runtime mounts are being updated to keep `/app` rooted at `services/api` while still exposing legacy source under `/app/legacy_backend`
- `tests/test_zuno_public_entrypoints.py` now verifies `services/api/src/zuno/main.py` as the current app entry file
- `tests/test_zuno_runtime_chain_guard.py` now guards a mixed runtime chain where migrated entrypoints and migrated storage already resolve from `services/api/src/zuno/...`, while remaining legacy runtime responsibilities still sit under `src/backend/zuno/...`

This means Phase 2 is not a naming cleanup.
It is the point where the real backend service root moves.

## Real Migration Surface

When this phase starts implementation, the minimum migration surface must include:

1. backend source root
   - move runnable backend code from `src/backend` toward `services/api`
   - keep package naming stable under `zuno`
2. local startup paths
   - update `README.md`
   - update `tools/scripts/start.py`
   - update any launcher helpers that assume `src/backend`
3. container build and runtime paths
   - update `infra/docker/Dockerfile`
   - update compose-mounted backend paths if they still point at `src/backend`
4. verification and regression surfaces
   - update tests that assert `src/backend/zuno/...` as the runtime root
   - update repo verifiers and any path-sensitive smoke scripts
5. documentation truth
   - sync `current-architecture.md`
   - sync `README.md`
   - sync development and launcher docs that describe backend startup

## Minimum Checks For This Phase

Before Phase 2 can close, the repo should prove all of these:

- backend startup works from `services/api`
- Docker image build no longer copies runtime code from `src/backend`
- launcher and local start scripts agree on the new backend root
- path-sensitive tests are updated to the new runtime root
- docs describe `services/api` as the current backend startup root and migration target, not as an empty placeholder

## Closure Gate

- `services/api` is the real backend service root
- package naming remains stable under `zuno`
- startup, tests, scripts, and docs agree on the new path
- compatibility surfaces are reduced instead of expanded
