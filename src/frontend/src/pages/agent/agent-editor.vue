<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { ArrowLeft, Check, PictureFilled } from '@element-plus/icons-vue'
import { createAgentAPI, getAgentByIdAPI, updateAgentAPI, type AgentCreateRequest, type AgentUpdateRequest } from '../../apis/agent'
import { getVisibleLLMsAPI, type LLMResponse } from '../../apis/llm'
import { getVisibleToolsAPI, type ToolResponse } from '../../apis/tool'
import { getMCPServersAPI, type MCPServer } from '../../apis/mcp-server'
import { getKnowledgeListAPI, type KnowledgeResponse } from '../../apis/knowledge'
import { getAgentSkillsAPI, type AgentSkill } from '../../apis/agent-skill'
import { uploadFileAPI } from '../../apis/file'
import type { AgentFormData } from '../../type'
import { useUserStore } from '../../store/user'
import { zunoAgentAvatar } from '../../utils/brand'
import { USER_AVATAR_PRESETS, withUserAvatarVersion } from '../../utils/user-avatars'

interface SelectOption {
  id: string
  name: string
  description?: string
}

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const props = defineProps<{ embedded?: boolean; embeddedAgentId?: string }>()
const emit = defineEmits<{
  (event: 'close'): void
  (event: 'saved'): void
}>()

const formRef = ref<FormInstance>()
const fileInputRef = ref<HTMLInputElement | null>(null)
const pageLoading = ref(false)
const saving = ref(false)
const uploadLoading = ref(false)
const optionLoading = ref(false)

const llmOptions = ref<SelectOption[]>([])
const toolOptions = ref<SelectOption[]>([])
const mcpOptions = ref<SelectOption[]>([])
const knowledgeOptions = ref<SelectOption[]>([])
const skillOptions = ref<SelectOption[]>([])

const form = reactive<AgentFormData>({
  name: '',
  description: '',
  logo_url: '',
  tool_ids: [],
  llm_id: '',
  mcp_ids: [],
  system_prompt: '',
  knowledge_ids: [],
  agent_skill_ids: [],
  enable_memory: true,
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入智能体名称', trigger: 'blur' }],
  description: [{ required: true, message: '请输入智能体描述', trigger: 'blur' }],
  llm_id: [{ required: true, message: '请选择模型', trigger: 'change' }],
  system_prompt: [{ required: true, message: '请输入系统提示词', trigger: 'blur' }],
}

const activeAgentId = computed(() => props.embeddedAgentId || String(route.query.id || ''))
const isEmbedded = computed(() => Boolean(props.embedded))
const isEditing = computed(() => Boolean(activeAgentId.value))
const pageTitle = computed(() => (isEditing.value ? '编辑智能体' : '创建智能体'))
const isAdmin = computed(() => String(userStore.userInfo?.id || '') === '1')
const agentListRoute = computed(() => route.name === 'workspaceSettingsAgentEditor' ? { name: 'workspaceSettingsAgent' } : '/agent')
const isWorkspaceSettings = computed(() => String(route.name || '').startsWith('workspaceSettings'))

const getSettingsThreadId = (event?: Event) => {
  const target = event?.currentTarget as HTMLElement | null
  const fromEvent = target?.closest<HTMLElement>('.settings-bubble')?.dataset.settingsThreadId
  if (fromEvent) return fromEvent
  return document
    .querySelector<HTMLElement>('.settings-bubble[data-settings-section="agent"][data-settings-detail="true"]')
    ?.dataset.settingsThreadId || ''
}

const navigateInWorkspaceSettings = (location: any, event?: Event) => {
  if (isEmbedded.value) {
    emit('close')
    return
  }
  if (!isWorkspaceSettings.value) {
    router.push(location)
    return
  }
  window.dispatchEvent(new CustomEvent('workspace-settings-navigate', {
    detail: {
      location,
      threadId: getSettingsThreadId(event),
    },
  }))
}

const namesFromIds = (ids: string[], options: SelectOption[]) =>
  ids.map((id) => options.find((item) => item.id === id)?.name).filter(Boolean) as string[]

const selectedLLMName = computed(() => llmOptions.value.find((item) => item.id === form.llm_id)?.name || '未选择')
const selectedToolNames = computed(() => namesFromIds(form.tool_ids, toolOptions.value))
const selectedMCPNames = computed(() => namesFromIds(form.mcp_ids, mcpOptions.value))
const selectedKnowledgeNames = computed(() => namesFromIds(form.knowledge_ids, knowledgeOptions.value))
const selectedSkillNames = computed(() => namesFromIds(form.agent_skill_ids, skillOptions.value))
const agentAvatarPresets = USER_AVATAR_PRESETS

const summaryItems = computed(() => [
  { label: '工具', value: form.tool_ids.length, names: selectedToolNames.value },
  { label: 'MCP', value: form.mcp_ids.length, names: selectedMCPNames.value },
  { label: '知识库', value: form.knowledge_ids.length, names: selectedKnowledgeNames.value },
  { label: 'Skill', value: form.agent_skill_ids.length, names: selectedSkillNames.value },
])

const isAgentDraftComplete = () =>
  Boolean(form.name.trim() && form.description.trim() && form.llm_id && form.system_prompt.trim())

const resetForm = () => {
  Object.assign(form, {
    name: '',
    description: '',
    logo_url: '',
    tool_ids: [],
    llm_id: '',
    mcp_ids: [],
    system_prompt: '',
    knowledge_ids: [],
    agent_skill_ids: [],
    enable_memory: true,
  })
}

const normalizeLLMs = (payload: Record<string, LLMResponse[]>) => {
  const merged: SelectOption[] = []
  Object.values(payload || {}).forEach((items) => {
    if (!Array.isArray(items)) return
    items.forEach((item) => {
      merged.push({
        id: item.llm_id,
        name: item.model,
        description: [item.provider, item.llm_type].filter(Boolean).join(' / '),
      })
    })
  })
  return merged
}

const loadOptions = async () => {
  optionLoading.value = true
  try {
    const [llmRes, toolRes, mcpRes, knowledgeRes, skillRes] = await Promise.all([
      getVisibleLLMsAPI(),
      getVisibleToolsAPI(),
      getMCPServersAPI(),
      getKnowledgeListAPI(),
      getAgentSkillsAPI(),
    ])

    llmOptions.value = llmRes.data.status_code === 200 ? normalizeLLMs(llmRes.data.data || {}) : []
    toolOptions.value = toolRes.data.status_code === 200
      ? (toolRes.data.data || []).map((item: ToolResponse) => ({
          id: item.tool_id,
          name: item.display_name || item.name,
          description: item.description,
        }))
      : []
    mcpOptions.value = mcpRes.data.status_code === 200
      ? (mcpRes.data.data || []).map((item: MCPServer) => ({
          id: item.mcp_server_id,
          name: item.server_name,
          description: item.type === 'stdio' ? 'STDIO 接入' : '流式 HTTP / 远程接入',
        }))
      : []
    knowledgeOptions.value = knowledgeRes.data.status_code === 200
      ? (knowledgeRes.data.data || []).map((item: KnowledgeResponse) => ({
          id: item.id,
          name: item.name,
          description: item.description || '暂无描述',
        }))
      : []
    skillOptions.value = skillRes.data.status_code === 200
      ? (skillRes.data.data || []).map((item: AgentSkill) => ({
          id: item.id,
          name: item.name,
          description: item.description || '暂无描述',
        }))
      : []
  } catch (error) {
    console.error('loadOptions failed', error)
    ElMessage.error('加载可绑定能力失败')
  } finally {
    optionLoading.value = false
  }
}

const loadAgent = async (agentId: string) => {
  pageLoading.value = true
  try {
    const response = await getAgentByIdAPI(agentId)
    if (response.data.status_code !== 200 || !response.data.data) {
      throw new Error(response.data.status_message || '智能体不存在')
    }

    const agent = response.data.data
    if (agent.is_custom === false && !isAdmin.value) {
      ElMessage.warning('只有管理员可以编辑官方智能体')
      navigateInWorkspaceSettings(agentListRoute.value)
      return
    }

    Object.assign(form, {
      name: agent.name || '',
      description: agent.description || '',
      logo_url: withUserAvatarVersion(agent.logo_url || ''),
      tool_ids: agent.tool_ids || [],
      llm_id: agent.llm_id || '',
      mcp_ids: agent.mcp_ids || [],
      system_prompt: agent.system_prompt || '',
      knowledge_ids: agent.knowledge_ids || [],
      agent_skill_ids: agent.agent_skill_ids || [],
      enable_memory: Boolean(agent.enable_memory),
    })
  } catch (error: any) {
    console.error('loadAgent failed', error)
    ElMessage.error(error.message || '加载智能体失败')
    navigateInWorkspaceSettings(agentListRoute.value)
  } finally {
    pageLoading.value = false
  }
}

const pickLogo = () => {
  fileInputRef.value?.click()
}

const selectPresetLogo = (avatarUrl: string) => {
  form.logo_url = withUserAvatarVersion(avatarUrl)
}

const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  const isImage = ['image/png', 'image/jpeg', 'image/webp', 'image/gif'].includes(file.type)
  if (!isImage) {
    ElMessage.warning('请选择 PNG、JPG、WebP 或 GIF 图片')
    input.value = ''
    return
  }

  const isLt5M = file.size / 1024 / 1024 <= 5
  if (!isLt5M) {
    ElMessage.warning('图片大小不能超过 5MB')
    input.value = ''
    return
  }

  uploadLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    const response: any = await uploadFileAPI(formData)
    if (response.data?.status_code !== 200) {
      throw new Error(response.data?.status_message || '上传头像失败')
    }
    form.logo_url = response.data.data
    ElMessage.success('头像上传成功')
  } catch (error: any) {
    console.error('upload avatar failed', error)
    ElMessage.error(error.message || '上传头像失败')
  } finally {
    uploadLoading.value = false
    input.value = ''
  }
}

const saveAgent = async (event?: Event) => {
  if (!formRef.value) return
  const threadId = getSettingsThreadId(event)

  if (!isAgentDraftComplete()) {
    formRef.value.clearValidate()
    navigateInWorkspaceSettings(agentListRoute.value, event)
    return
  }

  try {
    await formRef.value.validate()
  } catch {
    formRef.value.clearValidate()
    navigateInWorkspaceSettings(agentListRoute.value, event)
    return
  }

  saving.value = true
  try {
    const payload: AgentCreateRequest | AgentUpdateRequest = {
      ...(isEditing.value ? { agent_id: activeAgentId.value } : {}),
      name: form.name.trim(),
      description: form.description.trim(),
      logo_url: form.logo_url,
      tool_ids: [...form.tool_ids],
      llm_id: form.llm_id,
      mcp_ids: [...form.mcp_ids],
      system_prompt: form.system_prompt.trim(),
      knowledge_ids: [...form.knowledge_ids],
      agent_skill_ids: [...form.agent_skill_ids],
      enable_memory: form.enable_memory,
    }

    const response = isEditing.value ? await updateAgentAPI(payload as AgentUpdateRequest) : await createAgentAPI(payload as AgentCreateRequest)

    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || (isEditing.value ? '更新智能体失败' : '创建智能体失败'))
    }

    ElMessage.success(isEditing.value ? '智能体已更新' : '智能体已创建')
    if (isEmbedded.value) {
      emit('saved')
      emit('close')
    } else if (isWorkspaceSettings.value) {
      window.dispatchEvent(new CustomEvent('workspace-settings-navigate', {
        detail: {
          location: agentListRoute.value,
          threadId,
        },
      }))
    } else {
      router.push(agentListRoute.value)
    }
  } catch (error: any) {
    console.error('saveAgent failed', error)
    ElMessage.error(error.message || (isEditing.value ? '更新智能体失败' : '创建智能体失败'))
  } finally {
    saving.value = false
  }
}

const goBack = (event?: Event) => {
  navigateInWorkspaceSettings(agentListRoute.value, event)
}

const initializeEditor = async () => {
  resetForm()
  await loadOptions()
  const agentId = activeAgentId.value
  if (agentId) {
    await loadAgent(agentId)
  }
}

onMounted(initializeEditor)

watch(() => props.embeddedAgentId, () => {
  if (isEmbedded.value) initializeEditor()
})
</script>

<template>
  <div class="agent-editor-page" :class="{ 'agent-inline-editor': isWorkspaceSettings || isEmbedded }" v-loading="pageLoading || optionLoading">
    <div class="page-header">
      <div class="header-left">
        <el-button v-if="!isEmbedded" class="settings-icon-button" :icon="ArrowLeft" circle title="返回智能体" aria-label="返回智能体" @click="goBack($event)" />
        <div>
          <h2>{{ pageTitle }}</h2>
        </div>
      </div>
      <div class="header-actions">
        <el-button class="settings-icon-button" type="primary" :icon="Check" circle :loading="saving" :title="isEditing ? '保存修改' : '创建智能体'" :aria-label="isEditing ? '保存修改' : '创建智能体'" @click="saveAgent($event)" />
      </div>
    </div>

    <div class="editor-layout">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="editor-main agent-config-grid">
        <div class="logo-panel agent-logo-field">
          <div class="logo-current">
            <div class="logo-preview">
              <img :src="form.logo_url || zunoAgentAvatar" alt="智能体头像" />
            </div>
            <input ref="fileInputRef" type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="hidden-file-input" @change="handleFileChange" />
            <button class="logo-upload-button" type="button" :disabled="uploadLoading" :aria-label="uploadLoading ? '头像上传中' : '上传头像'" @click="pickLogo">
              <el-icon><PictureFilled /></el-icon>
              <span class="sr-only">{{ uploadLoading ? '上传中' : '上传' }}</span>
            </button>
          </div>
          <div class="logo-presets">
            <div class="logo-presets-head">
              <span>预设头像</span>
            </div>
            <div class="preset-avatar-strip" aria-label="预设头像">
              <button
                v-for="avatar in agentAvatarPresets"
                :key="avatar"
                type="button"
                class="preset-avatar-button"
                :class="{ active: form.logo_url === avatar }"
                @click="selectPresetLogo(avatar)"
              >
                <img :src="avatar" alt="" />
              </button>
            </div>
          </div>
        </div>

        <div class="memory-toggle agent-memory-field">
          <span>{{ form.enable_memory ? '记忆开启' : '记忆关闭' }}</span>
          <el-switch v-model="form.enable_memory" />
        </div>

        <el-form-item class="agent-field field-name" label="名称" prop="name">
          <el-input v-model="form.name" maxlength="50" show-word-limit placeholder="比如：产品需求助手" />
        </el-form-item>

        <el-form-item class="agent-field field-description" label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :autosize="{ minRows: 1, maxRows: 3 }" maxlength="200" show-word-limit placeholder="一句话说明它帮用户解决什么问题。" />
        </el-form-item>

        <el-form-item class="agent-field field-model" label="模型" prop="llm_id">
          <el-select v-model="form.llm_id" filterable placeholder="选择一个可见模型" class="full-width" no-data-text="当前没有可用模型，请先去模型页配置。">
            <el-option v-for="item in llmOptions" :key="item.id" :label="item.name" :value="item.id">
              <div class="option-line">
                <span>{{ item.name }}</span>
                <small>{{ item.description }}</small>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item class="agent-field field-prompt" label="提示词" prop="system_prompt">
          <el-input
            v-model="form.system_prompt"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 6 }"
            maxlength="5000"
            show-word-limit
            placeholder="写清楚这个智能体是谁、负责什么、有什么边界、回答时要遵守什么规则。"
          />
        </el-form-item>

        <el-form-item class="agent-field field-tool" label="工具">
          <el-select v-model="form.tool_ids" multiple filterable collapse-tags collapse-tags-tooltip class="full-width" placeholder="选择工具" no-data-text="当前没有可用工具，请先去工具页配置。">
            <el-option v-for="item in toolOptions" :key="item.id" :label="item.name" :value="item.id">
              <div class="option-line">
                <span>{{ item.name }}</span>
                <small>{{ item.description }}</small>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item class="agent-field field-mcp" label="MCP">
          <el-select v-model="form.mcp_ids" multiple filterable collapse-tags collapse-tags-tooltip class="full-width" placeholder="选择 MCP 服务" no-data-text="当前没有可用 MCP，请先去 MCP 页配置。">
            <el-option v-for="item in mcpOptions" :key="item.id" :label="item.name" :value="item.id">
              <div class="option-line">
                <span>{{ item.name }}</span>
                <small>{{ item.description }}</small>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item class="agent-field field-knowledge" label="知识库">
          <el-select v-model="form.knowledge_ids" multiple filterable collapse-tags collapse-tags-tooltip class="full-width" placeholder="选择知识库" no-data-text="当前没有知识库，请先去知识库页创建。">
            <el-option v-for="item in knowledgeOptions" :key="item.id" :label="item.name" :value="item.id">
              <div class="option-line">
                <span>{{ item.name }}</span>
                <small>{{ item.description }}</small>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <el-form-item class="agent-field field-skill" label="Skill">
          <el-select v-model="form.agent_skill_ids" multiple filterable collapse-tags collapse-tags-tooltip class="full-width" placeholder="选择 Skill" no-data-text="当前没有 Skill，请先去 Skill 页创建。">
            <el-option v-for="item in skillOptions" :key="item.id" :label="item.name" :value="item.id">
              <div class="option-line">
                <span>{{ item.name }}</span>
                <small>{{ item.description }}</small>
              </div>
            </el-option>
          </el-select>
        </el-form-item>

        <div class="binding-summary">
          <div v-for="item in summaryItems" :key="item.label" class="summary-item">
            <div class="summary-head">
              <strong>{{ item.label }}</strong>
              <span>{{ item.value }}</span>
            </div>
            <div class="summary-tags">
              <el-tag v-for="name in item.names" :key="name" size="small" effect="plain">{{ name }}</el-tag>
              <span v-if="item.names.length === 0" class="empty-text">未绑定</span>
            </div>
          </div>
        </div>
      </el-form>
    </div>
  </div>
</template>

<style scoped>
.agent-editor-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 12px 4px 14px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  color: #0f172a;
}

.page-header p {
  margin: 10px 0 0;
  color: #6f6050;
  line-height: 1.8;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.header-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.settings-icon-button {
  width: 34px;
  height: 34px;
  min-width: 34px;
  padding: 0;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(255, 255, 255, 0.74);
  color: #64748b;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.settings-icon-button.el-button--primary {
  border-color: rgba(245, 158, 11, 0.26);
  background: #f59e0b;
  color: #fff;
}

.editor-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 20px;
  align-items: start;
}

.editor-main {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.agent-config-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px 16px;
  align-items: start;
}

.agent-logo-field {
  grid-column: 1 / -1;
}

.agent-memory-field {
  align-self: center;
}

.field-name {
  grid-column: span 2;
}

.field-description {
  grid-column: span 2;
}

.field-model {
  grid-column: span 2;
}

.field-prompt {
  grid-column: span 3;
}

.field-tool,
.field-mcp,
.field-knowledge,
.field-skill {
  grid-column: span 2;
}

.binding-summary {
  grid-column: 1 / -1;
}

.editor-card,
.side-card {
  border-radius: 24px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 252, 248, 0.96);
  box-shadow: 0 14px 30px rgba(120, 80, 42, 0.07);
}

.editor-card {
  padding: 24px;
}

.side-card {
  padding: 22px;
}

.card-title-row,
.side-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 18px;
}

.card-title {
  font-size: 20px;
  font-weight: 700;
  color: #2f241d;
}

.card-subtitle {
  margin-top: 6px;
  color: #7b6756;
  line-height: 1.7;
}

.card-icon,
.side-title-row {
  color: #c47d43;
}

.basic-grid {
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr);
  gap: 24px;
}

.logo-panel {
  display: flex;
  align-items: center;
  gap: 18px;
  min-width: 0;
  width: 100%;
}

.logo-current {
  display: grid;
  justify-items: center;
  gap: 8px;
  flex: 0 0 86px;
}

.logo-preview {
  width: 76px;
  height: 76px;
  display: grid;
  place-items: center;
  overflow: visible;
  border-radius: 0;
  background: transparent;
}

.side-avatar {
  width: 140px;
  height: 140px;
  border-radius: 28px;
  overflow: hidden;
  background: rgba(214, 132, 70, 0.12);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-preview img,
.side-avatar img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.hidden-file-input {
  display: none;
}

.logo-upload-button {
  width: 30px;
  height: 30px;
  min-height: 30px;
  padding: 0;
  border: 0;
  border-radius: 999px;
  background: transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0;
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.2);
  color: #64748b;
  font: inherit;
  font-size: 12px;
  font-weight: 620;
  cursor: pointer;
  transition: color 140ms ease, background 140ms ease, box-shadow 140ms ease, transform 140ms ease;
}

.logo-upload-button:hover {
  color: #b45309;
  background: rgba(245, 158, 11, 0.08);
  box-shadow: inset 0 0 0 1px rgba(245, 158, 11, 0.32);
}

.logo-upload-button:active {
  transform: scale(0.96);
}

.logo-upload-button:disabled {
  opacity: 0.55;
  cursor: progress;
}

.logo-presets {
  min-width: 0;
  flex: 1 1 auto;
  display: grid;
  gap: 8px;
}

.logo-presets-head {
  color: #64748b;
  font-size: 12px;
  font-weight: 620;
}

.preset-avatar-strip {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 9px;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 2px 2px 8px;
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.28) transparent;
  scroll-snap-type: x proximity;
}

.preset-avatar-strip::-webkit-scrollbar {
  height: 4px;
}

.preset-avatar-strip::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.24);
}

.preset-avatar-strip::-webkit-scrollbar-track {
  background: transparent;
}

.preset-avatar-button {
  position: relative;
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  cursor: pointer;
  display: grid;
  place-items: center;
  opacity: 0.76;
  scroll-snap-align: start;
  transition: opacity 140ms ease, transform 140ms ease, filter 140ms ease;
}

.preset-avatar-button img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
  background: transparent;
}

.preset-avatar-button::after {
  content: '';
  position: absolute;
  left: 6px;
  right: 6px;
  bottom: -3px;
  height: 2px;
  border-radius: 999px;
  background: #f59e0b;
  opacity: 0;
  transform: scaleX(0.45);
  transition: opacity 140ms ease, transform 140ms ease;
}

.preset-avatar-button:hover,
.preset-avatar-button.active {
  opacity: 1;
  transform: translateY(-1px);
}

.preset-avatar-button.active {
  filter: drop-shadow(0 9px 18px rgba(245, 158, 11, 0.15));
}

.preset-avatar-button.active::after {
  opacity: 1;
  transform: scaleX(1);
}

.basic-fields {
  display: flex;
  flex-direction: column;
}

.full-width,
:deep(.full-width .el-select__wrapper) {
  width: 100%;
}

.option-line {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.option-line small {
  color: #8f7a67;
}

.capability-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 4px 16px;
}

.editor-side {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.profile-card {
  text-align: center;
}

.profile-card h3 {
  margin: 16px 0 8px;
  font-size: 24px;
  color: #2f241d;
}

.profile-card p {
  margin: 0;
  color: #6f6050;
  line-height: 1.8;
}

.profile-meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 16px;
  color: #8a6a4d;
  font-size: 13px;
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.summary-item {
  padding: 14px;
  border-radius: 18px;
  background: rgba(214, 132, 70, 0.06);
}

.summary-head {
  display: flex;
  justify-content: space-between;
  color: #2f241d;
}

.summary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.empty-text {
  color: #9a8571;
  font-size: 13px;
}

.prompt-card ul {
  margin: 0;
  padding-left: 18px;
  color: #6f6050;
  line-height: 1.8;
}

@media (max-width: 1080px) {
  .editor-layout {
    grid-template-columns: 1fr;
  }

  .agent-config-grid {
    grid-template-columns: 1fr;
  }

  .agent-logo-field,
  .field-name,
  .field-description,
  .field-model,
  .field-prompt,
  .field-tool,
  .field-mcp,
  .field-knowledge,
  .field-skill,
  .binding-summary {
    grid-column: 1;
  }

  .basic-grid,
  .capability-grid {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .logo-panel {
    grid-template-columns: 82px minmax(0, 1fr);
    gap: 12px;
  }

  .logo-preview {
    width: 64px;
    height: 64px;
  }
}
</style>
