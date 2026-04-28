<template>
  <div class="config-page">
    <section class="config-card">
      <template v-if="toolName">
        <header class="card-header">
          <div>
            <h1>{{ toolConfig?.display_name || '系统工具配置' }}</h1>
            <p>{{ toolConfig?.description || '正在加载工具配置...' }}</p>
            <div v-if="toolConfig" class="tool-kind-pill">{{ visibleToolKindLabel }}</div>
          </div>
        </header>

        <div v-if="loading" class="state-box">正在加载配置...</div>

        <div v-else-if="toolConfig" class="content-stack">
          <div v-if="toolStatus" class="status-banner" :class="statusClass">
            <strong>{{ toolStatus.label }}</strong>
            <span>{{ toolStatus.detail }}</span>
          </div>

          <div v-if="toolSummaryNote" class="note-card">
            {{ toolSummaryNote }}
          </div>

          <div v-if="toolGuideSections.length > 0" class="guide-grid">
            <section
              v-for="section in toolGuideSections"
              :key="section.key"
              class="guide-card"
              :class="`is-${section.tone}`"
            >
              <span class="guide-eyebrow">{{ section.eyebrow }}</span>
              <h2>{{ section.title }}</h2>
              <p v-if="section.summary">{{ section.summary }}</p>
              <ul v-if="section.steps.length > 0">
                <li v-for="step in section.steps" :key="step">{{ step }}</li>
              </ul>
            </section>
          </div>

          <template v-if="toolConfig.config_type === 'email_accounts'">
            <section class="panel-card">
              <div class="panel-head">
                <div>
                  <h2>{{ configPanel.title }}</h2>
                  <p>{{ configPanel.description }}</p>
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
                  <h2>{{ configPanel.title }}</h2>
                  <p>{{ configPanel.description }}</p>
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

          <section v-else class="panel-card">
            <div class="panel-head">
              <div>
                <h2>{{ configPanel.title }}</h2>
                <p>{{ configPanel.description }}</p>
              </div>
            </div>
            <div class="empty-box">{{ configPanel.emptyHint }}</div>
          </section>

          <div class="footer-actions">
            <button class="secondary-btn" type="button" :disabled="checkingStatus" @click="checkToolStatus">
              {{ checkingStatus ? '检测中...' : '手动检测' }}
            </button>
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
  getSystemToolStatusAPI,
  updateConfigAPI,
  updateSystemToolConfigAPI,
  type RuntimeConfigPayload,
  type SystemToolConfigPayload,
} from '../../apis/configuration'

type ToolStatus = RuntimeConfigPayload['system_tools'][number]['status']
type EmailAccount = NonNullable<SystemToolConfigPayload['accounts']>[number]
type GuideTone = 'strategy' | 'install' | 'config'
type ToolGuideSection = {
  key: string
  eyebrow: string
  title: string
  summary: string
  steps: string[]
  tone: GuideTone
}

const route = useRoute()
const toolName = ref('')
const loading = ref(false)
const saving = ref(false)
const checkingStatus = ref(false)
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
  return toolConfig.value?.status || systemToolMetaMap.value[toolName.value]?.status || null
})

const toolKind = computed(() => toolConfig.value?.tool_kind || systemToolMetaMap.value[toolName.value]?.tool_kind || 'remote_api')

const visibleToolKindLabel = computed(() => {
  return toolKind.value === 'remote_api' ? 'API' : 'CLI'
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

const toolGuideOverrides: Record<string, Partial<Record<GuideTone, Omit<ToolGuideSection, 'key' | 'eyebrow' | 'tone'>>>> = {
  send_email: {
    strategy: {
      title: '把邮箱做成稳定槽位',
      summary: '这个工具适合先把常用发件身份预置好，运行时只引用槽位名，不再重复填写 SMTP 参数。',
      steps: ['建议按业务身份拆槽位，例如 qq-main、support-mail、office-backup。'],
    },
    install: {
      title: '先准备授权码再保存',
      summary: 'QQ、163、Gmail、Outlook 都能直接套预设 SMTP 参数，自定义服务商再改主机和端口。',
      steps: ['每个槽位都需要发件邮箱和授权码，尽量不要直接使用登录密码。'],
    },
    config: {
      title: '配置区保存邮箱槽位',
      summary: '至少保存一个可用槽位后，发送邮件工具才能稳定复用发件身份。',
      steps: ['如果团队有多个发件身份，可以在这里长期维护多组槽位。'],
    },
  },
  get_arxiv: {
    strategy: {
      title: '直接使用公开论文源',
      summary: '这个工具走公开数据源，不需要额外密钥或本机依赖。',
      steps: ['重点是运行时给出明确主题、作者或关键词，而不是在这里做预配置。'],
    },
  },
  convert_to_pdf: {
    install: {
      title: '运行机器需要 LibreOffice',
      summary: 'Docx 转 PDF 依赖本机文档转换能力，真正决定是否可用的是运行 Zuno 的那台机器。',
      steps: ['安装 LibreOffice 后，确保后端进程能找到 libreoffice 或 soffice 命令。'],
    },
  },
  convert_to_docx: {
    install: {
      title: '运行机器需要 pdf2docx',
      summary: 'PDF 转 Docx 依赖 Python 包而不是远程接口，所以前端没有额外密钥可以填写。',
      steps: ['如果状态仍显示缺依赖，请在后端运行环境安装 pdf2docx。'],
    },
  },
}

const defaultGuideSectionMap: Record<NonNullable<SystemToolConfigPayload['tool_kind']>, Record<GuideTone, Omit<ToolGuideSection, 'key' | 'eyebrow' | 'tone'>>> = {
  remote_api: {
    strategy: {
      title: '固定凭据，运行时直接复用',
      summary: '这类工具靠预置 API 参数工作，配置完成后 Agent 调用时不需要再重复输入固定认证信息。',
      steps: ['优先在这里保存长期稳定的 Key、Endpoint 或鉴权字段。'],
    },
    install: {
      title: '先准备服务商凭据',
      summary: '前端这里只负责保存参数，不会帮你申请或校验第三方服务账号。',
      steps: ['先到对应服务商控制台拿到 Key 或接口地址，再回来保存。'],
    },
    config: {
      title: '把固定参数填在配置区',
      summary: '配置区只放持久化参数，运行时变化的查询词、城市、单号等内容不在这里填写。',
      steps: [],
    },
  },
  public_data_source: {
    strategy: {
      title: '公开数据源优先',
      summary: '这类工具直接读取开放数据，不依赖远程私有 API，也不要求单独安装本机 CLI。',
      steps: ['重点是运行时输入合适的查询条件，而不是在这里维护凭据。'],
    },
    install: {
      title: '通常不需要额外安装',
      summary: '如果状态正常，就代表前端没有需要你补的全局依赖或密钥。',
      steps: ['除非后续工具实现变化，否则这里一般不需要额外准备。'],
    },
    config: {
      title: '没有持久化配置项',
      summary: '这类工具通常开箱可用，配置页更多是给你确认当前策略，而不是保存参数。',
      steps: [],
    },
  },
  smtp_protocol: {
    strategy: {
      title: '把发件能力做成可复用资产',
      summary: 'SMTP 工具的核心不是一次性填参数，而是维护好长期可复用的发件槽位。',
      steps: ['Agent 运行时优先引用槽位名，这样更稳定，也更适合多人协作。'],
    },
    install: {
      title: '依赖邮箱服务商的 SMTP 能力',
      summary: '是否可用取决于你的邮箱服务商是否开放 SMTP 以及授权码是否正确。',
      steps: ['如果供应商限制 SMTP 或授权码无效，前端保存成功也无法真正发送。'],
    },
    config: {
      title: '配置区维护邮箱槽位',
      summary: '这里保存的是长期可复用的邮箱身份，不是一次性的收件信息。',
      steps: [],
    },
  },
  local_dependency: {
    strategy: {
      title: '走本机依赖，不走远程接口',
      summary: '这类工具真正依赖的是运行环境里的可执行程序或 Python 包，因此前端没有太多可存字段。',
      steps: ['状态是否可用主要由后端对本机依赖的检测结果决定。'],
    },
    install: {
      title: '先保证运行环境具备依赖',
      summary: '如果页面显示缺依赖，优先处理安装和 PATH，而不是反复刷新这个页面。',
      steps: ['确认依赖装在运行 Zuno backend 的环境里，而不是只装在当前开发机的任意地方。'],
    },
    config: {
      title: '配置区通常为空',
      summary: '这类工具一般没有单独的持久化表单，能否使用主要取决于本机环境是否准备好。',
      steps: [],
    },
  },
}

const toolSummaryNote = computed(() => {
  return toolKind.value === 'remote_api' ? toolConfig.value?.note || '' : ''
})

const toolGuideSections = computed<ToolGuideSection[]>(() => {
  if (!toolConfig.value) return []

  const kindKey = toolKind.value as keyof typeof defaultGuideSectionMap
  const defaults = defaultGuideSectionMap[kindKey] || defaultGuideSectionMap.remote_api
  const overrides = toolGuideOverrides[toolName.value] || {}
  const note = toolConfig.value.note?.trim()

  return (['strategy', 'install', 'config'] as GuideTone[]).map((tone) => {
    const base = defaults[tone]
    const override = overrides[tone]
    const steps = [...(base.steps || []), ...(override?.steps || [])]

    if (tone === 'strategy' && note && toolKind.value !== 'remote_api') {
      steps.push(note)
    }

    return {
      key: `${toolName.value}-${tone}`,
      eyebrow: tone === 'strategy' ? '使用策略' : tone === 'install' ? '安装依赖' : '配置范围',
      title: override?.title || base.title,
      summary: override?.summary || base.summary,
      steps,
      tone,
    }
  })
})

const configPanel = computed(() => {
  switch (toolKind.value) {
    case 'smtp_protocol':
      return {
        title: '邮箱槽位',
        description: '把长期可复用的发件邮箱维护成槽位，Agent 才能按槽位稳定调用。',
        emptyHint: '还没有邮箱槽位。至少保存一个可用槽位后，发送邮件工具才能直接发送邮件。',
      }
    case 'local_dependency':
      return {
        title: '本机配置',
        description: '这类工具主要依赖运行环境，本页通常只负责展示状态和少量固定说明。',
        emptyHint: '当前没有可保存的独立配置项。优先确认运行环境依赖是否已经安装并能被 backend 检测到。',
      }
    case 'public_data_source':
      return {
        title: '配置范围',
        description: '公开数据源工具通常没有固定凭据，本页主要用于确认它是否需要额外配置。',
        emptyHint: '当前没有需要持久化保存的配置项。直接在实际调用时给出查询条件即可。',
      }
    case 'remote_api':
      return {
        title: 'API 配置',
        description: '填写这个工具访问远程服务所需的固定参数，保存后运行时会自动复用。',
        emptyHint: '这个工具当前没有额外的远程配置项，可以直接使用。',
      }
    default:
      return {
        title: '配置项',
        description: '这里展示这个工具当前支持持久化保存的配置内容。',
        emptyHint: '当前没有可保存的配置项。',
      }
  }
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

const checkToolStatus = async () => {
  if (!toolName.value) return
  checkingStatus.value = true
  try {
    const response = await getSystemToolStatusAPI(toolName.value)
    const payload = response.data.data
    if (!payload?.status) throw new Error(response.data.status_message || '检测失败')

    if (toolConfig.value) {
      toolConfig.value = {
        ...toolConfig.value,
        status: payload.status,
      }
    }
    if (systemToolMetaMap.value[toolName.value]) {
      systemToolMetaMap.value = {
        ...systemToolMetaMap.value,
        [toolName.value]: {
          ...systemToolMetaMap.value[toolName.value],
          status: payload.status,
        },
      }
    }
    ElMessage.success(`${toolConfig.value?.display_name || toolName.value} 检测完成`)
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || error?.message || '检测失败')
  } finally {
    checkingStatus.value = false
  }
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

.tool-kind-pill {
  display: inline-flex;
  align-items: center;
  margin-top: 14px;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(214, 132, 70, 0.12);
  border: 1px solid rgba(214, 132, 70, 0.22);
  color: #a45d28;
  font-size: 13px;
  font-weight: 600;
}

.content-stack {
  display: grid;
  gap: 18px;
}

.guide-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
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

.note-card {
  padding: 14px 18px;
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

.guide-card {
  display: grid;
  gap: 10px;

  h2 {
    margin: 0;
    color: #5e3518;
    font-size: 18px;
  }

  p,
  ul {
    margin: 0;
    color: #7a6554;
  }

  ul {
    padding-left: 18px;
  }
}

.guide-card.is-strategy {
  background: rgba(255, 246, 235, 0.98);
}

.guide-card.is-install {
  background: rgba(255, 249, 240, 0.98);
}

.guide-card.is-config {
  background: rgba(255, 252, 247, 0.98);
}

.guide-eyebrow {
  display: inline-flex;
  width: fit-content;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(214, 132, 70, 0.1);
  color: #a45d28;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
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
  .guide-grid,
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
