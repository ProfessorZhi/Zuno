type DesktopConfig = {
  apiBaseUrl?: string
  bridgeUrl?: string
  bridgeToken?: string
  workspaceRoot?: string
}

declare global {
  interface Window {
    __ZUNO_DESKTOP__?: DesktopConfig
  }
}

const trimTrailingSlash = (value: string) => value.replace(/\/+$/, '')
const CONTAINER_ONLY_HOSTS = new Set(['backend', 'agentchat-backend', 'frontend', 'agentchat-frontend'])

export const getApiBaseUrl = () => {
  const desktopApiBaseUrl = window.__ZUNO_DESKTOP__?.apiBaseUrl?.trim()
  if (desktopApiBaseUrl) {
    return trimTrailingSlash(desktopApiBaseUrl)
  }

  const viteApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim()
  if (viteApiBaseUrl) {
    try {
      const parsed = new URL(viteApiBaseUrl)
      if (CONTAINER_ONLY_HOSTS.has(parsed.hostname)) {
        // 宿主机浏览器访问前端时，容器内部域名不可达，应退回同源 /api 代理。
        return ''
      }
    } catch {
      // ignore parse errors and fall through
    }
    return trimTrailingSlash(viteApiBaseUrl)
  }

  if (typeof window !== 'undefined') {
    const { hostname, port } = window.location
    const isLocalHost = hostname === '127.0.0.1' || hostname === 'localhost'
    const isFrontendDevPort = port === '8090' || port === '8091'
    if (isLocalHost && isFrontendDevPort) {
      return 'http://127.0.0.1:7860'
    }
  }

  return ''
}

export const apiUrl = (path: string) => {
  if (!path) {
    return path
  }

  if (/^https?:\/\//i.test(path)) {
    return path
  }

  const apiBaseUrl = getApiBaseUrl()
  if (!apiBaseUrl) {
    return path
  }

  if (path.startsWith('/')) {
    return `${apiBaseUrl}${path}`
  }

  return `${apiBaseUrl}/${path}`
}

export const isDesktopRuntime = () => {
  return Boolean(window.__ZUNO_DESKTOP__)
}
