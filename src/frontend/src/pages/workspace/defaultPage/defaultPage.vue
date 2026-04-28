<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown, ArrowUp, Plus } from '@element-plus/icons-vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import {
  createWorkspaceSessionAPI,
  deleteWorkspaceSessionAPI,
  getWorkspaceExecutionModesAPI,
  getWorkspacePluginsByModeAPI,
  getWorkspaceSessionInfoAPI,
  workspaceSimpleChatStreamAPI,
  type AccessScopeDefinition,
  type ExecutionModeDefinition,
  type WorkspaceAttachment,
  type WorkspaceExecutionConfig,
  type WorkspaceStreamEvent,
  type WorkSpaceSimpleTask,
} from '../../../apis/workspace'
import { uploadFile } from '../../../apis/chat'
import { getVisibleLLMsAPI, type LLMResponse } from '../../../apis/llm'
import { getAgentSkillsAPI, type AgentSkill } from '../../../apis/agent-skill'
import { getKnowledgeListAPI, type KnowledgeResponse } from '../../../apis/knowledge'
import { useUserStore } from '../../../store/user'
import { getRetrievalModeLabel, normalizeRetrievalMode } from '../../../utils/retrieval'
import { describeKnowledgeConfig, normalizeKnowledgeConfig } from '../../../utils/knowledge-config'
import { safeDisplayText } from '../../../utils/display-text'
import { sanitizeWorkspaceContexts } from '../../../utils/workspace-history'
import { zunoAgentAvatar } from '../../../utils/brand'
import { isDesktopRuntime } from '../../../utils/api'
import {
  loadWorkspaceDefaults,
  saveWorkspaceSessionMode,
  type WorkspaceMode,
} from '../../../utils/workspace-defaults'

const ALWAYS_WEB_SEARCH = true
const MAX_ATTACHMENTS = 5
const MAX_ATTACHMENT_SIZE = 20 * 1024 * 1024
const CHAT_IMAGE_EXTENSIONS = new Set(['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'])
const AGENT_DOCUMENT_EXTENSIONS = new Set(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'md', 'csv', 'xls', 'xlsx'])

const fallbackDescription = '\u6682\u65e0\u63cf\u8ff0'
const fallbackKnowledgeDescription = (count?: number) => `\u5171 ${count || 0} \u4e2a\u6587\u4ef6`

interface ChatMessage { role: 'user' | 'assistant'; content: string }
interface RetrievalRoundTrace { round: number; mode: string; trigger?: string; qualityReason?: string; query?: string }
interface RetrievalTraceSummary {
  firstMode: string
  finalMode: string
  roundCount: number
  fallbackReason: string
  rewrittenQueryUsed: boolean
  rounds: RetrievalRoundTrace[]
}
interface TraceRecord {
  id: string
  title: string
  detail: string
  at: string
  phase?: string
  status?: string
  accent?: 'default' | 'tool' | 'graph' | 'retrieval' | 'answer' | 'error'
  retrieval?: RetrievalTraceSummary | null
}
interface PendingAttachment extends WorkspaceAttachment { id: string; preview_url?: string }
interface ProgressStep { key: string; label: string; done: boolean; active: boolean; accent?: 'default' | 'tool' | 'graph' | 'retrieval' | 'answer' | 'error' }

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const modes = [
  { id: 'normal' as const, label: '聊天模式', description: '适合轻量对话、图片理解与快速问答。' },
  { id: 'agent' as const, label: 'Agent 模式', description: '可调用工具、分析附件，并执行更完整的任务流程。' },
]

const selectedMode = ref<WorkspaceMode>('normal')
const inputMessage = ref('')
const consumedInitialMessageKey = ref('')
const initialRouteMessageInFlightKey = ref('')
const messages = ref<ChatMessage[]>([])
const executionEvents = ref<TraceRecord[]>([])
const executionModes = ref<ExecutionModeDefinition[]>([])
const accessScopes = ref<AccessScopeDefinition[]>([])
const selectedExecutionMode = ref('tool')
const selectedAccessScope = ref('workspace')
const plugins = ref<any[]>([])
const selectedTools = ref<string[]>([])
const mcpServers = ref<any[]>([])
const selectedMcpServers = ref<string[]>([])
const skillOptions = ref<AgentSkill[]>([])
const selectedSkillIds = ref<string[]>([])
const knowledgeOptions = ref<KnowledgeResponse[]>([])
const selectedKnowledgeIds = ref<string[]>([])
const toolsTouched = ref(false)
const mcpTouched = ref(false)
const skillsTouched = ref(false)
const knowledgeTouched = ref(false)
const modelOptions = ref<LLMResponse[]>([])
const selectedModelId = ref('')
const isGenerating = ref(false)
const modelsLoading = ref(false)
const currentSessionId = ref('')
const conversationRef = ref<HTMLElement | null>(null)
const showTracePanel = ref(false)
const isPinnedToBottom = ref(true)
const workspaceHydrated = ref(false)
const attachmentInputRef = ref<HTMLInputElement | null>(null)
const pendingAttachments = ref<PendingAttachment[]>([])
const attachmentsUploading = ref(false)
const isAttachmentDragOver = ref(false)
const activeSuggestionIndex = ref(0)

type SlashSuggestion = {
  key: string
  label: string
  detail: string
  insertValue: string
}

type ToolCreationKind = 'general' | 'api' | 'cli'

const activeMode = computed(() => modes.find((mode) => mode.id === selectedMode.value) || modes[0])
const activeExecutionMode = computed(() => executionModes.value.find((mode) => mode.id === selectedExecutionMode.value) || null)
const activeAccessScope = computed(() => accessScopes.value.find((scope) => scope.id === selectedAccessScope.value) || null)
const isAgentMode = computed(() => selectedMode.value === 'agent')
const attachmentAccept = computed(() => isAgentMode.value ? '.jpg,.jpeg,.png,.gif,.webp,.bmp,.pdf,.doc,.docx,.ppt,.pptx,.txt,.md,.csv,.xls,.xlsx' : 'image/*')
const attachmentHint = computed(() => {
  if (!isAgentMode.value) return '聊天模式仅支持图片，文档请切换到 Agent 模式。'
  if (selectedExecutionMode.value === 'terminal') {
    return '终端模式支持图片、PDF、Word、PPT、TXT、Markdown 和 Excel，可结合本地文件与命令执行。'
  }
  return 'Agent 模式支持图片、PDF、Word、PPT、TXT、Markdown 和 Excel。'
})
const composerPlaceholder = computed(() => {
  if (!isAgentMode.value) return '输入你的问题，直接开始对话。'
  if (selectedExecutionMode.value === 'terminal') return '输入终端任务，或用 /terminal 明确要求访问本地文件与命令行。'
  return '输入你的任务，或输入 / 直接选择 Skill。'
})
const modeFooterCopy = computed(() => {
  if (!isAgentMode.value) return '聊天模式 / 支持图片输入'
  const base = `${activeExecutionMode.value?.label || '工具模式'} / ${activeAccessScope.value?.label || '工作区限制'}`
  if (selectedExecutionMode.value === 'terminal') return `${base} · 支持 /terminal`
  return `${base} · MCP 默认启用，输入 / 可快速选择 Skill`
})
const canPickTools = computed(() => isAgentMode.value && selectedExecutionMode.value === 'tool')
const autoAvailableMcpIds = computed(() => (
  mcpServers.value
    .filter((server: any) => !server?.config_enabled && (!Array.isArray(server?.config) || server.config.length === 0))
    .map((server: any) => server.mcp_server_id)
    .filter(Boolean)
))
const selectedToolCount = computed(() => (
  selectedTools.value.length
  + selectedMcpServers.value.length
  + selectedSkillIds.value.length
  + selectedKnowledgeIds.value.length
))
const selectedKnowledge = computed(() => {
  const currentId = selectedKnowledgeIds.value[0]
  return knowledgeOptions.value.find((item) => item.id === currentId) || null
})
const selectedKnowledgeConfig = computed(() => normalizeKnowledgeConfig(selectedKnowledge.value?.knowledge_config))
const effectiveRetrievalMode = computed(() => normalizeRetrievalMode(selectedKnowledgeConfig.value.retrieval_settings.default_mode))
const effectiveRetrievalModeLabel = computed(() => getRetrievalModeLabel(effectiveRetrievalMode.value))
const selectedKnowledgeSummary = computed(() => describeKnowledgeConfig(selectedKnowledgeConfig.value))
const buildToolCreationPrompt = (kind: ToolCreationKind = 'general') => {
  if (kind === 'api') {
    return [
      '请帮我新增一个 API 工具。',
      '你先判断我提供的信息是否足够；如果不够，请继续追问。',
      '我会继续给你：接口文档或文档地址、Base URL、路径、认证方式、API Key、图标。',
      '信息足够后，请直接创建工具，并告诉我创建结果、工具名称和下一步如何测试。',
    ].join('\n')
  }
  if (kind === 'cli') {
    return [
      '请帮我新增一个 CLI 工具。',
      '你先判断我提供的信息是否足够；如果不够，请继续追问。',
      '我会继续给你：本地目录、可执行命令、GitHub 地址、README、安装方法、所需凭证、图标。',
      '信息足够后，请直接创建工具，并告诉我创建结果、工具名称和下一步如何测试。',
    ].join('\n')
  }
  return [
    '请帮我新增一个工具。',
    '你先判断它应该接成 API 还是 CLI；如果信息不够，请继续追问。',
    '我会继续给你：文档地址、URL、API Key、本地目录、安装方法、图标等。',
    '信息足够后，请直接创建工具，并告诉我创建结果、工具名称和下一步如何测试。',
  ].join('\n')
}

const openToolCreationPrompt = (kind: ToolCreationKind = 'general') => {
  inputMessage.value = buildToolCreationPrompt(kind)
  activeSuggestionIndex.value = 0
}

const retrievalModeHint = computed(() => {
  if (!isAgentMode.value || !canPickTools.value || selectedKnowledgeIds.value.length === 0) {
    return '选中知识库后，会自动使用这个知识库自己的默认检索策略。首轮不足时会自动补检一轮。'
  }
  return `当前跟随知识库：${effectiveRetrievalModeLabel.value}`
})
const compactPanel = computed(() => messages.value.length > 0)
const traceVisible = computed(() => isAgentMode.value && showTracePanel.value)
const toolCreationSuggestions: SlashSuggestion[] = [
  {
    key: 'create-tool-general',
    label: '/新增工具',
    detail: '让 Agent 判断是 API 还是 CLI，并继续追问缺失信息。',
    insertValue: buildToolCreationPrompt('general'),
  },
  {
    key: 'create-tool-api',
    label: '/新增API工具',
    detail: '适合你已经有文档、URL、认证方式或 API Key 的接口能力。',
    insertValue: buildToolCreationPrompt('api'),
  },
  {
    key: 'create-tool-cli',
    label: '/新增CLI工具',
    detail: '适合本地目录、可执行命令、README、GitHub 仓库一类能力。',
    insertValue: buildToolCreationPrompt('cli'),
  },
]

const slashSuggestions = computed<SlashSuggestion[]>(() => {
  if (!isAgentMode.value || selectedExecutionMode.value === 'terminal') return []
  const text = inputMessage.value || ''
  if (!text.startsWith('/')) return []
  const trimmed = text.trimStart()
  if (!trimmed.startsWith('/')) return []

  const keyword = trimmed.slice(1).trim().toLowerCase()
  const builtIns = toolCreationSuggestions.filter((item) => {
    const haystack = `${item.label} ${item.detail}`.toLowerCase()
    return !keyword || haystack.includes(keyword)
  })
  const skillSuggestions = skillOptions.value
    .filter((skill) => {
      const name = (skill.name || '').toLowerCase()
      const desc = (skill.description || '').toLowerCase()
      return !keyword || name.includes(keyword) || desc.includes(keyword)
    })
    .slice(0, 8)
    .map((skill) => ({
      key: `skill-${skill.id}`,
      label: `/${skill.name}`,
      detail: skill.description || 'Skill',
      insertValue: `/${skill.name} `,
    }))
  return [...builtIns, ...skillSuggestions].slice(0, 8)
})
const latestTraceRecord = computed(() => executionEvents.value[executionEvents.value.length - 1] || null)
const progressStageIndex = computed(() => {
  if (!isAgentMode.value || (!isGenerating.value && executionEvents.value.length === 0)) return -1
  if (!isGenerating.value && executionEvents.value.length > 0) return 4
  const last = latestTraceRecord.value
  if (!last) return 0
  if (last.phase === 'complete' || last.status === 'END') return 4
  if (last.phase === 'model_call' || last.phase === 'answer') return 3
  if (last.accent === 'tool') return 2
  if (last.accent === 'graph') return 1
  if (last.accent === 'retrieval') return 1
  return 0
})
const progressSteps = computed<ProgressStep[]>(() => {
  const activeIndex = progressStageIndex.value
  return [
    { key: 'prepare', label: '准备请求', done: activeIndex > 0, active: activeIndex === 0, accent: 'default' },
    { key: 'retrieve', label: '检索知识', done: activeIndex > 1, active: activeIndex === 1, accent: effectiveRetrievalMode.value === 'graphrag' ? 'graph' : 'retrieval' },
    { key: 'tool', label: '调用能力', done: activeIndex > 2, active: activeIndex === 2, accent: 'tool' },
    { key: 'answer', label: '整理答案', done: activeIndex > 3, active: activeIndex === 3, accent: 'answer' },
    { key: 'done', label: '完成输出', done: !isGenerating.value && executionEvents.value.length > 0, active: activeIndex === 4, accent: 'default' },
  ]
})
const progressHeadline = computed(() => {
  if (!isAgentMode.value || (!isGenerating.value && executionEvents.value.length === 0)) return ''
  return latestTraceRecord.value?.title || '正在处理中'
})
const progressDetail = computed(() => {
  if (!isAgentMode.value || (!isGenerating.value && executionEvents.value.length === 0)) return ''
  return latestTraceRecord.value?.detail || `${activeExecutionMode.value?.label || selectedExecutionMode.value} / ${activeAccessScope.value?.label || selectedAccessScope.value}`
})
const liveProgressEvents = computed(() => executionEvents.value.slice(-3))

const safeQueryValue = (value: unknown, fallback: string) => Array.isArray(value) ? String(value[0] || fallback) : (typeof value === 'string' && value.trim() ? value : fallback)
const getFileExtension = (fileName: string) => fileName.split('.').pop()?.toLowerCase() || ''

const sanitizeAssistantChunk = (chunk: string) => isAgentMode.value ? chunk : chunk.replace(/ReAct\s*Agent[^\n]*\n?/gi, '').replace(/^\s+/, '')
const handleAvatarError = (event: Event) => { const target = event.target as HTMLImageElement; if (target) target.src = '/src/assets/user.svg' }
const scrollToBottom = async (force = false) => { await nextTick(); if (conversationRef.value && (force || isPinnedToBottom.value)) conversationRef.value.scrollTop = conversationRef.value.scrollHeight }
const handleConversationScroll = () => { const panel = conversationRef.value; if (!panel) return; isPinnedToBottom.value = panel.scrollHeight - (panel.scrollTop + panel.clientHeight) < 24 }
const emitSessionUpdated = () => window.dispatchEvent(new CustomEvent('workspace-session-updated', { detail: { sessionId: currentSessionId.value } }))
const emitSessionModeUpdated = () => window.dispatchEvent(new CustomEvent('workspace-session-mode-updated', { detail: { sessionId: currentSessionId.value, mode: selectedMode.value } }))
const clearConversationState = () => {
  inputMessage.value = ''
  messages.value = []
  executionEvents.value = []
  pendingAttachments.value = []
  attachmentsUploading.value = false
  isGenerating.value = false
  showTracePanel.value = false
  isPinnedToBottom.value = true
  consumedInitialMessageKey.value = ''
  initialRouteMessageInFlightKey.value = ''
}
const isCurrentSessionDisposable = () => (
  Boolean(currentSessionId.value)
  && messages.value.length === 0
  && executionEvents.value.length === 0
  && pendingAttachments.value.length === 0
)

const buildWorkspaceQuery = () => ({
  ...(currentSessionId.value ? { session_id: currentSessionId.value } : {}),
  mode: selectedMode.value,
  execution_mode: selectedExecutionMode.value,
  access_scope: selectedAccessScope.value,
})

const syncRouteState = async () => {
  await router.replace({ name: 'workspaceDefaultPage', query: buildWorkspaceQuery() })
}

const resetToDraftSession = async (mode: WorkspaceMode, options?: { pruneCurrent?: boolean }) => {
  const pruneCurrent = options?.pruneCurrent !== false
  const disposableSessionId = pruneCurrent && isCurrentSessionDisposable() ? currentSessionId.value : ''
  clearConversationState()
  selectedMode.value = mode
  currentSessionId.value = ''
  try {
    if (disposableSessionId) {
      await deleteWorkspaceSessionAPI(disposableSessionId)
    }
  } catch (error) {
    console.warn('清理空会话失败', error)
  }
  await syncRouteState()
  emitSessionUpdated()
}

const createPersistedSession = async (mode: WorkspaceMode) => {
  selectedMode.value = mode
  const response = await createWorkspaceSessionAPI({
    title: '新对话',
    workspace_mode: mode,
    agent: mode,
    contexts: [],
  })
  if (response.data?.status_code !== 200 || !response.data?.data?.session_id) {
    throw new Error('create_session_failed')
  }
  currentSessionId.value = String(response.data.data.session_id)
  saveWorkspaceSessionMode(currentSessionId.value, mode)
  await syncRouteState()
  emitSessionUpdated()
  emitSessionModeUpdated()
}

const startFreshConversation = async () => {
  const defaults = loadWorkspaceDefaults()
  selectedExecutionMode.value = defaults.executionMode || selectedExecutionMode.value
  selectedAccessScope.value = defaults.accessScope || selectedAccessScope.value
  if (defaults.modelId && modelOptions.value.some((model) => model.llm_id === defaults.modelId)) selectedModelId.value = defaults.modelId
  await resetToDraftSession(defaults.mode || selectedMode.value)
  await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
  applySavedWorkspaceDefaults()
}
const handleNewConversationRequest = async () => {
  if (isGenerating.value) {
    ElMessage.warning('请等待当前回复完成后再新建会话。')
    return
  }
  try {
    await startFreshConversation()
  } catch (error) {
    console.error('新建会话失败', error)
    ElMessage.error('新建会话失败')
  }
}
const getRetrievalTriggerLabel = (trigger: string) => {
  if (trigger === 'route_broadening') return '自动扩路补检'
  if (trigger === 'query_rewrite_retry') return '改写后重试'
  if (trigger === 'initial') return '首轮检索'
  return trigger || '检索'
}
const getQualityReasonLabel = (reason: string) => {
  if (reason === 'empty_result') return '结果为空'
  if (reason === 'graph_result_empty') return '图谱结果为空'
  if (reason === 'too_few_documents') return '召回片段过少'
  if (reason === 'low_rerank_score') return '重排分数过低'
  if (reason === 'no_relevant_documents') return '没有相关文档'
  return reason || ''
}
const buildRetrievalTrace = (data: Record<string, any>, retrievalMode: string): RetrievalTraceSummary | null => {
  const rounds = Array.isArray(data.rounds) ? data.rounds : []
  const firstMode = String(data.first_mode || retrievalMode || '').trim()
  const finalMode = String(data.final_mode || retrievalMode || '').trim()
  const fallbackReason = String(data.fallback_reason || '').trim()
  const roundCount = Number(data.round_count || rounds.length || 0)
  const rewrittenQueryUsed = Boolean(data.rewritten_query_used)
  if (!firstMode && !finalMode && !roundCount && !fallbackReason && rounds.length === 0)
    return null
  return {
    firstMode: firstMode || finalMode || retrievalMode || 'rag',
    finalMode: finalMode || firstMode || retrievalMode || 'rag',
    roundCount: roundCount || Math.max(rounds.length, 1),
    fallbackReason,
    rewrittenQueryUsed,
    rounds: rounds.map((item: any, index: number) => ({
      round: Number(item?.round || index + 1),
      mode: String(item?.mode || finalMode || retrievalMode || 'rag'),
      trigger: String(item?.trigger || ''),
      qualityReason: String(item?.quality_reason || ''),
      query: String(item?.query || ''),
    })),
  }
}
const buildRetrievalTraceDetail = (data: Record<string, any>, retrievalMode: string) => {
  const retrieval = buildRetrievalTrace(data, retrievalMode)
  if (!retrieval) return ''
  const routeSummary = retrieval.firstMode && retrieval.finalMode && retrieval.firstMode !== retrieval.finalMode
    ? `首轮 ${getRetrievalModeLabel(retrieval.firstMode)}，最终切到 ${getRetrievalModeLabel(retrieval.finalMode)}`
    : `检索策略：${getRetrievalModeLabel(retrieval.finalMode || retrievalMode)}`
  const parts = [`${routeSummary}，共 ${retrieval.roundCount} 轮。`]
  if (retrieval.fallbackReason) parts.push(`补检原因：${retrieval.fallbackReason}。`)
  if (retrieval.rewrittenQueryUsed) parts.push('已启用改写后的问题再次检索。')
  const lastRound = retrieval.rounds[retrieval.rounds.length - 1]
  if (lastRound?.trigger === 'query_rewrite_retry') {
    parts.push('最后一轮来自改写后重试。')
  } else if (lastRound?.trigger === 'route_broadening') {
    parts.push('最后一轮来自自动扩路补检。')
  }
  return parts.join('')
}

const buildTraceRecord = (event: WorkspaceStreamEvent): TraceRecord => {
  const data = event.data || {}
  const phase = String(data.phase || '')
  const status = String(data.status || '')
  const retrievalMode = String(data.retrieval_mode || effectiveRetrievalMode.value || '')
  const retrieval = buildRetrievalTrace(data, retrievalMode)
  const toolName = String(data.tool_name || '')
  const toolResult = String(data.result || data.message || '')
  const isToolCreation = event.type === 'tool_result' && ['create_remote_api_tool', 'create_cli_tool'].includes(toolName)
  if (event.type === 'tool_call') {
    return { id: event.id || crypto.randomUUID(), title: '正在调用工具', detail: String(data.tool_name || data.message || '正在执行外部能力'), at: new Date().toLocaleTimeString(), phase, status, accent: 'tool', retrieval }
  }
  if (event.type === 'tool_result') {
    const failed = data.ok === false
    return {
      id: event.id || crypto.randomUUID(),
      title: isToolCreation
        ? (
            failed
              ? (toolName === 'create_remote_api_tool' ? '创建 API 工具失败' : '创建 CLI 工具失败')
              : (toolName === 'create_remote_api_tool' ? '已创建 API 工具' : '已创建 CLI 工具')
          )
        : '工具已返回结果',
      detail: isToolCreation
        ? toolResult
        : String(data.tool_name || data.message || '已收到工具结果'),
      at: new Date().toLocaleTimeString(),
      phase,
      status,
      accent: data.ok === false ? 'error' : 'tool',
      retrieval,
    }
  }
  if (event.type === 'final') {
    return { id: event.id || crypto.randomUUID(), title: '正在整理最终回复', detail: `${buildRetrievalTraceDetail(data, retrievalMode)} 正在生成最终答案。`, at: new Date().toLocaleTimeString(), phase: phase || 'answer', status, accent: 'answer', retrieval }
  }
  const accent = phase.includes('error')
    ? 'error'
    : retrievalMode === 'graphrag'
      ? 'graph'
      : retrievalMode === 'hybrid' || retrievalMode === 'auto' || retrievalMode === 'rag'
        ? 'retrieval'
        : 'default'
  return {
    id: event.id || crypto.randomUUID(),
    title: String(data.message || event.title || '正在处理中'),
    detail: String(
      data.result
      || data.error
      || data.tool_name
      || event.detail
      || (
        retrievalMode
          ? buildRetrievalTraceDetail(data, retrievalMode)
          : ''
      )
    ),
    at: new Date().toLocaleTimeString(),
    phase,
    status,
    accent,
    retrieval,
  }
}
const pushTraceEvent = (event: WorkspaceStreamEvent) => {
  const nextRecord = buildTraceRecord(event)
  const lastRecord = executionEvents.value[executionEvents.value.length - 1]
  if (lastRecord && lastRecord.title === nextRecord.title && lastRecord.detail === nextRecord.detail) return
  executionEvents.value.push(nextRecord)
  if (executionEvents.value.length > 24) executionEvents.value.splice(0, executionEvents.value.length - 24)
}

const parseCreatedToolId = (text: string) => {
  const matched = text.match(/\(tool_id=([^)]+)\)/)
  return matched?.[1] || ''
}

const refreshToolSelectionsAfterCreation = async (event: WorkspaceStreamEvent) => {
  const data = event.data || {}
  const toolName = String(data.tool_name || '')
  if (event.type !== 'tool_result' || data.ok === false) return
  if (!['create_remote_api_tool', 'create_cli_tool'].includes(toolName)) return
  if (!canPickTools.value) return
  await fetchPlugins()
  const createdToolId = parseCreatedToolId(String(data.result || data.message || ''))
  if (createdToolId && !selectedTools.value.includes(createdToolId)) selectedTools.value.push(createdToolId)
  ElMessage.success(toolName === 'create_remote_api_tool' ? 'API 工具已创建并刷新到当前工具列表。' : 'CLI 工具已创建并刷新到当前工具列表。')
}

const buildLiveAssistantProgress = () => {
  const summary = [
    `**${progressHeadline.value || '正在处理中'}**`,
    progressDetail.value || `${activeExecutionMode.value?.label || selectedExecutionMode.value} / ${activeAccessScope.value?.label || selectedAccessScope.value} / ${effectiveRetrievalModeLabel.value}`,
    '',
    ...progressSteps.value.map((step) => `- ${step.done ? 'x' : step.active ? '>' : '-'} ${step.label}`),
  ]
  if (liveProgressEvents.value.length > 0) {
    summary.push('', '最近进展')
    liveProgressEvents.value.forEach((event) => {
      summary.push(`- ${event.title}${event.detail ? `: ${event.detail}` : ''}`)
    })
  }
  return summary.join('\n')
}

const buildFallbackAssistantMessage = () => [...executionEvents.value].reverse().find((event) => event.detail || event.title)?.detail || [...executionEvents.value].reverse().find((event) => event.detail || event.title)?.title || '这次请求没有返回可见内容，请稍后重试。'
const applySlashSuggestion = (suggestion: SlashSuggestion) => {
  inputMessage.value = suggestion.insertValue
  activeSuggestionIndex.value = 0
}

const waitForRetry = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms))

const ensureInitialRouteDependencies = async () => {
  const initialMessage = safeQueryValue(route.query.message, '').trim()
  if (!initialMessage)
    return true

  let attempt = 0
  while (attempt < 4) {
    attempt += 1

    if (!selectedModelId.value) {
      await fetchModels()
    }
    if (executionModes.value.length === 0 || accessScopes.value.length === 0) {
      await fetchExecutionConfig()
    }
    if (mcpServers.value.length === 0) {
      await fetchMcpServers()
    }

    const ready = Boolean(selectedModelId.value)
      && executionModes.value.length > 0
      && accessScopes.value.length > 0
      && mcpServers.value.length > 0
    if (ready)
      return true

    await waitForRetry(300 * attempt)
  }

  return false
}

const consumeInitialRouteMessage = async () => {
  const initialMessage = safeQueryValue(route.query.message, '').trim()
  if (!initialMessage || isGenerating.value)
    return

  const dependenciesReady = await ensureInitialRouteDependencies()
  if (!dependenciesReady || !selectedModelId.value)
    return

  const routeSessionId = safeQueryValue(route.query.session_id, 'new')
  const messageKey = `${routeSessionId}|${selectedMode.value}|${initialMessage}`
  if (consumedInitialMessageKey.value === messageKey)
    return
  if (initialRouteMessageInFlightKey.value === messageKey)
    return

  initialRouteMessageInFlightKey.value = messageKey
  try {
    inputMessage.value = initialMessage
    const submitted = await submitMessage()
    if (!submitted) return
    consumedInitialMessageKey.value = messageKey
    inputMessage.value = ''
  } finally {
    if (initialRouteMessageInFlightKey.value === messageKey) {
      initialRouteMessageInFlightKey.value = ''
    }
  }
}

const fetchModels = async () => {
  modelsLoading.value = true
  try {
    const response = await getVisibleLLMsAPI()
    if (response.data?.status_code !== 200) return
    const grouped = response.data.data || {}
    const list: LLMResponse[] = []
    Object.values(grouped).forEach((items: any) => Array.isArray(items) && list.push(...items))
    modelOptions.value = list.filter((item) => (item.llm_type || '').toUpperCase() === 'LLM')
    if (!selectedModelId.value && modelOptions.value.length > 0) selectedModelId.value = modelOptions.value[0].llm_id
  } catch (error) { console.error('获取模型失败', error) } finally { modelsLoading.value = false }
}

const fetchExecutionConfig = async () => {
  try {
    const response = await getWorkspaceExecutionModesAPI()
    if (response.data.status_code !== 200) return
    const config = (response.data.data || {}) as WorkspaceExecutionConfig
    executionModes.value = config.execution_modes || []
    accessScopes.value = config.access_scopes || []
  } catch (error) { console.error('获取执行配置失败', error) }
}

const fetchPlugins = async () => {
  if (!canPickTools.value) { plugins.value = []; selectedTools.value = []; return }
  try {
    const response = await getWorkspacePluginsByModeAPI(selectedExecutionMode.value, selectedAccessScope.value)
    if (response.data.status_code !== 200) return
    plugins.value = response.data.data || []
    syncDefaultSelections()
  } catch (error) { console.error('获取工具失败', error) }
}

const fetchMcpServers = async () => {
  try {
    const { getMCPServersAPI } = await import('../../../apis/mcp-server')
    const response = await getMCPServersAPI()
    if (response.data?.status_code === 200 && Array.isArray(response.data.data)) {
      mcpServers.value = response.data.data
      syncDefaultSelections()
    }
  } catch (error) { console.error('获取 MCP 失败', error) }
}

const fetchSkills = async () => {
  if (!canPickTools.value) { skillOptions.value = []; selectedSkillIds.value = []; return }
  try {
    const response = await getAgentSkillsAPI()
    if (response.data?.status_code !== 200 || !Array.isArray(response.data.data)) return
    skillOptions.value = response.data.data
    syncDefaultSelections()
  } catch (error) { console.error('获取 Skill 失败', error) }
}

const fetchKnowledges = async () => {
  if (!canPickTools.value) { knowledgeOptions.value = []; selectedKnowledgeIds.value = []; return }
  try {
    const response = await getKnowledgeListAPI()
    if (response.data?.status_code !== 200 || !Array.isArray(response.data.data)) return
    knowledgeOptions.value = response.data.data
    syncDefaultSelections()
  } catch (error) { console.error('获取知识库失败', error) }
}

const loadSessionHistory = async (sessionId: string) => {
  try {
    clearConversationState()
    const response = await getWorkspaceSessionInfoAPI(sessionId)
    if (response.data.status_code !== 200) return
    const session = response.data.data
    if (!session?.contexts || !Array.isArray(session.contexts)) return
    const contexts = sanitizeWorkspaceContexts(session.contexts)
    messages.value = contexts.map((context: any) => [{ role: 'user' as const, content: context.query || '' }, { role: 'assistant' as const, content: context.answer || '' }]).flat().filter((message: ChatMessage) => message.content)
    executionEvents.value = []
    await scrollToBottom(true)
  } catch (error) { console.error('加载会话历史失败', error); ElMessage.error('加载会话历史失败') }
}

const syncDefaultSelections = () => {
  if (!isAgentMode.value || !canPickTools.value) return

  const defaults = loadWorkspaceDefaults()
  const hasSavedDefaults = Boolean(defaults.updatedAt)
  const availableToolIds = plugins.value.map((item: any) => item.id || item.tool_id).filter(Boolean)
  const availableMcpIds = mcpServers.value.map((item: any) => item.mcp_server_id).filter(Boolean)
  const availableSkillIds = skillOptions.value.map((item) => item.id).filter(Boolean)
  const availableKnowledgeIds = knowledgeOptions.value.map((item) => item.id).filter(Boolean)

  if (hasSavedDefaults) {
    selectedTools.value = defaults.toolIds.filter((toolId) => availableToolIds.includes(toolId))
    selectedMcpServers.value = defaults.mcpServerIds.filter((serverId) => availableMcpIds.includes(serverId))
    selectedSkillIds.value = defaults.skillIds.filter((skillId) => availableSkillIds.includes(skillId))
    selectedKnowledgeIds.value = defaults.knowledgeIds
      .filter((knowledgeId) => availableKnowledgeIds.includes(knowledgeId))
      .slice(0, 1)
    toolsTouched.value = true
    mcpTouched.value = true
    skillsTouched.value = true
    knowledgeTouched.value = true
    return
  }

  if (!toolsTouched.value) {
    selectedTools.value = [...availableToolIds]
  } else {
    selectedTools.value = selectedTools.value.filter((toolId) => availableToolIds.includes(toolId))
  }

  if (!mcpTouched.value) {
    selectedMcpServers.value = [...availableMcpIds]
  } else {
    selectedMcpServers.value = selectedMcpServers.value.filter((serverId) => availableMcpIds.includes(serverId))
  }

  if (!skillsTouched.value) {
    selectedSkillIds.value = []
  } else {
    selectedSkillIds.value = selectedSkillIds.value.filter((skillId) => availableSkillIds.includes(skillId))
  }

  if (!knowledgeTouched.value) {
    selectedKnowledgeIds.value = []
  } else {
    selectedKnowledgeIds.value = selectedKnowledgeIds.value
      .filter((knowledgeId) => availableKnowledgeIds.includes(knowledgeId))
      .slice(0, 1)
  }
}

const applySavedWorkspaceDefaults = () => {
  const defaults = loadWorkspaceDefaults()
  if (!defaults.updatedAt) return

  if (!route.query.mode) {
    selectedMode.value = defaults.mode
  }

  if (defaults.modelId && modelOptions.value.some((model) => model.llm_id === defaults.modelId)) {
    selectedModelId.value = defaults.modelId
  }
  if (defaults.executionMode && executionModes.value.some((mode) => mode.id === defaults.executionMode)) {
    selectedExecutionMode.value = defaults.executionMode
  }
  if (defaults.accessScope && accessScopes.value.some((scope) => scope.id === defaults.accessScope)) {
    selectedAccessScope.value = defaults.accessScope
  }

  syncDefaultSelections()
}

const toggleTool = (toolId: string) => {
  toolsTouched.value = true
  const index = selectedTools.value.indexOf(toolId)
  index >= 0 ? selectedTools.value.splice(index, 1) : selectedTools.value.push(toolId)
}

const toggleMcp = (serverId: string) => {
  mcpTouched.value = true
  const index = selectedMcpServers.value.indexOf(serverId)
  index >= 0 ? selectedMcpServers.value.splice(index, 1) : selectedMcpServers.value.push(serverId)
}

const toggleSkill = (skillId: string) => {
  skillsTouched.value = true
  const index = selectedSkillIds.value.indexOf(skillId)
  index >= 0 ? selectedSkillIds.value.splice(index, 1) : selectedSkillIds.value.push(skillId)
}

const toggleKnowledge = (knowledgeId: string) => {
  knowledgeTouched.value = true
  selectedKnowledgeIds.value = selectedKnowledgeIds.value[0] === knowledgeId ? [] : [knowledgeId]
}

const getValidSelectedToolIds = () => {
  const availableToolIds = new Set(plugins.value.map((item: any) => item.id || item.tool_id).filter(Boolean))
  return selectedTools.value.filter((toolId) => availableToolIds.has(toolId))
}

const getValidSelectedMcpIds = () => {
  const availableMcpIds = new Set(mcpServers.value.map((item: any) => item.mcp_server_id).filter(Boolean))
  return selectedMcpServers.value.filter((serverId) => availableMcpIds.has(serverId))
}

const getValidAutoMcpIds = () => {
  const availableMcpIds = new Set(mcpServers.value.map((item: any) => item.mcp_server_id).filter(Boolean))
  return autoAvailableMcpIds.value.filter((serverId) => availableMcpIds.has(serverId))
}

const getValidSelectedSkillIds = () => {
  const availableSkillIds = new Set(skillOptions.value.map((item) => item.id).filter(Boolean))
  return selectedSkillIds.value.filter((skillId) => availableSkillIds.has(skillId))
}

const getValidSelectedKnowledgeIds = () => {
  const availableKnowledgeIds = new Set(knowledgeOptions.value.map((item) => item.id).filter(Boolean))
  return selectedKnowledgeIds.value.filter((knowledgeId) => availableKnowledgeIds.has(knowledgeId)).slice(0, 1)
}

const classifySelectedFile = (file: File) => {
  const extension = getFileExtension(file.name)
  if (file.type.startsWith('image/') || CHAT_IMAGE_EXTENSIONS.has(extension)) return 'image'
  if (AGENT_DOCUMENT_EXTENSIONS.has(extension)) return 'document'
  return 'unsupported'
}

const validateSelectedFile = (file: File) => {
  if (file.size > MAX_ATTACHMENT_SIZE) return `文件 ${file.name} 超过 20MB，无法上传。`
  const kind = classifySelectedFile(file)
  if (kind === 'unsupported') return `文件 ${file.name} 暂不支持。支持类型：图片、PDF、Word、PPT、TXT、Markdown、Excel。`
  if (!isAgentMode.value && kind !== 'image') return `聊天模式仅支持图片，请切换到 Agent 模式后再分析 ${file.name}。`
  return ''
}

const resetAttachmentInput = () => { if (attachmentInputRef.value) attachmentInputRef.value.value = '' }
const triggerAttachmentSelect = () => { if (!attachmentsUploading.value && !isGenerating.value) attachmentInputRef.value?.click() }
const revokeAttachmentPreview = (attachment: PendingAttachment) => {
  if (attachment.preview_url && attachment.preview_url.startsWith('blob:')) {
    URL.revokeObjectURL(attachment.preview_url)
  }
}

const removeAttachment = (attachmentId: string) => {
  const target = pendingAttachments.value.find((item) => item.id === attachmentId)
  if (target) revokeAttachmentPreview(target)
  pendingAttachments.value = pendingAttachments.value.filter((item) => item.id !== attachmentId)
}
const isImageAttachment = (attachment: PendingAttachment) => attachment.mime_type?.startsWith('image/')
const formatAttachmentSize = (size = 0) => {
  if (size < 1024 * 1024) return `${Math.max(1, Math.round(size / 1024))} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
}

const normalizeClipboardFile = (file: File, index: number) => {
  if (file.name && file.name.trim()) return file
  const extension = file.type.split('/')[1] || 'png'
  return new File([file], `clipboard-image-${Date.now()}-${index}.${extension}`, { type: file.type || 'image/png' })
}

const uploadAttachments = async (rawFiles: File[]) => {
  const files = rawFiles.map((file, index) => normalizeClipboardFile(file, index))
  if (files.length === 0) return
  if (pendingAttachments.value.length + files.length > MAX_ATTACHMENTS) { ElMessage.warning(`最多只能添加 ${MAX_ATTACHMENTS} 个附件。`); resetAttachmentInput(); return }
  for (const file of files) { const err = validateSelectedFile(file); if (err) { ElMessage.warning(err); resetAttachmentInput(); return } }
  attachmentsUploading.value = true
  try {
    for (const file of files) {
      const localPreviewUrl = file.type.startsWith('image/') ? URL.createObjectURL(file) : ''
      const response = await uploadFile(file)
      pendingAttachments.value.push({
        id: crypto.randomUUID(),
        name: file.name,
        url: response.data,
        preview_url: localPreviewUrl || response.data,
        mime_type: file.type,
        size: file.size,
      })
    }
    ElMessage.success(files.length === 1 ? '附件已添加。' : `已添加 ${files.length} 个附件。`)
  } catch (error) { console.error('附件上传失败', error); ElMessage.error('附件上传失败，请稍后重试') } finally { attachmentsUploading.value = false; resetAttachmentInput() }
}

const handleComposerPaste = async (event: ClipboardEvent) => {
  const files = Array.from(event.clipboardData?.items || [])
    .filter((item) => item.kind === 'file')
    .map((item) => item.getAsFile())
    .filter((file): file is File => !!file)
  if (files.length === 0) return
  event.preventDefault()
  if (attachmentsUploading.value || isGenerating.value) { ElMessage.warning('请等待当前任务结束后再粘贴附件。'); return }
  await uploadAttachments(files)
}

const handleAttachmentChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files || [])
  if (files.length === 0) return
  await uploadAttachments(files)
}

const handleAttachmentDragOver = (event: DragEvent) => {
  if (!event.dataTransfer?.types?.includes('Files')) return
  event.preventDefault()
  if (!attachmentsUploading.value && !isGenerating.value) isAttachmentDragOver.value = true
}

const handleAttachmentDragLeave = (event: DragEvent) => {
  const currentTarget = event.currentTarget as HTMLElement | null
  const nextTarget = event.relatedTarget as Node | null
  if (currentTarget && nextTarget && currentTarget.contains(nextTarget)) return
  isAttachmentDragOver.value = false
}

const handleAttachmentDrop = async (event: DragEvent) => {
  if (!event.dataTransfer?.files?.length) return
  event.preventDefault()
  isAttachmentDragOver.value = false
  if (attachmentsUploading.value || isGenerating.value) return
  await uploadAttachments(Array.from(event.dataTransfer.files))
}

const buildPayload = (query: string): WorkSpaceSimpleTask => ({
  query,
  model_id: selectedModelId.value,
  workspace_mode: selectedMode.value,
  web_search: ALWAYS_WEB_SEARCH,
  plugins: canPickTools.value ? getValidSelectedToolIds() : [],
  mcp_servers: canPickTools.value ? getValidSelectedMcpIds() : getValidAutoMcpIds(),
  knowledge_ids: canPickTools.value ? getValidSelectedKnowledgeIds() : [],
  retrieval_mode: canPickTools.value ? effectiveRetrievalMode.value : 'rag',
  agent_skill_ids: canPickTools.value ? getValidSelectedSkillIds() : [],
  session_id: currentSessionId.value,
  execution_mode: isAgentMode.value ? selectedExecutionMode.value : 'tool',
  access_scope: isAgentMode.value ? selectedAccessScope.value : 'workspace',
  desktop_bridge_url: isDesktopRuntime() ? window.__ZUNO_DESKTOP__?.bridgeUrl || '' : '',
  desktop_bridge_token: isDesktopRuntime() ? window.__ZUNO_DESKTOP__?.bridgeToken || '' : '',
  attachments: pendingAttachments.value.map(({ id: _id, preview_url: _previewUrl, ...attachment }) => attachment),
})

const submitMessage = async () => {
  const query = inputMessage.value.trim() || (pendingAttachments.value.length > 0 ? '请分析我上传的附件。' : '')
  if (!query) { ElMessage.warning('请输入内容。'); return false }
  if (isGenerating.value) { ElMessage.warning('请等待当前回复完成。'); return false }
  if (!selectedModelId.value) {
    await fetchModels()
  }
  if (!selectedModelId.value) { ElMessage.warning('请先选择模型'); return false }
  if (!currentSessionId.value) {
    try {
      await createPersistedSession(selectedMode.value)
    } catch (error) {
      console.error('补建会话失败', error)
      ElMessage.error('新建会话失败')
      return false
    }
  }
  await syncRouteState()
  inputMessage.value = ''
  isGenerating.value = true
  executionEvents.value = []
  showTracePanel.value = false
  const attachmentsForRequest = [...pendingAttachments.value]
  pendingAttachments.value = []
  const attachmentSummary = attachmentsForRequest.length ? `\n\n已附加 ${attachmentsForRequest.length} 个文件：${attachmentsForRequest.map((item) => item.name).join('，')}` : ''
  messages.value.push({ role: 'user', content: `${query}${attachmentSummary}`.trim() })
  const assistantIndex = messages.value.length
  messages.value.push({ role: 'assistant', content: isAgentMode.value ? buildLiveAssistantProgress() : '' })
  isPinnedToBottom.value = true
  await scrollToBottom(true)
  if (isAgentMode.value) executionEvents.value.push({ id: crypto.randomUUID(), title: '开始执行', detail: `${activeExecutionMode.value?.label || selectedExecutionMode.value} / ${activeAccessScope.value?.label || selectedAccessScope.value} / ${effectiveRetrievalModeLabel.value}`, at: new Date().toLocaleTimeString(), phase: 'start', status: 'START', accent: 'default' })
  let assistantHasRealContent = false
  const renderAgentProgress = async () => {
    if (!isAgentMode.value || assistantHasRealContent || !messages.value[assistantIndex]) return
    messages.value[assistantIndex].content = buildLiveAssistantProgress()
    await scrollToBottom()
  }
  const applyFallback = () => {
    if (messages.value[assistantIndex] && !assistantHasRealContent) messages.value[assistantIndex].content = buildFallbackAssistantMessage()
  }
  try {
    const payload = buildPayload(query)
    payload.attachments = attachmentsForRequest.map(({ id: _id, preview_url: _previewUrl, ...attachment }) => attachment)
    await workspaceSimpleChatStreamAPI(payload, {
      onMessage: async (chunk) => {
        const safeChunk = sanitizeAssistantChunk(chunk)
        if (!safeChunk) return
        if (!assistantHasRealContent) {
          messages.value[assistantIndex].content = ''
          assistantHasRealContent = true
        }
        messages.value[assistantIndex].content += safeChunk
        await scrollToBottom()
      },
      onFinalMessage: async (message) => {
        const safeMessage = sanitizeAssistantChunk(message)
        if (!safeMessage || !messages.value[assistantIndex]) return
        messages.value[assistantIndex].content = safeMessage
        assistantHasRealContent = true
        await scrollToBottom()
      },
      onEvent: async (event) => {
        if (!isAgentMode.value) return
        pushTraceEvent(event)
        await refreshToolSelectionsAfterCreation(event)
        await renderAgentProgress()
      },
      onError: (error) => { console.error('对话失败', error); pendingAttachments.value = attachmentsForRequest; applyFallback(); ElMessage.error('对话失败，请稍后重试'); isGenerating.value = false },
      onClose: () => {
        attachmentsForRequest.forEach(revokeAttachmentPreview)
        applyFallback()
        isGenerating.value = false
        emitSessionUpdated()
      },
    })
    return true
  } catch (error) {
    console.error('对话异常', error)
    pendingAttachments.value = attachmentsForRequest
    applyFallback()
    ElMessage.error('对话异常')
    isGenerating.value = false
    return false
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  if (slashSuggestions.value.length > 0) {
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      activeSuggestionIndex.value = (activeSuggestionIndex.value + 1) % slashSuggestions.value.length
      return
    }
    if (event.key === 'ArrowUp') {
      event.preventDefault()
      activeSuggestionIndex.value = (activeSuggestionIndex.value - 1 + slashSuggestions.value.length) % slashSuggestions.value.length
      return
    }
    if (event.key === 'Tab') {
      event.preventDefault()
      applySlashSuggestion(slashSuggestions.value[activeSuggestionIndex.value])
      return
    }
    if (event.key === 'Enter' && !event.shiftKey) {
      const trimmed = (inputMessage.value || '').trim()
      if (trimmed.startsWith('/')) {
        event.preventDefault()
        applySlashSuggestion(slashSuggestions.value[activeSuggestionIndex.value])
        return
      }
    }
  }

  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    if (!isGenerating.value) void submitMessage()
  }
}

watch(slashSuggestions, (nextSuggestions) => {
  if (!nextSuggestions.length) {
    activeSuggestionIndex.value = 0
    return
  }
  if (activeSuggestionIndex.value >= nextSuggestions.length) activeSuggestionIndex.value = 0
})

watch(selectedModelId, async (newModelId, oldModelId) => {
  if (!newModelId || newModelId === oldModelId) return
  await consumeInitialRouteMessage()
})

watch(() => route.query.session_id, async (newSessionId, oldSessionId) => {
  if (newSessionId && newSessionId !== oldSessionId) {
    clearConversationState()
    currentSessionId.value = String(newSessionId)
    selectedMode.value = safeQueryValue(route.query.mode, selectedMode.value) === 'agent' ? 'agent' : 'normal'
    toolsTouched.value = false
    mcpTouched.value = false
    skillsTouched.value = false
    knowledgeTouched.value = false
    selectedTools.value = []
    selectedMcpServers.value = []
    selectedSkillIds.value = []
    selectedKnowledgeIds.value = []
    await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
    syncDefaultSelections()
    await loadSessionHistory(String(newSessionId))
    await nextTick()
    await consumeInitialRouteMessage()
    return
  }
  if (!newSessionId && oldSessionId) {
    try {
      await resetToDraftSession(selectedMode.value, { pruneCurrent: false })
    } catch (error) {
      console.error('补建会话失败', error)
      ElMessage.error('新建会话失败')
    }
  }
})

watch(() => route.query.message, async (newMessage, oldMessage) => {
  if (!newMessage || newMessage === oldMessage)
    return

  await nextTick()
  await consumeInitialRouteMessage()
})

watch([selectedExecutionMode, selectedAccessScope, selectedMode], async () => {
  if (!isAgentMode.value) {
    plugins.value = []
    selectedTools.value = []
    selectedMcpServers.value = []
    skillOptions.value = []
    selectedSkillIds.value = []
    knowledgeOptions.value = []
    selectedKnowledgeIds.value = []
    toolsTouched.value = false
    mcpTouched.value = false
    skillsTouched.value = false
    knowledgeTouched.value = false
    showTracePanel.value = false
  }
  await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
  syncDefaultSelections()
})

watch(selectedMode, async (newMode, oldMode) => {
  if (!workspaceHydrated.value || newMode === oldMode) return
  try {
    if (currentSessionId.value) {
      saveWorkspaceSessionMode(currentSessionId.value, newMode)
      emitSessionModeUpdated()
    }
    await syncRouteState()
  } catch (error) {
    console.error('切换模式失败', error)
    ElMessage.error('切换模式失败')
  }
})

onMounted(async () => {
  window.addEventListener('workspace-new-conversation', handleNewConversationRequest)
  await Promise.all([fetchExecutionConfig(), fetchModels(), fetchMcpServers()])
  const savedDefaults = loadWorkspaceDefaults()
  selectedMode.value = safeQueryValue(route.query.mode, savedDefaults.mode || 'normal') === 'agent' ? 'agent' : 'normal'
  selectedExecutionMode.value = safeQueryValue(route.query.execution_mode, savedDefaults.executionMode || 'tool')
  selectedAccessScope.value = safeQueryValue(route.query.access_scope, savedDefaults.accessScope || 'workspace')
  selectedExecutionMode.value = executionModes.value.some((item) => item.id === selectedExecutionMode.value) ? selectedExecutionMode.value : 'tool'
  selectedAccessScope.value = accessScopes.value.some((item) => item.id === selectedAccessScope.value) ? selectedAccessScope.value : 'workspace'
  if (savedDefaults.modelId && modelOptions.value.some((model) => model.llm_id === savedDefaults.modelId)) selectedModelId.value = savedDefaults.modelId
  await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
  applySavedWorkspaceDefaults()
  const sessionId = safeQueryValue(route.query.session_id, '')
  if (sessionId) {
    currentSessionId.value = sessionId
    await loadSessionHistory(sessionId)
  } else {
    currentSessionId.value = ''
  }
  await nextTick()
  await consumeInitialRouteMessage()
  workspaceHydrated.value = true
})

onBeforeUnmount(() => {
  window.removeEventListener('workspace-new-conversation', handleNewConversationRequest)
})
</script>

<template>
  <div class="workspace-chat" :class="{ active: messages.length > 0 }">
    <div class="workspace-shell">
      <div v-if="messages.length === 0" class="intro-stack">
        <div class="intro-mark">Zuno Workspace</div>
        <h1>{{ selectedMode === 'agent' ? '把任务交给 Zuno。' : '今天想聊什么？' }}</h1>
        <p>{{ activeMode.description }}</p>
        <div class="mode-switcher">
          <button v-for="mode in modes" :key="mode.id" :class="['mode-pill', { active: selectedMode === mode.id }]" :disabled="isGenerating" @click="selectedMode = mode.id">
            {{ mode.label }}
          </button>
        </div>
      </div>
      <div v-if="messages.length > 0" ref="conversationRef" class="conversation-panel" @scroll="handleConversationScroll">
        <div v-for="(message, index) in messages" :key="index" class="message-row" :class="message.role">
                  <img v-if="message.role === 'assistant'" :src="zunoAgentAvatar" alt="Zuno" class="avatar" />
          <div class="message-bubble" :class="{ assistant: message.role === 'assistant', loading: message.role === 'assistant' && !message.content && isGenerating && index === messages.length - 1 }">
            <div v-if="message.role === 'assistant' && !message.content && isGenerating && index === messages.length - 1" class="loading-row" :class="{ agent: isAgentMode }">
              <template v-if="isAgentMode">
                <div class="loading-head">
                  <span class="spinner orbit"></span>
                  <div class="loading-copy">
                    <strong>{{ progressHeadline }}</strong>
                    <span>{{ progressDetail }}</span>
                  </div>
                  <div class="phase-pill-group">
                    <span class="phase-pill strong">{{ effectiveRetrievalModeLabel }}</span>
                    <span class="phase-pill">{{ selectedKnowledgeIds.length > 0 ? `${selectedKnowledgeIds.length} 个知识库` : '未选知识库' }}</span>
                  </div>
                </div>
                <div class="loading-steps">
                  <div v-for="step in progressSteps" :key="step.key" class="loading-step" :class="{ active: step.active, done: step.done }">
                    <span class="progress-dot"></span>
                    <span>{{ step.label }}</span>
                  </div>
                </div>
                <div v-if="liveProgressEvents.length > 0" class="loading-events">
                  <div v-for="event in liveProgressEvents" :key="event.id" class="loading-event" :class="event.accent || 'default'">
                    <strong>{{ event.title }}</strong>
                    <span v-if="event.detail">{{ event.detail }}</span>
                  </div>
                </div>
              </template>
              <template v-else>
                <span class="spinner"></span>
                <span>Zuno 正在回复...</span>
              </template>
            </div>
            <MdPreview v-else-if="message.content" :editorId="`workspace-message-${index}`" :modelValue="message.content" />
          </div>
          <img v-if="message.role === 'user'" :src="userStore.userInfo?.avatar || '/src/assets/user.svg'" alt="User" class="avatar" @error="handleAvatarError" />
        </div>
      </div>
      <div class="composer-dock" :class="{ fixed: messages.length > 0 }">
        <div class="composer-shell" :class="{ 'drag-active': isAttachmentDragOver }" @dragover.prevent="handleAttachmentDragOver" @dragleave="handleAttachmentDragLeave" @drop.prevent="handleAttachmentDrop">
          <div class="composer-top" :class="{ compact: compactPanel }">
            <div v-if="!compactPanel" class="mode-badge"><span class="label">当前模式</span><strong>{{ activeMode.label }}</strong></div>
            <div class="composer-actions">
              <button v-if="isAgentMode && compactPanel" class="ghost-pill subtle" type="button" @click="showTracePanel = !showTracePanel"><el-icon><ArrowDown v-if="showTracePanel" /><ArrowUp v-else /></el-icon>{{ showTracePanel ? '收起进展' : '查看进展' }}</button>
              <button class="ghost-pill subtle" type="button" @click="window.dispatchEvent(new CustomEvent('workspace-open-settings', { detail: { section: 'model' } }))">设置</button>
            </div>
          </div>

          <div v-if="traceVisible" class="trace-card" :class="{ generating: isGenerating }">
            <div v-if="isGenerating" class="progress-inline">
              <div class="progress-head">
                <div class="trace-head-copy">
                  <strong>{{ progressHeadline }}</strong>
                  <small>{{ progressDetail }}</small>
                </div>
                <div class="phase-pill-group">
                  <span class="progress-badge">处理中</span>
                  <span class="phase-pill strong">{{ effectiveRetrievalModeLabel }}</span>
                </div>
              </div>
              <div class="progress-steps">
                <div v-for="step in progressSteps" :key="step.key" class="progress-step" :class="{ active: step.active, done: step.done }">
                  <span class="progress-dot"></span>
                  <span>{{ step.label }}</span>
                </div>
              </div>
            </div>
            <div class="picker-head"><div class="trace-head-copy"><strong>执行进展</strong><small>{{ selectedToolCount > 0 ? `已启用 ${selectedToolCount} 项能力` : '未启用额外工具' }}</small></div></div>
            <div v-if="executionEvents.length === 0" class="empty-copy">正在等待新的执行事件...</div>
            <div v-else class="trace-list">
              <div v-for="event in executionEvents" :key="event.id" class="trace-item" :class="event.accent || 'default'">
                <div class="trace-head">
                  <strong>{{ event.title }}</strong>
                  <span>{{ event.at }}</span>
                </div>
                <div v-if="event.detail" class="trace-detail">{{ event.detail }}</div>
                <div v-if="event.retrieval" class="retrieval-trace">
                  <div class="retrieval-meta">
                    <span class="trace-pill strong">首轮 {{ getRetrievalModeLabel(event.retrieval.firstMode) }}</span>
                    <span class="trace-pill strong">最终 {{ getRetrievalModeLabel(event.retrieval.finalMode) }}</span>
                    <span class="trace-pill">{{ event.retrieval.roundCount }} 轮</span>
                    <span v-if="event.retrieval.rewrittenQueryUsed" class="trace-pill">改写重试</span>
                  </div>
                  <div v-if="event.retrieval.fallbackReason" class="trace-reason">
                    补检原因：{{ event.retrieval.fallbackReason }}
                  </div>
                  <div v-if="event.retrieval.rounds.length > 0" class="trace-round-list">
                    <div v-for="round in event.retrieval.rounds" :key="`${event.id}-${round.round}`" class="trace-round-item">
                      <div class="trace-round-head">
                        <strong>第 {{ round.round }} 轮</strong>
                        <span>{{ getRetrievalModeLabel(round.mode) }}</span>
                      </div>
                      <div class="trace-round-body">
                        <span>{{ getRetrievalTriggerLabel(round.trigger || '') }}</span>
                        <span v-if="round.qualityReason">{{ getQualityReasonLabel(round.qualityReason) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="pendingAttachments.length > 0" class="attachment-strip">
            <div v-for="attachment in pendingAttachments" :key="attachment.id" class="attachment-chip" :class="{ image: isImageAttachment(attachment) }">
              <img v-if="isImageAttachment(attachment)" :src="attachment.preview_url || attachment.url" :alt="attachment.name" class="attachment-thumb" />
              <div class="attachment-copy">
                <span class="attachment-name">{{ attachment.name }}</span>
                <span class="attachment-size">{{ formatAttachmentSize(attachment.size) }}</span>
              </div>
              <button type="button" class="attachment-remove" @click="removeAttachment(attachment.id)">×</button>
            </div>
          </div>
          <div v-if="isAttachmentDragOver" class="drop-hint">松开即可添加附件</div>
          <input ref="attachmentInputRef" class="attachment-input" type="file" multiple :accept="attachmentAccept" @change="handleAttachmentChange" />
          <textarea v-model="inputMessage" class="composer" :rows="compactPanel ? 1 : 2" :placeholder="composerPlaceholder" @keydown="handleKeydown" @paste="handleComposerPaste" />
          <div v-if="slashSuggestions.length > 0" class="slash-suggestions">
            <button
              v-for="(suggestion, index) in slashSuggestions"
              :key="suggestion.key"
              type="button"
              class="slash-suggestion"
              :class="{ active: index === activeSuggestionIndex }"
              @click="applySlashSuggestion(suggestion)"
            >
              <span class="slash-label">{{ suggestion.label }}</span>
              <span class="slash-detail">{{ suggestion.detail }}</span>
            </button>
          </div>
          <div class="composer-footer">
            <div class="composer-footer-left">
              <button class="attach-btn" type="button" :disabled="attachmentsUploading || isGenerating" @click="triggerAttachmentSelect"><el-icon><Plus /></el-icon><span>{{ attachmentsUploading ? '上传中...' : '添加附件' }}</span></button>
              <button v-if="isAgentMode && canPickTools" class="attach-btn tool-create-btn" type="button" :disabled="attachmentsUploading || isGenerating" @click="openToolCreationPrompt('general')"><el-icon><Plus /></el-icon><span>新增工具</span></button>
              <div class="composer-meta"><span class="composer-hint">{{ modeFooterCopy }}</span><span class="attachment-hint">{{ attachmentHint }}</span><span v-if="isAgentMode && canPickTools" class="retrieval-hint">检索：{{ effectiveRetrievalModeLabel }}</span></div>
            </div>
            <button class="send-btn" :disabled="isGenerating || attachmentsUploading" @click="submitMessage">{{ isGenerating ? '处理中...' : '发送' }}</button>
          </div>
      </div>
    </div>
  </div>
</div>
</template>

<style scoped>
.workspace-chat {
  flex: 1;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background:
    radial-gradient(circle at 50% 12%, rgba(214, 142, 79, 0.08), transparent 30%),
    linear-gradient(180deg, #f8f4ed 0%, #fcfaf6 100%);
}

.workspace-shell {
  flex: 1;
  height: 100%;
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 18px 20px 10px;
  overflow: hidden;
}

.workspace-chat:not(.active) .workspace-shell {
  justify-content: center;
}

.workspace-chat:not(.active) .composer-dock {
  background: transparent;
}

.workspace-chat:not(.active) .composer-shell {
  width: min(760px, calc(100% - 24px));
}

.intro-stack {
  flex: 0 0 auto;
  min-height: 0;
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 16px;
  padding: 0 0 6px;
  text-align: center;
}

.intro-mark {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 13px;
  border-radius: 999px;
  background: rgba(207, 128, 70, 0.1);
  color: #a76234;
  font-size: 12px;
  letter-spacing: 0.08em;
}

.intro-stack h1 {
  margin: 0;
  color: #302820;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(34px, 4vw, 56px);
  font-weight: 400;
  line-height: 1.08;
  letter-spacing: -0.05em;
}

.intro-stack p {
  margin: 0;
  max-width: 540px;
  color: #76685b;
  font-size: 15px;
  line-height: 1.65;
}

.mode-switcher {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.mode-pill {
  border: 1px solid rgba(220, 198, 176, 0.8);
  background: rgba(255, 251, 246, 0.85);
  color: #7f654d;
  border-radius: 999px;
  padding: 8px 16px;
  cursor: pointer;
}

.mode-pill.active {
  background: linear-gradient(135deg, #d58a4d 0%, #bc6733 100%);
  border-color: transparent;
  color: #fff;
}

.conversation-panel {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 0 0 10px;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.message-row.user {
  justify-content: flex-end;
}

.avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  flex: 0 0 auto;
}

.message-bubble {
  max-width: min(820px, 76vw);
  padding: 8px 10px;
  border-radius: 14px;
  background: linear-gradient(135deg, #d48a4f 0%, #bb6631 100%);
  color: #fff;
}

.message-bubble.assistant {
  background: rgba(255, 252, 248, 0.9);
  color: #2f241b;
  border: 1px solid rgba(229, 211, 194, 0.7);
}

.message-bubble.assistant.loading {
  min-width: 320px;
}

.loading-row {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #7b654f;
  font-size: 13px;
  min-height: 44px;
  width: 100%;
}

.loading-row.agent {
  display: grid;
  gap: 10px;
  align-items: stretch;
  min-height: 0;
}

.loading-head {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.phase-pill-group {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.phase-pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 9px;
  border-radius: 999px;
  background: rgba(255, 250, 245, 0.92);
  border: 1px solid rgba(227, 205, 184, 0.9);
  color: #866246;
  font-size: 11px;
  white-space: nowrap;
}

.phase-pill.strong {
  background: linear-gradient(135deg, rgba(255, 241, 227, 0.98), rgba(255, 248, 240, 0.96));
  border-color: rgba(201, 108, 45, 0.34);
  color: #9d5526;
  font-weight: 600;
  box-shadow: 0 8px 18px rgba(145, 92, 51, 0.08);
}

.loading-copy {
  display: grid;
  gap: 3px;
}

.loading-copy strong {
  color: #5b3920;
  font-size: 13px;
}

.loading-copy span {
  color: #7b654f;
  font-size: 12px;
  line-height: 1.45;
}

.loading-steps {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.loading-step {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(255, 248, 240, 0.95);
  border: 1px solid rgba(226, 206, 187, 0.9);
  color: #8b6d53;
  font-size: 11px;
}

.loading-step.active {
  color: #6d431d;
  border-color: rgba(201, 108, 45, 0.4);
  background: rgba(255, 242, 228, 0.98);
}

.loading-step.done {
  color: #6a543f;
}

.loading-events {
  display: grid;
  gap: 6px;
}

.loading-event {
  display: grid;
  gap: 2px;
  padding: 7px 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(235, 220, 204, 0.9);
}

.loading-event strong {
  color: #5b3920;
  font-size: 12px;
}

.loading-event span {
  color: #7b654f;
  font-size: 11px;
  line-height: 1.4;
}

.loading-event.retrieval,
.loading-event.graph,
.loading-event.tool,
.loading-event.answer,
.loading-event.error,
.trace-item.retrieval,
.trace-item.graph,
.trace-item.tool,
.trace-item.answer,
.trace-item.error {
  position: relative;
  overflow: hidden;
}

.loading-event.retrieval,
.trace-item.retrieval {
  background: linear-gradient(135deg, rgba(255, 247, 239, 0.96), rgba(255, 252, 247, 0.92));
  border-color: rgba(214, 153, 102, 0.42);
}

.loading-event.graph,
.trace-item.graph {
  background: linear-gradient(135deg, rgba(236, 247, 245, 0.96), rgba(247, 252, 251, 0.92));
  border-color: rgba(74, 145, 133, 0.3);
}

.loading-event.tool,
.trace-item.tool {
  background: linear-gradient(135deg, rgba(246, 243, 255, 0.96), rgba(252, 250, 255, 0.92));
  border-color: rgba(122, 112, 196, 0.28);
}

.loading-event.answer,
.trace-item.answer {
  background: linear-gradient(135deg, rgba(255, 246, 235, 0.96), rgba(255, 252, 248, 0.92));
  border-color: rgba(201, 108, 45, 0.32);
}

.loading-event.error,
.trace-item.error {
  background: linear-gradient(135deg, rgba(255, 241, 239, 0.96), rgba(255, 250, 249, 0.92));
  border-color: rgba(207, 92, 79, 0.34);
}

.spinner {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid rgba(212, 138, 79, 0.22);
  border-top-color: #d48a4f;
  animation: spin 0.9s linear infinite;
}

.spinner.orbit {
  position: relative;
  width: 18px;
  height: 18px;
  border-width: 2px;
  border-color: rgba(212, 138, 79, 0.18);
  border-top-color: rgba(212, 138, 79, 0.85);
  box-shadow: 0 0 0 4px rgba(212, 138, 79, 0.08);
}

.spinner.orbit::after {
  content: '';
  position: absolute;
  top: -2px;
  right: 2px;
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: #d48a4f;
  box-shadow: 0 0 10px rgba(212, 138, 79, 0.45);
}

.composer-dock {
  flex-shrink: 0;
  z-index: 6;
  margin-top: 0;
  padding-top: 6px;
  background: linear-gradient(180deg, rgba(248, 244, 237, 0) 0%, rgba(248, 244, 237, 0.92) 28%, rgba(248, 244, 237, 0.98) 100%);
}

.composer-dock.fixed {
  position: sticky;
  bottom: 0;
  padding-top: 6px;
}

.composer-shell {
  width: min(860px, calc(100% - 24px));
  margin: 0 auto;
  padding: 9px 10px 10px;
  border-radius: 22px;
  border: 1px solid rgba(225, 207, 189, 0.78);
  background: rgba(255, 253, 249, 0.94);
  box-shadow: 0 18px 42px rgba(83, 57, 34, 0.08);
  backdrop-filter: blur(10px);
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.composer-shell.drag-active {
  border-color: rgba(201, 108, 45, 0.68);
  box-shadow: 0 0 0 3px rgba(201, 108, 45, 0.14), 0 18px 32px rgba(90, 58, 29, 0.12);
  background: rgba(255, 248, 239, 0.98);
}

.drop-hint {
  margin-bottom: 6px;
  border: 1px dashed rgba(201, 108, 45, 0.48);
  border-radius: 14px;
  padding: 8px 10px;
  background: rgba(255, 244, 232, 0.82);
  color: #8a552e;
  font-size: 12px;
  text-align: center;
}

.slash-suggestions {
  display: grid;
  gap: 6px;
  margin-top: 8px;
  margin-bottom: 6px;
}

.slash-suggestion {
  width: 100%;
  border: 1px solid rgba(225, 207, 189, 0.82);
  background: rgba(255, 252, 248, 0.95);
  border-radius: 12px;
  padding: 8px 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.16s ease, background 0.16s ease, box-shadow 0.16s ease;
}

.slash-suggestion.active,
.slash-suggestion:hover {
  border-color: rgba(201, 108, 45, 0.45);
  background: rgba(255, 245, 235, 0.98);
  box-shadow: 0 6px 14px rgba(90, 58, 29, 0.06);
}

.slash-label {
  color: #5b3920;
  font-size: 13px;
  font-weight: 600;
}

.slash-detail {
  color: #8c735d;
  font-size: 11px;
  line-height: 1.4;
}

.composer-top,
.picker-head,
.trace-head,
.composer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.composer-top {
  margin-bottom: 2px;
}

.composer-top.compact {
  justify-content: flex-end;
  margin-bottom: 2px;
}

.mode-badge {
  display: grid;
  gap: 2px;
}

.label {
  font-size: 11px;
  color: #8d7054;
}

.mode-badge strong {
  color: #2f241b;
  font-size: 14px;
}

.composer-actions,
.composer-footer-left {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 8px;
}

.ghost-pill,
.attach-btn {
  border: 1px solid rgba(218, 192, 168, 0.78);
  background: rgba(255, 251, 246, 0.84);
  color: #7b644d;
  border-radius: 999px;
  padding: 4px 8px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 11px;
}

.ghost-pill.subtle {
  padding: 4px 9px;
  background: rgba(255, 251, 246, 0.65);
  border-color: rgba(223, 203, 182, 0.68);
}

.picker-head {
  align-items: flex-start;
  flex-wrap: wrap;
}

.picker-inline-action {
  border: none;
  background: rgba(212, 133, 71, 0.12);
  color: #c5722f;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 1;
  cursor: pointer;
  transition: background 0.2s ease, color 0.2s ease;
}

.picker-inline-action:hover {
  background: rgba(212, 133, 71, 0.2);
  color: #ad5f22;
}

.tool-create-btn {
  background: rgba(212, 133, 71, 0.12);
  border-color: rgba(212, 133, 71, 0.2);
  color: #c5722f;
}

.tool-create-btn:hover:not(:disabled) {
  background: rgba(212, 133, 71, 0.2);
  color: #ad5f22;
}

.trace-card {
  margin-bottom: 4px;
  padding: 6px;
  border-radius: 12px;
  border: 1px solid rgba(232, 216, 198, 0.86);
  background: rgba(255, 255, 255, 0.72);
  max-height: 176px;
  overflow-y: auto;
}

.trace-card.generating {
  max-height: none;
  overflow: visible;
}

.selector-grid,
.tool-columns {
  display: grid;
  gap: 10px;
}

.selector-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.agent-grid,
.tool-columns {
  margin-top: 10px;
}

.tool-columns {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.field {
  display: grid;
  gap: 4px;
}

.field span,
.composer-hint,
.attachment-hint,
.attachment-size {
  font-size: 11px;
  color: #866a51;
}

.field-hint {
  color: #8a6d54;
  font-size: 11px;
  line-height: 1.45;
}

.field select,
.composer {
  border: 1px solid rgba(225, 207, 189, 0.95);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
}

.field select {
  height: 32px;
  padding: 0 10px;
  font-size: 12px;
}

.picker-card {
  display: grid;
  gap: 7px;
  padding: 9px;
  border-radius: 14px;
  border: 1px solid rgba(236, 222, 207, 0.9);
  background: rgba(255, 252, 248, 0.72);
}

.picker-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  color: #4f3c2b;
}

.picker-item span,
.trace-head-copy,
.composer-meta,
.attachment-copy {
  display: grid;
  gap: 3px;
}

.picker-summary {
  display: grid;
  gap: 4px;
  margin-top: 8px;
  padding: 8px 10px;
  border-radius: 12px;
  background: rgba(255, 248, 240, 0.92);
  border: 1px solid rgba(226, 206, 187, 0.9);
  color: #6f543d;
}

.picker-summary strong {
  color: #5b3920;
}

.picker-item small,
.trace-head-copy small,
.empty-copy {
  color: #8a745f;
}

.progress-inline {
  display: grid;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px 10px;
  border-radius: 12px;
  border: 1px solid rgba(225, 207, 189, 0.92);
  background: rgba(255, 248, 240, 0.9);
}

.progress-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.progress-badge {
  flex: 0 0 auto;
  padding: 3px 8px;
  border-radius: 999px;
  background: rgba(201, 108, 45, 0.12);
  color: #b96534;
  font-size: 11px;
  font-weight: 600;
}

.progress-steps {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}

.progress-step {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 28px;
  padding: 6px 8px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.7);
  color: #8b6d53;
  font-size: 11px;
  border: 1px solid rgba(230, 214, 198, 0.9);
}

.progress-step.active {
  color: #6d431d;
  border-color: rgba(201, 108, 45, 0.45);
  background: rgba(255, 244, 232, 0.98);
}

.progress-step.done {
  color: #6a543f;
}

.progress-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: rgba(190, 158, 129, 0.55);
}

.progress-step.active .progress-dot {
  background: #cb7a3f;
  box-shadow: 0 0 0 4px rgba(203, 122, 63, 0.14);
}

.progress-step.done .progress-dot {
  background: #b56b36;
}

.trace-list {
  max-height: 140px;
  overflow-y: auto;
  display: grid;
  gap: 7px;
  margin-top: 6px;
}

.trace-card.generating .trace-list {
  max-height: 220px;
}

.trace-item {
  border: 1px solid rgba(239, 225, 209, 0.9);
  border-radius: 12px;
  background: rgba(251, 245, 238, 0.82);
  padding: 7px 9px;
  display: grid;
  gap: 3px;
}

.trace-detail {
  white-space: pre-wrap;
  word-break: break-word;
  color: #584434;
  line-height: 1.45;
  font-size: 12px;
}

.retrieval-trace {
  display: grid;
  gap: 7px;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid rgba(232, 216, 198, 0.76);
}

.retrieval-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.trace-pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 3px 8px;
  border-radius: 999px;
  background: rgba(255, 248, 240, 0.92);
  border: 1px solid rgba(228, 206, 182, 0.88);
  color: #815f43;
  font-size: 11px;
}

.trace-pill.strong {
  background: rgba(251, 239, 227, 0.96);
  color: #6b421c;
}

.trace-reason {
  color: #73563b;
  font-size: 11px;
  line-height: 1.45;
}

.trace-round-list {
  display: grid;
  gap: 6px;
}

.trace-round-item {
  display: grid;
  gap: 3px;
  padding: 7px 8px;
  border-radius: 10px;
  background: rgba(255, 252, 248, 0.86);
  border: 1px solid rgba(236, 222, 207, 0.9);
}

.trace-round-head,
.trace-round-body {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 6px;
}

.trace-round-head strong {
  color: #5a3a1e;
  font-size: 11px;
}

.trace-round-head span,
.trace-round-body span {
  color: #83664c;
  font-size: 11px;
}

.attachment-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 5px;
}

.attachment-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
  padding: 5px 8px;
  border-radius: 999px;
  background: rgba(255, 248, 240, 0.98);
  border: 1px solid rgba(222, 195, 169, 0.88);
  color: #6f543d;
}

.attachment-chip.image {
  border-radius: 16px;
  align-items: center;
}

.attachment-thumb {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  object-fit: cover;
  border: 1px solid rgba(222, 195, 169, 0.72);
}

.attachment-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 11px;
}

.attachment-remove {
  border: none;
  background: transparent;
  color: #9f6b43;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
  padding: 0;
}

.attachment-input {
  display: none;
}

.composer {
  width: 100%;
  min-height: 42px;
  max-height: 92px;
  padding: 9px 10px;
  resize: none;
  outline: none;
  color: #2f241b;
  line-height: 1.42;
  font-size: 13px;
}

.composer-footer {
  margin-top: 4px;
}

.send-btn {
  min-width: 74px;
  height: 30px;
  border: none;
  border-radius: 999px;
  background: linear-gradient(135deg, #d58a4d 0%, #bc6733 100%);
  color: #fff;
  font-size: 12px;
  cursor: pointer;
}

.message-bubble :deep(.md-editor-preview) {
  font-size: 12px;
  line-height: 1.42;
}

.message-bubble :deep(.md-editor-preview-wrapper) {
  padding: 0;
}

.message-bubble :deep(p) {
  margin: 0 0 0.42em;
}

.message-bubble :deep(h1),
.message-bubble :deep(h2),
.message-bubble :deep(h3),
.message-bubble :deep(h4) {
  margin: 0.12em 0 0.32em;
  line-height: 1.28;
}

.message-bubble :deep(h1) { font-size: 1.22em; }
.message-bubble :deep(h2) { font-size: 1.12em; }
.message-bubble :deep(h3) { font-size: 1.04em; }
.message-bubble :deep(ul),
.message-bubble :deep(ol) {
  margin: 0.25em 0 0.42em 1em;
  padding: 0;
}

.message-bubble :deep(li) {
  margin: 0.12em 0;
}

.message-bubble :deep(pre) {
  margin: 0.35em 0;
  padding: 8px 10px;
  border-radius: 10px;
  font-size: 11px;
}

.message-bubble :deep(code) {
  font-size: 0.88em;
}

.message-bubble.assistant :deep(table) {
  font-size: 11.5px;
}

.message-bubble.assistant :deep(blockquote) {
  margin: 0.32em 0;
  padding: 0.2em 0 0.2em 0.7em;
}

.composer-meta {
  gap: 1px;
}

.retrieval-hint {
  color: #a15a2a;
  font-weight: 600;
}

.send-btn:disabled,
.attach-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 1100px) {
  .message-bubble {
    max-width: min(100%, 74vw);
  }

  .selector-grid,
  .tool-columns {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .workspace-shell {
    padding: 8px 6px 6px;
  }

  .composer-shell {
    width: 100%;
    padding: 6px 7px;
    border-radius: 14px;
  }

  .message-bubble {
    max-width: calc(100vw - 120px);
  }

  .composer-top,
  .composer-footer,
  .composer-footer-left {
    align-items: flex-start;
    flex-direction: column;
  }

  .composer-actions {
    flex-wrap: wrap;
  }

  .attachment-name {
    max-width: 160px;
  }

  .progress-steps {
    grid-template-columns: 1fr;
  }

  .phase-pill-group {
    margin-left: 0;
    justify-content: flex-start;
  }

  .message-bubble.assistant.loading {
    min-width: min(260px, calc(100vw - 120px));
  }
}
</style>
