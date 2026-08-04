# Zuno Scripts

This folder contains local helper scripts that are useful for development and maintenance.

## Main Scripts

- `start.py`: local recovery-period starter for the current backend/frontend development surface.
- `clean_workspace.py`: removes safe local cache and temporary directories from the repo root.
- `run-full-e2e-smoke.ps1`: browser smoke-test helper.
- `zuno-*.bat`: legacy forwarders that now call the stable scripts in `tools/launchers/windows/`.

One-off migrations live in `tools/migrations/`.

## Local Start

From the repository root:

```powershell
python tools/scripts/start.py
```

This script currently exists to help during the mixed-runtime recovery period:

- frontend starts from `apps/web`
- backend startup still follows the repo's current mixed runtime surface
- when PostgreSQL is unavailable, backend startup should now fail fast instead of hanging indefinitely
- this script should not be treated as proof that the paused service migration is the active architecture target

For normal Windows usage, prefer the stable launchers:

```powershell
.\tools\launchers\windows\Zuno-Web-Start.cmd
.\tools\launchers\windows\Zuno-Desktop-Start.cmd
```

## Local Cleanup

```powershell
python tools/scripts/clean_workspace.py --dry-run
python tools/scripts/clean_workspace.py
```

## Smoke Test

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\scripts\run-full-e2e-smoke.ps1
```

## PHASE22 Final Legacy/Cutover Audit Gate

```powershell
python tools/scripts/verify_phase22_final_legacy_cutover.py
python tools/scripts/verify_phase22_final_legacy_cutover.py --json
```

`verify_phase22_final_legacy_cutover.py` (V2) is the PHASE22 fail-closed
audit gate. It walks every production file with the `ast` module,
detects Phase08 `_fallback_to_legacy` runtime blockers, dual-path
markers, alias/bypass constructors and public-adapter ownership
violations, enforces feature-flag expiry against the current
`PHASE22`, and tracks unresolved architectural escalations. YAML work
products are parsed with `yaml.safe_load`; the exact Head SHA is
read through `git rev-parse HEAD`.

Status priority (highest first):

1. `LEGACY_RUNTIME_BLOCKERS_FOUND` (exit 2)
2. `DUAL_PATH_BLOCKERS_FOUND` (exit 3)
3. `ALIAS_BYPASS_BLOCKERS_FOUND` (exit 4)
4. `PUBLIC_ADAPTER_OWNERSHIP_VIOLATION` (exit 5)
5. `AUDIT_UNRESOLVED` (exit 6)
6. `LEGACY_CUTOVER_AUDIT_CLEAN` (exit 0)
7. `TOOL_ERROR` (exit 7)

The companion test suite is
`tests/repo/test_phase22_final_legacy_cutover.py` (30 boundary tests
plus contract fixtures under `tests/fixtures/phase22_legacy_cutover/`).
Evidence artifacts live under
`docs/evidence/goal05-phase22-legacy-cutover-final-audit-v2/`.
