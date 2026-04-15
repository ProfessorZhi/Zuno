const { app, BrowserWindow, nativeImage, shell } = require('electron')
const path = require('node:path')
const fs = require('node:fs')
const { startDesktopBridgeServer } = require('./bridge.cjs')

const DEFAULT_DEV_FRONTEND_URL = 'http://localhost:8090'
let desktopBridgeState = null

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

function createWindow() {
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

  if (runtimeTarget.type === 'file') {
    if (!fs.existsSync(runtimeTarget.target)) {
      console.warn(`[desktop] Frontend dist not found: ${runtimeTarget.target}`)
    }
    mainWindow.loadFile(runtimeTarget.target)
    return
  }

  mainWindow.loadURL(runtimeTarget.target)
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
      createWindow()
    })
    .catch((error) => {
      console.error('[desktop] Failed to start local bridge:', error)
      createWindow()
    })

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow()
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
