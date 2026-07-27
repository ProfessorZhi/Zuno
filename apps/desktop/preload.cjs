const { contextBridge } = require('electron')

const DEFAULT_API_BASE_URL = 'http://127.0.0.1:7860'

function getEnv(name, fallback) {
  const value = process.env[name]
  return value && value.trim() ? value.trim() : fallback
}

const runtimeConfig = {
  apiBaseUrl: getEnv('DESKTOP_API_BASE_URL', getEnv('VITE_API_BASE_URL', DEFAULT_API_BASE_URL)),
  bridgeUrl: getEnv('DESKTOP_BRIDGE_URL', ''),
  bridgeToken: getEnv('DESKTOP_BRIDGE_TOKEN', ''),
  workspaceRoot: getEnv('DESKTOP_WORKSPACE_ROOT', ''),
  productBridgeVersion: 'product-desktop-bridge-v1.phase10',
  productBridgeCapabilities: {
    runtimeRequest: true,
    actionConsume: true,
    projectionStream: true,
    streamLastEventId: true,
    streamDedup: true,
    streamReauthorization: true,
    artifactRead: true,
    artifactDownload: true,
    feedback: true,
  },
  productEndpoints: {
    runtimeRequests: '/api/v1/product/runtime-requests',
    actionConsume: '/api/v1/product/actions/consume',
    streamEvents: '/api/v1/product/stream-events',
    stream: '/api/v1/product/stream',
    artifactReadTemplate: '/api/v1/product/artifacts/:artifactId',
    artifactDownloadTemplate: '/api/v1/product/artifacts/:artifactId/download',
    feedback: '/api/v1/product/feedback',
  },
  productBridgeHealth: {
    bridgeUrlConfigured: Boolean(getEnv('DESKTOP_BRIDGE_URL', '')),
    tokenConfigured: Boolean(getEnv('DESKTOP_BRIDGE_TOKEN', '')),
    workspaceRootConfigured: Boolean(getEnv('DESKTOP_WORKSPACE_ROOT', '')),
  },
  taskLifecycleEndpoint: '/api/v1/workspace/task-lifecycle',
  artifactDownloadEndpointTemplate: '/api/v1/workspace/artifact/:artifactId/download',
  workspaceTaskLifecycleStates: [
    'pending',
    'running',
    'approval_required',
    'recoverable_failed',
    'cancelled',
    'completed',
  ],
}

contextBridge.exposeInMainWorld('__ZUNO_DESKTOP__', runtimeConfig)
