import { spawnSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const appRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const binName = process.argv[2]
const binArgs = process.argv.slice(3)

const bins = {
  vite: 'vite/bin/vite.js',
  'vue-tsc': 'vue-tsc/bin/vue-tsc.js',
}

if (!binName || !bins[binName]) {
  console.error(`Unsupported frontend binary: ${binName || '<missing>'}`)
  process.exit(1)
}

const candidates = [
  resolve(appRoot, 'node_modules', bins[binName]),
  resolve(appRoot, '..', '..', 'node_modules', bins[binName]),
]
const entry = candidates.find((candidate) => existsSync(candidate))

if (!entry) {
  console.error(`Cannot find ${binName}. Tried: ${candidates.join(', ')}`)
  process.exit(1)
}

const result = spawnSync(process.execPath, [entry, ...binArgs], { stdio: 'inherit' })
process.exit(result.status ?? 1)
