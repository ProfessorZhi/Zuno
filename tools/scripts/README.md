# Zuno Scripts

This folder contains local helper scripts that are useful for development and maintenance.

## Main Scripts

- `start.py`: legacy local dev starter for backend/frontend.
- `clean_workspace.py`: removes safe local cache and temporary directories from the repo root.
- `run-full-e2e-smoke.ps1`: browser smoke-test helper.
- `zuno-*.bat`: legacy forwarders that now call the stable scripts in `tools/launchers/windows/`.

One-off migrations live in `tools/migrations/`.

## Local Start

From the repository root:

```powershell
python tools/scripts/start.py
```

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
