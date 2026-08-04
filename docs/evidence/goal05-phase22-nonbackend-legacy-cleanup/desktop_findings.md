# PHASE22 Desktop Findings

Branch: `claude/minimax-phase22-nonbackend-legacy-cleanup`
Scope: `apps/desktop/**`

## Files inspected

- `apps/desktop/main.cjs`
- `apps/desktop/preload.cjs`
- `apps/desktop/bridge.cjs`
- `apps/desktop/package.json`
- `apps/desktop/package-lock.json`

## Classification table

| Hit                                                                 | Context                                                                                                | Classification              |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | --------------------------- |
| `main.cjs::getEnv(name, fallback)`                                  | JS local function parameter name                                                                       | not legacy                  |
| `preload.cjs::getEnv(name, fallback)`                              | JS local function parameter name                                                                       | not legacy                  |
| `main.cjs::resetDesktopSessionCache`                               | Clears `appcache`, `shadercache`, `serviceworkers`, `cachestorage` on startup                          | not legacy                  |
| `main.cjs::runDesktopSmokeCheck` (capabilities array, smoke output) | Smoke verifies `runtimeRequest, actionConsume, projectionStream, streamLastEventId, streamDedup, streamReauthorization, artifactRead, artifactDownload, feedback` | not legacy (canonical capabilities) |
| `preload.cjs::productBridgeVersion`                                | `product-desktop-bridge-v1.phase10`                                                                    | not legacy (current version)|
| `preload.cjs::productEndpoints`                                    | `/api/v1/product/runtime-requests, /api/v1/product/actions/consume, /api/v1/product/stream-events, /api/v1/product/stream, /api/v1/product/artifacts/:artifactId, /api/v1/product/artifacts/:artifactId/download, /api/v1/product/feedback` | not legacy (canonical endpoints) |
| `bridge.cjs::runCommandAction`                                     | `powershell.exe` invocation under `unrestricted` access scope                                          | not legacy (intentional PowerShell host for desktop bridge) |
| `package-lock.json::"deprecated": "Package no longer supported..."` | A transitive (`semver` range) marked deprecated on npm                                                  | not legacy (npm upstream advisory) |

## Old desktop IPC channels

No retired IPC channels (`window.__ZUNO_DESKTOP__.legacy*`,
`electronLegacyBridge`, `phase0Stream`, etc.) were found in `preload.cjs`,
`main.cjs`, or `bridge.cjs`. The IPC surface is the canonical product bridge.

## Shell / PowerShell entrypoints

- `tools/launchers/windows/Zuno-Desktop-{Start,Stop,Rebuild,Full-Rebuild}.cmd`
  and the underlying `_Zuno-Desktop-{Common,StartFrontend,StartElectron,Cleanup,BuildFrontend}.cmd`
  / `*.ps1` are the canonical launchers.
- The four legacy forwarders in `tools/scripts/zuno-*.bat`
  (`zuno-start.bat`, `zuno-stop.bat`, `zuno-rebuild-start.bat`,
  `zuno-clean-rebuild-start.bat`) intentionally forward to the canonical
  launchers, and `tests/tools/test_launcher_scripts.py::test_legacy_desktop_forwarders_target_current_launcher_names`
  enforces the forward targets. They classify as ALLOWED_HISTORY_REFERENCE.

## Outcome

Nothing in `apps/desktop/**` qualifies as EXPIRED_CONFIG_RESIDUE. No edits
applied.
