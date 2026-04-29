const http = require('node:http')
const path = require('node:path')
const fs = require('node:fs/promises')
const crypto = require('node:crypto')
const { spawn } = require('node:child_process')

const DEFAULT_HOST = '0.0.0.0'
const MAX_READ_BYTES = 20000
const MAX_SEARCH_RESULTS = 40

function json(response, statusCode, payload) {
  response.writeHead(statusCode, {
    'Content-Type': 'application/json; charset=utf-8',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type, X-Zuno-Desktop-Token',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
  })
  response.end(JSON.stringify(payload))
}

function normalizeAccessScope(value) {
  return value === 'unrestricted' ? 'unrestricted' : 'workspace'
}

function createPathResolver(workspaceRoot, accessScope) {
  const normalizedWorkspaceRoot = path.resolve(workspaceRoot)

  return (inputPath = '.') => {
    const raw = String(inputPath || '.').trim()
    const resolved = path.isAbsolute(raw)
      ? path.resolve(raw)
      : path.resolve(normalizedWorkspaceRoot, raw)

    if (
      accessScope === 'workspace' &&
      resolved !== normalizedWorkspaceRoot &&
      !resolved.startsWith(`${normalizedWorkspaceRoot}${path.sep}`)
    ) {
      throw new Error(`路径超出工作区限制: ${resolved}`)
    }

    return resolved
  }
}

async function listDirectory(args, workspaceRoot, accessScope) {
  const resolvePath = createPathResolver(workspaceRoot, accessScope)
  const target = resolvePath(args.path)
  const entries = await fs.readdir(target, { withFileTypes: true })
  const slicedEntries = entries.slice(0, 200)
  const items = await Promise.all(
    slicedEntries.map(async (entry) => {
      const fullPath = path.join(target, entry.name)
      const stat = await fs.stat(fullPath)
      return {
        name: entry.name,
        path: fullPath,
        type: entry.isDirectory() ? 'directory' : 'file',
        size: stat.size,
        modified_at: stat.mtime.toISOString(),
      }
    })
  )
  return {
    ok: true,
    action: 'list_directory',
    path: target,
    items,
  }
}

async function readFileAction(args, workspaceRoot, accessScope) {
  const resolvePath = createPathResolver(workspaceRoot, accessScope)
  const target = resolvePath(args.path)
  const content = await fs.readFile(target, 'utf8')
  const truncated = content.length > MAX_READ_BYTES
  const safeContent = truncated ? content.slice(0, MAX_READ_BYTES) : content
  return {
    ok: true,
    action: 'read_file',
    path: target,
    truncated,
    content: safeContent,
  }
}

async function writeFileAction(args, workspaceRoot, accessScope) {
  const resolvePath = createPathResolver(workspaceRoot, accessScope)
  const target = resolvePath(args.path)
  const mode = args.append ? 'append' : 'overwrite'
  await fs.mkdir(path.dirname(target), { recursive: true })
  if (args.append) {
    await fs.appendFile(target, String(args.content ?? ''), 'utf8')
  } else {
    await fs.writeFile(target, String(args.content ?? ''), 'utf8')
  }
  const stat = await fs.stat(target)
  return {
    ok: true,
    action: 'write_file',
    path: target,
    mode,
    size: stat.size,
  }
}

async function searchFilesAction(args, workspaceRoot, accessScope) {
  const resolvePath = createPathResolver(workspaceRoot, accessScope)
  const root = resolvePath(args.path)
  const query = String(args.query || '').trim().toLowerCase()
  if (!query) {
    throw new Error('搜索关键字不能为空')
  }

  const results = []
  const maxResults = Math.min(Number(args.limit) || MAX_SEARCH_RESULTS, MAX_SEARCH_RESULTS)

  async function walk(currentPath) {
    if (results.length >= maxResults) return
    const entries = await fs.readdir(currentPath, { withFileTypes: true })
    for (const entry of entries) {
      if (results.length >= maxResults) break
      const fullPath = path.join(currentPath, entry.name)
      if (entry.isDirectory()) {
        if (['node_modules', '.git', 'dist', 'build', '__pycache__'].includes(entry.name)) continue
        await walk(fullPath)
        continue
      }
      const lowerName = entry.name.toLowerCase()
      if (lowerName.includes(query)) {
        results.push({ path: fullPath, match_type: 'filename' })
        continue
      }
      try {
        const buffer = await fs.readFile(fullPath)
        const text = buffer.toString('utf8')
        const index = text.toLowerCase().indexOf(query)
        if (index >= 0) {
          const snippetStart = Math.max(0, index - 80)
          const snippetEnd = Math.min(text.length, index + 160)
          results.push({
            path: fullPath,
            match_type: 'content',
            snippet: text.slice(snippetStart, snippetEnd),
          })
        }
      } catch {
        continue
      }
    }
  }

  await walk(root)
  return {
    ok: true,
    action: 'search_files',
    path: root,
    query,
    results,
  }
}

async function runCommandAction(args, workspaceRoot, accessScope) {
  if (accessScope !== 'unrestricted') {
    throw new Error('工作区限制模式下不允许执行任意终端命令，请切换到任意访问。')
  }

  const resolvePath = createPathResolver(workspaceRoot, accessScope)
  const cwd = resolvePath(args.cwd || '.')
  const command = String(args.command || '').trim()
  if (!command) {
    throw new Error('命令不能为空')
  }

  const timeoutMs = Math.min(Math.max(Number(args.timeout_ms) || 20000, 1000), 120000)

  return await new Promise((resolve, reject) => {
    const child = spawn(
      'powershell.exe',
      ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', command],
      {
        cwd,
        windowsHide: true,
        env: process.env,
      }
    )

    let stdout = ''
    let stderr = ''
    const timer = setTimeout(() => {
      child.kill()
      reject(new Error(`命令执行超时，已超过 ${timeoutMs}ms`))
    }, timeoutMs)

    child.stdout.on('data', (chunk) => {
      stdout += chunk.toString()
    })
    child.stderr.on('data', (chunk) => {
      stderr += chunk.toString()
    })
    child.on('error', (error) => {
      clearTimeout(timer)
      reject(error)
    })
    child.on('close', (code) => {
      clearTimeout(timer)
      resolve({
        ok: code === 0,
        action: 'run_command',
        cwd,
        command,
        exit_code: code ?? -1,
        stdout: stdout.trim(),
        stderr: stderr.trim(),
      })
    })
  })
}

function createBridgeHandler({ token, workspaceRoot }) {
  return async (request, response) => {
    if (request.method === 'OPTIONS') {
      json(response, 200, { ok: true })
      return
    }

    if (request.method !== 'POST' || request.url !== '/execute') {
      json(response, 404, { ok: false, error: 'Not Found' })
      return
    }

    const incomingToken = request.headers['x-zuno-desktop-token']
    if (!token || incomingToken !== token) {
      json(response, 401, { ok: false, error: 'Unauthorized' })
      return
    }

    let rawBody = ''
    request.on('data', (chunk) => {
      rawBody += chunk.toString()
    })

    request.on('end', async () => {
      try {
        const body = rawBody ? JSON.parse(rawBody) : {}
        const action = String(body.action || '').trim()
        const args = body.args || {}
        const accessScope = normalizeAccessScope(body.access_scope)

        let result
        if (action === 'list_directory') {
          result = await listDirectory(args, workspaceRoot, accessScope)
        } else if (action === 'read_file') {
          result = await readFileAction(args, workspaceRoot, accessScope)
        } else if (action === 'write_file') {
          result = await writeFileAction(args, workspaceRoot, accessScope)
        } else if (action === 'search_files') {
          result = await searchFilesAction(args, workspaceRoot, accessScope)
        } else if (action === 'run_command') {
          result = await runCommandAction(args, workspaceRoot, accessScope)
        } else {
          throw new Error(`不支持的 action: ${action}`)
        }

        json(response, 200, result)
      } catch (error) {
        json(response, 400, {
          ok: false,
          error: error instanceof Error ? error.message : String(error),
        })
      }
    })
  }
}

async function startDesktopBridgeServer(options = {}) {
  const workspaceRoot = path.resolve(options.workspaceRoot || path.resolve(__dirname, '..'))
  const token = options.token || crypto.randomUUID()

  const server = http.createServer(createBridgeHandler({ token, workspaceRoot }))

  await new Promise((resolve, reject) => {
    server.once('error', reject)
    server.listen(0, DEFAULT_HOST, resolve)
  })

  const address = server.address()
  const port = typeof address === 'object' && address ? address.port : 0

  return {
    server,
    port,
    token,
    workspaceRoot,
    bridgeUrlForBackend: `http://host.docker.internal:${port}`,
  }
}

module.exports = {
  startDesktopBridgeServer,
}
