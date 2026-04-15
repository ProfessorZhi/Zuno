<template>
  <div class="config-page">
    <section class="config-card">
      <template v-if="toolName">
        <header class="card-header">
          <div>
            <h1>{{ toolConfig?.display_name || '系统工具配置' }}</h1>
            <p>{{ toolConfig?.description || '正在加载工具配置...' }}</p>
          </div>
        </header>

        <div v-if="loading" class="state-box">正在加载配置...</div>

        <div v-else-if="toolConfig" class="content-stack">
          <div v-if="toolStatus" class="status-banner" :class="statusClass">
            <strong>{{ toolStatus.label }}</strong>
            <span>{{ toolStatus.detail }}</span>
          </div>

          <div v-if="toolConfig.note" class="note-card">
            {{ toolConfig.note }}
          </div>

          <template v-if="toolConfig.config_type === 'email_accounts'">
            <section class="panel-card">
              <div class="panel-head">
                <div>
                  <h2>邮箱槽位</h2>
                  <p>给发送邮件工具预先配置多个邮箱槽位，Agent 就能直接按槽位调用。</p>
                </div>
                <div class="quick-actions">
                  <button class="secondary-btn" type="button" @click="addEmailAccount('qq')">新增 QQ</button>
                  <button class="secondary-btn" type="button" @click="addEmailAccount('163')">新增 163</button>
                  <button class="secondary-btn" type="button" @click="addEmailAccount('gmail')">新增 Gmail</button>
                  <button class="secondary-btn" type="button" @click="addEmailAccount('outlook')">新增 Outlook</button>
                  <button class="secondary-btn" type="button" @click="addEmailAccount('custom')">新增自定义 SMTP</button>
                </div>
              </div>

              <div v-if="emailAccounts.length === 0" class="empty-box">
                还没有邮箱槽位。至少配置一个可用槽位后，Agent 才能直接发信。
              </div>

              <div v-else class="account-list">
                <article v-for="(account, index) in emailAccounts" :key="index" class="account-card">
                  <div class="account-head">
                    <strong>槽位 {{ index + 1 }}</strong>
                    <button class="danger-text-btn" type="button" @click="removeEmailAccount(index)">删除</button>
                  </div>

                  <div class="field-grid">
                    <label class="field-item">
                      <span>槽位名</span>
                      <input v-model="account.slot_name" class="field-input" placeholder="例如 qq-main" />
                    </label>
                    <label class="field-item">
                      <span>邮箱类型</span>
                      <select v-model="account.provider" class="field-input" @change="handleProviderChange(account)">
                        <option value="qq">QQ 邮箱</option>
                        <option value="163">163 邮箱</option>
                        <option value="gmail">Gmail</option>
                        <option value="outlook">Outlook</option>
                        <option value="custom">自定义 SMTP</option>
                      </select>
                    </label>
                    <label class="field-item">
                      <span>发件邮箱</span>
                      <input v-model="account.sender_email" class="field-input" placeholder="例如 user@qq.com" />
                    </label>
                    <label class="field-item">
                      <span>显示名称</span>
                      <input v-model="account.display_name" class="field-input" placeholder="例如 Zuno 主邮箱" />
                    </label>
                    <label class="field-item">
                      <span>授权码</span>
                      <input v-model="account.auth_code" type="password" class="field-input" placeholder="填写授权码" />
                    </label>
                    <label class="field-item">
                      <span>SMTP 主机</span>
                      <input v-model="account.smtp_host" class="field-input" placeholder="例如 smtp.qq.com" />
                    </label>
                    <label class="field-item">
                      <span>SMTP 端口</span>
                      <input v-model.number="account.smtp_port" type="number" min="1" class="field-input" />
                    </label>
                    <label class="field-item checkbox-item">
                      <span>连接方式</span>
                      <label class="checkbox-inline">
                        <input v-model="account.use_ssl" type="checkbox" />
                        <span>使用 SSL</span>
                      </label>
                    </label>
                  </div>
                </article>
              </div>
            </section>
          </template>

          <template v-else-if="toolConfig.fields.length > 0">
            <section class="panel-card">
              <div class="panel-head">
                <div>
                  <h2>配置项</h2>
                  <p>填写这个系统工具运行时所需的固定参数。</p>
                </div>
              </div>

              <div class="field-stack">
                <label v-for="field in toolConfig.fields" :key="field.key" class="field-item">
                  <span>
                    {{ field.label }}
                    <em v-if="field.required">*</em>
                  </span>
                  <input
                    v-model="toolValues[field.key]"
                    class="field-input"
                    :type="field.secret ? 'password' : 'text'"
                    :placeholder="field.placeholder || ''"
                  />
                </label>
              </div>
            </section>
          </template>

          <div v-else class="empty-box">这个工具当前没有额外的固定配置项，可以直接使用。</div>

          <section v-if="toolGuide.title" class="guide-card">
            <h2>{{ toolGuide.title }}</h2>
            <p v-if="toolGuide.summary">{{ toolGuide.summary }}</p>
            <ol v-if="toolGuide.steps.length > 0">
              <li v-for="step in toolGuide.steps" :key="step">{{ step }}</li>
            </ol>
          </section>

          <div class="footer-actions">
            <button class="secondary-btn" type="button" @click="reloadToolConfig">重置</button>
            <button class="primary-btn" type="button" :disabled="saving" @click="saveToolConfig">
              {{ saving ? '保存中...' : '保存配置' }}
            </button>
          </div>
        </div>
      </template>

      <template v-else>
        <header class="card-header">
          <div>
            <h1>运行配置</h1>
            <p>这里展示完整 YAML 配置，用于整体排查和高级修改。</p>
          </div>
        </header>

        <div v-if="loading" class="state-box">正在加载配置...</div>

        <div v-else class="content-stack">
          <textarea v-model="rawConfig" class="config-editor"></textarea>
          <div class="footer-actions">
            <button class="secondary-btn" type="button" @click="reloadRawConfig">重置</button>
            <button class="primary-btn" type="button" :disabled="saving" @click="saveRawConfig">
              {{ saving ? '保存中...' : '保存配置' }}
            </button>
          </div>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  getConfigAPI,
  getSystemToolConfigAPI,
  updateConfigAPI,
  updateSystemToolConfigAPI,
  type RuntimeConfigPayload,
  type SystemToolConfigPayload,
} from '../../apis/configuration'

type ToolStatus = RuntimeConfigPayload['system_tools'][number]['status']
type EmailAccount = NonNullable<SystemToolConfigPayload['accounts']>[number]
type ToolGuide = { title: string; summary: string; steps: string[] }

const route = useRoute()
const toolName = ref('')
const loading = ref(false)
const saving = ref(false)
const rawConfig = ref('')
const rawConfigSnapshot = ref('')
const toolConfig = ref<SystemToolConfigPayload | null>(null)
const toolValues = ref<Record<string, string>>({})
const emailAccounts = ref<EmailAccount[]>([])
const systemToolMetaMap = ref<Record<string, RuntimeConfigPayload['system_tools'][number]>>({})

const providerTemplates: Record<string, Pick<EmailAccount, 'smtp_host' | 'smtp_port' | 'use_ssl'>> = {
  qq: { smtp_host: 'smtp.qq.com', smtp_port: 465, use_ssl: true },
  '163': { smtp_host: 'smtp.163.com', smtp_port: 465, use_ssl: true },
  gmail: { smtp_host: 'smtp.gmail.com', smtp_port: 465, use_ssl: true },
  outlook: { smtp_host: 'smtp.office365.com', smtp_port: 587, use_ssl: false },
  custom: { smtp_host: '', smtp_port: 465, use_ssl: true },
}

const toolStatus = computed<ToolStatus | null>(() => {
  if (!toolName.value) return null
  return systemToolMetaMap.value[toolName.value]?.status || null
})

const statusClass = computed(() => {
  switch (toolStatus.value?.code) {
    case 'ready':
      return 'is-ready'
    case 'needs_config':
      return 'is-config'
    case 'runtime_input':
      return 'is-runtime'
    case 'missing_dependency':
      return 'is-missing'
    default:
      return ''
  }
})

const toolGuideMap: Record<string, ToolGuide> = {
  send_email: {
    title: '邮箱配置说明',
    summary: '建议把常用邮箱做成多个槽位，例如 qq-main、qq-backup、office-main。Agent 调用时只需要引用槽位名。',
    steps: [
      '每个槽位对应一个发件邮箱与授权码。',
      'QQ、163、Gmail、Outlook 都支持配置多个槽位。',
      '保存后，发送邮件工具会优先按槽位名匹配预设邮箱。',
    ],
  },
  get_weather: {
    title: '天气工具说明',
    summary: '天气工具需要固定 API Key 和接口地址，保存后才会进入可用状态。',
    steps: [
      '准备天气服务提供方的 API Key。',
      '填入 API Key 和接口地址。',
      '保存后状态会切换为“已就绪”。',
    ],
  },
  get_delivery: {
    title: '物流工具说明',
    summary: '物流工具依赖固定 APPCODE 或接口认证信息，保存后才能直接查快递。',
    steps: [
      '准备物流接口认证信息。',
      '填入 APPCODE 或约定字段。',
      '保存后状态会切换为“已就绪”。',
    ],
  },
  tavily_search: {
    title: '联网搜索说明',
    summary: '这个工具只需要固定 Tavily API Key。',
    steps: ['填入 Tavily API Key 后保存即可。'],
  },
  bocha_search: {
    title: '博查搜索说明',
    summary: '这个工具依赖博查搜索 API Key 与接口地址。',
    steps: ['填入 API Key 和接口地址。', '保存后状态会切换为“已就绪”。'],
  },
  convert_to_pdf: {
    title: 'Docx 转 PDF 说明',
    summary: '这个工具依赖 LibreOffice 或兼容的命令行转换能力。',
    steps: ['确认运行环境已安装 LibreOffice。', '确保 backend 能找到 libreoffice 命令。'],
  },
  convert_to_docx: {
    title: 'PDF 转 Docx 说明',
    summary: '这个工具依赖 Python 包 pdf2docx。',
    steps: ['如果状态显示缺依赖，请在 backend 运行环境安装 pdf2docx。'],
  },
}

const toolGuide = computed<ToolGuide>(() => {
  return toolGuideMap[toolName.value] || { title: '', summary: '', steps: [] }
})

const createEmailAccount = (provider: string = 'qq'): EmailAccount => {
  const preset = providerTemplates[provider] || providerTemplates.custom
  return {
    slot_name: '',
    provider,
    sender_email: '',
    auth_code: '',
    smtp_host: preset.smtp_host,
    smtp_port: preset.smtp_port,
    use_ssl: preset.use_ssl,
    display_name: '',
  }
}

const applyRoute = () => {
  toolName.value = typeof route.query.tool === 'string' ? route.query.tool : ''
}

const handleProviderChange = (account: EmailAccount) => {
  const preset = providerTemplates[account.provider] || providerTemplates.custom
  account.smtp_host = preset.smtp_host
  account.smtp_port = preset.smtp_port
  account.use_ssl = preset.use_ssl
}

const addEmailAccount = (provider: string = 'qq') => {
  emailAccounts.value.push(createEmailAccount(provider))
}

const removeEmailAccount = (index: number) => {
  emailAccounts.value.splice(index, 1)
}

const loadSystemToolMeta = async () => {
  const response = await getConfigAPI()
  const map: Record<string, RuntimeConfigPayload['system_tools'][number]> = {}
  for (const item of response.data.data.system_tools || []) {
    map[item.tool_name] = item
  }
  systemToolMetaMap.value = map
  rawConfig.value = response.data.data.content || ''
  rawConfigSnapshot.value = rawConfig.value
}

const loadRawConfig = async () => {
  loading.value = true
  try {
    await loadSystemToolMeta()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '加载配置失败')
  } finally {
    loading.value = false
  }
}

const loadToolConfig = async () => {
  if (!toolName.value) return

  loading.value = true
  try {
    const [metaResponse, toolResponse] = await Promise.all([
      getConfigAPI(),
      getSystemToolConfigAPI(toolName.value),
    ])

    const map: Record<string, RuntimeConfigPayload['system_tools'][number]> = {}
    for (const item of metaResponse.data.data.system_tools || []) {
      map[item.tool_name] = item
    }

    systemToolMetaMap.value = map
    toolConfig.value = toolResponse.data.data
    toolValues.value = { ...(toolConfig.value.values || {}) }
    emailAccounts.value = (toolConfig.value.accounts || []).map((item) => ({ ...item }))
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '加载系统工具配置失败')
  } finally {
    loading.value = false
  }
}

const reloadRawConfig = () => {
  rawConfig.value = rawConfigSnapshot.value
}

const reloadToolConfig = async () => {
  await loadToolConfig()
}

const saveRawConfig = async () => {
  saving.value = true
  try {
    const formData = new FormData()
    formData.append('data', rawConfig.value)
    const response = await updateConfigAPI(formData)
    rawConfigSnapshot.value = rawConfig.value
    ElMessage.success(response.data.data || '配置已保存')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '保存配置失败')
  } finally {
    saving.value = false
  }
}

const saveToolConfig = async () => {
  if (!toolName.value || !toolConfig.value) return

  saving.value = true
  try {
    const payload = toolConfig.value.config_type === 'email_accounts'
      ? { accounts: emailAccounts.value }
      : { values: toolValues.value }

    const response = await updateSystemToolConfigAPI(toolName.value, payload)
    ElMessage.success(response.data.data.message || '配置已保存')
    await loadToolConfig()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '保存系统工具配置失败')
  } finally {
    saving.value = false
  }
}

const initializePage = async () => {
  applyRoute()
  if (toolName.value) {
    await loadToolConfig()
    return
  }
  await loadRawConfig()
}

watch(
  () => route.query.tool,
  async () => {
    await initializePage()
  }
)

onMounted(async () => {
  await initializePage()
})
</script>

<style scoped lang="scss">
.config-page {
  min-height: calc(100vh - 62px);
  padding: 24px;
  background: linear-gradient(180deg, rgba(252, 246, 238, 0.9) 0%, rgba(255, 251, 245, 0.96) 100%);
}

.config-card {
  max-width: 1020px;
  margin: 0 auto;
  padding: 28px;
  border-radius: 24px;
  background: rgba(255, 252, 247, 0.96);
  border: 1px solid rgba(214, 132, 70, 0.14);
  box-shadow: 0 14px 36px rgba(154, 91, 39, 0.08);
}

.card-header {
  margin-bottom: 24px;

  h1 {
    margin: 0;
    font-size: 30px;
    color: #7e4b25;
  }

  p {
    margin: 10px 0 0;
    color: #8f7a68;
    line-height: 1.7;
  }
}

.content-stack {
  display: grid;
  gap: 18px;
}

.state-box,
.note-card,
.empty-box,
.guide-card,
.panel-card,
.account-card,
.status-banner {
  border-radius: 16px;
  padding: 18px;
  line-height: 1.7;
}

.state-box,
.note-card,
.empty-box,
.guide-card,
.panel-card,
.account-card {
  background: rgba(255, 249, 243, 0.94);
  color: #7e4b25;
  border: 1px solid rgba(214, 132, 70, 0.12);
}

.status-banner {
  display: grid;
  gap: 4px;
  border: 1px solid transparent;
}

.status-banner.is-ready {
  background: rgba(34, 197, 94, 0.08);
  color: #166534;
  border-color: rgba(34, 197, 94, 0.16);
}

.status-banner.is-config {
  background: rgba(201, 108, 45, 0.08);
  color: #7e4b25;
  border-color: rgba(201, 108, 45, 0.16);
}

.status-banner.is-runtime {
  background: rgba(59, 130, 246, 0.08);
  color: #1d4ed8;
  border-color: rgba(59, 130, 246, 0.16);
}

.status-banner.is-missing {
  background: rgba(239, 68, 68, 0.08);
  color: #b91c1c;
  border-color: rgba(239, 68, 68, 0.16);
}

.panel-head,
.account-head,
.footer-actions,
.quick-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-head {
  margin-bottom: 14px;

  h2 {
    margin: 0;
    color: #5e3518;
    font-size: 20px;
  }

  p {
    margin: 8px 0 0;
    color: #8f7a68;
  }
}

.quick-actions {
  flex-wrap: wrap;
  justify-content: flex-end;
}

.account-list,
.field-stack {
  display: grid;
  gap: 14px;
}

.field-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 12px;
}

.field-item {
  display: grid;
  gap: 10px;

  span {
    color: #7e4b25;
    font-weight: 600;
  }

  em {
    font-style: normal;
    color: #d05f2f;
    margin-left: 4px;
  }
}

.field-input,
.config-editor {
  width: 100%;
  border-radius: 14px;
  border: 1px solid rgba(214, 132, 70, 0.18);
  background: rgba(255, 252, 247, 0.96);
  color: #5d4838;
  outline: none;
  transition: all 0.2s ease;
}

.field-input {
  min-height: 46px;
  padding: 0 16px;
}

.config-editor {
  min-height: 520px;
  padding: 18px;
  resize: vertical;
  font-family: 'Consolas', 'Courier New', monospace;
  line-height: 1.6;
}

.field-input:focus,
.config-editor:focus {
  border-color: #c96c2d;
  box-shadow: 0 0 0 3px rgba(201, 108, 45, 0.12);
}

.guide-card {
  h2 {
    margin: 0 0 8px;
    color: #5e3518;
    font-size: 20px;
  }

  p {
    margin: 0 0 10px;
  }

  ol {
    margin: 0;
    padding-left: 20px;
  }
}

.primary-btn,
.secondary-btn,
.danger-text-btn {
  height: 44px;
  padding: 0 20px;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.primary-btn {
  background: linear-gradient(135deg, #d68446 0%, #c96c2d 100%);
  color: #fffdf9;
  box-shadow: 0 10px 20px rgba(201, 108, 45, 0.18);
}

.secondary-btn {
  background: rgba(255, 252, 247, 0.96);
  color: #7b6a5e;
  border: 1px solid rgba(214, 132, 70, 0.14);
}

.danger-text-btn {
  height: auto;
  padding: 0;
  background: transparent;
  color: #c4512f;
}

.primary-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.checkbox-item {
  align-content: end;
}

.checkbox-inline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #6f5a47;
}

@media (max-width: 900px) {
  .field-grid {
    grid-template-columns: 1fr;
  }

  .panel-head,
  .quick-actions,
  .account-head,
  .footer-actions {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
