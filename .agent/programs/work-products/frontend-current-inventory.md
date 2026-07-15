# PHASE01 Frontend and Desktop Current Inventory

phase_id: PHASE01
task_id: P01-T04
start_commit: 9d10f71cc10ea1880a4a738f4500982d6684ede7
status_boundary: "页面存在、类型存在和静态源码测试不等于真实浏览器/桌面 E2E、断线恢复、撤权或多 Interrupt 证明。"

## 1. Web API and State

| surface | path | symbol | current | gap |
| --- | --- | --- | --- | --- |
| HTTP client | `apps/web/src/utils/request.ts` | `axios` instance | adds `apiUrl`, Bearer token from `localStorage`, clears token on 401 and dispatches `zuno-auth-invalid` | not Product Contract authorization proof |
| Workspace API | `apps/web/src/apis/workspace.ts` | workspace API functions and DTOs | central client for task, lifecycle, approval, artifact, observability and feedback endpoints | still not generated from frozen shared contracts |
| Pinia stores | `apps/web/src/store/user/index.ts`, `apps/web/src/store/agent_card/index.ts` | user / agent card stores | local persisted user and card state | no Run/Approval/Artifact/Trace/Eval fact store |
| Legacy DTO envelope | `apps/web/src/apis/knowledge.ts`, `apps/web/src/apis/workspace.ts` | `UnifiedResponse`, `WorkSpaceSimpleTask` | current frontend still consumes legacy-shaped response/status types | PHASE10 must move to Product Contract |

## 2. Streaming, Approval, Citation, Artifact and Eval UI

| surface | path | symbol | current | gap |
| --- | --- | --- | --- | --- |
| SSE | `apps/web/src/apis/workspace.ts` | `streamWorkspaceChat`, task event stream | uses `@microsoft/fetch-event-source` for `/api/v1/workspace/simple/chat` and `/api/v1/workspace/task/{taskId}/events/stream` | no `Last-Event-ID`, opaque cursor, resume/resync, cursor expiry or disconnect reauthorization evidence found |
| Approval UI | `apps/web/src/pages/workspace/defaultPage/defaultPage.vue` | `pendingToolApproval`, approve/reject handlers | tool approval card and approve/reject calls exist | compressed to one pending approval; no multi Interrupt UI evidence |
| Citation / artifact | `apps/web/src/apis/workspace.ts`, `defaultPage.vue` | `WorkspaceCitationRef`, `ArtifactContract`, `runtime-artifact-panel`, citation chips | citation and artifact panels/download exist | artifact/citation independent authorization and revocation not proven |
| Trace / eval projection | `defaultPage.vue` | `runtime-observability-panel`, `release-eval` | observability and release eval panel exist | projection display only; not quality proof |
| Status string inference | `workspace.ts`, `defaultPage.vue` | `WorkspaceTaskStatus`, `WorkspaceTaskLifecycleState`, string comparisons | typed unions exist, UI still checks strings such as `completed`, `failed`, `recoverable_failed` | needs generated Product enum/action contract |

## 3. Routing and Desktop

| surface | path | symbol | current | gap |
| --- | --- | --- | --- | --- |
| Web routes | `apps/web/src/router/index.ts` | `/workspace`, redirects | primary product route is `/workspace`; older routes redirect into workspace/settings surfaces | old surface compatibility still needs PHASE02/PHASE10 matrix |
| Desktop preload | `apps/desktop/preload.cjs` | `window.__ZUNO_DESKTOP__` | exposes API base, bridge URL/token, task lifecycle and artifact endpoint | not a generated Product Desktop contract |
| Desktop main | `apps/desktop/main.cjs` | bridge startup | starts local desktop bridge | desktop smoke/E2E not found |
| Desktop bridge | `apps/desktop/bridge.cjs` | `X-Zuno-Desktop-Token`, list/read/write/search/run_command | token-gated local bridge with workspace scope and unrestricted command mode | security model needs PHASE05/PHASE10 proof |

## 4. Build and Tests

- `apps/web/package.json` defines `dev`, `build`, `preview`, and `lint`; lint runs `vue-tsc --noEmit`.
- `apps/desktop/package.json` defines Electron `start` and `dev`.
- `tests/frontend/*` are primarily static source assertions.
- `tests/api/test_workspace_task_runtime.py` and `tests/e2e/test_unified_agent_product_scenario.py` exercise backend/TestClient or service scenarios.
- No Playwright/Cypress/Selenium/browser Electron E2E was found for SSE gap/resume, revocation, UNKNOWN UI or desktop closed loop.

## 5. Current / Gap

Current:
- Workspace UI, task lifecycle, approval card, artifact panel, citation chips and observability/eval projection are present.
- Web client uses central request wrapper and workspace API module.
- Desktop bridge exists with token-gated local operations.

Gap:
- Web/Desktop are not yet solely consuming generated Product Contract, Projection and AvailableAction.
- Real browser/desktop E2E is missing.
- SSE resume, reauthorization, cursor expiry, multi approval and UNKNOWN effect UI are not proven.
