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
