export type WorkspaceMode = 'normal' | 'agent'

export interface WorkspaceGlobalDefaults {
  mode: WorkspaceMode
  modelId: string
  executionMode: string
  accessScope: string
  toolIds: string[]
  mcpServerIds: string[]
  skillIds: string[]
  knowledgeIds: string[]
  updatedAt: string
}

const DEFAULTS_KEY = 'zuno.workspace.defaults'
const SESSION_MODES_KEY = 'zuno.workspace.sessionModes'

export const createEmptyWorkspaceDefaults = (): WorkspaceGlobalDefaults => ({
  mode: 'normal',
  modelId: '',
  executionMode: 'tool',
  accessScope: 'workspace',
  toolIds: [],
  mcpServerIds: [],
  skillIds: [],
  knowledgeIds: [],
  updatedAt: '',
})

const isWorkspaceMode = (value: unknown): value is WorkspaceMode => value === 'normal' || value === 'agent'
const normalizeStringList = (value: unknown) => Array.isArray(value) ? value.filter((item): item is string => typeof item === 'string' && item.trim().length > 0) : []

export const loadWorkspaceDefaults = (): WorkspaceGlobalDefaults => {
  if (typeof window === 'undefined') return createEmptyWorkspaceDefaults()

  try {
    const raw = window.localStorage.getItem(DEFAULTS_KEY)
    if (!raw) return createEmptyWorkspaceDefaults()
    const parsed = JSON.parse(raw) as Partial<WorkspaceGlobalDefaults>
    return {
      mode: isWorkspaceMode(parsed.mode) ? parsed.mode : 'normal',
      modelId: typeof parsed.modelId === 'string' ? parsed.modelId : '',
      executionMode: typeof parsed.executionMode === 'string' && parsed.executionMode ? parsed.executionMode : 'tool',
      accessScope: typeof parsed.accessScope === 'string' && parsed.accessScope ? parsed.accessScope : 'workspace',
      toolIds: normalizeStringList(parsed.toolIds),
      mcpServerIds: normalizeStringList(parsed.mcpServerIds),
      skillIds: normalizeStringList(parsed.skillIds),
      knowledgeIds: normalizeStringList(parsed.knowledgeIds).slice(0, 1),
      updatedAt: typeof parsed.updatedAt === 'string' ? parsed.updatedAt : '',
    }
  } catch {
    return createEmptyWorkspaceDefaults()
  }
}

export const saveWorkspaceDefaults = (defaults: WorkspaceGlobalDefaults) => {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(DEFAULTS_KEY, JSON.stringify({
    ...defaults,
    knowledgeIds: defaults.knowledgeIds.slice(0, 1),
    updatedAt: new Date().toISOString(),
  }))
}

export const loadWorkspaceSessionModes = (): Record<string, WorkspaceMode> => {
  if (typeof window === 'undefined') return {}

  try {
    const raw = window.localStorage.getItem(SESSION_MODES_KEY)
    if (!raw) return {}
    const parsed = JSON.parse(raw) as Record<string, unknown>
    return Object.fromEntries(
      Object.entries(parsed).filter((entry): entry is [string, WorkspaceMode] => Boolean(entry[0]) && isWorkspaceMode(entry[1]))
    )
  } catch {
    return {}
  }
}

export const saveWorkspaceSessionMode = (sessionId: string, mode: WorkspaceMode) => {
  if (typeof window === 'undefined' || !sessionId) return
  const nextModes = loadWorkspaceSessionModes()
  nextModes[sessionId] = mode
  window.localStorage.setItem(SESSION_MODES_KEY, JSON.stringify(nextModes))
}

export const removeWorkspaceSessionMode = (sessionId: string) => {
  if (typeof window === 'undefined' || !sessionId) return
  const nextModes = loadWorkspaceSessionModes()
  delete nextModes[sessionId]
  window.localStorage.setItem(SESSION_MODES_KEY, JSON.stringify(nextModes))
}
