<script setup lang="ts">
import { computed, onActivated, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Delete,
  Edit,
  FolderOpened,
  Plus,
  Refresh,
  Search,
  Setting,
} from '@element-plus/icons-vue'
import knowledgeIcon from '../../assets/knowledge.svg'
import {
  createKnowledgeAPI,
  deleteKnowledgeAPI,
  getKnowledgeListAPI,
  updateKnowledgeAPI,
  type KnowledgeConfigPayload,
  type KnowledgeResponse,
} from '../../apis/knowledge'
import { getKnowledgeFileListAPI } from '../../apis/knowledge-file'
import { getVisibleLLMsAPI, type LLMResponse } from '../../apis/llm'
import { safeDisplayText } from '../../utils/display-text'
import { describeKnowledgeConfig, findBindingById, normalizeKnowledgeConfig } from '../../utils/knowledge-config'
import { summarizeKnowledgeProgress, type KnowledgeProgressSummary } from '../../utils/knowledge-task'

type KnowledgeItem = KnowledgeResponse

const KNOWLEDGE_NAME_MIN = 2
const KNOWLEDGE_NAME_MAX = 10
const KNOWLEDGE_DESC_MIN = 10
const KNOWLEDGE_DESC_MAX = 200

const router = useRouter()
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const knowledges = ref<KnowledgeItem[]>([])
const modelOptions = ref<LLMResponse[]>([])
const knowledgeProgressMap = ref<Record<string, KnowledgeProgressSummary>>({})
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)

const createForm = ref({
  knowledge_name: '',
  knowledge_desc: '',
})

const editForm = ref({
  knowledge_id: '',
  knowledge_name: '',
  knowledge_desc: '',
})

const filteredKnowledges = computed(() => {
  const search = keyword.value.trim().toLowerCase()
  const sorted = [...knowledges.value].sort((a, b) => (
    new Date(b.update_time || b.create_time).getTime() - new Date(a.update_time || a.create_time).getTime()
  ))

  if (!search) return sorted

  return sorted.filter((item) => (
    [item.name, item.description || '', item.file_size || '']
      .join(' ')
      .toLowerCase()
      .includes(search)
  ))
})

const getKnowledgeProgress = (item: KnowledgeItem) => (
  knowledgeProgressMap.value[item.id] || summarizeKnowledgeProgress([])
)

const getKnowledgeDescription = (item: KnowledgeItem) => (
  safeDisplayText(item.description, '\u6682\u65e0\u8bf4\u660e')
)

const isKnowledgeInputValid = (name: string, description: string) => {
  const cleanName = name.trim()
  const cleanDescription = description.trim()
  return (
    cleanName.length >= KNOWLEDGE_NAME_MIN
    && cleanName.length <= KNOWLEDGE_NAME_MAX
    && cleanDescription.length >= KNOWLEDGE_DESC_MIN
    && cleanDescription.length <= KNOWLEDGE_DESC_MAX
  )
}

const isCreateFormValid = computed(() => (
  isKnowledgeInputValid(createForm.value.knowledge_name, createForm.value.knowledge_desc)
))

const isEditFormValid = computed(() => (
  isKnowledgeInputValid(editForm.value.knowledge_name, editForm.value.knowledge_desc)
))

const fetchKnowledges = async () => {
  loading.value = true
  knowledgeProgressMap.value = {}
  try {
    const [knowledgeResponse, llmResponse] = await Promise.all([
      getKnowledgeListAPI(),
      getVisibleLLMsAPI(),
    ])

    if (knowledgeResponse.data.status_code === 200) {
      knowledges.value = knowledgeResponse.data.data || []
      const progressEntries = await Promise.all(
        knowledges.value.map(async (item) => {
          try {
            const fileResponse = await getKnowledgeFileListAPI(item.id)
            if (fileResponse.data.status_code === 200) {
              return [item.id, summarizeKnowledgeProgress(fileResponse.data.data || [])] as const
            }
          } catch (error) {
            console.error(`加载知识库 ${item.id} 进度失败`, error)
          }
          return [item.id, summarizeKnowledgeProgress([])] as const
        }),
      )
      knowledgeProgressMap.value = Object.fromEntries(progressEntries)
    } else {
      ElMessage.error(knowledgeResponse.data.status_message || '加载知识库失败')
    }

    if (llmResponse.data.status_code === 200) {
      modelOptions.value = Object.values(llmResponse.data.data || {}).flat().filter(Boolean) as LLMResponse[]
    }
  } catch (error) {
    console.error('加载知识库失败', error)
    ElMessage.error('加载知识库失败')
  } finally {
    loading.value = false
  }
}

const resetCreateForm = () => {
  createForm.value = {
    knowledge_name: '',
    knowledge_desc: '',
  }
}

const resetEditForm = () => {
  editForm.value = {
    knowledge_id: '',
    knowledge_name: '',
    knowledge_desc: '',
  }
}

const openCreateDialog = () => {
  resetCreateForm()
  createDialogVisible.value = true
}

const openEditDialog = (item: KnowledgeItem) => {
  editForm.value = {
    knowledge_id: item.id,
    knowledge_name: item.name,
    knowledge_desc: item.description || '',
  }
  editDialogVisible.value = true
}

const validateKnowledge = (name: string, description: string) => {
  const cleanName = name.trim()
  const cleanDescription = description.trim()

  if (!cleanName) {
    ElMessage.warning('请先填写知识库名称')
    return false
  }

  if (cleanName.length < KNOWLEDGE_NAME_MIN || cleanName.length > KNOWLEDGE_NAME_MAX) {
    ElMessage.warning(`知识库名称长度需要在 ${KNOWLEDGE_NAME_MIN} 到 ${KNOWLEDGE_NAME_MAX} 个字之间`)
    return false
  }

  if (!cleanDescription) {
    ElMessage.warning('请先填写知识库说明')
    return false
  }

  if (cleanDescription.length < KNOWLEDGE_DESC_MIN || cleanDescription.length > KNOWLEDGE_DESC_MAX) {
    ElMessage.warning(`知识库说明长度需要在 ${KNOWLEDGE_DESC_MIN} 到 ${KNOWLEDGE_DESC_MAX} 个字之间`)
    return false
  }

  return true
}

const handleCreate = async () => {
  const { knowledge_name, knowledge_desc } = createForm.value
  if (!validateKnowledge(knowledge_name, knowledge_desc)) return

  saving.value = true
  try {
    const response = await createKnowledgeAPI({
      knowledge_name: knowledge_name.trim(),
      knowledge_desc: knowledge_desc.trim(),
    })
    if (response.data.status_code === 200) {
      ElMessage.success('知识库已创建')
      createDialogVisible.value = false
      await fetchKnowledges()
      return
    }
    ElMessage.error(response.data.status_message || '创建知识库失败')
  } catch (error) {
    console.error('创建知识库失败', error)
    ElMessage.error('创建知识库失败')
  } finally {
    saving.value = false
  }
}

const handleEdit = async () => {
  const { knowledge_id, knowledge_name, knowledge_desc } = editForm.value
  if (!validateKnowledge(knowledge_name, knowledge_desc)) return

  saving.value = true
  try {
    const response = await updateKnowledgeAPI({
      knowledge_id,
      knowledge_name: knowledge_name.trim(),
      knowledge_desc: knowledge_desc.trim(),
    })
    if (response.data.status_code === 200) {
      ElMessage.success('知识库已更新')
      editDialogVisible.value = false
      await fetchKnowledges()
      return
    }
    ElMessage.error(response.data.status_message || '更新知识库失败')
  } catch (error) {
    console.error('更新知识库失败', error)
    ElMessage.error('更新知识库失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (item: KnowledgeItem) => {
  try {
    await ElMessageBox.confirm(
      `删除后，知识库“${item.name}”以及它的文件索引将无法恢复。`,
      '确认删除知识库',
      {
        confirmButtonText: '确认删除',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
  } catch {
    return
  }

  try {
    const response = await deleteKnowledgeAPI({ knowledge_id: item.id })
    if (response.data.status_code === 200) {
      ElMessage.success('知识库已删除')
      await fetchKnowledges()
      return
    }
    ElMessage.error(response.data.status_message || '删除知识库失败')
  } catch (error) {
    console.error('删除知识库失败', error)
    ElMessage.error('删除知识库失败')
  }
}

const openFiles = (item: KnowledgeItem) => {
  router.push({
    name: 'knowledge-file',
    params: { knowledgeId: item.id },
    query: { name: item.name },
  })
}

const openConfig = (item: KnowledgeItem) => {
  router.push({
    name: 'knowledge-config',
    params: { knowledgeId: item.id },
    query: { name: item.name },
  })
}

const formatDate = (value: string) => {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN')
}

const getConfigSummary = (item: KnowledgeItem) => {
  const config = normalizeKnowledgeConfig(item.knowledge_config as Partial<KnowledgeConfigPayload> | null)
  return describeKnowledgeConfig(config, {
    textEmbedding: findBindingById(config.model_refs.text_embedding_model_id, modelOptions.value),
    vlEmbedding: findBindingById(config.model_refs.vl_embedding_model_id, modelOptions.value),
    rerank: findBindingById(config.model_refs.rerank_model_id, modelOptions.value),
  })
}

const hasCustomConfig = (item: KnowledgeItem) => Boolean(item.knowledge_config)

onMounted(fetchKnowledges)
onActivated(fetchKnowledges)
</script>

<template>
  <div class="knowledge-page">
    <section class="page-header">
      <div class="header-copy">
        <div class="page-title-row">
          <img :src="knowledgeIcon" alt="知识库" class="page-icon" />
          <div>
            <h1>知识库管理</h1>
            <p>知识库自己负责索引和检索策略。首轮结果不够强时，会自动补检一轮。聊天页只选知识库，模型页只维护资源池。</p>
          </div>
        </div>
      </div>

      <div class="header-actions">
        <el-input v-model="keyword" clearable placeholder="搜索知识库" class="search-input">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button :icon="Refresh" @click="fetchKnowledges">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新建知识库</el-button>
      </div>
    </section>

    <section class="content-card" v-loading="loading">
      <div class="section-head">
        <div>
          <h2>知识库列表</h2>
          <p>参数配置、索引模型和检索策略都绑定在知识库本身，不再分散在聊天页和模型页。</p>
        </div>
      </div>

      <div v-if="filteredKnowledges.length === 0" class="empty-state">
        <h3>还没有知识库</h3>
        <p>先创建一个知识库，再去上传文件和配置参数。</p>
      </div>

      <div v-else class="knowledge-grid">
        <article v-for="item in filteredKnowledges" :key="item.id" class="knowledge-card">
          <div class="card-head">
        <div class="card-copy">
          <h3>{{ item.name }}</h3>
          <p>{{ getKnowledgeDescription(item) }}</p>
        </div>
            <span class="config-badge" :class="{ active: hasCustomConfig(item) }">
              {{ hasCustomConfig(item) ? '已配置参数' : '默认参数' }}
            </span>
          </div>

          <div class="meta-row">
            <span>文件数 {{ item.count }}</span>
            <span>体积 {{ item.file_size }}</span>
            <span>更新时间 {{ formatDate(item.update_time || item.create_time) }}</span>
          </div>

          <div class="summary-grid">
            <div class="summary-item">
              <strong>索引策略</strong>
              <span>{{ getConfigSummary(item).chunkModeLabel }} / {{ getConfigSummary(item).imageStrategyLabel }}</span>
            </div>
            <div class="summary-item">
              <strong>检索策略</strong>
              <span>{{ getConfigSummary(item).retrievalModeLabel }} / {{ getConfigSummary(item).rerankLabel }}</span>
            </div>
            <div class="summary-item">
              <strong>文本 Embedding</strong>
              <span>{{ getConfigSummary(item).textEmbeddingLabel }}</span>
            </div>
          </div>

          <div class="progress-row">
            <div>
              <strong>索引进度</strong>
              <span>{{ getKnowledgeProgress(item).label }}</span>
            </div>
            <el-tag
              size="small"
              :type="getKnowledgeProgress(item).failed > 0 ? 'danger' : getKnowledgeProgress(item).processing > 0 ? 'warning' : getKnowledgeProgress(item).pending > 0 ? 'info' : getKnowledgeProgress(item).total > 0 ? 'success' : 'info'"
            >
              {{ getKnowledgeProgress(item).total > 0 ? `${getKnowledgeProgress(item).completionRate}%` : '暂无文件' }}
            </el-tag>
          </div>

          <div class="card-actions">
            <el-button :icon="Setting" @click="openConfig(item)">参数配置</el-button>
            <el-button :icon="FolderOpened" @click="openFiles(item)">文件管理</el-button>
            <el-button :icon="Edit" @click="openEditDialog(item)">编辑</el-button>
            <el-button type="danger" plain :icon="Delete" @click="handleDelete(item)">删除</el-button>
          </div>
        </article>
      </div>
    </section>

    <el-dialog v-model="createDialogVisible" title="新建知识库" width="620px">
      <el-form label-position="top">
        <el-form-item label="名称">
          <el-input v-model="createForm.knowledge_name" maxlength="10" show-word-limit />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="createForm.knowledge_desc" type="textarea" :rows="5" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!isCreateFormValid" :loading="saving" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="编辑知识库" width="620px">
      <el-form label-position="top">
        <el-form-item label="名称">
          <el-input v-model="editForm.knowledge_name" maxlength="10" show-word-limit />
        </el-form-item>
        <el-form-item label="说明">
          <el-input v-model="editForm.knowledge_desc" type="textarea" :rows="5" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!isEditFormValid" :loading="saving" @click="handleEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.knowledge-page {
  display: grid;
  gap: 20px;
  padding: 24px;
  min-width: 0;
}

.page-header,
.content-card {
  border-radius: 24px;
  border: 1px solid rgba(214, 132, 70, 0.14);
  background: rgba(255, 252, 247, 0.96);
  box-shadow: 0 16px 36px rgba(160, 95, 42, 0.08);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  padding: 28px;
}

.page-header > * {
  min-width: 0;
}

.header-copy {
  flex: 1 1 420px;
  min-width: 0;
}

.page-title-row {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.page-icon {
  width: 52px;
  height: 52px;
}

.header-copy h1 {
  margin: 0;
  color: #5e3518;
  font-size: 32px;
}

.header-copy p {
  margin: 8px 0 0;
  color: #8f7a68;
  max-width: 760px;
  line-height: 1.8;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  justify-content: flex-end;
  flex-wrap: wrap;
  flex: 0 1 520px;
}

.search-input {
  width: min(320px, 100%);
}

.content-card {
  padding: 24px;
}

.section-head {
  margin-bottom: 18px;
}

.section-head h2 {
  margin: 0;
  color: #5e3518;
}

.section-head p {
  margin: 8px 0 0;
  color: #8f7a68;
}

.knowledge-grid {
  display: grid;
  gap: 16px;
}

.knowledge-card {
  display: grid;
  gap: 16px;
  padding: 20px;
  border-radius: 18px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 249, 243, 0.94);
}

.card-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
}

.card-copy {
  flex: 1 1 auto;
  min-width: 0;
}

.card-head h3 {
  margin: 0;
  color: #5e3518;
  display: -webkit-box;
  line-height: 1.28;
  overflow: hidden;
  word-break: break-word;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-head p {
  margin: 8px 0 0;
  color: #8f7a68;
  line-height: 1.6;
  display: -webkit-box;
  overflow: hidden;
  word-break: break-word;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.config-badge {
  padding: 7px 12px;
  border-radius: 999px;
  background: rgba(214, 132, 70, 0.1);
  color: #99663d;
  font-size: 13px;
  white-space: nowrap;
}

.config-badge.active {
  background: rgba(34, 197, 94, 0.12);
  color: #166534;
}

.meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.meta-row span,
.summary-item {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(201, 108, 45, 0.08);
  color: #7e4b25;
  font-size: 13px;
  min-width: 0;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.summary-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.summary-item {
  display: grid;
  gap: 6px;
  border-radius: 16px;
  padding: 14px;
}

.summary-item strong {
  color: #5a3115;
}

.summary-item span {
  color: #7f6956;
  line-height: 1.6;
  word-break: break-word;
}

.progress-row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid rgba(214, 132, 70, 0.12);
}

.progress-row strong {
  display: block;
  color: #5a3115;
}

.progress-row span {
  display: block;
  margin-top: 6px;
  color: #7f6956;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.progress-row :deep(.el-tag) {
  flex-shrink: 0;
}

.card-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: flex-start;
}

.empty-state {
  padding: 36px;
  text-align: center;
  border-radius: 18px;
  background: rgba(255, 249, 243, 0.94);
}

.empty-state h3 {
  margin: 0;
  color: #5e3518;
}

.empty-state p {
  margin: 10px 0 0;
  color: #8f7a68;
}

@media (max-width: 1200px) {
  .page-header {
    flex-wrap: wrap;
  }
}

@media (max-width: 1080px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 1024px) {
  .card-head,
  .progress-row {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 960px) {
  .page-header,
  .card-head {
    flex-direction: column;
  }

  .header-actions,
  .card-actions {
    flex-wrap: wrap;
  }

  .search-input {
    width: 100%;
  }
}
</style>
