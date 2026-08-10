# PHASE01 Frontend and Desktop Current Inventory

phase_id: PHASE01
task_id: P01-T04
start_commit: c01420e915db19a3b0d6f979ca4450c8d5de0c85
prompt_start_commit: c01420e915db19a3b0d6f979ca4450c8d5de0c85
branch: codex/P01-T04-frontend-desktop-inventory
owner_module: "01 Product Surface, Web/Desktop clients as consumers"
status: completion_candidate
status_boundary: "页面、组件、DTO、静态测试或 Electron 壳存在，只能证明 surface exists；不能证明 generated contract、AuthorizedView、AvailableAction、Browser E2E、Desktop Smoke、断线恢复、撤权、多 Interrupt 或 UNKNOWN 恢复语义已经 Current。"

## 1. Current

### 1.1 Web API Client / DTO / Store

| item | page/component exists | contract adopted | generated or machine-checked type | authorized projection | available action | real E2E/smoke evidence | current proof | gap/blocker | target phase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| HTTP request wrapper | yes | partial legacy API wrapper | no generated Product Contract | no | no | no | `apps/web/src/utils/request.ts` creates an Axios instance, adds `apiUrl`, reads Bearer token from `localStorage`, clears token on 401 and dispatches `zuno-auth-invalid`. | Authorization is client token handling only; no Product AuthorizedView proof. | PHASE10 |
| Workspace API module | yes | partial legacy workspace product loop DTOs | TypeScript hand-written unions/interfaces only | no | partial status/recovery arrays | static tests only | `apps/web/src/apis/workspace.ts` defines workspace task, lifecycle, approval, artifact, trace/eval and feedback calls. `tests/frontend/test_workspace_product_loop_types.py` checks these symbols. | Not generated from frozen shared Product Surface contract; unknown enums are not machine-checked fail-closed. | PHASE10 |
| Pinia user/card stores | yes | no Product Run/Approval fact contract | local app state only | no | no | no | `apps/web/src/store/user/index.ts`, `apps/web/src/store/agent_card/index.ts` persist user/card state. | Frontend remains non-authoritative; no Run, Approval, Artifact, Trace, Eval or Memory fact store should be treated as Current. | PHASE10 |
| Legacy response and status DTOs | yes | legacy-compatible only | hand-written TypeScript | no | partial string actions | static tests only | `UnifiedResponse` appears in API modules; `WorkspaceTaskStatus` and `WorkspaceTaskLifecycleState` are string unions in `workspace.ts`. | UI still infers behavior from status strings such as `completed`, `failed`, `recoverable_failed`, `approval_required`. | PHASE10 |

### 1.2 Web Page / SSE / Approval / Citation / Artifact / Trace

| item | page/component exists | contract adopted | generated or machine-checked type | authorized projection | available action | real E2E/smoke evidence | current proof | gap/blocker | target phase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Workspace route | yes | legacy route redirect compatibility | no | no | no | no browser E2E | `apps/web/src/router/index.ts` routes `/workspace` and redirects older `/conversation`, `/agent`, `/knowledge`, `/tool`, `/model`, `/dashboard` surfaces into workspace/settings surfaces. | Route existence is not Product Contract parity. | PHASE02, PHASE10 |
| Workspace runtime page | yes | partial workspace runtime loop | Vue type checking only when lint can run | no | partial local decisions | static source tests only | `apps/web/src/pages/workspace/defaultPage/defaultPage.vue` includes task creation, streaming, lifecycle, artifact, approval, feedback and observability UI surfaces. | No browser-driven proof for normal, failure, reconnect, revoke, UNKNOWN or multi Interrupt paths. | PHASE10, PHASE21 |
| SSE simple chat stream | yes | legacy `/api/v1/workspace/simple/chat` | no cursor type | no | no | no Browser E2E | `workspaceSimpleChatStreamAPI` uses `@microsoft/fetch-event-source` POST and normalizes `event`, `task_id`, `trace_id`, `artifact_id`, `citation_ids`, approval fields. | No `Last-Event-ID`, opaque cursor, resume, resync, cursor expiry, duplicate-delta idempotency or reauthorization evidence. | PHASE10, PHASE21 |
| SSE task event stream | yes | legacy `/api/v1/workspace/task/{taskId}/events/stream` | no cursor type | no | no | no Browser E2E | `workspaceTaskEventsStreamAPI` uses `fetchEventSource` GET and event normalizer. | Same SSE resume and reauthorization gaps; close/error only aborts local controller. | PHASE10, PHASE21 |
| Approval UI | yes | partial task approval endpoint | hand-written `WorkspaceApprovalRequest` | no | no server-provided AvailableAction object | no multi Interrupt E2E | `pendingToolApproval`, `capturePendingToolApproval`, `submitToolApproval`, `tool-approval-card`, `approveWorkspaceTaskAPI` exist. | UI compresses approval to one `pendingToolApproval`; no multiple pending Interrupt list, scoped action token, stale approval, epoch change or replay proof. | PHASE10, PHASE21 |
| Citation UI | yes | partial citation ID display | hand-written `WorkspaceCitationRef` | not proven | no | no content authorization E2E | Citation IDs are merged into `activeRuntimeCitationIds` and displayed as chips. | Citation metadata/content authorization, source span access denial and revocation are not proven. | PHASE10, PHASE21 |
| Artifact UI and download | yes | partial artifact endpoint | hand-written `ArtifactContract` | not proven | local download button, not AvailableAction | no download authorization E2E | `getWorkspaceArtifactAPI`, `downloadWorkspaceArtifactAPI`, `runtime-artifact-panel`, `runtime-download-button` exist. | Download session authorization, expiry, revocation and MIME/sandbox behavior are not proven. | PHASE10, PHASE21 |
| Trace / Eval display | yes | projection display only | `WorkspaceObservabilitySnapshot` hand-written | not proven | no | no quality E2E | `runtime-observability-panel`, `release-eval`, trace source refs and span count display exist. | Display does not prove Observability/Eval facts, release quality or fixed benchmark. | PHASE21 |
| UNKNOWN effect UI | partial failure panel | no canonical UNKNOWN recovery contract | no | no | no Owner-provided recovery action object | no | `runtimeFailure` and `recovery_actions` appear in page/API surfaces. | No dedicated `TOOL_EFFECT_UNKNOWN` / reconcile / human review / compensate UI proof; no blind-retry guard proof. | PHASE10, PHASE21 |

### 1.3 Desktop Shell / Bridge / Smoke

| item | page/component exists | contract adopted | generated or machine-checked type | authorized projection | available action | real E2E/smoke evidence | current proof | gap/blocker | target phase |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Desktop preload | yes | partial desktop runtime config | no generated Desktop Contract | no | no | no smoke found | `apps/desktop/preload.cjs` exposes `window.__ZUNO_DESKTOP__`, API base URL, bridge URL/token, workspace root, task lifecycle endpoint and artifact download template. | Renderer config is not a typed Product Desktop contract and not authorization proof. | PHASE10 |
| Desktop main window | yes | Electron shell only | no | no | no | no smoke found | `apps/desktop/main.cjs` creates BrowserWindow, loads dev URL or file target, starts desktop bridge. | No packaged/open-window smoke, backend connectivity, revocation or Desktop/Web contract parity proof. | PHASE10, PHASE21 |
| Desktop bridge | yes | local bridge protocol | no generated IPC contract | no | bridge actions are local action strings | no smoke found | `apps/desktop/bridge.cjs` gates `/execute` with `X-Zuno-Desktop-Token`, supports list/read/write/search/run_command, workspace/unrestricted scopes. | Security model, action token binding, audit, approval, budget and idempotency are not Product Current; unrestricted command mode is a PHASE05/PHASE10 risk. | PHASE05, PHASE10 |
| Desktop package scripts | yes | no | no | no | no | not run; dependencies absent | `apps/desktop/package.json` defines `start` and `dev`. | Electron dependencies are not installed in this worktree; no smoke run. | PHASE21 |

## 2. Build and Test Inventory

| command/surface | current availability | result boundary | gap/blocker | target phase |
| --- | --- | --- | --- | --- |
| `apps/web` package scripts | `dev`, `build`, `preview`, `lint` exist in `apps/web/package.json`. | Package command existence only. | `node_modules`, `apps/web/node_modules` absent in current worktree; lint/build cannot run without install. | PHASE10 |
| `apps/desktop` package scripts | `start`, `dev` exist in `apps/desktop/package.json`. | Package command existence only. | `apps/desktop/node_modules` absent; Electron smoke cannot run without install. | PHASE21 |
| Static frontend tests | `tests/frontend/test_workspace_product_loop_types.py`, `tests/frontend/test_frontend_workspace_features.py`, `tests/frontend/test_product_wiring_v1_api_contract.py`. | Static source assertions prove symbols and strings exist. | They are not Browser E2E, SSE gap/resume, revocation, UNKNOWN or Desktop smoke. | PHASE10, PHASE21 |
| Backend/API scenario tests | `tests/api/test_workspace_task_runtime.py`, `tests/e2e/test_unified_agent_product_scenario.py`. | TestClient/service scenario coverage only. | Not browser-driven Web/Desktop evidence. | PHASE21 |
| Browser E2E | no Playwright/Cypress/Selenium config found by `rg --files`. | unavailable | Missing Browser E2E harness for normal, reconnect, revoked stream, multiple Interrupt and UNKNOWN. | PHASE21 |
| Desktop Smoke | no Electron smoke test found. | unavailable | Missing Desktop smoke for preload config, bridge token, task lifecycle, artifact download and restricted/unrestricted bridge behavior. | PHASE21 |

## 3. Gap Ledger

| gap_id | gap | blocker / reason | target phase | handoff risk |
| --- | --- | --- | --- | --- |
| P01-T04-G01 | Web/Desktop do not consume generated Product Surface Contract. | Current DTOs are hand-written TypeScript and legacy-compatible response/status shapes. | PHASE10 | Client/server enum drift and unknown value handling remain manual. |
| P01-T04-G02 | Authorized Projection is not Current. | UI consumes API payloads and local state; no evidence of per-query AuthorizedView generation, epoch reauthorization or redaction. | PHASE10 | Revoked or stale views can be misrepresented if backend contracts are not upgraded. |
| P01-T04-G03 | AvailableAction is not Current. | Approval/download/recovery buttons are local UI decisions or endpoint availability, not server-scoped action tokens. | PHASE10 | UI may expose stale approve/download/retry controls. |
| P01-T04-G04 | SSE resume/resync/cursor expiry/reauthorization are missing. | `fetchEventSource` usage has no `Last-Event-ID`, cursor parameter or resync path. | PHASE10, PHASE21 | Disconnect may be confused with progress or terminal state. |
| P01-T04-G05 | Multiple Interrupt UI is missing. | Current UI stores one `pendingToolApproval`. | PHASE10 | Concurrent pending interrupts can be hidden or overwritten. |
| P01-T04-G06 | UNKNOWN effect recovery UI is not proven. | No dedicated reconcile/human-review/compensate AvailableAction rendering. | PHASE10, PHASE21 | Blind retry prevention cannot be proven in UI. |
| P01-T04-G07 | Citation and Artifact authorization is not proven. | Citation chips and download button exist, but independent content/download authorization, expiry and revocation are not tested. | PHASE10, PHASE21 | Sensitive content may be over-displayed without Product authorization proof. |
| P01-T04-G08 | Browser E2E and Desktop Smoke are missing. | No browser automation or Electron smoke harness found; JS dependencies absent in this worktree. | PHASE21 | PHASE21 must not inherit static tests as E2E evidence. |

## 4. Plan

This P01-T04 work package intentionally does not change frontend or desktop behavior.

1. Expand: replace the partial frontend inventory with a Required Contract matrix that distinguishes surface existence, contract adoption, generated/machine-checked type, Authorized Projection, AvailableAction, real E2E/smoke evidence, gap/blocker and target phase.
2. Verify: add/update repository verifier and tests so P01-T04 inventory/evidence completeness is machine-checked without opening PHASE01 closure gates.
3. Evidence: add `docs/evidence/phase01-frontend-desktop-inventory.md` with commit, environment, package command availability, run results, blocked Browser/Desktop evidence and artifact hash.
4. Contract: keep `phase-readiness.yaml` at `completion_candidate` for P01-T04 only; PHASE01 remains blocked until Coordinator closure and other work packages complete.
5. Rollback: revert this branch commit; no runtime code, frontend behavior, backend API, dependency or migration changes are introduced.

## 5. Current / Gap Summary

Current:
- Web workspace route, page, API module, hand-written DTOs, Pinia local stores, SSE clients, single pending approval card, citation chips, artifact panel/download button and Trace/Eval projection display exist.
- Desktop Electron shell, preload runtime config and token-gated local bridge exist.
- Static frontend source tests exist for several workspace product-loop symbols.

Gap:
- Contract adopted is partial and legacy-compatible, not generated Product Surface Contract.
- Authorized Projection and AvailableAction are not Current.
- Browser E2E, Desktop Smoke, SSE resume/resync/reauthorization, multiple Interrupt UI, UNKNOWN recovery UI and citation/artifact revocation are missing.
