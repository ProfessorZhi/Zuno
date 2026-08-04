# PHASE22 Web Findings

Branch: `claude/minimax-phase22-nonbackend-legacy-cleanup`
Scope: `apps/web/**`, `tests/frontend/**`

## Files inspected

- `apps/web/src/apis/knowledge.ts`
- `apps/web/src/apis/workspace.ts`
- `apps/web/src/router/index.ts`
- `apps/web/src/utils/retrieval.ts`
- `apps/web/src/utils/knowledge-config.ts`
- `apps/web/src/utils/user-avatars.ts`
- `apps/web/src/utils/display-text.ts`
- `apps/web/src/product/runtime.ts`
- `apps/web/src/pages/index.vue`
- `apps/web/src/pages/workspace/defaultPage/defaultPage.vue`
- `apps/web/src/pages/workspace/defaultPage/defaultPage.constants.ts`
- `apps/web/src/pages/dashboard/dashboard.vue`
- `apps/web/src/pages/profile/profile.vue`
- `apps/web/src/pages/workspace/workspace.vue`
- `apps/web/src/pages/agent/agent-editor.vue`
- `apps/web/src/pages/agent/index.ts`
- `apps/web/src/pages/agent-skill/index.ts`
- `apps/web/src/pages/configuration/configuration.vue`
- `apps/web/src/pages/dashboard/index.ts`
- `apps/web/src/pages/knowledge/{index.ts,knowledge-create.vue,knowledge-config.vue,knowledge-file.vue,knowledge-settings.vue}`
- `apps/web/src/pages/mcp-server/index.ts`
- `apps/web/src/pages/model/index.ts`
- `apps/web/src/pages/profile/index.ts`
- `apps/web/src/pages/tool/{index.ts,tool.vue}`
- `apps/web/src/style.css`
- `apps/web/package-lock.json`

## Classification table

| Hit                                            | Symbol / Context                                  | Classification               |
| ---------------------------------------------- | ------------------------------------------------- | ---------------------------- |
| `router/index.ts`                              | `/:homepage, /:configuration, /:agent, /:agent/editor, /:mcp-server, /:knowledge*, /:tool, /:agent-skill, /:model, /:model/editor, /:profile, /:dashboard, /:conversation*` legacy redirects | ALLOWED_HISTORY_REFERENCE (intentional back-compat routes redirect to `workspaceSettings*`) |
| `pages/agent/index.ts`, `agent-skill/index.ts`, `configuration/configuration.vue`, `dashboard/index.ts`, `knowledge/{index.ts,knowledge-create.vue,knowledge-config.vue,knowledge-file.vue,knowledge-settings.vue}`, `mcp-server/index.ts`, `model/index.ts`, `profile/index.ts`, `tool/{index.ts,tool.vue}` | Standalone page exports re-used as embedded components by `pages/workspace/components/WorkspaceSettingsShell.vue` and `pages/workspace/defaultPage/defaultPage.vue` | ALLOWED_HISTORY_REFERENCE (re-export layer feeding the consolidated workspace shell) |
| `utils/retrieval.ts`                           | `legacyModeMap` (auto / default / hybrid / graphrag → rag / rag_graph) | ALLOWED_HISTORY_REFERENCE (temporary allowlist entry, deadline PHASE10, owner 01 Product Surface, test `tests/frontend/test_product_wiring_v1_api_contract.py`; payload compatibility for legacy client-generated settings) |
| `utils/knowledge-config.ts`                    | `LegacyKnowledgeProductMode` (incl. `enhanced`), `LegacyKnowledgeConfigInput` (incl. `domain_pack_id`), `legacyMap` | ALLOWED_HISTORY_REFERENCE (temporary allowlist entry, deadline PHASE10, owner 01 Product Surface, same test) |
| `utils/user-avatars.ts`                        | `isLegacyRemoteUserAvatar` matching `zuno.oss-cn-beijing.aliyuncs.com`, `/zuno/icons/user/`, `/icons/user/` prefixes | ALLOWED_HISTORY_REFERENCE (temporary allowlist entry, deadline PHASE10, owner 01 Product Surface, test `tests/repo/test_history_overview_and_branding.py`; old OSS-hosted avatars vs. `/avatars/user/zuno-user-NN.png`) |
| `utils/display-text.ts`                        | Local JS parameter `fallback` for `truncateDisplayText` | not legacy (parameter name; no config / no runtime reader) |
| `apis/knowledge.ts`                            | `fallback_triggered`, `fallback_reason`, `query_method_fallback_reason`, retrieval `fallback_reason` | not legacy (current contract; backend `KnowledgeQuery` DTO shape) |
| `apis/workspace.ts`                            | `fallback_reason` on workspace payload | not legacy (current contract) |
| `pages/index.vue`, `pages/profile/profile.vue`, `pages/workspace/workspace.vue`, `pages/workspace/defaultPage/defaultPage.vue` | `isLegacyRemoteUserAvatar` import + branch to DEFAULT_USER_AVATAR | covered by `utils/user-avatars.ts` ALLOWED_HISTORY_REFERENCE |
| `pages/workspace/defaultPage/defaultPage.constants.ts`, `defaultPage.vue`, `pages/dashboard/dashboard.vue` | `fallbackDescription`, `fallbackKnowledgeDescription`, `fallbackBenchmarkMetrics`, `buildFallbackAssistantMessage`, `fallbackRouteName`, `fallbackArtifactId`, `safeQueryValue(value, fallback)` | not legacy (local UI sentinel values; downstream display fallback when upstream returns empty) |
| `pages/tool/tool.vue`                          | `target.dataset.fallbackApplied`, `getErrorMessage(error, fallback)` | not legacy (DOM marker for "tried once" state; error.message selection) |
| `product/runtime.ts`                           | `ProductRuntimeCutoverMode` (`shadow` / `canary` / `new_default` / `rollback`), `ProductRuntimeRollbackError`, `VITE_PRODUCT_RUNTIME_CUTOVER_MODE`, `localStorage.getItem(PRODUCT_RUNTIME_CUTOVER_STORAGE_KEY)`, `SHADOW_SUBMIT_USER_GOAL` / `CANARY_SUBMIT_USER_GOAL` command kinds | ALLOWED_FAIL_CLOSED_TEST (active Product Runtime cutover-mode machine; rollback mode throws fail-closed; allowed by `test_phase22_cleanup_boundary_allowlist.py`, `test_launcher_scripts.py::test_full_e2e_smoke_covers_product_runtime_cutover_modes`) |
| `style.css`                                    | CSS comment `flatten remaining legacy cards, pills and framed controls` | not legacy (UI cleanup comment; refactor narrative) |
| `package-lock.json`                            | `@codemirror/legacy-modes` transitive dependency | not legacy (CodeMirror published package; only the substring `legacy` in the vendor name) |

## Old API endpoints (router / API surface)

Searched `apps/web/src/apis/` for any reference to retired routes such as
`/api/v1/dialog`, `/api/v1/completion`, `/api/v1/agent/legacy`, `/api/v1/chat/legacy`,
`/api/v1/llm/legacy`, `/api/v1/message_events/legacy`:

- No such references found.
- `apis/chat.ts`, `apis/configuration.ts`, `apis/file.ts`, `apis/knowledge.ts`, `apis/knowledge-file.ts`, `apis/agent-skill.ts`, `apis/auth.ts`, `apis/llm.ts`, `apis/mcp-server.ts`, `apis/tool.ts`, `apis/usage-stats.ts`, `apis/workspace.ts` all target `/api/v1/...` canonical paths that match the active backend contract for the given feature surface.

## Old SSE events (workspace SSE)

`apps/web/src/product/{client,runtime,store,contracts}.ts` and `apps/web/src/apis/knowledge.ts` were inspected for legacy SSE event names (`event: "agent.legacy"`, `event: "dialog_chunk_v0"`, `event: "completion_legacy_chunk"`). None found — only the canonical `ProductStreamEvent` types listed in `apps/web/src/product/contracts.ts` are in use.

## Old desktop bridge channels

`apps/desktop/main.cjs` smoke check declares the canonical capability set:

```
runtimeRequest, actionConsume, projectionStream, streamLastEventId, streamDedup,
streamReauthorization, artifactRead, artifactDownload, feedback
```

No legacy (`streamReauthorizeV0`, `chunkStreamV0`, etc.) channels are exposed.
`productBridgeVersion` reads `product-desktop-bridge-v1.phase10` which is current.

## Old frontend action names

`/pages/workspace/defaultPage/defaultPage.vue` and product runtime use the
`AvailableAction.action_token_id` action surface — no legacy action enum
literal (e.g. `RUN_LEGACY_AGENT`, `LEGACY_STREAM_CHUNK`) was found.

## Outcome

No 1:1 web replacement was appropriate: every front-end legacy touchpoint is
either a permanent compat shim (with deadline passed but owner protected),
an allowed back-compat URL alias, or a fail-closed mode of the live cutover
state machine. Worker therefore records the audit and does not edit these
files. The verifier + test in this PR reinforce the invariants so that a
future worker cannot regress them by hand.
