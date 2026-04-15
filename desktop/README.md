# AgentChat Desktop

This directory contains the first-stage Electron shell for AgentChat.

## Goals

- Reuse the existing Vue frontend as the desktop renderer
- Keep the current FastAPI backend running independently
- Inject a runtime API base URL so the same frontend code works in Web and Electron

## Development

1. Start the backend separately.
   Default API base URL: `http://127.0.0.1:7860`
2. Start the frontend dev server from `src/frontend`:

```bash
npm run dev
```

3. Start Electron from `desktop`:

```bash
npm install
npm run dev
```

Optional environment variables:

- `DESKTOP_FRONTEND_URL`: override the frontend dev server URL
- `DESKTOP_API_BASE_URL`: override the backend API base URL used by the desktop app

## Production Build Flow

1. Build the frontend in `src/frontend`:

```bash
npm run build
```

2. Start Electron from `desktop`:

```bash
npm run start
```

Electron will load `src/frontend/dist/index.html` in packaged-style mode.
