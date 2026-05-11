<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Connection, CopyDocument, Delete, EditPen, InfoFilled, Plus, Search, Setting, Upload } from '@element-plus/icons-vue'
import ConfigurationPanel from '../configuration/configuration.vue'
import toolArxivIcon from '../../assets/tools/tool-arxiv.svg'
import toolDefaultIcon from '../../assets/tools/tool-default.svg'
import toolDeliveryIcon from '../../assets/tools/tool-delivery.svg'
import toolDocxIcon from '../../assets/tools/tool-convert-pdf-docx.svg'
import toolEmailIcon from '../../assets/tools/tool-email.svg'
import toolPdfIcon from '../../assets/tools/tool-convert-docx-pdf.svg'
import toolWeatherIcon from '../../assets/tools/tool-weather.svg'
import settingsToolIcon from '../../assets/settings-icons/tool.svg'
import emptyDataIcon from '../../assets/dashboard/空数据.svg'
import {
  assistRemoteApiToolAPI,
  createToolAPI,
  deleteToolAPI,
  getDefaultToolLogoAPI,
  getVisibleToolsAPI,
  previewCliToolAPI,
  testSavedToolConnectivityAPI,
  testSystemToolConnectivityAPI,
  testToolConnectivityAPI,
  updateToolAPI,
  uploadFileAPI,
  type CliAssistRequest,
  type CliConfig,
  type CliPreviewCandidate,
  type CliPreviewResult,
  type CliSourceType,
  type CliStructuredSuggestion,
  type RemoteApiAssistRequest,
  type RemoteApiAssistResponse,
  type RemoteApiAuthType,
  type RemoteApiMode,
  type RuntimeType,
  type SimpleApiConfig,
  type SimpleApiParamConfig,
  type ToolConnectivityResponse,
  type ToolResponse,
} from '../../apis/tool'
import { getConfigAPI, getSystemToolConfigAPI, type RuntimeConfigPayload, type SystemToolConfigPayload } from '../../apis/configuration'
import { safeDisplayText } from '../../utils/display-text'
import { useUserStore } from '../../store/user'
import ZunoMiniPager from '../../components/ZunoMiniPager.vue'

interface ToolItem extends ToolResponse {
  system_tool_kind?: RuntimeConfigPayload['system_tools'][number]['tool_kind']
  system_tool_kind_label?: RuntimeConfigPayload['system_tools'][number]['tool_kind_label']
  strategy_code?: RuntimeConfigPayload['system_tools'][number]['strategy_code']
  strategy_label?: string
  strategy_summary?: string
  install_requirement?: RuntimeConfigPayload['system_tools'][number]['install_requirement']
  config_requirement?: RuntimeConfigPayload['system_tools'][number]['config_requirement']
  has_fields?: boolean
  system_status?: RuntimeConfigPayload['system_tools'][number]['status']
  runtime_status?: ToolConnectivityResponse['status']
}

type SystemToolKind = NonNullable<SystemToolConfigPayload['tool_kind']>
type GuideTone = 'strategy' | 'install' | 'config'
interface ToolInfoCard {
  key: string
  eyebrow: string
  title: string
  summary: string
  items: string[]
  tone?: GuideTone | 'status'
}

interface ToolFormState {
  tool_id?: string
  display_name: string
  description: string
  logo_url: string
  runtime_type: RuntimeType
  remote_api_mode: RemoteApiMode
  openapi_schema: string
  auth_type: RemoteApiAuthType
  auth_key_name: string
  auth_token: string
  simple_api_config: SimpleApiConfig
  cli_config: CliConfig
}

interface CliAssistState {
  github_url: string
  docs_url: string
  local_path: string
  notes: string
}

interface RemoteApiAssistState {
  endpoint_url: string
  docs_urls_text: string
  sample_curl: string
  probe_args: Record<string, any>
}

interface AssistCard {
  id: string
  title: string
  summary: string
  confidence?: number
  notes: string[]
  warnings: string[]
  references: string[]
  payload: Partial<CliStructuredSuggestion>
}

const userStore = useUserStore()
type ToolWorkbenchMode = 'list' | 'create' | 'edit' | 'config'
const loading = ref(false)
const statusRefreshing = ref<Record<string, boolean>>({})
const keyword = ref('')
const activeTab = ref<'all' | 'custom'>('all')
const tools = ref<ToolItem[]>([])
const LIST_PAGE_SIZE = 6
const listPage = ref(1)
const workbenchMode = ref<ToolWorkbenchMode>('list')
const selectedTool = ref<ToolItem | null>(null)
const configPanelRef = ref<InstanceType<typeof ConfigurationPanel> | null>(null)
const expandedToolInfoId = ref('')
const expandedConfigToolId = ref('')
const toolInfoLoading = ref<Record<string, boolean>>({})
const toolDetailCache = ref<Record<string, SystemToolConfigPayload>>({})
const dialogVisible = ref(false)
const dialogLoading = ref(false)
const isEditMode = ref(false)
const logoUploading = ref(false)
const remoteApiAssistLoading = ref(false)
const remoteApiAssistError = ref('')
const remoteApiAssistResult = ref<RemoteApiAssistResponse | null>(null)
const toolConnectivityLoading = ref(false)
const toolConnectivityError = ref('')
const toolConnectivityResult = ref<ToolConnectivityResponse | null>(null)
const cliPreviewLoading = ref(false)
const cliPreviewError = ref('')
const cliPreviewResult = ref<CliPreviewResult | null>(null)
const advancedSections = ref<string[]>([])
const apiAdvancedSections = ref<string[]>([])

const isToolFormMode = computed(() => workbenchMode.value === 'create' || workbenchMode.value === 'edit')
const workbenchTitle = computed(() => {
  if (workbenchMode.value === 'create') return '新建工具'
  if (workbenchMode.value === 'edit') return '编辑工具'
  return '工具'
})
const createDefaultOpenApiSchema = () => JSON.stringify({ openapi: '3.1.0', info: { title: 'Untitled API', version: '1.0.0' }, servers: [{ url: '' }], paths: {} }, null, 2)
const createDefaultCliConfig = (): CliConfig => ({ source_type: 'local_directory', tool_dir: '', command: '', args_template: '', cwd_mode: 'tool_dir', cwd: '', timeout_ms: 30000, install_command: '', install_source: '', install_notes: '', healthcheck_command: '', credential_mode: 'none' })
const createDefaultSimpleApiConfig = (): SimpleApiConfig => ({ base_url: '', path: '/', method: 'GET', operation_id: '', summary: '', description: '', params: [], body_schema: null, response_schema: null })

const assistForm = ref<CliAssistState>({ github_url: '', docs_url: '', local_path: '', notes: '' })
const remoteApiAssistForm = ref<RemoteApiAssistState>({ endpoint_url: '', docs_urls_text: '', sample_curl: '', probe_args: {} })
const form = ref<ToolFormState>({ display_name: '', description: '', logo_url: '', runtime_type: 'remote_api', remote_api_mode: 'simple', openapi_schema: createDefaultOpenApiSchema(), auth_type: '', auth_key_name: '', auth_token: '', simple_api_config: createDefaultSimpleApiConfig(), cli_config: createDefaultCliConfig() })

const cliSourceOptions: Array<{ value: CliSourceType; label: string; helper: string }> = [
  { value: 'local_directory', label: '本地目录', helper: '适合自己维护的 CLI 项目目录，Agent 可结合 README 和入口文件补全安装建议。' },
  { value: 'executable', label: '可执行文件', helper: '适合已经可以直接运行的 exe、cmd、bat、ps1 等命令入口。' },
  { value: 'npm_package', label: 'npm/pnpm 包', helper: '适合 Node CLI，重点是包名、安装方式和推荐启动命令。' },
  { value: 'python_package', label: 'pip/uv 包', helper: '适合 Python CLI，重点是包名、模块入口和 healthcheck。' },
  { value: 'github_repo', label: 'GitHub 仓库', helper: '适合需要 clone 或按文档安装的开源 CLI，支持同时提供仓库和本地路径。' },
]

const currentCliSourceOption = computed(() => cliSourceOptions.find((item) => item.value === currentSourceType.value) || cliSourceOptions[0])
const isAdmin = computed(() => String(userStore.userInfo?.id || '') === '1')
const currentSourceType = computed(() => form.value.cli_config.source_type || 'local_directory')
const requiresToolDir = computed(() => ['local_directory', 'github_repo'].includes(currentSourceType.value))
const simpleApiParams = computed(() => form.value.simple_api_config.params || [])
const requiredSimpleApiParams = computed(() => simpleApiParams.value.filter((item) => item.required && item.name?.trim()))
const requiredSimpleApiParamNames = computed(() => requiredSimpleApiParams.value.map((item) => item.name.trim()).join('、'))
const remoteApiProbeArgs = computed(() => remoteApiAssistForm.value.probe_args || {})
const probeArgNames = computed(() => Object.keys(remoteApiProbeArgs.value).filter(Boolean).join('、'))
const missingProbeParamNames = computed(() => requiredSimpleApiParams.value.filter((item) => !(item.name in remoteApiProbeArgs.value)).map((item) => item.name.trim()).join('、'))
const needsAuthKeyName = computed(() => ['api_key_query', 'api_key_header'].includes(form.value.auth_type))
const remoteApiAssistSummary = computed(() => remoteApiAssistResult.value?.description || remoteApiAssistResult.value?.display_name || '')
const previewCandidates = computed(() => cliPreviewResult.value?.candidates || cliPreviewResult.value?.command_candidates || [])
const previewRecommended = computed(() => cliPreviewResult.value?.recommended || previewCandidates.value[0] || null)
const detectedFiles = computed(() => (cliPreviewResult.value?.detected_files || []).slice(0, 8))
const previewSummary = computed(() => cliPreviewResult.value?.assist_summary || cliPreviewResult.value?.readme_summary || cliPreviewResult.value?.description || cliPreviewResult.value?.default_description || '')

const previewStructuredCards = computed<AssistCard[]>(() => {
  const result = cliPreviewResult.value
  if (!result) return []
  return [result.structured_suggestions, result.suggestions, result.assist_suggestions, result.plans]
    .flatMap((items) => items || [])
    .filter(Boolean)
    .map((item, index) => ({
      id: item.id || `assist-${index}`,
      title: item.title || item.label || item.tool_name || `建议 ${index + 1}`,
      summary: item.summary || item.description || item.reason || '后端返回了一条结构化建议。',
      confidence: item.confidence,
      notes: item.notes || [],
      warnings: item.warnings || [],
      references: item.references || item.detected_files || [],
      payload: item,
    }))
})

const visibleTools = computed(() => {
  const source = activeTab.value === 'custom' ? tools.value.filter((item) => item.user_id !== '0') : tools.value
  const search = keyword.value.trim().toLowerCase()
  const filtered = search ? source.filter((item) => [item.display_name, item.description || '', item.name, item.runtime_type || ''].join(' ').toLowerCase().includes(search)) : source
  return [...filtered].sort((a, b) => {
    const officialDiff = Number(a.user_id === '0') === Number(b.user_id === '0') ? 0 : a.user_id === '0' ? -1 : 1
    if (officialDiff !== 0) return officialDiff
    return a.display_name.localeCompare(b.display_name, 'zh-CN')
  })
})
const paginatedTools = computed(() => visibleTools.value.slice(
  (listPage.value - 1) * LIST_PAGE_SIZE,
  listPage.value * LIST_PAGE_SIZE,
))

const statusToneMap: Record<string, string> = { ready: 'is-ready', needs_config: 'is-warning', runtime_input: 'is-neutral', missing_dependency: 'is-danger' }
const getResolvedStatus = (tool: ToolItem) => tool.runtime_status || tool.system_status || null
const isSystemTool = (tool: ToolItem) => tool.user_id === '0'
const getToolRuntimeLabel = (tool: ToolItem) => (isSystemTool(tool) ? (tool.system_tool_kind === 'remote_api' ? 'API' : 'CLI') : tool.runtime_type === 'cli' ? 'CLI' : 'API')
const getToolStatusLabel = (tool: ToolItem) => getResolvedStatus(tool)?.label || '待检测'
const getToolStatusTone = (tool: ToolItem) => statusToneMap[getResolvedStatus(tool)?.code || ''] || 'is-neutral'
const getToolSummary = (tool: ToolItem) => safeDisplayText(tool.description) || (isSystemTool(tool) ? (getToolRuntimeLabel(tool) === 'API' ? '通过远程接口提供能力。' : '通过本地命令、内置程序或系统依赖运行。') : '暂无说明')
const getToolHints = (tool: ToolItem) => (isSystemTool(tool) ? tool.system_tool_kind === 'smtp_protocol' ? ['多凭证'] : tool.system_tool_kind === 'remote_api' ? ['远程配置'] : ['本地运行'] : [])
const canConfigureSystemTool = (tool: ToolItem) => {
  if (!isSystemTool(tool)) return false
  const status = getResolvedStatus(tool)
  return Boolean(status?.configurable || tool.has_fields)
}
const canOpenPrimaryAction = (tool: ToolItem) => !isSystemTool(tool) || canConfigureSystemTool(tool)
const isEditingTool = (tool: ToolItem) => workbenchMode.value === 'edit' && selectedTool.value?.tool_id === tool.tool_id
const getPrimaryActionLabel = (tool: ToolItem) => (!isSystemTool(tool) ? (isEditingTool(tool) ? '保存并收起' : '编辑') : '配置')
const getPrimaryActionIcon = (tool: ToolItem) => (!isSystemTool(tool) ? (isEditingTool(tool) ? Check : EditPen) : Setting)
const isToolConfigExpanded = (tool: ToolItem) => expandedConfigToolId.value === tool.tool_id
const isToolInfoExpanded = (tool: ToolItem) => expandedToolInfoId.value === tool.tool_id
const defaultToolInfoByKind: Record<SystemToolKind, Record<GuideTone, Omit<ToolInfoCard, 'key' | 'eyebrow' | 'tone'>>> = {
  remote_api: {
    strategy: {
      title: '固定凭据，运行时直接复用',
      summary: '这类工具靠预置 API 参数工作，配置完成后 Agent 调用时不需要再重复输入固定认证信息。',
      items: ['优先在这里保存长期稳定的 Key、Endpoint 或鉴权字段。'],
    },
    install: {
      title: '先准备服务商凭据',
      summary: '前端这里只负责保存参数，不会帮你申请或校验第三方服务账号。',
      items: ['先到对应服务商控制台拿到 Key 或接口地址，再回来保存。'],
    },
    config: {
      title: '把固定参数填在配置区',
      summary: '配置区只放持久化参数，运行时变化的查询词、城市、单号等内容不在这里填写。',
      items: [],
    },
  },
  public_data_source: {
    strategy: {
      title: '公开数据源优先',
      summary: '这类工具直接读取开放数据，不依赖远程私有 API，也不要求单独安装本机 CLI。',
      items: ['重点是运行时输入合适的查询条件，而不是在这里维护凭据。'],
    },
    install: {
      title: '通常不需要额外安装',
      summary: '如果状态正常，就代表前端没有需要你补的全局依赖或密钥。',
      items: ['除非后续工具实现变化，否则这里一般不需要额外准备。'],
    },
    config: {
      title: '没有持久化配置项',
      summary: '这类工具通常开箱可用，配置页更多是给你确认当前策略，而不是保存参数。',
      items: [],
    },
  },
  smtp_protocol: {
    strategy: {
      title: '把发件能力做成可复用资产',
      summary: 'SMTP 工具的核心不是一次性填参数，而是维护好长期可复用的发件槽位。',
      items: ['Agent 运行时优先引用槽位名，这样更稳定，也更适合多人协作。'],
    },
    install: {
      title: '依赖邮箱服务商的 SMTP 能力',
      summary: '是否可用取决于你的邮箱服务商是否开放 SMTP 以及授权码是否正确。',
      items: ['如果供应商限制 SMTP 或授权码无效，前端保存成功也无法真正发送。'],
    },
    config: {
      title: '配置区维护邮箱槽位',
      summary: '这里保存的是长期可复用的邮箱身份，不是一次性的收件信息。',
      items: [],
    },
  },
  local_dependency: {
    strategy: {
      title: '走本机依赖，不走远程接口',
      summary: '这类工具真正依赖的是运行环境里的可执行程序或 Python 包，因此前端没有太多可存字段。',
      items: ['状态是否可用主要由后端对本机依赖的检测结果决定。'],
    },
    install: {
      title: '先保证运行环境具备依赖',
      summary: '如果页面显示缺依赖，优先处理安装和 PATH，而不是反复刷新这个页面。',
      items: ['确认依赖装在运行 Zuno backend 的环境里，而不是只装在当前开发机的任意地方。'],
    },
    config: {
      title: '配置区通常为空',
      summary: '这类工具一般没有单独的持久化表单，能否使用主要取决于本机环境是否准备好。',
      items: [],
    },
  },
}

const toolInfoOverrides: Record<string, Partial<Record<GuideTone, Partial<Omit<ToolInfoCard, 'key' | 'eyebrow' | 'tone'>>>>> = {
  send_email: {
    strategy: { title: '把邮箱做成稳定槽位', summary: '这个工具适合先把常用发件身份预置好，运行时只引用槽位名，不再重复填写 SMTP 参数。', items: ['建议按业务身份拆槽位，例如 qq-main、support-mail、office-backup。'] },
    install: { title: '先准备授权码再保存', summary: 'QQ、163、Gmail、Outlook 都能直接套预设 SMTP 参数，自定义服务商再改主机和端口。', items: ['每个槽位都需要发件邮箱和授权码，尽量不要直接使用登录密码。'] },
    config: { title: '配置区保存邮箱槽位', summary: '至少保存一个可用槽位后，发送邮件工具才能稳定复用发件身份。', items: ['如果团队有多个发件身份，可以在这里长期维护多组槽位。'] },
  },
  get_arxiv: {
    strategy: {
      title: '直接使用公开论文源',
      summary: '这个工具走公开数据源，不需要额外密钥或本机依赖。',
      items: ['重点是运行时给出明确主题、作者或关键词，而不是在这里做预配置。'],
    },
  },
  convert_to_pdf: {
    install: {
      title: '运行机器需要 LibreOffice',
      summary: 'Docx 转 PDF 依赖本机文档转换能力，真正决定是否可用的是运行 Zuno 的那台机器。',
      items: ['安装 LibreOffice 后，确保后端进程能找到 libreoffice 或 soffice 命令。'],
    },
  },
  convert_to_docx: {
    install: {
      title: '运行机器需要 pdf2docx',
      summary: 'PDF 转 Docx 依赖 Python 包而不是远程接口，所以前端没有额外密钥可以填写。',
      items: ['如果状态仍显示缺依赖，请在后端运行环境安装 pdf2docx。'],
    },
  },
}

const loadToolDetail = async (tool: ToolItem) => {
  if (!isSystemTool(tool) || toolDetailCache.value[tool.name] || toolInfoLoading.value[tool.tool_id]) return
  toolInfoLoading.value[tool.tool_id] = true
  try {
    const response = await getSystemToolConfigAPI(tool.name)
    toolDetailCache.value = { ...toolDetailCache.value, [tool.name]: response.data.data }
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '加载工具说明失败')
  } finally {
    toolInfoLoading.value[tool.tool_id] = false
  }
}

const toggleToolInfo = async (tool: ToolItem) => {
  if (expandedToolInfoId.value === tool.tool_id) {
    expandedToolInfoId.value = ''
    return
  }
  expandedConfigToolId.value = ''
  expandedToolInfoId.value = tool.tool_id
  await loadToolDetail(tool)
}

const getToolDetail = (tool: ToolItem) => toolDetailCache.value[tool.name] || null
const getSystemToolKind = (tool: ToolItem): SystemToolKind => getToolDetail(tool)?.tool_kind || tool.system_tool_kind || 'remote_api'
const getToolInfoCards = (tool: ToolItem): ToolInfoCard[] => {
  if (!isSystemTool(tool)) {
    const lines = [getToolSummary(tool), `自定义工具 · ${getToolRuntimeLabel(tool)}`]
    const metadata = tool.source_metadata || {}
    if (metadata.docs_url) lines.push(`文档：${metadata.docs_url}`)
    if (metadata.endpoint_url) lines.push(`接口：${metadata.endpoint_url}`)
    if (tool.runtime_type === 'cli' && tool.auth_config?.cli_config?.command) lines.push(`启动命令：${tool.auth_config.cli_config.command}`)
    return [{
      key: `${tool.tool_id}-custom`,
      eyebrow: '工具信息',
      title: tool.display_name,
      summary: getToolSummary(tool),
      items: Array.from(new Set(lines.filter(Boolean))),
      tone: 'status',
    }]
  }

  const detail = getToolDetail(tool)
  const kind = getSystemToolKind(tool)
  const defaults = defaultToolInfoByKind[kind]
  const overrides = toolInfoOverrides[tool.name] || {}
  const status = getResolvedStatus(tool) || detail?.status || null
  const strategySummary = detail?.strategy?.summary || detail?.strategy_summary || tool.strategy_summary
  const installRequirement = detail?.strategy?.install_requirement || detail?.install_requirement || tool.install_requirement
  const configRequirement = detail?.strategy?.config_requirement || detail?.config_requirement || tool.config_requirement
  const fieldLabels = (detail?.fields || []).map((field) => `${field.label}${field.required ? '（必填）' : ''}`)
  const accountCount = detail?.accounts?.length || 0
  const note = detail?.note?.trim()

  const cards: ToolInfoCard[] = [
    {
      key: `${tool.tool_id}-status`,
      eyebrow: '当前状态',
      title: status?.label || '待检测',
      summary: status?.detail || `${tool.system_tool_kind_label || getToolRuntimeLabel(tool)} · ${getToolRuntimeLabel(tool)}`,
      items: [
        strategySummary ? `接入策略：${strategySummary}` : '',
        tool.has_fields || fieldLabels.length ? `配置字段：${fieldLabels.length ? fieldLabels.join('、') : '需要固定配置项'}` : '',
        accountCount ? `已配置邮箱槽位：${accountCount} 个` : '',
      ].filter(Boolean),
      tone: 'status',
    },
  ]

  for (const tone of ['strategy', 'install', 'config'] as GuideTone[]) {
    const base = defaults[tone]
    const override = overrides[tone]
    const dynamic = tone === 'install' ? installRequirement : tone === 'config' ? configRequirement : null
    cards.push({
      key: `${tool.tool_id}-${tone}`,
      eyebrow: tone === 'strategy' ? '使用策略' : tone === 'install' ? '安装依赖' : '配置范围',
      title: override?.title || dynamic?.label || base.title,
      summary: dynamic?.detail || override?.summary || base.summary,
      items: Array.from(new Set([
        ...(override?.items || base.items || []),
        tone === 'config' && fieldLabels.length ? `可填写：${fieldLabels.join('、')}` : '',
        tone === 'config' && note ? note : '',
      ].filter(Boolean))),
      tone,
    })
  }

  return cards
}
const isStatusRefreshing = (tool: ToolItem) => !!statusRefreshing.value[tool.tool_id]
const systemToolIconMap: Record<string, string> = {
  send_email: toolEmailIcon,
  get_weather: toolWeatherIcon,
  get_delivery: toolDeliveryIcon,
  get_arxiv: toolArxivIcon,
  convert_to_pdf: toolPdfIcon,
  convert_to_docx: toolDocxIcon,
}
const isRemoteDefaultToolLogo = (value: string) => value.includes('agentchat.oss-cn-beijing.aliyuncs.com/icons/tools/default.png')
const getToolLogo = (tool: ToolItem) => {
  if (isSystemTool(tool)) return systemToolIconMap[tool.name] || toolDefaultIcon
  const logoUrl = String(tool.logo_url || '').trim()
  return logoUrl && !isRemoteDefaultToolLogo(logoUrl) ? logoUrl : toolDefaultIcon
}
const handleToolLogoError = (event: Event) => {
  const target = event.target as HTMLImageElement | null
  if (!target || target.dataset.fallbackApplied === 'true') return
  target.dataset.fallbackApplied = 'true'
  target.src = toolDefaultIcon
}

const cliPathLabel = computed(() => currentSourceType.value === 'github_repo' ? '本地仓库目录' : currentSourceType.value === 'npm_package' ? '可选本地目录' : currentSourceType.value === 'python_package' ? '可选工具目录' : '工具目录')
const cliPathPlaceholder = computed(() => currentSourceType.value === 'github_repo' ? '例如：tools/cli/my-github-cli' : currentSourceType.value === 'npm_package' ? '例如：tools/cli/playwright-cli（可选）' : currentSourceType.value === 'python_package' ? '例如：tools/cli/obsidian-cli（可选）' : '例如：tools/cli/my-cli')
const commandPlaceholder = computed(() => currentSourceType.value === 'executable' ? '例如：F:\\tools\\mycli\\mycli.exe' : currentSourceType.value === 'npm_package' ? '例如：npx @scope/my-cli' : currentSourceType.value === 'python_package' ? '例如：uvx my-cli 或 python -m my_cli' : '例如：python main.py 或 ./bin/cli')
const installSourceLabel = computed(() => currentSourceType.value === 'github_repo' ? 'GitHub 仓库 / 安装来源' : currentSourceType.value === 'npm_package' ? 'npm 包名 / 文档来源' : currentSourceType.value === 'python_package' ? 'Python 包名 / 文档来源' : '安装来源 / 文档')
const installSourcePlaceholder = computed(() => currentSourceType.value === 'github_repo' ? '例如：https://github.com/org/repo' : currentSourceType.value === 'npm_package' ? '例如：@playwright/cli 或其文档链接' : currentSourceType.value === 'python_package' ? '例如：obsidian-cli 或其文档链接' : '可填包名、文档链接或留空')
const sourceAssistHints = computed(() => currentSourceType.value === 'github_repo' ? ['优先填 GitHub 链接', '如果已经 clone，可以再补本地路径', 'Agent 会优先产出安装与启动建议'] : currentSourceType.value === 'npm_package' ? ['优先填包名或文档链接', '如果有示例命令，Agent 更容易推荐 npx 或 pnpm dlx'] : currentSourceType.value === 'python_package' ? ['优先填包名或文档链接', '可补充 uvx / python -m 使用习惯，便于给出更准确命令'] : currentSourceType.value === 'executable' ? ['优先填本地可执行路径', '如果还有 README，可补 docs 或目录让 Agent 理解用法'] : ['优先填本地目录', '如有 GitHub 或文档地址也一起给，建议会更完整'])

const extractUrls = (value?: string) => Array.from(new Set((value || '').match(/https?:\/\/[^\s"'<>]+/g)?.map((item) => item.replace(/[.,);]+$/, '')) || []))
const buildEndpointUrl = (baseUrl?: string, path?: string) => {
  const base = (baseUrl || '').trim().replace(/\/+$/, '')
  const apiPath = (path || '').trim()
  if (!base) return ''
  if (!apiPath || apiPath === '/') return `${base}/`
  return `${base}${apiPath.startsWith('/') ? '' : '/'}${apiPath}`
}
const guessDisplayNameFromEndpoint = (value: string) => {
  try {
    const host = new URL(value).hostname.replace(/^api\./, '').split('.')[0]
    return host || 'remote_api_tool'
  } catch {
    return 'remote_api_tool'
  }
}
const getErrorMessage = (error: any, fallback: string) => error?.response?.data?.detail || error?.response?.data?.status_message || error?.message || fallback
const formatArgsTemplate = (value?: string[] | string | null) => (Array.isArray(value) ? value.join(' ') : value || '')
const formatConfidence = (value?: number) => (typeof value === 'number' && !Number.isNaN(value) ? `${Math.round(value * 100)}%` : '')

const resetToolConnectivityState = () => { toolConnectivityError.value = ''; toolConnectivityResult.value = null }
const setConfigPanelRef = (instance: InstanceType<typeof ConfigurationPanel> | null) => {
  configPanelRef.value = instance
}
const addSimpleApiParam = () => simpleApiParams.value.push({ name: '', in: 'query', required: false, type: 'string', description: '' })
const removeSimpleApiParam = (index: number) => simpleApiParams.value.splice(index, 1)
const shouldAutoRefreshToolStatus = (tool: ToolItem) => {
  if (isSystemTool(tool) || tool.runtime_status) return false
  const metadata = tool.source_metadata || tool.auth_config?.source_metadata || {}
  const cliConfig = tool.auth_config?.cli_config || {}
  return Boolean(metadata.probe_args || cliConfig.healthcheck_command)
}
const refreshCustomToolStatuses = (items: ToolItem[]) => {
  items
    .filter(shouldAutoRefreshToolStatus)
    .slice(0, 8)
    .forEach((tool, index) => {
      window.setTimeout(() => refreshToolStatus(tool, { silent: true }), 120 * index)
    })
}

const fetchTools = async () => {
  loading.value = true
  try {
    const [toolResponse, configResponse] = await Promise.all([getVisibleToolsAPI(), getConfigAPI().catch(() => null)])
    const systemMeta = new Map((configResponse?.data?.data?.system_tools || []).map((item) => [item.tool_name, item]))
    tools.value = (toolResponse.data.data || []).map((tool) => {
      const meta = systemMeta.get(tool.name)
      return {
        ...tool,
        runtime_type: tool.runtime_type || 'remote_api',
        system_tool_kind: meta?.tool_kind,
        system_tool_kind_label: meta?.tool_kind_label,
        strategy_code: meta?.strategy_code,
        strategy_label: meta?.strategy_label,
        strategy_summary: meta?.strategy_summary,
        install_requirement: meta?.install_requirement,
        config_requirement: meta?.config_requirement,
        has_fields: meta?.has_fields,
        system_status: meta?.status,
      }
    })
    refreshCustomToolStatuses(tools.value)
  } catch (error: any) {
    ElMessage.error(getErrorMessage(error, '加载工具失败'))
  } finally {
    loading.value = false
  }
}

const resetDialog = () => {
  isEditMode.value = false
  remoteApiAssistError.value = ''
  remoteApiAssistResult.value = null
  toolConnectivityError.value = ''
  toolConnectivityResult.value = null
  cliPreviewError.value = ''
  cliPreviewResult.value = null
  assistForm.value = { github_url: '', docs_url: '', local_path: '', notes: '' }
  remoteApiAssistForm.value = { endpoint_url: '', docs_urls_text: '', sample_curl: '', probe_args: {} }
  form.value = { display_name: '', description: '', logo_url: '', runtime_type: 'remote_api', remote_api_mode: 'simple', openapi_schema: createDefaultOpenApiSchema(), auth_type: '', auth_key_name: '', auth_token: '', simple_api_config: createDefaultSimpleApiConfig(), cli_config: createDefaultCliConfig() }
}

const openCreateDialog = async () => {
  if (workbenchMode.value === 'create') {
    closeWorkbench()
    return
  }
  resetDialog()
  selectedTool.value = null
  expandedConfigToolId.value = ''
  workbenchMode.value = 'create'
  dialogVisible.value = true
  try {
    const response = await getDefaultToolLogoAPI()
    form.value.logo_url = response.data.data.logo_url || ''
  } catch {}
}

const openEditDialog = async (tool: ToolItem) => {
  if (isEditingTool(tool)) {
    await submitDialog()
    return
  }
  resetDialog()
  isEditMode.value = true
  selectedTool.value = tool
  expandedConfigToolId.value = ''
  workbenchMode.value = 'edit'
  const auth = tool.auth_config || {}
  const simpleFromAuth = auth.simple_api_config || auth.source_metadata?.simple_api_config
  const storedAuthType = auth.type || (auth.auth_type === 'APIKey' && auth.in === 'query' ? 'api_key_query' : auth.auth_type === 'APIKey' && auth.in === 'header' ? 'api_key_header' : String(auth.auth_type || '').toLowerCase())
  form.value = {
    tool_id: tool.tool_id,
    display_name: tool.display_name,
    description: tool.description || '',
    logo_url: tool.logo_url || '',
    runtime_type: tool.runtime_type || (auth.runtime_type === 'cli' ? 'cli' : 'remote_api'),
    remote_api_mode: tool.openapi_schema && !tool.simple_api_config && !simpleFromAuth ? 'openapi' : 'simple',
    openapi_schema: JSON.stringify(tool.openapi_schema || {}, null, 2),
    auth_type: (storedAuthType === 'none' ? '' : storedAuthType || '') as RemoteApiAuthType,
    auth_key_name: auth.name || '',
    auth_token: auth.token || auth.data || '',
    simple_api_config: tool.simple_api_config || simpleFromAuth || createDefaultSimpleApiConfig(),
    cli_config: { ...createDefaultCliConfig(), ...(auth.cli_config || {}) },
  }
  const metadata = tool.source_metadata || auth.source_metadata || {}
  remoteApiAssistForm.value = { endpoint_url: metadata.endpoint_url || buildEndpointUrl(form.value.simple_api_config.base_url, form.value.simple_api_config.path), docs_urls_text: (metadata.docs_urls || [metadata.docs_url]).filter(Boolean).join('\n'), sample_curl: metadata.sample_curl || '', probe_args: metadata.probe_args || {} }
  assistForm.value = { github_url: metadata.github_url || '', docs_url: metadata.docs_url || '', local_path: metadata.local_path || form.value.cli_config.tool_dir || '', notes: metadata.notes || '' }
  dialogVisible.value = true
}

const openSystemToolConfig = (tool: ToolItem) => {
  if (expandedConfigToolId.value === tool.tool_id) {
    expandedConfigToolId.value = ''
    selectedTool.value = null
    return
  }
  selectedTool.value = tool
  expandedToolInfoId.value = ''
  expandedConfigToolId.value = tool.tool_id
  dialogVisible.value = false
  workbenchMode.value = 'list'
}

const closeWorkbench = () => {
  workbenchMode.value = 'list'
  selectedTool.value = null
  expandedConfigToolId.value = ''
  dialogVisible.value = false
}

const saveEmbeddedConfig = () => configPanelRef.value?.saveToolConfig()
const toggleAdvancedTools = () => {
  if (form.value.runtime_type === 'remote_api') {
    apiAdvancedSections.value = apiAdvancedSections.value.length ? [] : ['api']
  } else {
    advancedSections.value = advancedSections.value.length ? [] : ['execution']
  }
}
const resetInlineConfig = async (tool: ToolItem) => {
  if (!isSystemTool(tool)) return
  if (!isToolConfigExpanded(tool)) {
    openSystemToolConfig(tool)
    await nextTick()
    return
  }
  configPanelRef.value?.reloadToolConfig()
}
const handlePrimaryAction = async (tool: ToolItem) => isSystemTool(tool) ? openSystemToolConfig(tool) : await openEditDialog(tool)
const copyToolName = async (tool: ToolItem) => {
  try {
    await navigator.clipboard?.writeText(tool.name)
    ElMessage.success('工具名已复制')
  } catch {
    ElMessage.info(tool.name)
  }
}

const applyRemoteApiAssist = (result: RemoteApiAssistResponse) => {
  form.value.display_name = result.display_name || form.value.display_name
  form.value.description = result.description || form.value.description
  form.value.simple_api_config = result.simple_api_config || form.value.simple_api_config
  form.value.openapi_schema = JSON.stringify(result.openapi_schema || {}, null, 2)
  const auth = result.auth_config || {}
  const normalizedAuthType = auth.type || (auth.auth_type === 'APIKey' && auth.in === 'query' ? 'api_key_query' : auth.auth_type === 'APIKey' && auth.in === 'header' ? 'api_key_header' : String(auth.auth_type || '').toLowerCase())
  form.value.auth_type = (normalizedAuthType === 'none' ? '' : normalizedAuthType || form.value.auth_type) as RemoteApiAuthType
  form.value.auth_key_name = auth.name || form.value.auth_key_name
  form.value.auth_token = auth.token || auth.data || form.value.auth_token
  remoteApiAssistForm.value.endpoint_url = buildEndpointUrl(form.value.simple_api_config.base_url, form.value.simple_api_config.path)
  remoteApiAssistForm.value.probe_args = result.probe_args || {}
}

const previewRemoteApi = async (options: { silent?: boolean } = {}) => {
  const docsUrls = extractUrls(remoteApiAssistForm.value.docs_urls_text)
  const payload: RemoteApiAssistRequest = { endpoint_url: remoteApiAssistForm.value.endpoint_url.trim(), docs_url: docsUrls[0] || '', docs_urls: docsUrls, sample_curl: remoteApiAssistForm.value.sample_curl.trim(), api_key: form.value.auth_token.trim(), api_key_name: form.value.auth_key_name.trim(), auth_type: form.value.auth_type || undefined, display_name: form.value.display_name.trim(), description: form.value.description.trim(), method: form.value.simple_api_config.method || 'GET' }
  if (!payload.endpoint_url && !payload.sample_curl && !docsUrls.length) {
    remoteApiAssistError.value = '至少提供一个文档地址；如果文档里没有接口示例，再补接口地址或 curl 示例。'
    if (!options.silent) ElMessage.warning(remoteApiAssistError.value)
    return false
  }
  remoteApiAssistLoading.value = true
  remoteApiAssistError.value = ''
  try {
    const response = await assistRemoteApiToolAPI(payload)
    if (response.data.status_code !== 200) throw new Error(response.data.status_message || '智能填表失败')
    remoteApiAssistResult.value = response.data.data
    applyRemoteApiAssist(response.data.data)
    if (!options.silent) ElMessage.success('智能填表完成')
    return true
  } catch (error: any) {
    remoteApiAssistError.value = getErrorMessage(error, '智能填表失败')
    if (!options.silent) ElMessage.error(remoteApiAssistError.value)
    return false
  } finally {
    remoteApiAssistLoading.value = false
  }
}

const ensureRemoteApiDraftReady = async () => {
  if (form.value.runtime_type !== 'remote_api' || form.value.remote_api_mode !== 'simple') return true
  if (form.value.simple_api_config.base_url.trim() && form.value.simple_api_config.path.trim()) return true
  return previewRemoteApi({ silent: true })
}

const validateToolForm = (options: { silent?: boolean } = {}) => {
  const warn = (message: string) => {
    if (!options.silent) ElMessage.warning(message)
    return false
  }
  if (!form.value.display_name.trim()) form.value.display_name = form.value.runtime_type === 'remote_api' ? guessDisplayNameFromEndpoint(remoteApiAssistForm.value.endpoint_url || extractUrls(remoteApiAssistForm.value.docs_urls_text)[0] || '') : ''
  if (!form.value.display_name.trim()) return warn('请先填写工具名称')
  if (!form.value.description.trim()) return warn('请先填写工具描述，或点击智能填表让 Agent 生成描述')
  if (form.value.runtime_type === 'cli' && !form.value.cli_config.command?.trim()) return warn('CLI 工具至少需要一个启动命令')
  if (form.value.runtime_type === 'cli' && requiresToolDir.value && !form.value.cli_config.tool_dir?.trim()) return warn('当前来源类型需要填写本地目录')
  return true
}

const syncSimpleApiMetadata = () => {
  if (!form.value.simple_api_config.operation_id.trim()) form.value.simple_api_config.operation_id = form.value.display_name.trim().replace(/\W+/g, '_').toLowerCase() || 'call_api'
  if (!form.value.simple_api_config.summary?.trim()) form.value.simple_api_config.summary = form.value.description.trim()
  if (!form.value.simple_api_config.description?.trim()) form.value.simple_api_config.description = form.value.description.trim()
}

const buildToolPayload = () => {
  const payload: Record<string, any> = { display_name: form.value.display_name.trim(), description: form.value.description.trim(), logo_url: form.value.logo_url.trim(), runtime_type: form.value.runtime_type }
  if (form.value.runtime_type === 'remote_api') {
    if (form.value.remote_api_mode === 'simple') {
      syncSimpleApiMetadata()
      payload.simple_api_config = { ...form.value.simple_api_config, base_url: form.value.simple_api_config.base_url.trim(), path: form.value.simple_api_config.path.trim(), params: simpleApiParams.value.map((item) => ({ ...item, name: item.name.trim(), description: item.description?.trim() || '' })) }
    } else {
      payload.openapi_schema = JSON.parse(form.value.openapi_schema)
    }
    const docsUrls = extractUrls(remoteApiAssistForm.value.docs_urls_text)
    payload.source_metadata = { endpoint_url: remoteApiAssistForm.value.endpoint_url.trim() || buildEndpointUrl(form.value.simple_api_config.base_url, form.value.simple_api_config.path), docs_url: docsUrls[0] || '', docs_urls: docsUrls, sample_curl: remoteApiAssistForm.value.sample_curl.trim(), remote_api_mode: form.value.remote_api_mode, probe_args: remoteApiProbeArgs.value }
    payload.auth_config = form.value.auth_type ? { type: form.value.auth_type, token: form.value.auth_token || '', name: needsAuthKeyName.value ? form.value.auth_key_name.trim() : '' } : {}
    return payload
  }
  payload.cli_config = { ...form.value.cli_config, source_type: form.value.cli_config.source_type || 'local_directory', tool_dir: form.value.cli_config.tool_dir.trim(), command: form.value.cli_config.command.trim(), args_template: form.value.cli_config.args_template?.trim() || '', cwd: form.value.cli_config.cwd?.trim() || '', install_command: form.value.cli_config.install_command?.trim() || '', install_source: form.value.cli_config.install_source?.trim() || '', install_notes: form.value.cli_config.install_notes?.trim() || '', healthcheck_command: form.value.cli_config.healthcheck_command?.trim() || '', credential_mode: form.value.cli_config.credential_mode || 'none' }
  payload.source_metadata = { github_url: assistForm.value.github_url.trim(), docs_url: assistForm.value.docs_url.trim(), local_path: assistForm.value.local_path.trim(), notes: assistForm.value.notes.trim() }
  return payload
}

const testToolConnectivity = async () => {
  if (!(await ensureRemoteApiDraftReady()) || !validateToolForm()) return
  toolConnectivityLoading.value = true
  resetToolConnectivityState()
  try {
    const payload = buildToolPayload()
    const response = await testToolConnectivityAPI({ runtime_type: payload.runtime_type, auth_config: payload.auth_config, cli_config: payload.cli_config, openapi_schema: payload.openapi_schema, simple_api_config: payload.simple_api_config, probe_args: remoteApiProbeArgs.value })
    toolConnectivityResult.value = response.data.data
    if (response.data.data.ok && response.data.data.executed) ElMessage.success('连通性测试成功')
    else if (response.data.data.ok) ElMessage.info(response.data.data.summary || '未执行真实检测')
    else ElMessage.warning(response.data.data.summary || '检测未通过')
  } catch (error: any) {
    toolConnectivityError.value = getErrorMessage(error, '测试工具连通性失败')
  } finally {
    toolConnectivityLoading.value = false
  }
}

const submitDialog = async () => {
  if (!validateToolForm({ silent: true })) {
    closeWorkbench()
    return
  }
  if (!(await ensureRemoteApiDraftReady()) || !validateToolForm({ silent: true })) {
    closeWorkbench()
    return
  }
  dialogLoading.value = true
  try {
    const payload = buildToolPayload()
    const response = isEditMode.value && form.value.tool_id ? await updateToolAPI({ tool_id: form.value.tool_id, ...payload }) : await createToolAPI(payload)
    if (response.data.status_code !== 200) throw new Error(response.data.status_message || '保存工具失败')
    ElMessage.success(isEditMode.value ? '工具已更新' : '工具已创建')
    closeWorkbench()
    await fetchTools()
  } catch (error: any) {
    ElMessage.error(getErrorMessage(error, '保存工具失败'))
  } finally {
    dialogLoading.value = false
  }
}

const handleDelete = async (tool: ToolItem) => {
  if (isSystemTool(tool)) {
    ElMessage.info('系统工具由后端配置托管，不能在这里删除。')
    return
  }
  try { await ElMessageBox.confirm(`确认删除工具「${tool.display_name}」吗？`, '删除工具', { type: 'warning', confirmButtonText: '删除', cancelButtonText: '取消' }) } catch { return }
  try {
    const response = await deleteToolAPI({ tool_id: tool.tool_id })
    if (response.data.status_code !== 200) throw new Error(response.data.status_message || '删除工具失败')
    ElMessage.success('工具已删除')
    await fetchTools()
  } catch (error: any) {
    ElMessage.error(getErrorMessage(error, '删除工具失败'))
  }
}

const showConnectivityToast = (tool: ToolItem, result: ToolConnectivityResponse) => {
  if (result.ok && result.executed) ElMessage.success(`${tool.display_name} 连通性正常`)
  else if (result.ok) ElMessage.info(result.summary || '未执行真实检测')
  else ElMessage.warning(result.summary || '检测未通过')
}

const refreshToolStatus = async (tool: ToolItem, options: { silent?: boolean } = {}) => {
  statusRefreshing.value[tool.tool_id] = true
  try {
    const response = isSystemTool(tool) ? await testSystemToolConnectivityAPI(tool.name) : await testSavedToolConnectivityAPI(tool.tool_id)
    const status = response.data.data.status || null
    if (isSystemTool(tool)) tool.system_status = status
    else tool.runtime_status = status
    if (!options.silent) showConnectivityToast(tool, response.data.data)
  } catch (error: any) {
    if (!options.silent) ElMessage.error(getErrorMessage(error, '检测失败'))
  } finally {
    statusRefreshing.value[tool.tool_id] = false
  }
}

const applyCliSuggestion = (payload: Partial<CliStructuredSuggestion | CliPreviewCandidate>) => {
  const nextArgs = formatArgsTemplate(payload.args_template as string[] | string | null)
  form.value.display_name = payload.display_name || payload.tool_name || form.value.display_name || cliPreviewResult.value?.display_name || ''
  form.value.description = payload.description || payload.reason || form.value.description || cliPreviewResult.value?.description || cliPreviewResult.value?.default_description || ''
  if (payload.command) form.value.cli_config.command = payload.command
  if (nextArgs) form.value.cli_config.args_template = nextArgs
  if (payload.cwd_mode) form.value.cli_config.cwd_mode = payload.cwd_mode
  if (payload.cwd !== undefined && payload.cwd !== null) form.value.cli_config.cwd = payload.cwd
  if (payload.tool_dir) form.value.cli_config.tool_dir = payload.tool_dir
  if (payload.install_source) form.value.cli_config.install_source = payload.install_source
  if (payload.install_command) form.value.cli_config.install_command = payload.install_command
  if (payload.healthcheck_command) form.value.cli_config.healthcheck_command = payload.healthcheck_command
}

const previewCli = async () => {
  const requestPayload: CliAssistRequest = { tool_dir: form.value.cli_config.tool_dir.trim() || assistForm.value.local_path.trim(), source_type: currentSourceType.value, install_source: form.value.cli_config.install_source?.trim() || '', command: form.value.cli_config.command?.trim() || '', doc_url: assistForm.value.docs_url.trim(), github_url: assistForm.value.github_url.trim(), docs_url: assistForm.value.docs_url.trim(), local_path: assistForm.value.local_path.trim(), notes: assistForm.value.notes.trim() }
  if (!requestPayload.tool_dir && !requestPayload.github_url && !requestPayload.docs_url) { cliPreviewError.value = '至少提供一个本地路径、GitHub 链接或文档链接。'; return }
  cliPreviewLoading.value = true
  cliPreviewError.value = ''
  cliPreviewResult.value = null
  try {
    const response = await previewCliToolAPI(requestPayload)
    cliPreviewResult.value = response.data.data
    if (!form.value.display_name.trim()) form.value.display_name = response.data.data.display_name || response.data.data.suggested_name || ''
    if (!form.value.description.trim()) form.value.description = response.data.data.description || response.data.data.default_description || ''
    if (!form.value.cli_config.healthcheck_command?.trim() && response.data.data.suggested_healthcheck_command) form.value.cli_config.healthcheck_command = response.data.data.suggested_healthcheck_command
    if (!form.value.cli_config.command?.trim() && response.data.data.recommended?.command) applyCliSuggestion(response.data.data.recommended)
  } catch (error: any) {
    cliPreviewError.value = getErrorMessage(error, 'Agent assist 分析失败')
  } finally {
    cliPreviewLoading.value = false
  }
}

const handleLogoUpload = async (uploadFile: any) => {
  logoUploading.value = true
  try {
    const response = await uploadFileAPI(uploadFile.raw)
    form.value.logo_url = response.data.data
    ElMessage.success('图标上传成功')
  } catch (error: any) {
    ElMessage.error(getErrorMessage(error, '上传工具图标失败'))
  } finally {
    logoUploading.value = false
  }
}

onMounted(fetchTools)
</script><template>
  <div class="tool-page">
    <section class="hero-card">
      <div>
        <div class="settings-title-row">
          <img :src="settingsToolIcon" alt="工具" class="page-icon" />
          <h1>工具</h1>
        </div>
      </div>
      <div class="hero-actions">
        <el-button
          :class="['settings-icon-button', { 'is-create-open': dialogVisible && !isEditMode }]"
          type="primary"
          :icon="Plus"
          circle
          :title="dialogVisible && !isEditMode ? '收起新建工具' : '新建工具'"
          :aria-label="dialogVisible && !isEditMode ? '收起新建工具' : '新建工具'"
          @click="openCreateDialog"
        />
      </div>
    </section>

    <section class="toolbar-card">
      <el-tabs v-model="activeTab" class="tool-tabs">
        <el-tab-pane label="全部工具" name="all" />
        <el-tab-pane label="我的工具" name="custom" />
      </el-tabs>
      <div class="settings-search-row tool-search-row">
        <el-input v-model="keyword" placeholder="搜索工具名称、描述或运行方式" clearable class="search-box search-input">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </section>

    <Transition name="settings-panel">
      <section v-if="isToolFormMode" class="tool-workbench-card tool-config-bubble">
        <header class="workbench-head">
          <div>
            <h2>{{ workbenchTitle }}</h2>
          </div>
          <div class="workbench-actions">
            <el-button class="settings-icon-button save-action" type="primary" :icon="Check" circle :loading="dialogLoading" title="保存" aria-label="保存" @click="submitDialog" />
          </div>
        </header>

        <el-form label-position="top" class="tool-form">
          <el-form-item label="工具图标">
            <div class="logo-upload-row">
              <div class="logo-preview"><img :src="form.logo_url || toolDefaultIcon" alt="工具图标预览" @error="handleToolLogoError" /></div>
              <el-upload :show-file-list="false" :auto-upload="false" accept="image/*" :on-change="handleLogoUpload">
                <el-button :loading="logoUploading" :icon="Upload">上传图标</el-button>
              </el-upload>
            </div>
          </el-form-item>

          <div class="field-grid">
            <el-form-item label="名称"><el-input v-model="form.display_name" placeholder="例如：IP 地理位置查询" /></el-form-item>
            <el-form-item label="运行方式">
              <el-radio-group v-model="form.runtime_type">
                <el-radio-button label="remote_api" value="remote_api">远程 API</el-radio-button>
                <el-radio-button label="cli" value="cli">CLI</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="描述" class="span-2">
              <el-input v-model="form.description" type="textarea" :autosize="{ minRows: 1, maxRows: 3 }" resize="none" placeholder="一句话说明这个工具负责什么能力，供 Agent 判断何时调用。" />
            </el-form-item>
          </div>

          <div class="form-utility-row">
            <el-button
              v-if="form.runtime_type === 'remote_api'"
              class="inline-utility-button"
              :icon="EditPen"
              :loading="remoteApiAssistLoading"
              @click="() => previewRemoteApi()"
            >
              智能填表
            </el-button>
            <el-button
              v-else
              class="inline-utility-button"
              :icon="EditPen"
              :loading="cliPreviewLoading"
              @click="previewCliAssist"
            >
              智能分析
            </el-button>
            <el-button class="inline-utility-button" :icon="Connection" :loading="toolConnectivityLoading" @click="testToolConnectivity">检测草稿</el-button>
            <span v-if="toolConnectivityResult" class="utility-status" :class="{ warning: !toolConnectivityResult.ok }">{{ toolConnectivityResult.summary }}</span>
            <span v-else-if="toolConnectivityError" class="utility-status warning">{{ toolConnectivityError }}</span>
          </div>

          <template v-if="form.runtime_type === 'remote_api'">
            <section class="nested-panel">
              <div class="panel-head api-assist-head">
                <div>
                  <h3>连接配置</h3>
                </div>
              </div>

              <div class="field-grid">
                <el-form-item label="文档地址" class="span-2" required>
                  <el-input v-model="remoteApiAssistForm.docs_urls_text" type="textarea" :autosize="{ minRows: 1, maxRows: 3 }" resize="none" placeholder="每行一个文档地址，例如：https://docs.apilayer.com/ipstack/docs/quickstart-guide" />
                </el-form-item>
                <el-form-item label="API Key" class="span-2" required>
                  <el-input v-model="form.auth_token" type="textarea" :autosize="{ minRows: 1, maxRows: 3 }" resize="none" placeholder="只填服务商给你的 API Key。" />
                </el-form-item>
                <el-form-item label="接口地址" class="span-2">
                  <el-input v-model="remoteApiAssistForm.endpoint_url" placeholder="例如：https://api.ipstack.com/check" />
                </el-form-item>
              </div>

              <el-alert v-if="remoteApiAssistError" type="error" :closable="false" :title="remoteApiAssistError" />
              <el-alert v-else-if="remoteApiAssistResult" type="success" :closable="false" :title="remoteApiAssistSummary || '已生成 API 草稿，可继续微调。'" />

              <el-collapse v-model="apiAdvancedSections" class="advanced-block">
                <el-collapse-item title="高级设置" name="api">
                  <el-form-item label="接入方式">
                    <el-radio-group v-model="form.remote_api_mode">
                      <el-radio-button label="simple" value="simple">简单接入</el-radio-button>
                      <el-radio-button label="openapi" value="openapi">原始 OpenAPI</el-radio-button>
                    </el-radio-group>
                  </el-form-item>
                  <template v-if="form.remote_api_mode === 'simple'">
                    <div class="field-grid">
                      <el-form-item label="认证方式">
                        <el-select v-model="form.auth_type" placeholder="由 Agent 自动识别">
                          <el-option label="无认证" value="" />
                          <el-option label="Bearer Token" value="bearer" />
                          <el-option label="Basic Auth" value="basic" />
                          <el-option label="API Key（Query）" value="api_key_query" />
                          <el-option label="API Key（Header）" value="api_key_header" />
                        </el-select>
                      </el-form-item>
                      <el-form-item label="认证字段"><el-input v-model="form.auth_key_name" placeholder="例如：access_key / api_key / x-api-key" /></el-form-item>
                      <el-form-item label="curl 示例" class="span-2"><el-input v-model="remoteApiAssistForm.sample_curl" type="textarea" :autosize="{ minRows: 1, maxRows: 3 }" resize="none" placeholder="可选。直接贴一段 curl。" /></el-form-item>
                      <el-form-item label="Base URL"><el-input v-model="form.simple_api_config.base_url" placeholder="例如：https://api.ipstack.com" /></el-form-item>
                      <el-form-item label="Path"><el-input v-model="form.simple_api_config.path" placeholder="/check" /></el-form-item>
                      <el-form-item label="Method">
                        <el-select v-model="form.simple_api_config.method">
                          <el-option label="GET" value="GET" />
                          <el-option label="POST" value="POST" />
                          <el-option label="PUT" value="PUT" />
                          <el-option label="DELETE" value="DELETE" />
                        </el-select>
                      </el-form-item>
                      <el-form-item label="Operation ID"><el-input v-model="form.simple_api_config.operation_id" /></el-form-item>
                    </div>
                  </template>
                  <el-form-item v-else label="OpenAPI Schema">
                    <el-input v-model="form.openapi_schema" type="textarea" :rows="8" />
                  </el-form-item>
                </el-collapse-item>
              </el-collapse>
            </section>
          </template>

          <template v-else>
            <section class="nested-panel">
              <div class="panel-head">
                <div>
                  <h3>CLI 配置</h3>
                </div>
              </div>
              <div class="field-grid">
                <el-form-item label="来源类型">
                  <el-select v-model="form.cli_config.source_type">
                    <el-option v-for="option in cliSourceOptions" :key="option.value" :label="option.label" :value="option.value" />
                  </el-select>
                </el-form-item>
                <el-form-item v-if="requiresToolDir" label="工具目录"><el-input v-model="form.cli_config.tool_dir" placeholder="本地目录或仓库目录" /></el-form-item>
                <el-form-item label="命令" class="span-2"><el-input v-model="form.cli_config.command" placeholder="例如：python main.py" /></el-form-item>
                <el-form-item label="参数模板" class="span-2"><el-input v-model="form.cli_config.args_template" placeholder="例如：--city {{city}}" /></el-form-item>
              </div>
            </section>
          </template>
        </el-form>
      </section>
    </Transition>

    <section class="list-card" v-loading="loading">
      <div v-if="!visibleTools.length && !isToolFormMode" class="empty-state settings-empty-hint">
        <img :src="emptyDataIcon" alt="空数据" class="empty-state-icon" />
        {{ keyword ? '没有匹配到工具，换个关键词试试看吧 (´･_･`)' : '工具箱还是空的，点右上角 + 加一件趁手小工具吧 ( •̀ ω •́ )✧' }}
      </div>
      <template v-for="row in paginatedTools" :key="row.tool_id">
        <article class="tool-row" :class="{ 'is-info-open': isToolInfoExpanded(row), 'is-config-open': isToolConfigExpanded(row) }">
          <div class="logo-wrap"><img :src="getToolLogo(row)" :alt="row.display_name" @error="handleToolLogoError" /></div>
          <div class="tool-main">
            <div class="tool-title-row">
              <span class="tool-name" :title="row.display_name">{{ row.display_name }}</span>
              <span class="tool-description" :title="getToolSummary(row)">{{ getToolSummary(row) }}</span>
            </div>
            <div class="tool-meta-row">
              <span v-if="isSystemTool(row)" class="meta-badge">系统</span>
              <span class="hint-chip">{{ getToolRuntimeLabel(row) }}</span>
              <span v-for="hint in getToolHints(row)" :key="hint" class="hint-chip">{{ hint }}</span>
              <span class="status-pill" :class="getToolStatusTone(row)">
                <span class="status-dot" />
                <span>{{ getToolStatusLabel(row) }}</span>
              </span>
            </div>
          </div>
          <div class="tool-side">
            <div class="action-row">
              <el-button class="ghost-action icon-action" :class="{ active: isToolInfoExpanded(row) }" :icon="InfoFilled" circle title="信息" aria-label="信息" @click="toggleToolInfo(row)" />
              <el-button v-if="canOpenPrimaryAction(row)" class="primary-action icon-action" :class="{ active: isToolConfigExpanded(row) || isEditingTool(row) }" :icon="getPrimaryActionIcon(row)" circle :loading="isEditingTool(row) && dialogLoading" :title="isToolConfigExpanded(row) ? '收起' : getPrimaryActionLabel(row)" :aria-label="isToolConfigExpanded(row) ? '收起' : getPrimaryActionLabel(row)" @click="handlePrimaryAction(row)" />
              <el-button class="secondary-action icon-action" :icon="Connection" circle plain :loading="isStatusRefreshing(row)" title="检测" aria-label="检测" @click="refreshToolStatus(row)" />
              <el-button class="ghost-action icon-action" :icon="CopyDocument" circle title="复制工具名" aria-label="复制工具名" @click="copyToolName(row)" />
              <el-button v-if="!isSystemTool(row)" class="danger-action icon-action" :icon="Delete" circle title="删除" aria-label="删除" @click="handleDelete(row)" />
            </div>
          </div>
        </article>
        <section v-if="isToolInfoExpanded(row)" class="tool-row-info">
          <div v-if="toolInfoLoading[row.tool_id]" class="tool-info-loading">正在整理工具信息...</div>
          <template v-else>
            <article v-for="card in getToolInfoCards(row)" :key="card.key" class="tool-info-card" :class="card.tone ? `is-${card.tone}` : ''">
              <div class="tool-info-kicker">{{ card.eyebrow }}</div>
              <div class="tool-info-body">
                <strong>{{ card.title }}</strong>
                <p>{{ card.summary }}</p>
                <ul v-if="card.items.length">
                  <li v-for="item in card.items" :key="item">{{ item }}</li>
                </ul>
              </div>
            </article>
          </template>
        </section>
        <section v-if="isToolConfigExpanded(row)" class="tool-inline-config">
          <header class="inline-config-head">
            <span>{{ row.display_name }}配置</span>
            <el-button class="settings-icon-button save-action" type="primary" :icon="Check" circle title="保存" aria-label="保存" @click="saveEmbeddedConfig" />
          </header>
          <ConfigurationPanel :ref="setConfigPanelRef" :tool="row.name" embedded :show-intro="false" />
        </section>
      </template>
      <ZunoMiniPager v-model:page="listPage" class="settings-list-pager" :total="visibleTools.length" :page-size="LIST_PAGE_SIZE" />
    </section>
  </div>
</template>
<style scoped lang="scss">
.tool-page {
  display: grid;
  gap: 18px;
  padding: 24px;
}

.hero-card,
.toolbar-card,
.list-card,
.tool-workbench-card {
  border-radius: 24px;
  border: 1px solid rgba(214, 132, 70, 0.1);
  background: rgba(255, 252, 248, 0.97);
  box-shadow: 0 12px 28px rgba(120, 80, 42, 0.05);
}

.hero-card,
.toolbar-card {
  padding: 22px 24px;
}

.hero-card {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
}

.hero-card > div:first-child {
  min-width: 0;
}

.settings-title-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.page-icon {
  width: 40px;
  height: 40px;
  object-fit: contain;
}

.hero-card h1 {
  margin: 0;
  font-size: 32px;
  color: #2f241b;
}

.hero-card p {
  margin: 0;
  color: #786656;
  line-height: 1.8;
  max-width: 760px;
}

.hero-actions {
  margin-top: 18px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.hero-actions .is-create-open :deep(.el-icon) {
  transform: rotate(45deg);
  transition: transform 180ms cubic-bezier(.2, .8, .2, 1);
}

.toolbar-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 8px;
  align-items: start;
}

.tool-tabs {
  min-width: 0;
}

.tool-search-row {
  width: 100%;
}

.search-box {
  width: 100%;
}

.list-card {
  padding: 2px 0;
  overflow: hidden;
}

.tool-workbench-card {
  padding: 18px 22px 20px;
  overflow: visible;
  background:
    linear-gradient(180deg, rgba(255, 253, 250, 0.96), rgba(255, 250, 245, 0.88)),
    rgba(255, 255, 255, 0.84);
  animation: tool-workbench-rise 220ms cubic-bezier(.2, .8, .2, 1) both;
}

.workbench-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 14px;
}

.workbench-head h2 {
  margin: 0;
  font-size: 17px;
  color: #111827;
  letter-spacing: 0;
}

.workbench-head p {
  margin: 6px 0 0;
  color: #718096;
  font-size: 13px;
  line-height: 1.55;
}

.workbench-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  flex-shrink: 0;
}

.workbench-actions :deep(.el-button + .el-button),
.workbench-actions :deep(.el-dropdown + .el-button),
.workbench-actions :deep(.el-button + .el-dropdown) {
  margin-left: 0;
}

.workbench-actions .is-active {
  border-color: rgba(245, 158, 11, 0.34);
  background: rgba(245, 158, 11, 0.12);
  color: #b45309;
}

.save-action {
  box-shadow: 0 14px 26px rgba(245, 158, 11, 0.16);
}

.tool-form {
  display: grid;
  gap: 10px;
}

.tool-info-panel {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 12px 16px;
  align-items: start;
  padding: 18px;
  border-radius: 20px;
  border: 1px solid rgba(245, 158, 11, 0.14);
  background: linear-gradient(180deg, rgba(255, 251, 247, 0.96), rgba(255, 247, 236, 0.72));
}

.info-orb {
  display: grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.tool-info-panel h3 {
  margin: 0;
  font-size: 17px;
  color: #111827;
}

.tool-info-panel p {
  margin: 5px 0 0;
  color: #718096;
  font-size: 13px;
  line-height: 1.6;
}

.tool-info-panel ul {
  grid-column: 2;
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  color: #526174;
  font-size: 13px;
  line-height: 1.6;
  list-style: none;
}

.tool-info-panel li {
  position: relative;
  padding-left: 14px;
}

.tool-info-panel li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.72em;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: rgba(245, 158, 11, 0.76);
}

@keyframes tool-workbench-rise {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.992);
    filter: blur(4px);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
    filter: blur(0);
  }
}

.empty-state {
  padding: 44px 24px;
  text-align: center;
  color: #8b7868;
}

.tool-row {
  display: grid;
  grid-template-columns: 32px minmax(0, 1fr) max-content;
  gap: 16px;
  align-items: center;
  padding: 11px 4px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.14);
  transition: background 160ms ease;
}

.tool-row:last-child {
  border-bottom: none;
}

.tool-row:hover {
  background: linear-gradient(90deg, rgba(255, 251, 247, 0.5), rgba(255, 255, 255, 0));
}

.tool-row.is-info-open,
.tool-row.is-config-open {
  background: linear-gradient(90deg, rgba(255, 251, 247, 0.78), rgba(255, 255, 255, 0));
}

.tool-row-info {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0;
  margin: -2px 0 0 48px;
  padding: 2px 4px 10px 0;
  color: #6b7280;
  font-size: 12px;
  line-height: 1.5;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
  animation: tool-info-unfold 160ms ease both;
}

.tool-info-loading {
  grid-column: 1 / -1;
  color: #8a7765;
}

.tool-info-card {
  display: grid;
  grid-template-columns: 74px minmax(0, 1fr);
  gap: 12px;
  align-items: start;
  min-width: 0;
  padding: 9px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  background: transparent;
}

.tool-info-card:last-child {
  border-bottom: none;
}

.tool-info-card strong {
  color: #2f241b;
  font-size: 13px;
  line-height: 1.35;
}

.tool-info-card p {
  margin: 0;
  color: #6f6257;
  line-height: 1.5;
}

.tool-info-card ul {
  display: flex;
  flex-wrap: wrap;
  gap: 5px 8px;
  margin: 5px 0 0;
  padding: 0;
  list-style: none;
}

.tool-info-card li {
  display: inline-flex;
  min-width: 0;
  max-width: 100%;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.06);
  color: #7a6758;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.tool-info-card li::before {
  content: none;
}

.tool-info-kicker {
  display: inline-flex;
  justify-content: flex-start;
  color: #b78345;
  font-size: 10px;
  font-weight: 680;
  line-height: 1.45;
}

.tool-info-body {
  display: grid;
  gap: 3px;
  min-width: 0;
}

.tool-row-info span,
.tool-info-card p,
.tool-info-card li {
  overflow-wrap: anywhere;
}

.tool-inline-config {
  display: grid;
  gap: 8px;
  margin: 2px 0 16px 52px;
  padding: 12px 14px 14px;
  border-radius: 0;
  border: 0;
  border-top: 1px solid rgba(226, 232, 240, 0.72);
  border-bottom: 1px solid rgba(226, 232, 240, 0.48);
  background:
    linear-gradient(180deg, rgba(255, 253, 250, 0.54), rgba(255, 255, 255, 0.14));
  box-shadow: none;
  animation: tool-config-unfold 190ms cubic-bezier(.2, .8, .2, 1) both;
}

.inline-config-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  min-height: 32px;
}

.inline-config-head span {
  color: #2f241b;
  font-size: 14px;
  font-weight: 680;
}

@keyframes tool-info-unfold {
  from {
    opacity: 0;
    transform: translateY(-4px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes tool-config-unfold {
  from {
    opacity: 0;
    transform: translateY(-6px) scaleY(0.985);
    transform-origin: top;
  }

  to {
    opacity: 1;
    transform: translateY(0) scaleY(1);
    transform-origin: top;
  }
}

.logo-wrap {
  width: 30px;
  height: 30px;
  border-radius: 9px;
  overflow: hidden;
  background: transparent;
  border: 0;
  box-shadow: none;
}

.logo-wrap img,
.logo-preview img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.tool-main {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.tool-name-line,
.tool-title-row {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.tool-name {
  display: block;
  flex: 0 0 auto;
  max-width: min(34vw, 240px);
  font-size: 15px;
  font-weight: 680;
  color: #32261d;
  line-height: 1.25;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  word-break: break-word;
}

.meta-badge,
.meta-chip,
.source-pill,
.confidence-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid rgba(214, 132, 70, 0.1);
  font-size: 12px;
}

.meta-badge {
  background: #f8f4ee;
  color: #7a6656;
}

.meta-chip {
  background: rgba(255, 248, 238, 0.9);
  color: #7b6554;
  max-width: 100%;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.source-pill,
.confidence-chip {
  background: rgba(190, 109, 56, 0.1);
  color: #9a592f;
}

.tool-description {
  display: block;
  flex: 1 1 auto;
  min-width: 0;
  color: #615446;
  line-height: 1.35;
  font-size: 12px;
  margin: 0;
  max-width: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  word-break: break-word;
}

.tool-hints,
.tool-meta-row,
.hint-row,
.reference-row,
.detected-files {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tool-meta-row {
  align-items: center;
}

.hint-chip {
  display: inline-flex;
  align-items: center;
  min-height: 18px;
  padding: 0 7px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.06);
  color: #8a7765;
  font-size: 10.5px;
  line-height: 18px;
}

.hint-chip.soft {
  background: rgba(255, 248, 238, 0.95);
}

.tool-side {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  min-width: 0;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  min-height: 18px;
  padding: 0 7px;
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 540;
  background: #f5f5f5;
  color: #666;
}

.status-dot {
  width: 5px;
  height: 5px;
  border-radius: 999px;
  background: currentColor;
  opacity: 0.72;
}

.status-pill.is-ready {
  background: rgba(43, 178, 76, 0.12);
  color: #2d8a46;
}

.status-pill.is-warning {
  background: rgba(233, 170, 38, 0.14);
  color: #b17113;
}

.status-pill.is-danger {
  background: rgba(232, 90, 90, 0.12);
  color: #cf4f4f;
}

.status-pill.is-neutral {
  background: rgba(117, 117, 117, 0.1);
  color: #757575;
}

.action-row {
  display: flex;
  justify-content: flex-end;
  gap: 7px;
  flex-wrap: nowrap;
  min-width: max-content;
}

.action-row :deep(.el-button + .el-button),
.action-row :deep(.el-dropdown + .el-button),
.action-row :deep(.el-button + .el-dropdown) {
  margin-left: 0;
}

.icon-action {
  width: 28px;
  height: 28px;
  min-width: 28px;
  padding: 0;
  border-radius: 999px;
  flex-shrink: 0;
}

.primary-action {
  border: 1px solid rgba(245, 158, 11, 0.22);
  background: rgba(245, 158, 11, 0.1);
  color: #b45309;
}

.primary-action:hover {
  background: rgba(245, 158, 11, 0.18);
  color: #92400e;
}

.primary-action.active {
  background: #f59e0b;
  border-color: rgba(245, 158, 11, 0.92);
  color: #fff;
  box-shadow: 0 10px 18px rgba(245, 158, 11, 0.18);
}

.secondary-action {
  border-color: rgba(214, 132, 70, 0.2);
  color: #8b5a33;
  background: rgba(255, 252, 247, 0.62);
}

.ghost-action {
  border: 1px solid rgba(214, 132, 70, 0.12);
  color: #6f6257;
  background: rgba(255, 255, 255, 0.62);
}

.ghost-action.active {
  border-color: rgba(245, 158, 11, 0.3);
  color: #b45309;
  background: rgba(245, 158, 11, 0.1);
}

.danger-action {
  border: 1px solid rgba(239, 68, 68, 0.16);
  background: rgba(239, 68, 68, 0.055);
  color: #b91c1c;
}

.danger-action:hover {
  border-color: rgba(239, 68, 68, 0.28);
  background: rgba(239, 68, 68, 0.1);
  color: #991b1b;
}

.logo-editor {
  display: flex;
  gap: 16px;
  align-items: center;
}

.logo-preview {
  width: 44px;
  height: 44px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(214, 132, 70, 0.16);
  background: #f8efe4;
}

.logo-upload-row {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.cli-shell {
  display: grid;
  gap: 16px;
}

.cli-panel,
.advanced-block {
  border: 1px solid rgba(214, 132, 70, 0.12);
  border-radius: 20px;
  background: rgba(255, 250, 244, 0.92);
  padding: 18px;
}

.nested-panel {
  margin-top: 6px;
  background: rgba(255, 255, 255, 0.82);
}

.api-assist-head {
  margin-top: 8px;
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}

.panel-actions,
.field-stack {
  display: grid;
  gap: 10px;
}

.mini-tool-button {
  width: 30px;
  height: 30px;
  min-width: 30px;
  padding: 0;
  border-radius: 50%;
  border: 1px solid rgba(245, 158, 11, 0.18);
  background: rgba(255, 251, 247, 0.78);
  color: #b45309;
}

.panel-head h3 {
  margin: 0 0 6px;
  font-size: 18px;
  color: #2f241b;
}

.panel-head p,
.source-intro p,
.assist-summary p,
.recommend-card p,
.candidate-item p,
.structured-card p {
  margin: 0;
  color: #786656;
  line-height: 1.7;
}

.tool-workbench-card .panel-head {
  margin-bottom: 10px;
}

.tool-workbench-card .panel-head h3 {
  margin-bottom: 0;
  font-size: 15px;
}

.tool-config-bubble :deep(.el-form-item) {
  display: grid !important;
  grid-template-columns: minmax(54px, max-content) minmax(0, 1fr) !important;
  align-items: start;
  column-gap: 8px;
  row-gap: 2px;
  min-width: 0;
  margin: 0;
}

.tool-config-bubble :deep(.el-form-item__label) {
  float: none !important;
  display: flex !important;
  width: auto !important;
  min-width: 0 !important;
  min-height: 28px !important;
  height: auto !important;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.2;
  margin: 0;
  padding: 7px 0 0;
  text-align: left;
  justify-content: flex-start !important;
  white-space: nowrap;
}

.tool-config-bubble :deep(.el-form-item__content) {
  display: block !important;
  grid-column: 2;
  margin-left: 0 !important;
  min-width: 0;
}

.source-intro {
  margin-bottom: 16px;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(255, 245, 232, 0.9);
}

.source-intro strong {
  color: #32261d;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(160px, 1fr));
  gap: 7px 14px;
}

.form-utility-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px 10px;
  margin-top: -2px;
}

.inline-utility-button {
  min-height: 30px;
  border-radius: 999px;
  border-color: rgba(245, 158, 11, 0.22);
  background: rgba(245, 158, 11, 0.08);
  color: #b45309;
  font-size: 12px;
}

.utility-status {
  min-width: 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.45;
}

.utility-status.warning {
  color: #b45309;
}

.assist-panel {
  background: linear-gradient(180deg, rgba(255, 251, 247, 0.98), rgba(255, 245, 235, 0.96));
}

.assist-result {
  display: grid;
  gap: 12px;
  margin-top: 14px;
}

.assist-summary,
.recommend-card,
.candidate-item,
.structured-card {
  border-radius: 16px;
  border: 1px solid rgba(214, 132, 70, 0.1);
  background: rgba(255, 255, 255, 0.86);
}

.assist-summary {
  display: grid;
  gap: 10px;
  padding: 14px 16px;
}

.summary-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.warning-item {
  margin: 0;
}

.dialog-inline-alert {
  margin-top: 16px;
}

.connectivity-card {
  display: grid;
  gap: 10px;
  margin-top: 16px;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid rgba(43, 178, 76, 0.16);
  background: rgba(241, 251, 244, 0.92);
}

.connectivity-card.is-warning {
  border-color: rgba(233, 170, 38, 0.18);
  background: rgba(255, 249, 238, 0.95);
}

.connectivity-head {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.recommend-card,
.candidate-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
}

.recommend-copy,
.structured-command,
.stack-copy,
.warning-stack {
  display: grid;
  gap: 8px;
}

.recommend-copy,
.candidate-item > div {
  min-width: 0;
  flex: 1;
}

.recommend-title,
.structured-head {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.recommend-card code,
.structured-card code {
  display: inline-flex;
  padding: 8px 10px;
  border-radius: 12px;
  background: #fff7ef;
  color: #6f4528;
  word-break: break-all;
}

.candidate-item strong {
  display: block;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.structured-grid,
.candidate-list {
  display: grid;
  gap: 12px;
}

.param-list {
  display: grid;
  gap: 12px;
}

.param-row {
  display: grid;
  grid-template-columns: minmax(120px, 1fr) 120px 120px 90px minmax(180px, 1.2fr) auto;
  gap: 10px;
  align-items: center;
}

.structured-card {
  display: grid;
  gap: 10px;
  padding: 14px 16px;
}

.stack-copy span,
.warning-stack span,
.detected-label {
  color: #7a6758;
  font-size: 13px;
}

.warning-stack span {
  color: #b95d2d;
}

.empty-inline {
  color: #8a7765;
  font-size: 13px;
}

.advanced-block :deep(.el-collapse-item__header) {
  background: transparent;
  color: #2f241b;
  font-weight: 600;
}

.advanced-block :deep(.el-collapse-item__wrap),
.advanced-block :deep(.el-collapse-item__content) {
  background: transparent;
}

.cli-grid {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 12px;
  width: 100%;
}

.span-2 {
  grid-column: span 2;
}

@media (max-width: 1180px) {
  .toolbar-card {
    grid-template-columns: 1fr;
  }

  .tool-row {
    grid-template-columns: 32px minmax(0, 1fr) max-content;
  }

  .tool-side {
    align-items: center;
    grid-column: auto;
    width: auto;
    min-width: 100px;
  }
}

@media (max-width: 960px) {
  .hero-card,
  .toolbar-card {
    flex-direction: column;
    align-items: stretch;
  }

  .search-box {
    width: 100%;
  }

  .field-grid,
  .cli-grid {
    grid-template-columns: 1fr;
  }

  .param-row {
    grid-template-columns: 1fr;
  }

  .tool-row {
    grid-template-columns: 32px minmax(0, 1fr) max-content;
    gap: 12px;
  }

  .tool-side {
    align-items: center;
    grid-column: auto;
    justify-content: flex-end;
    min-width: 100px;
  }

  .recommend-card,
  .candidate-item,
  .panel-head {
    justify-content: flex-start;
    align-items: flex-start;
    flex-direction: column;
  }

  .tool-side .action-row {
    justify-content: flex-end;
    align-items: center;
    flex-direction: row;
  }

  .span-2 {
    grid-column: auto;
  }
}

@media (max-width: 760px) {
  .tool-page {
    padding: 16px;
  }

  .tool-workbench-card {
    padding: 18px;
  }

  .workbench-head {
    align-items: center;
    flex-direction: row;
  }

  .workbench-actions {
    justify-content: flex-end;
  }

  .tool-row {
    grid-template-columns: 30px minmax(0, 1fr);
    align-items: flex-start;
    padding: 12px 0;
  }

  .tool-title-row {
    flex-wrap: wrap;
    gap: 4px 10px;
  }

  .tool-name {
    max-width: 100%;
  }

  .tool-description {
    flex-basis: 100%;
  }

  .tool-side {
    grid-column: 2;
    justify-content: flex-start;
    min-width: 0;
  }

  .tool-row-info,
  .tool-inline-config {
    grid-column: 1 / -1;
    margin-left: 0;
  }

  .tool-row-info {
    grid-template-columns: 1fr;
  }

  .tool-info-card {
    grid-template-columns: 1fr;
    gap: 4px;
  }
}
</style>










