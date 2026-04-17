const { app, BrowserWindow, nativeImage, shell, session } = require('electron')
const path = require('node:path')
const fs = require('node:fs')
const { startDesktopBridgeServer } = require('./bridge.cjs')

const DEFAULT_DEV_FRONTEND_URL = 'http://localhost:8090'
let desktopBridgeState = null

app.commandLine.appendSwitch('disable-http-cache')

function resolveDesktopIcon() {
  const candidates = [
    path.resolve(__dirname, 'assets', 'zuno-icon.png'),
    path.resolve(__dirname, '..', 'src', 'frontend', 'src', 'assets', 'zuno-mark.svg'),
    path.resolve(__dirname, '..', 'src', 'frontend', 'public', 'zuno-favicon.svg'),
  ]

  for (const iconPath of candidates) {
    if (fs.existsSync(iconPath)) {
      return nativeImage.createFromPath(iconPath)
    }
  }
  return undefined
}

function getEnv(name, fallback) {
  const value = process.env[name]
  return value && value.trim() ? value.trim() : fallback
}

function resolveFrontendTarget() {
  if (app.isPackaged) {
    return {
      type: 'file',
      target: path.resolve(__dirname, '..', 'src', 'frontend', 'dist', 'index.html'),
    }
  }

  return {
    type: 'url',
    target: getEnv('DESKTOP_FRONTEND_URL', getEnv('VITE_DEV_SERVER_URL', DEFAULT_DEV_FRONTEND_URL)),
  }
}

function appendDesktopVersion(url) {
  const separator = url.includes('?') ? '&' : '?'
  return `${url}${separator}desktop_version=${app.getVersion()}`
}

async function resetDesktopSessionCache() {
  try {
    await session.defaultSession.clearCache()
    await session.defaultSession.clearStorageData({
      storages: ['appcache', 'shadercache', 'serviceworkers', 'cachestorage'],
    })
  } catch (error) {
    console.warn('[desktop] Failed to clear session cache:', error)
  }
}

async function createWindow() {
  const runtimeTarget = resolveFrontendTarget()
  const icon = resolveDesktopIcon()

  const mainWindow = new BrowserWindow({
    width: 1440,
    height: 960,
    minWidth: 1200,
    minHeight: 800,
    title: 'Zuno',
    icon,
    backgroundColor: '#f7f3ee',
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false,
    },
  })

  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  await resetDesktopSessionCache()

  if (runtimeTarget.type === 'file') {
    if (!fs.existsSync(runtimeTarget.target)) {
      console.warn(`[desktop] Frontend dist not found: ${runtimeTarget.target}`)
    }
    await mainWindow.loadFile(runtimeTarget.target)
    return
  }

  const targetUrl = appendDesktopVersion(runtimeTarget.target)

  mainWindow.webContents.on('did-fail-load', (_event, errorCode, errorDescription, validatedURL) => {
    const escapedMessage = String(errorDescription || 'unknown error')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
    const escapedUrl = String(validatedURL || targetUrl)
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
    const html = `<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <title>Zuno Desktop Load Error</title>
    <style>
      body {
        margin: 0;
        min-height: 100vh;
        display: grid;
        place-items: center;
        background: #f7efe5;
        color: #4c4038;
        font-family: "Segoe UI", "PingFang SC", sans-serif;
      }
      .panel {
        width: min(760px, calc(100vw - 64px));
        padding: 28px 30px;
        border-radius: 22px;
        background: rgba(255, 253, 249, 0.96);
        border: 1px solid rgba(214, 132, 70, 0.16);
        box-shadow: 0 20px 48px rgba(130, 71, 31, 0.12);
      }
      h1 { margin: 0 0 12px; font-size: 24px; }
      p { margin: 0 0 12px; line-height: 1.7; color: #6c5c50; }
      code {
        display: block;
        margin-top: 8px;
        padding: 12px 14px;
        border-radius: 14px;
        background: #fff7ef;
        color: #8b542d;
        word-break: break-all;
      }
    </style>
  </head>
  <body>
    <div class="panel">
      <h1>Zuno Desktop 未能加载前端页面</h1>
      <p>当前桌面窗口已经启动，但 Electron 无法连接到前端地址。请确认桌面前端 dev server 已经启动。</p>
      <p>错误：${escapedMessage} (${errorCode})</p>
      <code>${escapedUrl}</code>
    </div>
  </body>
</html>`
    void mainWindow.loadURL(`data:text/html;charset=utf-8,${encodeURIComponent(html)}`)
  })

  await mainWindow.loadURL(targetUrl)
}

app.whenReady().then(() => {
  app.setName('Zuno')
  if (process.platform === 'win32') {
    app.setAppUserModelId('com.zuno.desktop')
  }
  startDesktopBridgeServer({
    workspaceRoot: path.resolve(__dirname, '..'),
  })
    .then((bridgeState) => {
      desktopBridgeState = bridgeState
      process.env.DESKTOP_BRIDGE_URL = bridgeState.bridgeUrlForBackend
      process.env.DESKTOP_BRIDGE_TOKEN = bridgeState.token
      process.env.DESKTOP_WORKSPACE_ROOT = bridgeState.workspaceRoot
      void createWindow()
    })
    .catch((error) => {
      console.error('[desktop] Failed to start local bridge:', error)
      void createWindow()
    })

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      void createWindow()
    }
  })
})

app.on('window-all-closed', () => {
  if (desktopBridgeState?.server) {
    desktopBridgeState.server.close()
    desktopBridgeState = null
  }
  if (process.platform !== 'darwin') {
    app.quit()
  }
})
