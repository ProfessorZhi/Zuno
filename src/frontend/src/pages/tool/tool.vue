<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Setting, Search, Refresh, Upload } from '@element-plus/icons-vue'
import pluginIcon from '../../assets/plugin.svg'
import {
  getVisibleToolsAPI,
  createToolAPI,
  updateToolAPI,
  deleteToolAPI,
  getDefaultToolLogoAPI,
  uploadFileAPI,
  previewCliToolAPI,
  type ToolResponse,
  type RuntimeType,
  type CliConfig,
  type CliPreviewCandidate,
} from '../../apis/tool'
import { getConfigAPI, type RuntimeConfigPayload } from '../../apis/configuration'
import { useUserStore } from '../../store/user'

interface ToolItem extends ToolResponse {
  system_status?: RuntimeConfigPayload['system_tools'][number]['status']
}

interface ToolFormState {
  tool_id?: string
  display_name: string
  description: string
  logo_url: string
  runtime_type: RuntimeType
  openapi_schema: string
  auth_type: '' | 'bearer' | 'basic'
  auth_token: string
  cli_config: CliConfig
}

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const keyword = ref('')
const activeTab = ref<'all' | 'custom'>('all')
const tools = ref<ToolItem[]>([])

const dialogVisible = ref(false)
const dialogLoading = ref(false)
const isEditMode = ref(false)
const logoUploading = ref(false)

const cliPreviewLoading = ref(false)
const cliPreviewError = ref('')
const cliPreviewCandidates = ref<CliPreviewCandidate[]>([])

const form = ref<ToolFormState>({
  display_name: '',
  description: '',
  logo_url: '',
  runtime_type: 'remote_api',
  openapi_schema: JSON.stringify(
    {
      openapi: '3.1.0',
      info: { title: 'Untitled API', description: 'Describe what this tool does.', version: '1.0.0' },
      servers: [{ url: '' }],
      paths: {},
    },
    null,
    2
  ),
  auth_type: '',
  auth_token: '',
  cli_config: {
    tool_dir: '',
    command: '',
    args_template: '',
    cwd_mode: 'tool_dir',
    cwd: '',
    timeout_ms: 30000,
  },
})

const visibleTools = computed(() => {
  const source = activeTab.value === 'custom' ? tools.value.filter((item) => item.user_id !== '0') : tools.value
  const search = keyword.value.trim().toLowerCase()
  const filtered = search
    ? source.filter((item) => [item.display_name, item.description || '', item.name, item.runtime_type || ''].join(' ').toLowerCase().includes(search))
    : source

  return [...filtered].sort((a, b) => {
    const officialDiff = Number(a.user_id === '0') === Number(b.user_id === '0') ? 0 : a.user_id === '0' ? -1 : 1
    if (officialDiff !== 0) return officialDiff
    return a.display_name.localeCompare(b.display_name, 'zh-CN')
  })
})

const isSystemTool = (tool: ToolItem) => tool.user_id === '0'
const isAdmin = computed(() => String(userStore.userInfo?.id || '') === '1')

const statusMap: Record<string, { type: 'success' | 'warning' | 'info' | 'danger'; label: string }> = {
  ready: { type: 'success', label: '已就绪' },
  needs_config: { type: 'warning', label: '需配置' },
  runtime_input: { type: 'info', label: '依赖运行时输入' },
  missing_dependency: { type: 'danger', label: '缺少依赖' },
}

const fetchTools = async () => {
  loading.value = true
  try {
    const [toolResponse, configResponse] = await Promise.all([getVisibleToolsAPI(), getConfigAPI()])
    if (toolResponse.data.status_code !== 200) {
      ElMessage.error(toolResponse.data.status_message || '加载工具失败')
      return
    }

    const statusLookup = new Map((configResponse.data.data?.system_tools || []).map((item) => [item.tool_name, item.status] as const))
    tools.value = (toolResponse.data.data || []).map((item) => ({ ...item, system_status: statusLookup.get(item.name) }))
  } catch (error) {
    console.error('加载工具失败:', error)
    ElMessage.error('加载工具失败')
  } finally {
    loading.value = false
  }
}

const resetForm = async () => {
  let defaultLogo = ''
  try {
    const response = await getDefaultToolLogoAPI()
    if (response.data.status_code === 200) defaultLogo = response.data.data.logo_url
  } catch (error) {
    console.warn('加载默认工具图标失败:', error)
  }

  form.value = {
    display_name: '',
    description: '',
    logo_url: defaultLogo,
    runtime_type: 'remote_api',
    openapi_schema: JSON.stringify(
      {
        openapi: '3.1.0',
        info: { title: 'Untitled API', description: 'Describe what this tool does.', version: '1.0.0' },
        servers: [{ url: '' }],
        paths: {},
      },
      null,
      2
    ),
    auth_type: '',
    auth_token: '',
    cli_config: {
      tool_dir: '',
      command: '',
      args_template: '',
      cwd_mode: 'tool_dir',
      cwd: '',
      timeout_ms: 30000,
    },
  }
  cliPreviewError.value = ''
  cliPreviewCandidates.value = []
  isEditMode.value = false
}

const openCreateDialog = async () => {
  await resetForm()
  dialogVisible.value = true
}

const openEditDialog = (tool: ToolItem) => {
  if (isSystemTool(tool) && !isAdmin.value) {
    ElMessage.warning('只有管理员可以编辑系统工具')
    return
  }

  const cliConfigSource = (tool as any).cli_config || {}
  form.value = {
    tool_id: tool.tool_id,
    display_name: tool.display_name,
    description: tool.description || '',
    logo_url: tool.logo_url || '',
    runtime_type: tool.runtime_type || 'remote_api',
    openapi_schema: tool.openapi_schema ? JSON.stringify(tool.openapi_schema, null, 2) : '{}',
    auth_type: tool.auth_config?.type || '',
    auth_token: tool.auth_config?.token || '',
    cli_config: {
      tool_dir: cliConfigSource.tool_dir || '',
      command: cliConfigSource.command || '',
      args_template: cliConfigSource.args_template || '',
      cwd_mode: cliConfigSource.cwd_mode || 'tool_dir',
      cwd: cliConfigSource.cwd || '',
      timeout_ms: cliConfigSource.timeout_ms || 30000,
    },
  }
  cliPreviewError.value = ''
  cliPreviewCandidates.value = []
  isEditMode.value = true
  dialogVisible.value = true
}

const openConfigPage = (tool: ToolItem) => {
  router.push({ name: 'configuration', query: { tool: tool.name } })
}

const validateToolForm = () => {
  if (!form.value.display_name.trim()) return ElMessage.warning('请先填写工具名称'), false
  if (!form.value.description.trim()) return ElMessage.warning('请先填写工具说明'), false

  if (form.value.runtime_type === 'remote_api') {
    try {
      JSON.parse(form.value.openapi_schema)
    } catch {
      ElMessage.warning('OpenAPI Schema 不是合法的 JSON')
      return false
    }
  }

  if (form.value.runtime_type === 'cli' && (!form.value.cli_config.tool_dir?.trim() || !form.value.cli_config.command?.trim())) {
    ElMessage.warning('CLI 工具至少需要目录和命令')
    return false
  }

  return true
}

const submitDialog = async () => {
  if (!validateToolForm()) return
  dialogLoading.value = true
  try {
    const payload: any = {
      display_name: form.value.display_name.trim(),
      description: form.value.description.trim(),
      logo_url: form.value.logo_url.trim(),
      runtime_type: form.value.runtime_type,
    }

    if (form.value.runtime_type === 'remote_api') {
      payload.openapi_schema = JSON.parse(form.value.openapi_schema)
      payload.auth_config = form.value.auth_type ? { type: form.value.auth_type, token: form.value.auth_token || '' } : {}
    } else {
      payload.cli_config = {
        ...form.value.cli_config,
        tool_dir: form.value.cli_config.tool_dir.trim(),
        command: form.value.cli_config.command.trim(),
        args_template: form.value.cli_config.args_template?.trim() || '',
        cwd: form.value.cli_config.cwd?.trim() || '',
      }
    }

    const response = isEditMode.value && form.value.tool_id
      ? await updateToolAPI({ tool_id: form.value.tool_id, ...payload })
      : await createToolAPI(payload)

    if (response.data.status_code !== 200) throw new Error(response.data.status_message || '保存工具失败')
    ElMessage.success(isEditMode.value ? '工具已更新' : '工具已创建')
    dialogVisible.value = false
    await fetchTools()
  } catch (error: any) {
    console.error('保存工具失败:', error)
    ElMessage.error(error.message || '保存工具失败')
  } finally {
    dialogLoading.value = false
  }
}

const handleDelete = async (tool: ToolItem) => {
  if (isSystemTool(tool) && !isAdmin.value) {
    ElMessage.warning('只有管理员可以删除系统工具')
    return
  }
  try {
    await ElMessageBox.confirm(`确认删除工具“${tool.display_name}”吗？`, '删除工具', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
  } catch {
    return
  }

  try {
    const response = await deleteToolAPI({ tool_id: tool.tool_id })
    if (response.data.status_code !== 200) throw new Error(response.data.status_message || '删除工具失败')
    ElMessage.success('工具已删除')
    await fetchTools()
  } catch (error: any) {
    console.error('删除工具失败:', error)
    ElMessage.error(error.message || '删除工具失败')
  }
}

const previewCli = async () => {
  cliPreviewLoading.value = true
  cliPreviewError.value = ''
  cliPreviewCandidates.value = []
  try {
    const response = await previewCliToolAPI({
      tool_dir: form.value.cli_config.tool_dir,
      command: form.value.cli_config.command,
    })
    if (response.data.status_code !== 200) throw new Error(response.data.status_message || 'CLI 预览失败')
    cliPreviewCandidates.value = response.data.data?.candidates || []
    if (!cliPreviewCandidates.value.length) cliPreviewError.value = '没有识别到可用命令说明，你也可以直接手工填写。'
  } catch (error: any) {
    console.error('CLI 预览失败:', error)
    cliPreviewError.value = error.message || 'CLI 预览失败'
  } finally {
    cliPreviewLoading.value = false
  }
}

const handleLogoUpload = async (uploadFile: any) => {
  logoUploading.value = true
  try {
    const response = await uploadFileAPI(uploadFile.raw)
    if (response.data.status_code !== 200) throw new Error(response.data.status_message || '上传失败')
    form.value.logo_url = response.data.data
    ElMessage.success('图标上传成功')
  } catch (error: any) {
    console.error('上传工具图标失败:', error)
    ElMessage.error(error.message || '上传工具图标失败')
  } finally {
    logoUploading.value = false
  }
}

onMounted(fetchTools)
</script>

<template>
  <div class="tool-page">
    <section class="hero-card">
      <div>
        <div class="eyebrow">TOOLS</div>
        <h1>工具管理</h1>
        <p>系统工具负责平台内置能力，自定义工具负责扩展能力。普通用户只能管理自己的工具，管理员可以维护系统工具。</p>
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
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </section>

    <section class="list-card" v-loading="loading">
      <el-table :data="visibleTools" empty-text="暂无工具">
        <el-table-column label="名称" min-width="260">
          <template #default="{ row }">
            <div class="tool-cell">
              <div class="logo-wrap"><img :src="row.logo_url || pluginIcon" :alt="row.display_name" /></div>
              <div class="tool-copy">
                <div class="tool-name-line">
                  <span class="tool-name">{{ row.display_name }}</span>
                  <el-tag v-if="isSystemTool(row)" type="warning" size="small">系统工具</el-tag>
                </div>
                <div class="tool-meta">{{ row.runtime_type === 'cli' ? 'CLI 工具' : '远程 API 工具' }}</div>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="描述" min-width="320">
          <template #default="{ row }"><div class="tool-description">{{ row.description || '暂无说明' }}</div></template>
        </el-table-column>

        <el-table-column label="状态" width="140" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.system_status" :type="statusMap[row.system_status]?.type || 'info'" size="small">
              {{ statusMap[row.system_status]?.label || row.system_status }}
            </el-tag>
            <span v-else class="status-placeholder">自定义</span>
          </template>
        </el-table-column>

        <el-table-column label="创建时间" min-width="180">
          <template #default="{ row }">{{ row.create_time || '--' }}</template>
        </el-table-column>

        <el-table-column label="操作" min-width="260" align="center">
          <template #default="{ row }">
            <div class="action-row">
              <el-button v-if="isSystemTool(row)" size="small" type="success" :icon="Setting" @click="openConfigPage(row)">配置</el-button>
              <el-button size="small" type="primary" :icon="Edit" @click="openEditDialog(row)">编辑</el-button>
              <el-button size="small" type="danger" :icon="Delete" @click="handleDelete(row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </section>

    <el-dialog v-model="dialogVisible" :title="isEditMode ? '编辑工具' : '新建工具'" width="840px">
      <el-form label-position="top">
        <el-form-item label="工具图标">
          <div class="logo-editor">
            <div class="logo-preview"><img :src="form.logo_url || pluginIcon" alt="工具图标预览" /></div>
            <el-upload :show-file-list="false" :auto-upload="false" :on-change="handleLogoUpload">
              <el-button :loading="logoUploading" :icon="Upload">上传图标</el-button>
            </el-upload>
          </div>
        </el-form-item>

        <el-form-item label="名称"><el-input v-model="form.display_name" placeholder="例如：项目构建助手" /></el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="说明这个工具解决什么问题" />
        </el-form-item>
        <el-form-item label="运行方式">
          <el-radio-group v-model="form.runtime_type">
            <el-radio-button label="remote_api">远程 API</el-radio-button>
            <el-radio-button label="cli">CLI</el-radio-button>
          </el-radio-group>
        </el-form-item>

        <template v-if="form.runtime_type === 'remote_api'">
          <el-form-item label="OpenAPI Schema">
            <el-input v-model="form.openapi_schema" type="textarea" :rows="16" placeholder="填写 OpenAPI Schema，定义工具可调用的接口。" />
          </el-form-item>
          <el-form-item label="认证方式">
            <el-select v-model="form.auth_type" placeholder="无认证">
              <el-option label="无认证" value="" />
              <el-option label="Bearer Token" value="bearer" />
              <el-option label="Basic Auth" value="basic" />
            </el-select>
          </el-form-item>
          <el-form-item v-if="form.auth_type" label="认证密钥">
            <el-input v-model="form.auth_token" type="textarea" :rows="3" placeholder="填写认证信息" />
          </el-form-item>
        </template>

        <template v-else>
          <el-form-item label="工具目录">
            <el-input v-model="form.cli_config.tool_dir" placeholder="例如：F:\\agent_project\\agent\\AgentChat\\Zuno\\tools\\my-cli" />
          </el-form-item>
          <el-form-item label="命令"><el-input v-model="form.cli_config.command" placeholder="例如：python main.py 或 mycli.exe" /></el-form-item>
          <el-form-item label="参数模板"><el-input v-model="form.cli_config.args_template" placeholder="例如：--input {input} --output {output}" /></el-form-item>
          <el-form-item label="工作目录">
            <div class="cli-grid">
              <el-select v-model="form.cli_config.cwd_mode">
                <el-option label="使用工具目录" value="tool_dir" />
                <el-option label="自定义目录" value="custom" />
              </el-select>
              <el-input v-if="form.cli_config.cwd_mode === 'custom'" v-model="form.cli_config.cwd" placeholder="填写执行时的工作目录" />
            </div>
          </el-form-item>
          <el-form-item label="超时时间（毫秒）"><el-input-number v-model="form.cli_config.timeout_ms" :min="1000" :step="1000" /></el-form-item>

          <div class="cli-preview-block">
            <div class="cli-preview-head">
              <strong>CLI 自动识别</strong>
              <el-button size="small" @click="previewCli" :loading="cliPreviewLoading">扫描目录</el-button>
            </div>
            <p class="cli-preview-tip">如果目录里有 README 或典型入口文件，可以先扫描，辅助你确认命令怎么接。</p>
            <el-alert v-if="cliPreviewError" :title="cliPreviewError" type="warning" :closable="false" />
            <div v-if="cliPreviewCandidates.length" class="candidate-list">
              <article v-for="item in cliPreviewCandidates" :key="item.command" class="candidate-item">
                <strong>{{ item.command }}</strong>
                <p>{{ item.reason }}</p>
              </article>
            </div>
          </div>
        </template>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="submitDialog">{{ isEditMode ? '保存修改' : '创建工具' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.tool-page { display: grid; gap: 20px; padding: 24px; }
.hero-card, .toolbar-card, .list-card {
  border-radius: 24px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 252, 248, 0.94);
  box-shadow: 0 18px 36px rgba(120, 80, 42, 0.08);
}
.hero-card, .toolbar-card { padding: 24px 26px; }
.eyebrow { font-size: 12px; letter-spacing: 0.16em; color: #be6d38; }
.hero-card h1 { margin: 12px 0 10px; font-size: 32px; color: #2f241b; }
.hero-card p { margin: 0; color: #786656; line-height: 1.8; }
.hero-actions { margin-top: 18px; display: flex; gap: 12px; flex-wrap: wrap; }
.toolbar-card { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.tool-tabs { flex: 1; }
.search-box { width: 320px; }
.list-card { padding: 10px 14px; }
.tool-cell { display: flex; align-items: center; gap: 14px; }
.logo-wrap {
  width: 52px; height: 52px; border-radius: 16px; overflow: hidden; background: #f8efe4;
  border: 1px solid rgba(214, 132, 70, 0.14);
}
.logo-wrap img, .logo-preview img { width: 100%; height: 100%; object-fit: cover; }
.tool-name-line { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
.tool-name { font-size: 16px; font-weight: 700; color: #32261d; }
.tool-meta, .tool-description, .status-placeholder { color: #7c6a5a; }
.action-row { display: flex; justify-content: center; gap: 8px; flex-wrap: wrap; }
.logo-editor { display: flex; gap: 16px; align-items: center; }
.logo-preview {
  width: 72px; height: 72px; border-radius: 20px; overflow: hidden;
  border: 1px solid rgba(214, 132, 70, 0.16); background: #f8efe4;
}
.cli-grid { display: grid; grid-template-columns: 220px 1fr; gap: 12px; width: 100%; }
.cli-preview-block {
  padding: 16px; border-radius: 18px; background: #fff8f1;
  border: 1px solid rgba(214, 132, 70, 0.12);
}
.cli-preview-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.cli-preview-tip { margin: 8px 0 12px; color: #7a6656; }
.candidate-list { display: grid; gap: 10px; }
.candidate-item {
  padding: 12px 14px; border-radius: 14px; background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(214, 132, 70, 0.1);
}
.candidate-item strong { display: block; color: #32261d; }
.candidate-item p { margin: 6px 0 0; color: #7a6758; }

@media (max-width: 960px) {
  .toolbar-card { flex-direction: column; align-items: stretch; }
  .search-box { width: 100%; }
  .cli-grid { grid-template-columns: 1fr; }
}
</style>
