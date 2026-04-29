# Zuno Scripts

This folder contains local helper scripts that are useful for development and maintenance.

## Main Scripts

- `start.py`: legacy local dev starter for backend/frontend.
- `run-full-e2e-smoke.ps1`: browser smoke-test helper.
- `fix_fastapi_jwt_auth.py`: local compatibility repair helper.
- `zuno-*.bat`: legacy forwarders that now call the stable scripts in `launchers/`.

One-off migrations live in `tools/migrations/`.

## Local Start

From the repository root:

```powershell
python tools/scripts/start.py
```

For normal Windows usage, prefer the stable launchers:

```powershell
.\launchers\Zuno-Web-Start.cmd
.\launchers\Zuno-Desktop-Start.cmd
```

## Smoke Test

```powershell
powershell -ExecutionPolicy Bypass -File .\tools\scripts\run-full-e2e-smoke.ps1
```
