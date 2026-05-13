<script setup lang="ts">
import { computed, markRaw, nextTick, onBeforeUnmount, onMounted, onUpdated, ref, watch, type Component } from 'vue'
import { useRoute, useRouter, type RouteLocationRaw } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowDown, ArrowLeft, ArrowUp, CopyDocument, Plus } from '@element-plus/icons-vue'
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
import { getAgentsAPI, type AgentResponse } from '../../../apis/agent'
import { getAgentSkillsAPI, type AgentSkill } from '../../../apis/agent-skill'
import { getKnowledgeListAPI, type KnowledgeResponse } from '../../../apis/knowledge'
import { useUserStore } from '../../../store/user'
import { getRetrievalModeLabel, normalizeRetrievalMode } from '../../../utils/retrieval'
import { describeKnowledgeConfig, normalizeKnowledgeConfig } from '../../../utils/knowledge-config'
import { safeDisplayText } from '../../../utils/display-text'
import { sanitizeWorkspaceContexts } from '../../../utils/workspace-history'
import { zunoAgentAvatar } from '../../../utils/brand'
import { isDesktopRuntime } from '../../../utils/api'
import { getSettingsIcon } from '../../../utils/settings-icons'
import MascotPresence from '../../../components/MascotPresence.vue'
import type { ZunoPetMood } from '../../../components/zuno-pet'
import messageIcon from '../../../assets/message.svg'
import { DEFAULT_USER_AVATAR, isLegacyRemoteUserAvatar, withUserAvatarVersion } from '../../../utils/user-avatars'
import Agent from '../../agent'
import AgentEditor from '../../agent/agent-editor.vue'
import AgentSkillPage from '../../agent-skill'
import Dashboard from '../../dashboard'
import Knowledge from '../../knowledge'
import KnowledgeConfig from '../../knowledge/knowledge-config.vue'
import KnowledgeFile from '../../knowledge/knowledge-file.vue'
import McpServer from '../../mcp-server'
import Model from '../../model'
import Profile from '../../profile'
import Tool from '../../tool'
import { ConversationArchive } from '../../account'
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

type MessageMotion = 'sending' | 'thinking' | 'streaming' | 'complete' | 'error'
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  attachments?: ChatAttachment[]
  uiOrder?: number
  motion?: MessageMotion
}
interface ChatAttachment extends WorkspaceAttachment {
  id?: string
  preview_url?: string
}
interface SettingsThreadItem {
  id: string
  order: number
  section: string
  label: string
  command: string
  commandTurns: SettingsCommandTurn[]
  icon: string
  component: Component
  routeName: string
  routeKey: string
  routeSnapshot: SettingsRouteSnapshot | null
  detail: boolean
  history: SettingsRouteSnapshot[]
  commandVisible: boolean
  assistantVisible: boolean
  ready: boolean
  switching: boolean
}
interface SettingsCommandTurn {
  id: string
  command: string
}
interface SettingsRouteSnapshot {
  name: string
  fullPath: string
  params: Record<string, any>
  query: Record<string, any>
}
type ConversationBlock =
  | { type: 'message'; order: number; message: ChatMessage; index: number }
  | { type: 'settings'; order: number; thread: SettingsThreadItem }
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
interface NewConversationDetail { mode?: WorkspaceMode; agentId?: string; agentName?: string }
interface AgentOption {
  id: string
  name: string
  description: string
  avatar: string
}
type MascotPresenceState = 'idle' | 'listening' | 'thinking' | 'typing' | 'success' | 'confused' | 'error' | 'hover' | 'click'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const modes = [
  { id: 'normal' as const, label: '聊天模式', description: '适合轻量对话、图片理解与快速问答。' },
  { id: 'agent' as const, label: 'Agent 模式', description: '可调用工具、分析附件，并执行更完整的任务流程。' },
]

const selectedMode = ref<WorkspaceMode>('normal')
const activeAgentName = ref('')
const activeAgentId = ref('')
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
const sessionHistoryLoading = ref(false)
const sessionHistoryLabel = ref('正在打开对话')
const conversationRef = ref<HTMLElement | null>(null)
const showTracePanel = ref(false)
const isPinnedToBottom = ref(true)
const workspaceHydrated = ref(false)
const preserveConversationOnRouteSync = ref(false)
const attachmentInputRef = ref<HTMLInputElement | null>(null)
const composerInputRef = ref<HTMLTextAreaElement | null>(null)
const pendingAttachments = ref<PendingAttachment[]>([])
const attachmentsUploading = ref(false)
const isAttachmentDragOver = ref(false)
const activeSuggestionIndex = ref(0)
const settingsThreads = ref<SettingsThreadItem[]>([])
const composerExpanded = ref(false)
const composerFocused = ref(false)
const transientPetMood = ref<ZunoPetMood | ''>('')
const agentPickerOpen = ref(false)
const agentPickerLoading = ref(false)
const agentOptions = ref<AgentOption[]>([])
const activeAssistantMessageIndex = ref(-1)
const assistantTextStreaming = ref(false)
let conversationOrder = 0
let settingsMutationObserver: MutationObserver | null = null
let settingsBubbleAnchorCleanup: (() => void) | null = null
let settingsAnchorProgrammaticScroll = false
let settingsAnchorProgrammaticTimer = 0
let autosizeFrame = 0
let viewportResizeFrame = 0
let viewportResizeTimer = 0
let transientPetMoodTimer = 0
const messageMotionTimers = new Map<ChatMessage, number>()
let restoringSettingsRoute = false
let pendingSettingsNavigationThreadId = ''
let sessionHistoryLoadToken = ''
const activeSettingsRouteSnapshot = ref<SettingsRouteSnapshot | null>(null)

type SlashSuggestion = {
  key: string
  label: string
  detail: string
  insertValue: string
}

type ToolCreationKind = 'general' | 'api' | 'cli'

const settingsLabels: Record<string, string> = {
  agent: '智能体',
  model: '模型',
  knowledge: '知识库',
  mcp: 'MCP',
  tool: '工具',
  skill: 'Skill',
  dashboard: '数据看板',
  profile: '个人资料',
  conversations: '对话记录',
}
const settingsCommandSections = [
  { section: 'agent', names: ['智能体', 'agent', 'agent管理', '智能体管理'] },
  { section: 'model', names: ['模型', 'model', '模型管理', '模型资源池'] },
  { section: 'knowledge', names: ['知识库', 'knowledge', '知识库管理'] },
  { section: 'mcp', names: ['mcp', 'mcp管理', 'mcp服务', 'mcp服务管理'] },
  { section: 'tool', names: ['工具', 'tool', '工具管理'] },
  { section: 'skill', names: ['skill', 'skill管理'] },
  { section: 'dashboard', names: ['数据看板', '看板', 'dashboard', '数据'] },
]
const settingsRouteBySection: Record<string, string> = {
  agent: 'workspaceSettingsAgent',
  model: 'workspaceSettingsModel',
  knowledge: 'workspaceSettingsKnowledge',
  mcp: 'workspaceSettingsMcp',
  tool: 'workspaceSettingsTool',
  skill: 'workspaceSettingsSkill',
  dashboard: 'workspaceSettingsDashboard',
}
const settingsComponentByRouteName: Record<string, Component> = {
  workspaceSettingsAgent: markRaw(Agent),
  workspaceSettingsAgentEditor: markRaw(AgentEditor),
  workspaceSettingsModel: markRaw(Model),
  workspaceSettingsKnowledge: markRaw(Knowledge),
  workspaceSettingsKnowledgeFile: markRaw(KnowledgeFile),
  workspaceSettingsKnowledgeConfig: markRaw(KnowledgeConfig),
  workspaceSettingsMcp: markRaw(McpServer),
  workspaceSettingsTool: markRaw(Tool),
  workspaceSettingsSkill: markRaw(AgentSkillPage),
  workspaceSettingsDashboard: markRaw(Dashboard),
  workspaceAccountProfile: markRaw(Profile),
  workspaceAccountConversations: markRaw(ConversationArchive),
}

const activeMode = computed(() => modes.find((mode) => mode.id === selectedMode.value) || modes[0])
const conversationBlocks = computed<ConversationBlock[]>(() => {
  const messageBlocks = messages.value.map((message, index) => ({
    type: 'message' as const,
    order: message.uiOrder || index + 1,
    message,
    index,
  }))
  const settingsBlocks = settingsThreads.value.map((thread) => ({
    type: 'settings' as const,
    order: thread.order,
    thread,
  }))
  return [...messageBlocks, ...settingsBlocks].sort((a, b) => a.order - b.order)
})
const hasConversationBlocks = computed(() => conversationBlocks.value.length > 0)
const conversationSurfaceActive = computed(() => hasConversationBlocks.value || sessionHistoryLoading.value)
const latestAssistantMessageIndex = computed(() => {
  for (let index = messages.value.length - 1; index >= 0; index -= 1) {
    if (messages.value[index]?.role === 'assistant') return index
  }
  return -1
})
const normalizePetMood = (mood: ZunoPetMood | ''): MascotPresenceState | '' => {
  if (!mood) return ''
  if (mood === 'wake') return 'click'
  return mood
}
const getAssistantMascotState = (messageIndex: number): MascotPresenceState => {
  if (messageIndex !== latestAssistantMessageIndex.value) return 'idle'

  const transientState = normalizePetMood(transientPetMood.value)
  if (transientState) return transientState

  const message = messages.value[messageIndex]
  if (message?.motion === 'error') return 'error'
  if (message?.motion === 'complete') return 'success'
  if (message?.motion === 'streaming') return 'typing'
  if (message?.motion === 'thinking') return 'thinking'

  if (isGenerating.value && messageIndex === activeAssistantMessageIndex.value) {
    return assistantTextStreaming.value ? 'typing' : 'thinking'
  }

  if (composerFocused.value || inputMessage.value.trim()) return 'listening'
  return 'idle'
}
const getAssistantStatusLabel = (message: ChatMessage, messageIndex: number) => {
  if (message.motion === 'error') return '需要调整'
  if (message.motion === 'thinking') return '正在思考'
  if (message.motion === 'streaming') return '正在输出'
  if (message.motion === 'complete') return '已完成'
  if (!message.content && isGenerating.value && messageIndex === messages.value.length - 1) return '正在思考'
  return '已回复'
}
const shouldShowAssistantStatus = (message: ChatMessage, messageIndex: number) => (
  !!message.motion || (!message.content && isGenerating.value && messageIndex === messages.value.length - 1)
)
const getSettingsMascotState = (thread: SettingsThreadItem): MascotPresenceState => (
  thread.ready ? 'idle' : 'thinking'
)
const isAccountThread = (thread: SettingsThreadItem) => ['profile', 'conversations'].includes(thread.section)
const getThreadLoadingVerb = (thread: SettingsThreadItem) => isAccountThread(thread) ? '正在整理' : '正在整理'
const getThreadLoadingText = (thread: SettingsThreadItem) => isAccountThread(thread) ? 'Zuno 正在整理账号内容' : 'Zuno 正在拉取配置'
const normalizeAvatarUrl = (avatar?: string) => {
  const raw = String(avatar || '').trim()
  if (!raw || raw.startsWith('/src/assets/') || isLegacyRemoteUserAvatar(raw)) return DEFAULT_USER_AVATAR
  return withUserAvatarVersion(raw)
}
const userAvatarSrc = computed(() => normalizeAvatarUrl(userStore.userInfo?.avatar))
const activeExecutionMode = computed(() => executionModes.value.find((mode) => mode.id === selectedExecutionMode.value) || null)
const activeAccessScope = computed(() => accessScopes.value.find((scope) => scope.id === selectedAccessScope.value) || null)
const isAgentMode = computed(() => selectedMode.value === 'agent')
const selectedModel = computed(() => modelOptions.value.find((model) => model.llm_id === selectedModelId.value) || null)
const modelStatusLabel = computed(() => {
  if (modelsLoading.value) return '正在读取模型'
  if (selectedModel.value) return `模型：${selectedModel.value.model || selectedModel.value.provider || '已就绪'}`
  return '还没有可用模型'
})
const modelStatusTone = computed(() => selectedModel.value ? 'ready' : (modelsLoading.value ? 'loading' : 'empty'))
const heroTitle = computed(() => isAgentMode.value && activeAgentName.value ? `和 ${activeAgentName.value} 开聊` : '今天想让 Zuno 做什么？')
const heroSubtitle = computed(() => isAgentMode.value && activeAgentName.value ? '这个对话会跟随选中的 Agent，工具和知识库也会一起工作。' : '直接输入问题，或切到 Agent 处理带工具的任务。')
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
const traceVisible = computed(() => isAgentMode.value && showTracePanel.value)
const compactPanel = computed(() => conversationSurfaceActive.value)
const canCollapseComposer = computed(() => (
  conversationSurfaceActive.value
  && !sessionHistoryLoading.value
  && !inputMessage.value.trim()
  && pendingAttachments.value.length === 0
  && slashSuggestions.value.length === 0
  && !traceVisible.value
  && !isAttachmentDragOver.value
  && !attachmentsUploading.value
))
const compactComposerVisible = computed(() => canCollapseComposer.value && !composerExpanded.value)
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
const normalizeSessionMode = (session: any): WorkspaceMode => {
  if (normalizeSessionAgentName(session)) return 'agent'
  const explicitMode = String(session?.workspace_mode || '').trim().toLowerCase()
  if (explicitMode === 'normal') return 'normal'
  return 'normal'
}
const normalizeSessionAgentName = (session: any) => {
  const raw = String(session?.agent || '').trim()
  if (!raw || ['normal', 'simple', 'agent'].includes(raw.toLowerCase())) return ''
  return raw
}

const sanitizeAssistantChunk = (chunk: string) => isAgentMode.value ? chunk : chunk.replace(/ReAct\s*Agent[^\n]*\n?/gi, '').replace(/^\s+/, '')
const normalizeMessageMarkdown = (content: string) => {
  const lines = content.replace(/\r\n/g, '\n').split('\n')
  let insideFence = false

  const normalizedLines = lines.map((line) => {
    if (/^\s*```/.test(line)) {
      insideFence = !insideFence
      return line
    }
    if (insideFence) return line

    return line
      .replace(/^(\s{0,3})(#{1,6})(?=[^\s#])/g, '$1$2 ')
      .replace(/([。！？!?；;：:])\s*(#{1,6})(?=\s?\S)/g, '$1\n\n$2 ')
      .replace(/(\S)\s*(#{2,6})(?=[^\s#])/g, '$1\n\n$2 ')
      .replace(/^(\s{0,3})(#{1,6})\s{2,}/g, '$1$2 ')
      .replace(/^(\s*[-*+])(?=\S)/g, '$1 ')
      .replace(/^(\s*\d+\.)(?=\S)/g, '$1 ')
  })

  return normalizedLines
    .join('\n')
    .replace(/([^\n])\n(\|[^\n]+\|\n\|[-:\s|]+\|)/g, '$1\n\n$2')
    .replace(/(^|\n)(\s{0,3})(#{1,6})\s{2,}/g, '$1$2$3 ')
    .replace(/\n{4,}/g, '\n\n\n')
}
const handleAvatarError = (event: Event) => { const target = event.target as HTMLImageElement; if (target) target.src = DEFAULT_USER_AVATAR }
const copyMessageContent = async (message: ChatMessage) => {
  const content = message.content.trim()
  if (!content) return
  try {
    await navigator.clipboard.writeText(content)
    ElMessage.success('已复制')
  } catch (error) {
    console.error('复制消息失败', error)
    ElMessage.error('复制失败')
  }
}
const wait = (ms: number) => new Promise<void>((resolve) => window.setTimeout(resolve, ms))
const shouldReduceMotion = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
const clearTransientPetMood = () => {
  if (transientPetMoodTimer) window.clearTimeout(transientPetMoodTimer)
  transientPetMoodTimer = 0
  transientPetMood.value = ''
}
const pulsePetMood = (mood: ZunoPetMood, duration = 1200) => {
  if (transientPetMoodTimer) window.clearTimeout(transientPetMoodTimer)
  transientPetMood.value = mood
  transientPetMoodTimer = window.setTimeout(() => {
    transientPetMood.value = ''
    transientPetMoodTimer = 0
  }, shouldReduceMotion() ? Math.min(duration, 240) : duration)
}
const clearMessageMotionTimers = () => {
  messageMotionTimers.forEach((timer) => window.clearTimeout(timer))
  messageMotionTimers.clear()
}
const setMessageMotion = (message: ChatMessage | undefined, motion: MessageMotion, duration = 0) => {
  if (!message) return
  const existingTimer = messageMotionTimers.get(message)
  if (existingTimer) window.clearTimeout(existingTimer)
  message.motion = motion
  if (!duration) {
    messageMotionTimers.delete(message)
    return
  }
  const timer = window.setTimeout(() => {
    if (message.motion === motion) message.motion = undefined
    messageMotionTimers.delete(message)
  }, shouldReduceMotion() ? Math.min(duration, 240) : duration)
  messageMotionTimers.set(message, timer)
}
const scrollToBottom = async (force = false, behavior: ScrollBehavior = 'auto') => {
  await nextTick()
  const panel = conversationRef.value
  if (!panel || (!force && !isPinnedToBottom.value)) return
  panel.scrollTo({
    top: panel.scrollHeight,
    behavior: shouldReduceMotion() ? 'auto' : behavior,
  })
}
const markSettingsAnchorProgrammaticScroll = () => {
  settingsAnchorProgrammaticScroll = true
  if (settingsAnchorProgrammaticTimer) window.clearTimeout(settingsAnchorProgrammaticTimer)
  settingsAnchorProgrammaticTimer = window.setTimeout(() => {
    settingsAnchorProgrammaticScroll = false
    settingsAnchorProgrammaticTimer = 0
  }, 120)
}
const cancelSettingsBubbleAnchor = () => {
  settingsBubbleAnchorCleanup?.()
}
const handleConversationScroll = () => {
  const panel = conversationRef.value
  if (!panel) return
  isPinnedToBottom.value = panel.scrollHeight - (panel.scrollTop + panel.clientHeight) < 24
  if (settingsBubbleAnchorCleanup && !settingsAnchorProgrammaticScroll) {
    cancelSettingsBubbleAnchor()
  }
}
const restoreSettingsBubbleTop = (bubble: HTMLElement, targetTop: number) => {
  const panel = conversationRef.value
  if (!panel || !panel.contains(bubble)) return false
  const nextTop = bubble.getBoundingClientRect().top
  const delta = nextTop - targetTop
  if (Math.abs(delta) < 0.5) return false
  markSettingsAnchorProgrammaticScroll()
  panel.scrollTop += delta
  return true
}
const lockSettingsBubbleTop = (bubble: HTMLElement, duration = 760) => {
  const panel = conversationRef.value
  if (!panel || !panel.contains(bubble)) return
  settingsBubbleAnchorCleanup?.()
  const targetTop = bubble.getBoundingClientRect().top
  let disposed = false
  const frameIds: number[] = []
  const timerIds: number[] = []
  let lastDelta = 0
  let expectedScrollTop = panel.scrollTop
  const runStable = () => {
    if (disposed) return
    if (!settingsAnchorProgrammaticScroll && Math.abs(panel.scrollTop - expectedScrollTop) > 3) {
      cancelSettingsBubbleAnchor()
      return
    }
    const nextTop = bubble.getBoundingClientRect().top
    const delta = nextTop - targetTop
    if (Math.abs(delta) < 1 || Math.abs(delta - lastDelta) < 0.5) return
    lastDelta = delta
    if (restoreSettingsBubbleTop(bubble, targetTop)) {
      expectedScrollTop = panel.scrollTop
    }
  }
  const queueFrame = () => {
    frameIds.push(window.requestAnimationFrame(() => {
      runStable()
      frameIds.push(window.requestAnimationFrame(runStable))
    }))
  }
  const resizeObserver = new ResizeObserver(runStable)
  resizeObserver.observe(bubble)
  queueFrame()
  ;[80, 180, 360, duration].forEach((delay) => {
    timerIds.push(window.setTimeout(runStable, delay))
  })
  const cleanupTimer = window.setTimeout(() => {
    settingsBubbleAnchorCleanup?.()
  }, duration + 80)
  settingsBubbleAnchorCleanup = () => {
    if (disposed) return
    disposed = true
    resizeObserver.disconnect()
    frameIds.forEach((id) => window.cancelAnimationFrame(id))
    timerIds.forEach((id) => window.clearTimeout(id))
    window.clearTimeout(cleanupTimer)
    settingsBubbleAnchorCleanup = null
  }
}
const lockSettingsBubbleFromEvent = (event: Event) => {
  const target = event.target as Element | null
  const bubble = target?.closest<HTMLElement>('.settings-bubble')
  if (!bubble) return
  const shouldLock = Boolean(target?.closest([
    'button',
    'a',
    'input',
    'textarea',
    'select',
    '[role="button"]',
    '[role="tab"]',
    '[role="menuitem"]',
    '.el-button',
    '.el-dropdown',
    '.el-tabs',
    '.el-collapse',
    '.el-switch',
    '.el-radio',
    '.el-checkbox',
    '.el-select',
    '.el-input',
  ].join(',')))
  if (!shouldLock) return
  lockSettingsBubbleTop(bubble)
}
const waitForSettingsBubbleLayout = (threadId: string) => new Promise<void>((resolve) => {
  const startedAt = Date.now()
  const maxWait = 1600
  const stableDelay = 180
  let lastHeight = -1
  let stableSince = Date.now()
  let frameId = 0
  let observer: MutationObserver | null = null
  let finished = false

  const finish = () => {
    if (finished) return
    finished = true
    if (frameId) window.cancelAnimationFrame(frameId)
    observer?.disconnect()
    resolve()
  }

  const measure = () => {
    const bubble = conversationRef.value?.querySelector<HTMLElement>(`.settings-bubble[data-settings-thread-id="${threadId}"]`)
    if (!bubble) {
      frameId = window.requestAnimationFrame(measure)
      return
    }

    const height = Math.ceil(bubble.scrollHeight)
    const imagesReady = Array.from(bubble.querySelectorAll<HTMLImageElement>('img')).every((image) => image.complete)
    const loadingSettled = !Array
      .from(bubble.querySelectorAll<HTMLElement>('.el-loading-mask'))
      .some((mask) => getComputedStyle(mask).display !== 'none' && getComputedStyle(mask).visibility !== 'hidden')
    const heightChanged = Math.abs(height - lastHeight) > 1
    if (heightChanged) {
      lastHeight = height
      stableSince = Date.now()
    }

    const waited = Date.now() - startedAt
    const stableFor = Date.now() - stableSince
    if ((imagesReady && loadingSettled && stableFor >= stableDelay) || waited >= maxWait) {
      finish()
      return
    }
    frameId = window.requestAnimationFrame(measure)
  }

  window.requestAnimationFrame(() => {
    const bubble = conversationRef.value?.querySelector<HTMLElement>(`.settings-bubble[data-settings-thread-id="${threadId}"]`)
    if (bubble) {
      observer = new MutationObserver(() => {
        stableSince = Date.now()
      })
      observer.observe(bubble, { childList: true, subtree: true, attributes: true, characterData: true })
    }
    measure()
  })
})
const autosizeTextarea = (textarea: HTMLTextAreaElement) => {
  textarea.rows = 1
  textarea.style.height = 'auto'
  textarea.style.overflowY = 'hidden'
  textarea.style.height = `${Math.max(30, textarea.scrollHeight)}px`
}
const autosizeComposerTextarea = async () => {
  await nextTick()
  const textarea = composerInputRef.value
  if (!textarea) return
  const minHeight = hasConversationBlocks.value ? 34 : 44
  const maxHeight = hasConversationBlocks.value ? 104 : 68
  textarea.style.height = 'auto'
  const height = Math.min(Math.max(minHeight, textarea.scrollHeight), maxHeight)
  textarea.style.height = `${height}px`
  textarea.style.overflowY = textarea.scrollHeight > maxHeight ? 'auto' : 'hidden'
}
const autosizeSettingsTextareas = async () => {
  await nextTick()
  const panel = conversationRef.value
  if (!panel) return
  panel.querySelectorAll<HTMLTextAreaElement>('.settings-bubble textarea').forEach((textarea) => {
    autosizeTextarea(textarea)
    if (textarea.dataset.zunoAutosize === 'true') return
    textarea.dataset.zunoAutosize = 'true'
    textarea.addEventListener('input', () => autosizeTextarea(textarea))
  })
}
const scheduleSettingsTextareaAutosize = () => {
  if (autosizeFrame) window.cancelAnimationFrame(autosizeFrame)
  autosizeFrame = window.requestAnimationFrame(() => {
    autosizeFrame = 0
    void autosizeSettingsTextareas()
  })
}
const stabilizeConversationViewport = async (forceBottom = false) => {
  await autosizeComposerTextarea()
  await autosizeSettingsTextareas()
  if (hasConversationBlocks.value && (forceBottom || isPinnedToBottom.value)) {
    await scrollToBottom(true, 'auto')
  }
}
const handleViewportResize = () => {
  const shouldKeepLatestTurnVisible = hasConversationBlocks.value && (isPinnedToBottom.value || settingsThreads.value.length > 0)
  if (viewportResizeFrame) window.cancelAnimationFrame(viewportResizeFrame)
  viewportResizeFrame = window.requestAnimationFrame(() => {
    viewportResizeFrame = 0
    void stabilizeConversationViewport(shouldKeepLatestTurnVisible)
  })
  if (viewportResizeTimer) window.clearTimeout(viewportResizeTimer)
  viewportResizeTimer = window.setTimeout(() => {
    viewportResizeTimer = 0
    void stabilizeConversationViewport(shouldKeepLatestTurnVisible)
  }, 160)
}
const ensureSettingsMutationObserver = () => {
  const panel = conversationRef.value
  if (!panel || settingsMutationObserver) return
  settingsMutationObserver = new MutationObserver(() => scheduleSettingsTextareaAutosize())
  settingsMutationObserver.observe(panel, { childList: true, subtree: true })
}
const emitSessionUpdated = () => window.dispatchEvent(new CustomEvent('workspace-session-updated', { detail: { sessionId: currentSessionId.value } }))
const emitSessionModeUpdated = () => window.dispatchEvent(new CustomEvent('workspace-session-mode-updated', { detail: { sessionId: currentSessionId.value, mode: selectedMode.value } }))
const nextConversationOrder = () => {
  conversationOrder += 1
  return conversationOrder
}
const getSettingsCommand = (label: string, routeName: string, detail = false) => {
  if (routeName === 'workspaceSettingsAgentEditor') return route.query.id ? '编辑智能体' : '创建智能体'
  if (routeName === 'workspaceSettingsKnowledgeFile') return '打开知识库文件'
  if (routeName === 'workspaceSettingsKnowledgeConfig') return '打开知识库参数'
  return detail ? `打开${label}详情` : `打开${label}`
}
const getSettingsSectionCommand = (label: string) => `打开${label}`
const getSettingsPanelTitle = (label: string, routeName: string) => {
  if (routeName === 'workspaceSettingsAgentEditor') return route.query.id ? '编辑智能体' : '创建智能体'
  if (routeName === 'workspaceSettingsKnowledgeFile') return `${route.query.name || '知识库'} · 文件`
  if (routeName === 'workspaceSettingsKnowledgeConfig') return `${route.query.name || '知识库'} · 参数`
  return label
}
const getThreadIcon = (section: string, routeName = '') => {
  if (section === 'conversations' || routeName === 'workspaceAccountConversations') return messageIcon
  if (section === 'profile' || routeName === 'workspaceAccountProfile') return DEFAULT_USER_AVATAR
  return getSettingsIcon(section)
}
const normalizeSettingsCommandText = (value: string) => value
  .trim()
  .replace(/\s+/g, '')
  .replace(/[。.!！?？,，;；:：]/g, '')
  .toLowerCase()
const getSettingsSectionFromLocalCommand = (value: string) => {
  const normalized = normalizeSettingsCommandText(value)
  if (!normalized) return ''
  const commandBody = normalized
    .replace(/^(请|帮我|麻烦|帮忙|给我|我要|我想|想)?(打开|进入|去|切到|切换到|查看|调出|唤起)/, '')
    .replace(/(页面|页|面板|设置|配置|中心)$/, '')
  if (!commandBody) return ''

  const matched = settingsCommandSections.find((item) => item.names.some((name) => {
    const alias = normalizeSettingsCommandText(name)
    return commandBody === alias || commandBody === `${alias}管理`
  }))
  return matched?.section || ''
}
const snapshotSettingsRoute = (): SettingsRouteSnapshot | null => {
  const routeName = String(route.name || '')
  if (!routeName || (!route.meta.settingsSection && !route.meta.accountSection)) return null
  return {
    name: routeName,
    fullPath: route.fullPath,
    params: { ...route.params },
    query: { ...route.query },
  }
}
const appendSettingsThreadFromRoute = async () => {
  const section = String(route.meta.settingsSection || route.meta.accountSection || '')
  if (!section) return

  const routeName = String(route.name || '')
  const component = settingsComponentByRouteName[routeName]
  if (!component) return

  const label = settingsLabels[section] || '设置'
  const detail = Boolean(route.meta.settingsDetail)
  const snapshot = snapshotSettingsRoute()
  const requestedThread = pendingSettingsNavigationThreadId
    ? settingsThreads.value.find((thread) => thread.id === pendingSettingsNavigationThreadId)
    : null
  const latestThread = requestedThread || settingsThreads.value[settingsThreads.value.length - 1]
  const previousSnapshot = requestedThread?.routeSnapshot || activeSettingsRouteSnapshot.value
  const canReuseLatestThread = Boolean(
    latestThread
    && previousSnapshot
    && latestThread.section === section
    && (requestedThread || latestThread.routeKey === previousSnapshot.fullPath)
    && (detail || restoringSettingsRoute || requestedThread)
  )
  if (canReuseLatestThread && latestThread) {
    const nextLabel = getSettingsPanelTitle(label, routeName)
    const nextCommand = getSettingsCommand(label, routeName, detail)
    const sectionCommand = getSettingsSectionCommand(label)
    if (
      snapshot
      && previousSnapshot
      && previousSnapshot.fullPath !== snapshot.fullPath
      && !restoringSettingsRoute
      && detail
      && latestThread.history[latestThread.history.length - 1]?.fullPath !== previousSnapshot.fullPath
    ) {
      latestThread.history.push(previousSnapshot)
    }
    latestThread.command = nextCommand
    if (!restoringSettingsRoute && !detail && latestThread.commandTurns.length === 0) {
      latestThread.commandTurns.push({
        id: `${Date.now()}-${latestThread.commandTurns.length}`,
        command: sectionCommand,
      })
    }
    latestThread.label = nextLabel
    latestThread.switching = true
    await nextTick()
    await scrollToBottom(false, 'smooth')
    await wait(shouldReduceMotion() ? 0 : 320)
    if (route.fullPath !== snapshot?.fullPath) return
    latestThread.section = section
    latestThread.icon = getThreadIcon(section, routeName)
    latestThread.component = component
    latestThread.routeName = routeName
    latestThread.routeKey = route.fullPath
    latestThread.routeSnapshot = snapshot
    latestThread.detail = detail
    latestThread.ready = true
    activeSettingsRouteSnapshot.value = snapshot
    pendingSettingsNavigationThreadId = ''
    ensureSettingsMutationObserver()
    await nextTick()
    await autosizeSettingsTextareas()
    await scrollToBottom(false, 'smooth')
    window.setTimeout(() => {
      if (latestThread.routeKey === route.fullPath) {
        latestThread.switching = false
      }
    }, shouldReduceMotion() ? 0 : 260)
    return
  }
  const thread: SettingsThreadItem = {
    id: `${Date.now()}-${settingsThreads.value.length}`,
    order: nextConversationOrder(),
    section,
    label: getSettingsPanelTitle(label, routeName),
    command: getSettingsCommand(label, routeName, detail),
    commandTurns: [{
      id: `${Date.now()}-0`,
      command: getSettingsSectionCommand(label),
    }],
    icon: getThreadIcon(section, routeName),
    component,
    routeName,
    routeKey: route.fullPath,
    routeSnapshot: snapshot,
    detail,
    history: [],
    commandVisible: false,
    assistantVisible: false,
    ready: false,
    switching: false,
  }
  const threadIndex = settingsThreads.value.push(thread) - 1
  activeSettingsRouteSnapshot.value = snapshot
  isPinnedToBottom.value = true
  ensureSettingsMutationObserver()
  try {
    await wait(120)
    const commandThread = settingsThreads.value[threadIndex]
    if (commandThread) commandThread.commandVisible = true
    await scrollToBottom(true, 'smooth')
    await wait(280)
    const assistantThread = settingsThreads.value[threadIndex]
    if (assistantThread) assistantThread.assistantVisible = true
    await scrollToBottom(true, 'smooth')
    await wait(120)
    await nextTick()
    await waitForSettingsBubbleLayout(thread.id)
    await autosizeSettingsTextareas()
  } finally {
    const currentThread = settingsThreads.value[threadIndex]
    if (currentThread) currentThread.ready = true
    pendingSettingsNavigationThreadId = ''
    await nextTick()
    await scrollToBottom(true, 'smooth')
  }
}
const expandComposer = async () => {
  composerExpanded.value = true
  composerFocused.value = true
  await nextTick()
  await autosizeComposerTextarea()
  composerInputRef.value?.focus()
}
const handleComposerFocus = () => {
  composerExpanded.value = true
  composerFocused.value = true
}
const handleComposerFocusOut = (event: FocusEvent) => {
  const currentTarget = event.currentTarget as HTMLElement | null
  const nextTarget = event.relatedTarget as Node | null
  if (currentTarget && nextTarget && currentTarget.contains(nextTarget)) return
  composerFocused.value = false
  window.setTimeout(() => {
    if (canCollapseComposer.value) composerExpanded.value = false
  }, 80)
}
const handleIntroPetClick = async () => {
  pulsePetMood('wake', 900)
  await nextTick()
  composerExpanded.value = true
  composerFocused.value = true
  composerInputRef.value?.focus()
}
const handleSettingsNavigateRequest = async (event: Event) => {
  const detail = (event as CustomEvent<{ location?: RouteLocationRaw; threadId?: string }>).detail
  if (!detail?.location) return
  pendingSettingsNavigationThreadId = detail.threadId || ''
  try {
    await router.push(detail.location)
  } catch (error) {
    pendingSettingsNavigationThreadId = ''
    throw error
  }
}
const canNavigateSettingsThreadBack = (thread: SettingsThreadItem) => thread.detail
const handleSettingsThreadBack = async (thread: SettingsThreadItem) => {
  const fallbackRouteName = settingsRouteBySection[thread.section] || 'workspaceSettingsAgent'
  thread.history = []
  pendingSettingsNavigationThreadId = thread.id
  try {
    await router.push({
      name: fallbackRouteName,
      query: { ...route.query, settings_turn: String(Date.now()) },
    })
  } catch (error) {
    pendingSettingsNavigationThreadId = ''
    throw error
  }
}
const clearConversationState = (options?: { keepSessionHistoryLoading?: boolean }) => {
  inputMessage.value = ''
  clearMessageMotionTimers()
  messages.value = []
  settingsThreads.value = []
  activeAssistantMessageIndex.value = -1
  assistantTextStreaming.value = false
  activeSettingsRouteSnapshot.value = null
  conversationOrder = 0
  composerExpanded.value = false
  composerFocused.value = false
  clearTransientPetMood()
  executionEvents.value = []
  pendingAttachments.value = []
  attachmentsUploading.value = false
  isGenerating.value = false
  showTracePanel.value = false
  isPinnedToBottom.value = true
  consumedInitialMessageKey.value = ''
  initialRouteMessageInFlightKey.value = ''
  if (!options?.keepSessionHistoryLoading) {
    sessionHistoryLoading.value = false
    sessionHistoryLoadToken = ''
  }
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
  ...(activeAgentName.value ? { agent_name: activeAgentName.value } : {}),
  ...(activeAgentId.value ? { agent_id: activeAgentId.value } : {}),
})

const syncRouteState = async (options?: { preserveConversation?: boolean }) => {
  if (options?.preserveConversation) preserveConversationOnRouteSync.value = true
  try {
    await router.replace({ name: 'workspaceDefaultPage', query: buildWorkspaceQuery() })
    await nextTick()
  } finally {
    if (options?.preserveConversation) preserveConversationOnRouteSync.value = false
  }
}

const resetToDraftSession = async (mode: WorkspaceMode, options?: { pruneCurrent?: boolean; agentName?: string; agentId?: string }) => {
  const pruneCurrent = options?.pruneCurrent !== false
  const disposableSessionId = pruneCurrent && isCurrentSessionDisposable() ? currentSessionId.value : ''
  clearConversationState()
  selectedMode.value = mode
  activeAgentName.value = mode === 'agent' ? String(options?.agentName || activeAgentName.value || '').trim() : ''
  activeAgentId.value = mode === 'agent' ? String(options?.agentId || activeAgentId.value || '').trim() : ''
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
  const agentName = mode === 'agent' ? activeAgentName.value.trim() : ''
  const response = await createWorkspaceSessionAPI({
    title: '新对话',
    workspace_mode: mode,
    agent: agentName || mode,
    contexts: [],
  })
  if (response.data?.status_code !== 200 || !response.data?.data?.session_id) {
    throw new Error('create_session_failed')
  }
  currentSessionId.value = String(response.data.data.session_id)
  saveWorkspaceSessionMode(currentSessionId.value, mode)
  emitSessionUpdated()
  emitSessionModeUpdated()
}

const startFreshConversation = async (detail?: NewConversationDetail) => {
  const defaults = loadWorkspaceDefaults()
  const nextMode = detail?.mode === 'agent' ? 'agent' : 'normal'
  selectedExecutionMode.value = defaults.executionMode || selectedExecutionMode.value
  selectedAccessScope.value = defaults.accessScope || selectedAccessScope.value
  if (defaults.modelId && modelOptions.value.some((model) => model.llm_id === defaults.modelId)) selectedModelId.value = defaults.modelId
  await resetToDraftSession(nextMode || defaults.mode || selectedMode.value, {
    agentName: detail?.agentName,
    agentId: detail?.agentId,
  })
  await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
  applySavedWorkspaceDefaults()
}
const handleNewConversationRequest = async (event?: Event) => {
  if (isGenerating.value) {
    ElMessage.warning('请等待当前回复完成后再新建会话。')
    return
  }
  try {
    const detail = (event as CustomEvent<NewConversationDetail> | undefined)?.detail
    await startFreshConversation(detail)
  } catch (error) {
    console.error('新建会话失败', error)
    ElMessage.error('新建会话失败')
  }
}

const normalizeAgentAvatar = (avatar?: string) => {
  const raw = String(avatar || '').trim()
  if (!raw || raw.startsWith('/src/assets/')) return zunoAgentAvatar
  return withUserAvatarVersion(raw)
}

const normalizeAgentOption = (agent: AgentResponse): AgentOption => ({
  id: String(agent.agent_id || agent.id || agent.name || '').trim(),
  name: String(agent.name || '未命名智能体').trim(),
  description: String(agent.description || '暂无描述').trim(),
  avatar: normalizeAgentAvatar(agent.logo_url),
})

const fetchAgentOptions = async () => {
  try {
    agentPickerLoading.value = true
    const response = await getAgentsAPI()
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '获取 Agent 失败')
    }
    agentOptions.value = (response.data.data || [])
      .map(normalizeAgentOption)
      .filter((agent) => Boolean(agent.id))
  } catch (error) {
    console.error('获取 Agent 失败', error)
    agentOptions.value = []
  } finally {
    agentPickerLoading.value = false
  }
}

const openAgentPicker = async () => {
  if (isGenerating.value) return
  agentPickerOpen.value = !agentPickerOpen.value
  if (!agentPickerOpen.value) return
  pulsePetMood('listening', 900)
  await fetchAgentOptions()
}

const handleAgentPickerPointerDown = (event: PointerEvent) => {
  if (!agentPickerOpen.value) return
  const target = event.target as Element | null
  if (target?.closest('.mode-switcher')) return
  agentPickerOpen.value = false
}

const selectAgentOption = async (agent: AgentOption) => {
  if (isGenerating.value) return
  agentPickerOpen.value = false
  await resetToDraftSession('agent', {
    pruneCurrent: false,
    agentName: agent.name,
    agentId: agent.id,
  })
  await Promise.all([fetchPlugins(), fetchSkills(), fetchKnowledges()])
  applySavedWorkspaceDefaults()
  pulsePetMood('success', 1100)
}
const handleAgentOptionAvatarError = (event: Event) => {
  const target = event.target as HTMLImageElement | null
  if (target) target.src = zunoAgentAvatar
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

const buildChatErrorMessage = (raw: string) => {
  const text = String(raw || '').trim()
  if (!text) return '这次请求没有成功完成，请稍后再试。'

  const unsupportedModel = text.match(/Not supported model\s+([^'",}]+)/i)
  if (unsupportedModel?.[1]) {
    return `模型接口不支持当前模型 ID「${unsupportedModel[1].trim()}」。请在模型设置里填写接口实际使用的 model id，例如小米 Token Plan 通常使用 mimo-v2.5 或 mimo-v2.5-pro。`
  }

  return `这次请求没有成功完成。后端返回的错误是：${text}`
}

const buildMissingModelMessage = () => [
  '我现在还没找到可用的聊天模型。',
  '',
  '先在 Settings 里添加一个 LLM，再回来继续这句就行。也可以直接输入「打开模型管理」。',
].join('\n')
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
    if (selectedModelId.value && !modelOptions.value.some((model) => model.llm_id === selectedModelId.value)) selectedModelId.value = ''
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
  const loadToken = `${sessionId}-${Date.now()}-${Math.random()}`
  sessionHistoryLoadToken = loadToken
  sessionHistoryLabel.value = '正在打开对话'
  sessionHistoryLoading.value = true
  try {
    clearConversationState({ keepSessionHistoryLoading: true })
    const response = await getWorkspaceSessionInfoAPI(sessionId)
    if (sessionHistoryLoadToken !== loadToken) return
    if (response.data.status_code !== 200) return
    const session = response.data.data
    const sessionMode = normalizeSessionMode(session)
    selectedMode.value = sessionMode
    activeAgentName.value = sessionMode === 'agent' ? normalizeSessionAgentName(session) : ''
    if (!session?.contexts || !Array.isArray(session.contexts)) return
    const contexts = sanitizeWorkspaceContexts(session.contexts)
    messages.value = contexts
      .map((context: any) => [{ role: 'user' as const, content: context.query || '' }, { role: 'assistant' as const, content: context.answer || '' }])
      .flat()
      .filter((message: ChatMessage) => message.content)
      .map((message: ChatMessage) => ({ ...message, uiOrder: nextConversationOrder() }))
    executionEvents.value = []
    await scrollToBottom(true)
  } catch (error) {
    if (sessionHistoryLoadToken === loadToken) {
      console.error('加载会话历史失败', error)
      ElMessage.error('加载会话历史失败')
    }
  } finally {
    if (sessionHistoryLoadToken === loadToken) {
      sessionHistoryLoading.value = false
    }
  }
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
const isImageAttachment = (attachment: ChatAttachment) => attachment.mime_type?.startsWith('image/')
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
  agent_name: isAgentMode.value ? activeAgentName.value : '',
  agent_id: isAgentMode.value ? activeAgentId.value : '',
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
  const localSettingsSection = pendingAttachments.value.length ? '' : getSettingsSectionFromLocalCommand(query)
  if (localSettingsSection) {
    inputMessage.value = ''
    composerExpanded.value = false
    composerFocused.value = false
    pulsePetMood('wake', 900)
    window.dispatchEvent(new CustomEvent('workspace-open-settings', { detail: { section: localSettingsSection } }))
    return true
  }
  if (!selectedModelId.value || !selectedModel.value) {
    await fetchModels()
  }
  if (!selectedModelId.value || !selectedModel.value) {
    inputMessage.value = ''
    composerExpanded.value = false
    const userMessage: ChatMessage = { role: 'user', content: query, uiOrder: nextConversationOrder() }
    const assistantMessage: ChatMessage = { role: 'assistant', content: buildMissingModelMessage(), uiOrder: nextConversationOrder() }
    messages.value.push(userMessage)
    messages.value.push(assistantMessage)
    setMessageMotion(userMessage, 'sending', 520)
    setMessageMotion(assistantMessage, 'error', 1800)
    activeAssistantMessageIndex.value = messages.value.length - 1
    assistantTextStreaming.value = false
    pulsePetMood('confused', 1800)
    isPinnedToBottom.value = true
    await scrollToBottom(true, 'smooth')
    return false
  }
  if (!currentSessionId.value) {
    try {
      await createPersistedSession(selectedMode.value)
    } catch (error) {
      console.error('补建会话失败', error)
      pulsePetMood('error', 1600)
      ElMessage.error('新建会话失败')
      return false
    }
  }
  clearTransientPetMood()
  inputMessage.value = ''
  composerExpanded.value = false
  composerFocused.value = false
  isGenerating.value = true
  executionEvents.value = []
  showTracePanel.value = false
  const attachmentsForRequest = [...pendingAttachments.value]
  pendingAttachments.value = []
  const attachmentsForMessage = attachmentsForRequest.map((attachment) => ({
    ...attachment,
    preview_url: attachment.url,
  }))
  const userMessage: ChatMessage = { role: 'user', content: query, attachments: attachmentsForMessage, uiOrder: nextConversationOrder() }
  messages.value.push(userMessage)
  setMessageMotion(userMessage, 'sending', 520)
  const assistantIndex = messages.value.length
  const assistantMessage: ChatMessage = { role: 'assistant', content: isAgentMode.value ? buildLiveAssistantProgress() : '', uiOrder: nextConversationOrder() }
  messages.value.push(assistantMessage)
  setMessageMotion(assistantMessage, 'thinking')
  activeAssistantMessageIndex.value = assistantIndex
  assistantTextStreaming.value = false
  isPinnedToBottom.value = true
  await scrollToBottom(true)
  await syncRouteState({ preserveConversation: true })
  if (isAgentMode.value) executionEvents.value.push({ id: crypto.randomUUID(), title: '开始执行', detail: `${activeExecutionMode.value?.label || selectedExecutionMode.value} / ${activeAccessScope.value?.label || selectedAccessScope.value} / ${effectiveRetrievalModeLabel.value}`, at: new Date().toLocaleTimeString(), phase: 'start', status: 'START', accent: 'default' })
  let assistantHasRealContent = false
  let generationFailed = false
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
        assistantTextStreaming.value = true
        setMessageMotion(messages.value[assistantIndex], 'streaming')
        messages.value[assistantIndex].content += safeChunk
        await scrollToBottom()
      },
      onFinalMessage: async (message) => {
        const safeMessage = sanitizeAssistantChunk(message)
        if (!safeMessage || !messages.value[assistantIndex]) return
        messages.value[assistantIndex].content = safeMessage
        assistantHasRealContent = true
        assistantTextStreaming.value = true
        setMessageMotion(messages.value[assistantIndex], 'streaming')
        await scrollToBottom()
      },
      onEvent: async (event) => {
        if (String(event.data?.status || '').toUpperCase() === 'ERROR') {
          if (messages.value[assistantIndex]) {
            messages.value[assistantIndex].content = buildChatErrorMessage(event.detail || event.title)
            assistantHasRealContent = true
            assistantTextStreaming.value = false
            generationFailed = true
            setMessageMotion(messages.value[assistantIndex], 'error', 1800)
            pulsePetMood('error', 1600)
            await scrollToBottom()
          }
          return
        }
        if (!isAgentMode.value) return
        pushTraceEvent(event)
        await refreshToolSelectionsAfterCreation(event)
        await renderAgentProgress()
      },
      onError: (error) => {
        console.error('对话失败', error)
        generationFailed = true
        pendingAttachments.value = attachmentsForRequest
        applyFallback()
        assistantTextStreaming.value = false
        setMessageMotion(messages.value[assistantIndex], 'error', 1800)
        pulsePetMood('error', 1800)
        ElMessage.error('对话失败，请稍后重试')
        isGenerating.value = false
      },
      onClose: () => {
        attachmentsForRequest.forEach(revokeAttachmentPreview)
        applyFallback()
        isGenerating.value = false
        assistantTextStreaming.value = false
        setMessageMotion(messages.value[assistantIndex], generationFailed ? 'error' : 'complete', generationFailed ? 1800 : 1100)
        pulsePetMood(generationFailed ? 'error' : 'success', generationFailed ? 1800 : 1300)
        emitSessionUpdated()
      },
    })
    return true
  } catch (error) {
    console.error('对话异常', error)
    pendingAttachments.value = attachmentsForRequest
    applyFallback()
    assistantTextStreaming.value = false
    setMessageMotion(messages.value[assistantIndex], 'error', 1800)
    pulsePetMood('error', 1800)
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
    if (preserveConversationOnRouteSync.value && String(newSessionId) === currentSessionId.value) {
      selectedMode.value = safeQueryValue(route.query.mode, selectedMode.value) === 'agent' ? 'agent' : 'normal'
      return
    }
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

watch(() => route.fullPath, async (newPath, oldPath) => {
  if (newPath === oldPath) return
  await appendSettingsThreadFromRoute()
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
  window.addEventListener('resize', handleViewportResize)
  window.addEventListener('pointerdown', handleAgentPickerPointerDown)
  window.addEventListener('workspace-settings-navigate', handleSettingsNavigateRequest as EventListener)
  await Promise.all([fetchExecutionConfig(), fetchModels(), fetchMcpServers()])
  const savedDefaults = loadWorkspaceDefaults()
  selectedMode.value = safeQueryValue(route.query.mode, savedDefaults.mode || 'normal') === 'agent' ? 'agent' : 'normal'
  activeAgentName.value = selectedMode.value === 'agent' ? safeQueryValue(route.query.agent_name, '') : ''
  activeAgentId.value = selectedMode.value === 'agent' ? safeQueryValue(route.query.agent_id, '') : ''
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
  await appendSettingsThreadFromRoute()
  workspaceHydrated.value = true
  ensureSettingsMutationObserver()
  await autosizeSettingsTextareas()
})

onUpdated(() => {
  ensureSettingsMutationObserver()
  void autosizeSettingsTextareas()
  void autosizeComposerTextarea()
})

watch([inputMessage, compactComposerVisible], () => {
  void autosizeComposerTextarea()
}, { flush: 'post' })

onBeforeUnmount(() => {
  window.removeEventListener('workspace-new-conversation', handleNewConversationRequest)
  window.removeEventListener('resize', handleViewportResize)
  window.removeEventListener('pointerdown', handleAgentPickerPointerDown)
  window.removeEventListener('workspace-settings-navigate', handleSettingsNavigateRequest as EventListener)
  settingsBubbleAnchorCleanup?.()
  settingsMutationObserver?.disconnect()
  if (autosizeFrame) window.cancelAnimationFrame(autosizeFrame)
  if (viewportResizeFrame) window.cancelAnimationFrame(viewportResizeFrame)
  if (viewportResizeTimer) window.clearTimeout(viewportResizeTimer)
  if (transientPetMoodTimer) window.clearTimeout(transientPetMoodTimer)
  if (settingsAnchorProgrammaticTimer) window.clearTimeout(settingsAnchorProgrammaticTimer)
  clearMessageMotionTimers()
})
</script>

<template>
  <div class="workspace-chat" :class="{ active: conversationSurfaceActive, 'session-loading': sessionHistoryLoading }">
    <div class="workspace-shell">
      <Transition name="workspace-surface">
      <div v-if="!conversationSurfaceActive" key="intro" class="intro-stack">
        <MascotPresence
          class="intro-pet"
          size="beacon"
          animated
          interactive
          aria-label="唤醒 Zuno"
          @pet-click="handleIntroPetClick"
        />
        <h1>{{ heroTitle }}</h1>
        <p>{{ heroSubtitle }}</p>
        <div class="intro-status-row" aria-label="工作台状态">
          <span class="intro-status-pill" :class="modelStatusTone">{{ modelStatusLabel }}</span>
          <span v-if="isAgentMode && activeAgentName" class="intro-status-pill subtle">Agent：{{ activeAgentName }}</span>
        </div>
        <div class="mode-switcher" :class="{ 'agent-active': selectedMode === 'agent' || agentPickerOpen }" aria-label="会话入口">
          <button :class="['mode-pill', { active: selectedMode === 'normal' && !agentPickerOpen }]" :disabled="isGenerating" @click="selectedMode = 'normal'; activeAgentName = ''; activeAgentId = ''; agentPickerOpen = false">
            Chat
          </button>
          <button :class="['mode-pill', { active: selectedMode === 'agent' || agentPickerOpen }]" :disabled="isGenerating" @click="openAgentPicker">
            Agent
          </button>
          <Transition name="agent-picker">
            <div v-if="agentPickerOpen" class="agent-picker-panel" :class="{ empty: !agentPickerLoading && agentOptions.length === 0 }" aria-label="选择 Agent">
              <div v-if="agentPickerLoading" class="agent-picker-empty">正在读取已配置的 Agent...</div>
              <template v-else>
                <button
                  v-for="agent in agentOptions"
                  :key="agent.id"
                  type="button"
                  :class="['agent-choice', { active: activeAgentId === agent.id }]"
                  @click="selectAgentOption(agent)"
                >
                  <img
                    class="agent-choice-avatar"
                    :src="agent.avatar"
                    :alt="`${agent.name} 头像`"
                    @error="handleAgentOptionAvatarError"
                  />
                  <span>
                    <strong>{{ agent.name }}</strong>
                    <small>{{ agent.description }}</small>
                  </span>
                </button>
              </template>
            </div>
          </Transition>
        </div>
      </div>
      <div
        v-else
        key="conversation"
        ref="conversationRef"
        class="conversation-panel"
        @scroll="handleConversationScroll"
        @wheel.passive="cancelSettingsBubbleAnchor"
        @touchmove.passive="cancelSettingsBubbleAnchor"
        @pointerdown.capture="lockSettingsBubbleFromEvent"
        @click.capture="lockSettingsBubbleFromEvent"
        @beforeinput.capture="lockSettingsBubbleFromEvent"
        @change.capture="lockSettingsBubbleFromEvent"
        @keydown.capture="lockSettingsBubbleFromEvent"
      >
        <div v-if="sessionHistoryLoading && !hasConversationBlocks" class="message-row assistant session-loading-row">
          <MascotPresence
            class="avatar assistant-pet-avatar"
            size="avatar"
            state="thinking"
            aria-label="Zuno"
          />
          <div class="message-bubble assistant session-loading-bubble">
            <div class="chat-message-meta">
              <strong>Zuno</strong>
              <span>正在切换</span>
            </div>
            <div class="session-loading-copy">
              <span>{{ sessionHistoryLabel }}</span>
              <i></i>
              <i></i>
              <i></i>
            </div>
          </div>
        </div>
        <template v-for="block in conversationBlocks" :key="block.type === 'message' ? `message-${block.index}` : block.thread.id">
          <div
            v-if="block.type === 'message'"
            class="message-row"
            :class="[block.message.role, block.message.motion ? `motion-${block.message.motion}` : '']"
          >
            <MascotPresence
              v-if="block.message.role === 'assistant'"
              class="avatar assistant-pet-avatar"
              size="avatar"
              :state="getAssistantMascotState(block.index)"
              aria-label="Zuno"
            />
            <div
              class="message-bubble"
              :class="[
                {
                  assistant: block.message.role === 'assistant',
                  'has-content': !!block.message.content,
                  'has-attachments': !!block.message.attachments?.length,
                  loading: block.message.role === 'assistant' && !block.message.content && isGenerating && block.index === messages.length - 1,
                },
                block.message.motion ? `motion-${block.message.motion}` : '',
              ]"
            >
              <div v-if="block.message.role === 'assistant'" class="chat-message-meta">
                <strong>Zuno</strong>
                <span v-if="shouldShowAssistantStatus(block.message, block.index)">{{ getAssistantStatusLabel(block.message, block.index) }}</span>
              </div>
              <div v-if="block.message.role === 'assistant' && !block.message.content && isGenerating && block.index === messages.length - 1" class="loading-row" :class="{ agent: isAgentMode }">
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
                <span>Zuno 正在想一想...</span>
              </template>
            </div>
            <div
              v-else-if="block.message.content"
              class="message-content"
              :class="block.message.role === 'assistant' ? 'zuno-prose' : 'user-prose'"
            >
              <MdPreview :editorId="`workspace-message-${block.index}`" :modelValue="normalizeMessageMarkdown(block.message.content)" />
            </div>
            <div v-if="block.message.attachments?.length" class="message-attachments">
              <a
                v-for="attachment in block.message.attachments"
                :key="attachment.id || attachment.url || attachment.name"
                class="message-attachment-card"
                :class="{ image: isImageAttachment(attachment) }"
                :href="attachment.url"
                target="_blank"
                rel="noreferrer"
              >
                <img v-if="isImageAttachment(attachment)" :src="attachment.preview_url || attachment.url" :alt="attachment.name" class="message-attachment-thumb" />
                <span v-else class="message-attachment-file">FILE</span>
                <span class="message-attachment-copy">
                  <strong>{{ attachment.name }}</strong>
                  <small>{{ formatAttachmentSize(attachment.size) }}</small>
                </span>
              </a>
            </div>
            <div v-if="block.message.content" class="message-actions" aria-label="消息操作">
              <button type="button" class="message-action" title="复制" aria-label="复制消息" @click.stop="copyMessageContent(block.message)">
                <el-icon><CopyDocument /></el-icon>
              </button>
            </div>
          </div>
            <img v-if="block.message.role === 'user'" :src="userAvatarSrc" alt="User" class="avatar" @error="handleAvatarError" />
          </div>
          <div v-else class="settings-thread-block">
            <div
              v-for="turn in block.thread.commandVisible ? block.thread.commandTurns : []"
              :key="turn.id"
              class="message-row user settings-command-row settings-turn-enter"
            >
              <div class="message-bubble settings-command settings-command-refresh">{{ turn.command }}</div>
              <img :src="userAvatarSrc" alt="User" class="avatar" @error="handleAvatarError" />
            </div>
            <article
              v-if="block.thread.assistantVisible"
              class="message-row assistant settings-panel-row settings-turn-enter assistant"
            >
              <MascotPresence
                class="avatar assistant-pet-avatar"
                size="avatar"
                :state="getSettingsMascotState(block.thread)"
                aria-label="Zuno"
              />
              <div class="settings-message-stack" :class="{ 'is-loading': !block.thread.ready }">
                <div v-if="!block.thread.ready" class="message-bubble assistant loading motion-thinking settings-loading-bubble" aria-live="polite">
                  <div class="chat-message-meta settings-loading-meta">
                    <strong>Zuno</strong>
                    <span>{{ getThreadLoadingVerb(block.thread) }}</span>
                  </div>
                  <div class="loading-row settings-loading-row">
                    <span class="spinner"></span>
                    <span>{{ getThreadLoadingText(block.thread) }}</span>
                    <i></i>
                    <i></i>
                    <i></i>
                  </div>
                </div>
                <div v-else class="settings-message-meta">
                  <strong>Zuno</strong>
                  <span>{{ `${block.thread.label} 已打开` }}</span>
                </div>
                <div class="settings-bubble-shell" :class="{ 'is-ready': block.thread.ready }">
                  <section
                    class="settings-bubble"
                    :data-settings-thread-id="block.thread.id"
                    :data-settings-section="block.thread.section"
                    :data-settings-route="block.thread.routeName"
                    :data-settings-detail="block.thread.detail ? 'true' : 'false'"
                    :style="{ '--settings-page-icon': `url(${block.thread.icon})` }"
                  >
                    <div v-if="canNavigateSettingsThreadBack(block.thread)" class="settings-bubble-toolbar">
                      <button
                        class="settings-bubble-nav-button"
                        type="button"
                        title="返回上一级"
                        aria-label="返回上一级"
                        @click="handleSettingsThreadBack(block.thread)"
                      >
                        <el-icon><ArrowLeft /></el-icon>
                      </button>
                    </div>
                    <Transition name="settings-page-switch">
                      <component :is="block.thread.component" :key="block.thread.routeKey" />
                    </Transition>
                  </section>
                </div>
              </div>
            </article>
          </div>
        </template>
      </div>
      </Transition>
      <div class="composer-dock" :class="{ fixed: conversationSurfaceActive }">
        <button v-if="compactComposerVisible" class="composer-collapsed" type="button" @click="expandComposer">
          <img class="composer-collapsed-icon" :src="messageIcon" alt="" aria-hidden="true" />
          <span>给 Zuno 发消息</span>
        </button>
        <div
          v-else
          class="composer-shell"
          :class="{ 'drag-active': isAttachmentDragOver, 'is-sending': isGenerating }"
          @focusout="handleComposerFocusOut"
          @dragover.prevent="handleAttachmentDragOver"
          @dragleave="handleAttachmentDragLeave"
          @drop.prevent="handleAttachmentDrop"
        >
          <div class="composer-top" :class="{ compact: compactPanel }">
            <div class="composer-actions">
              <button v-if="isAgentMode && compactPanel" class="ghost-pill subtle" type="button" @click="showTracePanel = !showTracePanel"><el-icon><ArrowDown v-if="showTracePanel" /><ArrowUp v-else /></el-icon>{{ showTracePanel ? '收起进展' : '查看进展' }}</button>
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
          <textarea ref="composerInputRef" v-model="inputMessage" class="composer" :rows="compactPanel ? 1 : 2" :placeholder="composerPlaceholder" @focus="handleComposerFocus" @keydown="handleKeydown" @paste="handleComposerPaste" />
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
      <p v-if="!hasConversationBlocks" class="composer-disclaimer">重要信息仍建议核验。</p>
    </div>
  </div>
</div>
</template>

<style scoped>
.workspace-chat {
  flex: 1;
  height: 100%;
  min-height: 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fffdf9;
}

.workspace-shell {
  flex: 1;
  height: 100%;
  min-height: 0;
  min-width: 0;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0 18px 24px;
  overflow: hidden;
  align-items: stretch;
}

.workspace-chat:not(.active) .workspace-shell {
  justify-content: center;
  align-items: center;
}

.workspace-chat:not(.active) .composer-dock {
  background: transparent;
  width: 100%;
}

.workspace-chat:not(.active) .composer-shell {
  width: min(720px, calc(100% - 24px));
}

.intro-stack {
  flex: 0 0 auto;
  min-height: 0;
  display: grid;
  align-content: center;
  justify-items: center;
  gap: 16px;
  padding: 0 0 22px;
  text-align: center;
  width: 100%;
  min-width: 0;
  overflow: hidden;
}

.intro-stack h1 {
  margin: 0;
  color: #171717;
  font-family: inherit;
  max-width: 100%;
  font-size: 32px;
  font-weight: 520;
  line-height: 1.2;
  letter-spacing: 0;
  overflow-wrap: anywhere;
}

.mode-switcher {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
  max-width: 100%;
}

.mode-pill {
  border: 1px solid rgba(214, 214, 214, 0.9);
  background: #fff;
  color: #404040;
  border-radius: 999px;
  padding: 6px 13px;
  cursor: pointer;
  font-size: 13px;
}

.mode-pill.active {
  background: #171717;
  border-color: #171717;
  color: #fff;
}

.workspace-surface-enter-active,
.workspace-surface-leave-active {
  transition:
    opacity 0.26s cubic-bezier(0.2, 0.78, 0.22, 1),
    transform 0.3s cubic-bezier(0.2, 0.78, 0.22, 1),
    filter 0.3s ease;
}

.workspace-surface-leave-active {
  position: absolute;
  inset: 0 18px 24px;
  z-index: 1;
  width: auto;
  pointer-events: none;
}

.workspace-surface-enter-active {
  position: relative;
  z-index: 2;
}

.workspace-surface-enter-from,
.workspace-surface-leave-to {
  opacity: 0;
  filter: blur(7px);
}

.workspace-surface-enter-from {
  transform: translateY(14px) scale(0.992);
}

.workspace-surface-leave-to {
  transform: translateY(-10px) scale(0.996);
}

.conversation-panel {
  flex: 1 1 auto;
  width: min(860px, calc(100% - 24px));
  margin: 0 auto;
  min-height: 0;
  min-width: 0;
  overflow-y: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 24px 0 10px;
  overflow-anchor: none;
  scrollbar-gutter: stable both-edges;
}

.session-loading-row {
  padding-top: 16px;
  animation: settingsTurnIn 0.24s cubic-bezier(0.2, 0.78, 0.22, 1) both;
}

.session-loading-bubble {
  width: fit-content;
  min-width: min(230px, calc(100% - 44px));
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.86), rgba(255, 247, 237, 0.56)),
    rgba(245, 158, 11, 0.08) !important;
  border-color: rgba(245, 158, 11, 0.16) !important;
}

.session-loading-copy {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #64748b;
  font-size: 13px;
  line-height: 1.4;
}

.session-loading-copy i {
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.68);
  animation: settingsThinkingDot 1s ease-in-out infinite;
}

.session-loading-copy i:nth-child(3) {
  animation-delay: 0.14s;
}

.session-loading-copy i:nth-child(4) {
  animation-delay: 0.28s;
}

.workspace-chat.session-loading .conversation-panel {
  animation: sessionPanelAwake 0.34s cubic-bezier(0.2, 0.78, 0.22, 1) both;
}

.message-row {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  min-width: 0;
  max-width: 100%;
  overflow-anchor: none;
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
  min-width: 0;
  max-width: min(720px, calc(100% - 44px));
  padding: 9px 12px;
  border-radius: 18px;
  background: #f1f1f1;
  color: #171717;
  font-size: 14px;
  line-height: 1.6;
}

.message-bubble.assistant {
  background: transparent;
  color: #171717;
  border: none;
  padding-left: 2px;
  box-shadow: none;
  backdrop-filter: none;
}

.message-bubble.assistant.loading {
  min-width: min(320px, calc(100% - 44px));
}

.settings-thread-block {
  display: grid;
  gap: 8px;
  min-width: 0;
  overflow-anchor: none;
}

.settings-command-row {
  margin-top: 12px;
}

.settings-command-row + .settings-command-row {
  margin-top: 0;
}

.settings-turn-enter {
  animation: settingsTurnIn 0.28s cubic-bezier(0.2, 0.78, 0.22, 1) both;
}

.settings-turn-enter.assistant {
  animation-delay: 0.04s;
}

.settings-command {
  max-width: min(420px, calc(100% - 44px));
  background: #f59e0b;
  color: #ffffff;
  border: none;
  box-shadow: 0 10px 22px rgba(245, 158, 11, 0.16);
}

.settings-command-refresh {
  animation: settingsCommandPulse 0.24s cubic-bezier(0.2, 0.78, 0.22, 1) both;
}

.settings-panel-row {
  align-items: flex-start;
}

.settings-message-stack {
  position: relative;
  min-width: 0;
  width: min(860px, calc(100% - 58px));
  display: grid;
  gap: 8px;
}

.settings-message-meta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding-left: 2px;
  color: #64748b;
  font-size: 12px;
}

.settings-message-meta strong {
  color: #0f172a;
  font-size: 13px;
  font-weight: 650;
}

.settings-bubble-shell {
  min-width: 0;
  display: block;
  opacity: 0;
  transform: translateY(5px);
  visibility: hidden;
  position: absolute;
  left: 0;
  right: 0;
  overflow: visible;
  max-width: 100%;
  overflow-anchor: none;
  transition:
    opacity 0.16s ease,
    transform 0.2s cubic-bezier(0.2, 0.78, 0.22, 1);
}

.settings-bubble-shell.is-ready {
  position: relative;
  left: auto;
  right: auto;
  visibility: visible;
  opacity: 1;
  transform: translateY(0);
  overflow: visible;
}

.settings-bubble-shell > .settings-bubble {
  min-height: 0;
  overflow: visible;
}

.settings-bubble-shell:not(.is-ready) {
  pointer-events: none;
}

.settings-bubble-shell:not(.is-ready) > .settings-bubble {
  pointer-events: none;
}

.settings-bubble-shell.is-ready > .settings-bubble {
  overflow: visible;
}

.settings-bubble {
  position: relative;
  min-width: 0;
  max-width: 100%;
  padding: 24px 28px;
  max-height: none;
  overflow: visible;
  overscroll-behavior: auto;
  overflow-anchor: none;
  border-radius: var(--zuno-radius-composer);
  border: 1px solid var(--zuno-glass-border);
  background: var(--zuno-glass-surface);
  box-shadow: var(--zuno-shadow-composer), inset 0 1px 0 rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(28px);
  opacity: 1;
  transition: opacity 0.12s ease-out;
}

.settings-bubble-toolbar {
  position: absolute;
  top: 18px;
  right: 22px;
  z-index: 8;
  display: flex;
  justify-content: flex-end;
  margin: 0;
  pointer-events: none;
}

.settings-bubble-nav-button {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  width: 30px;
  height: 30px;
  padding: 0;
  border: 1px solid rgba(226, 232, 240, 0.9);
  border-radius: 999px;
  color: #b45309;
  font-size: 12px;
  font-weight: 590;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(255, 247, 237, 0.78)),
    rgba(255, 255, 255, 0.72);
  box-shadow:
    0 10px 22px -18px rgba(146, 64, 14, 0.42),
    inset 0 1px 0 rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(14px);
  cursor: pointer;
  pointer-events: auto;
  transition:
    transform 0.16s ease,
    border-color 0.16s ease,
    box-shadow 0.16s ease;
}

.settings-bubble-nav-button:hover {
  transform: translateY(-1px);
  border-color: rgba(245, 158, 11, 0.42);
  box-shadow:
    0 14px 28px -20px rgba(146, 64, 14, 0.48),
    inset 0 1px 0 rgba(255, 255, 255, 0.94);
}

.settings-bubble-nav-button .el-icon {
  font-size: 13px;
}

.settings-page-switch-enter-active,
.settings-page-switch-leave-active {
  transition:
    opacity 0.14s ease,
    transform 0.16s cubic-bezier(0.2, 0.78, 0.22, 1);
}

.settings-page-switch-enter-active {
  position: relative;
  z-index: 2;
}

.settings-page-switch-leave-active {
  position: absolute;
  inset: 24px 28px;
  z-index: 1;
  width: calc(100% - 56px);
  pointer-events: none;
}

.settings-page-switch-enter-from {
  opacity: 0;
  transform: translateY(4px);
}

.settings-page-switch-leave-to {
  opacity: 0;
  transform: translateY(-3px);
}

.settings-bubble :deep(.settings-panel-enter-active),
.settings-bubble :deep(.settings-panel-leave-active) {
  transition:
    opacity 0.16s ease,
    transform 0.18s cubic-bezier(0.2, 0.78, 0.22, 1) !important;
}

.settings-bubble :deep(.settings-panel-enter-from),
.settings-bubble :deep(.settings-panel-leave-to) {
  opacity: 0 !important;
  transform: translateY(-4px) !important;
}

.settings-bubble[data-settings-detail='true'] :deep(.agent-editor-page .header-actions),
.settings-bubble[data-settings-detail='true'] :deep(.knowledge-file-page .header-actions),
.settings-bubble[data-settings-detail='true'] :deep(.knowledge-config-page .hero-actions) {
  margin-right: 40px !important;
}

.settings-bubble :deep(.agent-page),
.settings-bubble :deep(.agent-editor-page),
.settings-bubble :deep(.model-page),
.settings-bubble :deep(.knowledge-page),
.settings-bubble :deep(.knowledge-file-page),
.settings-bubble :deep(.knowledge-config-page),
.settings-bubble :deep(.mcp-page),
.settings-bubble :deep(.tool-page),
.settings-bubble :deep(.skill-page),
.settings-bubble :deep(.dashboard-page),
.settings-bubble :deep(.profile-page),
.settings-bubble :deep(.conversation-archive-page) {
  max-width: none;
  margin: 0;
  padding: 0 !important;
  gap: 14px !important;
  overflow: visible !important;
  max-height: none !important;
  font-family: var(--zuno-font-sans);
}

.settings-bubble :deep(.el-scrollbar),
.settings-bubble :deep(.el-scrollbar__wrap),
.settings-bubble :deep(.el-scrollbar__view),
.settings-bubble :deep(.el-dialog__body),
.settings-bubble :deep(.el-drawer__body),
.settings-bubble :deep(.el-table__inner-wrapper),
.settings-bubble :deep(.el-table__body-wrapper),
.settings-bubble :deep(.param-list),
.settings-bubble :deep(.trace-list),
.settings-bubble :deep(.event-list),
.settings-bubble :deep(.rank-list),
.settings-bubble :deep(.file-grid),
.settings-bubble :deep(.model-grid),
.settings-bubble :deep(.skill-grid),
.settings-bubble :deep(.tool-grid),
.settings-bubble :deep(.server-list) {
  max-height: none !important;
  height: auto !important;
  overflow: visible !important;
}

.settings-bubble :deep(.el-scrollbar__bar) {
  display: none !important;
}

.settings-bubble :deep(.el-overlay),
.settings-bubble :deep(.el-overlay-dialog) {
  position: static !important;
  inset: auto !important;
  display: block !important;
  width: 100% !important;
  height: auto !important;
  margin: 0 !important;
  background: transparent !important;
  overflow: visible !important;
}

.settings-bubble :deep(.el-dialog) {
  width: 100% !important;
  max-width: none !important;
  margin: 8px 0 0 !important;
  border-radius: 16px !important;
  border: 1px solid rgba(226, 232, 240, 0.74) !important;
  background: rgba(255, 255, 255, 0.5) !important;
  box-shadow: none !important;
  transform-origin: calc(100% - 34px) 0;
  will-change: transform, opacity;
}

.settings-bubble :deep(.el-drawer) {
  position: static !important;
  width: 100% !important;
  max-width: none !important;
  height: auto !important;
  margin: 8px 0 0 !important;
  border-radius: 16px !important;
  border: 1px solid rgba(226, 232, 240, 0.74) !important;
  background: rgba(255, 255, 255, 0.5) !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.el-dialog__header),
.settings-bubble :deep(.el-dialog__body),
.settings-bubble :deep(.el-dialog__footer),
.settings-bubble :deep(.el-drawer__header),
.settings-bubble :deep(.el-drawer__body) {
  padding: 10px 12px !important;
}

.settings-bubble :deep(.el-dialog__header),
.settings-bubble :deep(.el-drawer__header) {
  border-bottom: 1px solid rgba(226, 232, 240, 0.68) !important;
  margin: 0 !important;
}

.settings-bubble :deep(.el-dialog__footer) {
  border-top: 1px solid rgba(226, 232, 240, 0.68) !important;
}

.settings-bubble :deep(.dialog-fade-enter-active),
.settings-bubble :deep(.dialog-fade-leave-active) {
  transition: opacity 160ms ease !important;
}

.settings-bubble :deep(.dialog-fade-enter-active .el-dialog),
.settings-bubble :deep(.dialog-fade-leave-active .el-dialog) {
  transition:
    opacity 170ms ease,
    transform 210ms cubic-bezier(0.2, 0.78, 0.22, 1) !important;
}

.settings-bubble :deep(.dialog-fade-enter-from),
.settings-bubble :deep(.dialog-fade-leave-to) {
  opacity: 0 !important;
}

.settings-bubble :deep(.dialog-fade-enter-from .el-dialog),
.settings-bubble :deep(.dialog-fade-leave-to .el-dialog) {
  opacity: 0 !important;
  transform: translateY(-6px) scale(0.992) !important;
}

.settings-bubble :deep(.dialog-fade-enter-to .el-dialog),
.settings-bubble :deep(.dialog-fade-leave-from .el-dialog) {
  opacity: 1 !important;
  transform: translateY(0) scale(1) !important;
}

.settings-bubble :deep(.agent-hero),
.settings-bubble :deep(.page-header),
.settings-bubble :deep(.page-hero),
.settings-bubble :deep(.hero-card) {
  align-items: flex-start;
  padding: 0 0 12px !important;
  border: none !important;
  border-bottom: 1px solid rgba(226, 232, 240, 0.72) !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.toolbar-card),
.settings-bubble :deep(.content-card),
.settings-bubble :deep(.table-card),
.settings-bubble :deep(.list-card),
.settings-bubble :deep(.agent-card),
.settings-bubble :deep(.editor-card),
.settings-bubble :deep(.side-card),
.settings-bubble :deep(.logo-panel),
.settings-bubble :deep(.model-card),
.settings-bubble :deep(.knowledge-card),
.settings-bubble :deep(.mcp-card),
.settings-bubble :deep(.tool-card),
.settings-bubble :deep(.skill-card),
.settings-bubble :deep(.kpi-card),
.settings-bubble :deep(.panel-card),
.settings-bubble :deep(.config-panel),
.settings-bubble :deep(.config-card),
.settings-bubble :deep(.preview-card),
.settings-bubble :deep(.form-card),
.settings-bubble :deep(.summary-card),
.settings-bubble :deep(.summary-block) {
  border: 1px solid rgba(226, 232, 240, 0.82) !important;
  border-radius: var(--zuno-radius-card) !important;
  background: var(--zuno-glass-card) !important;
  box-shadow: var(--zuno-shadow-card), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
  backdrop-filter: blur(18px);
}

.settings-bubble :deep(.content-card),
.settings-bubble :deep(.table-card),
.settings-bubble :deep(.list-card),
.settings-bubble :deep(.toolbar-card),
.settings-bubble :deep(.editor-card),
.settings-bubble :deep(.side-card),
.settings-bubble :deep(.form-card),
.settings-bubble :deep(.summary-card),
.settings-bubble :deep(.config-panel),
.settings-bubble :deep(.preview-card) {
  padding: 12px !important;
}

.settings-bubble :deep(.hero-actions),
.settings-bubble :deep(.header-actions),
.settings-bubble :deep(.card-actions),
.settings-bubble :deep(.filter-bar),
.settings-bubble :deep(.toolbar-card) {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: center !important;
  gap: 10px !important;
}

.settings-bubble :deep(h1),
.settings-bubble :deep(h2),
.settings-bubble :deep(h3) {
  color: #0f172a !important;
  letter-spacing: 0 !important;
}

.settings-bubble :deep(h1),
.settings-bubble :deep(.agent-hero h2),
.settings-bubble :deep(.hero-card h2),
.settings-bubble :deep(.page-hero h1) {
  margin: 0 !important;
  font-size: 21px !important;
  font-weight: 650 !important;
  line-height: 1.2 !important;
}

.settings-bubble :deep(h2) {
  font-size: 16px !important;
  font-weight: 650 !important;
}

.settings-bubble :deep(h3),
.settings-bubble :deep(.card-title),
.settings-bubble :deep(.side-title-row strong),
.settings-bubble :deep(.profile-meta strong) {
  font-size: 14px !important;
  font-weight: 620 !important;
}

.settings-bubble :deep(p),
.settings-bubble :deep(.meta-row),
.settings-bubble :deep(.scope-text),
.settings-bubble :deep(.skill-meta),
.settings-bubble :deep(.summary-item span),
.settings-bubble :deep(.card-subtitle),
.settings-bubble :deep(.profile-meta span),
.settings-bubble :deep(.empty-text),
.settings-bubble :deep(.tool-description),
.settings-bubble :deep(.server-subtitle),
.settings-bubble :deep(.server-hint) {
  color: #64748b !important;
  font-size: 12.5px !important;
  line-height: 1.5 !important;
}

.settings-bubble :deep(.eyebrow),
.settings-bubble :deep(.empty-kicker),
.settings-bubble :deep(.official-badge),
.settings-bubble :deep(.badge),
.settings-bubble :deep(.config-badge),
.settings-bubble :deep(.meta-pill),
.settings-bubble :deep(.meta-badge),
.settings-bubble :deep(.hint-chip),
.settings-bubble :deep(.official-tag),
.settings-bubble :deep(.status-pill),
.settings-bubble :deep(.el-tag) {
  border-radius: 999px !important;
  border-color: rgba(245, 158, 11, 0.22) !important;
  background: rgba(245, 158, 11, 0.08) !important;
  color: #b45309 !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  letter-spacing: 0 !important;
}

.settings-bubble :deep(.agent-grid),
.settings-bubble :deep(.model-grid),
.settings-bubble :deep(.knowledge-grid),
.settings-bubble :deep(.skill-grid),
.settings-bubble :deep(.kpi-grid),
.settings-bubble :deep(.content-grid) {
  display: grid !important;
  gap: 10px !important;
}

.settings-bubble :deep(.agent-grid),
.settings-bubble :deep(.model-grid),
.settings-bubble :deep(.knowledge-grid),
.settings-bubble :deep(.skill-grid) {
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)) !important;
}

.settings-bubble :deep(.content-grid) {
  grid-template-columns: minmax(0, 1.35fr) minmax(220px, 0.82fr) minmax(220px, 0.82fr) !important;
}

.settings-bubble :deep(.tool-row) {
  display: grid !important;
  grid-template-columns: 38px minmax(0, 1fr) auto !important;
  align-items: center !important;
  gap: 12px !important;
  padding: 11px !important;
  border-radius: var(--zuno-radius-card) !important;
  border: 1px solid rgba(226, 232, 240, 0.82) !important;
  background: var(--zuno-glass-card) !important;
  box-shadow: var(--zuno-shadow-card), inset 0 1px 0 rgba(255, 255, 255, 0.9) !important;
}

.settings-bubble :deep(.server-table) {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 8px;
}

.settings-bubble :deep(.server-table th) {
  color: #94a3b8;
  font-size: 11.5px;
  font-weight: 560;
  text-align: left;
}

.settings-bubble :deep(.server-table td) {
  padding: 9px 10px !important;
  background: rgba(255, 255, 255, 0.78);
  border-top: 1px solid rgba(226, 232, 240, 0.78);
  border-bottom: 1px solid rgba(226, 232, 240, 0.78);
}

.settings-bubble :deep(.server-table td:first-child) {
  border-left: 1px solid rgba(226, 232, 240, 0.78);
  border-radius: 8px 0 0 8px;
}

.settings-bubble :deep(.server-table td:last-child) {
  border-right: 1px solid rgba(226, 232, 240, 0.78);
  border-radius: 0 8px 8px 0;
}

.settings-bubble :deep(.page-icon),
.settings-bubble :deep(.title-icon),
.settings-bubble :deep(.header-icon) {
  width: 36px !important;
  height: 36px !important;
  border-radius: 12px !important;
}

.settings-bubble :deep(.title-block),
.settings-bubble :deep(.header-left),
.settings-bubble :deep(.card-top),
.settings-bubble :deep(.skill-title-wrap),
.settings-bubble :deep(.server-cell) {
  gap: 10px !important;
}

.settings-bubble :deep(.avatar-wrap),
.settings-bubble :deep(.logo-wrap),
.settings-bubble :deep(.skill-icon-wrap),
.settings-bubble :deep(.server-logo) {
  width: 40px !important;
  height: 40px !important;
  border-radius: 12px !important;
}

.settings-bubble :deep(.meta-grid),
.settings-bubble :deep(.summary-grid),
.settings-bubble :deep(.field-grid),
.settings-bubble :deep(.dialog-grid),
.settings-bubble :deep(.basic-grid),
.settings-bubble :deep(.options-grid) {
  gap: 10px !important;
}

.settings-bubble :deep(.model-card),
.settings-bubble :deep(.knowledge-card),
.settings-bubble :deep(.agent-card),
.settings-bubble :deep(.skill-card),
.settings-bubble :deep(.kpi-card) {
  min-height: 0 !important;
  padding: 12px !important;
}

.settings-bubble :deep(.card-footer),
.settings-bubble :deep(.tool-side),
.settings-bubble :deep(.skill-actions),
.settings-bubble :deep(.row-actions),
.settings-bubble :deep(.action-row) {
  gap: 8px !important;
}

.settings-bubble :deep(.el-button) {
  min-height: 32px;
  border-radius: var(--zuno-radius-control);
  padding: 7px 11px;
  font-size: 12.5px;
  font-weight: 500;
}

.settings-bubble :deep(.el-button--primary) {
  --el-button-bg-color: #f59e0b;
  --el-button-border-color: #f59e0b;
  --el-button-hover-bg-color: #d97706;
  --el-button-hover-border-color: #d97706;
  --el-button-active-bg-color: #b45309;
  --el-button-active-border-color: #b45309;
  box-shadow: 0 8px 18px rgba(245, 158, 11, 0.16);
}

.settings-bubble :deep(.header-actions .el-button--primary.is-circle),
.settings-bubble :deep(.hero-actions .el-button--primary.is-circle),
.settings-bubble :deep(.inline-form-actions .el-button--primary.is-circle),
.settings-bubble :deep(.inline-panel-actions .el-button--primary.is-circle),
.settings-bubble :deep(.workbench-actions .el-button--primary.is-circle),
.settings-bubble :deep(.panel-actions .el-button--primary.is-circle) {
  width: 36px !important;
  height: 36px !important;
  min-width: 36px !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 999px !important;
  background: #f59e0b !important;
  color: #fff !important;
  box-shadow:
    0 12px 24px rgba(245, 158, 11, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.32) !important;
}

.settings-bubble :deep(.is-create-open .el-icon) {
  transform: rotate(45deg);
  transition: transform 180ms cubic-bezier(.2, .8, .2, 1);
}

.settings-bubble :deep(.el-input__wrapper),
.settings-bubble :deep(.el-textarea__inner),
.settings-bubble :deep(.el-select__wrapper) {
  min-height: 32px;
  border-radius: var(--zuno-radius-control) !important;
  background: rgba(255, 255, 255, 0.88) !important;
  box-shadow:
    inset 0 0 0 1px rgba(226, 232, 240, 0.92),
    inset 0 1px 0 rgba(255, 255, 255, 0.98),
    0 8px 18px -16px rgba(15, 23, 42, 0.2) !important;
}

.settings-bubble :deep(.el-input__inner),
.settings-bubble :deep(.el-textarea__inner),
.settings-bubble :deep(.el-select__selected-item),
.settings-bubble :deep(.el-select__placeholder) {
  font-size: 12.5px !important;
}

.settings-bubble :deep(.tool-config-bubble .el-form-item) {
  display: block !important;
  grid-template-columns: none !important;
  margin-bottom: 10px !important;
}

.settings-bubble :deep(.tool-config-bubble .el-form-item__label) {
  float: none !important;
  display: flex !important;
  width: auto !important;
  min-width: 0 !important;
  height: auto !important;
  margin: 0 0 5px !important;
  padding: 0 !important;
  justify-content: flex-start !important;
  line-height: 1.2 !important;
}

.settings-bubble :deep(.tool-config-bubble .el-form-item__content) {
  display: block !important;
  margin-left: 0 !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.empty-state) {
  border: 1px dashed rgba(203, 213, 225, 0.95) !important;
  border-radius: var(--zuno-radius-card) !important;
  background: rgba(248, 250, 252, 0.56) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.76) !important;
}

.settings-bubble :deep(.logo-preview),
.settings-bubble :deep(.side-avatar),
.settings-bubble :deep(.summary-item),
.settings-bubble :deep(.logo-wrap),
.settings-bubble :deep(.avatar-wrap),
.settings-bubble :deep(.server-logo),
.settings-bubble :deep(.skill-icon-wrap) {
  border-color: rgba(226, 232, 240, 0.9) !important;
  background: #ffffff !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.empty-visual) {
  filter: saturate(0.82);
  transform: scale(0.88);
}

.settings-bubble :deep(.el-table) {
  --el-table-border-color: rgba(226, 232, 240, 0.72);
  --el-table-header-bg-color: rgba(248, 250, 252, 0.9);
  --el-table-row-hover-bg-color: rgba(245, 158, 11, 0.045);
  border-radius: 8px;
  overflow: hidden;
}

@keyframes settingsTurnIn {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.985);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes settingsCommandPulse {
  from {
    opacity: 0;
    transform: translateY(7px) scale(0.985);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes settingsThinkingDot {
  0%,
  80%,
  100% {
    opacity: 0.34;
    transform: translateY(0);
  }

  38% {
    opacity: 1;
    transform: translateY(-2px);
  }
}

@keyframes sessionPanelAwake {
  from {
    opacity: 0.96;
    transform: translateY(4px);
    filter: blur(2px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
    filter: blur(0);
  }
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
  background: transparent;
}

.composer-dock.fixed {
  position: sticky;
  bottom: 0;
  padding-top: 6px;
}

.composer-shell {
  width: min(780px, calc(100% - 24px));
  min-width: 0;
  margin: 0 auto;
  padding: 10px 12px 11px;
  border-radius: 22px;
  border: 1px solid rgba(215, 215, 215, 0.95);
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(10px);
  transition: border-color 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.composer-shell:focus-within {
  border-color: rgba(23, 23, 23, 0.24);
  box-shadow: 0 14px 42px rgba(0, 0, 0, 0.12);
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
  margin-bottom: 0;
  justify-content: flex-end;
  min-height: 0;
}

.composer-top.compact {
  justify-content: flex-end;
  margin-bottom: 2px;
}

.workspace-chat:not(.active) .composer-top {
  display: none;
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
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.ghost-pill,
.attach-btn {
  border: none;
  background: transparent;
  color: #4a4a4a;
  border-radius: 999px;
  padding: 4px 7px;
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
  min-height: 36px;
  max-height: 92px;
  padding: 8px 4px;
  resize: none;
  outline: none;
  color: #171717;
  line-height: 1.45;
  font-size: 15px;
  border: none;
  background: transparent;
}

.composer-footer {
  margin-top: 2px;
}

.send-btn {
  min-width: 48px;
  height: 32px;
  border: none;
  border-radius: 999px;
  background: #171717;
  color: #fff;
  font-size: 12px;
  cursor: pointer;
}

.message-bubble :deep(.md-editor-preview) {
  background: transparent !important;
  color: inherit;
  font-size: 12px;
  line-height: 1.42;
}

.message-bubble :deep(.md-editor) {
  background: transparent !important;
}

.message-bubble :deep(.md-editor-preview-wrapper) {
  background: transparent !important;
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
    max-width: min(100%, calc(100% - 44px));
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

  .intro-stack h1 {
    font-size: 28px;
  }

  .conversation-panel {
    width: 100%;
    padding-top: 14px;
  }

  .composer-shell {
    width: 100%;
    padding: 6px 7px;
    border-radius: 14px;
  }

  .message-bubble {
    max-width: min(100%, calc(100% - 44px));
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
    min-width: min(260px, calc(100% - 44px));
  }
}

.workspace-chat {
  background:
    radial-gradient(circle at 56% 26%, rgba(255, 255, 255, 0.92), transparent 34%),
    linear-gradient(135deg, #fbfbfd 0%, #f5f6f8 52%, #ffffff 100%);
}

.workspace-shell {
  padding: 44px 48px 28px;
}

.workspace-chat:not(.active) .workspace-shell {
  justify-content: flex-end;
  padding-bottom: 34px;
}

.intro-stack {
  gap: 20px;
  padding-bottom: 34px;
}

.hero-glyph {
  width: 78px;
  height: 78px;
  display: grid;
  place-items: center;
  border-radius: 24px;
  color: #f59e0b;
  background: linear-gradient(180deg, rgba(255, 251, 235, 0.96), rgba(255, 246, 218, 0.9));
  border: 1px solid rgba(255, 255, 255, 0.9);
  box-shadow:
    0 24px 54px rgba(245, 158, 11, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.92);
  font-size: 42px;
  line-height: 1;
}

.intro-stack h1 {
  color: #111827;
  font-size: clamp(34px, 3.2vw, 48px);
  font-weight: 720;
  line-height: 1.08;
  letter-spacing: 0;
}

.intro-stack p {
  max-width: 720px;
  margin: -4px 0 0;
  color: #3f3024;
  font-size: 20px;
  line-height: 1.55;
}

.mode-switcher {
  margin-top: 172px;
  padding: 6px;
  gap: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.64);
  border: 1px solid rgba(226, 232, 240, 0.72);
  box-shadow:
    0 16px 32px rgba(15, 23, 42, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.84);
  backdrop-filter: blur(24px);
}

.mode-pill {
  min-width: 98px;
  height: 38px;
  border: none;
  border-radius: 999px;
  padding: 0 22px;
  background: transparent;
  color: #52657f;
  font-size: 16px;
  font-weight: 650;
}

.mode-pill.active,
.mode-pill:hover {
  color: #ffffff;
  background: #f59e0b;
  box-shadow: 0 12px 24px rgba(245, 158, 11, 0.22);
}

.workspace-chat:not(.active) .composer-dock {
  width: 100%;
  padding-top: 0;
  background: transparent;
}

.workspace-chat:not(.active) .composer-shell,
.composer-shell {
  width: min(1120px, calc(100% - 40px));
  min-height: 236px;
  padding: 38px 42px 34px;
  border-radius: 36px;
  border: 1px solid rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.74);
  box-shadow:
    0 30px 80px rgba(15, 23, 42, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(30px);
}

.composer-shell:focus-within {
  border-color: rgba(245, 158, 11, 0.34);
  box-shadow:
    0 34px 88px rgba(15, 23, 42, 0.1),
    0 0 0 4px rgba(245, 158, 11, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.94);
}

.composer {
  min-height: 120px;
  color: #111827;
  font-size: 18px;
}

.composer::placeholder {
  color: #8ba0bd;
}

.composer-footer {
  align-items: flex-end;
}

.attach-btn,
.ghost-pill {
  color: #52657f;
  font-size: 16px;
  font-weight: 650;
}

.composer-meta,
.attachment-hint,
.composer-hint,
.retrieval-hint {
  color: #8ba0bd;
}

.send-btn {
  min-width: 116px;
  height: 50px;
  border-radius: 999px;
  background: #f59e0b;
  color: #ffffff;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 18px 32px rgba(245, 158, 11, 0.24);
}

.send-btn:hover:not(:disabled) {
  background: #e89105;
}

.conversation-panel {
  width: min(920px, calc(100% - 40px));
  padding-top: 20px;
}

.message-bubble {
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(226, 232, 240, 0.74);
  box-shadow: 0 18px 38px rgba(15, 23, 42, 0.06);
}

.message-row.user .message-bubble {
  background: #f59e0b;
  color: #ffffff;
  border-color: transparent;
}

@media (max-width: 900px) {
  .workspace-shell {
    padding: 74px 16px 18px;
  }

  .mode-switcher {
    margin-top: 54px;
  }

  .workspace-chat:not(.active) .composer-shell,
  .composer-shell {
    width: 100%;
    min-height: 188px;
    padding: 24px 22px;
    border-radius: 26px;
  }

  .composer-footer,
  .composer-footer-left {
    flex-direction: row;
    align-items: center;
  }
}

/* Minimal workspace refinement, matched to the Stitch main-page proportions. */
.workspace-chat {
  font-family: var(--zuno-font-sans);
  background:
    radial-gradient(circle at 58% 24%, rgba(255, 255, 255, 0.9), transparent 33%),
    radial-gradient(circle at 12% 92%, rgba(245, 158, 11, 0.055), transparent 30%),
    #f9f9fb;
}

.workspace-shell {
  padding: 32px 32px 28px;
}

.workspace-chat:not(.active) .workspace-shell {
  justify-content: flex-end;
  padding-bottom: 30px;
}

.intro-stack {
  max-width: 672px;
  gap: 14px;
  padding-bottom: 28px;
}

.hero-glyph {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  color: #f59e0b;
  background: linear-gradient(135deg, #fff7df 0%, #fffaf0 100%);
  border: 1px solid rgba(255, 255, 255, 0.92);
  box-shadow:
    0 18px 38px rgba(245, 158, 11, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.96);
  font-size: 34px;
}

.intro-stack h1 {
  color: #0f172a;
  font-size: 32px;
  font-weight: 600;
  line-height: 1.2;
  letter-spacing: 0;
}

.intro-stack p {
  max-width: 600px;
  margin: 0;
  color: #64748b;
  font-size: 16px;
  line-height: 1.55;
  font-weight: 400;
}

.mode-switcher {
  margin-top: 144px;
  padding: 4px;
  gap: 4px;
  border-radius: 999px;
  background: rgba(248, 250, 252, 0.82);
  border: 1px solid rgba(226, 232, 240, 0.78);
  box-shadow:
    0 10px 24px rgba(15, 23, 42, 0.045),
    inset 0 1px 0 rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(24px);
}

.mode-pill {
  min-width: 92px;
  height: 36px;
  padding: 0 22px;
  color: #64748b;
  font-size: 14px;
  font-weight: 500;
}

.mode-pill.active,
.mode-pill:hover {
  background: #f59e0b;
  color: #ffffff;
  box-shadow: 0 8px 18px rgba(245, 158, 11, 0.18);
}

.workspace-chat:not(.active) .composer-dock {
  width: 100%;
  padding-top: 0;
  background: transparent;
}

.workspace-chat:not(.active) .composer-shell {
  width: min(896px, calc(100% - 48px));
  min-height: 168px;
  padding: 24px 26px 22px;
  border-radius: 28px;
  border: 1px solid var(--zuno-glass-border);
  background: var(--zuno-glass-surface);
  box-shadow: var(--zuno-shadow-composer), inset 0 1px 0 rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(28px);
}

.workspace-chat.active .composer-shell {
  position: relative;
  width: min(760px, calc(100% - 40px));
  min-height: auto;
  display: grid;
  grid-template-rows: auto auto;
  gap: 5px;
  padding: 13px 15px 12px;
  border-radius: 18px;
  border: 1px solid rgba(226, 232, 240, 0.84);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.68)),
    rgba(255, 247, 237, 0.24);
  box-shadow:
    0 20px 54px -32px rgba(15, 23, 42, 0.28),
    0 1px 0 rgba(255, 255, 255, 0.92) inset,
    0 0 0 1px rgba(255, 255, 255, 0.5) inset;
  backdrop-filter: blur(28px) saturate(1.18);
  overflow: hidden;
}

.composer-collapsed {
  width: fit-content;
  min-width: min(276px, calc(100% - 40px));
  height: 54px;
  margin: 0 auto 8px;
  padding: 0 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 13px;
  border: 1px solid rgba(255, 255, 255, 0.68);
  border-radius: 999px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.36), rgba(255, 255, 255, 0.18)),
    rgba(255, 255, 255, 0.16);
  color: rgba(51, 65, 85, 0.86);
  box-shadow:
    0 16px 42px -28px rgba(15, 23, 42, 0.32),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(26px) saturate(1.28);
  cursor: pointer;
  font-size: 15px;
  font-weight: 620;
  letter-spacing: 0;
  transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
}

.composer-collapsed:hover {
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.5), rgba(255, 255, 255, 0.28)),
    rgba(255, 255, 255, 0.24);
  color: rgba(30, 41, 59, 0.92);
  box-shadow:
    0 18px 48px -28px rgba(15, 23, 42, 0.36),
    inset 0 1px 0 rgba(255, 255, 255, 0.86);
  transform: translateY(-1px);
}

.composer-collapsed-icon {
  width: 23px;
  height: 23px;
  display: block;
  flex: 0 0 auto;
  object-fit: contain;
  filter: drop-shadow(0 8px 12px rgba(180, 83, 9, 0.14));
}

.workspace-chat:not(.active) .composer-top {
  display: none;
}

.workspace-chat.active .composer-top {
  position: absolute;
  top: 10px;
  right: 15px;
  z-index: 2;
}

.composer-shell:focus-within {
  border-color: rgba(245, 158, 11, 0.32);
  box-shadow: var(--zuno-shadow-composer-focus);
}

.composer {
  min-height: 58px;
  width: 100%;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  color: #0f172a;
  font-size: 14px;
  line-height: 1.45;
  font-weight: 400;
  outline: none;
  resize: none;
}

.workspace-chat.active .composer {
  min-height: 34px;
  max-height: 104px;
  padding: 2px 88px 1px 3px;
  line-height: 1.55;
  scrollbar-width: thin;
}

.composer::placeholder {
  color: #94a3b8;
}

.composer-footer {
  align-items: center;
  margin-top: 0;
}

.workspace-chat.active .composer-footer {
  min-height: 36px;
  padding-top: 4px;
  border-top: 1px solid rgba(226, 232, 240, 0.48);
}

.workspace-chat:not(.active) .composer-meta,
.workspace-chat.active .composer-meta {
  display: none;
}

.composer-footer-left {
  gap: 7px;
}

.attach-btn,
.ghost-pill {
  min-height: 28px;
  padding: 0 4px;
  color: #64748b;
  background: transparent;
  border-color: transparent;
  font-size: 12.5px;
  font-weight: 500;
}

.workspace-chat.active .attach-btn,
.workspace-chat.active .ghost-pill {
  min-height: 27px;
  padding: 0 9px;
  border-radius: 999px;
}

.attach-btn:hover,
.ghost-pill:hover {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.06);
}

.send-btn {
  min-width: 70px;
  height: 34px;
  border-radius: 999px;
  background: #f59e0b;
  color: #ffffff;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 10px 22px rgba(245, 158, 11, 0.2);
}

.workspace-chat.active .send-btn {
  min-width: 66px;
  height: 31px;
  font-size: 12.5px;
  box-shadow: 0 10px 20px -8px rgba(245, 158, 11, 0.5);
}

.composer-disclaimer {
  width: min(896px, calc(100% - 48px));
  margin: 14px auto 0;
  color: #94a3b8;
  text-align: center;
  font-size: 12px;
  line-height: 1.4;
}

/* High-density chat surface: smaller primitives, wider working area, less vertical waste. */
.workspace-shell {
  padding: 22px 24px 18px;
}

.conversation-panel {
  width: min(1020px, calc(100% - 28px));
  gap: 6px;
  padding: 16px 0 8px;
}

.message-row {
  gap: 7px;
}

.avatar {
  width: 24px;
  height: 24px;
}

.message-bubble {
  max-width: min(820px, calc(100% - 38px));
  padding: 7px 10px;
  border-radius: 14px;
  font-size: 12.5px;
  line-height: 1.48;
}

.settings-command {
  max-width: min(360px, calc(100% - 38px));
  padding: 7px 12px;
}

.settings-message-stack {
  width: min(1000px, calc(100% - 38px));
  gap: 6px;
}

.settings-message-meta {
  font-size: 11px;
}

.settings-message-meta strong {
  font-size: 12px;
}

.settings-bubble {
  padding: 24px 28px;
  border-radius: 22px;
}

.settings-bubble :deep(.agent-page),
.settings-bubble :deep(.agent-editor-page),
.settings-bubble :deep(.model-page),
.settings-bubble :deep(.knowledge-page),
.settings-bubble :deep(.knowledge-file-page),
.settings-bubble :deep(.knowledge-config-page),
.settings-bubble :deep(.mcp-page),
.settings-bubble :deep(.tool-page),
.settings-bubble :deep(.skill-page),
.settings-bubble :deep(.dashboard-page) {
  gap: 8px !important;
  font-size: 11.5px !important;
}

.settings-bubble :deep(.agent-hero),
.settings-bubble :deep(.page-header),
.settings-bubble :deep(.page-hero),
.settings-bubble :deep(.hero-card) {
  padding: 0 0 8px !important;
  gap: 8px !important;
}

.settings-bubble :deep(.toolbar-card),
.settings-bubble :deep(.content-card),
.settings-bubble :deep(.table-card),
.settings-bubble :deep(.list-card),
.settings-bubble :deep(.editor-card),
.settings-bubble :deep(.side-card),
.settings-bubble :deep(.form-card),
.settings-bubble :deep(.summary-card),
.settings-bubble :deep(.config-panel),
.settings-bubble :deep(.preview-card) {
  padding: 8px !important;
}

.settings-bubble :deep(.model-card),
.settings-bubble :deep(.knowledge-card),
.settings-bubble :deep(.agent-card),
.settings-bubble :deep(.skill-card),
.settings-bubble :deep(.kpi-card) {
  padding: 8px !important;
}

.settings-bubble :deep(.hero-actions),
.settings-bubble :deep(.header-actions),
.settings-bubble :deep(.card-actions),
.settings-bubble :deep(.filter-bar),
.settings-bubble :deep(.toolbar-card) {
  gap: 7px !important;
}

.settings-bubble :deep(h1),
.settings-bubble :deep(.agent-hero h2),
.settings-bubble :deep(.hero-card h2),
.settings-bubble :deep(.page-hero h1) {
  font-size: 18px !important;
  line-height: 1.16 !important;
}

.settings-bubble :deep(h2) {
  font-size: 13.5px !important;
}

.settings-bubble :deep(h3),
.settings-bubble :deep(.card-title),
.settings-bubble :deep(.side-title-row strong),
.settings-bubble :deep(.profile-meta strong) {
  font-size: 12.5px !important;
}

.settings-bubble :deep(p),
.settings-bubble :deep(.meta-row),
.settings-bubble :deep(.scope-text),
.settings-bubble :deep(.skill-meta),
.settings-bubble :deep(.summary-item span),
.settings-bubble :deep(.card-subtitle),
.settings-bubble :deep(.profile-meta span),
.settings-bubble :deep(.empty-text),
.settings-bubble :deep(.tool-description),
.settings-bubble :deep(.server-subtitle),
.settings-bubble :deep(.server-hint) {
  font-size: 11px !important;
  line-height: 1.38 !important;
}

.settings-bubble :deep(.eyebrow),
.settings-bubble :deep(.empty-kicker),
.settings-bubble :deep(.official-badge),
.settings-bubble :deep(.badge),
.settings-bubble :deep(.config-badge),
.settings-bubble :deep(.meta-pill),
.settings-bubble :deep(.meta-badge),
.settings-bubble :deep(.hint-chip),
.settings-bubble :deep(.official-tag),
.settings-bubble :deep(.status-pill),
.settings-bubble :deep(.el-tag) {
  min-height: 18px !important;
  padding: 0 6px !important;
  font-size: 10px !important;
}

.settings-bubble :deep(.agent-grid),
.settings-bubble :deep(.model-grid),
.settings-bubble :deep(.knowledge-grid),
.settings-bubble :deep(.skill-grid),
.settings-bubble :deep(.kpi-grid),
.settings-bubble :deep(.content-grid) {
  gap: 7px !important;
}

.settings-bubble :deep(.agent-grid),
.settings-bubble :deep(.model-grid),
.settings-bubble :deep(.knowledge-grid),
.settings-bubble :deep(.skill-grid) {
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)) !important;
}

.settings-bubble :deep(.content-grid) {
  grid-template-columns: minmax(0, 1.4fr) minmax(180px, 0.8fr) minmax(180px, 0.8fr) !important;
}

.settings-bubble :deep(.tool-row) {
  grid-template-columns: 30px minmax(0, 1fr) auto !important;
  gap: 8px !important;
  padding: 8px !important;
}

.settings-bubble :deep(.server-table) {
  border-spacing: 0 5px;
}

.settings-bubble :deep(.server-table th) {
  font-size: 10.5px;
}

.settings-bubble :deep(.server-table td) {
  padding: 6px 8px !important;
}

.settings-bubble :deep(.page-icon),
.settings-bubble :deep(.title-icon),
.settings-bubble :deep(.header-icon) {
  width: 30px !important;
  height: 30px !important;
  border-radius: 9px !important;
}

.settings-bubble :deep(.avatar-wrap),
.settings-bubble :deep(.logo-wrap),
.settings-bubble :deep(.skill-icon-wrap),
.settings-bubble :deep(.server-logo) {
  width: 32px !important;
  height: 32px !important;
  border-radius: 9px !important;
}

.settings-bubble :deep(.title-block),
.settings-bubble :deep(.header-left),
.settings-bubble :deep(.card-top),
.settings-bubble :deep(.skill-title-wrap),
.settings-bubble :deep(.server-cell),
.settings-bubble :deep(.meta-grid),
.settings-bubble :deep(.summary-grid),
.settings-bubble :deep(.field-grid),
.settings-bubble :deep(.dialog-grid),
.settings-bubble :deep(.basic-grid),
.settings-bubble :deep(.options-grid),
.settings-bubble :deep(.card-footer),
.settings-bubble :deep(.tool-side),
.settings-bubble :deep(.skill-actions),
.settings-bubble :deep(.row-actions),
.settings-bubble :deep(.action-row) {
  gap: 6px !important;
}

.settings-bubble :deep(.el-button) {
  min-height: 26px !important;
  padding: 4px 8px !important;
  font-size: 11px !important;
}

.settings-bubble :deep(.el-input__wrapper),
.settings-bubble :deep(.el-textarea__inner),
.settings-bubble :deep(.el-select__wrapper) {
  min-height: 26px !important;
}

.settings-bubble :deep(.el-input__inner),
.settings-bubble :deep(.el-textarea__inner),
.settings-bubble :deep(.el-select__selected-item),
.settings-bubble :deep(.el-select__placeholder) {
  font-size: 11px !important;
}

.settings-bubble :deep(.empty-state) {
  padding: 14px !important;
}

.settings-bubble :deep(.empty-visual) {
  transform: scale(0.72);
}

/* Settings bubble composition pass: remove old page chrome and let every module read like one flowing message. */
.settings-bubble :deep(.agent-page),
.settings-bubble :deep(.agent-editor-page),
.settings-bubble :deep(.model-page),
.settings-bubble :deep(.knowledge-page),
.settings-bubble :deep(.knowledge-file-page),
.settings-bubble :deep(.knowledge-config-page),
.settings-bubble :deep(.mcp-page),
.settings-bubble :deep(.tool-page),
.settings-bubble :deep(.skill-page),
.settings-bubble :deep(.dashboard-page) {
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
  padding: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.agent-hero),
.settings-bubble :deep(.page-header),
.settings-bubble :deep(.page-hero),
.settings-bubble :deep(.hero-card) {
  display: flex !important;
  flex-direction: column !important;
  align-items: stretch !important;
  justify-content: flex-start !important;
  min-height: 0 !important;
  gap: 8px !important;
  padding: 0 0 8px !important;
  border: 0 !important;
  border-bottom: 1px solid rgba(226, 232, 240, 0.68) !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
}

.settings-bubble :deep(.agent-hero p),
.settings-bubble :deep(.page-header p),
.settings-bubble :deep(.page-hero p),
.settings-bubble :deep(.hero-card p),
.settings-bubble :deep(.section-head p),
.settings-bubble :deep(.card-subtitle),
.settings-bubble :deep(.empty-kicker),
.settings-bubble :deep(.eyebrow),
.settings-bubble :deep(.guide-eyebrow),
.settings-bubble :deep(.server-hint),
.settings-bubble :deep(.tool-description),
.settings-bubble :deep(.source-helper),
.settings-bubble :deep(.helper),
.settings-bubble :deep(.hint-text) {
  display: none !important;
}

.settings-bubble[data-settings-detail='true'] :deep(.agent-editor-page .page-header .header-left > .el-button:first-child),
.settings-bubble[data-settings-detail='true'] :deep(.knowledge-file-page .page-header .title-wrap > .el-button:first-child),
.settings-bubble[data-settings-detail='true'] :deep(.knowledge-config-page .page-hero .back-btn) {
  display: none !important;
}

.settings-bubble[data-settings-detail='true'] :deep(.agent-editor-page .page-header),
.settings-bubble[data-settings-detail='true'] :deep(.knowledge-file-page .page-header) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) auto !important;
  align-items: center !important;
  column-gap: 12px !important;
}

.settings-bubble[data-settings-detail='true'] :deep(.agent-editor-page .header-left),
.settings-bubble[data-settings-detail='true'] :deep(.knowledge-file-page .title-wrap) {
  min-width: 0 !important;
  align-items: center !important;
}

.settings-bubble :deep(.header-copy),
.settings-bubble :deep(.hero-copy),
.settings-bubble :deep(.title-block),
.settings-bubble :deep(.header-left),
.settings-bubble :deep(.page-title-row),
.settings-bubble :deep(.card-title-row),
.settings-bubble :deep(.panel-head),
.settings-bubble :deep(.section-head) {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  min-width: 0 !important;
  margin: 0 !important;
  flex: 0 0 auto !important;
}

.settings-bubble :deep(.header-actions),
.settings-bubble :deep(.hero-actions),
.settings-bubble :deep(.filter-bar),
.settings-bubble :deep(.toolbar-card) {
  width: 100% !important;
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: center !important;
  justify-content: flex-start !important;
  align-content: flex-start !important;
  gap: 6px !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  flex: 0 0 auto !important;
  height: auto !important;
  min-height: 0 !important;
}

.settings-bubble :deep(.search-input),
.settings-bubble :deep(.search-box),
.settings-bubble :deep(.el-input) {
  max-width: 320px !important;
}

.settings-bubble :deep(.content-card),
.settings-bubble :deep(.table-card),
.settings-bubble :deep(.list-card),
.settings-bubble :deep(.config-panel),
.settings-bubble :deep(.preview-card),
.settings-bubble :deep(.editor-card),
.settings-bubble :deep(.side-card),
.settings-bubble :deep(.form-card),
.settings-bubble :deep(.summary-block),
.settings-bubble :deep(.summary-card:not(.kpi-card)) {
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
}

.settings-bubble :deep(.agent-grid),
.settings-bubble :deep(.model-grid),
.settings-bubble :deep(.knowledge-grid),
.settings-bubble :deep(.skill-grid),
.settings-bubble :deep(.file-grid),
.settings-bubble :deep(.kpi-grid),
.settings-bubble :deep(.content-grid),
.settings-bubble :deep(.workspace),
.settings-bubble :deep(.editor-layout),
.settings-bubble :deep(.config-layout),
.settings-bubble :deep(.workspace-grid),
.settings-bubble :deep(.detail-layout),
.settings-bubble :deep(.basic-grid),
.settings-bubble :deep(.capability-grid),
.settings-bubble :deep(.option-grid),
.settings-bubble :deep(.form-grid),
.settings-bubble :deep(.summary-grid),
.settings-bubble :deep(.meta-grid),
.settings-bubble :deep(.field-grid),
.settings-bubble :deep(.dialog-grid),
.settings-bubble :deep(.options-grid) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  align-content: start !important;
  justify-content: stretch !important;
  gap: 7px !important;
}

.settings-bubble :deep(.agent-card),
.settings-bubble :deep(.model-card),
.settings-bubble :deep(.knowledge-card),
.settings-bubble :deep(.skill-card),
.settings-bubble :deep(.file-card),
.settings-bubble :deep(.mcp-card),
.settings-bubble :deep(.tool-card),
.settings-bubble :deep(.tool-row),
.settings-bubble :deep(.server-row),
.settings-bubble :deep(.mode-card),
.settings-bubble :deep(.switch-card),
.settings-bubble :deep(.config-summary-card),
.settings-bubble :deep(.status-card),
.settings-bubble :deep(.kpi-card),
.settings-bubble :deep(.event-card),
.settings-bubble :deep(.empty-state),
.settings-bubble :deep(.empty-panel) {
  width: 100% !important;
  min-height: 0 !important;
  padding: 9px 10px !important;
  border: 1px solid rgba(226, 232, 240, 0.72) !important;
  border-radius: 12px !important;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(248, 250, 252, 0.54)),
    rgba(255, 255, 255, 0.52) !important;
  box-shadow: 0 10px 28px -24px rgba(15, 23, 42, 0.26), inset 0 1px 0 rgba(255, 255, 255, 0.82) !important;
  backdrop-filter: blur(16px) !important;
}

.settings-bubble :deep(.card-top),
.settings-bubble :deep(.card-head),
.settings-bubble :deep(.skill-card-head),
.settings-bubble :deep(.server-cell),
.settings-bubble :deep(.tool-row),
.settings-bubble :deep(.progress-row),
.settings-bubble :deep(.card-footer),
.settings-bubble :deep(.row-actions),
.settings-bubble :deep(.action-row),
.settings-bubble :deep(.card-actions),
.settings-bubble :deep(.skill-actions),
.settings-bubble :deep(.tool-side) {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: center !important;
  justify-content: flex-start !important;
  gap: 6px !important;
}

.settings-bubble :deep(.card-main p),
.settings-bubble :deep(.card-copy p),
.settings-bubble :deep(.skill-meta),
.settings-bubble :deep(.scope-text),
.settings-bubble :deep(.server-subtitle),
.settings-bubble :deep(.profile-meta span),
.settings-bubble :deep(.empty-copy p) {
  display: block !important;
  max-width: 100% !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
  color: #64748b !important;
  font-size: 11px !important;
  line-height: 1.36 !important;
}

.settings-bubble :deep(.empty-visual),
.settings-bubble :deep(.hero-side),
.settings-bubble :deep(.official-badge) {
  display: none !important;
}

.settings-bubble :deep(.meta-row),
.settings-bubble :deep(.summary-grid),
.settings-bubble :deep(.hero-pills) {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 5px !important;
}

.settings-bubble :deep(.meta-pill),
.settings-bubble :deep(.meta-badge),
.settings-bubble :deep(.config-badge),
.settings-bubble :deep(.status-pill),
.settings-bubble :deep(.hero-pill),
.settings-bubble :deep(.el-tag) {
  min-height: 18px !important;
  padding: 0 6px !important;
  border-radius: 999px !important;
  border-color: rgba(245, 158, 11, 0.2) !important;
  background: rgba(245, 158, 11, 0.075) !important;
  color: #b45309 !important;
  font-size: 10px !important;
  font-weight: 520 !important;
}

.settings-bubble :deep(.page-icon),
.settings-bubble :deep(.title-icon),
.settings-bubble :deep(.header-icon),
.settings-bubble :deep(.avatar-wrap),
.settings-bubble :deep(.logo-wrap),
.settings-bubble :deep(.skill-icon-wrap),
.settings-bubble :deep(.server-logo),
.settings-bubble :deep(.side-avatar) {
  width: 28px !important;
  height: 28px !important;
  border-radius: 9px !important;
  flex: 0 0 auto !important;
  box-shadow: none !important;
}

.settings-bubble :deep(h1),
.settings-bubble :deep(.agent-hero h2),
.settings-bubble :deep(.hero-card h2),
.settings-bubble :deep(.page-hero h1) {
  margin: 0 !important;
  color: #0f172a !important;
  font-size: 17px !important;
  font-weight: 650 !important;
  line-height: 1.18 !important;
}

.settings-bubble :deep(h2),
.settings-bubble :deep(.card-title),
.settings-bubble :deep(.panel-head h2),
.settings-bubble :deep(.section-head h2) {
  margin: 0 !important;
  color: #0f172a !important;
  font-size: 12.5px !important;
  font-weight: 630 !important;
  line-height: 1.22 !important;
}

.settings-bubble :deep(h3),
.settings-bubble :deep(.card-main h3),
.settings-bubble :deep(.card-copy h3),
.settings-bubble :deep(.profile-meta strong),
.settings-bubble :deep(.side-title-row strong) {
  margin: 0 !important;
  color: #0f172a !important;
  font-size: 12px !important;
  font-weight: 620 !important;
  line-height: 1.22 !important;
}

.settings-bubble :deep(.el-table),
.settings-bubble :deep(.server-table) {
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.server-table) {
  border-spacing: 0 5px !important;
}

.settings-bubble :deep(.server-table th) {
  display: none !important;
}

.settings-bubble :deep(.server-table td) {
  padding: 7px 8px !important;
  background: rgba(255, 255, 255, 0.58) !important;
  border-color: rgba(226, 232, 240, 0.68) !important;
}

.settings-bubble :deep(.agent-grid),
.settings-bubble :deep(.knowledge-grid),
.settings-bubble :deep(.model-grid),
.settings-bubble :deep(.skill-grid),
.settings-bubble :deep(.file-grid) {
  margin-top: 0 !important;
}

.settings-bubble :deep(.empty-state) {
  min-height: 0 !important;
  grid-column: auto !important;
  text-align: left !important;
  place-items: start !important;
}

.settings-bubble :deep(.empty-copy) {
  display: grid !important;
  gap: 4px !important;
}

.settings-bubble :deep(.empty-actions) {
  grid-column: auto !important;
  justify-content: flex-start !important;
}

.settings-bubble :deep(.section-head),
.settings-bubble :deep(.subsection-head),
.settings-bubble :deep(.panel-head),
.settings-bubble :deep(.card-title-row) {
  margin-bottom: 4px !important;
}

.settings-bubble :deep(.subsection),
.settings-bubble :deep(.switch-row),
.settings-bubble :deep(.summary-stack),
.settings-bubble :deep(.rank-list) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 7px !important;
  margin-top: 7px !important;
}

.settings-bubble :deep(.field),
.settings-bubble :deep(.switch-card),
.settings-bubble :deep(.mode-card),
.settings-bubble :deep(.rank-item),
.settings-bubble :deep(.summary-item),
.settings-bubble :deep(.summary-card),
.settings-bubble :deep(.preview-chunk),
.settings-bubble :deep(.pipeline-item) {
  min-height: 0 !important;
  padding: 8px 10px !important;
  border-radius: 11px !important;
  border: 1px solid rgba(226, 232, 240, 0.7) !important;
  background: rgba(255, 255, 255, 0.5) !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.field small),
.settings-bubble :deep(.mode-card span),
.settings-bubble :deep(.switch-card p),
.settings-bubble :deep(.pipeline-item p),
.settings-bubble :deep(.preview-chunk p),
.settings-bubble :deep(.summary-lines span),
.settings-bubble :deep(.panel-head span),
.settings-bubble :deep(.kpi-card small) {
  color: #64748b !important;
  font-size: 10.5px !important;
  line-height: 1.3 !important;
}

.settings-bubble :deep(.mode-card span),
.settings-bubble :deep(.switch-card p),
.settings-bubble :deep(.pipeline-item p),
.settings-bubble :deep(.preview-chunk p),
.settings-bubble :deep(.panel-head p),
.settings-bubble :deep(.subsection-head p),
.settings-bubble :deep(.impact-panel p),
.settings-bubble :deep(.status-card p),
.settings-bubble :deep(.card-caption),
.settings-bubble :deep(.form-tip),
.settings-bubble :deep(.setting-tip),
.settings-bubble :deep(.empty-state p) {
  display: none !important;
}

.settings-bubble :deep(.el-form-item) {
  margin-bottom: 8px !important;
}

.settings-bubble :deep(.el-form-item__label) {
  height: auto !important;
  margin-bottom: 4px !important;
  color: #475569 !important;
  font-size: 11px !important;
  font-weight: 560 !important;
  line-height: 1.25 !important;
}

.settings-bubble :deep(.el-input__wrapper),
.settings-bubble :deep(.el-select__wrapper),
.settings-bubble :deep(.el-textarea__inner),
.settings-bubble :deep(.el-input-number),
.settings-bubble :deep(.el-input-number .el-input__wrapper) {
  min-height: 30px !important;
  border-radius: 10px !important;
  background: rgba(255, 255, 255, 0.64) !important;
  box-shadow: 0 0 0 1px rgba(226, 232, 240, 0.76) inset !important;
}

.settings-bubble :deep(.el-input__inner),
.settings-bubble :deep(.el-select__placeholder),
.settings-bubble :deep(.el-textarea__inner) {
  font-size: 11.5px !important;
}

.settings-bubble :deep(.el-textarea__inner),
.settings-bubble :deep(textarea) {
  height: auto;
  min-height: 30px !important;
  max-height: none !important;
  line-height: 1.45 !important;
  resize: none !important;
  overflow-y: hidden !important;
}

.settings-bubble :deep(.prompt-editor textarea),
.settings-bubble :deep(.agent-editor-page textarea),
.settings-bubble :deep(.knowledge-config-page textarea) {
  min-height: 30px !important;
  max-height: none !important;
}

.settings-bubble :deep(.el-radio-group),
.settings-bubble :deep(.el-checkbox-group) {
  gap: 6px !important;
}

.settings-bubble :deep(.el-radio-button__inner),
.settings-bubble :deep(.el-checkbox-button__inner) {
  min-height: 28px !important;
  padding: 6px 10px !important;
  border-radius: 9px !important;
  font-size: 11px !important;
}

.settings-bubble :deep(.el-switch) {
  --el-switch-on-color: #f59e0b;
  height: 18px !important;
  line-height: 18px !important;
}

.settings-bubble :deep(.el-switch__core) {
  min-width: 34px !important;
  height: 18px !important;
}

.settings-bubble :deep(.el-switch__action) {
  width: 14px !important;
  height: 14px !important;
}

.settings-bubble :deep(.el-slider) {
  --el-slider-height: 4px;
  --el-slider-button-size: 14px;
}

.settings-bubble :deep(.el-empty) {
  --el-empty-padding: 8px 0;
  padding: 8px 0 !important;
}

.settings-bubble :deep(.el-empty__image) {
  width: 34px !important;
  height: 34px !important;
  opacity: 0.32;
}

.settings-bubble :deep(.el-empty__description) {
  margin-top: 4px !important;
  font-size: 11px !important;
}

.settings-bubble :deep(.kpi-grid) {
  grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
}

.settings-bubble :deep(.kpi-card) {
  gap: 4px !important;
  padding: 8px 10px !important;
}

.settings-bubble :deep(.kpi-card strong) {
  font-size: 18px !important;
  line-height: 1 !important;
}

.settings-bubble :deep(.kpi-label) {
  font-size: 10.5px !important;
}

.settings-bubble :deep(.footer-actions),
.settings-bubble :deep(.status-actions) {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 6px !important;
  margin-top: 8px !important;
}

.settings-bubble :deep(.basic-card .basic-grid) {
  grid-template-columns: 104px minmax(0, 1fr) !important;
  align-items: start !important;
}

.settings-bubble :deep(.basic-card),
.settings-bubble :deep(.capability-card),
.settings-bubble :deep(.model-card),
.settings-bubble :deep(.knowledge-card),
.settings-bubble :deep(.agent-card) {
  container-type: inline-size;
}

.settings-bubble :deep(.logo-panel) {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: flex-start !important;
  gap: 6px !important;
  padding: 8px !important;
}

.settings-bubble :deep(.logo-preview),
.settings-bubble :deep(.side-avatar) {
  width: 72px !important;
  height: 72px !important;
  border-radius: 18px !important;
}

.settings-bubble :deep(.profile-card),
.settings-bubble :deep(.prompt-card) {
  display: none !important;
}

.settings-bubble :deep(.agent-editor-page .editor-layout) {
  grid-template-columns: minmax(0, 1fr) !important;
}

.settings-bubble :deep(.agent-editor-page .right-column) {
  display: none !important;
}

.settings-bubble :deep(.knowledge-config-page .workspace),
.settings-bubble :deep(.knowledge-config-page .config-column),
.settings-bubble :deep(.knowledge-config-page .preview-column) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 7px !important;
}

.settings-bubble :deep(.knowledge-config-page .preview-column) {
  order: 3;
}

.settings-bubble :deep(.knowledge-config-page .sticky-card) {
  position: static !important;
}

.settings-bubble :deep(.knowledge-config-page .panel-icon),
.settings-bubble :deep(.pipeline-icon) {
  display: none !important;
}

.settings-bubble :deep(.knowledge-config-page .panel-head),
.settings-bubble :deep(.knowledge-config-page .subsection-head),
.settings-bubble :deep(.agent-editor-page .panel-head) {
  padding: 0 !important;
}

.settings-bubble :deep(:is(
  .agent-page,
  .agent-editor-page,
  .model-page,
  .knowledge-page,
  .knowledge-file-page,
  .knowledge-config-page,
  .mcp-page,
  .tool-page,
  .skill-page,
  .dashboard-page,
  .content-card,
  .table-card,
  .list-card,
  .agent-grid,
  .model-grid,
  .knowledge-grid,
  .skill-grid,
  .tool-grid,
  .server-list
)) {
  transition: none !important;
  animation: none !important;
}

.settings-bubble :deep(.knowledge-config-page .config-panel),
.settings-bubble :deep(.agent-editor-page .editor-card),
.settings-bubble :deep(.knowledge-file-page .content-card) {
  gap: 8px !important;
}

.settings-bubble :deep(.knowledge-config-page .option-grid) {
  grid-template-columns: repeat(auto-fit, minmax(132px, 1fr)) !important;
  gap: 6px !important;
}

.settings-bubble :deep(.knowledge-config-page .mode-card) {
  min-height: 32px !important;
  align-items: center !important;
  padding: 7px 9px !important;
}

.settings-bubble :deep(.knowledge-config-page .mode-card.active),
.settings-bubble :deep(.agent-editor-page .mode-card.active) {
  border-color: rgba(245, 158, 11, 0.44) !important;
  background: rgba(245, 158, 11, 0.1) !important;
}

.settings-bubble :deep(.knowledge-config-page .form-grid) {
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 6px !important;
}

.settings-bubble :deep(.knowledge-config-page .field) {
  display: grid !important;
  grid-template-columns: 116px minmax(0, 1fr) auto !important;
  align-items: center !important;
  column-gap: 10px !important;
  row-gap: 4px !important;
  padding: 7px 10px !important;
}

.settings-bubble :deep(.knowledge-config-page .field > span) {
  color: #334155 !important;
  font-size: 11.5px !important;
  font-weight: 590 !important;
}

.settings-bubble :deep(.knowledge-config-page .field > .el-slider) {
  grid-column: 2 !important;
  margin: 0 !important;
}

.settings-bubble :deep(.knowledge-config-page .field > small) {
  grid-column: 3 !important;
  justify-self: end !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(.knowledge-config-page .field > .el-input),
.settings-bubble :deep(.knowledge-config-page .field > .el-select) {
  grid-column: 2 / -1 !important;
}

.settings-bubble :deep(.knowledge-config-page .switch-row) {
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)) !important;
  gap: 6px !important;
}

.settings-bubble :deep(.knowledge-config-page .switch-card) {
  grid-template-columns: minmax(0, 1fr) auto !important;
  align-items: center !important;
  padding: 7px 10px !important;
}

.settings-bubble :deep(.knowledge-config-page .status-card),
.settings-bubble :deep(.knowledge-config-page .impact-panel) {
  display: none !important;
}

.settings-bubble :deep(.knowledge-config-page .preview-card),
.settings-bubble :deep(.knowledge-config-page .sticky-card) {
  max-height: none !important;
}

.settings-bubble :deep(.skill-page .empty-state),
.settings-bubble :deep(.mcp-page .empty-state),
.settings-bubble :deep(.tool-page .empty-state) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) auto !important;
  align-items: center !important;
}

.settings-bubble :deep(.agent-editor-page .basic-card .basic-grid) {
  grid-template-columns: 96px minmax(0, 1fr) !important;
  gap: 8px !important;
}

.settings-bubble :deep(.agent-editor-page .logo-panel) {
  background: transparent !important;
}

.settings-bubble :deep(.agent-editor-page .logo-preview) {
  width: 60px !important;
  height: 60px !important;
  border-radius: 16px !important;
}

.settings-bubble :deep(.agent-editor-page .capability-grid) {
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  gap: 8px !important;
}

.settings-bubble :deep(.agent-editor-page .el-form-item:has(textarea)) {
  margin-bottom: 6px !important;
}

.settings-bubble :deep(.knowledge-file-page .config-strip),
.settings-bubble :deep(.knowledge-file-page .summary-grid) {
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  gap: 7px !important;
}

.settings-bubble :deep(.knowledge-file-page .summary-head p),
.settings-bubble :deep(.knowledge-file-page .file-head p),
.settings-bubble :deep(.knowledge-file-page .task-meta) {
  display: none !important;
}

.settings-bubble :deep(.knowledge-file-page .summary-item),
.settings-bubble :deep(.knowledge-file-page .status-pill) {
  min-height: 0 !important;
  padding: 6px 8px !important;
}

.settings-bubble :deep(.model-page .model-card) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) auto !important;
  align-items: center !important;
  gap: 12px !important;
  min-height: 0 !important;
  padding: 10px 0 !important;
  border: 0 !important;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18) !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.model-page .model-card:last-child) {
  border-bottom: 0 !important;
}

.settings-bubble :deep(.model-page .model-main) {
  gap: 5px !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.model-page .top-line) {
  gap: 7px !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.model-page .top-line h3) {
  max-width: min(44vw, 320px) !important;
  color: #0f172a !important;
  font-size: 14.5px !important;
  font-weight: 700 !important;
  line-height: 1.25 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(.model-page .badge) {
  min-height: 17px !important;
  padding: 0 6px !important;
  border: 0 !important;
  background: rgba(245, 158, 11, 0.07) !important;
  color: #a16207 !important;
  font-size: 9.5px !important;
  font-weight: 520 !important;
  line-height: 17px !important;
}

.settings-bubble :deep(.model-page .meta-grid) {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 4px !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.model-page .meta-grid span) {
  width: auto !important;
  max-width: min(100%, 240px) !important;
  min-height: 17px !important;
  padding: 0 6px !important;
  border: 0 !important;
  border-radius: 999px !important;
  background: rgba(245, 158, 11, 0.05) !important;
  color: #8a6a45 !important;
  font-size: 9.5px !important;
  line-height: 17px !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(.model-page .card-actions),
.settings-bubble :deep(.mcp-page .card-actions),
.settings-bubble :deep(.tool-page .card-actions) {
  justify-content: flex-end !important;
}

.settings-bubble :deep(.model-page .card-actions) {
  display: flex !important;
  flex-wrap: nowrap !important;
  gap: 6px !important;
  min-width: max-content !important;
}

.settings-bubble :deep(.model-page .card-actions .el-button + .el-button) {
  margin-left: 0 !important;
}

.settings-bubble :deep(.model-page .model-icon-button.el-button) {
  width: 26px !important;
  height: 26px !important;
  min-width: 26px !important;
  padding: 0 !important;
  border-radius: 999px !important;
  border-color: rgba(245, 158, 11, 0.2) !important;
  background: rgba(245, 158, 11, 0.08) !important;
  color: #b45309 !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.model-page .model-icon-button.active.el-button) {
  border-color: rgba(245, 158, 11, 0.38) !important;
  background: #f59e0b !important;
  color: #ffffff !important;
  box-shadow: 0 10px 22px rgba(245, 158, 11, 0.18) !important;
}

.settings-bubble :deep(.model-page .model-icon-button.danger.el-button) {
  border-color: rgba(239, 68, 68, 0.16) !important;
  background: rgba(239, 68, 68, 0.06) !important;
  color: #b91c1c !important;
}

.settings-bubble :deep(.skill-page .el-empty__image),
.settings-bubble :deep(.skill-page .empty-illustration) {
  display: none !important;
}

.settings-bubble :deep(.knowledge-file-page .content-grid),
.settings-bubble :deep(.knowledge-file-page .summary-grid) {
  grid-template-columns: minmax(0, 1fr) !important;
}

.settings-bubble :deep(.el-loading-mask) {
  background: rgba(255, 255, 255, 0.28) !important;
  backdrop-filter: blur(3px);
}

/* Settings primitives: one visual grammar for headers, controls, surfaces, rows and inline dialogs. */
.settings-bubble {
  --settings-ink: #0f172a;
  --settings-muted: #64748b;
  --settings-line: rgba(226, 232, 240, 0.46);
  --settings-tint: rgba(245, 158, 11, 0.1);
  --settings-surface: rgba(255, 255, 255, 0.54);
  --settings-surface-strong: rgba(255, 255, 255, 0.72);
  --settings-radius: 12px;
  --settings-row-pad: 8px 10px;
}

.settings-bubble :deep(:is(
  .agent-page,
  .agent-editor-page,
  .model-page,
  .knowledge-page,
  .knowledge-file-page,
  .knowledge-config-page,
  .mcp-page,
  .tool-page,
  .skill-page,
  .dashboard-page
)) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 8px !important;
}

.settings-bubble :deep(:is(
  .agent-hero,
  .page-header,
  .page-hero,
  .hero-card
)) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 7px !important;
  padding: 0 0 6px !important;
  border: 0 !important;
  border-bottom: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(:is(.page-icon, .title-icon, .header-icon)) {
  display: none !important;
}

.settings-bubble :deep(:is(
  .agent-hero h2,
  .page-header h1,
  .page-header h2,
  .page-hero h1,
  .hero-card h1,
  .hero-card h2
)) {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
}

.settings-bubble :deep(:is(
  .agent-hero h2,
  .page-header h1,
  .page-header h2,
  .page-hero h1,
  .hero-card h1,
  .hero-card h2
)::before) {
  content: '';
  width: 27px;
  height: 27px;
  flex: 0 0 27px;
  display: inline-block;
  background-image: var(--settings-page-icon);
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
  filter: drop-shadow(0 8px 12px rgba(245, 158, 11, 0.18));
}

.settings-bubble :deep(:is(
  .header-left,
  .title-wrap,
  .title-block,
  .hero-copy,
  .page-title-row,
  .section-head,
  .panel-head,
  .card-title-row,
  .summary-head,
  .editor-head,
  .file-sidebar-head
)) {
  display: flex !important;
  min-width: 0 !important;
  align-items: center !important;
  justify-content: flex-start !important;
  gap: 7px !important;
  margin: 0 !important;
  padding: 0 !important;
}

.settings-bubble :deep(:is(
  .header-actions,
  .hero-actions,
  .panel-actions,
  .card-actions,
  .skill-actions,
  .row-actions,
  .action-row,
  .config-actions,
  .footer-actions,
  .status-actions
)) {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: center !important;
  justify-content: flex-start !important;
  gap: 6px !important;
  margin: 0 !important;
}

.settings-bubble :deep(:is(
  .toolbar-card,
  .filter-bar,
  .tabs-toolbar,
  .config-strip,
  .content-card,
  .table-card,
  .list-card,
  .editor-card,
  .side-card,
  .form-card,
  .panel-card,
  .nested-panel,
  .cli-panel,
  .advanced-block,
  .config-section,
  .task-drawer,
  .editor-pane,
  .file-sidebar
)) {
  min-width: 0 !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(:is(
  .agent-card,
  .model-card,
  .knowledge-card,
  .skill-card,
  .file-card,
  .mcp-card,
  .tool-card,
  .tool-row,
  .server-row,
  .mode-card,
  .switch-card,
  .summary-card,
  .summary-item,
  .config-summary-card,
  .status-card,
  .kpi-card,
  .event-card,
  .param-row,
  .recommend-card,
  .structured-card,
  .candidate-item,
  .connectivity-card,
  .empty-state,
  .empty-panel,
  .readonly-list,
  .source-intro
)) {
  min-width: 0 !important;
  min-height: 0 !important;
  padding: var(--settings-row-pad) !important;
  border: 1px solid var(--settings-line) !important;
  border-radius: var(--settings-radius) !important;
  background:
    linear-gradient(180deg, var(--settings-surface-strong), rgba(248, 250, 252, 0.52)),
    var(--settings-surface) !important;
  box-shadow: 0 10px 28px -24px rgba(15, 23, 42, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.82) !important;
}

.settings-bubble :deep(:is(
  .field-grid,
  .form-grid,
  .dialog-grid,
  .basic-grid,
  .capability-grid,
  .option-grid,
  .summary-grid,
  .meta-grid,
  .workspace,
  .editor-layout,
  .detail-layout,
  .cli-shell,
  .tool-form,
  .config-column,
  .preview-column
)) {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 340px), 1fr)) !important;
  align-content: start !important;
  align-items: start !important;
  gap: 6px !important;
}

.settings-bubble :deep(.tool-page .tool-form > .field-grid) {
  display: contents !important;
}

.settings-bubble :deep(.tool-page .tool-form > :is(
  .nested-panel,
  .advanced-block,
  .cli-panel,
  .footer-actions,
  .el-alert,
  .assist-result
)) {
  grid-column: 1 / -1 !important;
}

.settings-bubble :deep(:is(.field, .el-form-item)) {
  min-width: 0 !important;
  margin: 0 !important;
}

.settings-bubble :deep(.el-form-item) {
  display: grid !important;
  grid-template-columns: minmax(76px, 108px) minmax(0, 1fr) !important;
  align-items: start !important;
  column-gap: 10px !important;
  row-gap: 3px !important;
  padding: 4px 0 !important;
}

.settings-bubble :deep(.field:not(label)) {
  display: grid !important;
  grid-template-columns: minmax(76px, 108px) minmax(0, 1fr) !important;
  align-items: center !important;
  column-gap: 10px !important;
  row-gap: 4px !important;
}

.settings-bubble :deep(:is(.span-2, .el-form-item:has(.el-textarea), .field:has(textarea))) {
  grid-column: 1 / -1 !important;
}

.settings-bubble :deep(.el-form-item__label) {
  grid-column: 1 !important;
  display: flex !important;
  justify-content: flex-start !important;
  align-items: flex-start !important;
  height: auto !important;
  min-height: 30px !important;
  margin: 0 !important;
  padding: 7px 0 0 !important;
  color: #475569 !important;
  font-size: 11px !important;
  font-weight: 570 !important;
  line-height: 1.24 !important;
  text-align: left !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.settings-bubble :deep(.el-form-item__content) {
  grid-column: 2 !important;
  min-width: 0 !important;
  display: flex !important;
  align-items: center !important;
  flex-wrap: wrap !important;
  gap: 6px !important;
  line-height: 1.2 !important;
}

.settings-bubble :deep(.field:not(label) > label) {
  grid-column: 1 !important;
  align-self: center !important;
  min-width: 0 !important;
  margin: 0 !important;
  color: #475569 !important;
  font-size: 11px !important;
  font-weight: 570 !important;
  line-height: 1.24 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.settings-bubble :deep(.field:not(label) > :not(label):not(small)) {
  grid-column: 2 !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.field:not(label) > small) {
  grid-column: 2 !important;
  margin: -1px 0 0 !important;
}

.settings-bubble :deep(label.field) {
  display: grid !important;
  grid-template-columns: minmax(76px, 108px) minmax(0, 1fr) auto !important;
  align-items: center !important;
  column-gap: 10px !important;
  row-gap: 3px !important;
}

.settings-bubble :deep(label.field > span:first-child) {
  grid-column: 1 !important;
  min-width: 0 !important;
  color: #475569 !important;
  font-size: 11px !important;
  font-weight: 570 !important;
  line-height: 1.24 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.settings-bubble :deep(label.field > :is(.el-input, .el-select, .el-input-number, .el-slider, textarea)) {
  grid-column: 2 !important;
  min-width: 0 !important;
}

.settings-bubble :deep(label.field > small) {
  grid-column: 3 !important;
  justify-self: end !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(:is(.field-grid, .form-grid, .dialog-grid, .basic-grid, .options-grid) > .span-2),
.settings-bubble :deep(:is(.field-grid, .form-grid, .dialog-grid, .basic-grid, .options-grid) > .el-form-item:has(.el-textarea)),
.settings-bubble :deep(:is(.field-grid, .form-grid, .dialog-grid, .basic-grid, .options-grid) > .field:has(textarea)) {
  grid-column: 1 / -1 !important;
}

.settings-bubble :deep(:is(
  .el-input,
  .el-select,
  .el-input-number,
  .search-input,
  .search-box,
  .full-width
)) {
  width: 100% !important;
  max-width: none !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.el-form-item__content > :is(.el-input, .el-select, .el-textarea, .el-input-number, .el-radio-group, .el-checkbox-group)),
.settings-bubble :deep(.field:not(label) > :is(.el-input, .el-select, .el-textarea, .el-input-number, .el-radio-group, .el-checkbox-group)) {
  width: 100% !important;
  flex: 1 1 220px !important;
}

.settings-bubble :deep(.logo-upload-row) {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  min-width: 0 !important;
}

.settings-bubble :deep(:is(.logo-preview, .logo-wrap, .side-avatar, .avatar-wrap)) {
  width: 42px !important;
  height: 42px !important;
  min-width: 42px !important;
  min-height: 42px !important;
  border-radius: 12px !important;
  overflow: hidden !important;
}

.settings-bubble :deep(:is(.logo-preview, .logo-wrap, .side-avatar, .avatar-wrap) img) {
  display: block !important;
  width: 100% !important;
  height: 100% !important;
  object-fit: cover !important;
  color: transparent !important;
  font-size: 0 !important;
}

.settings-bubble :deep(:is(
  .el-input__wrapper,
  .el-select__wrapper,
  .el-textarea__inner
)) {
  min-height: 30px !important;
  border-radius: 10px !important;
  background: rgba(255, 255, 255, 0.66) !important;
  box-shadow: 0 0 0 1px var(--settings-line) inset !important;
}

/* Unified settings top controls: icon-only actions beside the title, quiet linear search below. */
.settings-bubble :deep(:is(
  .agent-hero,
  .page-header,
  .page-hero,
  .hero-card
)) {
  grid-template-columns: minmax(0, 1fr) auto !important;
  align-items: start !important;
  column-gap: 10px !important;
  row-gap: 5px !important;
}

.settings-bubble :deep(:is(
  .agent-hero,
  .page-header,
  .page-hero,
  .hero-card
) > :first-child) {
  grid-column: 1 !important;
  grid-row: 1 !important;
  min-width: 0 !important;
}

.settings-bubble :deep(:is(
  .agent-hero,
  .page-header,
  .page-hero,
  .hero-card
) > :is(.hero-actions, .header-actions)) {
  grid-column: 2 !important;
  grid-row: 1 !important;
  align-self: start !important;
  justify-self: end !important;
  display: flex !important;
  flex-wrap: nowrap !important;
  align-items: center !important;
  justify-content: flex-end !important;
  gap: 6px !important;
  padding: 0 !important;
  margin: 0 !important;
}

.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button.el-button) {
  --el-button-bg-color: transparent;
  --el-button-border-color: transparent;
  --el-button-hover-bg-color: transparent;
  --el-button-hover-border-color: transparent;
  --el-button-active-bg-color: transparent;
  --el-button-active-border-color: transparent;
  width: 30px !important;
  min-width: 30px !important;
  height: 30px !important;
  min-height: 30px !important;
  padding: 0 !important;
  border-radius: 999px !important;
  border-color: rgba(226, 232, 240, 0.86) !important;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(248, 250, 252, 0.58)),
    rgba(255, 255, 255, 0.52) !important;
  color: #64748b !important;
  box-shadow: 0 10px 24px -20px rgba(15, 23, 42, 0.36), inset 0 1px 0 rgba(255, 255, 255, 0.88) !important;
  backdrop-filter: blur(16px);
}

.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button.el-button::before),
.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button.el-button::after) {
  display: none !important;
}

.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button.el-button:hover) {
  border-color: rgba(245, 158, 11, 0.32) !important;
  color: #b45309 !important;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(255, 247, 237, 0.62)),
    rgba(245, 158, 11, 0.08) !important;
}

.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button.el-button:focus),
.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button.el-button:focus-visible) {
  outline: none !important;
}

.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button.el-button--primary) {
  --el-button-bg-color: #f59e0b;
  --el-button-border-color: #f59e0b;
  --el-button-hover-bg-color: #f59e0b;
  --el-button-hover-border-color: #f59e0b;
  --el-button-active-bg-color: #d97706;
  --el-button-active-border-color: #d97706;
  border-color: #f59e0b !important;
  background: #f59e0b !important;
  color: #ffffff !important;
  box-shadow: 0 12px 26px -18px rgba(180, 83, 9, 0.74) !important;
  overflow: hidden !important;
}

.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button.el-button--primary:hover),
.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button.el-button--primary:focus) {
  border-color: #f59e0b !important;
  background: #f59e0b !important;
  color: #ffffff !important;
}

.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button.el-button--primary:active) {
  border-color: #d97706 !important;
  background: #d97706 !important;
  color: #ffffff !important;
}

.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button .el-icon) {
  margin: 0 !important;
  font-size: 14px !important;
  transform-origin: center;
  transition: transform 210ms cubic-bezier(0.2, 0.78, 0.22, 1);
}

.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button.el-button--primary .el-icon) {
  color: #ffffff !important;
}

.settings-bubble :deep(:is(.hero-actions, .header-actions) .settings-icon-button.is-create-open .el-icon) {
  transform: rotate(45deg);
}

.settings-bubble :deep(.settings-search-row) {
  grid-column: 1 / -1 !important;
  grid-row: 2 !important;
  display: flex !important;
  align-items: center !important;
  min-width: 0 !important;
  width: 100% !important;
  min-height: 30px !important;
  padding: 0 !important;
  margin: -1px 0 0 !important;
  border-bottom: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.toolbar-card) {
  display: grid !important;
  grid-template-columns: auto minmax(0, 1fr) !important;
  align-items: center !important;
  gap: 8px 12px !important;
  min-height: 32px !important;
  padding: 0 0 2px !important;
  border: 0 !important;
  border-bottom: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.toolbar-card:has(> .el-input:only-child)) {
  grid-template-columns: minmax(0, 1fr) !important;
}

.settings-bubble :deep(.toolbar-card .el-tabs) {
  flex: 0 0 auto !important;
  width: auto !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.toolbar-card .el-tabs__header) {
  margin: 0 !important;
}

.settings-bubble :deep(.toolbar-card .el-tabs__nav-wrap::after) {
  display: none !important;
}

.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) :is(.search-input, .search-box, .el-input)) {
  flex: 1 1 auto !important;
  width: 100% !important;
  min-width: 140px !important;
  max-width: none !important;
}

.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input__wrapper) {
  min-height: 28px !important;
  padding: 0 2px !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input__inner) {
  height: 28px !important;
  color: #334155 !important;
  font-size: 11.5px !important;
}

.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input__prefix) {
  color: #94a3b8 !important;
}

.settings-bubble :deep(.dashboard-page .filter-bar) {
  grid-column: 1 / -1 !important;
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)) !important;
  gap: 8px !important;
  min-height: 32px !important;
  padding: 0 0 2px !important;
  border-bottom: 0 !important;
}

.settings-bubble :deep(.settings-empty-hint.empty-state) {
  grid-column: 1 / -1 !important;
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  place-items: center !important;
  justify-content: center !important;
  min-height: 0 !important;
  width: 100% !important;
  max-width: none !important;
  padding: 10px 16px !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  color: rgba(148, 163, 184, 0.86) !important;
  font-size: 13px !important;
  font-weight: 460 !important;
  line-height: 1.55 !important;
  text-align: center !important;
}

.settings-bubble :deep(.settings-empty-hint.empty-state .empty-state-icon) {
  opacity: 0.64 !important;
  filter: grayscale(0.08) saturate(0.72) opacity(0.9) !important;
}

.settings-bubble :deep(:is(.content-card, .table-card, .list-card):has(.settings-empty-hint:only-child)),
.settings-bubble :deep(:is(.agent-grid, .model-grid, .knowledge-grid, .skill-grid):has(.settings-empty-hint:only-child)) {
  min-height: 0 !important;
  padding-block: 6px !important;
}

.settings-bubble :deep(:is(.model-page, .mcp-page, .skill-page, .tool-page, .agent-page, .knowledge-page):has(.settings-empty-hint)) {
  gap: 4px !important;
}

.settings-bubble :deep(:is(
  .badge,
  .config-badge,
  .meta-pill,
  .meta-badge,
  .hint-chip,
  .status-pill,
  .hero-pill,
  .source-pill,
  .confidence-chip,
  .el-tag
)) {
  min-height: 18px !important;
  padding: 0 6px !important;
  border-radius: 999px !important;
  border-color: rgba(245, 158, 11, 0.2) !important;
  background: var(--settings-tint) !important;
  color: #b45309 !important;
  font-size: 10px !important;
  font-weight: 540 !important;
}

.settings-bubble :deep(:is(.el-dialog, .el-drawer)) {
  position: static !important;
  width: 100% !important;
  max-width: none !important;
  height: auto !important;
  margin: 8px 0 0 !important;
  border: 1px solid var(--settings-line) !important;
  border-radius: 16px !important;
  background: rgba(255, 255, 255, 0.52) !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.el-overlay[style*="display: none"]) {
  display: none !important;
}

.settings-bubble :deep(:is(
  .el-dialog__header,
  .el-dialog__body,
  .el-dialog__footer,
  .el-drawer__header,
  .el-drawer__body
)) {
  padding: 10px 12px !important;
}

.settings-bubble :deep(:is(.el-dialog__headerbtn, .el-drawer__close-btn)) {
  display: none !important;
}

.settings-bubble :deep(:is(.el-dialog, .el-drawer)) {
  border: 0 !important;
  border-radius: 14px !important;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.68), rgba(255, 250, 244, 0.34)),
    rgba(255, 255, 255, 0.32) !important;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.84),
    0 10px 24px rgba(15, 23, 42, 0.04) !important;
  backdrop-filter: blur(18px) saturate(1.08) !important;
}

.settings-bubble :deep(:is(.el-dialog__header, .el-drawer__header)) {
  min-height: 0 !important;
  margin: 0 !important;
  padding: 7px 10px 2px !important;
  border-bottom: 0 !important;
}

.settings-bubble :deep(:is(.el-dialog__title, .el-drawer__title)) {
  color: #8a6746 !important;
  font-size: 12px !important;
  font-weight: 650 !important;
  line-height: 1.25 !important;
}

.settings-bubble :deep(:is(.el-dialog__body, .el-drawer__body)) {
  padding: 6px 10px 8px !important;
}

.settings-bubble :deep(.el-dialog__footer) {
  padding: 2px 10px 10px !important;
  border-top: 0 !important;
}

.settings-bubble :deep(:is(.el-dialog .el-form, .el-drawer .el-form)) {
  display: grid !important;
  gap: 7px !important;
}

.settings-bubble :deep(:is(.el-dialog .el-form-item, .el-drawer .el-form-item)) {
  margin-bottom: 6px !important;
}

.settings-bubble :deep(:is(.el-dialog .dialog-grid, .el-drawer .dialog-grid)) {
  gap: 7px !important;
}

.settings-bubble :deep(:is(.el-dialog .el-form-item__label, .el-drawer .el-form-item__label)) {
  margin-bottom: 3px !important;
  color: #7c6b5d !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  line-height: 1.2 !important;
}

.settings-bubble :deep(:is(.el-dialog .el-input__wrapper, .el-dialog .el-select__wrapper, .el-drawer .el-input__wrapper, .el-drawer .el-select__wrapper)) {
  min-height: 31px !important;
  border-radius: 11px !important;
  background: rgba(255, 255, 255, 0.66) !important;
  box-shadow:
    inset 0 0 0 1px rgba(148, 163, 184, 0.18),
    0 8px 18px rgba(15, 23, 42, 0.03) !important;
}

.settings-bubble :deep(:is(.el-dialog .el-input__inner, .el-dialog .el-select__placeholder, .el-drawer .el-input__inner, .el-drawer .el-select__placeholder)) {
  font-size: 12px !important;
}

.settings-bubble :deep(:is(.el-collapse, .advanced-block)) {
  border: 0 !important;
}

.settings-bubble :deep(.el-collapse-item__header) {
  min-height: 42px !important;
  padding: 0 10px !important;
  border: 1px solid rgba(245, 158, 11, 0.16) !important;
  border-radius: 12px !important;
  background: rgba(255, 247, 237, 0.52) !important;
  color: var(--settings-ink) !important;
}

.settings-bubble :deep(:is(.el-collapse-item__wrap, .el-collapse-item__content)) {
  border: 0 !important;
  background: transparent !important;
}

.settings-bubble :deep(.el-collapse-item__content) {
  padding: 8px 0 0 !important;
}

.settings-bubble :deep(:is(.summary-lines, .pipeline-list, .preview-chunks)) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 6px !important;
}

.settings-bubble :deep(.summary-lines span) {
  display: grid !important;
  grid-template-columns: 128px minmax(0, 1fr) !important;
  gap: 8px !important;
  align-items: center !important;
}

.settings-bubble :deep(.preview-chunk) {
  display: grid !important;
  grid-template-columns: 72px minmax(0, 1fr) !important;
  gap: 8px !important;
  align-items: start !important;
}

.settings-bubble :deep(.pipeline-item) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 3px !important;
  align-items: start !important;
}

.settings-bubble :deep(.pipeline-item > div) {
  grid-column: 1 / -1 !important;
}

.settings-bubble :deep(.preview-chunk > p) {
  min-width: 0 !important;
}

.settings-bubble :deep(.preview-chunk .chunk-index) {
  min-width: 0 !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(.pipeline-item p),
.settings-bubble :deep(.preview-chunk p) {
  display: block !important;
  margin: 0 !important;
  color: var(--settings-muted) !important;
  font-size: 11px !important;
  line-height: 1.45 !important;
  white-space: normal !important;
  overflow: visible !important;
  text-overflow: clip !important;
}

.settings-bubble :deep(.tool-page .toolbar-card) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 6px !important;
  padding-bottom: 4px !important;
}

.settings-bubble :deep(.tool-page .tool-tabs),
.settings-bubble :deep(.tool-page .tool-search-row) {
  grid-column: 1 / -1 !important;
  width: 100% !important;
}

.settings-bubble :deep(.tool-page .tool-search-row) {
  grid-row: auto !important;
}

.settings-bubble :deep(.tool-page .list-card) {
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
}

.settings-bubble :deep(.tool-page .tool-row) {
  display: grid !important;
  grid-template-columns: 28px minmax(0, 1fr) auto !important;
  gap: 16px !important;
  align-items: center !important;
  width: 100% !important;
  padding: 8px 0 !important;
  border: 0 !important;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2) !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
}

.settings-bubble :deep(.tool-page .tool-row:last-child) {
  border-bottom: 0 !important;
}

.settings-bubble :deep(.tool-page .tool-row:hover) {
  background: rgba(255, 247, 237, 0.34) !important;
}

.settings-bubble :deep(.tool-page .tool-inline-config) {
  display: grid !important;
  gap: 8px !important;
  margin: 2px 0 14px 44px !important;
  padding: 8px 0 10px !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.tool-page .tool-inline-config .inline-config-head) {
  min-height: 28px !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
}

.settings-bubble :deep(.tool-page .tool-inline-config .inline-config-head span) {
  color: #0f172a !important;
  font-size: 13px !important;
  font-weight: 700 !important;
}

.settings-bubble :deep(.tool-page .logo-wrap) {
  width: 27px !important;
  height: 27px !important;
  min-width: 27px !important;
  min-height: 27px !important;
  border: 0 !important;
  border-radius: 9px !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.tool-page .logo-wrap img) {
  object-fit: contain !important;
}

.settings-bubble :deep(.tool-page .tool-main) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 3px !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.tool-page .tool-title-row) {
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.tool-page .tool-name) {
  flex: 0 1 auto !important;
  max-width: min(32vw, 220px) !important;
  color: #0f172a !important;
  font-size: 12.5px !important;
  font-weight: 650 !important;
  line-height: 1.2 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(.tool-page .tool-description) {
  display: block !important;
  flex: 1 1 auto !important;
  min-width: 0 !important;
  margin: 0 !important;
  color: #64748b !important;
  font-size: 11px !important;
  line-height: 1.25 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(.tool-page .tool-meta-row) {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: center !important;
  gap: 4px !important;
}

.settings-bubble :deep(.tool-page :is(.meta-badge, .hint-chip, .status-pill)) {
  min-height: 17px !important;
  padding: 0 6px !important;
  border: 0 !important;
  border-radius: 999px !important;
  background: rgba(245, 158, 11, 0.055) !important;
  color: #8a6a45 !important;
  font-size: 9.5px !important;
  font-weight: 520 !important;
  line-height: 17px !important;
}

.settings-bubble :deep(.tool-page .status-pill.is-ready) {
  background: rgba(34, 197, 94, 0.08) !important;
  color: #15803d !important;
}

.settings-bubble :deep(.tool-page .status-pill.is-warning) {
  background: rgba(245, 158, 11, 0.08) !important;
  color: #a16207 !important;
}

.settings-bubble :deep(.tool-page .status-pill.is-danger) {
  background: rgba(239, 68, 68, 0.08) !important;
  color: #b91c1c !important;
}

.settings-bubble :deep(.tool-page .status-dot) {
  width: 4px !important;
  height: 4px !important;
  opacity: 0.72 !important;
}

.settings-bubble :deep(.tool-page .tool-side) {
  display: flex !important;
  justify-content: flex-end !important;
  align-items: center !important;
  min-width: max-content !important;
}

.settings-bubble :deep(.tool-page .action-row) {
  display: flex !important;
  flex-wrap: nowrap !important;
  justify-content: flex-end !important;
  gap: 6px !important;
}

.settings-bubble :deep(.tool-page .action-row :is(.el-button + .el-button, .el-dropdown + .el-button, .el-button + .el-dropdown)) {
  margin-left: 0 !important;
}

.settings-bubble :deep(.tool-page .action-row .el-dropdown) {
  margin-left: 0 !important;
  line-height: 0 !important;
}

.settings-bubble :deep(.tool-page .icon-action.el-button) {
  width: 26px !important;
  height: 26px !important;
  min-width: 26px !important;
  padding: 0 !important;
  border-radius: 999px !important;
  color: #7c6a58 !important;
  background: rgba(255, 255, 255, 0.54) !important;
  border-color: rgba(148, 163, 184, 0.2) !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.tool-page .primary-action.el-button) {
  color: #b45309 !important;
  background: rgba(245, 158, 11, 0.1) !important;
  border-color: rgba(245, 158, 11, 0.2) !important;
}

.settings-bubble :deep(.skill-page .skill-grid) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 0 !important;
  margin-top: 0 !important;
}

.settings-bubble :deep(.skill-page .skill-card) {
  display: block !important;
  width: 100% !important;
  min-height: 0 !important;
  padding: 8px 0 !important;
  border: 0 !important;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2) !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
}

.settings-bubble :deep(.skill-page .skill-card:last-of-type) {
  border-bottom: 0 !important;
}

.settings-bubble :deep(.skill-page .skill-card-head) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) auto !important;
  gap: 16px !important;
  align-items: center !important;
}

.settings-bubble :deep(.skill-page .skill-title-wrap) {
  display: grid !important;
  grid-template-columns: 28px minmax(0, 1fr) !important;
  gap: 16px !important;
  align-items: center !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.skill-page .skill-icon-wrap) {
  width: 27px !important;
  height: 27px !important;
  min-width: 27px !important;
  min-height: 27px !important;
  border: 0 !important;
  border-radius: 9px !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.skill-page .skill-icon-wrap img) {
  object-fit: contain !important;
}

.settings-bubble :deep(.skill-page .skill-main) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 3px !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.skill-page .skill-heading) {
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.skill-page .skill-heading h3) {
  flex: 0 1 auto !important;
  max-width: min(32vw, 220px) !important;
  margin: 0 !important;
  color: #0f172a !important;
  font-size: 12.5px !important;
  font-weight: 650 !important;
  line-height: 1.2 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(.skill-page .skill-heading p) {
  display: block !important;
  flex: 1 1 auto !important;
  min-width: 0 !important;
  margin: 0 !important;
  color: #64748b !important;
  font-size: 11px !important;
  line-height: 1.25 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(.skill-page .skill-meta) {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: center !important;
  gap: 4px !important;
  margin: 0 !important;
  color: #7b6859 !important;
  font-size: 10px !important;
  line-height: 1.2 !important;
  overflow: visible !important;
  white-space: normal !important;
}

.settings-bubble :deep(.skill-page .skill-pill) {
  min-height: 17px !important;
  padding: 0 6px !important;
  border: 0 !important;
  border-radius: 999px !important;
  background: rgba(245, 158, 11, 0.055) !important;
  color: #8a6a45 !important;
  font-size: 9.5px !important;
  font-weight: 520 !important;
  line-height: 17px !important;
}

.settings-bubble :deep(.skill-page .skill-actions) {
  display: flex !important;
  flex-wrap: nowrap !important;
  justify-content: flex-end !important;
  gap: 6px !important;
  min-width: max-content !important;
}

.settings-bubble :deep(.skill-page .skill-actions .el-button + .el-button) {
  margin-left: 0 !important;
}

.settings-bubble :deep(.skill-page .skill-icon-button.el-button) {
  width: 26px !important;
  height: 26px !important;
  min-width: 26px !important;
  padding: 0 !important;
  border-radius: 999px !important;
  color: #b45309 !important;
  background: rgba(245, 158, 11, 0.1) !important;
  border-color: rgba(245, 158, 11, 0.2) !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.skill-page .skill-icon-button.danger.el-button) {
  color: #b91c1c !important;
  background: rgba(239, 68, 68, 0.07) !important;
  border-color: rgba(239, 68, 68, 0.16) !important;
}

.settings-bubble :deep(.dashboard-page) {
  gap: 8px !important;
}

.settings-bubble :deep(.dashboard-page .page-header) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) auto !important;
  gap: 6px 12px !important;
  padding: 0 0 4px !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.dashboard-page .filter-bar) {
  grid-column: 1 / -1 !important;
  display: grid !important;
  grid-template-columns: 18px repeat(3, minmax(0, 1fr)) !important;
  gap: 7px !important;
  align-items: center !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
}

.settings-bubble :deep(.dashboard-page .filter-icon) {
  width: 16px !important;
  height: 16px !important;
  object-fit: contain !important;
}

.settings-bubble :deep(.dashboard-page .kpi-grid) {
  display: grid !important;
  grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
  gap: 7px !important;
}

.settings-bubble :deep(.dashboard-page .kpi-card) {
  position: relative !important;
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  align-content: center !important;
  gap: 3px !important;
  min-height: 66px !important;
  padding: 9px 9px 8px 36px !important;
  border: 1px solid rgba(226, 232, 240, 0.76) !important;
  border-radius: 12px !important;
  background: rgba(255, 255, 255, 0.54) !important;
  box-shadow: 0 12px 30px -28px rgba(15, 23, 42, 0.28) !important;
}

.settings-bubble :deep(.dashboard-page .kpi-icon) {
  position: absolute !important;
  left: 10px !important;
  top: 12px !important;
  width: 19px !important;
  height: 19px !important;
  object-fit: contain !important;
}

.settings-bubble :deep(.dashboard-page .kpi-label) {
  color: #64748b !important;
  font-size: 10.5px !important;
  line-height: 1.2 !important;
}

.settings-bubble :deep(.dashboard-page .kpi-card strong) {
  color: #0f172a !important;
  font-size: 17px !important;
  line-height: 1 !important;
}

.settings-bubble :deep(.dashboard-page .kpi-card small) {
  color: #94a3b8 !important;
  font-size: 9.5px !important;
  line-height: 1.2 !important;
}

.settings-bubble :deep(.dashboard-page .content-grid) {
  display: grid !important;
  grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.34fr) !important;
  grid-template-areas:
    "trend detail"
    "model detail"
    "agent detail" !important;
  grid-auto-rows: minmax(112px, auto) !important;
  gap: 8px !important;
  align-items: stretch !important;
}

.settings-bubble :deep(.dashboard-page .panel-card) {
  padding: 9px 10px !important;
  border: 1px solid rgba(226, 232, 240, 0.76) !important;
  border-radius: 12px !important;
  background: rgba(255, 255, 255, 0.48) !important;
  box-shadow: 0 12px 30px -28px rgba(15, 23, 42, 0.28) !important;
}

.settings-bubble :deep(.dashboard-page .detail-panel) {
  grid-area: detail !important;
  min-height: 100% !important;
  align-self: stretch !important;
}

.settings-bubble :deep(.dashboard-page .trend-panel) {
  grid-area: trend !important;
}

.settings-bubble :deep(.dashboard-page .model-rank-panel) {
  grid-area: model !important;
}

.settings-bubble :deep(.dashboard-page .agent-rank-panel) {
  grid-area: agent !important;
}

.settings-bubble :deep(.dashboard-page .panel-head) {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  gap: 8px !important;
  margin: 0 0 7px !important;
}

.settings-bubble :deep(.dashboard-page .panel-title) {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.dashboard-page .panel-icon) {
  width: 17px !important;
  height: 17px !important;
  object-fit: contain !important;
}

.settings-bubble :deep(.dashboard-page .panel-head h2) {
  margin: 0 !important;
  color: #0f172a !important;
  font-size: 12.5px !important;
  font-weight: 680 !important;
  line-height: 1.2 !important;
}

.settings-bubble :deep(.dashboard-page .panel-head span) {
  margin: 0 !important;
  color: #64748b !important;
  font-size: 10px !important;
  line-height: 1.2 !important;
}

.settings-bubble :deep(.dashboard-page :is(.trend-list, .detail-list, .rank-list)) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 4px !important;
  margin: 0 !important;
}

.settings-bubble :deep(.dashboard-page .trend-row) {
  display: grid !important;
  grid-template-columns: 38px minmax(0, 1fr) 58px !important;
  gap: 6px !important;
  align-items: center !important;
  min-height: 20px !important;
  color: #64748b !important;
  font-size: 10px !important;
}

.settings-bubble :deep(.dashboard-page .trend-row strong) {
  justify-self: end !important;
  color: #334155 !important;
  font-size: 10px !important;
}

.settings-bubble :deep(.dashboard-page .trend-track),
.settings-bubble :deep(.dashboard-page .metric-cell i),
.settings-bubble :deep(.dashboard-page .rank-item i) {
  height: 3px !important;
  border-radius: 999px !important;
  background: rgba(245, 158, 11, 0.08) !important;
  overflow: hidden !important;
}

.settings-bubble :deep(.dashboard-page .trend-track i),
.settings-bubble :deep(.dashboard-page .metric-cell i),
.settings-bubble :deep(.dashboard-page .rank-item i) {
  display: block !important;
  height: 3px !important;
  border-radius: 999px !important;
  background: linear-gradient(90deg, rgba(245, 158, 11, 0.86), rgba(217, 119, 6, 0.48)) !important;
}

.settings-bubble :deep(.dashboard-page .detail-row) {
  display: grid !important;
  grid-template-columns: 48px repeat(4, minmax(0, 1fr)) !important;
  gap: 6px !important;
  align-items: center !important;
  min-height: 32px !important;
  padding: 4px 0 !important;
  border: 0 !important;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18) !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.dashboard-page .detail-row:last-child) {
  border-bottom: 0 !important;
}

.settings-bubble :deep(.dashboard-page :is(.date-cell, .metric-cell)) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 2px !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.dashboard-page :is(.date-cell strong, .metric-cell strong)) {
  color: #0f172a !important;
  font-size: 10.5px !important;
  line-height: 1.2 !important;
}

.settings-bubble :deep(.dashboard-page :is(.date-cell span, .metric-cell span)) {
  color: #94a3b8 !important;
  font-size: 9px !important;
  line-height: 1.2 !important;
}

.settings-bubble :deep(.dashboard-page .rank-item) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 4px !important;
  padding: 5px 0 !important;
  border: 0 !important;
  border-bottom: 1px solid rgba(148, 163, 184, 0.18) !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.dashboard-page .rank-item:last-child) {
  border-bottom: 0 !important;
}

.settings-bubble :deep(.dashboard-page .rank-line) {
  display: flex !important;
  align-items: center !important;
  gap: 6px !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.dashboard-page .rank-index) {
  width: 16px !important;
  height: 16px !important;
  display: inline-grid !important;
  place-items: center !important;
  flex: 0 0 auto !important;
  border-radius: 999px !important;
  background: rgba(245, 158, 11, 0.08) !important;
  color: #b45309 !important;
  font-size: 9px !important;
  font-weight: 650 !important;
}

.settings-bubble :deep(.dashboard-page .rank-name) {
  flex: 1 1 auto !important;
  min-width: 0 !important;
  color: #334155 !important;
  font-size: 10.5px !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(.dashboard-page .rank-line strong) {
  flex: 0 0 auto !important;
  color: #0f172a !important;
  font-size: 10.5px !important;
}

.settings-bubble :deep(.dashboard-page .empty-panel) {
  min-height: 60px !important;
  display: grid !important;
  place-items: center !important;
  gap: 4px !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  color: #94a3b8 !important;
  font-size: 10px !important;
  background: transparent !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
}

.settings-bubble :deep(.dashboard-page .empty-panel img) {
  width: 28px !important;
  height: 28px !important;
  object-fit: contain !important;
  opacity: 0.72 !important;
}

@media (max-width: 1180px) {
  .settings-bubble :deep(.kpi-grid) {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }

  .settings-bubble :deep(.dashboard-page .content-grid) {
    grid-template-columns: minmax(0, 1fr) !important;
    grid-template-areas:
      "trend"
      "detail"
      "model"
      "agent" !important;
    grid-auto-rows: auto !important;
  }
}

.composer-dock,
.composer-dock.fixed,
.workspace-chat.active .composer-dock,
.workspace-chat:not(.active) .composer-dock {
  background: transparent !important;
}

.workspace-chat.active .conversation-panel {
  width: calc(100% - 14px);
  margin: 0 6px 0 auto;
  padding-right: 4px;
  padding-bottom: 146px;
  border-radius: 0;
  background: transparent;
  overflow-y: auto;
  scrollbar-gutter: stable both-edges;
  scrollbar-width: thin;
  scrollbar-color: rgba(120, 113, 108, 0.16) transparent;
}

.workspace-chat.active .conversation-panel > .message-row,
.workspace-chat.active .conversation-panel > .settings-thread-block {
  width: min(1040px, calc(100% - 56px));
  margin-left: auto;
  margin-right: auto;
}

.workspace-chat.active .conversation-panel::-webkit-scrollbar {
  width: 10px;
}

.workspace-chat.active .conversation-panel::-webkit-scrollbar-track {
  margin: 18px 0 108px;
  border-radius: 999px;
  background: transparent;
}

.workspace-chat.active .conversation-panel::-webkit-scrollbar-thumb {
  min-height: 56px;
  border: 3px solid transparent;
  border-radius: 999px;
  background:
    linear-gradient(180deg, rgba(146, 64, 14, 0.18), rgba(120, 113, 108, 0.14))
    content-box;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.34);
}

.workspace-chat.active .conversation-panel::-webkit-scrollbar-thumb:hover {
  background:
    linear-gradient(180deg, rgba(146, 64, 14, 0.28), rgba(120, 113, 108, 0.22))
    content-box;
}

.workspace-chat.active .composer-dock.fixed {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 14px;
  z-index: 18;
  width: 100%;
  padding: 0 24px;
  pointer-events: none;
}

.workspace-chat.active .composer-dock.fixed > * {
  pointer-events: auto;
}

.workspace-chat.active .composer-collapsed {
  border-color: rgba(245, 158, 11, 0.18);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.52), rgba(255, 247, 237, 0.26)),
    rgba(245, 158, 11, 0.075);
  color: rgba(120, 53, 15, 0.82);
  box-shadow:
    0 18px 44px -30px rgba(146, 64, 14, 0.34),
    0 1px 0 rgba(255, 255, 255, 0.56) inset;
  backdrop-filter: blur(34px) saturate(1.18);
}

.workspace-chat.active .composer-collapsed:hover {
  border-color: rgba(245, 158, 11, 0.24);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.62), rgba(255, 247, 237, 0.34)),
    rgba(245, 158, 11, 0.11);
  color: rgba(100, 45, 12, 0.88);
  box-shadow:
    0 20px 50px -30px rgba(146, 64, 14, 0.4),
    0 1px 0 rgba(255, 255, 255, 0.64) inset;
}

.workspace-chat.active .composer-collapsed-icon {
  filter: drop-shadow(0 8px 12px rgba(180, 83, 9, 0.18));
}

@media (max-width: 900px) {
  .workspace-shell {
    padding: 72px 16px 18px;
  }

  .workspace-chat:not(.active) .workspace-shell {
    justify-content: flex-end;
    padding-bottom: 18px;
  }

  .intro-stack {
    gap: 12px;
    padding-bottom: 22px;
  }

  .hero-glyph {
    width: 56px;
    height: 56px;
    font-size: 30px;
  }

  .intro-stack h1 {
    font-size: 28px;
  }

  .intro-stack p {
    font-size: 15px;
  }

  .mode-switcher {
    margin-top: 52px;
  }

  .workspace-chat:not(.active) .composer-shell,
  .workspace-chat.active .composer-shell {
    width: 100%;
    min-height: 148px;
    padding: 20px 18px;
    border-radius: 22px;
  }

  .workspace-chat.active .composer-shell {
    min-height: auto;
    padding: 11px 12px 10px;
    border-radius: 18px;
  }

  .workspace-chat.active .composer {
    padding-right: 78px;
  }

  .composer-collapsed {
    min-width: min(250px, calc(100% - 24px));
    height: 50px;
    margin-bottom: 6px;
    padding: 0 22px;
    font-size: 15px;
  }

  .workspace-chat.active .conversation-panel {
    width: min(100%, calc(100% - 8px));
    padding-right: 8px;
    padding-bottom: 132px;
  }

  .workspace-chat.active .composer-dock.fixed {
    bottom: 12px;
    padding: 0 16px;
  }

  .composer-footer,
  .composer-footer-left {
    flex-direction: row;
    align-items: center;
  }

  .composer-disclaimer {
    width: 100%;
  }
}

/* Idle composer should feel like a floating input, not a large empty panel. */
.workspace-chat:not(.active) .composer-shell {
  min-height: 124px;
  display: grid;
  grid-template-rows: minmax(40px, auto) auto;
  gap: 8px;
  padding: 16px 24px 14px;
  border-radius: 26px;
}

.workspace-chat:not(.active) .composer {
  min-height: 44px;
  height: 44px;
  max-height: 68px;
  padding: 0 2px;
  font-size: 15px;
  line-height: 1.45;
}

.workspace-chat:not(.active) .composer-footer {
  min-height: 34px;
  align-items: center;
}

.workspace-chat:not(.active) .attach-btn {
  min-height: 30px;
}

.workspace-chat:not(.active) .send-btn {
  min-width: 78px;
  height: 34px;
}

@media (max-width: 900px) {
  .workspace-chat:not(.active) .composer-shell {
    min-height: 116px;
    gap: 8px;
    padding: 14px 16px 12px;
    border-radius: 22px;
  }

  .workspace-chat:not(.active) .composer {
    min-height: 40px;
    height: 40px;
    max-height: 64px;
  }
}

.intro-stack,
.mode-switcher {
  overflow: visible;
}

.mode-switcher {
  position: relative;
  isolation: isolate;
}

.mode-switcher::before {
  content: '';
  position: absolute;
  top: 4px;
  bottom: 4px;
  left: 4px;
  z-index: 0;
  width: calc((100% - 12px) / 2);
  border-radius: 999px;
  background: #f59e0b;
  box-shadow: 0 10px 22px rgba(245, 158, 11, 0.2);
  transform: translateX(0);
  transition:
    transform 0.32s cubic-bezier(0.2, 0.82, 0.18, 1),
    box-shadow 0.24s ease;
}

.mode-switcher.agent-active::before {
  transform: translateX(calc(100% + 4px));
}

.mode-switcher .mode-pill {
  position: relative;
  z-index: 1;
  background: transparent !important;
  border-color: transparent !important;
  box-shadow: none !important;
  transition: color 0.22s ease;
}

.mode-switcher .mode-pill.active {
  color: #ffffff !important;
}

.mode-switcher .mode-pill:not(.active):hover {
  color: #334155 !important;
}

.agent-picker-panel {
  position: absolute;
  top: 50%;
  left: calc(100% + 10px);
  z-index: 24;
  width: min(268px, calc(100vw - 48px));
  max-height: 232px;
  min-height: 18px;
  overflow-y: auto;
  display: grid;
  gap: 2px;
  margin: 0;
  padding: 6px;
  border: 1px solid rgba(226, 232, 240, 0.82);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.74);
  box-shadow:
    0 18px 44px rgba(15, 23, 42, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(24px);
  transform: translateY(-50%);
}

.agent-picker-panel.empty {
  min-height: 18px;
  width: min(220px, calc(100vw - 48px));
  padding-block: 8px;
}

.agent-choice {
  width: 100%;
  min-height: 42px;
  display: grid;
  grid-template-columns: 30px minmax(0, 1fr);
  align-items: center;
  gap: 9px;
  padding: 6px 8px;
  border: none;
  border-radius: 12px;
  background: transparent;
  color: #0f172a;
  text-align: left;
  cursor: pointer;
  transition: background 0.18s ease, transform 0.18s ease;
}

.agent-choice:hover,
.agent-choice.active {
  background: rgba(245, 158, 11, 0.08);
}

.agent-choice:hover {
  transform: translateY(-1px);
}

.agent-choice-avatar {
  width: 30px;
  height: 30px;
  display: block;
  object-fit: contain;
  background: transparent;
  border: 0;
  border-radius: 0;
  filter: drop-shadow(0 5px 10px rgba(15, 23, 42, 0.06));
}

.agent-choice span {
  min-width: 0;
  display: grid;
  gap: 1px;
}

.agent-choice strong,
.agent-choice small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.agent-choice strong {
  font-size: 12.5px;
  font-weight: 650;
}

.agent-choice small {
  color: #64748b;
  font-size: 10.5px;
}

.agent-picker-empty {
  min-height: 42px;
  display: grid;
  place-items: center;
  border: none;
  border-radius: 13px;
  background: rgba(248, 250, 252, 0.72);
  color: #64748b;
  font-size: 12.5px;
}

.agent-picker-enter-active,
.agent-picker-leave-active {
  transition: opacity 0.2s ease, transform 0.22s ease, filter 0.22s ease;
}

.agent-picker-enter-from,
.agent-picker-leave-to {
  opacity: 0;
  filter: blur(4px);
  transform: translate(8px, -50%) scale(0.98);
}

@media (max-width: 900px) {
  .agent-picker-panel {
    top: calc(100% + 10px);
    left: 50%;
    width: min(280px, calc(100vw - 48px));
    transform: translateX(-50%);
  }

  .agent-picker-panel.empty {
    width: min(220px, calc(100vw - 48px));
  }

  .agent-picker-enter-from,
  .agent-picker-leave-to {
    transform: translate(-50%, -6px) scale(0.98);
  }
}

.settings-bubble :deep(.agent-editor-page) {
  gap: 10px !important;
}

.settings-bubble :deep(.agent-editor-page .page-header) {
  min-height: 34px !important;
  padding: 0 0 2px 0 !important;
  border-bottom: 0 !important;
  position: relative !important;
}

.settings-bubble[data-settings-section='agent'][data-settings-detail='true'] .settings-bubble-toolbar {
  display: none !important;
}

.settings-bubble :deep(.settings-icon-button[title="刷新"]),
.settings-bubble :deep(.settings-icon-button[aria-label="刷新"]) {
  display: none !important;
}

.settings-bubble :deep(.agent-editor-page .header-left) {
  gap: 8px !important;
}

.settings-bubble :deep(.agent-editor-page .header-left > .settings-icon-button) {
  display: none !important;
}

.settings-bubble :deep(.agent-editor-page .page-header h2) {
  font-size: 16px !important;
  font-weight: 720 !important;
}

.settings-bubble :deep(.agent-editor-page .header-actions) {
  position: static !important;
  justify-self: end !important;
  align-self: center !important;
  margin-right: 0 !important;
}

.settings-bubble :deep(.agent-editor-page .editor-layout) {
  grid-template-columns: minmax(0, 1fr) !important;
  gap: 8px !important;
}

.settings-bubble :deep(.agent-editor-page .editor-main) {
  gap: 0 !important;
}

.settings-bubble :deep(.agent-editor-page .agent-config-grid) {
  display: grid !important;
  grid-template-columns: 70px minmax(160px, 0.9fr) minmax(190px, 1.1fr) minmax(150px, 0.85fr) !important;
  gap: 8px 12px !important;
  align-items: start !important;
}

.settings-bubble :deep(.agent-editor-page .agent-logo-field) {
  grid-column: 1 !important;
  grid-row: span 2 !important;
}

.settings-bubble :deep(.agent-editor-page .agent-memory-field) {
  grid-column: 4 !important;
  justify-self: end !important;
  align-self: center !important;
}

.settings-bubble :deep(.agent-editor-page .field-name) {
  grid-column: 2 !important;
}

.settings-bubble :deep(.agent-editor-page .field-description) {
  grid-column: 3 / 5 !important;
}

.settings-bubble :deep(.agent-editor-page .field-model) {
  grid-column: 2 !important;
}

.settings-bubble :deep(.agent-editor-page .field-prompt) {
  grid-column: 3 / 5 !important;
}

.settings-bubble :deep(.agent-editor-page .field-tool),
.settings-bubble :deep(.agent-editor-page .field-mcp),
.settings-bubble :deep(.agent-editor-page .field-knowledge),
.settings-bubble :deep(.agent-editor-page .field-skill) {
  grid-column: span 2 !important;
}

.settings-bubble :deep(.agent-editor-page .binding-summary) {
  grid-column: 1 / -1 !important;
  margin-top: 1px !important;
}

.settings-bubble :deep(.agent-editor-page .editor-card),
.settings-bubble :deep(.agent-editor-page .side-card) {
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.agent-editor-page .card-title-row) {
  display: none !important;
}

.settings-bubble :deep(.agent-editor-page .card-title) {
  font-size: 13px !important;
  font-weight: 700 !important;
  color: #0f172a !important;
}

.settings-bubble :deep(.agent-editor-page .memory-toggle) {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  color: #64748b !important;
  font-size: 11.5px !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(.agent-editor-page .memory-toggle .el-switch) {
  --el-switch-on-color: #f59e0b;
  --el-switch-off-color: #cbd5e1;
}

.settings-bubble :deep(.agent-editor-page .card-subtitle),
.settings-bubble :deep(.agent-editor-page .card-icon),
.settings-bubble :deep(.agent-editor-page .profile-card),
.settings-bubble :deep(.agent-editor-page .prompt-card) {
  display: none !important;
}

.settings-bubble :deep(.agent-editor-page .logo-panel) {
  gap: 6px !important;
  align-items: center !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
}

.settings-bubble :deep(.agent-editor-page .logo-preview) {
  width: 54px !important;
  height: 54px !important;
  border-radius: 16px !important;
  background: rgba(245, 158, 11, 0.08) !important;
  box-shadow:
    0 10px 24px rgba(245, 158, 11, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.88) !important;
}

.settings-bubble :deep(.agent-editor-page .logo-panel .el-button) {
  min-height: 24px !important;
  height: 24px !important;
  padding: 0 7px !important;
  border-radius: 999px !important;
  font-size: 10px !important;
  background: rgba(255, 255, 255, 0.52) !important;
}

.settings-bubble :deep(.agent-editor-page .basic-fields) {
  gap: 0 !important;
}

.settings-bubble :deep(.agent-editor-page .el-form-item) {
  display: grid !important;
  grid-template-columns: auto minmax(0, 1fr) !important;
  gap: 7px !important;
  align-items: start !important;
  margin-bottom: 0 !important;
}

.settings-bubble :deep(.agent-editor-page .el-form-item__label) {
  min-height: 30px !important;
  display: flex !important;
  align-items: center !important;
  padding: 0 !important;
  color: #475569 !important;
  font-size: 11.5px !important;
  line-height: 1.3 !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(.agent-editor-page .el-form-item.is-required:not(.is-no-asterisk).asterisk-left > .el-form-item__label::before) {
  color: rgba(245, 158, 11, 0.78) !important;
  font-weight: 700 !important;
}

.settings-bubble :deep(.agent-editor-page .el-form-item__content) {
  min-width: 0 !important;
}

.settings-bubble :deep(.agent-editor-page .el-form-item__error) {
  position: absolute !important;
  left: 0 !important;
  top: calc(100% + 2px) !important;
  margin-top: 0 !important;
  padding: 0 !important;
  color: rgba(239, 68, 68, 0.68) !important;
  font-size: 10.5px !important;
  line-height: 1.2 !important;
}

.settings-bubble :deep(.agent-editor-page :is(.el-input__wrapper, .el-select__wrapper, .el-textarea__inner)) {
  min-height: 30px !important;
  border-radius: 15px !important;
  background: rgba(255, 255, 255, 0.6) !important;
  box-shadow: 0 0 0 1px rgba(226, 232, 240, 0.88) inset !important;
}

.settings-bubble :deep(.agent-editor-page :is(.el-input__wrapper, .el-select__wrapper, .el-textarea__inner):hover) {
  box-shadow: 0 0 0 1px rgba(245, 158, 11, 0.22) inset !important;
}

.settings-bubble :deep(.agent-editor-page .el-textarea__inner) {
  min-height: 30px !important;
  resize: none !important;
  line-height: 1.45 !important;
}

.settings-bubble :deep(.agent-editor-page .capability-grid) {
  grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  gap: 0 12px !important;
}

.settings-bubble :deep(.agent-editor-page .editor-side) {
  display: block !important;
}

.settings-bubble :deep(.agent-editor-page .editor-side .side-card:not(.profile-card):not(.prompt-card)) {
  margin-top: 0 !important;
}

.settings-bubble :deep(.agent-editor-page .summary-list) {
  display: grid !important;
  grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
  gap: 6px !important;
}

.settings-bubble :deep(.agent-editor-page .binding-summary) {
  display: grid !important;
  grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
  gap: 6px !important;
}

.settings-bubble :deep(.agent-editor-page .summary-item) {
  min-width: 0 !important;
  padding: 6px 2px 4px !important;
  border: 0 !important;
  border-top: 1px solid rgba(226, 232, 240, 0.7) !important;
  border-radius: 0 !important;
  background: transparent !important;
}

.settings-bubble :deep(.agent-editor-page .summary-head) {
  align-items: center !important;
  color: #0f172a !important;
  font-size: 11px !important;
}

.settings-bubble :deep(.agent-editor-page .summary-tags) {
  gap: 4px !important;
  margin-top: 5px !important;
}

.settings-bubble :deep(.agent-editor-page .empty-text) {
  color: #94a3b8 !important;
  font-size: 10.5px !important;
}

@media (max-width: 1180px) {
  .settings-bubble :deep(.agent-editor-page .agent-config-grid),
  .settings-bubble :deep(.agent-editor-page .summary-list) {
    grid-template-columns: minmax(0, 1fr) !important;
  }

  .settings-bubble :deep(.agent-editor-page .binding-summary) {
    grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
  }

  .settings-bubble :deep(.agent-editor-page .agent-logo-field),
  .settings-bubble :deep(.agent-editor-page .agent-memory-field),
  .settings-bubble :deep(.agent-editor-page .field-name),
  .settings-bubble :deep(.agent-editor-page .field-description),
  .settings-bubble :deep(.agent-editor-page .field-model),
  .settings-bubble :deep(.agent-editor-page .field-prompt),
  .settings-bubble :deep(.agent-editor-page .field-tool),
  .settings-bubble :deep(.agent-editor-page .field-mcp),
  .settings-bubble :deep(.agent-editor-page .field-knowledge),
  .settings-bubble :deep(.agent-editor-page .field-skill),
  .settings-bubble :deep(.agent-editor-page .binding-summary) {
    grid-column: 1 !important;
  }
}

@media (max-width: 900px) {
  .settings-bubble :deep(.agent-editor-page .binding-summary) {
    grid-template-columns: minmax(0, 1fr) !important;
  }

  .settings-bubble :deep(.agent-editor-page .el-form-item) {
    grid-template-columns: minmax(0, 1fr) !important;
    gap: 3px !important;
  }
}

/* Normal chat now shares the same glass language as settings bubbles. */
.intro-status-row {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  max-width: min(680px, 100%);
  margin-top: -8px;
}

.intro-status-pill {
  min-height: 28px;
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(226, 232, 240, 0.82);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(255, 251, 245, 0.62)),
    rgba(255, 255, 255, 0.46);
  color: #64748b;
  font-size: 12px;
  font-weight: 560;
  box-shadow:
    0 12px 28px rgba(15, 23, 42, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(18px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.intro-status-pill.ready {
  border-color: rgba(245, 158, 11, 0.24);
  background:
    linear-gradient(180deg, rgba(255, 251, 235, 0.88), rgba(255, 247, 237, 0.7)),
    rgba(245, 158, 11, 0.08);
  color: #a16207;
}

.intro-status-pill.empty {
  color: #94a3b8;
}

.intro-status-pill.loading {
  color: #8a745f;
}

.intro-status-pill.subtle {
  color: #64748b;
}

.message-row {
  animation: settingsTurnIn 0.24s cubic-bezier(0.2, 0.78, 0.22, 1) both;
}

.message-row.assistant {
  align-items: flex-start;
}

.message-row.user .message-bubble {
  border-radius: 22px 22px 8px 22px;
  padding: 9px 14px;
  background:
    linear-gradient(180deg, #f8aa1b, #f59e0b);
  box-shadow:
    0 16px 32px -22px rgba(146, 64, 14, 0.62),
    inset 0 1px 0 rgba(255, 255, 255, 0.32);
}

.message-row.assistant .message-bubble {
  width: fit-content;
  max-width: min(850px, calc(100% - 58px));
  border-radius: 22px 22px 22px 10px;
  padding: 10px 14px 11px;
  border: 1px solid var(--zuno-glass-border);
  background: var(--zuno-glass-surface);
  box-shadow:
    var(--zuno-shadow-card),
    inset 0 1px 0 rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(24px) saturate(1.08);
}

.message-row.assistant .message-bubble.loading {
  min-width: min(360px, calc(100% - 58px));
}

.chat-message-meta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  color: #8a9ab0;
  font-size: 11px;
  line-height: 1;
}

.chat-message-meta strong {
  color: #0f172a;
  font-size: 12px;
  font-weight: 680;
}

.message-row.assistant .loading-row {
  min-height: 30px;
  color: #64748b;
  font-size: 12px;
}

.message-row.assistant .loading-row:not(.agent) {
  width: fit-content;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(226, 232, 240, 0.78);
  background: rgba(255, 255, 255, 0.56);
}

.message-row.assistant .loading-head,
.message-row.assistant .loading-events,
.message-row.assistant .loading-steps {
  max-width: 100%;
}

.message-row.assistant .loading-event,
.message-row.assistant .loading-step,
.message-row.assistant .phase-pill {
  background: rgba(255, 255, 255, 0.58);
  border-color: rgba(226, 232, 240, 0.76);
}

.message-bubble :deep(.md-editor-preview) {
  color: #334155;
  font-size: 12.5px;
  line-height: 1.58;
}

.message-row.user .message-bubble :deep(.md-editor-preview) {
  color: #ffffff;
}

.message-bubble :deep(.md-editor-preview p:last-child),
.message-bubble :deep(.md-editor-preview ul:last-child),
.message-bubble :deep(.md-editor-preview ol:last-child) {
  margin-bottom: 0;
}

.message-bubble :deep(pre) {
  border: 1px solid rgba(226, 232, 240, 0.72);
  background: rgba(248, 250, 252, 0.78);
  color: #1e293b;
}

.message-bubble :deep(code) {
  color: #9a3412;
  background: rgba(255, 247, 237, 0.72);
  border-radius: 6px;
  padding: 0.08em 0.32em;
}

.message-bubble :deep(pre code) {
  color: inherit;
  background: transparent;
  padding: 0;
}

.workspace-chat.active .conversation-panel {
  gap: 10px;
}

.workspace-chat.active .conversation-panel .settings-thread-block {
  margin-top: 4px;
}

.composer-disclaimer {
  color: #a8b3c4;
  font-size: 11.5px;
}

@media (max-width: 900px) {
  .intro-status-row {
    margin-top: -4px;
  }

  .message-row.assistant .message-bubble {
    max-width: min(100%, calc(100% - 36px));
    padding: 9px 11px 10px;
    border-radius: 18px 18px 18px 9px;
  }

  .message-row.user .message-bubble {
    border-radius: 18px 18px 8px 18px;
  }
}

.settings-message-stack.is-loading {
  width: var(--zuno-thread-width);
  gap: 0;
}

.settings-loading-bubble.message-bubble.assistant {
  width: min(540px, 100%);
  max-width: 100%;
  min-width: min(360px, 100%);
  min-height: 86px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 14px 18px 16px;
  border-radius: 22px 22px 22px 10px;
  animation: zunoAssistantMessageWake 0.44s cubic-bezier(0.18, 0.82, 0.22, 1) both;
}

.settings-loading-meta {
  margin-bottom: 9px;
}

.settings-loading-meta span {
  color: #c65f1f;
}

.settings-loading-row.loading-row {
  width: fit-content;
  min-height: 32px;
  display: inline-flex;
  align-items: center;
  gap: 9px;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgba(226, 232, 240, 0.78);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(255, 251, 245, 0.64)),
    rgba(255, 255, 255, 0.42);
  color: #64748b;
  box-shadow:
    0 12px 26px -22px rgba(146, 64, 14, 0.34),
    inset 0 1px 0 rgba(255, 255, 255, 0.86);
  backdrop-filter: blur(18px) saturate(1.08);
}

.settings-loading-row .spinner {
  width: 15px;
  height: 15px;
}

.message-row.motion-sending {
  animation: zunoUserMessageSend 0.42s cubic-bezier(0.18, 0.82, 0.22, 1) both;
}

.message-row.motion-thinking {
  animation: zunoAssistantMessageWake 0.44s cubic-bezier(0.18, 0.82, 0.22, 1) both;
}

.message-row.motion-complete .message-bubble.assistant {
  animation: zunoAssistantMessageComplete 0.72s cubic-bezier(0.2, 0.78, 0.22, 1) both;
}

.message-row.motion-error .message-bubble.assistant {
  animation: zunoAssistantMessageError 0.42s ease-in-out both;
  border-color: rgba(248, 113, 113, 0.32);
}

.message-bubble.motion-streaming.assistant {
  position: relative;
  overflow: hidden;
  border-color: rgba(245, 158, 11, 0.28);
}

.message-bubble.motion-streaming.assistant::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  border-radius: inherit;
  background:
    linear-gradient(115deg, transparent 0%, rgba(245, 158, 11, 0.07) 38%, rgba(255, 255, 255, 0.42) 50%, rgba(245, 158, 11, 0.06) 62%, transparent 100%);
  transform: translateX(-115%);
  animation: zunoStreamingSheen 2.15s ease-in-out infinite;
}

.message-row.motion-thinking .chat-message-meta span,
.message-row.motion-streaming .chat-message-meta span {
  color: #b45309;
}

.composer-shell.is-sending {
  animation: zunoComposerSendPulse 1.35s ease-in-out infinite;
}

.composer-shell.is-sending .send-btn {
  transform: translateY(-1px);
  box-shadow:
    0 14px 30px -18px rgba(146, 64, 14, 0.78),
    inset 0 1px 0 rgba(255, 255, 255, 0.36);
}

@keyframes zunoUserMessageSend {
  from {
    opacity: 0;
    transform: translate3d(12px, 8px, 0) scale(0.985);
    filter: blur(2px);
  }
  70% {
    opacity: 1;
    transform: translate3d(-1px, -1px, 0) scale(1.006);
    filter: blur(0);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0) scale(1);
    filter: blur(0);
  }
}

@keyframes zunoAssistantMessageWake {
  from {
    opacity: 0;
    transform: translate3d(-10px, 10px, 0) scale(0.988);
    filter: blur(2px);
  }
  to {
    opacity: 1;
    transform: translate3d(0, 0, 0) scale(1);
    filter: blur(0);
  }
}

@keyframes zunoAssistantMessageComplete {
  0% {
    box-shadow:
      0 18px 40px -28px rgba(245, 158, 11, 0.12),
      inset 0 1px 0 rgba(255, 255, 255, 0.94);
  }
  38% {
    border-color: rgba(245, 158, 11, 0.34);
    box-shadow:
      0 22px 44px -26px rgba(245, 158, 11, 0.22),
      inset 0 1px 0 rgba(255, 255, 255, 0.96);
  }
  100% {
    box-shadow:
      var(--zuno-shadow-card),
      inset 0 1px 0 rgba(255, 255, 255, 0.94);
  }
}

@keyframes zunoAssistantMessageError {
  0%,
  100% {
    transform: translateX(0);
  }
  26% {
    transform: translateX(-4px);
  }
  52% {
    transform: translateX(4px);
  }
  76% {
    transform: translateX(-2px);
  }
}

@keyframes zunoStreamingSheen {
  0% {
    transform: translateX(-115%);
    opacity: 0;
  }
  22%,
  68% {
    opacity: 1;
  }
  100% {
    transform: translateX(115%);
    opacity: 0;
  }
}

@keyframes zunoComposerSendPulse {
  0%,
  100% {
    border-color: var(--zuno-glass-border);
  }
  50% {
    border-color: rgba(245, 158, 11, 0.32);
  }
}

@media (prefers-reduced-motion: reduce) {
  .message-row.motion-sending,
  .message-row.motion-thinking,
  .message-row.motion-complete .message-bubble.assistant,
  .message-row.motion-error .message-bubble.assistant,
  .message-bubble.motion-streaming.assistant::after,
  .composer-shell.is-sending {
    animation: none;
  }
}

/* Second-level settings forms: flat, dense, and free of card nesting. */
.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
)) {
  margin: 2px 0 8px !important;
  padding: 10px 0 12px !important;
  border: 0 !important;
  border-top: 1px solid rgba(226, 232, 240, 0.72) !important;
  border-bottom: 1px solid rgba(226, 232, 240, 0.48) !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
) :is(.page-header, .workbench-head, .inline-form-head, .inline-panel-head)) {
  min-height: 32px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 10px !important;
  margin: 0 0 8px !important;
  padding: 0 !important;
  border: 0 !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
) :is(h2, h3)) {
  margin: 0 !important;
  color: #0f172a !important;
  font-size: 15px !important;
  font-weight: 730 !important;
  line-height: 1.25 !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
) :is(
  .tool-form,
  .compact-model-form,
  .compact-knowledge-form,
  .compact-form,
  .dialog-grid,
  .agent-config-grid
)) {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr)) !important;
  gap: 7px 12px !important;
  align-items: start !important;
  align-content: start !important;
}

.settings-bubble :deep(:is(
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
) :is(.field-grid, .dialog-grid)) {
  display: grid !important;
  grid-column: 1 / -1 !important;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 210px), 1fr)) !important;
  gap: 7px 12px !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
) :is(.el-form-item, .field)) {
  min-width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
  display: grid !important;
  grid-template-columns: minmax(52px, max-content) minmax(0, 1fr) !important;
  align-items: start !important;
  column-gap: 8px !important;
  row-gap: 2px !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
) :is(.el-form-item__label, .field > label)) {
  grid-column: 1 !important;
  min-height: 28px !important;
  width: auto !important;
  margin: 0 !important;
  padding: 6px 0 0 !important;
  color: #64748b !important;
  font-size: 10.5px !important;
  font-weight: 620 !important;
  line-height: 1.2 !important;
  white-space: nowrap !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
) :is(.el-form-item__content, .field > :not(label):not(small))) {
  grid-column: 2 !important;
  min-width: 0 !important;
  width: 100% !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
) :is(.span-2, .el-form-item:has(.el-textarea), .field:has(textarea))) {
  grid-column: auto / span 2 !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
) :is(.el-input__wrapper, .el-select__wrapper, .el-textarea__inner)) {
  min-height: 28px !important;
  border-radius: 9px !important;
  background: rgba(255, 255, 255, 0.54) !important;
  box-shadow:
    0 0 0 1px rgba(226, 232, 240, 0.82) inset,
    inset 0 1px 0 rgba(255, 255, 255, 0.74) !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
) .el-textarea__inner) {
  min-height: 28px !important;
  padding-top: 5px !important;
  padding-bottom: 5px !important;
  line-height: 1.42 !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
) :is(.nested-panel, .advanced-block, .cli-panel, .config-section, .source-intro)) {
  grid-column: 1 / -1 !important;
  margin: 2px 0 0 !important;
  padding: 8px 0 0 !important;
  border: 0 !important;
  border-top: 1px solid rgba(226, 232, 240, 0.64) !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.tool-workbench-card .panel-head),
.settings-bubble :deep(.tool-workbench-card .panel-head h3) {
  display: none !important;
}

.settings-bubble :deep(.tool-workbench-card .advanced-block) {
  padding-top: 2px !important;
}

.settings-bubble :deep(.tool-workbench-card .advanced-block .el-collapse) {
  border: 0 !important;
}

.settings-bubble :deep(.tool-workbench-card .advanced-block .el-collapse-item__header) {
  min-height: 28px !important;
  height: 28px !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
  color: #94a3b8 !important;
  font-size: 11px !important;
}

.settings-bubble :deep(.tool-workbench-card .advanced-block .el-collapse-item__wrap) {
  border: 0 !important;
  background: transparent !important;
}

.settings-bubble :deep(.tool-workbench-card .advanced-block .el-collapse-item__content) {
  padding: 4px 0 0 !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .tool-workbench-card,
  .inline-panel.create-panel
) .logo-upload-row),
.settings-bubble :deep(.agent-editor-page .logo-panel) {
  display: inline-flex !important;
  align-items: center !important;
  gap: 7px !important;
  padding: 0 !important;
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .tool-workbench-card,
  .inline-panel.create-panel
) :is(.logo-preview, .avatar-wrap)) {
  width: 30px !important;
  height: 30px !important;
  min-width: 30px !important;
  min-height: 30px !important;
  border-radius: 9px !important;
  background: rgba(245, 158, 11, 0.06) !important;
  box-shadow: none !important;
}

.settings-bubble :deep(:is(
  .agent-inline-editor,
  .tool-workbench-card,
  .inline-panel.create-panel
) :is(.logo-upload-row .el-button, .logo-panel .el-button)) {
  min-height: 26px !important;
  height: 26px !important;
  padding: 0 8px !important;
  border-radius: 999px !important;
  font-size: 10.5px !important;
  color: #8a6a45 !important;
  background: rgba(255, 255, 255, 0.5) !important;
}

.settings-bubble :deep(.tool-workbench-card .form-utility-row) {
  grid-column: 1 / -1 !important;
  margin: -1px 0 0 !important;
  padding: 0 !important;
  gap: 6px !important;
}

.settings-bubble :deep(.tool-workbench-card .inline-utility-button) {
  min-height: 26px !important;
  height: 26px !important;
  padding: 0 9px !important;
  border-radius: 999px !important;
  font-size: 10.5px !important;
  border-color: rgba(245, 158, 11, 0.18) !important;
  background: rgba(245, 158, 11, 0.06) !important;
  color: #b45309 !important;
}

.settings-bubble :deep(.mcp-workbench-panel .transport-switch) {
  grid-column: 1 / -1 !important;
  margin: 0 !important;
}

.settings-bubble :deep(.mcp-workbench-panel .inline-row) {
  display: grid !important;
  grid-template-columns: repeat(2, minmax(110px, 1fr)) 24px !important;
  align-items: center !important;
  gap: 6px !important;
  margin: 0 !important;
}

.settings-bubble :deep(.mcp-workbench-panel .inline-row.one-col) {
  grid-template-columns: minmax(0, 1fr) 24px !important;
}

.settings-bubble :deep(.mcp-workbench-panel .repeat-stack) {
  display: grid !important;
  gap: 5px !important;
  min-width: 0 !important;
}

.settings-bubble :deep(.mcp-workbench-panel .repeat-stack.is-empty) {
  width: max-content !important;
  max-width: 100% !important;
}

.settings-bubble :deep(.mcp-workbench-panel .field > .repeat-stack.is-empty) {
  width: max-content !important;
}

.settings-bubble :deep(.mcp-workbench-panel .repeat-add) {
  --el-button-bg-color: transparent !important;
  --el-button-border-color: transparent !important;
  --el-button-hover-bg-color: rgba(245, 158, 11, 0.08) !important;
  --el-button-hover-border-color: transparent !important;
  justify-self: start !important;
  width: max-content !important;
  max-width: max-content !important;
  min-height: 22px !important;
  height: 22px !important;
  padding: 0 7px !important;
  border: 0 !important;
  border-radius: 999px !important;
  background: transparent !important;
  color: #b45309 !important;
  box-shadow: none !important;
  font-size: 10.5px !important;
}

.settings-bubble :deep(.mcp-workbench-panel .repeat-remove) {
  width: 22px !important;
  height: 22px !important;
  min-width: 22px !important;
  padding: 0 !important;
  color: #b76b45 !important;
  background: rgba(255, 255, 255, 0.45) !important;
}

.settings-bubble :deep(.mcp-workbench-panel .field > .el-button),
.settings-bubble :deep(.mcp-workbench-panel .inline-row .el-button) {
  min-height: 24px !important;
  padding: 0 6px !important;
  font-size: 10.5px !important;
}

.settings-bubble :deep(.mcp-workbench-panel .inline-row .repeat-remove) {
  min-height: 22px !important;
  padding: 0 !important;
}

.settings-bubble :deep(.agent-editor-page .binding-summary) {
  margin-top: 2px !important;
  padding-top: 5px !important;
  border-top: 1px solid rgba(226, 232, 240, 0.6) !important;
}

.settings-bubble :deep(.agent-editor-page .summary-item) {
  padding: 0 !important;
  border: 0 !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .page-header) {
  display: grid !important;
  grid-template-columns: minmax(0, 1fr) auto !important;
  align-items: center !important;
  justify-items: stretch !important;
  margin: 0 0 6px !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .header-left) {
  justify-self: start !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .editor-layout) {
  margin: 0 !important;
  padding: 0 !important;
  gap: 0 !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .agent-config-grid) {
  grid-template-columns: 42px repeat(4, minmax(120px, 1fr)) !important;
  gap: 6px 10px !important;
  margin: 0 !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .agent-logo-field) {
  grid-column: 1 !important;
  grid-row: 1 / span 2 !important;
  align-self: start !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .logo-panel .el-button) {
  width: 28px !important;
  min-width: 28px !important;
  padding: 0 !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .logo-panel .el-button span) {
  display: none !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .agent-memory-field) {
  grid-column: 5 !important;
  justify-self: end !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-name) {
  grid-column: 2 !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-description) {
  grid-column: 3 / span 2 !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-model) {
  grid-column: 2 !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-prompt) {
  grid-column: 3 / span 3 !important;
}

.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-tool),
.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-mcp),
.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-knowledge),
.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-skill) {
  grid-column: span 2 !important;
}

.settings-bubble :deep(:is(.el-form-item__error, .utility-status, .empty-text)) {
  font-size: 10.5px !important;
}

/* Settings form language: ink-line controls instead of boxed rectangles. */
.settings-bubble :deep(:is(
  .el-input__wrapper.el-input__wrapper,
  .el-select__wrapper.el-select__wrapper,
  .el-input-number .el-input__wrapper.el-input__wrapper
)) {
  min-height: 30px !important;
  padding: 0 3px 2px !important;
  border: 0 !important;
  border-radius: 0 !important;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.34) 14%, rgba(148, 163, 184, 0.46) 72%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 255, 255, 0.34), rgba(255, 255, 255, 0.08)) !important;
  box-shadow: none !important;
  transition: background 180ms ease, box-shadow 180ms ease, transform 180ms ease !important;
}

.settings-bubble :deep(.el-textarea__inner.el-textarea__inner) {
  min-height: 30px !important;
  padding: 5px 3px 7px !important;
  border: 0 !important;
  border-radius: 0 !important;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.34) 14%, rgba(148, 163, 184, 0.46) 72%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 255, 255, 0.32), rgba(255, 255, 255, 0.08)) !important;
  box-shadow: none !important;
  transition: background 180ms ease, box-shadow 180ms ease !important;
}

.settings-bubble :deep(:is(.el-input, .el-select, .el-textarea):hover :is(.el-input__wrapper.el-input__wrapper, .el-select__wrapper.el-select__wrapper, .el-textarea__inner.el-textarea__inner)) {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.28) 16%, rgba(148, 163, 184, 0.38) 78%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 251, 247, 0.38), rgba(255, 255, 255, 0.08)) !important;
}

.settings-bubble :deep(:is(.el-input.is-focus .el-input__wrapper.el-input__wrapper, .el-input__wrapper.el-input__wrapper:focus-within, .el-select__wrapper.el-select__wrapper.is-focused, .el-select__wrapper.el-select__wrapper:focus-within, .el-textarea__inner.el-textarea__inner:focus)) {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.88) 18%, rgba(217, 119, 6, 0.9) 58%, rgba(245, 158, 11, 0)) left bottom / 100% 2px no-repeat,
    radial-gradient(85% 120% at 48% 100%, rgba(245, 158, 11, 0.12), rgba(245, 158, 11, 0) 58%),
    linear-gradient(180deg, rgba(255, 251, 247, 0.48), rgba(255, 255, 255, 0.08)) !important;
  box-shadow: 0 10px 22px -22px rgba(180, 83, 9, 0.42) !important;
}

.settings-bubble :deep(:is(.el-input__inner, .el-select__placeholder, .el-select__selected-item, .el-textarea__inner)) {
  color: #334155 !important;
  font-size: 12px !important;
}

.settings-bubble :deep(:is(.el-input__inner::placeholder, .el-textarea__inner::placeholder, .el-select__placeholder)) {
  color: #a8b1c0 !important;
}

.settings-bubble :deep(:is(.el-input__prefix, .el-input__suffix, .el-select__suffix)) {
  color: #94a3b8 !important;
}

.settings-bubble :deep(:is(.el-radio-group, .el-checkbox-group)) {
  display: inline-flex !important;
  flex-wrap: wrap !important;
  gap: 4px 12px !important;
  min-height: 28px !important;
  align-items: center !important;
  background: transparent !important;
}

.settings-bubble :deep(:is(.el-radio-button, .el-checkbox-button)) {
  margin: 0 !important;
}

.settings-bubble :deep(:is(.el-radio-button__inner.el-radio-button__inner, .el-checkbox-button__inner.el-checkbox-button__inner)) {
  min-height: 26px !important;
  height: 26px !important;
  padding: 0 3px 3px !important;
  border: 0 !important;
  border-radius: 0 !important;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.26), rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat !important;
  color: #64748b !important;
  box-shadow: none !important;
  font-size: 11px !important;
  font-weight: 600 !important;
  line-height: 25px !important;
  transition: color 160ms ease, background 160ms ease, transform 160ms ease !important;
}

.settings-bubble :deep(:is(.el-radio-button:first-child .el-radio-button__inner.el-radio-button__inner, .el-radio-button:last-child .el-radio-button__inner.el-radio-button__inner, .el-checkbox-button:first-child .el-checkbox-button__inner.el-checkbox-button__inner, .el-checkbox-button:last-child .el-checkbox-button__inner.el-checkbox-button__inner)) {
  border-radius: 0 !important;
}

.settings-bubble :deep(:is(.el-radio-button__inner.el-radio-button__inner:hover, .el-checkbox-button__inner.el-checkbox-button__inner:hover)) {
  color: #b45309 !important;
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.42), rgba(245, 158, 11, 0)) left bottom / 100% 1px no-repeat !important;
}

.settings-bubble :deep(:is(.el-radio-button.is-active .el-radio-button__inner.el-radio-button__inner, .el-checkbox-button.is-checked .el-checkbox-button__inner.el-checkbox-button__inner, .el-radio-button__original-radio:checked + .el-radio-button__inner.el-radio-button__inner, .el-checkbox-button__original:checked + .el-checkbox-button__inner.el-checkbox-button__inner)) {
  color: #b45309 !important;
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.92) 22%, rgba(217, 119, 6, 0.88) 68%, rgba(245, 158, 11, 0)) left bottom / 100% 2px no-repeat,
    radial-gradient(80% 90% at 50% 100%, rgba(245, 158, 11, 0.12), rgba(245, 158, 11, 0) 64%) !important;
  box-shadow: none !important;
}

.settings-bubble :deep(:is(.el-select .el-tag, .el-select__tags .el-tag, .el-select__selection .el-tag)) {
  min-height: 18px !important;
  height: 18px !important;
  padding: 0 5px !important;
  border: 0 !important;
  border-radius: 0 !important;
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.34), rgba(245, 158, 11, 0)) left bottom / 100% 1px no-repeat !important;
  color: #9a5b0f !important;
  font-size: 10.5px !important;
}

.settings-bubble :deep(:is(.logo-upload-row .el-button, .inline-utility-button, .repeat-add, .config-actions .el-button:not(.el-button--primary))) {
  border: 0 !important;
  border-radius: 0 !important;
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.38), rgba(245, 158, 11, 0)) left bottom / 100% 1px no-repeat !important;
  box-shadow: none !important;
}

@media (max-width: 980px) {
  .settings-bubble :deep(:is(
    .agent-inline-editor,
    .model-form-panel,
    .knowledge-form-panel,
    .tool-workbench-card,
    .mcp-workbench-panel,
    .inline-panel.create-panel
  ) :is(.span-2, .el-form-item:has(.el-textarea), .field:has(textarea))) {
    grid-column: 1 / -1 !important;
  }
}

.settings-bubble :deep(.el-input.el-input .el-input__wrapper.el-input__wrapper),
.settings-bubble :deep(.el-select.el-select .el-select__wrapper.el-select__wrapper),
.settings-bubble :deep(.el-input-number.el-input-number .el-input__wrapper.el-input__wrapper) {
  border: 0 !important;
  border-radius: 0 !important;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.34) 14%, rgba(148, 163, 184, 0.46) 72%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 255, 255, 0.34), rgba(255, 255, 255, 0.08)) !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.el-textarea.el-textarea .el-textarea__inner.el-textarea__inner) {
  border: 0 !important;
  border-radius: 0 !important;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.34) 14%, rgba(148, 163, 184, 0.46) 72%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 255, 255, 0.32), rgba(255, 255, 255, 0.08)) !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.el-radio-button.el-radio-button .el-radio-button__inner.el-radio-button__inner),
.settings-bubble :deep(.el-checkbox-button.el-checkbox-button .el-checkbox-button__inner.el-checkbox-button__inner) {
  border: 0 !important;
  border-radius: 0 !important;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.26), rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.mcp-workbench-panel :is(.el-input__wrapper.el-input__wrapper, .el-select__wrapper.el-select__wrapper, .el-textarea__inner.el-textarea__inner)) {
  border: 0 !important;
  border-radius: 0 !important;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.34) 14%, rgba(148, 163, 184, 0.44) 72%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 255, 255, 0.28), rgba(255, 255, 255, 0.04)) !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.mcp-workbench-panel :is(.config-summary div, .readonly-chip, .meta-pill, .official-tag, .repeat-add)) {
  border: 0 !important;
  border-radius: 0 !important;
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.34), rgba(245, 158, 11, 0)) left bottom / 100% 1px no-repeat !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.mcp-workbench-panel .repeat-remove.el-button) {
  background: transparent !important;
  border-color: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.mcp-workbench-panel :is(.empty-panel, .tool-card)) {
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.mcp-workbench-panel :is(.field, .inline-row, .repeat-stack, .repeat-field)) {
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(.mcp-workbench-panel .field) {
  min-height: 0 !important;
  padding: 2px 0 !important;
}

.settings-bubble :deep(.mcp-workbench-panel .repeat-stack) {
  padding: 0 !important;
}

.settings-bubble :deep(.mcp-workbench-panel :is(.mcp-line-input, .mcp-line-value)) {
  border: 0 !important;
  border-radius: 0 !important;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.34) 14%, rgba(148, 163, 184, 0.44) 72%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 255, 255, 0.28), rgba(255, 255, 255, 0.04)) !important;
  box-shadow: none !important;
  outline: none !important;
}

/* Phase 2: Zuno pet as the live conversation presence. */
.intro-pet {
  margin-bottom: 2px;
}

.workspace-chat:not(.active) .intro-pet {
  transform: translateY(0);
}

.assistant-pet-avatar.avatar {
  width: 44px;
  height: 44px;
  flex: 0 0 44px;
  align-self: flex-start;
  margin-top: 0;
  margin-left: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.message-row > img.avatar {
  width: 44px;
  height: 44px;
  flex: 0 0 44px;
  align-self: flex-start;
  margin-top: 0;
  border-radius: 14px;
  object-fit: cover;
  background: transparent;
  box-shadow: none;
}

.message-row.user {
  align-items: flex-start;
}

.message-row.user .message-bubble {
  margin-top: 3px;
}

.message-row.assistant .assistant-pet-avatar {
  margin-top: 0;
}

.settings-panel-row .assistant-pet-avatar {
  margin-top: 0;
}

.assistant-pet-avatar.is-animated {
  filter: drop-shadow(0 8px 18px rgba(15, 23, 42, 0.12));
}

/* Phase 3: richer normal conversation typography and quiet message tools. */
.message-bubble.has-content {
  position: relative;
}

.message-bubble.has-attachments {
  position: relative;
}

.message-row.assistant .message-bubble.has-content {
  padding: 10px 40px 11px 14px;
}

.message-row.user .message-bubble.has-content {
  padding: 9px 38px 9px 14px;
}

.message-row.user .message-bubble {
  max-width: min(680px, 76%);
  word-break: break-word;
}

.message-row.assistant .message-bubble {
  max-width: min(920px, calc(100% - 58px));
}

.message-row.user .message-bubble.has-attachments {
  padding-bottom: 10px;
}

.message-content {
  min-width: 0;
  max-width: 100%;
}

.message-actions {
  position: absolute;
  top: 7px;
  right: 7px;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  opacity: 0;
  transform: translateY(-2px) scale(0.96);
  pointer-events: none;
  transition: opacity 160ms ease, transform 160ms ease;
}

.message-bubble.has-content:hover .message-actions,
.message-bubble.has-content:focus-within .message-actions {
  opacity: 1;
  transform: translateY(0) scale(1);
  pointer-events: auto;
}

.message-action {
  width: 24px;
  height: 24px;
  display: inline-grid;
  place-items: center;
  padding: 0;
  border-radius: 999px;
  border: 1px solid rgba(226, 232, 240, 0.82);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.86), rgba(255, 251, 245, 0.64)),
    rgba(255, 255, 255, 0.5);
  color: #64748b;
  cursor: pointer;
  box-shadow:
    0 10px 22px -18px rgba(15, 23, 42, 0.28),
    inset 0 1px 0 rgba(255, 255, 255, 0.92);
  transition: color 160ms ease, border-color 160ms ease, transform 160ms ease, background 160ms ease;
}

.message-action:hover {
  transform: translateY(-1px);
  color: #b45309;
  border-color: rgba(245, 158, 11, 0.34);
  background:
    linear-gradient(180deg, rgba(255, 251, 235, 0.94), rgba(255, 247, 237, 0.68)),
    rgba(245, 158, 11, 0.08);
}

.message-action :deep(.el-icon) {
  font-size: 13px;
}

.message-row.user .message-action {
  border-color: rgba(255, 255, 255, 0.24);
  background: rgba(255, 255, 255, 0.16);
  color: rgba(255, 255, 255, 0.9);
  box-shadow: none;
}

.message-row.user .message-action:hover {
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.46);
  background: rgba(255, 255, 255, 0.24);
}

.message-content :deep(.md-editor),
.message-content :deep(.md-editor-preview),
.message-content :deep(.md-editor-preview-wrapper) {
  background: transparent !important;
  color: inherit;
  padding: 0 !important;
  box-shadow: none !important;
}

.zuno-prose :deep(.md-editor-preview) {
  color: #334155;
  font-size: 13px;
  line-height: 1.66;
  letter-spacing: 0;
  word-break: break-word;
}

.zuno-prose :deep(.md-editor-preview > *:first-child) {
  margin-top: 0 !important;
}

.zuno-prose :deep(.md-editor-preview > *:last-child) {
  margin-bottom: 0 !important;
}

.zuno-prose :deep(p) {
  margin: 0 0 0.58em;
}

.zuno-prose :deep(a) {
  color: #b45309;
  text-decoration: none;
  border-bottom: 1px solid rgba(245, 158, 11, 0.32);
}

.zuno-prose :deep(a:hover) {
  color: #92400e;
  border-bottom-color: rgba(245, 158, 11, 0.68);
}

.zuno-prose :deep(h1),
.zuno-prose :deep(h2),
.zuno-prose :deep(h3),
.zuno-prose :deep(h4) {
  margin: 0.2em 0 0.44em;
  color: #0f172a;
  font-weight: 720;
  line-height: 1.28;
  letter-spacing: 0;
}

.zuno-prose :deep(h1) { font-size: 1.2em; }
.zuno-prose :deep(h2) { font-size: 1.12em; }
.zuno-prose :deep(h3) { font-size: 1.04em; }
.zuno-prose :deep(h4) { font-size: 1em; }

.zuno-prose :deep(ul),
.zuno-prose :deep(ol) {
  margin: 0.28em 0 0.62em 1.15em;
  padding: 0;
}

.zuno-prose :deep(li) {
  margin: 0.14em 0;
  padding-left: 0.05em;
}

.zuno-prose :deep(li::marker) {
  color: #d97706;
  font-weight: 700;
}

.zuno-prose :deep(blockquote) {
  margin: 0.52em 0;
  padding: 0.18em 0 0.18em 0.74em;
  border-left: 2px solid rgba(245, 158, 11, 0.46);
  color: #64748b;
  background: transparent;
}

.zuno-prose :deep(pre) {
  max-width: 100%;
  overflow: auto;
  margin: 0.58em 0;
  padding: 10px 12px;
  border: 1px solid rgba(226, 232, 240, 0.76);
  border-radius: 12px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(248, 250, 252, 0.64)),
    rgba(248, 250, 252, 0.72);
  color: #1e293b;
  font-size: 11.5px;
  line-height: 1.52;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
}

.zuno-prose :deep(pre::-webkit-scrollbar),
.zuno-prose :deep(table::-webkit-scrollbar) {
  height: 7px;
}

.zuno-prose :deep(pre::-webkit-scrollbar-track),
.zuno-prose :deep(table::-webkit-scrollbar-track) {
  background: rgba(248, 250, 252, 0.72);
  border-radius: 999px;
}

.zuno-prose :deep(pre::-webkit-scrollbar-thumb),
.zuno-prose :deep(table::-webkit-scrollbar-thumb) {
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.34);
}

.zuno-prose :deep(code) {
  padding: 0.08em 0.34em;
  border-radius: 6px;
  background: rgba(255, 247, 237, 0.72);
  color: #9a3412;
  font-size: 0.9em;
}

.zuno-prose :deep(pre code) {
  padding: 0;
  border-radius: 0;
  background: transparent;
  color: inherit;
  font-size: inherit;
}

.zuno-prose :deep(table) {
  display: block;
  width: 100%;
  max-width: 100%;
  overflow: auto;
  margin: 0.62em 0;
  border-collapse: collapse;
  font-size: 12px;
}

.zuno-prose :deep(hr) {
  height: 1px;
  margin: 0.8em 0;
  border: 0;
  background: linear-gradient(90deg, transparent, rgba(226, 232, 240, 0.92), transparent);
}

.zuno-prose :deep(img) {
  max-width: min(100%, 560px);
  max-height: 360px;
  display: block;
  margin: 0.62em 0;
  border-radius: 14px;
  object-fit: contain;
  border: 1px solid rgba(226, 232, 240, 0.78);
}

.zuno-prose :deep(th),
.zuno-prose :deep(td) {
  padding: 6px 8px;
  border: 0;
  border-bottom: 1px solid rgba(226, 232, 240, 0.78);
  text-align: left;
  white-space: nowrap;
}

.zuno-prose :deep(th) {
  color: #0f172a;
  font-weight: 700;
  background: rgba(255, 251, 245, 0.5);
}

.user-prose :deep(.md-editor-preview) {
  color: #ffffff;
  font-size: 13px;
  line-height: 1.52;
  letter-spacing: 0;
  word-break: break-word;
}

.user-prose :deep(p),
.user-prose :deep(ul),
.user-prose :deep(ol) {
  margin-top: 0;
}

.user-prose :deep(p:last-child),
.user-prose :deep(ul:last-child),
.user-prose :deep(ol:last-child) {
  margin-bottom: 0;
}

.message-attachments {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 176px), 1fr));
  gap: 7px;
  margin-top: 9px;
  min-width: min(420px, 100%);
}

.message-attachment-card {
  min-width: 0;
  min-height: 42px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 9px;
  border-radius: 14px;
  text-decoration: none;
  border: 1px solid rgba(226, 232, 240, 0.76);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.72), rgba(248, 250, 252, 0.54)),
    rgba(255, 255, 255, 0.56);
  color: #334155;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.82);
  transition: transform 160ms ease, border-color 160ms ease, background 160ms ease;
}

.message-attachment-card:hover {
  transform: translateY(-1px);
  border-color: rgba(245, 158, 11, 0.34);
  background:
    linear-gradient(180deg, rgba(255, 251, 235, 0.9), rgba(255, 247, 237, 0.62)),
    rgba(245, 158, 11, 0.08);
}

.message-row.user .message-attachment-card {
  border-color: rgba(255, 255, 255, 0.24);
  background: rgba(255, 255, 255, 0.15);
  color: #ffffff;
  box-shadow: none;
}

.message-row.user .message-attachment-card:hover {
  border-color: rgba(255, 255, 255, 0.45);
  background: rgba(255, 255, 255, 0.22);
}

.message-attachment-thumb,
.message-attachment-file {
  width: 30px;
  height: 30px;
  flex: 0 0 30px;
  border-radius: 10px;
}

.message-attachment-thumb {
  object-fit: cover;
}

.message-attachment-file {
  display: grid;
  place-items: center;
  border: 1px solid rgba(245, 158, 11, 0.22);
  background: rgba(245, 158, 11, 0.08);
  color: #b45309;
  font-size: 8px;
  font-weight: 760;
  letter-spacing: 0;
}

.message-row.user .message-attachment-file {
  border-color: rgba(255, 255, 255, 0.24);
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
}

.message-attachment-copy {
  min-width: 0;
  display: grid;
  gap: 1px;
}

.message-attachment-copy strong {
  overflow: hidden;
  color: inherit;
  font-size: 11.5px;
  font-weight: 690;
  line-height: 1.25;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message-attachment-copy small {
  color: #94a3b8;
  font-size: 10.5px;
}

.message-row.user .message-attachment-copy small {
  color: rgba(255, 255, 255, 0.72);
}

.message-bubble.motion-streaming.assistant .message-content::after {
  content: '';
  display: inline-block;
  width: 5px;
  height: 1.08em;
  margin-left: 4px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.78);
  vertical-align: -0.15em;
  animation: zunoTypingCaret 0.95s ease-in-out infinite;
}

@keyframes zunoTypingCaret {
  0%, 42% { opacity: 1; transform: translateY(1px); }
  58%, 100% { opacity: 0.18; transform: translateY(1px); }
}

@media (max-width: 760px) {
  .assistant-pet-avatar.avatar {
    width: 38px;
    height: 38px;
    flex-basis: 38px;
    --mascot-slot-size: 38px;
    --mascot-scale: 0.3166667;
  }

  .message-row > img.avatar {
    width: 38px;
    height: 38px;
    flex-basis: 38px;
    border-radius: 12px;
  }

  .message-row.user .message-bubble {
    max-width: min(100%, calc(100% - 46px));
  }

  .message-attachments {
    grid-template-columns: 1fr;
    min-width: 0;
  }
}

/* Zuno premium polish: make chat and settings feel like one product, not two skins. */
.workspace-chat {
  --zuno-thread-width: min(1040px, calc(100% - 56px));
  color: #0f172a;
}

.workspace-shell {
  background:
    radial-gradient(circle at 58% 18%, rgba(255, 255, 255, 0.94), transparent 32%),
    radial-gradient(circle at 50% 105%, rgba(245, 158, 11, 0.052), transparent 34%),
    linear-gradient(180deg, #fbfcff 0%, #f7f8fb 100%);
}

.intro-stack h1 {
  color: #0f172a;
  letter-spacing: 0;
}

.intro-stack p,
.hero-subtitle,
.composer-disclaimer {
  color: #64748b;
}

.intro-status-pill {
  min-height: 24px;
  padding: 0 2px 3px;
  border: 0;
  border-radius: 0;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.28), rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat;
  box-shadow: none;
  backdrop-filter: none;
}

.intro-status-pill.ready {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.42), rgba(245, 158, 11, 0)) left bottom / 100% 1px no-repeat;
}

.conversation-panel {
  width: 100%;
  padding-inline: max(22px, calc((100% - 1040px) / 2));
  scroll-padding-bottom: 148px;
}

.message-row,
.settings-thread-block {
  width: 100%;
}

.message-row.user .message-bubble {
  border-radius: 16px 16px 6px 16px;
  background: linear-gradient(180deg, #f8aa1b, #f59e0b);
}

.message-row.assistant .message-bubble {
  border-radius: 16px 16px 16px 6px;
  border-color: rgba(226, 232, 240, 0.72);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(248, 250, 252, 0.78)),
    rgba(255, 255, 255, 0.82);
  box-shadow:
    0 20px 50px -34px rgba(15, 23, 42, 0.22),
    inset 0 1px 0 rgba(255, 255, 255, 0.94);
}

.chat-message-meta {
  color: #94a3b8;
}

.chat-message-meta span {
  color: #94a3b8;
}

.message-actions {
  right: 8px;
}

.message-action {
  border-radius: 8px;
  box-shadow: none;
}

.settings-message-stack {
  width: var(--zuno-thread-width);
}

.settings-message-meta {
  padding-left: 2px;
}

.settings-bubble {
  padding: 18px 20px;
  border-radius: 18px 18px 18px 6px;
  border-color: rgba(226, 232, 240, 0.74);
  background:
    radial-gradient(circle at 88% 0%, rgba(245, 158, 11, 0.042), transparent 28%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.82)),
    rgba(255, 255, 255, 0.84);
  box-shadow:
    0 24px 68px -42px rgba(15, 23, 42, 0.28),
    inset 0 1px 0 rgba(255, 255, 255, 0.96);
}

.settings-bubble :deep(.agent-hero),
.settings-bubble :deep(.page-header),
.settings-bubble :deep(.page-hero),
.settings-bubble :deep(.hero-card) {
  border-bottom-color: rgba(226, 232, 240, 0.58) !important;
}

.settings-bubble :deep(.toolbar-card),
.settings-bubble :deep(.content-card),
.settings-bubble :deep(.table-card),
.settings-bubble :deep(.list-card),
.settings-bubble :deep(.agent-card),
.settings-bubble :deep(.editor-card),
.settings-bubble :deep(.side-card),
.settings-bubble :deep(.logo-panel),
.settings-bubble :deep(.model-card),
.settings-bubble :deep(.knowledge-card),
.settings-bubble :deep(.mcp-card),
.settings-bubble :deep(.tool-card),
.settings-bubble :deep(.skill-card),
.settings-bubble :deep(.config-panel),
.settings-bubble :deep(.config-card),
.settings-bubble :deep(.preview-card),
.settings-bubble :deep(.form-card),
.settings-bubble :deep(.summary-card),
.settings-bubble :deep(.summary-block) {
  border-width: 0 0 1px !important;
  border-color: rgba(226, 232, 240, 0.66) !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  backdrop-filter: none !important;
}

.settings-bubble :deep(.kpi-card),
.settings-bubble :deep(.panel-card) {
  border-radius: 8px !important;
}

.settings-loading-bubble.message-bubble.assistant {
  min-height: 82px;
}

.settings-loading-row.loading-row {
  border-radius: 14px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(248, 250, 252, 0.72)),
    rgba(255, 255, 255, 0.72);
}

.settings-loading-row i {
  width: 4px;
  height: 4px;
  border-radius: 999px;
  background: #f59e0b;
  opacity: 0.42;
  animation: zunoSettingsLoadDot 1.12s ease-in-out infinite;
}

.settings-loading-row i:nth-of-type(2) {
  animation-delay: 0.16s;
}

.settings-loading-row i:nth-of-type(3) {
  animation-delay: 0.32s;
}

.picker-card,
.picker-summary,
.progress-inline,
.trace-item,
.trace-round-item,
.attachment-chip {
  border-color: rgba(226, 232, 240, 0.76);
  border-radius: 8px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.78), rgba(248, 250, 252, 0.58)),
    rgba(255, 255, 255, 0.68);
  color: #475569;
  box-shadow: none;
}

.picker-item,
.picker-summary,
.trace-detail,
.trace-reason,
.trace-round-head span,
.trace-round-body span,
.attachment-chip {
  color: #475569;
}

.picker-summary strong,
.trace-round-head strong {
  color: #0f172a;
}

.picker-item small,
.trace-head-copy small,
.empty-copy,
.attachment-size {
  color: #94a3b8;
}

.progress-badge,
.phase-pill,
.trace-pill {
  border: 0;
  border-radius: 0;
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.34), rgba(245, 158, 11, 0)) left bottom / 100% 1px no-repeat;
  color: #b45309;
}

.progress-step {
  border: 0;
  border-radius: 0;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.28), rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat;
  color: #64748b;
}

.progress-step.active {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.56), rgba(245, 158, 11, 0)) left bottom / 100% 2px no-repeat,
    rgba(245, 158, 11, 0.03);
  color: #b45309;
}

.progress-dot,
.progress-step.done .progress-dot,
.progress-step.active .progress-dot {
  background: #f59e0b;
}

@keyframes zunoSettingsLoadDot {
  0%, 80%, 100% {
    transform: translateY(0);
    opacity: 0.34;
  }
  38% {
    transform: translateY(-3px);
    opacity: 0.9;
  }
}

@media (max-width: 900px) {
  .workspace-chat {
    --zuno-thread-width: 100%;
  }

  .conversation-panel {
    padding-inline: 14px;
  }

  .settings-bubble {
    padding: 14px;
  }
}

/* Correction pass: settings content should be clean text + single-line inputs, not orange backplates. */
.settings-bubble :deep(:is(.settings-search-row, .search-row, .filter-row, .toolbar-card)) {
  border-bottom: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble :deep(:is(
  .meta-pill,
  .badge,
  .tag,
  .status-pill,
  .official-tag,
  .custom-tag,
  .config-badge,
  .hint-chip,
  .phase-pill,
  .trace-pill,
  .type-badge,
  .capability-badge,
  .el-tag,
  .tool-info-card li,
  .progress-badge
)) {
  background: transparent !important;
  background-image: none !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: none !important;
  color: #64748b !important;
  padding: 0 !important;
}

.settings-bubble :deep(:is(.active, .is-active, .is-ready) :is(
  .meta-pill,
  .badge,
  .tag,
  .status-pill,
  .config-badge,
  .hint-chip,
  .el-tag
)) {
  color: #b45309 !important;
}

.settings-bubble :deep(:is(
  .el-input__wrapper.el-input__wrapper,
  .el-select__wrapper.el-select__wrapper,
  .el-textarea__inner.el-textarea__inner,
  .mcp-line-input,
  .mcp-line-value,
  .field-input,
  .config-input,
  input:not(.el-input__inner):not([type='checkbox']):not([type='radio']):not([type='file']):not([type='range']),
  textarea:not(.el-textarea__inner)
)) {
  background: transparent !important;
  background-image: none !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: inset 0 -1px 0 rgba(148, 163, 184, 0.32) !important;
}

.settings-bubble :deep(:is(
  .el-input.is-focus .el-input__wrapper.el-input__wrapper,
  .el-input__wrapper.el-input__wrapper:focus-within,
  .el-select__wrapper.el-select__wrapper.is-focused,
  .el-select__wrapper.el-select__wrapper:focus-within,
  .el-textarea__inner.el-textarea__inner:focus,
  .mcp-line-input:focus,
  .field-input:focus,
  .config-input:focus,
  input:not(.el-input__inner):focus,
  textarea:not(.el-textarea__inner):focus
)) {
  background: transparent !important;
  background-image: none !important;
  box-shadow: inset 0 -2px 0 rgba(245, 158, 11, 0.72) !important;
}

.settings-bubble :deep(:is(.el-input__inner, .el-select__placeholder, .el-select__selected-item, .el-textarea__inner)) {
  background: transparent !important;
}

.settings-bubble :deep(:is(.el-input__inner, .el-select__placeholder, .el-select__selected-item)) {
  background-image: none !important;
  border: 0 !important;
  box-shadow: none !important;
}

.settings-bubble :deep(:is(.el-radio-button__inner.el-radio-button__inner, .el-checkbox-button__inner.el-checkbox-button__inner)) {
  background: transparent !important;
  background-image: none !important;
  border: 0 !important;
  border-radius: 0 !important;
  box-shadow: inset 0 -1px 0 rgba(148, 163, 184, 0.24) !important;
}

.settings-bubble :deep(:is(
  .el-radio-button.is-active .el-radio-button__inner.el-radio-button__inner,
  .el-checkbox-button.is-checked .el-checkbox-button__inner.el-checkbox-button__inner,
  .el-radio-button__original-radio:checked + .el-radio-button__inner.el-radio-button__inner,
  .el-checkbox-button__original:checked + .el-checkbox-button__inner.el-checkbox-button__inner
)) {
  background: transparent !important;
  background-image: none !important;
  color: #b45309 !important;
  box-shadow: inset 0 -2px 0 rgba(245, 158, 11, 0.72) !important;
}

.progress-step.active {
  background: transparent !important;
}

/* Stability pass: one visual line per control, no header divider doubling, no panel bounce. */
.conversation-panel {
  scroll-behavior: smooth;
  overscroll-behavior: contain;
}

.settings-bubble :deep(:is(.agent-hero, .page-header, .page-hero, .hero-card)) {
  border-bottom: 0 !important;
}

.settings-bubble :deep(:is(.model-form-panel, .knowledge-form-panel, .tool-workbench-card, .mcp-workbench-panel, .inline-panel.create-panel)) {
  border-bottom: 0 !important;
  animation: none !important;
}

.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input__wrapper) {
  box-shadow: none !important;
}

.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input__inner) {
  box-shadow: inset 0 -1px 0 rgba(148, 163, 184, 0.28) !important;
}

.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input.is-focus .el-input__inner),
.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input__wrapper:focus-within .el-input__inner) {
  box-shadow: inset 0 -2px 0 rgba(245, 158, 11, 0.68) !important;
}

/* Divider diet: the ink-line controls already provide structure, so remove
   the extra panel rules that visually read as doubled input lines. */
.settings-bubble.settings-bubble :deep(:is(
  .agent-hero,
  .page-header,
  .page-hero,
  .hero-card,
  .content-card,
  .toolbar-card,
  .table-card,
  .list-card,
  .editor-card,
  .side-card,
  .form-card,
  .summary-card,
  .config-panel,
  .config-card,
  .preview-card,
  .source-intro,
  .nested-panel,
  .advanced-block,
  .inline-form-head,
  .inline-panel-head,
  .workbench-head,
  .panel-head
)) {
  border-top: 0 !important;
  border-bottom: 0 !important;
  box-shadow: none !important;
}

.settings-bubble.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
)) {
  border: 0 !important;
  border-radius: 0 !important;
  margin-top: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble.settings-bubble :deep(:is(
  .el-tabs__nav-wrap::after,
  .el-divider,
  .divider,
  .section-divider,
  hr
)) {
  display: none !important;
}

.settings-bubble.settings-bubble :deep(:is(.settings-search-row, .search-row, .filter-row, .toolbar-card)) {
  border: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input__wrapper.el-input__wrapper) {
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.32) 12%, rgba(148, 163, 184, 0.46) 70%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 255, 255, 0.28), rgba(255, 255, 255, 0.06)) !important;
  box-shadow: none !important;
}

.settings-bubble.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input__inner) {
  background: transparent !important;
  background-image: none !important;
  box-shadow: none !important;
}

.settings-bubble.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input.is-focus .el-input__wrapper.el-input__wrapper),
.settings-bubble.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input__wrapper.el-input__wrapper:focus-within) {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.82) 16%, rgba(217, 119, 6, 0.9) 58%, rgba(245, 158, 11, 0)) left bottom / 100% 2px no-repeat,
    radial-gradient(80% 120% at 48% 100%, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0) 60%),
    linear-gradient(180deg, rgba(255, 251, 247, 0.4), rgba(255, 255, 255, 0.08)) !important;
  box-shadow: none !important;
}

/* Action icon rhythm: create/close/save share one optical size. */
.settings-bubble.settings-bubble :deep(.settings-icon-button.el-button),
.settings-bubble.settings-bubble :deep(.settings-icon-button.el-button.is-circle),
.settings-bubble.settings-bubble :deep(.settings-icon-button.save-action.el-button),
.settings-bubble.settings-bubble :deep(.skill-icon-button.el-button--primary.is-circle) {
  width: 32px !important;
  min-width: 32px !important;
  height: 32px !important;
  min-height: 32px !important;
  padding: 0 !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  line-height: 1 !important;
}

.settings-bubble.settings-bubble :deep(.settings-icon-button.el-button .el-icon),
.settings-bubble.settings-bubble :deep(.settings-icon-button.save-action.el-button .el-icon),
.settings-bubble.settings-bubble :deep(.skill-icon-button.el-button--primary.is-circle .el-icon) {
  width: 15px !important;
  height: 15px !important;
  margin: 0 !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  font-size: 15px !important;
  line-height: 1 !important;
}

.settings-bubble.settings-bubble :deep(.settings-icon-button.el-button .el-icon svg),
.settings-bubble.settings-bubble :deep(.settings-icon-button.save-action.el-button .el-icon svg),
.settings-bubble.settings-bubble :deep(.skill-icon-button.el-button--primary.is-circle .el-icon svg) {
  width: 15px !important;
  height: 15px !important;
}

.settings-bubble.settings-bubble :deep(.skill-icon-button.el-button--primary.is-circle) {
  border-color: #f59e0b !important;
  background: #f59e0b !important;
  color: #ffffff !important;
  box-shadow: 0 12px 26px -18px rgba(180, 83, 9, 0.74) !important;
}

.settings-bubble.settings-bubble :deep(:is(
  .agent-inline-editor,
  .model-form-panel,
  .knowledge-form-panel,
  .tool-workbench-card,
  .mcp-workbench-panel,
  .inline-panel.create-panel
) :is(.el-form-item, .field, .inline-row, .repeat-stack, .repeat-field, .config-row, .form-row)) {
  border-top: 0 !important;
  border-bottom: 0 !important;
}

/* Focus should not draw a loud orange rule across settings surfaces. */
.settings-bubble.settings-bubble :deep(:is(
  .el-input.is-focus .el-input__wrapper.el-input__wrapper,
  .el-input__wrapper.el-input__wrapper:focus-within,
  .el-select__wrapper.el-select__wrapper.is-focused,
  .el-select__wrapper.el-select__wrapper:focus-within,
  .el-textarea__inner.el-textarea__inner:focus,
  .field-input:focus,
  .config-input:focus,
  input:not(.el-input__inner):focus,
  textarea:not(.el-textarea__inner):focus
)) {
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.3) 12%, rgba(148, 163, 184, 0.42) 70%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 255, 255, 0.32), rgba(255, 255, 255, 0.08)) !important;
  box-shadow: none !important;
}

.settings-bubble.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input.is-focus .el-input__wrapper.el-input__wrapper),
.settings-bubble.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input__wrapper.el-input__wrapper:focus-within) {
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.3) 12%, rgba(148, 163, 184, 0.42) 70%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 255, 255, 0.28), rgba(255, 255, 255, 0.06)) !important;
  box-shadow: none !important;
}

.settings-bubble.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input.is-focus .el-input__inner),
.settings-bubble.settings-bubble :deep(:is(.settings-search-row, .toolbar-card) .el-input__wrapper.el-input__wrapper:focus-within .el-input__inner),
.settings-bubble.settings-bubble :deep(:is(.el-input__inner, .el-select__selected-item, .el-select__placeholder)) {
  box-shadow: none !important;
}

/* Account profile should read like content inside the chat bubble, not a card pasted in. */
.settings-bubble.settings-bubble :deep(:is(
  .profile-page,
  .profile-content,
  .profile-panel,
  .profile-page .description-section,
  .profile-page .description-preview,
  .profile-page .description-edit,
  .profile-page .dialog-body,
  .profile-page .selected-section,
  .profile-page .avatar-grid-section,
  .profile-page .upload-section
)) {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

.settings-bubble.settings-bubble :deep(.profile-avatar-dialog.el-dialog) {
  border-color: rgba(226, 232, 240, 0.36) !important;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.36), rgba(255, 255, 255, 0.14)) !important;
  box-shadow: none !important;
}

.settings-bubble.settings-bubble :deep(.profile-avatar-dialog .el-dialog__header),
.settings-bubble.settings-bubble :deep(.profile-avatar-dialog .el-dialog__body),
.settings-bubble.settings-bubble :deep(.profile-avatar-dialog .el-dialog__footer) {
  background: transparent !important;
  border-color: rgba(226, 232, 240, 0.36) !important;
}

/* Final avatar selector pass: no card tiles, no cached white backplates. */
.settings-bubble.settings-bubble :deep(.profile-page :is(.avatar-grid, .avatar-option, .avatar-option img, .selected-avatar, .selected-avatar img)) {
  background: transparent !important;
  border: 0 !important;
  box-shadow: none !important;
}

.settings-bubble.settings-bubble :deep(.profile-page .avatar-option) {
  display: grid !important;
  place-items: center !important;
  min-height: 68px !important;
  border-radius: 0 !important;
  overflow: visible !important;
}

.settings-bubble.settings-bubble :deep(.profile-page .avatar-option img) {
  width: min(68px, 100%) !important;
  height: auto !important;
  aspect-ratio: 1 !important;
  object-fit: contain !important;
  border-radius: 0 !important;
}

.settings-bubble.settings-bubble :deep(.profile-avatar-dialog .el-dialog__footer) {
  display: none !important;
  padding: 0 !important;
  border: 0 !important;
}

/* Agent editor avatar row: current avatar on the left, presets on the right. */
.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .agent-config-grid) {
  grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
  gap: 8px 12px !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .agent-logo-field) {
  grid-column: 1 / -1 !important;
  grid-row: auto !important;
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: flex-start !important;
  gap: 12px !important;
  margin: 2px 0 4px !important;
  min-width: 0 !important;
  width: 100% !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .logo-panel) {
  display: flex !important;
  flex-direction: row !important;
  align-items: center !important;
  justify-content: flex-start !important;
  gap: 12px !important;
  min-width: 0 !important;
  width: 100% !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .logo-current) {
  display: grid !important;
  justify-items: center !important;
  gap: 5px !important;
  flex: 0 0 76px !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .logo-preview) {
  width: 58px !important;
  height: 58px !important;
  min-width: 58px !important;
  min-height: 58px !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
  overflow: visible !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .logo-preview img) {
  width: 100% !important;
  height: 100% !important;
  object-fit: contain !important;
  border-radius: 0 !important;
  background: transparent !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .logo-upload-button) {
  width: 28px !important;
  height: 28px !important;
  min-width: 28px !important;
  min-height: 28px !important;
  padding: 0 !important;
  border: 0 !important;
  border-radius: 999px !important;
  background: transparent !important;
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.2) !important;
  color: #64748b !important;
  font-size: 10.5px !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .logo-upload-button span) {
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0, 0, 0, 0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .logo-presets) {
  min-width: 0 !important;
  flex: 1 1 auto !important;
  display: grid !important;
  gap: 6px !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .logo-presets-head) {
  color: #64748b !important;
  font-size: 11px !important;
  font-weight: 620 !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .preset-avatar-strip) {
  width: 100% !important;
  max-height: none !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 2px 2px 7px !important;
  overflow-x: auto !important;
  overflow-y: hidden !important;
  scrollbar-width: thin !important;
  scrollbar-color: rgba(148, 163, 184, 0.24) transparent !important;
  scroll-snap-type: x proximity !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .preset-avatar-button) {
  flex: 0 0 34px !important;
  width: 34px !important;
  height: 34px !important;
  border: 0 !important;
  border-radius: 0 !important;
  background: transparent !important;
  box-shadow: none !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .preset-avatar-button img) {
  width: 100% !important;
  height: 100% !important;
  object-fit: contain !important;
  border-radius: 0 !important;
  background: transparent !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .agent-memory-field) {
  grid-column: 4 !important;
  justify-self: end !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-name) {
  grid-column: 1 / span 2 !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-description) {
  grid-column: 3 / span 2 !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-model),
.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-tool),
.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-knowledge) {
  grid-column: 1 / span 2 !important;
}

.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-prompt),
.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-mcp),
.settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .field-skill) {
  grid-column: 3 / span 2 !important;
}

@media (max-width: 900px) {
  .settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .agent-config-grid),
  .settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .agent-logo-field),
  .settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor .logo-panel) {
    grid-template-columns: minmax(0, 1fr) !important;
    flex-wrap: wrap !important;
  }

  .settings-bubble.settings-bubble :deep(.agent-editor-page.agent-inline-editor :is(
    .agent-logo-field,
    .agent-memory-field,
    .field-name,
    .field-description,
    .field-model,
    .field-prompt,
    .field-tool,
    .field-mcp,
    .field-knowledge,
    .field-skill
  )) {
    grid-column: 1 !important;
  }
}

/* Paint guard: Chrome occasionally composites translucent setting bubbles above
   their children while the conversation is scrolling. Keep each turn isolated
   and draw the glass surface on a behind-the-content pseudo layer. */
.settings-thread-block,
.settings-panel-row,
.settings-message-stack,
.settings-bubble-shell,
.settings-bubble {
  isolation: isolate;
}

.settings-bubble-shell.is-ready,
.settings-bubble {
  backface-visibility: hidden;
  transform: translateZ(0);
}

.settings-bubble.settings-bubble {
  background: transparent !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.settings-bubble.settings-bubble::before {
  content: '';
  position: absolute;
  inset: 0;
  z-index: -1;
  border-radius: inherit;
  pointer-events: none;
  background:
    radial-gradient(circle at 88% 0%, rgba(245, 158, 11, 0.05), transparent 28%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.9)),
    #fffdfa;
  box-shadow:
    0 24px 68px -42px rgba(15, 23, 42, 0.28),
    inset 0 1px 0 rgba(255, 255, 255, 0.96);
}

.settings-bubble.settings-bubble :deep(.el-loading-mask) {
  background: rgba(255, 253, 250, 0.62) !important;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

/* Chat text legibility pass: keep the quiet layout, but give conversation
   content a little more ink so it reads less fragile on the glass surface. */
.workspace-chat .message-bubble {
  font-weight: 500;
  -webkit-font-smoothing: antialiased;
  text-rendering: geometricPrecision;
}

.workspace-chat .message-row.assistant .message-bubble {
  font-weight: 520;
}

.workspace-chat .message-row.user .message-bubble {
  font-weight: 560;
}

.workspace-chat .message-bubble :deep(.md-editor-preview),
.workspace-chat .message-bubble :deep(.md-editor-preview p),
.workspace-chat .message-bubble :deep(.md-editor-preview li) {
  font-weight: inherit;
}

.workspace-chat .message-bubble :deep(.md-editor-preview :is(p, li, td, blockquote)) {
  font-weight: 520;
}

.workspace-chat .message-bubble :deep(.md-editor-preview :is(strong, b, h1, h2, h3, h4, th)) {
  font-weight: revert;
}

.workspace-chat .message-bubble :deep(pre),
.workspace-chat .message-bubble :deep(code),
.workspace-chat .chat-message-meta,
.workspace-chat .chat-message-meta span {
  font-weight: 400;
}

/* Conversational markdown polish: denser, calmer AI answers without raw document heaviness. */
.workspace-chat .message-row.assistant .message-bubble.has-content {
  padding: 17px 52px 18px 22px;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview) {
  color: #27364a;
  font-size: 14px;
  line-height: 1.74;
  letter-spacing: 0;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview p) {
  margin: 0 0 0.68em;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview p + p) {
  margin-top: 0.28em;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview :is(h1, h2, h3, h4)) {
  margin: 0.86em 0 0.42em;
  color: #101827;
  font-weight: 760;
  line-height: 1.32;
  letter-spacing: 0;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview :is(h1, h2):first-child),
.workspace-chat .zuno-prose :deep(.md-editor-preview :is(h3, h4):first-child) {
  margin-top: 0;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview h1) { font-size: 17px; }
.workspace-chat .zuno-prose :deep(.md-editor-preview h2) { font-size: 16px; }
.workspace-chat .zuno-prose :deep(.md-editor-preview h3) { font-size: 15px; }
.workspace-chat .zuno-prose :deep(.md-editor-preview h4) { font-size: 14px; }

.workspace-chat .zuno-prose :deep(.md-editor-preview :is(ul, ol)) {
  margin: 0.38em 0 0.78em;
  padding-left: 1.25em;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview li) {
  margin: 0.2em 0;
  padding-left: 0.08em;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview li > :is(p, ul, ol):last-child) {
  margin-bottom: 0;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview li::marker) {
  color: #d97706;
  font-weight: 760;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview strong) {
  color: #111827;
  font-weight: 760;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview blockquote) {
  margin: 0.78em 0;
  padding: 0.08em 0 0.08em 0.78em;
  border-left: 2px solid rgba(245, 158, 11, 0.42);
  color: #64748b;
  background: transparent !important;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview table) {
  display: block;
  width: fit-content;
  max-width: 100%;
  overflow-x: auto;
  margin: 0.82em 0 0.92em;
  border-collapse: collapse;
  font-size: 13px;
  line-height: 1.55;
  background: transparent !important;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview :is(thead, tbody, tr)) {
  background: transparent !important;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview tr:nth-child(2n)) {
  background: transparent !important;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview :is(th, td)) {
  padding: 8px 12px;
  border: 0;
  border-bottom: 1px solid rgba(226, 232, 240, 0.86);
  background: transparent !important;
  white-space: nowrap;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview th) {
  color: #101827;
  font-weight: 760;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview td) {
  color: #314158;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview tr:last-child td) {
  border-bottom-color: rgba(226, 232, 240, 0.56);
}

.workspace-chat .zuno-prose :deep(.md-editor-preview code:not(pre code)) {
  padding: 0.06em 0.3em;
  border-radius: 5px;
  background: rgba(255, 247, 237, 0.62);
  color: #a3470a;
  font-size: 0.9em;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview pre) {
  margin: 0.78em 0;
  padding: 11px 13px;
  border-radius: 10px;
  border: 1px solid rgba(226, 232, 240, 0.74);
  background: rgba(248, 250, 252, 0.72) !important;
}

.workspace-chat .user-prose :deep(.md-editor-preview) {
  font-size: 13.5px;
  line-height: 1.62;
  font-weight: 570;
}

/* Round 2: make long AI answers scan like conversation, not pasted documents. */
.workspace-chat .message-row.assistant .message-bubble.has-content {
  max-width: min(880px, calc(100% - 58px));
}

.workspace-chat .zuno-prose :deep(.md-editor-preview) {
  max-width: min(100%, 820px);
  overflow-wrap: anywhere;
  text-wrap: pretty;
}

.workspace-chat .message-row.assistant .message-actions {
  top: 11px;
  right: 11px;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview :is(h1, h2, h3, h4, h5, h6)) {
  border: 0 !important;
  padding: 0 !important;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview h2) {
  margin-top: 1.05em;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview h3) {
  margin-top: 0.95em;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview h2 + p),
.workspace-chat .zuno-prose :deep(.md-editor-preview h3 + p),
.workspace-chat .zuno-prose :deep(.md-editor-preview h4 + p) {
  margin-top: 0;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview :is(ul, ol) :is(ul, ol)) {
  margin-top: 0.16em;
  margin-bottom: 0.24em;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview li + li) {
  margin-top: 0.26em;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview table) {
  max-width: 100%;
  border-spacing: 0;
  scrollbar-gutter: stable;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview table::-webkit-scrollbar) {
  height: 6px;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview table::-webkit-scrollbar-track) {
  background: transparent;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview table::-webkit-scrollbar-thumb) {
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.28);
}

.workspace-chat .zuno-prose :deep(.md-editor-preview :is(th, td)) {
  vertical-align: top;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview tbody tr:hover td) {
  background: rgba(255, 251, 245, 0.46) !important;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview blockquote p) {
  margin-bottom: 0.34em;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview pre) {
  max-height: 420px;
  overflow: auto;
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
  font-size: 12px;
  line-height: 1.58;
  scrollbar-gutter: stable;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview pre::-webkit-scrollbar) {
  width: 7px;
  height: 7px;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview pre::-webkit-scrollbar-track) {
  background: transparent;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview pre::-webkit-scrollbar-thumb) {
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.3);
}

.workspace-chat .zuno-prose :deep(.md-editor-preview :is(hr, .md-editor-catalog-link)) {
  display: none;
}

.workspace-chat .zuno-prose :deep(.md-editor-preview :is(table, pre, code)) {
  font-variant-numeric: tabular-nums;
}

@media (max-width: 760px) {
  .workspace-chat .message-row.assistant .message-bubble.has-content {
    max-width: calc(100% - 46px);
    padding: 14px 42px 15px 17px;
  }

  .workspace-chat .zuno-prose :deep(.md-editor-preview) {
    font-size: 13.2px;
    line-height: 1.68;
  }

  .workspace-chat .zuno-prose :deep(.md-editor-preview :is(th, td)) {
    padding: 7px 10px;
  }
}
</style>
