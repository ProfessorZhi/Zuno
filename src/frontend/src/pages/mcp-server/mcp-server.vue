<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Delete, Edit, Plus, Search, Setting } from '@element-plus/icons-vue'
import defaultMcpLogo from '../../assets/mcp.svg'
import emptyDataIcon from '../../assets/dashboard/空数据.svg'
import {
  createMCPServerAPI,
  deleteMCPServerAPI,
  getDefaultMCPLogoAPI,
  getMCPServersAPI,
  getMCPToolsAPI,
  getMCPUserConfigAPI,
  testMCPUserConfigAPI,
  updateMCPServerAPI,
  updateMCPUserConfigAPI,
  type MCPServer,
} from '../../apis/mcp-server'
import { useUserStore } from '../../store/user'
import ZunoMiniPager from '../../components/ZunoMiniPager.vue'

type TransportType = 'stdio' | 'streamable_http'

interface KeyValueItem {
  key: string
  value: string
}

interface StructuredServerForm {
  server_name: string
  logo_url: string
  transport: TransportType
  command: string
  args: string[]
  env: KeyValueItem[]
  env_passthrough: string[]
  cwd: string
  url: string
  headers: KeyValueItem[]
}

interface TestStatusView {
  code: 'success' | 'failed' | 'untested'
  label: string
  type: 'success' | 'danger' | 'info'
  detail: string
  tools: string[]
  testedAt?: string | null
}

interface MCPServerView extends MCPServer {
  displayStatus: TestStatusView
}

const userStore = useUserStore()
const loading = ref(false)
const savingServer = ref(false)
const savingConfig = ref(false)
const testingConfig = ref(false)
const toolsLoading = ref(false)
const keyword = ref('')
const LIST_PAGE_SIZE = 6
const listPage = ref(1)

const serverDialogVisible = ref(false)
const configDialogVisible = ref(false)
const toolsDialogVisible = ref(false)

const isEditMode = ref(false)
const currentServer = ref<MCPServerView | null>(null)
const toolsDialogTitle = ref('')
const currentTools = ref<any[]>([])

const servers = ref<MCPServerView[]>([])
const defaultLogoUrl = ref(defaultMcpLogo)
const visibleServers = computed(() => {
  const search = keyword.value.trim().toLowerCase()
  const list = [...servers.value]
  if (!search) return list
  return list.filter((server) => [
    server.server_name,
    server.transport,
    connectionModeText(server),
    connectionHint(server),
    server.displayStatus.label,
  ].join(' ').toLowerCase().includes(search))
})
const paginatedServers = computed(() => visibleServers.value.slice(
  (listPage.value - 1) * LIST_PAGE_SIZE,
  listPage.value * LIST_PAGE_SIZE,
))

const serverForm = reactive<StructuredServerForm>({
  server_name: '',
  logo_url: '',
  transport: 'stdio',
  command: '',
  args: [],
  env: [],
  env_passthrough: [],
  cwd: '',
  url: '',
  headers: [],
})

const personalConfigValues = ref<Record<string, string>>({})
const currentTestStatus = ref<TestStatusView>(buildStatus())

const isAdmin = computed(() => String(userStore.userInfo?.id || '') === '1')

function buildStatus(input?: MCPServer['test_status'] | null): TestStatusView {
  const code = input?.code || 'untested'
  const rawDetail = input?.detail || ''
  const detailLooksBroken = /^[?？\s]+$/.test(rawDetail) || rawDetail.includes(String.fromCharCode(0xfffd))
  const safeDetail = detailLooksBroken ? '' : rawDetail
  if (code === 'success') {
    return {
      code,
      label: '测试通过',
      type: 'success',
      detail: safeDetail || '连接测试通过。',
      tools: input?.tools || [],
      testedAt: input?.tested_at,
    }
  }
  if (code === 'failed') {
    return {
      code,
      label: '测试失败',
      type: 'danger',
      detail: safeDetail || '连接测试失败。',
      tools: input?.tools || [],
      testedAt: input?.tested_at,
    }
  }
  return {
    code: 'untested',
    label: '未测试',
    type: 'info',
    detail: safeDetail || '还没有执行过连接测试。',
    tools: input?.tools || [],
    testedAt: input?.tested_at,
  }
}

function createEmptyKeyValue(): KeyValueItem {
  return { key: '', value: '' }
}

function createDefaultServerForm(): StructuredServerForm {
  return {
    server_name: '',
    logo_url: defaultLogoUrl.value,
    transport: 'stdio',
    command: '',
    args: [],
    env: [],
    env_passthrough: [],
    cwd: '',
    url: '',
    headers: [],
  }
}

function resetServerForm() {
  Object.assign(serverForm, createDefaultServerForm())
}

function normalizeRows<T extends string | KeyValueItem>(rows: T[], emptyFactory: () => T): T[] {
  const filtered = rows.filter((item) => {
    if (typeof item === 'string') return item.trim().length > 0
    return item.key.trim().length > 0 || item.value.trim().length > 0
  })
  return filtered.length > 0 ? filtered : [emptyFactory()]
}

function keyValueArrayToObject(rows: KeyValueItem[]) {
  return rows.reduce<Record<string, string>>((acc, row) => {
    const key = row.key.trim()
    if (key) acc[key] = row.value
    return acc
  }, {})
}

function parseImportedConfig(server: MCPServer | null) {
  const imported = server?.imported_config || {}
  const serversMap = imported?.mcpServers || {}
  const firstName = Object.keys(serversMap)[0]
  return firstName ? serversMap[firstName] || {} : {}
}

function fillServerForm(server?: MCPServer | null) {
  const next = createDefaultServerForm()
  if (server) {
    const config = parseImportedConfig(server)
    next.server_name = server.server_name || ''
    next.logo_url = server.logo_url || defaultLogoUrl.value
    next.transport = config.type === 'streamable_http' ? 'streamable_http' : 'stdio'
    next.command = config.command || ''
    next.args = Array.isArray(config.args) && config.args.length > 0 ? [...config.args] : []
    next.env =
      config.env && typeof config.env === 'object'
        ? Object.entries(config.env).map(([key, value]) => ({ key, value: String(value ?? '') }))
        : []
    next.env_passthrough =
      Array.isArray(config.env_passthrough) && config.env_passthrough.length > 0
        ? config.env_passthrough.map((item: unknown) => String(item))
        : []
    next.cwd = config.cwd || ''
    next.url = config.url || server.url || ''
    next.headers =
      config.headers && typeof config.headers === 'object'
        ? Object.entries(config.headers).map(([key, value]) => ({ key, value: String(value ?? '') }))
        : []
  }
  Object.assign(serverForm, next)
}

function buildImportedConfigFromForm() {
  const serverName = serverForm.server_name.trim() || 'mcp-server'
  if (serverForm.transport === 'stdio') {
    const command = serverForm.command.trim()
    if (!command) throw new Error('请填写 STDIO 启动命令。')
    const args = normalizeRows(serverForm.args, () => '').filter((item) => item.trim())
    return {
      mcpServers: {
        [serverName]: {
          type: 'stdio',
          command,
          args,
          env: keyValueArrayToObject(normalizeRows(serverForm.env, createEmptyKeyValue)),
          env_passthrough: normalizeRows(serverForm.env_passthrough, () => '').filter((item) => item.trim()),
          cwd: serverForm.cwd.trim() || undefined,
        },
      },
    }
  }

  const url = serverForm.url.trim()
  if (!url) throw new Error('请填写流式 HTTP 地址。')
  return {
    mcpServers: {
      [serverName]: {
        type: 'streamable_http',
        url,
        headers: keyValueArrayToObject(normalizeRows(serverForm.headers, createEmptyKeyValue)),
      },
    },
  }
}

function syncServerStatus(serverId: string, status?: MCPServer['test_status'] | null) {
  const target = servers.value.find((item) => item.mcp_server_id === serverId)
  if (!target) return
  target.test_status = status || undefined
  target.displayStatus = buildStatus(status)
}

async function loadDefaultLogo() {
  try {
    const response = await getDefaultMCPLogoAPI()
    if (response.data.status_code === 200) {
      defaultLogoUrl.value = response.data.data.logo_url || defaultMcpLogo
    }
  } catch (error) {
    console.warn('加载默认 MCP 图标失败', error)
    defaultLogoUrl.value = defaultMcpLogo
  }
}

function handleLogoError(event: Event) {
  const target = event.target as HTMLImageElement
  if (target && target.src !== defaultMcpLogo) {
    target.src = defaultMcpLogo
  }
}

async function fetchServers() {
  loading.value = true
  try {
    const response = await getMCPServersAPI()
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '加载 MCP 服务失败')
    }
    servers.value = (response.data.data || []).map((server) => ({
      ...server,
      displayStatus: buildStatus(server.test_status),
    }))
  } catch (error: any) {
    console.error('fetchServers failed', error)
    ElMessage.error(error.message || '加载 MCP 服务失败')
  } finally {
    loading.value = false
  }
}

function openCreateServerDialog() {
  if (serverDialogVisible.value && !isEditMode.value) {
    serverDialogVisible.value = false
    return
  }
  configDialogVisible.value = false
  toolsDialogVisible.value = false
  isEditMode.value = false
  currentServer.value = null
  resetServerForm()
  serverDialogVisible.value = true
}

function openEditServerDialog(server: MCPServerView) {
  if (server.user_id === '0' && !isAdmin.value) {
    ElMessage.warning('官方 MCP 连接定义仅管理员可编辑。')
    return
  }
  configDialogVisible.value = false
  toolsDialogVisible.value = false
  isEditMode.value = true
  currentServer.value = server
  fillServerForm(server)
  serverDialogVisible.value = true
}

function isServerDraftComplete() {
  if (!serverForm.server_name.trim()) return false
  if (serverForm.transport === 'stdio') return Boolean(serverForm.command.trim())
  return Boolean(serverForm.url.trim())
}

async function submitServerDialog() {
  if (!isServerDraftComplete()) {
    serverDialogVisible.value = false
    return
  }
  savingServer.value = true
  try {
    const imported_config = buildImportedConfigFromForm()
    const payload = {
      server_name: serverForm.server_name.trim(),
      logo_url: (serverForm.logo_url || defaultLogoUrl.value).trim(),
      imported_config,
    }
    const response =
      isEditMode.value && currentServer.value
        ? await updateMCPServerAPI({
            server_id: currentServer.value.mcp_server_id,
            name: payload.server_name,
            logo_url: payload.logo_url,
            imported_config: payload.imported_config,
          })
        : await createMCPServerAPI(payload)

    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '保存 MCP 服务失败')
    }
    ElMessage.success(isEditMode.value ? 'MCP 服务已更新。' : 'MCP 服务已创建。')
    serverDialogVisible.value = false
    await fetchServers()
  } catch (error: any) {
    console.error('submitServerDialog failed', error)
    ElMessage.error(error.message || '保存 MCP 服务失败')
  } finally {
    savingServer.value = false
  }
}

async function handleDelete(server: MCPServerView) {
  if (server.user_id === '0' && !isAdmin.value) {
    ElMessage.warning('官方 MCP 仅管理员可删除。')
    return
  }
  try {
    await ElMessageBox.confirm(`确认删除“${server.server_name}”吗？`, '删除 MCP', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      confirmButtonClass: 'el-button--danger',
    })
    const response = await deleteMCPServerAPI(server.mcp_server_id)
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '删除失败')
    }
    ElMessage.success('MCP 服务已删除。')
    await fetchServers()
  } catch (error: any) {
    if (error === 'cancel' || error === 'close') return
    console.error('deleteMCP failed', error)
    ElMessage.error(error.message || '删除失败')
  }
}

async function openToolsDialog(server: MCPServerView) {
  if (toolsDialogVisible.value && currentServer.value?.mcp_server_id === server.mcp_server_id) {
    toolsDialogVisible.value = false
    currentServer.value = null
    currentTools.value = []
    return
  }
  serverDialogVisible.value = false
  configDialogVisible.value = false
  currentServer.value = server
  toolsLoading.value = true
  toolsDialogVisible.value = true
  toolsDialogTitle.value = `${server.server_name} · 工具列表`
  currentTools.value = []
  try {
    const response = await getMCPToolsAPI(server.mcp_server_id)
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '加载工具列表失败')
    }
    currentTools.value = response.data.data || []
  } catch (error: any) {
    console.error('getMCPTools failed', error)
    ElMessage.error(error.message || '加载工具列表失败')
  } finally {
    toolsLoading.value = false
  }
}

async function openConfigDialog(server: MCPServerView) {
  if (configDialogVisible.value && currentServer.value?.mcp_server_id === server.mcp_server_id) {
    configDialogVisible.value = false
    currentServer.value = null
    return
  }
  serverDialogVisible.value = false
  toolsDialogVisible.value = false
  currentServer.value = server
  fillServerForm(server)
  personalConfigValues.value = {}
  currentTestStatus.value = buildStatus(server.test_status)
  configDialogVisible.value = true

  try {
    const response = await getMCPUserConfigAPI(server.mcp_server_id)
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '加载个人配置失败')
    }
    const data = response.data.data
    const values: Record<string, string> = {}
    ;(data?.config || []).forEach((item: any) => {
      values[item.key] = item.value || ''
    })
    personalConfigValues.value = values
    currentTestStatus.value = buildStatus(data?.test_status || server.test_status)
    syncServerStatus(server.mcp_server_id, data?.test_status || server.test_status)
  } catch (error: any) {
    console.error('openConfigDialog failed', error)
    ElMessage.error(error.message || '加载个人配置失败')
  }
}

const personalConfigFields = computed(() => currentServer.value?.config || [])

function buildPersonalConfigPayload() {
  return personalConfigFields.value.map((item: any) => ({
    key: item.key,
    label: item.label || item.key,
    value: personalConfigValues.value[item.key] || '',
  }))
}

async function persistPersonalConfig(showSuccess = true) {
  if (!currentServer.value) return
  savingConfig.value = true
  try {
    const payload = buildPersonalConfigPayload()
    const response = await updateMCPUserConfigAPI({
      server_id: currentServer.value.mcp_server_id,
      config: payload,
    })
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '保存个人配置失败')
    }
    const untested = buildStatus({
      code: 'untested',
      label: '未测试',
      detail: '配置已保存，尚未执行测试。',
      tools: [],
      tested_at: new Date().toISOString(),
    })
    currentTestStatus.value = untested
    syncServerStatus(currentServer.value.mcp_server_id, {
      code: 'untested',
      label: '未测试',
      detail: '配置已保存，尚未执行测试。',
      tools: [],
      tested_at: new Date().toISOString(),
    })
    if (showSuccess) ElMessage.success('个人配置已保存。')
  } catch (error: any) {
    console.error('persistPersonalConfig failed', error)
    ElMessage.error(error.message || '保存个人配置失败')
    throw error
  } finally {
    savingConfig.value = false
  }
}

async function testCurrentConfig() {
  if (!currentServer.value) return
  testingConfig.value = true
  try {
    if (personalConfigFields.value.length > 0) {
      await persistPersonalConfig(false)
    }
    const response = await testMCPUserConfigAPI({ server_id: currentServer.value.mcp_server_id })
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '测试失败')
    }
    const result = response.data.data
    const status = buildStatus({
      code: result.success ? 'success' : 'failed',
      label: result.success ? '测试通过' : '测试失败',
      detail: result.message,
      tools: result.tools || [],
      tested_at: new Date().toISOString(),
    })
    currentTestStatus.value = status
    syncServerStatus(currentServer.value.mcp_server_id, {
      code: status.code,
      label: status.label,
      detail: status.detail,
      tools: status.tools,
      tested_at: status.testedAt,
    })
    ElMessage.success(result.success ? '测试成功。' : '测试已执行，结果为失败。')
    await fetchServers()
  } catch (error: any) {
    console.error('testCurrentConfig failed', error)
    ElMessage.error(error.message || '测试失败')
  } finally {
    testingConfig.value = false
  }
}

function canEditServer(server: MCPServerView) {
  return server.user_id !== '0' || isAdmin.value
}

function connectionHint(server: MCPServerView) {
  if (server.user_id === '0') {
    return server.config_enabled ? '平台预置连接，需要个人参数。' : '平台预置连接，无需个人参数。'
  }
  return '自定义 MCP 连接。'
}

function connectionModeText(server: MCPServerView) {
  const config = parseImportedConfig(server)
  const type = config.type || server.type
  if (type === 'stdio') return `STDIO · ${config.command || '未设置命令'}`
  if (type === 'streamable_http') return '流式 HTTP'
  return String(type || '未知')
}

onMounted(async () => {
  await loadDefaultLogo()
  resetServerForm()
  await fetchServers()
})
</script>

<template>
  <div class="mcp-page">
    <section class="hero-card">
      <div>
        <div class="settings-title-row">
          <img :src="defaultMcpLogo" alt="MCP" class="page-icon" />
          <h2>MCP</h2>
        </div>
      </div>
      <div class="hero-actions">
        <el-button
          :class="['settings-icon-button', { 'is-create-open': serverDialogVisible && !isEditMode }]"
          type="primary"
          :icon="Plus"
          circle
          :title="serverDialogVisible && !isEditMode ? '收起新增 MCP 服务' : '添加服务器'"
          :aria-label="serverDialogVisible && !isEditMode ? '收起新增 MCP 服务' : '添加服务器'"
          @click="openCreateServerDialog"
        />
      </div>
      <div class="settings-search-row">
        <el-input v-model="keyword" clearable placeholder="搜索 MCP 服务名称或连接方式" class="search-input">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
    </section>

    <section class="table-card" v-loading="loading">
      <div v-if="!visibleServers.length && !serverDialogVisible" class="empty-state settings-empty-hint">
        <img :src="emptyDataIcon" alt="空数据" class="empty-state-icon" />
        {{ keyword ? '没有匹配到 MCP 服务，换个关键词试试看吧 (´･_･`)' : '还没有 MCP 服务，点右上角 + 接上第一条能力通道吧 (｀・ω・´)ゞ' }}
      </div>
      <div v-else class="server-list">
        <article v-for="server in paginatedServers" :key="server.mcp_server_id" class="server-row">
          <img
            class="server-logo"
            :src="server.logo_url || defaultLogoUrl"
            :alt="server.server_name"
            @error="handleLogoError"
          />
          <div class="server-main">
            <div class="server-title">
              <span>{{ server.server_name }}</span>
              <span v-if="server.user_id === '0'" class="official-tag">官方</span>
            </div>
            <div class="server-subtitle">{{ connectionModeText(server) }}</div>
            <div class="server-meta">
              <button class="meta-pill as-button" type="button" @click="openToolsDialog(server)">
                {{ server.tools?.length || 0 }} 个工具
              </button>
              <span class="meta-pill">{{ server.displayStatus.label }}</span>
              <span class="meta-pill">{{ connectionHint(server) }}</span>
            </div>
          </div>
          <div class="server-actions">
            <el-button class="mcp-icon-button primary" :icon="Setting" circle title="配置" aria-label="配置" @click="openConfigDialog(server)" />
            <el-button
              v-if="canEditServer(server)"
              class="mcp-icon-button"
              :icon="Edit"
              circle
              title="编辑"
              aria-label="编辑"
              @click="openEditServerDialog(server)"
            />
            <el-button
              v-if="canEditServer(server)"
              class="mcp-icon-button danger"
              :icon="Delete"
              circle
              title="删除"
              aria-label="删除"
              @click="handleDelete(server)"
            />
          </div>
        </article>
      </div>
      <ZunoMiniPager v-model:page="listPage" class="settings-list-pager" :total="visibleServers.length" :page-size="LIST_PAGE_SIZE" />
    </section>

    <section v-if="serverDialogVisible" class="mcp-workbench-panel">
      <header class="inline-panel-head">
        <div>
          <h3>{{ isEditMode ? '编辑 MCP 服务' : '新增 MCP 服务' }}</h3>
        </div>
        <div class="inline-panel-actions">
          <el-button class="settings-icon-button save-action" type="primary" :icon="Check" :loading="savingServer" circle title="保存" aria-label="保存" @click="submitServerDialog" />
        </div>
      </header>

      <div class="dialog-grid">
        <div class="field">
          <label>名称</label>
          <input v-model="serverForm.server_name" class="mcp-line-input" placeholder="例如：我的 MCP Server" />
        </div>
        <div class="field">
          <label>Logo URL</label>
          <input v-model="serverForm.logo_url" class="mcp-line-input" placeholder="留空则使用默认图标" />
        </div>
      </div>

      <div class="transport-switch">
        <el-radio-group v-model="serverForm.transport">
          <el-radio-button label="stdio">STDIO</el-radio-button>
          <el-radio-button label="streamable_http">流式 HTTP</el-radio-button>
        </el-radio-group>
      </div>

      <template v-if="serverForm.transport === 'stdio'">
        <div class="field">
          <label>启动命令</label>
          <input v-model="serverForm.command" class="mcp-line-input" placeholder="例如：python 或 uvx" />
        </div>
        <div class="field repeat-field">
          <label>参数</label>
          <div class="repeat-stack" :class="{ 'is-empty': serverForm.args.length === 0 }">
            <div v-for="(arg, index) in serverForm.args" :key="`arg-${index}`" class="inline-row one-col">
              <input v-model="serverForm.args[index]" class="mcp-line-input" placeholder="一项参数一行" />
              <el-button class="repeat-remove" text type="danger" :icon="Delete" circle title="删除参数" aria-label="删除参数" @click="serverForm.args.splice(index, 1)" />
            </div>
            <button class="repeat-add" type="button" @click="serverForm.args.push('')">+ 参数</button>
          </div>
        </div>
        <div class="field repeat-field">
          <label>环境变量</label>
          <div class="repeat-stack" :class="{ 'is-empty': serverForm.env.length === 0 }">
            <div v-for="(item, index) in serverForm.env" :key="`env-${index}`" class="inline-row">
              <input v-model="item.key" class="mcp-line-input" placeholder="键" />
              <input v-model="item.value" class="mcp-line-input" placeholder="值" />
              <el-button class="repeat-remove" text type="danger" :icon="Delete" circle title="删除环境变量" aria-label="删除环境变量" @click="serverForm.env.splice(index, 1)" />
            </div>
            <button class="repeat-add" type="button" @click="serverForm.env.push(createEmptyKeyValue())">+ 环境变量</button>
          </div>
        </div>
        <div class="field repeat-field">
          <label>变量传递</label>
          <div class="repeat-stack" :class="{ 'is-empty': serverForm.env_passthrough.length === 0 }">
            <div v-for="(item, index) in serverForm.env_passthrough" :key="`passthrough-${index}`" class="inline-row one-col">
              <input v-model="serverForm.env_passthrough[index]" class="mcp-line-input" placeholder="例如：OPENAI_API_KEY" />
              <el-button class="repeat-remove" text type="danger" :icon="Delete" circle title="删除传递变量" aria-label="删除传递变量" @click="serverForm.env_passthrough.splice(index, 1)" />
            </div>
            <button class="repeat-add" type="button" @click="serverForm.env_passthrough.push('')">+ 传递变量</button>
          </div>
        </div>
        <div class="field">
          <label>工作目录</label>
          <input v-model="serverForm.cwd" class="mcp-line-input" placeholder="例如：/app 或 ~/code" />
        </div>
      </template>

      <template v-else>
        <div class="field">
          <label>流式 HTTP 地址</label>
          <input v-model="serverForm.url" class="mcp-line-input" placeholder="https://example.com/mcp" />
        </div>
        <div class="field repeat-field">
          <label>请求头</label>
          <div class="repeat-stack" :class="{ 'is-empty': serverForm.headers.length === 0 }">
            <div v-for="(item, index) in serverForm.headers" :key="`header-${index}`" class="inline-row">
              <input v-model="item.key" class="mcp-line-input" placeholder="Header 名称" />
              <input v-model="item.value" class="mcp-line-input" placeholder="Header 值" />
              <el-button class="repeat-remove" text type="danger" :icon="Delete" circle title="删除请求头" aria-label="删除请求头" @click="serverForm.headers.splice(index, 1)" />
            </div>
            <button class="repeat-add" type="button" @click="serverForm.headers.push(createEmptyKeyValue())">+ 请求头</button>
          </div>
        </div>
      </template>
    </section>

    <section v-if="configDialogVisible" class="mcp-workbench-panel">
      <template v-if="currentServer">
        <header class="inline-panel-head">
          <div>
            <h3>{{ currentServer.server_name }} 配置</h3>
            <p>连接信息只读展示，个人参数和测试结果在这里维护。</p>
          </div>
          <div class="inline-panel-actions">
            <el-button class="mcp-icon-button primary" :icon="Check" :loading="testingConfig" circle title="测试" aria-label="测试" @click="testCurrentConfig" />
          </div>
        </header>

        <section class="config-section">
          <h3>连接配置</h3>
          <div class="config-summary">
            <div><strong>名称：</strong>{{ serverForm.server_name }}</div>
            <div><strong>接入方式：</strong>{{ serverForm.transport === 'stdio' ? 'STDIO' : '流式 HTTP' }}</div>
            <div><strong>连接来源：</strong>{{ currentServer.user_id === '0' ? '平台预置连接' : '自定义连接' }}</div>
          </div>

          <template v-if="serverForm.transport === 'stdio'">
            <div class="field readonly-field">
              <label>启动命令</label>
              <span class="mcp-line-value">{{ serverForm.command || '未设置' }}</span>
            </div>
            <div class="field readonly-field">
              <label>参数</label>
              <div class="readonly-list">
                <span v-for="(arg, index) in serverForm.args.filter((item) => item.trim())" :key="index" class="readonly-chip">{{ arg }}</span>
                <span v-if="serverForm.args.filter((item) => item.trim()).length === 0" class="muted-text">未设置参数</span>
              </div>
            </div>
            <div class="field readonly-field">
              <label>工作目录</label>
              <span class="mcp-line-value">{{ serverForm.cwd || '未设置' }}</span>
            </div>
          </template>
          <template v-else>
            <div class="field readonly-field">
              <label>流式 HTTP 地址</label>
              <span class="mcp-line-value">{{ serverForm.url || '未设置' }}</span>
            </div>
          </template>
        </section>

        <section class="config-section">
          <h3>个人配置</h3>
          <template v-if="personalConfigFields.length > 0">
            <div v-for="item in personalConfigFields" :key="item.key" class="field">
              <label>{{ item.label || item.key }}</label>
              <input
                v-model="personalConfigValues[item.key]"
                class="mcp-line-input"
                :type="/secret|token|key|password/i.test(item.key) ? 'password' : 'text'"
                :placeholder="`请输入 ${item.label || item.key}`"
              />
            </div>
            <div class="config-actions">
              <el-button :loading="savingConfig" @click="persistPersonalConfig()">保存我的配置</el-button>
              <el-button type="primary" :loading="testingConfig" @click="testCurrentConfig()">测试我的配置</el-button>
            </div>
          </template>
          <template v-else>
            <div class="empty-panel">当前没有需要填写的个人配置项。这是平台预置连接的正常情况，直接测试即可。</div>
            <div class="config-actions">
              <el-button type="primary" :loading="testingConfig" @click="testCurrentConfig()">测试连接</el-button>
            </div>
          </template>
        </section>

        <section class="config-section">
          <h3>测试结果</h3>
          <div class="status-row">
            <el-tag :type="currentTestStatus.type">{{ currentTestStatus.label }}</el-tag>
            <span class="muted-text" v-if="currentTestStatus.testedAt">测试时间：{{ currentTestStatus.testedAt }}</span>
          </div>
          <p class="status-detail-block">{{ currentTestStatus.detail }}</p>
          <div v-if="currentTestStatus.tools.length > 0" class="readonly-list">
            <span v-for="tool in currentTestStatus.tools" :key="tool" class="readonly-chip">{{ tool }}</span>
          </div>
        </section>
      </template>
    </section>

    <section v-if="toolsDialogVisible" class="mcp-workbench-panel">
      <header class="inline-panel-head">
        <div>
          <h3>{{ toolsDialogTitle }}</h3>
        </div>
      </header>
      <div v-loading="toolsLoading">
        <div v-if="currentTools.length === 0 && !toolsLoading" class="empty-panel">当前没有可展示的工具。</div>
        <div v-for="tool in currentTools" :key="tool.tool_name" class="tool-card">
          <div class="tool-name">{{ tool.tool_name }}</div>
          <div class="tool-description">{{ tool.tool_description || '暂无描述' }}</div>
          <div v-if="tool.tool_schema?.length" class="tool-schema">
            <div v-for="field in tool.tool_schema" :key="field.name" class="schema-row">
              <span class="schema-name">{{ field.name }}</span>
              <span class="schema-type">{{ field.type || 'string' }}</span>
              <span class="schema-required">{{ field.required ? '必填' : '可选' }}</span>
              <span class="schema-desc">{{ field.description || '无说明' }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.mcp-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-card {
  order: 0;
}

.mcp-workbench-panel {
  order: 1;
}

.table-card {
  order: 2;
}

.hero-card,
.table-card {
  padding: 28px 32px;
  border-radius: 28px;
  background: rgba(255, 252, 247, 0.96);
  border: 1px solid rgba(214, 132, 70, 0.12);
  box-shadow: 0 18px 40px rgba(140, 100, 62, 0.08);
}

.table-card {
  overflow: hidden;
}

.mcp-workbench-panel {
  display: grid;
  gap: 12px;
  padding: 18px 22px 20px;
  border-radius: 24px;
  border: 1px solid rgba(214, 132, 70, 0.14);
  background:
    linear-gradient(180deg, rgba(255, 253, 250, 0.96), rgba(255, 250, 245, 0.88)),
    rgba(255, 255, 255, 0.84);
  box-shadow: 0 16px 36px rgba(160, 95, 42, 0.08);
  animation: mcp-panel-rise 180ms cubic-bezier(.2, .8, .2, 1) both;
}

.inline-panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.inline-panel-head h3 {
  margin: 0;
  color: #2f241d;
  font-size: 17px;
}

.inline-panel-head p {
  margin: 4px 0 0;
  color: #8a7765;
  font-size: 12px;
}

.inline-panel-actions {
  display: flex;
  gap: 7px;
  min-width: max-content;
}

.inline-panel-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

@keyframes mcp-panel-rise {
  from {
    opacity: 0;
    transform: translateY(-4px) scaleY(0.99);
    transform-origin: top;
  }

  to {
    opacity: 1;
    transform: translateY(0) scaleY(1);
    transform-origin: top;
  }
}

.hero-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
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

.hero-card h2 {
  margin: 0;
  color: #2f241d;
  font-size: 34px;
}

.hero-card p {
  margin: 12px 0 0;
  color: #6e5d4e;
  line-height: 1.8;
  max-width: 760px;
}

.hero-actions {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.server-list {
  display: grid;
  gap: 0;
}

.server-row {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr) max-content;
  align-items: center;
  gap: 14px;
  padding: 12px 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.14);
  transition: background 160ms ease;
}

.server-row:last-child {
  border-bottom: 0;
}

.server-row:hover {
  background: linear-gradient(90deg, rgba(255, 251, 247, 0.52), rgba(255, 255, 255, 0));
}

.server-logo {
  width: 32px;
  height: 32px;
  border-radius: 9px;
  object-fit: contain;
  border: 0;
}

.server-main {
  display: grid;
  gap: 4px;
  min-width: 0;
}

.server-title {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  font-size: 15px;
  font-weight: 700;
  color: #2f241d;
}

.server-title > span:first-child {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.official-tag {
  display: inline-flex;
  padding: 2px 8px;
  border-radius: 0;
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.36), rgba(245, 158, 11, 0)) left bottom / 100% 1px no-repeat;
  color: #b86c33;
  font-size: 12px;
}

.server-subtitle,
.server-hint,
.status-detail,
.muted-text {
  color: #7b6a5a;
  font-size: 12px;
}

.server-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.meta-pill {
  display: inline-flex;
  align-items: center;
  min-height: 19px;
  max-width: 100%;
  padding: 0 2px 2px;
  border: 0;
  border-radius: 0;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.22), rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat;
  color: #806b58;
  font-size: 11px;
  line-height: 19px;
}

.meta-pill.as-button {
  cursor: pointer;
}

.meta-pill.as-button:hover {
  color: #b45309;
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.46), rgba(245, 158, 11, 0)) left bottom / 100% 1px no-repeat;
}

.server-actions,
.row-actions {
  display: flex;
  justify-content: flex-end;
  gap: 7px;
  min-width: max-content;
}

.server-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.mcp-icon-button {
  width: 28px;
  height: 28px;
  min-width: 28px;
  padding: 0;
  border-radius: 999px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 255, 255, 0.62);
  color: #6f6257;
}

.mcp-icon-button.primary {
  border-color: rgba(245, 158, 11, 0.22);
  background: rgba(245, 158, 11, 0.1);
  color: #b45309;
}

.mcp-icon-button.danger {
  color: #d05f5f;
  border-color: rgba(239, 68, 68, 0.14);
  background: rgba(255, 255, 255, 0.62);
}

.dialog-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.transport-switch {
  margin: 24px 0 12px;
}

.field {
  display: grid;
  grid-template-columns: minmax(92px, 132px) minmax(0, 1fr);
  align-items: center;
  gap: 10px;
  margin-top: 9px;
}

.field label {
  display: block;
  margin-bottom: 0;
  color: #7b6b5c;
  font-size: 12px;
  font-weight: 620;
  align-self: start;
  padding-top: 7px;
}

.field > :not(label) {
  grid-column: 2;
}

.mcp-line-input,
.mcp-line-value {
  display: block;
  width: 100%;
  min-width: 0;
  min-height: 32px;
  padding: 0 3px 3px;
  border: 0;
  border-radius: 0;
  outline: none;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.34) 14%, rgba(148, 163, 184, 0.44) 72%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 255, 255, 0.32), rgba(255, 255, 255, 0.04));
  color: #334155;
  font: inherit;
  font-size: 13px;
  line-height: 32px;
  box-shadow: none;
  transition: background 180ms ease, box-shadow 180ms ease;
}

.mcp-line-input::placeholder {
  color: #a8b1c0;
}

.mcp-line-input:hover {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.3) 16%, rgba(148, 163, 184, 0.36) 78%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 251, 247, 0.36), rgba(255, 255, 255, 0.04));
}

.mcp-line-input:focus {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.86) 18%, rgba(217, 119, 6, 0.88) 58%, rgba(245, 158, 11, 0)) left bottom / 100% 2px no-repeat,
    radial-gradient(85% 120% at 48% 100%, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0) 58%),
    linear-gradient(180deg, rgba(255, 251, 247, 0.46), rgba(255, 255, 255, 0.04));
  box-shadow: 0 10px 22px -22px rgba(180, 83, 9, 0.42);
}

.mcp-line-value {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #64748b;
}

.field :deep(.el-input__wrapper),
.field :deep(.el-textarea__inner) {
  min-height: 32px;
  padding: 0 3px 3px;
  border: 0 !important;
  border-radius: 0 !important;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.34) 14%, rgba(148, 163, 184, 0.44) 72%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 255, 255, 0.32), rgba(255, 255, 255, 0.04)) !important;
  box-shadow: none !important;
}

.field :deep(.el-input:hover .el-input__wrapper),
.field :deep(.el-input__wrapper:hover),
.field :deep(.el-textarea__inner:hover) {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.3) 16%, rgba(148, 163, 184, 0.36) 78%, rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    linear-gradient(180deg, rgba(255, 251, 247, 0.36), rgba(255, 255, 255, 0.04)) !important;
}

.field :deep(.el-input.is-focus .el-input__wrapper),
.field :deep(.el-input__wrapper:focus-within),
.field :deep(.el-textarea__inner:focus) {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.86) 18%, rgba(217, 119, 6, 0.88) 58%, rgba(245, 158, 11, 0)) left bottom / 100% 2px no-repeat,
    radial-gradient(85% 120% at 48% 100%, rgba(245, 158, 11, 0.1), rgba(245, 158, 11, 0) 58%),
    linear-gradient(180deg, rgba(255, 251, 247, 0.46), rgba(255, 255, 255, 0.04)) !important;
}

.inline-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  align-items: center;
  gap: 8px;
}

.inline-row.one-col {
  grid-template-columns: minmax(0, 1fr) auto;
}

.repeat-field {
  align-items: start;
}

.repeat-stack {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.repeat-stack.is-empty {
  width: max-content;
  max-width: 100%;
}

.field > .repeat-stack.is-empty {
  width: max-content;
}

.repeat-add {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  justify-self: start;
  width: max-content;
  max-width: max-content;
  min-height: 24px;
  padding: 0 2px 2px;
  border: 0;
  border-radius: 0;
  color: #b45309;
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.34), rgba(245, 158, 11, 0)) left bottom / 100% 1px no-repeat;
  box-shadow: none;
  cursor: pointer;
  font: inherit;
  font-size: 12px;
  line-height: 1;
}

.repeat-add:hover {
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.58), rgba(245, 158, 11, 0)) left bottom / 100% 1px no-repeat;
}

.repeat-add:focus-visible {
  outline: 0;
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.62), rgba(245, 158, 11, 0)) left bottom / 100% 1px no-repeat;
}

.repeat-remove {
  width: 24px;
  height: 24px;
  min-width: 24px;
  padding: 0;
  color: #b76b45;
  background: transparent;
}

.readonly-field :deep(.el-input__wrapper) {
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.24), rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat,
    transparent !important;
}

.readonly-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.readonly-chip {
  display: inline-flex;
  padding: 1px 2px 3px;
  border-radius: 0;
  background:
    linear-gradient(90deg, rgba(245, 158, 11, 0), rgba(245, 158, 11, 0.34), rgba(245, 158, 11, 0)) left bottom / 100% 1px no-repeat;
  color: #8c582d;
  font-size: 12px;
}

.config-section + .config-section {
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid rgba(148, 163, 184, 0.12);
}

.config-section h3 {
  margin: 0 0 10px;
  color: #2f241d;
  font-size: 14px;
}

.config-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  color: #5b4a3d;
}

.config-summary div {
  display: inline-flex;
  min-height: 22px;
  align-items: center;
  padding: 0 2px 2px;
  border-radius: 0;
  background:
    linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0)) left bottom / 100% 1px no-repeat;
  font-size: 12px;
}

.config-actions {
  display: flex;
  gap: 12px;
  margin-top: 18px;
}

.status-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-detail-block {
  margin: 14px 0;
  color: #5b4a3d;
  line-height: 1.7;
}

.empty-panel {
  padding: 8px 0;
  border-radius: 0;
  border-top: 1px solid rgba(226, 232, 240, 0.6);
  border-bottom: 1px solid rgba(226, 232, 240, 0.42);
  background: transparent;
  color: #6e5d4e;
  line-height: 1.55;
}

.tool-card {
  padding: 12px 0;
  border-radius: 0;
  background: transparent;
  border: 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.14);
}

.tool-card + .tool-card {
  margin-top: 0;
}

.tool-name {
  color: #2f241d;
  font-size: 18px;
  font-weight: 700;
}

.tool-description {
  margin-top: 8px;
  color: #6e5d4e;
  line-height: 1.7;
}

.tool-schema {
  margin-top: 14px;
  display: grid;
  gap: 8px;
}

.schema-row {
  display: grid;
  grid-template-columns: 160px 100px 80px 1fr;
  gap: 12px;
  align-items: start;
  font-size: 13px;
  color: #6c5a4b;
}

.schema-name {
  font-weight: 700;
  color: #433327;
}

@media (max-width: 1100px) {
  .hero-card {
    flex-direction: column;
  }

  .dialog-grid,
  .field,
  .inline-row,
  .schema-row {
    grid-template-columns: 1fr;
  }

  .field > :not(label) {
    grid-column: 1;
  }

  .row-actions {
    flex-wrap: wrap;
  }

  .server-row {
    grid-template-columns: 32px minmax(0, 1fr);
    align-items: flex-start;
  }

  .server-actions {
    grid-column: 2;
    justify-content: flex-start;
  }
}
</style>
