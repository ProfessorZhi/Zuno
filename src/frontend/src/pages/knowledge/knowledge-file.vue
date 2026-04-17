<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Delete, Refresh, Upload, View, RefreshRight, Warning } from '@element-plus/icons-vue'
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
import { apiUrl } from '../../utils/api'
import { buildStageTimeline, getPipelineStageLabel, getPipelineStatusTagType } from '../../utils/knowledge-task'
import { getRetrievalModeLabel, normalizeRetrievalMode } from '../../utils/retrieval'

const route = useRoute()
const router = useRouter()

const knowledgeId = computed(() => String(route.params.knowledgeId || ''))
const knowledgeName = computed(() => String(route.query.name || '未命名知识库'))
const retrievalModeLabel = computed(() => getRetrievalModeLabel(String(route.query.mode || 'rag')))

const loading = ref(false)
const uploading = ref(false)
const retryingTaskId = ref('')
const files = ref<KnowledgeFileResponse[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)
const taskDrawerVisible = ref(false)
const taskDetailLoading = ref(false)
const taskDetail = ref<KnowledgeTaskDetailResponse | null>(null)
const activeFileName = ref('')

let pollingTimer: ReturnType<typeof setInterval> | null = null

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
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
}

const startPolling = () => {
  stopPolling()
  pollingTimer = setInterval(async () => {
    await fetchFiles(false)
    if (!hasProcessingFiles.value) stopPolling()
  }, 10000)
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
    console.error('加载知识库文件失败', error)
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
        uploadResult?.data?.path ||
        uploadResult?.data?.url ||
        uploadResult?.data ||
        uploadResult?.path ||
        uploadResult?.url

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
      `删除后，文件“${file.file_name}”及其索引都会被移除。`,
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
    console.error('删除知识库文件失败', error)
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
      if (taskDrawerVisible.value) await openTaskDetail({ ...file, last_task_id: response.data.data?.task_id || file.last_task_id })
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
  if (isPendingStatus(file.status) || isPendingStatus(file.parse_status) || isPendingStatus(file.rag_index_status) || isPendingStatus(file.graph_index_status)) {
    return { label: '处理中', type: 'warning' as const }
  }
  return { label: '待处理', type: 'info' as const }
}

const taskTimeline = computed(() => {
  const task = taskDetail.value?.task
  if (!task) return []
  return buildStageTimeline(task.current_stage, task.status === 'failed')
})

const goBack = () => {
  router.push('/knowledge')
}

onMounted(fetchFiles)

onUnmounted(() => {
  stopPolling()
})
</script>

<template>
  <div class="knowledge-file-page">
    <section class="page-header">
      <div class="title-wrap">
        <el-button :icon="ArrowLeft" @click="goBack">返回知识库</el-button>
        <div>
          <h1>{{ knowledgeName }}</h1>
          <p>上传文件、查看阶段状态、跟踪任务事件，并在失败时直接重试。</p>
          <div class="header-meta">
            <el-tag effect="plain">{{ retrievalModeLabel }}</el-tag>
            <span>默认检索模式</span>
          </div>
        </div>
      </div>

      <div class="header-actions">
        <input ref="fileInputRef" type="file" multiple hidden @change="handleUpload" />
        <el-button :icon="Refresh" @click="fetchFiles">刷新</el-button>
        <el-button type="primary" :icon="Upload" :loading="uploading" @click="triggerUpload">上传文件</el-button>
      </div>
    </section>

    <section class="content-card" v-loading="loading">
      <div v-if="sortedFiles.length === 0" class="empty-state">
        <h3>这个知识库还没有文件</h3>
        <p>上传 PDF、Word、Markdown 或图片后，这里会显示处理阶段和最终状态。</p>
      </div>

      <div v-else class="file-grid">
        <article v-for="file in sortedFiles" :key="file.id" class="file-card">
          <div class="file-head">
            <div>
              <h3>{{ file.file_name }}</h3>
              <p>{{ getFileType(file.file_name) }} · {{ formatFileSize(file.file_size) }} · {{ new Date(file.update_time || file.create_time).toLocaleString('zh-CN') }}</p>
            </div>
            <el-tag :type="fileSummaryStatus(file).type">{{ fileSummaryStatus(file).label }}</el-tag>
          </div>

          <div class="status-pills">
            <span class="status-pill">
              <strong>解析</strong>
              <el-tag size="small" :type="getPipelineStatusTagType(file.parse_status)">{{ getPipelineStageLabel(file.parse_status) }}</el-tag>
            </span>
            <span class="status-pill">
              <strong>RAG</strong>
              <el-tag size="small" :type="getPipelineStatusTagType(file.rag_index_status)">{{ getPipelineStageLabel(file.rag_index_status) }}</el-tag>
            </span>
            <span class="status-pill">
              <strong>GraphRAG</strong>
              <el-tag size="small" :type="getPipelineStatusTagType(file.graph_index_status)">{{ getPipelineStageLabel(file.graph_index_status) }}</el-tag>
            </span>
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

    <el-drawer v-model="taskDrawerVisible" :title="`任务详情 · ${activeFileName}`" size="560px">
      <div v-loading="taskDetailLoading" class="task-drawer">
        <template v-if="taskDetail?.task">
          <div class="task-summary">
            <div class="summary-row">
              <span>任务 ID</span>
              <strong>{{ taskDetail.task.id }}</strong>
            </div>
            <div class="summary-row">
              <span>主状态</span>
              <el-tag :type="getPipelineStatusTagType(taskDetail.task.status)">{{ taskDetail.task.status }}</el-tag>
            </div>
            <div class="summary-row">
              <span>当前阶段</span>
              <strong>{{ getPipelineStageLabel(taskDetail.task.current_stage) }}</strong>
            </div>
          </div>

          <div class="timeline-strip">
            <div v-for="step in taskTimeline" :key="step.key" class="timeline-step" :class="{ done: step.done, active: step.active, failed: step.failed }">
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
          <p>这个文件还没有返回可显示的任务事件。</p>
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
.content-card {
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

  h1 {
    margin: 0;
    font-size: 30px;
    color: #5e3518;
  }

  p {
    margin: 8px 0 0;
    color: #8f7a68;
  }
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  color: #8f7a68;
  font-size: 13px;
}

.header-actions {
  display: flex;
  gap: 12px;
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

.file-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;

  h3 {
    margin: 0;
    color: #4d2d15;
  }

  p {
    margin: 8px 0 0;
    color: #806957;
  }
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

  h3 {
    margin: 0;
    color: #5e3518;
  }

  p {
    margin: 10px 0 0;
    color: #8f7a68;
  }
}

.empty-state.compact {
  padding: 24px;
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

  .file-head {
    flex-direction: column;
  }
}
</style>
