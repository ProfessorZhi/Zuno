<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { ArrowLeft, Check, DocumentCopy, Management, PictureFilled, Cpu, Setting } from '@element-plus/icons-vue'
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

interface SelectOption {
  id: string
  name: string
  description?: string
}

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

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

const isEditing = computed(() => Boolean(route.query.id))
const pageTitle = computed(() => (isEditing.value ? '编辑智能体' : '创建智能体'))
const isAdmin = computed(() => String(userStore.userInfo?.id || '') === '1')

const namesFromIds = (ids: string[], options: SelectOption[]) =>
  ids.map((id) => options.find((item) => item.id === id)?.name).filter(Boolean) as string[]

const selectedLLMName = computed(() => llmOptions.value.find((item) => item.id === form.llm_id)?.name || '未选择')
const selectedToolNames = computed(() => namesFromIds(form.tool_ids, toolOptions.value))
const selectedMCPNames = computed(() => namesFromIds(form.mcp_ids, mcpOptions.value))
const selectedKnowledgeNames = computed(() => namesFromIds(form.knowledge_ids, knowledgeOptions.value))
const selectedSkillNames = computed(() => namesFromIds(form.agent_skill_ids, skillOptions.value))

const summaryItems = computed(() => [
  { label: '工具', value: form.tool_ids.length, names: selectedToolNames.value },
  { label: 'MCP', value: form.mcp_ids.length, names: selectedMCPNames.value },
  { label: '知识库', value: form.knowledge_ids.length, names: selectedKnowledgeNames.value },
  { label: 'Skill', value: form.agent_skill_ids.length, names: selectedSkillNames.value },
])

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
      router.push('/agent')
      return
    }

    Object.assign(form, {
      name: agent.name || '',
      description: agent.description || '',
      logo_url: agent.logo_url || '',
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
    router.push('/agent')
  } finally {
    pageLoading.value = false
  }
}

const pickLogo = () => {
  fileInputRef.value?.click()
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

const saveAgent = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  saving.value = true
  try {
    const payload: AgentCreateRequest | AgentUpdateRequest = {
      ...(isEditing.value ? { agent_id: String(route.query.id) } : {}),
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
    router.push('/agent')
  } catch (error: any) {
    console.error('saveAgent failed', error)
    ElMessage.error(error.message || (isEditing.value ? '更新智能体失败' : '创建智能体失败'))
  } finally {
    saving.value = false
  }
}

const goBack = () => {
  router.push('/agent')
}

onMounted(async () => {
  resetForm()
  await loadOptions()
  const agentId = route.query.id as string | undefined
  if (agentId) {
    await loadAgent(agentId)
  }
})
</script>

<template>
  <div class="agent-editor-page" v-loading="pageLoading || optionLoading">
    <div class="page-header">
      <div class="header-left">
        <el-button :icon="ArrowLeft" circle @click="goBack" />
        <div>
          <div class="eyebrow">AGENT STUDIO</div>
          <h2>{{ pageTitle }}</h2>
          <p>这里只展示真实可绑定的数据源，不再注入测试工具、测试 MCP 或测试知识库。</p>
        </div>
      </div>
      <div class="header-actions">
        <el-button @click="goBack">取消</el-button>
        <el-button type="primary" :icon="Check" :loading="saving" @click="saveAgent">{{ isEditing ? '保存修改' : '创建智能体' }}</el-button>
      </div>
    </div>

    <div class="editor-layout">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="editor-main">
        <section class="editor-card basic-card">
          <div class="card-title-row">
            <div>
              <div class="card-title">基本信息</div>
              <div class="card-subtitle">确定名字、头像和一句话定位，后续列表页就直接展示这里的内容。</div>
            </div>
            <el-switch v-model="form.enable_memory" active-text="启用记忆" inactive-text="关闭记忆" />
          </div>

          <div class="basic-grid">
            <div class="logo-panel">
              <div class="logo-preview">
<img :src="form.logo_url || zunoAgentAvatar" alt="智能体头像" />
              </div>
              <input ref="fileInputRef" type="file" accept="image/png,image/jpeg,image/webp,image/gif" class="hidden-file-input" @change="handleFileChange" />
              <el-button :icon="PictureFilled" :loading="uploadLoading" @click="pickLogo">上传头像</el-button>
            </div>

            <div class="basic-fields">
              <el-form-item label="智能体名称" prop="name">
                <el-input v-model="form.name" maxlength="50" show-word-limit placeholder="比如：产品需求助手" />
              </el-form-item>
              <el-form-item label="智能体描述" prop="description">
                <el-input v-model="form.description" type="textarea" :rows="4" maxlength="200" show-word-limit placeholder="一句话说明它帮用户解决什么问题。" />
              </el-form-item>
            </div>
          </div>
        </section>

        <section class="editor-card">
          <div class="card-title-row">
            <div>
              <div class="card-title">模型与系统提示词</div>
              <div class="card-subtitle">这里决定智能体的思考底座和默认行为边界。</div>
            </div>
            <el-icon class="card-icon"><Cpu /></el-icon>
          </div>

          <el-form-item label="绑定模型" prop="llm_id">
            <el-select v-model="form.llm_id" filterable placeholder="选择一个可见模型" class="full-width" no-data-text="当前没有可用模型，请先去模型页配置。">
              <el-option v-for="item in llmOptions" :key="item.id" :label="item.name" :value="item.id">
                <div class="option-line">
                  <span>{{ item.name }}</span>
                  <small>{{ item.description }}</small>
                </div>
              </el-option>
            </el-select>
          </el-form-item>

          <el-form-item label="系统提示词" prop="system_prompt">
            <el-input
              v-model="form.system_prompt"
              type="textarea"
              :rows="14"
              maxlength="5000"
              show-word-limit
              placeholder="写清楚这个智能体是谁、负责什么、有什么边界、回答时要遵守什么规则。"
            />
          </el-form-item>
        </section>

        <section class="editor-card">
          <div class="card-title-row">
            <div>
              <div class="card-title">能力挂载</div>
              <div class="card-subtitle">只绑定真正需要的能力，避免把所有东西一股脑塞给智能体。</div>
            </div>
            <el-icon class="card-icon"><Setting /></el-icon>
          </div>

          <div class="capability-grid">
            <el-form-item label="工具">
              <el-select v-model="form.tool_ids" multiple filterable collapse-tags collapse-tags-tooltip class="full-width" placeholder="选择工具" no-data-text="当前没有可用工具，请先去工具页配置。">
                <el-option v-for="item in toolOptions" :key="item.id" :label="item.name" :value="item.id">
                  <div class="option-line">
                    <span>{{ item.name }}</span>
                    <small>{{ item.description }}</small>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="MCP">
              <el-select v-model="form.mcp_ids" multiple filterable collapse-tags collapse-tags-tooltip class="full-width" placeholder="选择 MCP 服务" no-data-text="当前没有可用 MCP，请先去 MCP 页配置。">
                <el-option v-for="item in mcpOptions" :key="item.id" :label="item.name" :value="item.id">
                  <div class="option-line">
                    <span>{{ item.name }}</span>
                    <small>{{ item.description }}</small>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="知识库">
              <el-select v-model="form.knowledge_ids" multiple filterable collapse-tags collapse-tags-tooltip class="full-width" placeholder="选择知识库" no-data-text="当前没有知识库，请先去知识库页创建。">
                <el-option v-for="item in knowledgeOptions" :key="item.id" :label="item.name" :value="item.id">
                  <div class="option-line">
                    <span>{{ item.name }}</span>
                    <small>{{ item.description }}</small>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="Skill">
              <el-select v-model="form.agent_skill_ids" multiple filterable collapse-tags collapse-tags-tooltip class="full-width" placeholder="选择 Skill" no-data-text="当前没有 Skill，请先去 Skill 页创建。">
                <el-option v-for="item in skillOptions" :key="item.id" :label="item.name" :value="item.id">
                  <div class="option-line">
                    <span>{{ item.name }}</span>
                    <small>{{ item.description }}</small>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </div>
        </section>
      </el-form>

      <aside class="editor-side">
        <section class="side-card profile-card">
          <div class="side-avatar">
<img :src="form.logo_url || zunoAgentAvatar" alt="头像预览" />
          </div>
          <h3>{{ form.name || '未命名智能体' }}</h3>
          <p>{{ form.description || '这里会展示你填写的智能体描述。' }}</p>
          <div class="profile-meta">
            <span>{{ form.enable_memory ? '启用记忆' : '关闭记忆' }}</span>
            <span>模型：{{ selectedLLMName }}</span>
          </div>
        </section>

        <section class="side-card">
          <div class="side-title-row">
            <el-icon><Management /></el-icon>
            <span>已绑定能力</span>
          </div>
          <div class="summary-list">
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
        </section>

        <section class="side-card prompt-card">
          <div class="side-title-row">
            <el-icon><DocumentCopy /></el-icon>
            <span>提示词检查</span>
          </div>
          <ul>
            <li>有没有写清楚角色和目标。</li>
            <li>有没有写清楚不能做什么。</li>
            <li>是否真的只绑定了需要的工具和 MCP。</li>
          </ul>
        </section>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.agent-editor-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  padding: 26px 30px;
  border-radius: 28px;
  border: 1px solid rgba(214, 132, 70, 0.14);
  background: linear-gradient(180deg, rgba(255, 251, 245, 0.96) 0%, rgba(252, 246, 238, 0.94) 100%);
  box-shadow: 0 18px 40px rgba(140, 100, 62, 0.08);
}

.header-left {
  display: flex;
  gap: 16px;
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

.page-header h2 {
  margin: 0;
  font-size: 32px;
  color: #2f241d;
}

.page-header p {
  margin: 10px 0 0;
  color: #6f6050;
  line-height: 1.8;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.editor-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 320px;
  gap: 20px;
  align-items: start;
}

.editor-main {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.logo-preview,
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
  object-fit: cover;
}

.hidden-file-input {
  display: none;
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
}
</style>
