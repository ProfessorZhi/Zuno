<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowLeft,
  Delete,
  FolderOpened,
  Refresh,
  RefreshRight,
  Setting,
  Upload,
  View,
  Warning,
} from '@element-plus/icons-vue'
import {
  createKnowledgeFileAPI,
  deleteKnowledgeFileAPI,
  formatFileSize,
  getFileType,
  getKnowledgeFileListAPI,
  getKnowledgeTaskDetailAPI,
  retryKnowledgeTaskAPI,
  type KnowledgeFileResponse,
  type KnowledgeTaskDetailResponse,
} from '../../apis/knowledge-file'
import { getKnowledgeListAPI, type KnowledgeResponse } from '../../apis/knowledge'
import { apiUrl } from '../../utils/api'
import {
  buildStageTimeline,
  getFileProgressSummary,
  getPipelineStageLabel,
  getPipelineStatusTagType,
  getStatusLabel,
  summarizeKnowledgeProgress,
} from '../../utils/knowledge-task'
import { describeKnowledgeConfig, findBindingById } from '../../utils/knowledge-config'
import { getVisibleLLMsAPI, type LLMResponse } from '../../apis/llm'

const route = useRoute()
const router = useRouter()

const knowledgeId = computed(() => String(route.params.knowledgeId || ''))
const knowledgeName = computed(() => String(route.query.name || '知识库'))

const loading = ref(false)
const uploading = ref(false)
const retryingTaskId = ref('')
const files = ref<KnowledgeFileResponse[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)
const taskDrawerVisible = ref(false)
const taskDetailLoading = ref(false)
const taskDetail = ref<KnowledgeTaskDetailResponse | null>(null)
const activeFileName = ref('')
const knowledge = ref<KnowledgeResponse | null>(null)
const modelOptions = ref<LLMResponse[]>([])

let pollingTimer: ReturnType<typeof setInterval> | null = null

const configSummary = computed(() => describeKnowledgeConfig(
  knowledge.value?.knowledge_config,
  {
    textEmbedding: findBindingById(knowledge.value?.knowledge_config?.model_refs.text_embedding_model_id, modelOptions.value),
    vlEmbedding: findBindingById(knowledge.value?.knowledge_config?.model_refs.vl_embedding_model_id, modelOptions.value),
    rerank: findBindingById(knowledge.value?.knowledge_config?.model_refs.rerank_model_id, modelOptions.value),
  },
))

const knowledgeProgressSummary = computed(() => summarizeKnowledgeProgress(files.value))

const isPendingStatus = (status?: string | number | null) => {
  const normalized = String(status || '').toLowerCase()
  return ['pending', 'queued', 'running', 'process'].some((value) => normalized.includes(value))
}

const hasProcessingFiles = computed(() => {
  return files.value.some((file) => (
    isPendingStatus(file.status)
    || isPendingStatus(file.parse_status)
    || isPendingStatus(file.rag_index_status)
    || isPendingStatus(file.graph_index_status)
  ))
})

const sortedFiles = computed(() => {
  return [...files.value].sort((a, b) => (
    new Date(b.update_time || b.create_time).getTime() - new Date(a.update_time || a.create_time).getTime()
  ))
})

const stopPolling = () => {
  if (!pollingTimer) return
  clearInterval(pollingTimer)
  pollingTimer = null
}

const startPolling = () => {
  stopPolling()
  pollingTimer = setInterval(async () => {
    await fetchFiles(false)
    if (!hasProcessingFiles.value) stopPolling()
  }, 10000)
}

const fetchKnowledgeContext = async () => {
  if (!knowledgeId.value) return
  try {
    const [knowledgeResponse, llmResponse] = await Promise.all([
      getKnowledgeListAPI(),
      getVisibleLLMsAPI(),
    ])
    if (knowledgeResponse.data.status_code === 200) {
      knowledge.value = (knowledgeResponse.data.data || []).find((item) => item.id === knowledgeId.value) || null
    }
    if (llmResponse.data.status_code === 200) {
      modelOptions.value = Object.values(llmResponse.data.data || {}).flat().filter(Boolean) as LLMResponse[]
    }
  } catch (error) {
    console.error('加载知识库摘要失败', error)
  }
}

const fetchFiles = async (showLoading = true) => {
  if (!knowledgeId.value) {
    ElMessage.error('缺少知识库 ID')
    return
  }

  if (showLoading) loading.value = true
  try {
    const response = await getKnowledgeFileListAPI(knowledgeId.value)
    if (response.data.status_code === 200) {
      files.value = response.data.data || []
      if (hasProcessingFiles.value) startPolling()
      else stopPolling()
      return
    }
    ElMessage.error(response.data.status_message || '加载文件列表失败')
  } catch (error) {
    console.error('加载文件列表失败', error)
    ElMessage.error('加载文件列表失败')
  } finally {
    if (showLoading) loading.value = false
  }
}

const triggerUpload = () => {
  fileInputRef.value?.click()
}

const handleUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const list = target.files
  if (!list?.length || !knowledgeId.value) return

  const token = localStorage.getItem('token') || ''
  uploading.value = true

  try {
    for (const file of Array.from(list)) {
      const payload = new FormData()
      payload.append('file', file)

      const uploadResponse = await fetch(apiUrl('/api/v1/upload'), {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: payload,
      })

      if (!uploadResponse.ok) {
        throw new Error(`上传文件 ${file.name} 失败`)
      }

      const uploadResult = await uploadResponse.json()
      const uploadedPath =
        uploadResult?.data?.path
        || uploadResult?.data?.url
        || uploadResult?.data
        || uploadResult?.path
        || uploadResult?.url

      if (!uploadedPath) {
        throw new Error(`文件 ${file.name} 没有返回可用地址`)
      }

      const createResponse = await createKnowledgeFileAPI({
        knowledge_id: knowledgeId.value,
        file_url: uploadedPath,
      })

      if (createResponse.data.status_code !== 200) {
        throw new Error(createResponse.data.status_message || `写入知识库 ${file.name} 失败`)
      }
    }

    ElMessage.success('文件已加入知识库')
    await fetchFiles()
  } catch (error: any) {
    console.error('上传知识库文件失败', error)
    ElMessage.error(error?.message || '上传知识库文件失败')
  } finally {
    uploading.value = false
    target.value = ''
  }
}

const handleDelete = async (file: KnowledgeFileResponse) => {
  try {
    await ElMessageBox.confirm(
      `删除后，文件“${file.file_name}”和它的索引都会被移除。`,
      '确认删除文件',
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
    const response = await deleteKnowledgeFileAPI({ knowledge_file_id: file.id })
    if (response.data.status_code === 200) {
      ElMessage.success('文件已删除')
      await fetchFiles()
      return
    }
    ElMessage.error(response.data.status_message || '删除文件失败')
  } catch (error) {
    console.error('删除文件失败', error)
    ElMessage.error('删除文件失败')
  }
}

const openTaskDetail = async (file: KnowledgeFileResponse) => {
  if (!file.last_task_id) {
    ElMessage.warning('这个文件暂时没有可查看的任务记录')
    return
  }

  taskDrawerVisible.value = true
  taskDetailLoading.value = true
  activeFileName.value = file.file_name
  try {
    const response = await getKnowledgeTaskDetailAPI(file.last_task_id)
    if (response.data.status_code === 200) {
      taskDetail.value = response.data.data || null
      return
    }
    ElMessage.error(response.data.status_message || '加载任务详情失败')
  } catch (error) {
    console.error('加载任务详情失败', error)
    ElMessage.error('加载任务详情失败')
  } finally {
    taskDetailLoading.value = false
  }
}

const retryTask = async (file: KnowledgeFileResponse) => {
  if (!file.last_task_id) {
    ElMessage.warning('这个文件还没有可重试的任务')
    return
  }

  retryingTaskId.value = file.last_task_id
  try {
    const response = await retryKnowledgeTaskAPI({ task_id: file.last_task_id })
    if (response.data.status_code === 200) {
      ElMessage.success('重试任务已提交')
      await fetchFiles()
      if (taskDrawerVisible.value) {
        await openTaskDetail({ ...file, last_task_id: response.data.data?.task_id || file.last_task_id })
      }
      return
    }
    ElMessage.error(response.data.status_message || '重试任务失败')
  } catch (error) {
    console.error('重试任务失败', error)
    ElMessage.error('重试任务失败')
  } finally {
    retryingTaskId.value = ''
  }
}

const fileSummaryStatus = (file: KnowledgeFileResponse) => {
  if (file.last_error) return { label: '失败', type: 'danger' as const }
  if (file.graph_index_status === 'success') return { label: '已完成', type: 'success' as const }
  if (
    isPendingStatus(file.status)
    || isPendingStatus(file.parse_status)
    || isPendingStatus(file.rag_index_status)
    || isPendingStatus(file.graph_index_status)
  ) {
    return { label: '处理中', type: 'warning' as const }
  }
  return { label: '待处理', type: 'info' as const }
}

const taskTimeline = computed(() => {
  const task = taskDetail.value?.task
  if (!task) return []
  return buildStageTimeline(task.current_stage, task.status === 'failed')
})

const fileProgressSummary = (file: KnowledgeFileResponse) => getFileProgressSummary(file)

const goBack = () => {
  router.push('/knowledge')
}

const openConfig = () => {
  router.push({
    name: 'knowledge-config',
    params: { knowledgeId: knowledgeId.value },
    query: { name: knowledgeName.value },
  })
}

onMounted(async () => {
  await Promise.all([fetchKnowledgeContext(), fetchFiles()])
})

onUnmounted(stopPolling)
</script>

<template>
  <div class="knowledge-file-page">
    <section class="page-header">
      <div class="title-wrap">
        <el-button :icon="ArrowLeft" @click="goBack">返回知识库</el-button>
        <div>
          <h1>{{ knowledge?.name || knowledgeName }}</h1>
          <p>
            文件上传页现在只负责导入资料和查看处理进度。
            索引、检索策略、模型选择都收口到这个知识库自己的参数中心。
          </p>
        </div>
      </div>

      <div class="header-actions">
        <input ref="fileInputRef" type="file" multiple hidden @change="handleUpload" />
        <el-button :icon="Refresh" @click="fetchFiles">刷新</el-button>
        <el-button :icon="Setting" @click="openConfig">参数中心</el-button>
        <el-button type="primary" :icon="Upload" :loading="uploading" @click="triggerUpload">上传文件</el-button>
      </div>
    </section>

    <section class="config-strip">
      <article class="config-summary-card">
        <div class="summary-head">
          <div>
            <h2>当前知识库参数</h2>
            <p>这里显示这个知识库自己的索引与检索策略，首轮结果不够强时会自动补检一轮，聊天页不会再单独覆盖这些配置。</p>
          </div>
          <el-button :icon="FolderOpened" @click="openConfig">去调整参数</el-button>
        </div>
        <div class="summary-grid">
          <div class="summary-item">
            <strong>索引策略</strong>
            <span>{{ configSummary.chunkModeLabel }} / {{ configSummary.imageStrategyLabel }}</span>
          </div>
          <div class="summary-item">
            <strong>检索策略</strong>
            <span>{{ configSummary.retrievalModeLabel }} / {{ configSummary.rerankLabel }}</span>
          </div>
          <div class="summary-item">
            <strong>索引模型</strong>
            <span>{{ configSummary.textEmbeddingLabel }}</span>
          </div>
        </div>
      </article>

      <article class="config-summary-card progress-summary-card">
        <div class="summary-head">
          <div>
            <h2>索引进度</h2>
            <p>{{ knowledgeProgressSummary.label }}</p>
          </div>
          <el-tag :type="knowledgeProgressSummary.failed > 0 ? 'danger' : knowledgeProgressSummary.processing > 0 ? 'warning' : knowledgeProgressSummary.pending > 0 ? 'info' : 'success'">
            {{ getStatusLabel(knowledgeProgressSummary.processing > 0 ? 'process' : knowledgeProgressSummary.failed > 0 ? 'fail' : knowledgeProgressSummary.pending > 0 ? 'pending' : 'success') }}
          </el-tag>
        </div>
        <div class="summary-grid progress-grid">
          <div class="summary-item">
            <strong>{{ knowledgeProgressSummary.total }}</strong>
            <span>文件总数</span>
          </div>
          <div class="summary-item">
            <strong>{{ knowledgeProgressSummary.completed }}</strong>
            <span>已完成</span>
          </div>
          <div class="summary-item">
            <strong>{{ knowledgeProgressSummary.processing }}</strong>
            <span>处理中 / 待处理</span>
          </div>
        </div>
      </article>
    </section>

    <section class="content-card" v-loading="loading">
      <div v-if="sortedFiles.length === 0" class="empty-state">
        <h3>这个知识库还没有文件</h3>
        <p>上传 PDF、Word、Markdown 或图片后，这里会显示解析阶段、检索策略和图谱索引状态。</p>
      </div>

      <div v-else class="file-grid">
        <article v-for="file in sortedFiles" :key="file.id" class="file-card">
          <div class="file-head">
            <div>
              <h3>{{ file.file_name }}</h3>
              <p>{{ getFileType(file.file_name) }} / {{ formatFileSize(file.file_size) }} / {{ new Date(file.update_time || file.create_time).toLocaleString('zh-CN') }}</p>
            </div>
            <el-tag :type="fileSummaryStatus(file).type">{{ fileSummaryStatus(file).label }}</el-tag>
          </div>

          <div class="status-pills">
            <span class="status-pill">
              <strong>解析</strong>
              <el-tag size="small" :type="getPipelineStatusTagType(file.parse_status)">{{ getStatusLabel(file.parse_status) }}</el-tag>
            </span>
            <span class="status-pill">
              <strong>检索策略</strong>
              <el-tag size="small" :type="getPipelineStatusTagType(file.rag_index_status)">{{ getStatusLabel(file.rag_index_status) }}</el-tag>
            </span>
            <span class="status-pill">
              <strong>图谱</strong>
              <el-tag size="small" :type="getPipelineStatusTagType(file.graph_index_status)">{{ getStatusLabel(file.graph_index_status) }}</el-tag>
            </span>
          </div>

          <div class="file-progress-copy">
            <span>进度</span>
            <strong>{{ fileProgressSummary(file).label }}</strong>
          </div>

          <div v-if="file.last_error" class="error-banner">
            <el-icon><Warning /></el-icon>
            <span>{{ file.last_error }}</span>
          </div>

          <div class="task-meta">
            <span>最近任务：{{ file.last_task_id || '暂无' }}</span>
          </div>

          <div class="card-actions">
            <el-button size="small" :icon="View" @click="openTaskDetail(file)">任务详情</el-button>
            <el-button
              v-if="file.last_task_id"
              size="small"
              :icon="RefreshRight"
              :loading="retryingTaskId === file.last_task_id"
              @click="retryTask(file)"
            >
              重试
            </el-button>
            <el-button type="danger" plain size="small" :icon="Delete" @click="handleDelete(file)">删除</el-button>
          </div>
        </article>
      </div>
    </section>

    <el-drawer v-model="taskDrawerVisible" :title="`任务详情 / ${activeFileName}`" size="560px">
      <div v-loading="taskDetailLoading" class="task-drawer">
        <template v-if="taskDetail?.task">
          <div class="task-summary">
            <div class="summary-row">
              <span>任务 ID</span>
              <strong>{{ taskDetail.task.id }}</strong>
            </div>
            <div class="summary-row">
              <span>主状态</span>
              <el-tag :type="getPipelineStatusTagType(taskDetail.task.status)">{{ getStatusLabel(taskDetail.task.status) }}</el-tag>
            </div>
            <div class="summary-row">
              <span>当前阶段</span>
              <strong>{{ getPipelineStageLabel(taskDetail.task.current_stage) }}</strong>
            </div>
          </div>

          <div class="timeline-strip">
            <div
              v-for="step in taskTimeline"
              :key="step.key"
              class="timeline-step"
              :class="{ done: step.done, active: step.active, failed: step.failed }"
            >
              <span class="timeline-dot"></span>
              <span>{{ step.label }}</span>
            </div>
          </div>

          <div class="event-list">
            <article v-for="event in taskDetail.events" :key="event.id" class="event-card">
              <div class="event-head">
                <strong>{{ event.message }}</strong>
                <el-tag size="small" :type="getPipelineStatusTagType(event.status)">{{ getPipelineStageLabel(event.stage) }}</el-tag>
              </div>
              <div class="event-time">{{ new Date(event.create_time).toLocaleString('zh-CN') }}</div>
              <pre v-if="event.detail && Object.keys(event.detail).length > 0" class="event-detail">{{ JSON.stringify(event.detail, null, 2) }}</pre>
            </article>
          </div>
        </template>
        <div v-else class="empty-state compact">
          <h3>暂无任务详情</h3>
          <p>这个文件还没有返回可展示的任务事件。</p>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped lang="scss">
.knowledge-file-page {
  display: grid;
  gap: 20px;
  padding: 24px;
}

.page-header,
.content-card,
.config-summary-card {
  border-radius: 24px;
  border: 1px solid rgba(214, 132, 70, 0.14);
  background: rgba(255, 252, 247, 0.96);
  box-shadow: 0 16px 36px rgba(160, 95, 42, 0.08);
}

.page-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 28px;
}

.title-wrap {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.title-wrap h1 {
  margin: 0;
  font-size: 30px;
  color: #5e3518;
}

.title-wrap p {
  margin: 8px 0 0;
  color: #8f7a68;
  line-height: 1.7;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.summary-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: flex-start;
  margin-bottom: 18px;
}

.summary-head h2 {
  margin: 0;
  color: #5e3518;
}

.summary-head p {
  margin: 8px 0 0;
  color: #8f7a68;
  line-height: 1.7;
}

.summary-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.config-strip {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.progress-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.summary-item {
  display: grid;
  gap: 8px;
  padding: 16px;
  border-radius: 18px;
  background: rgba(255, 249, 243, 0.94);
  border: 1px solid rgba(214, 132, 70, 0.12);
}

.summary-item strong {
  color: #5a3115;
}

.summary-item span {
  color: #826b59;
  line-height: 1.6;
}

.content-card {
  padding: 24px;
}

.file-grid {
  display: grid;
  gap: 16px;
}

.file-card {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 20px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 249, 243, 0.94);
}

.file-progress-copy {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.7);
  color: #7a6151;
}

.file-progress-copy strong {
  color: #4f2d16;
}

.file-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.file-head h3 {
  margin: 0;
  color: #4d2d15;
}

.file-head p {
  margin: 8px 0 0;
  color: #806957;
}

.status-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.9);
  border: 1px solid rgba(214, 132, 70, 0.12);
  color: #6f543d;
}

.task-meta {
  color: #8a7563;
  font-size: 13px;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 14px;
  color: #9f4f33;
  background: rgba(255, 238, 231, 0.95);
  border: 1px solid rgba(214, 103, 70, 0.22);
}

.card-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.task-drawer {
  display: grid;
  gap: 18px;
}

.task-summary,
.event-card {
  border-radius: 18px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 249, 243, 0.92);
  padding: 14px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #725a47;
}

.summary-row + .summary-row {
  margin-top: 10px;
}

.timeline-strip {
  display: grid;
  gap: 10px;
}

.timeline-step {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #907b68;
}

.timeline-step.done {
  color: #6a543f;
}

.timeline-step.active {
  color: #6d431d;
}

.timeline-step.failed {
  color: #a14b38;
}

.timeline-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: rgba(190, 158, 129, 0.55);
}

.timeline-step.done .timeline-dot,
.timeline-step.active .timeline-dot {
  background: #cb7a3f;
}

.timeline-step.failed .timeline-dot {
  background: #d26b5c;
}

.event-list {
  display: grid;
  gap: 12px;
}

.event-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.event-time {
  margin-top: 6px;
  color: #8b7765;
  font-size: 12px;
}

.event-detail {
  margin: 10px 0 0;
  padding: 12px;
  border-radius: 12px;
  background: rgba(255, 253, 249, 0.95);
  color: #5b4738;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.empty-state {
  padding: 36px;
  border-radius: 18px;
  background: rgba(255, 249, 243, 0.94);
  text-align: center;
}

.empty-state h3 {
  margin: 0;
  color: #5e3518;
}

.empty-state p {
  margin: 10px 0 0;
  color: #8f7a68;
}

.empty-state.compact {
  padding: 24px;
}

@media (max-width: 1080px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .config-strip {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .page-header {
    flex-direction: column;
  }

  .header-actions,
  .card-actions,
  .status-pills {
    flex-wrap: wrap;
  }

  .file-head,
  .summary-head {
    flex-direction: column;
  }
}
</style>
