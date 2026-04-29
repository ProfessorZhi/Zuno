<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MoreFilled, Plus, Refresh, Search, Upload } from '@element-plus/icons-vue'
import pluginIcon from '../../assets/plugin.svg'
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
import { getConfigAPI, type RuntimeConfigPayload } from '../../apis/configuration'
import { safeDisplayText } from '../../utils/display-text'
import { useUserStore } from '../../store/user'

interface ToolItem extends ToolResponse {
  system_tool_kind?: RuntimeConfigPayload['system_tools'][number]['tool_kind']
  system_tool_kind_label?: RuntimeConfigPayload['system_tools'][number]['tool_kind_label']
  system_status?: RuntimeConfigPayload['system_tools'][number]['status']
  runtime_status?: ToolConnectivityResponse['status']
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

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const statusRefreshing = ref<Record<string, boolean>>({})
const keyword = ref('')
const activeTab = ref<'all' | 'custom'>('all')
const tools = ref<ToolItem[]>([])
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
const advancedSections = ref(['execution'])
const apiAdvancedSections = ref<string[]>([])

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

const statusToneMap: Record<string, string> = { ready: 'is-ready', needs_config: 'is-warning', runtime_input: 'is-neutral', missing_dependency: 'is-danger' }
const getResolvedStatus = (tool: ToolItem) => tool.runtime_status || tool.system_status || null
const isSystemTool = (tool: ToolItem) => tool.user_id === '0'
const getToolRuntimeLabel = (tool: ToolItem) => (isSystemTool(tool) ? (tool.system_tool_kind === 'remote_api' ? 'API' : 'CLI') : tool.runtime_type === 'cli' ? 'CLI' : 'API')
const getToolStatusLabel = (tool: ToolItem) => getResolvedStatus(tool)?.label || '待检测'
const getToolStatusTone = (tool: ToolItem) => statusToneMap[getResolvedStatus(tool)?.code || ''] || 'is-neutral'
const getToolSummary = (tool: ToolItem) => safeDisplayText(tool.description) || (isSystemTool(tool) ? (getToolRuntimeLabel(tool) === 'API' ? '通过远程接口提供能力。' : '通过本地命令、内置程序或系统依赖运行。') : '暂无说明')
const getToolHints = (tool: ToolItem) => (isSystemTool(tool) ? tool.system_tool_kind === 'smtp_protocol' ? ['多凭证'] : tool.system_tool_kind === 'remote_api' ? ['远程配置'] : ['本地运行'] : [])
const getPrimaryActionLabel = (tool: ToolItem) => (!isSystemTool(tool) ? '编辑' : tool.system_tool_kind === 'local_dependency' || tool.system_tool_kind === 'public_data_source' ? '查看' : '配置')
const isStatusRefreshing = (tool: ToolItem) => !!statusRefreshing.value[tool.tool_id]

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
const addSimpleApiParam = () => simpleApiParams.value.push({ name: '', in: 'query', required: false, type: 'string', description: '' })
const removeSimpleApiParam = (index: number) => simpleApiParams.value.splice(index, 1)

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
        system_status: meta?.status?.code === 'ready' ? undefined : meta?.status,
      }
    })
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
  resetDialog()
  dialogVisible.value = true
  try {
    const response = await getDefaultToolLogoAPI()
    form.value.logo_url = response.data.data.logo_url || ''
  } catch {}
}

const openEditDialog = (tool: ToolItem) => {
  resetDialog()
  isEditMode.value = true
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

const handlePrimaryAction = (tool: ToolItem) => isSystemTool(tool) ? router.push({ path: '/configuration', query: { tool: tool.name } }) : openEditDialog(tool)
const handleToolCommand = (tool: ToolItem, command: 'edit' | 'delete' | 'config') => command === 'delete' ? handleDelete(tool) : command === 'config' ? router.push({ path: '/configuration', query: { tool: tool.name } }) : openEditDialog(tool)

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

const validateToolForm = () => {
  if (!form.value.display_name.trim()) form.value.display_name = form.value.runtime_type === 'remote_api' ? guessDisplayNameFromEndpoint(remoteApiAssistForm.value.endpoint_url || extractUrls(remoteApiAssistForm.value.docs_urls_text)[0] || '') : ''
  if (!form.value.display_name.trim()) return ElMessage.warning('请先填写工具名称'), false
  if (!form.value.description.trim()) return ElMessage.warning('请先填写工具描述，或点击智能填表让 Agent 生成描述'), false
  if (form.value.runtime_type === 'cli' && !form.value.cli_config.command?.trim()) return ElMessage.warning('CLI 工具至少需要一个启动命令'), false
  if (form.value.runtime_type === 'cli' && requiresToolDir.value && !form.value.cli_config.tool_dir?.trim()) return ElMessage.warning('当前来源类型需要填写本地目录'), false
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
  if (!(await ensureRemoteApiDraftReady()) || !validateToolForm()) return
  dialogLoading.value = true
  try {
    const payload = buildToolPayload()
    const response = isEditMode.value && form.value.tool_id ? await updateToolAPI({ tool_id: form.value.tool_id, ...payload }) : await createToolAPI(payload)
    if (response.data.status_code !== 200) throw new Error(response.data.status_message || '保存工具失败')
    ElMessage.success(isEditMode.value ? '工具已更新' : '工具已创建')
    dialogVisible.value = false
    await fetchTools()
  } catch (error: any) {
    ElMessage.error(getErrorMessage(error, '保存工具失败'))
  } finally {
    dialogLoading.value = false
  }
}

const handleDelete = async (tool: ToolItem) => {
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
        <div class="eyebrow">TOOLS</div>
        <h1>工具管理</h1>
        <p>系统工具负责平台内置能力，自定义工具负责扩展能力。普通用户只管理自己的工具，管理员可以维护系统工具。</p>
      </div>
      <div class="hero-actions">
        <el-button :icon="Refresh" @click="fetchTools">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新建工具</el-button>
      </div>
    </section>

    <section class="toolbar-card">
      <el-tabs v-model="activeTab" class="tool-tabs">
        <el-tab-pane label="全部工具" name="all" />
        <el-tab-pane label="我的工具" name="custom" />
      </el-tabs>
      <el-input v-model="keyword" placeholder="搜索工具名称、描述或运行方式" clearable class="search-box">
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </section>

    <section class="list-card" v-loading="loading">
      <div v-if="!visibleTools.length" class="empty-state">暂无工具</div>
      <article v-for="row in visibleTools" :key="row.tool_id" class="tool-row">
        <div class="logo-wrap"><img :src="row.logo_url || pluginIcon" :alt="row.display_name" /></div>
        <div class="tool-main">
          <div class="tool-name-line">
            <span class="tool-name" :title="row.display_name">{{ row.display_name }}</span>
            <span v-if="isSystemTool(row)" class="meta-badge">系统工具</span>
          </div>
          <div class="tool-description" :title="getToolSummary(row)">{{ getToolSummary(row) }}</div>
          <div class="tool-hints">
            <span class="hint-chip">{{ getToolRuntimeLabel(row) }}</span>
            <span v-for="hint in getToolHints(row)" :key="hint" class="hint-chip">{{ hint }}</span>
          </div>
        </div>
        <div class="tool-side">
          <div class="status-pill" :class="getToolStatusTone(row)">
            <span class="status-dot" />
            <span>{{ getToolStatusLabel(row) }}</span>
          </div>
          <div class="action-row">
            <el-button class="primary-action" @click="handlePrimaryAction(row)">{{ getPrimaryActionLabel(row) }}</el-button>
            <el-button class="secondary-action" plain :loading="isStatusRefreshing(row)" @click="refreshToolStatus(row)">检测</el-button>
            <el-dropdown trigger="click" @command="(command) => handleToolCommand(row, command as 'edit' | 'delete' | 'config')">
              <el-button class="ghost-action" :icon="MoreFilled" circle />
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item v-if="isSystemTool(row)" command="config">配置</el-dropdown-item>
                  <el-dropdown-item command="edit">编辑</el-dropdown-item>
                  <el-dropdown-item command="delete">删除</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </article>
    </section>

    <el-dialog v-model="dialogVisible" :title="isEditMode ? '编辑工具' : '新建工具'" width="min(940px, calc(100vw - 32px))">
      <el-form label-position="top" class="tool-form">
        <el-form-item label="工具图标">
          <div class="logo-upload-row">
            <div class="logo-preview"><img :src="form.logo_url || pluginIcon" alt="工具图标预览" /></div>
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
            <el-input v-model="form.description" type="textarea" :rows="3" placeholder="一句话说明这个工具负责什么能力，供 Agent 判断何时调用。" />
          </el-form-item>
        </div>

        <template v-if="form.runtime_type === 'remote_api'">
          <section class="nested-panel">
            <div class="panel-head api-assist-head">
              <div>
                <h3>远程 API 接入</h3>
                <p>默认只填文档地址和 API Key；接口地址、认证方式、字段名和参数由 Agent 从文档里自动推断。</p>
              </div>
              <div class="panel-actions">
                <el-button type="primary" plain :loading="remoteApiAssistLoading" @click="() => previewRemoteApi()">智能填表</el-button>
                <el-button plain :loading="toolConnectivityLoading" @click="testToolConnectivity">测试连通性</el-button>
              </div>
            </div>

            <div class="field-grid">
              <el-form-item label="文档地址（必填，可多条）" class="span-2" required>
                <el-input v-model="remoteApiAssistForm.docs_urls_text" type="textarea" :rows="3" placeholder="每行一个文档地址，例如：https://docs.apilayer.com/ipstack/docs/quickstart-guide" />
              </el-form-item>
              <el-form-item label="API Key（必填）" class="span-2" required>
                <el-input v-model="form.auth_token" type="textarea" :rows="3" placeholder="只填服务商给你的 API Key，Agent 会判断它应放在 Query、Header 还是 Bearer 里。" />
              </el-form-item>
              <el-form-item label="接口地址（可选）" class="span-2">
                <el-input v-model="remoteApiAssistForm.endpoint_url" placeholder="文档里找不到接口地址时再填，例如：https://api.ipstack.com/check" />
              </el-form-item>
            </div>

            <el-alert v-if="remoteApiAssistError" type="error" :closable="false" :title="remoteApiAssistError" />
            <el-alert v-else-if="remoteApiAssistResult" type="success" :closable="false" :title="remoteApiAssistSummary || '已生成 API 草稿，可继续微调。'" />
            <el-alert v-if="remoteApiAssistResult && requiredSimpleApiParams.length && probeArgNames" type="info" :closable="false" :title="`Agent 已识别出必填业务参数：${requiredSimpleApiParamNames}，并生成测试参数：${probeArgNames}。连通性检测会带这些示例值发起真实请求。`" />
            <el-alert v-else-if="remoteApiAssistResult && requiredSimpleApiParams.length" type="warning" :closable="false" :title="`Agent 已识别出必填业务参数：${missingProbeParamNames || requiredSimpleApiParamNames}，但没有找到可靠测试值。连通性检测会停在“缺少测试参数”，不会伪装成成功。`" />
            <div v-if="remoteApiAssistResult?.warnings?.length" class="warning-stack api-warning-stack">
              <span v-for="warning in remoteApiAssistResult.warnings" :key="warning">{{ warning }}</span>
            </div>

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
                    <el-form-item label="认证方式（自动识别，可选）">
                      <el-select v-model="form.auth_type" placeholder="由 Agent 自动识别">
                        <el-option label="无认证" value="" />
                        <el-option label="Bearer Token" value="bearer" />
                        <el-option label="Basic Auth" value="basic" />
                        <el-option label="API Key（Query）" value="api_key_query" />
                        <el-option label="API Key（Header）" value="api_key_header" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="认证字段名（自动识别，可选）"><el-input v-model="form.auth_key_name" placeholder="例如：access_key / api_key / x-api-key" /></el-form-item>
                    <el-form-item label="curl 示例" class="span-2"><el-input v-model="remoteApiAssistForm.sample_curl" type="textarea" :rows="3" placeholder="可选。直接贴一段 curl，Agent 更容易识别认证方式和参数。" /></el-form-item>
                    <el-form-item label="Base URL"><el-input v-model="form.simple_api_config.base_url" placeholder="例如：https://api.ipstack.com" /></el-form-item>
                    <el-form-item label="路径"><el-input v-model="form.simple_api_config.path" placeholder="例如：/{ip} 或 /check" /></el-form-item>
                    <el-form-item label="请求方法">
                      <el-select v-model="form.simple_api_config.method">
                        <el-option label="GET" value="GET" /><el-option label="POST" value="POST" /><el-option label="PUT" value="PUT" /><el-option label="PATCH" value="PATCH" /><el-option label="DELETE" value="DELETE" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="operationId"><el-input v-model="form.simple_api_config.operation_id" placeholder="例如：lookupIpLocation" /></el-form-item>
                    <el-form-item label="摘要" class="span-2"><el-input v-model="form.simple_api_config.summary" placeholder="一句话告诉 Agent 这个接口做什么。" /></el-form-item>
                    <el-form-item label="接口说明" class="span-2"><el-input v-model="form.simple_api_config.description" type="textarea" :rows="3" placeholder="补充参数、返回值和适用场景，帮助 Agent 更准确调用。" /></el-form-item>
                  </div>
                  <section class="nested-panel">
                    <div class="panel-head api-assist-head"><div><h3>请求参数</h3><p>列出模型运行时需要填写的 query、path、header 参数，后端会转换成 OpenAPI。</p></div><el-button plain @click="addSimpleApiParam">添加参数</el-button></div>
                    <div v-if="simpleApiParams.length" class="param-list">
                      <div v-for="(param, index) in simpleApiParams" :key="`param-${index}`" class="param-row">
                        <el-input v-model="param.name" placeholder="参数名，例如 ip / city" />
                        <el-select v-model="param.in"><el-option label="query" value="query" /><el-option label="path" value="path" /><el-option label="header" value="header" /></el-select>
                        <el-select v-model="param.type"><el-option label="string" value="string" /><el-option label="number" value="number" /><el-option label="integer" value="integer" /><el-option label="boolean" value="boolean" /></el-select>
                        <el-switch v-model="param.required" inline-prompt active-text="必填" inactive-text="可选" />
                        <el-input v-model="param.description" placeholder="参数说明" />
                        <el-button text type="danger" @click="removeSimpleApiParam(index)">删除</el-button>
                      </div>
                    </div>
                    <div v-else class="empty-inline">还没有参数。纯 GET 检查接口可以先不填，需要路径或查询变量时再添加。</div>
                  </section>
                </template>
                <template v-else><el-form-item label="OpenAPI Schema"><el-input v-model="form.openapi_schema" type="textarea" :rows="16" placeholder="粘贴完整 OpenAPI Schema。适合已有 Swagger/OpenAPI 文件时直接接入。" /></el-form-item></template>
              </el-collapse-item>
            </el-collapse>
          </section>
        </template>

        <template v-else>
          <div class="cli-shell">
            <section class="cli-panel">
              <div class="panel-head"><div><h3>来源</h3><p>先告诉 Zuno 这个 CLI 从哪里来，再决定安装和运行方式。</p></div><span class="source-pill">{{ currentCliSourceOption.label }}</span></div>
              <div class="field-grid">
                <el-form-item label="CLI 来源类型"><el-select v-model="form.cli_config.source_type"><el-option v-for="item in cliSourceOptions" :key="item.value" :label="item.label" :value="item.value" /></el-select></el-form-item>
                <el-form-item v-if="currentSourceType !== 'executable'" :label="cliPathLabel"><el-input v-model="form.cli_config.tool_dir" :placeholder="cliPathPlaceholder" /></el-form-item>
                <el-form-item v-if="currentSourceType === 'executable'" label="可执行文件路径"><el-input v-model="form.cli_config.command" :placeholder="commandPlaceholder" /></el-form-item>
                <el-form-item v-if="['github_repo', 'npm_package', 'python_package'].includes(currentSourceType)" :label="installSourceLabel"><el-input v-model="form.cli_config.install_source" :placeholder="installSourcePlaceholder" /></el-form-item>
              </div>
              <div class="source-intro"><strong>{{ currentCliSourceOption.label }}</strong><p>{{ currentCliSourceOption.helper }}</p></div>
            </section>

            <section class="cli-panel">
              <div class="panel-head"><div><h3>运行方式</h3><p>这里保留真正决定执行结果的核心字段，其他细节放到高级配置。</p></div></div>
              <div class="field-grid">
                <el-form-item v-if="currentSourceType !== 'executable'" label="启动命令"><el-input v-model="form.cli_config.command" :placeholder="commandPlaceholder" /></el-form-item>
                <el-form-item label="参数模板"><el-input v-model="form.cli_config.args_template" placeholder="例如：--input {{input}} --format json" /></el-form-item>
                <el-form-item label="安装命令"><el-input v-model="form.cli_config.install_command" placeholder="例如：npm dlx @playwright/cli@latest 或 uv tool install ..." /></el-form-item>
              </div>
            </section>

            <section class="cli-panel assist-panel">
              <div class="panel-head"><div><h3>Agent assist</h3><p>给 GitHub、文档或本地路径，Agent 帮你归纳安装方式、启动命令和 CLI 建议。</p></div><el-button type="primary" plain :loading="cliPreviewLoading" @click="previewCli">分析并给建议</el-button></div>
              <div class="hint-row"><span v-for="hint in sourceAssistHints" :key="hint" class="hint-chip soft">{{ hint }}</span></div>
              <div class="field-grid">
                <el-form-item label="GitHub 链接"><el-input v-model="assistForm.github_url" placeholder="例如：https://github.com/org/repo" /></el-form-item>
                <el-form-item label="文档链接"><el-input v-model="assistForm.docs_url" placeholder="例如：https://tool.docs.dev/get-started" /></el-form-item>
                <el-form-item label="本地路径"><el-input v-model="assistForm.local_path" placeholder="例如：F:\tools\repo 或 tools\cli\my-cli" /></el-form-item>
                <el-form-item label="补充说明" class="span-2"><el-input v-model="assistForm.notes" type="textarea" :rows="3" placeholder="例如：希望优先推荐 uvx，只做只读扫描，不假设全局安装。" /></el-form-item>
              </div>
              <el-alert v-if="cliPreviewError" :title="cliPreviewError" type="warning" :closable="false" />
              <div v-if="cliPreviewResult" class="assist-result">
                <div class="assist-summary"><div><strong>{{ cliPreviewResult.display_name || cliPreviewResult.suggested_name || 'Agent 已返回建议' }}</strong><p>{{ previewSummary || '已拿到结构化建议，可直接回填到表单。' }}</p></div><div class="summary-meta"><span v-if="cliPreviewResult.resolved_path" class="meta-chip">{{ cliPreviewResult.resolved_path }}</span><span v-if="cliPreviewResult.suggested_install_command" class="meta-chip">已识别安装命令</span><span v-if="cliPreviewResult.suggested_healthcheck_command" class="meta-chip">已识别健康检查</span></div></div>
                <el-alert v-for="warning in cliPreviewResult.warnings || []" :key="warning" :title="warning" type="warning" :closable="false" class="warning-item" />
                <div v-if="previewRecommended" class="recommend-card"><div class="recommend-copy"><div class="recommend-title"><strong>推荐方案</strong><span v-if="formatConfidence(previewRecommended.confidence)" class="confidence-chip">{{ formatConfidence(previewRecommended.confidence) }}</span></div><code>{{ previewRecommended.command }} {{ formatArgsTemplate(previewRecommended.args_template) }}</code><p>{{ previewRecommended.reason || previewRecommended.notes?.[0] || '后端给出了一条优先推荐的运行方式。' }}</p></div><el-button @click="applyCliSuggestion(previewRecommended)">一键回填</el-button></div>
                <div v-if="previewStructuredCards.length" class="structured-grid"><article v-for="card in previewStructuredCards" :key="card.id" class="structured-card"><div class="structured-head"><strong>{{ card.title }}</strong><span v-if="formatConfidence(card.confidence)" class="confidence-chip">{{ formatConfidence(card.confidence) }}</span></div><p>{{ card.summary }}</p><div v-if="card.payload.command" class="structured-command"><code>{{ card.payload.command }} {{ formatArgsTemplate(card.payload.args_template) }}</code></div><div v-if="card.references.length" class="reference-row"><span v-for="reference in card.references" :key="reference" class="meta-chip">{{ reference }}</span></div><div v-if="card.notes.length" class="stack-copy"><span v-for="note in card.notes" :key="note">{{ note }}</span></div><div v-if="card.warnings.length" class="warning-stack"><span v-for="warning in card.warnings" :key="warning">{{ warning }}</span></div><el-button size="small" @click="applyCliSuggestion(card.payload)">应用这条建议</el-button></article></div>
                <div v-if="previewCandidates.length > 1" class="candidate-list"><article v-for="item in previewCandidates.slice(1)" :key="`${item.command}-${formatArgsTemplate(item.args_template)}-${item.source || ''}`" class="candidate-item"><div><strong>{{ item.command }} {{ formatArgsTemplate(item.args_template) }}</strong><p>{{ item.reason || item.notes?.[0] || '备选命令候选。' }}</p></div><el-button size="small" @click="applyCliSuggestion(item)">采用</el-button></article></div>
                <div v-if="detectedFiles.length" class="detected-files"><span class="detected-label">识别到的关键文件</span><span v-for="file in detectedFiles" :key="file" class="meta-chip">{{ file }}</span></div>
              </div>
            </section>

            <el-collapse v-model="advancedSections" class="advanced-block">
              <el-collapse-item title="高级配置" name="execution">
                <div class="field-grid">
                  <el-form-item label="健康检查命令"><div class="field-stack"><el-input v-model="form.cli_config.healthcheck_command" placeholder="例如：mycli --help 或 python main.py --version" /><el-button plain :loading="toolConnectivityLoading" @click="testToolConnectivity">测试连通性</el-button></div></el-form-item>
                  <el-form-item label="凭证模式"><el-select v-model="form.cli_config.credential_mode"><el-option label="无需凭证" value="none" /><el-option label="单份凭证" value="single" /><el-option label="多份凭证 / 多 profile" value="profiles" /></el-select></el-form-item>
                  <el-form-item label="工作目录"><div class="field-stack"><el-select v-model="form.cli_config.cwd_mode"><el-option label="使用工具目录" value="tool_dir" /><el-option label="工作区目录" value="workspace" /><el-option label="自定义目录" value="custom" /></el-select><el-input v-if="form.cli_config.cwd_mode === 'custom'" v-model="form.cli_config.cwd" placeholder="填写执行时的工作目录" /></div></el-form-item>
                  <el-form-item label="超时时间（毫秒）"><el-input-number v-model="form.cli_config.timeout_ms" :min="1000" :step="1000" /></el-form-item>
                  <el-form-item label="接入备注" class="span-2"><el-input v-model="form.cli_config.install_notes" type="textarea" :rows="3" placeholder="补充平台差异、依赖说明、凭证获取方式或运行约束。" /></el-form-item>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
        </template>
      </el-form>

      <el-alert v-if="toolConnectivityError" :title="toolConnectivityError" type="warning" :closable="false" class="dialog-inline-alert" />
      <div v-if="toolConnectivityResult" class="connectivity-card" :class="{ 'is-warning': !toolConnectivityResult.ok }">
        <div class="connectivity-head"><strong>{{ toolConnectivityResult.summary }}</strong><span class="meta-badge">{{ toolConnectivityResult.runtime_type === 'cli' ? 'CLI' : 'API' }}</span></div>
        <div v-if="toolConnectivityResult.details?.length" class="stack-copy"><span v-for="detail in toolConnectivityResult.details" :key="detail">{{ detail }}</span></div>
        <div v-if="toolConnectivityResult.warnings?.length" class="warning-stack"><span v-for="warning in toolConnectivityResult.warnings" :key="warning">{{ warning }}</span></div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="submitDialog">{{ isEditMode ? '保存修改' : '创建工具' }}</el-button>
      </template>
    </el-dialog>
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
.list-card {
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

.eyebrow {
  font-size: 12px;
  letter-spacing: 0.16em;
  color: #be6d38;
}

.hero-card h1 {
  margin: 12px 0 10px;
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

.toolbar-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(240px, 360px);
  gap: 18px;
  align-items: center;
}

.tool-tabs {
  min-width: 0;
}

.search-box {
  width: 100%;
}

.list-card {
  padding: 8px 0;
  overflow: hidden;
}

.empty-state {
  padding: 44px 24px;
  text-align: center;
  color: #8b7868;
}

.tool-row {
  display: grid;
  grid-template-columns: 56px minmax(0, 1fr) minmax(132px, auto);
  gap: 18px;
  align-items: flex-start;
  padding: 20px 24px;
  border-bottom: 1px solid rgba(214, 132, 70, 0.08);
  transition: background 160ms ease, transform 160ms ease;
}

.tool-row:last-child {
  border-bottom: none;
}

.tool-row:hover {
  background: rgba(255, 249, 241, 0.72);
}

.logo-wrap {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  overflow: hidden;
  background: linear-gradient(180deg, #fff, #f7f1e8);
  border: 1px solid rgba(214, 132, 70, 0.12);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9);
}

.logo-wrap img,
.logo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tool-main {
  min-width: 0;
}

.tool-name-line {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.tool-name {
  display: -webkit-box;
  font-size: 18px;
  font-weight: 700;
  color: #32261d;
  line-height: 1.28;
  overflow: hidden;
  word-break: break-word;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
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
  display: -webkit-box;
  color: #615446;
  line-height: 1.65;
  font-size: 14px;
  margin-bottom: 8px;
  max-width: 640px;
  overflow: hidden;
  word-break: break-word;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.tool-hints,
.hint-row,
.reference-row,
.detected-files {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hint-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(247, 241, 232, 0.8);
  color: #8a7765;
  font-size: 12px;
}

.hint-chip.soft {
  background: rgba(255, 248, 238, 0.95);
}

.tool-side {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
  min-width: 0;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  background: #f5f5f5;
  color: #666;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: currentColor;
  opacity: 0.95;
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
  gap: 10px;
  flex-wrap: wrap;
}

.primary-action {
  min-width: 88px;
  border-radius: 12px;
  border: none;
  background: #2a2622;
  color: white;
  flex-shrink: 0;
}

.primary-action:hover {
  background: #1f1c18;
  color: white;
}

.secondary-action {
  min-width: 78px;
  border-radius: 12px;
  border-color: rgba(214, 132, 70, 0.2);
  color: #8b5a33;
  background: rgba(255, 252, 247, 0.94);
  flex-shrink: 0;
}

.ghost-action {
  border-radius: 12px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  color: #6f6257;
  background: white;
  flex-shrink: 0;
}

.logo-editor {
  display: flex;
  gap: 16px;
  align-items: center;
}

.logo-preview {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  overflow: hidden;
  border: 1px solid rgba(214, 132, 70, 0.16);
  background: #f8efe4;
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
  margin-top: 16px;
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
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 16px;
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
  grid-column: 1 / -1;
}

@media (max-width: 1180px) {
  .toolbar-card {
    grid-template-columns: 1fr;
  }

  .tool-row {
    grid-template-columns: 56px minmax(0, 1fr);
  }

  .tool-side {
    align-items: flex-start;
    grid-column: 2;
    width: 100%;
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
  .cli-grid,
  .tool-row {
    grid-template-columns: 1fr;
  }

  .param-row {
    grid-template-columns: 1fr;
  }

  .tool-row {
    grid-template-columns: 56px minmax(0, 1fr);
  }

  .tool-side {
    align-items: flex-start;
    grid-column: 1 / -1;
  }

  .action-row,
  .recommend-card,
  .candidate-item,
  .panel-head {
    justify-content: flex-start;
    align-items: flex-start;
    flex-direction: column;
  }

  .span-2 {
    grid-column: auto;
  }
}
</style>










