# Zuno Launchers

This folder keeps the Windows launcher scripts grouped by product surface.

- `Zuno-Web-*.cmd`: browser-based Docker stack launchers
- `Zuno-Desktop-*.cmd`: Electron desktop launchers backed by Docker services

Behavior summary:

- `Web-Start`: starts the browser stack without forcing rebuild
- `Web-Rebuild`: rebuilds the Docker web stack and starts it
- `Desktop-Start`: starts backend containers, local Vite desktop frontend, and Electron
- `Desktop-Stop`: closes Electron plus the backend containers used by desktop mode
- `Desktop-Rebuild`: rebuilds the backend image used by desktop mode, then restarts the desktop runtime
- `Full Rebuild`: rebuilds from scratch and clears caches where applicable

Current launcher guarantees:

- success paths exit automatically and do not wait on `pause`
- failure paths still stop and show the error so the operator can read it
- web launchers wait for `7860` and `8090` before declaring success
- desktop launchers wait for `7860` and `8091` before declaring success
- desktop frontend PID tracking is bound to the real `8091` listener, not just the starter shell
- compose lifecycle commands use `--remove-orphans`, so legacy containers do not leak into current runs

Runtime services included in the Docker-backed stack:

- PostgreSQL
- Redis
- Neo4j
- MinIO
- FastAPI backend
- Vite frontend (web mode only)

Recommended desktop shortcuts:

- Web:
  - `Zuno-Web-Start`
  - `Zuno-Web-Stop`
  - `Zuno-Web-Rebuild`
  - `Zuno-Web-Full-Rebuild`
- Desktop:
  - `Zuno-Desktop-Start`
  - `Zuno-Desktop-Stop`
  - `Zuno-Desktop-Rebuild`
  - `Zuno-Desktop-Full-Rebuild`

Desktop runtime notes:

- local desktop frontend logs are written under `%TEMP%\zuno-desktop-runtime`
- the key files are `frontend.log`, `frontend.err.log`, `desktop.log`, and `desktop.err.log`
- if Electron does not appear but `8091` is healthy, check `desktop.err.log` first
- brief backend `health: starting` state during startup is normal convergence, not a launcher failure

Troubleshooting order:

1. Verify `docker ps` and confirm whether containers are actually up.
2. Verify `http://127.0.0.1:7860/health`.
3. For desktop mode, verify `http://127.0.0.1:8091`.
4. For web mode, verify `http://127.0.0.1:8090`.
5. If desktop UI still does not appear, inspect `%TEMP%\zuno-desktop-runtime\desktop.err.log`.

Known non-issues:

- `docker compose` may briefly report container stop/remove activity after the stop command has already made ports unreachable.
- backend health may remain `starting` for a short period even after the API is already reachable.
