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

## Product Bridge V1

PHASE10 adds a versioned Product bridge contract to `window.__ZUNO_DESKTOP__`.

- `productBridgeVersion`: `product-desktop-bridge-v1.phase10`
- `productBridgeCapabilities`: runtime request, action consume, projection stream, Last-Event-ID resume, dedup, reauthorization, artifact read/download and feedback
- `productEndpoints.runtimeRequests`: `/api/v1/product/runtime-requests`
- `productEndpoints.actionConsume`: `/api/v1/product/actions/consume`
- `productEndpoints.streamEvents`: `/api/v1/product/stream-events`
- `productEndpoints.stream`: `/api/v1/product/stream`
- `productEndpoints.artifactReadTemplate`: `/api/v1/product/artifacts/:artifactId`
- `productEndpoints.artifactDownloadTemplate`: `/api/v1/product/artifacts/:artifactId/download`
- `productEndpoints.feedback`: `/api/v1/product/feedback`
- `productBridgeHealth`: reports whether the local desktop bridge URL, token and workspace root were injected

## Production-style Run

1. Build the frontend in `apps/web`:

```bash
npm run build
```

2. Start Electron from `apps/desktop`:

```bash
npm run start
```
