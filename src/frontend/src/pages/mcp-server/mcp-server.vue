<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Edit, Plus, Refresh, Setting } from '@element-plus/icons-vue'
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

const serverDialogVisible = ref(false)
const configDialogVisible = ref(false)
const toolsDialogVisible = ref(false)

const isEditMode = ref(false)
const currentServer = ref<MCPServerView | null>(null)
const toolsDialogTitle = ref('')
const currentTools = ref<any[]>([])

const servers = ref<MCPServerView[]>([])
const defaultLogoUrl = ref('')

const serverForm = reactive<StructuredServerForm>({
  server_name: '',
  logo_url: '',
  transport: 'stdio',
  command: '',
  args: [''],
  env: [{ key: '', value: '' }],
  env_passthrough: [''],
  cwd: '',
  url: '',
  headers: [{ key: '', value: '' }],
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
    args: [''],
    env: [createEmptyKeyValue()],
    env_passthrough: [''],
    cwd: '',
    url: '',
    headers: [createEmptyKeyValue()],
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
    next.args = Array.isArray(config.args) && config.args.length > 0 ? [...config.args] : ['']
    next.env =
      config.env && typeof config.env === 'object'
        ? Object.entries(config.env).map(([key, value]) => ({ key, value: String(value ?? '') }))
        : [createEmptyKeyValue()]
    next.env_passthrough =
      Array.isArray(config.env_passthrough) && config.env_passthrough.length > 0
        ? config.env_passthrough.map((item: unknown) => String(item))
        : ['']
    next.cwd = config.cwd || ''
    next.url = config.url || server.url || ''
    next.headers =
      config.headers && typeof config.headers === 'object'
        ? Object.entries(config.headers).map(([key, value]) => ({ key, value: String(value ?? '') }))
        : [createEmptyKeyValue()]
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
      defaultLogoUrl.value = response.data.data.logo_url || ''
    }
  } catch (error) {
    console.warn('加载默认 MCP 图标失败', error)
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
  isEditMode.value = true
  currentServer.value = server
  fillServerForm(server)
  serverDialogVisible.value = true
}

async function submitServerDialog() {
  savingServer.value = true
  try {
    if (!serverForm.server_name.trim()) throw new Error('请填写 MCP 名称。')
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
        <div class="eyebrow">MCP CENTER</div>
        <h2>MCP 服务管理</h2>
        <p>新增 MCP 只保留两种标准接入：STDIO 和流式 HTTP。官方预置服务也使用同一套结构化配置展示。</p>
      </div>
      <div class="hero-actions">
        <el-button :icon="Refresh" :loading="loading" @click="fetchServers">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateServerDialog">添加服务器</el-button>
      </div>
    </section>

    <section class="table-card" v-loading="loading">
      <table class="server-table">
        <thead>
          <tr>
            <th>服务</th>
            <th>工具数</th>
            <th>配置状态</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="server in servers" :key="server.mcp_server_id">
            <td>
              <div class="server-cell">
                <img class="server-logo" :src="server.logo_url || defaultLogoUrl" :alt="server.server_name" />
                <div>
                  <div class="server-title">
                    <span>{{ server.server_name }}</span>
                    <span v-if="server.user_id === '0'" class="official-tag">官方</span>
                  </div>
                  <div class="server-subtitle">{{ connectionModeText(server) }}</div>
                  <div class="server-hint">{{ connectionHint(server) }}</div>
                </div>
              </div>
            </td>
            <td>
              <el-button link type="primary" @click="openToolsDialog(server)">{{ server.tools?.length || 0 }} 个工具</el-button>
            </td>
            <td>
              <el-tag :type="server.displayStatus.type">{{ server.displayStatus.label }}</el-tag>
              <div class="status-detail">{{ server.displayStatus.detail }}</div>
            </td>
            <td>{{ server.create_time }}</td>
            <td>
              <div class="row-actions">
                <el-button size="small" type="success" :icon="Setting" @click="openConfigDialog(server)">配置</el-button>
                <el-button
                  v-if="canEditServer(server)"
                  size="small"
                  type="primary"
                  :icon="Edit"
                  @click="openEditServerDialog(server)"
                >
                  编辑
                </el-button>
                <el-button
                  v-if="canEditServer(server)"
                  size="small"
                  type="danger"
                  :icon="Delete"
                  @click="handleDelete(server)"
                >
                  删除
                </el-button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <el-dialog v-model="serverDialogVisible" :title="isEditMode ? '编辑 MCP 服务' : '新增 MCP 服务'" width="820px">
      <div class="dialog-grid">
        <div class="field">
          <label>名称</label>
          <el-input v-model="serverForm.server_name" placeholder="例如：我的 MCP Server" />
        </div>
        <div class="field">
          <label>Logo URL</label>
          <el-input v-model="serverForm.logo_url" placeholder="留空则使用默认图标" />
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
          <el-input v-model="serverForm.command" placeholder="例如：python 或 uvx" />
        </div>
        <div class="field">
          <label>参数</label>
          <div v-for="(arg, index) in serverForm.args" :key="`arg-${index}`" class="inline-row">
            <el-input v-model="serverForm.args[index]" placeholder="一项参数一行" />
            <el-button text type="danger" @click="serverForm.args.splice(index, 1)">删除</el-button>
          </div>
          <el-button text @click="serverForm.args.push('')">添加参数</el-button>
        </div>
        <div class="field">
          <label>环境变量</label>
          <div v-for="(item, index) in serverForm.env" :key="`env-${index}`" class="inline-row">
            <el-input v-model="item.key" placeholder="键" />
            <el-input v-model="item.value" placeholder="值" />
            <el-button text type="danger" @click="serverForm.env.splice(index, 1)">删除</el-button>
          </div>
          <el-button text @click="serverForm.env.push(createEmptyKeyValue())">添加环境变量</el-button>
        </div>
        <div class="field">
          <label>环境变量传递</label>
          <div v-for="(item, index) in serverForm.env_passthrough" :key="`passthrough-${index}`" class="inline-row">
            <el-input v-model="serverForm.env_passthrough[index]" placeholder="例如：OPENAI_API_KEY" />
            <el-button text type="danger" @click="serverForm.env_passthrough.splice(index, 1)">删除</el-button>
          </div>
          <el-button text @click="serverForm.env_passthrough.push('')">添加变量</el-button>
        </div>
        <div class="field">
          <label>工作目录</label>
          <el-input v-model="serverForm.cwd" placeholder="例如：/app 或 ~/code" />
        </div>
      </template>

      <template v-else>
        <div class="field">
          <label>流式 HTTP 地址</label>
          <el-input v-model="serverForm.url" placeholder="https://example.com/mcp" />
        </div>
        <div class="field">
          <label>请求头</label>
          <div v-for="(item, index) in serverForm.headers" :key="`header-${index}`" class="inline-row">
            <el-input v-model="item.key" placeholder="Header 名称" />
            <el-input v-model="item.value" placeholder="Header 值" />
            <el-button text type="danger" @click="serverForm.headers.splice(index, 1)">删除</el-button>
          </div>
          <el-button text @click="serverForm.headers.push(createEmptyKeyValue())">添加请求头</el-button>
        </div>
      </template>

      <template #footer>
        <el-button @click="serverDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingServer" @click="submitServerDialog">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="configDialogVisible" title="MCP 配置" width="860px">
      <template v-if="currentServer">
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
              <el-input :model-value="serverForm.command" readonly />
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
              <el-input :model-value="serverForm.cwd || '未设置'" readonly />
            </div>
          </template>
          <template v-else>
            <div class="field readonly-field">
              <label>流式 HTTP 地址</label>
              <el-input :model-value="serverForm.url" readonly />
            </div>
          </template>
        </section>

        <section class="config-section">
          <h3>个人配置</h3>
          <template v-if="personalConfigFields.length > 0">
            <div v-for="item in personalConfigFields" :key="item.key" class="field">
              <label>{{ item.label || item.key }}</label>
              <el-input
                v-model="personalConfigValues[item.key]"
                :type="/secret|token|key|password/i.test(item.key) ? 'password' : 'text'"
                :show-password="/secret|token|key|password/i.test(item.key)"
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
    </el-dialog>

    <el-dialog v-model="toolsDialogVisible" :title="toolsDialogTitle" width="760px">
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
    </el-dialog>
  </div>
</template>

<style scoped>
.mcp-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
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
  overflow-x: auto;
}

.hero-card {
  display: flex;
  justify-content: space-between;
  gap: 24px;
}

.eyebrow {
  display: inline-flex;
  margin-bottom: 10px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(214, 132, 70, 0.1);
  color: #b86c33;
  font-size: 12px;
  letter-spacing: 0.14em;
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

.server-table {
  width: 100%;
  min-width: 980px;
  border-collapse: collapse;
}

.server-table th,
.server-table td {
  padding: 20px 12px;
  border-bottom: 1px solid rgba(214, 132, 70, 0.12);
  text-align: left;
  vertical-align: top;
}

.server-table th {
  color: #6b5b4d;
  font-weight: 700;
}

.server-cell {
  display: flex;
  gap: 16px;
}

.server-logo {
  width: 68px;
  height: 68px;
  border-radius: 20px;
  object-fit: cover;
  border: 1px solid rgba(214, 132, 70, 0.12);
}

.server-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  font-size: 18px;
  font-weight: 700;
  color: #2f241d;
}

.official-tag {
  display: inline-flex;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(214, 132, 70, 0.12);
  color: #b86c33;
  font-size: 12px;
}

.server-subtitle,
.server-hint,
.status-detail,
.muted-text {
  color: #7b6a5a;
  font-size: 14px;
}

.status-detail {
  margin-top: 8px;
  max-width: 280px;
  line-height: 1.6;
}

.row-actions {
  display: flex;
  gap: 8px;
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
  margin-top: 16px;
}

.field label {
  display: block;
  margin-bottom: 8px;
  color: #4c3b2f;
  font-weight: 600;
}

.inline-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 12px;
  margin-bottom: 10px;
}

.readonly-field :deep(.el-input__wrapper) {
  background: rgba(245, 239, 231, 0.6);
}

.readonly-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.readonly-chip {
  display: inline-flex;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(214, 132, 70, 0.1);
  color: #8c582d;
  font-size: 13px;
}

.config-section + .config-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid rgba(214, 132, 70, 0.12);
}

.config-section h3 {
  margin: 0 0 14px;
  color: #2f241d;
}

.config-summary {
  display: grid;
  gap: 8px;
  color: #5b4a3d;
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
  padding: 16px 18px;
  border-radius: 18px;
  background: rgba(245, 239, 231, 0.7);
  color: #6e5d4e;
  line-height: 1.7;
}

.tool-card {
  padding: 18px;
  border-radius: 18px;
  background: rgba(250, 246, 240, 0.9);
  border: 1px solid rgba(214, 132, 70, 0.12);
}

.tool-card + .tool-card {
  margin-top: 14px;
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
  .inline-row,
  .schema-row {
    grid-template-columns: 1fr;
  }

  .row-actions {
    flex-wrap: wrap;
  }
}
</style>
