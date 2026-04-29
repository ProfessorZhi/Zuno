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
}

contextBridge.exposeInMainWorld('__ZUNO_DESKTOP__', runtimeConfig)
