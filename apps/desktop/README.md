# Zuno Desktop

This directory contains the Electron shell for Zuno.

## Development

1. Start the backend separately. Default API base URL: `http://127.0.0.1:7860`
2. Start the frontend dev server from `apps/web`:

```bash
npm run dev
```

3. Start Electron from `apps/desktop`:

```bash
npm install
npm run dev
```

## Optional Environment Variables

- `DESKTOP_FRONTEND_URL`
- `DESKTOP_API_BASE_URL`

## Workspace Task Lifecycle

The Electron shell runs the same Web workspace product loop and exposes the same backend task lifecycle contract through `window.__ZUNO_DESKTOP__`:

- `taskLifecycleEndpoint`: `/api/v1/workspace/task-lifecycle`
- `artifactDownloadEndpointTemplate`: `/api/v1/workspace/artifact/:artifactId/download`
- `workspaceTaskLifecycleStates`: `pending`, `running`, `approval_required`, `recoverable_failed`, `cancelled`, `completed`

## Production-style Run

1. Build the frontend in `apps/web`:

```bash
npm run build
```

2. Start Electron from `apps/desktop`:

```bash
npm run start
```
