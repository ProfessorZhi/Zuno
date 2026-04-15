<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Delete, Refresh, Upload } from '@element-plus/icons-vue'
import {
  createKnowledgeFileAPI,
  deleteKnowledgeFileAPI,
  formatFileSize,
  getFileType,
  getKnowledgeFileListAPI,
  KnowledgeFileStatus,
  type KnowledgeFileResponse,
} from '../../apis/knowledge-file'
import { apiUrl } from '../../utils/api'

const route = useRoute()
const router = useRouter()

const knowledgeId = computed(() => String(route.params.knowledgeId || ''))
const knowledgeName = computed(() => String(route.query.name || '未命名知识库'))

const loading = ref(false)
const uploading = ref(false)
const files = ref<KnowledgeFileResponse[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)

let pollingTimer: ReturnType<typeof setInterval> | null = null

const isProcessingStatus = (status: string | number) => {
  const normalized = String(status || '').toUpperCase()
  return normalized.includes(KnowledgeFileStatus.PROCESS) || normalized.includes('处理中')
}

const hasProcessingFiles = computed(() => {
  return files.value.some((file) => isProcessingStatus(file.status))
})

const sortedFiles = computed(() => {
  return [...files.value].sort((a, b) => {
    return new Date(b.update_time || b.create_time).getTime() - new Date(a.update_time || a.create_time).getTime()
  })
})

const getStatusMeta = (status: string | number) => {
  const normalized = String(status || '').toUpperCase()
  if (normalized.includes(KnowledgeFileStatus.SUCCESS)) {
    return { label: '已完成', type: 'success' as const }
  }
  if (normalized.includes(KnowledgeFileStatus.FAIL)) {
    return { label: '失败', type: 'danger' as const }
  }
  return { label: '处理中', type: 'warning' as const }
}

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
    if (!hasProcessingFiles.value) {
      stopPolling()
    }
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
      if (hasProcessingFiles.value) {
        startPolling()
      } else {
        stopPolling()
      }
      return
    }
    ElMessage.error(response.data.status_message || '加载文件列表失败')
  } catch (error) {
    console.error('加载知识库文件失败:', error)
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
    console.error('上传知识库文件失败:', error)
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
      }
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
    console.error('删除知识库文件失败:', error)
    ElMessage.error('删除文件失败')
  }
}

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
          <p>上传文件、观察处理状态，并按需要删除已有索引。</p>
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
        <p>上传 PDF、Word、Markdown 或图片后，这里会显示处理进度和最终状态。</p>
      </div>

      <div v-else class="table-wrap">
        <table class="file-table">
          <thead>
            <tr>
              <th>文件名</th>
              <th>类型</th>
              <th>大小</th>
              <th>状态</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="file in sortedFiles" :key="file.id">
              <td>{{ file.file_name }}</td>
              <td>{{ getFileType(file.file_name) }}</td>
              <td>{{ formatFileSize(file.file_size) }}</td>
              <td>
                <el-tag :type="getStatusMeta(file.status).type">
                  {{ getStatusMeta(file.status).label }}
                </el-tag>
              </td>
              <td>{{ new Date(file.update_time || file.create_time).toLocaleString('zh-CN') }}</td>
              <td>
                <el-button type="danger" plain size="small" :icon="Delete" @click="handleDelete(file)">删除</el-button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
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
  align-items: center;
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

.header-actions {
  display: flex;
  gap: 12px;
}

.content-card {
  padding: 24px;
}

.table-wrap {
  overflow-x: auto;
}

.file-table {
  width: 100%;
  border-collapse: collapse;

  th,
  td {
    padding: 14px 16px;
    border-bottom: 1px solid rgba(214, 132, 70, 0.12);
    text-align: left;
    color: #725a47;
  }

  th {
    color: #5e3518;
    font-weight: 700;
    background: rgba(255, 247, 239, 0.82);
  }
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

@media (max-width: 960px) {
  .page-header {
    flex-direction: column;
  }

  .header-actions {
    flex-wrap: wrap;
  }
}
</style>
