<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, FolderOpened, Refresh, Search } from '@element-plus/icons-vue'
import knowledgeIcon from '../../assets/knowledge.svg'
import {
  getKnowledgeListAPI,
  createKnowledgeAPI,
  updateKnowledgeAPI,
  deleteKnowledgeAPI,
  type KnowledgeResponse,
} from '../../apis/knowledge'

type KnowledgeItem = KnowledgeResponse

const router = useRouter()
const loading = ref(false)
const keyword = ref('')
const knowledges = ref<KnowledgeItem[]>([])

const createDialogVisible = ref(false)
const editDialogVisible = ref(false)
const saving = ref(false)

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
  const list = [...knowledges.value].sort((a, b) =>
    new Date(b.update_time || b.create_time).getTime() - new Date(a.update_time || a.create_time).getTime()
  )

  if (!search) return list

  return list.filter((item) => {
    const haystack = [item.name, item.description || '', item.file_size || ''].join(' ').toLowerCase()
    return haystack.includes(search)
  })
})

const fetchKnowledges = async () => {
  loading.value = true
  try {
    const response = await getKnowledgeListAPI()
    if (response.data.status_code === 200) {
      knowledges.value = response.data.data || []
      return
    }
    ElMessage.error(response.data.status_message || '加载知识库失败')
  } catch (error) {
    console.error('加载知识库失败:', error)
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

  if (cleanName.length < 2 || cleanName.length > 30) {
    ElMessage.warning('知识库名称长度需要在 2 到 30 个字符之间')
    return false
  }

  if (cleanDescription && cleanDescription.length > 200) {
    ElMessage.warning('知识库说明不能超过 200 个字符')
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
    console.error('创建知识库失败:', error)
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
    console.error('更新知识库失败:', error)
    ElMessage.error('更新知识库失败')
  } finally {
    saving.value = false
  }
}

const handleDelete = async (item: KnowledgeItem) => {
  try {
    await ElMessageBox.confirm(
      `删除后，知识库“${item.name}”及其文件索引将无法恢复。`,
      '确认删除知识库',
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
    const response = await deleteKnowledgeAPI({ knowledge_id: item.id })
    if (response.data.status_code === 200) {
      ElMessage.success('知识库已删除')
      await fetchKnowledges()
      return
    }
    ElMessage.error(response.data.status_message || '删除知识库失败')
  } catch (error) {
    console.error('删除知识库失败:', error)
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

const formatDate = (value: string) => {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN')
}

onMounted(fetchKnowledges)
</script>

<template>
  <div class="knowledge-page">
    <section class="page-header">
      <div class="header-copy">
        <div class="page-title-row">
          <img :src="knowledgeIcon" alt="知识库" class="page-icon" />
          <div>
            <h1>知识库管理</h1>
            <p>管理知识库条目与文件入口，让 RAG 配置保持清晰可控。</p>
          </div>
        </div>
      </div>

      <div class="header-actions">
        <el-input
          v-model="keyword"
          placeholder="搜索知识库名称或说明"
          clearable
          class="search-input"
        >
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
          <p>共 {{ filteredKnowledges.length }} 个知识库</p>
        </div>
      </div>

      <div v-if="filteredKnowledges.length === 0" class="empty-state">
        <h3>还没有可展示的知识库</h3>
        <p>可以先创建一个知识库，再进入文件页上传材料。</p>
      </div>

      <div v-else class="knowledge-grid">
        <article v-for="item in filteredKnowledges" :key="item.id" class="knowledge-card">
          <div class="knowledge-main">
            <div>
              <h3>{{ item.name }}</h3>
              <p>{{ item.description || '这个知识库还没有补充说明。' }}</p>
            </div>
            <div class="meta-list">
              <span>文件数 {{ item.count }}</span>
              <span>体积 {{ item.file_size || '-' }}</span>
              <span>更新于 {{ formatDate(item.update_time || item.create_time) }}</span>
            </div>
          </div>

          <div class="card-actions">
            <el-button :icon="FolderOpened" @click="openFiles(item)">文件管理</el-button>
            <el-button :icon="Edit" @click="openEditDialog(item)">编辑</el-button>
            <el-button type="danger" plain :icon="Delete" @click="handleDelete(item)">删除</el-button>
          </div>
        </article>
      </div>
    </section>

    <el-dialog v-model="createDialogVisible" title="新建知识库" width="560px">
      <el-form label-position="top">
        <el-form-item label="名称">
          <el-input v-model="createForm.knowledge_name" maxlength="30" show-word-limit />
        </el-form-item>
        <el-form-item label="说明">
          <el-input
            v-model="createForm.knowledge_desc"
            type="textarea"
            :rows="4"
            maxlength="200"
            show-word-limit
            placeholder="告诉团队这个知识库主要装什么内容。"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="编辑知识库" width="560px">
      <el-form label-position="top">
        <el-form-item label="名称">
          <el-input v-model="editForm.knowledge_name" maxlength="30" show-word-limit />
        </el-form-item>
        <el-form-item label="说明">
          <el-input
            v-model="editForm.knowledge_desc"
            type="textarea"
            :rows="4"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.knowledge-page {
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

.page-title-row {
  display: flex;
  align-items: center;
  gap: 16px;

  h1 {
    margin: 0;
    font-size: 32px;
    color: #5e3518;
  }

  p {
    margin: 8px 0 0;
    color: #8f7a68;
  }
}

.page-icon {
  width: 52px;
  height: 52px;
}

.header-actions {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.search-input {
  width: 300px;
}

.content-card {
  padding: 24px;
}

.section-head {
  margin-bottom: 16px;

  h2 {
    margin: 0;
    font-size: 22px;
    color: #5e3518;
  }

  p {
    margin: 8px 0 0;
    color: #8f7a68;
  }
}

.knowledge-grid {
  display: grid;
  gap: 16px;
}

.knowledge-card {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px;
  border-radius: 18px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 249, 243, 0.94);
}

.knowledge-main {
  display: grid;
  gap: 12px;

  h3 {
    margin: 0;
    font-size: 20px;
    color: #5e3518;
  }

  p {
    margin: 8px 0 0;
    color: #725a47;
    line-height: 1.7;
  }
}

.meta-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;

  span {
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(201, 108, 45, 0.1);
    color: #99663d;
    font-size: 13px;
  }
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 10px;
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
  .page-header,
  .knowledge-card {
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
