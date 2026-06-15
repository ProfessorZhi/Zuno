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
