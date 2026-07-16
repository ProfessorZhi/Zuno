# PHASE01 Frontend / Desktop Inventory Evidence

phase_id: PHASE01
task_id: P01-T04
branch: codex/P01-T04-frontend-desktop-inventory
start_commit: 688a50fa5730f8815b2f09050f01eeb42633ae1d
prompt_start_commit: c01420e915db19a3b0d6f979ca4450c8d5de0c85
evidence_status: completion_candidate

## Environment

- OS / shell: Windows PowerShell in Codex desktop worktree.
- Current worktree: `C:\Users\Administrator\.codex\worktrees\0ea6\Zuno`
- Node dependencies: `node_modules`, `apps/web/node_modules` and `apps/desktop/node_modules` were absent at inventory time.
- Network/dependency install: not performed; P01-T04 does not authorize dependency changes.
- Runtime behavior changes: none.

## Artifact Hash

- artifact: `.agent/programs/work-products/frontend-current-inventory.md`
- artifact hash: `sha256:119c86d7439bdd533e9ebf91fcfdab0ca90dac0bcbd0fa34a5d59d3ffd50b967`

## Inventory Commands and Results

| command | result |
| --- | --- |
| `git rev-parse HEAD` | `688a50fa5730f8815b2f09050f01eeb42633ae1d` |
| `git status --short --branch` | clean on `codex/P01-T04-frontend-desktop-inventory` before edits |
| `rg --files apps/web apps/desktop tests` | found Web package, Desktop package, workspace API/page/router/store files, static frontend tests and backend/TestClient scenarios |
| `rg -n "fetch-event-source\|Last-Event-ID\|cursor\|resume\|pendingToolApproval\|approval\|Artifact\|citation\|runtime-observability\|release-eval\|AvailableAction\|UNKNOWN" apps/web/src apps/desktop tests -S` | found SSE, single pending approval, artifact, citation and Trace/Eval UI surfaces; did not find Product `AvailableAction`, cursor resume or Browser/Desktop E2E proof |
| `Get-Content apps/web/package.json` | `dev`, `build`, `preview`, `lint` scripts exist |
| `Get-Content apps/desktop/package.json` | `start`, `dev` scripts exist |
| `Test-Path node_modules; Test-Path apps/web/node_modules; Test-Path apps/desktop/node_modules` | all returned `False` |

## Current Evidence

- Web API client and DTOs exist in `apps/web/src/apis/workspace.ts`.
- Web workspace route exists in `apps/web/src/router/index.ts`.
- Workspace runtime page exists in `apps/web/src/pages/workspace/defaultPage/defaultPage.vue`.
- Single pending approval UI exists through `pendingToolApproval`, `capturePendingToolApproval`, `submitToolApproval` and `tool-approval-card`.
- Artifact and download UI exists through `getWorkspaceArtifactAPI`, `downloadWorkspaceArtifactAPI`, `runtime-artifact-panel` and `runtime-download-button`.
- Citation chips and Trace/Eval projection display exist through `runtime-citation-chip`, `runtime-observability-panel` and `release-eval`.
- Desktop shell, preload config and bridge exist in `apps/desktop/main.cjs`, `apps/desktop/preload.cjs` and `apps/desktop/bridge.cjs`.
- Static frontend tests exist under `tests/frontend/*`.

## Gap Evidence

- Generated or machine-checked Product Contract was not found for Web/Desktop DTOs.
- Product `AvailableAction` surface was not found in Web/Desktop source.
- `Last-Event-ID`, opaque cursor resume, resync, cursor expiry and disconnect reauthorization evidence were not found in SSE clients.
- Multiple pending Interrupt UI was not found; current page stores one `pendingToolApproval`.
- `TOOL_EFFECT_UNKNOWN` / reconcile / human-review / compensate UI proof was not found.
- Browser E2E framework/config and Desktop smoke tests were not found by static file inventory.
- Citation and Artifact independent authorization, revocation and download-session expiry were not proven.

## Available Package Commands

| package | scripts | run status | reason |
| --- | --- | --- | --- |
| `apps/web` | `dev`, `build`, `preview`, `lint` | not run | `node_modules` and `apps/web/node_modules` are absent; installing dependencies is outside P01-T04 allowed paths and would change dependency state |
| `apps/desktop` | `start`, `dev` | not run | `apps/desktop/node_modules` is absent; Electron smoke would require dependency install and a running frontend/backend |

## Browser / Desktop Evidence Status

- Browser E2E: blocked / not current. Static tests exist, but no Playwright/Cypress/Selenium browser run evidence was found or produced.
- Desktop Smoke: blocked / not current. Electron package scripts exist, but dependencies are absent and no smoke harness was found or run.
- SSE disconnect/resume/revoke: blocked / not current. Source inventory shows no cursor/resume/reauthorization path.
- Multiple Interrupt: target_not_current. Source inventory shows single `pendingToolApproval`.
- UNKNOWN UI recovery: target_not_current. Source inventory shows general failure/recovery fields, not canonical UNKNOWN reconciliation actions.

## Verification Results

| command | result |
| --- | --- |
| `git diff --check` | passed; only Git line-ending warnings were emitted |
| `python tools/scripts/verify_current_program.py` | passed |
| `python .agent/scripts/verify_agent_system.py` | passed |
| `python tools/scripts/verify_phase01_complete_baseline.py` | failed as expected for PHASE01 closure: P01-T01/T02/T05 stale or incomplete inventory, P01-T03 ledger gaps, all work packages not completed, Coordinator approval pending, PHASE02 gate closed, risk register P0 proof missing |
| `pytest -q tests/repo/test_current_program_contract.py tests/repo/test_phase01_complete_baseline.py -p no:cacheprovider` | passed, `10 passed` |

## Reproduction

Run from repository root:

```powershell
git status --short --branch
rg --files apps/web apps/desktop tests
rg -n "fetch-event-source|Last-Event-ID|cursor|resume|pendingToolApproval|approval|Artifact|citation|runtime-observability|release-eval|AvailableAction|UNKNOWN" apps/web/src apps/desktop tests -S
Get-FileHash -Algorithm SHA256 -LiteralPath .agent/programs/work-products/frontend-current-inventory.md
python tools/scripts/verify_phase01_complete_baseline.py
pytest -q tests/repo/test_current_program_contract.py tests/repo/test_phase01_complete_baseline.py -p no:cacheprovider
```

## Status Boundary

P01-T04 changes Current inventory evidence only. It does not modify Web/Desktop behavior and does not prove Browser E2E, Desktop Smoke, Product Contract adoption, AuthorizedView, AvailableAction, revocation, multiple Interrupt or UNKNOWN recovery. Those remain PHASE10 / PHASE21 handoff risks.
