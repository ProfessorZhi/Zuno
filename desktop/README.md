# Zuno Desktop

This directory contains the Electron shell for Zuno.

## Development

1. Start the backend separately. Default API base URL: `http://127.0.0.1:7860`
2. Start the frontend dev server from `src/frontend`:

```bash
npm run dev
```

3. Start Electron from `desktop`:

```bash
npm install
npm run dev
```

## Optional Environment Variables

- `DESKTOP_FRONTEND_URL`
- `DESKTOP_API_BASE_URL`

## Production-style Run

1. Build the frontend in `src/frontend`:

```bash
npm run build
```

2. Start Electron from `desktop`:

```bash
npm run start
```
