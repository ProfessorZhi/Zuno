<script setup lang="ts">
import { computed, onActivated, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Check,
  Delete,
  Edit,
  FolderOpened,
  Plus,
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
import ZunoMiniPager from '../../components/ZunoMiniPager.vue'
import ZunoEmptyState from '../../components/zuno-settings/ZunoEmptyState.vue'
import ZunoIconButton from '../../components/zuno-settings/ZunoIconButton.vue'
import ZunoLineInput from '../../components/zuno-settings/ZunoLineInput.vue'
import ZunoSearchInput from '../../components/zuno-settings/ZunoSearchInput.vue'

type KnowledgeItem = KnowledgeResponse

const KNOWLEDGE_NAME_MIN = 2
const KNOWLEDGE_NAME_MAX = 10
const KNOWLEDGE_DESC_MIN = 10
const KNOWLEDGE_DESC_MAX = 200

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const saving = ref(false)
const keyword = ref('')
const knowledges = ref<KnowledgeItem[]>([])
const modelOptions = ref<LLMResponse[]>([])
const knowledgeProgressMap = ref<Record<string, KnowledgeProgressSummary>>({})
const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const LIST_PAGE_SIZE = 6
const listPage = ref(1)

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
const paginatedKnowledges = computed(() => filteredKnowledges.value.slice(
  (listPage.value - 1) * LIST_PAGE_SIZE,
  listPage.value * LIST_PAGE_SIZE,
))

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

const closeInlineForm = () => {
  createDialogVisible.value = false
  editDialogVisible.value = false
  resetCreateForm()
  resetEditForm()
}

const openCreateDialog = () => {
  if (createDialogVisible.value) {
    createDialogVisible.value = false
    return
  }
  resetCreateForm()
  editDialogVisible.value = false
  createDialogVisible.value = true
}

const openEditDialog = (item: KnowledgeItem) => {
  createDialogVisible.value = false
  editForm.value = {
    knowledge_id: item.id,
    knowledge_name: item.name,
    knowledge_desc: item.description || '',
  }
  editDialogVisible.value = true
}

const submitInlineForm = () => {
  if (editDialogVisible.value) {
    handleEdit()
    return
  }
  handleCreate()
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
  if (!validateKnowledge(knowledge_name, knowledge_desc)) {
    closeInlineForm()
    return
  }

  saving.value = true
  try {
    const response = await createKnowledgeAPI({
      knowledge_name: knowledge_name.trim(),
      knowledge_desc: knowledge_desc.trim(),
    })
    if (response.data.status_code === 200) {
      ElMessage.success('知识库已创建')
      closeInlineForm()
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
  if (!validateKnowledge(knowledge_name, knowledge_desc)) {
    closeInlineForm()
    return
  }

  saving.value = true
  try {
    const response = await updateKnowledgeAPI({
      knowledge_id,
      knowledge_name: knowledge_name.trim(),
      knowledge_desc: knowledge_desc.trim(),
    })
    if (response.data.status_code === 200) {
      ElMessage.success('知识库已更新')
      closeInlineForm()
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
    name: route.name === 'workspaceSettingsKnowledge' ? 'workspaceSettingsKnowledgeFile' : 'knowledge-file',
    params: { knowledgeId: item.id },
    query: { name: item.name },
  })
}

const openConfig = (item: KnowledgeItem) => {
  router.push({
    name: route.name === 'workspaceSettingsKnowledge' ? 'workspaceSettingsKnowledgeConfig' : 'knowledge-config',
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
            <h1>知识库</h1>
          </div>
        </div>
      </div>

      <div class="header-actions">
        <ZunoIconButton
          type="primary"
          :icon="Plus"
          :active="createDialogVisible"
          :title="createDialogVisible ? '收起新建知识库' : '新建知识库'"
          @click="openCreateDialog"
        />
      </div>
      <div class="settings-search-row">
        <ZunoSearchInput v-model="keyword" placeholder="搜索知识库" />
      </div>
    </section>

    <section v-if="createDialogVisible || editDialogVisible" class="knowledge-form-panel">
      <header class="inline-form-head">
        <div>
          <h2>{{ editDialogVisible ? '编辑知识库' : '新建知识库' }}</h2>
        </div>
        <div class="inline-form-actions">
          <ZunoIconButton
            class="save-action"
            type="primary"
            :icon="Check"
            :loading="saving"
            title="保存"
            @click="submitInlineForm"
          />
        </div>
      </header>

      <el-form label-position="top" class="compact-knowledge-form">
        <ZunoLineInput
          v-if="createDialogVisible"
          v-model="createForm.knowledge_name"
          label="名称"
          maxlength="10"
          show-word-limit
          placeholder="2-10 个字"
        />
        <ZunoLineInput
          v-else
          v-model="editForm.knowledge_name"
          label="名称"
          maxlength="10"
          show-word-limit
          placeholder="2-10 个字"
        />
        <ZunoLineInput
          v-if="createDialogVisible"
          v-model="createForm.knowledge_desc"
          label="说明"
          textarea
          :autosize="{ minRows: 1, maxRows: 4 }"
          maxlength="200"
          show-word-limit
          placeholder="一句话说明这个知识库收什么资料"
        />
        <ZunoLineInput
          v-else
          v-model="editForm.knowledge_desc"
          label="说明"
          textarea
          :autosize="{ minRows: 1, maxRows: 4 }"
          maxlength="200"
          show-word-limit
          placeholder="一句话说明这个知识库收什么资料"
        />
      </el-form>
    </section>

    <section class="content-card" v-loading="loading">
      <ZunoEmptyState v-if="filteredKnowledges.length === 0 && !createDialogVisible && !editDialogVisible">
        {{ keyword ? '没有匹配到知识库，换个关键词试试看吧 (´･_･`)' : '知识库还在等第一份资料，点右上角 + 开始投喂吧 (｡•̀ᴗ-)✧' }}
      </ZunoEmptyState>

      <div v-else class="knowledge-grid">
        <article v-for="item in paginatedKnowledges" :key="item.id" class="knowledge-list-row">
          <div class="knowledge-summary-row">
            <div class="knowledge-main">
              <div class="knowledge-title-line">
                <h3>{{ item.name }}</h3>
                <span class="knowledge-status-pill" :class="{ active: hasCustomConfig(item) }">
                  {{ hasCustomConfig(item) ? '已配置' : '默认' }}
                </span>
              </div>
              <p>{{ getKnowledgeDescription(item) }}</p>
            </div>

            <div class="knowledge-progress-cell" :style="{ '--knowledge-progress': `${getKnowledgeProgress(item).completionRate}%` }">
              <div class="progress-copy">
                <strong>{{ getKnowledgeProgress(item).total > 0 ? `${getKnowledgeProgress(item).completionRate}%` : '空' }}</strong>
                <span>{{ getKnowledgeProgress(item).label }}</span>
              </div>
              <div class="progress-track" :class="{ failed: getKnowledgeProgress(item).failed > 0, processing: getKnowledgeProgress(item).processing > 0 }"></div>
            </div>
          </div>

          <div class="knowledge-detail-row">
            <div class="knowledge-status-line">
              <div class="knowledge-config-line">
                <span><strong>索引</strong>{{ getConfigSummary(item).chunkModeLabel }} / {{ getConfigSummary(item).imageStrategyLabel }}</span>
                <span><strong>检索</strong>{{ getConfigSummary(item).retrievalModeLabel }} / {{ getConfigSummary(item).rerankLabel }}</span>
                <span><strong>向量</strong>{{ getConfigSummary(item).textEmbeddingLabel }}</span>
              </div>
            </div>

            <div class="knowledge-actions">
              <el-button class="knowledge-icon-button" :icon="Setting" circle title="参数配置" aria-label="参数配置" @click="openConfig(item)" />
              <el-button class="knowledge-icon-button" :icon="FolderOpened" circle title="文件管理" aria-label="文件管理" @click="openFiles(item)" />
              <el-button class="knowledge-icon-button" :icon="Edit" circle title="编辑" aria-label="编辑" @click="openEditDialog(item)" />
              <el-button class="knowledge-icon-button danger" type="danger" plain :icon="Delete" circle title="删除" aria-label="删除" @click="handleDelete(item)" />
            </div>
          </div>

          <div class="knowledge-meta-line">
            <span>{{ item.count || 0 }} 文件</span>
            <span>{{ item.file_size || '0B' }}</span>
            <span>{{ formatDate(item.update_time || item.create_time) }}</span>
          </div>
        </article>
      </div>
      <ZunoMiniPager v-model:page="listPage" class="settings-list-pager" :total="filteredKnowledges.length" :page-size="LIST_PAGE_SIZE" />
    </section>

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
.content-card,
.knowledge-form-panel {
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

.content-card {
  padding: 24px;
}

.knowledge-form-panel {
  display: grid;
  gap: 12px;
  padding: 18px 22px 20px;
  background:
    linear-gradient(180deg, rgba(255, 253, 250, 0.96), rgba(255, 250, 245, 0.88)),
    rgba(255, 255, 255, 0.84);
  animation: knowledge-panel-rise 180ms cubic-bezier(.2, .8, .2, 1) both;
}

.inline-form-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.inline-form-head h2 {
  margin: 0;
  color: #2f241d;
  font-size: 17px;
}

.inline-form-head p {
  margin: 4px 0 0;
  color: #8a7765;
  font-size: 12px;
}

.inline-form-actions {
  display: flex;
  gap: 7px;
  min-width: max-content;
}

.inline-form-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.knowledge-icon-button {
  width: 28px;
  height: 28px;
  min-width: 28px;
  padding: 0;
  border-radius: 999px;
  border: 1px solid rgba(245, 158, 11, 0.2);
  background: rgba(245, 158, 11, 0.08);
  color: #b45309;
}

.knowledge-icon-button.active {
  border-color: rgba(245, 158, 11, 0.38);
  background: #f59e0b;
  color: #ffffff;
  box-shadow: 0 10px 22px rgba(245, 158, 11, 0.18);
}

.compact-knowledge-form :deep(.el-form-item) {
  margin-bottom: 10px;
}

.compact-knowledge-form :deep(.el-form-item__label) {
  color: #7b6b5c;
  font-size: 12px;
  font-weight: 620;
}

.compact-knowledge-form :deep(.el-input__wrapper),
.compact-knowledge-form :deep(.el-textarea__inner) {
  min-height: 34px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 0 0 1px rgba(214, 132, 70, 0.12) inset;
}

.compact-knowledge-form :deep(.el-textarea__inner) {
  padding-top: 7px;
  resize: none;
}

@keyframes knowledge-panel-rise {
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
  gap: 0;
}

.knowledge-list-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 8px;
  min-width: 0;
  padding: 14px 2px 13px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.14);
  background: transparent;
  transition: background 160ms ease, border-color 160ms ease;
}

.knowledge-list-row:last-child {
  border-bottom: 0;
}

.knowledge-list-row:hover {
  border-color: rgba(245, 158, 11, 0.16);
  background: rgba(245, 158, 11, 0.025);
}

.knowledge-summary-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(220px, 0.42fr);
  align-items: end;
  gap: 18px;
  min-width: 0;
}

.knowledge-main {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.knowledge-title-line {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.knowledge-title-line h3 {
  margin: 0;
  min-width: 0;
  color: #111827;
  font-size: 15px;
  font-weight: 760;
  line-height: 1.28;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.knowledge-main p {
  margin: 0;
  color: #64748b;
  font-size: 12px;
  line-height: 1.45;
  display: -webkit-box;
  overflow: hidden;
  word-break: break-word;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.knowledge-status-pill {
  flex: 0 0 auto;
  min-height: 18px;
  padding: 0 7px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.12);
  color: #64748b;
  font-size: 10.5px;
  font-weight: 650;
  line-height: 18px;
  white-space: nowrap;
}

.knowledge-status-pill.active {
  background: rgba(245, 158, 11, 0.12);
  color: #b45309;
}

.knowledge-detail-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  min-width: 0;
}

.knowledge-status-line {
  display: flex;
  align-items: center;
  flex: 1 1 auto;
  gap: 8px 18px;
  min-width: 0;
}

.knowledge-meta-line,
.knowledge-config-line {
  display: flex;
  align-items: center;
  min-width: 0;
  color: #8a99ad;
  font-size: 11px;
  line-height: 1.35;
}

.knowledge-meta-line {
  flex: 1 1 100%;
  gap: 6px 10px;
  margin-top: -1px;
  padding-top: 1px;
  color: #94a3b8;
}

.knowledge-meta-line span {
  position: relative;
  min-width: 0;
  white-space: nowrap;
}

.knowledge-meta-line span + span::before {
  content: '';
  display: inline-block;
  width: 3px;
  height: 3px;
  margin: 0 8px 2px 0;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.5);
}

.knowledge-config-line {
  flex: 1 1 auto;
  flex-wrap: nowrap;
  gap: 5px 14px;
  color: #64748b;
  overflow: hidden;
}

.knowledge-config-line span {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
  flex: 0 1 auto;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.knowledge-config-line strong {
  flex: 0 0 auto;
  color: #8a4b16;
  font-size: 11px;
}

.knowledge-progress-cell {
  display: grid;
  gap: 6px;
  min-width: 0;
  align-self: center;
}

.progress-copy {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
  min-width: 0;
}

.progress-copy strong {
  color: #b45309;
  font-size: 13px;
  font-weight: 760;
}

.progress-copy span {
  min-width: 0;
  color: #8a99ad;
  font-size: 10.5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.progress-track {
  position: relative;
  height: 3px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.14);
}

.progress-track::after {
  content: '';
  position: absolute;
  inset: 0 auto 0 0;
  width: var(--knowledge-progress, 0%);
  border-radius: inherit;
  background: #f59e0b;
  transition: width 220ms ease;
}

.progress-track.failed::after {
  background: #ef4444;
}

.progress-track.processing::after {
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
}

.knowledge-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex: 0 0 auto;
  gap: 7px;
  min-width: max-content;
}

.knowledge-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.knowledge-icon-button.danger {
  border-color: rgba(239, 68, 68, 0.16);
  background: rgba(239, 68, 68, 0.06);
  color: #b91c1c;
}

@media (max-width: 1200px) {
  .page-header {
    flex-wrap: wrap;
  }
}

@media (max-width: 1080px) {
  .knowledge-summary-row {
    grid-template-columns: minmax(0, 1fr) minmax(190px, 0.48fr);
  }
}

@media (max-width: 1024px) {
  .knowledge-detail-row,
  .knowledge-status-line {
    align-items: flex-start;
    flex-wrap: wrap;
  }

  .knowledge-config-line {
    flex-basis: 100%;
  }
}

@media (max-width: 960px) {
  .page-header {
    flex-direction: column;
  }

  .header-actions,
  .knowledge-actions {
    flex-wrap: wrap;
  }

  .knowledge-summary-row {
    grid-template-columns: 1fr;
    align-items: flex-start;
  }

  .knowledge-actions {
    justify-content: flex-start;
  }

}
</style>
