<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, Search, Refresh, View, Hide } from '@element-plus/icons-vue'
import modelIcon from '../../assets/model.svg'
import {
  getVisibleLLMsAPI,
  searchLLMsAPI,
  createLLMAPI,
  updateLLMAPI,
  deleteLLMAPI,
  type LLMResponse,
  type CreateLLMRequest,
} from '../../apis/llm'
import { useUserStore } from '../../store/user'

const loading = ref(false)
const keyword = ref('')
const models = ref<LLMResponse[]>([])
const userStore = useUserStore()

const dialogVisible = ref(false)
const dialogLoading = ref(false)
const isEditMode = ref(false)
const showApiKey = ref(false)

const form = ref<CreateLLMRequest & { llm_id?: string }>({
  model: '',
  api_key: '',
  base_url: '',
  provider: '',
  llm_type: 'LLM',
})

let searchTimer: ReturnType<typeof setTimeout> | null = null

const sortedModels = computed(() => {
  return [...models.value].sort((a, b) => {
    const officialDiff = Number(a.user_id === '0') === Number(b.user_id === '0')
      ? 0
      : a.user_id === '0'
        ? -1
        : 1

    if (officialDiff !== 0) return officialDiff
    return new Date(b.update_time || b.create_time).getTime() - new Date(a.update_time || a.create_time).getTime()
  })
})

const isOfficial = (item: LLMResponse) => item.user_id === '0'
const isAdmin = computed(() => String(userStore.userInfo?.id || '') === '1')

const flattenModelMap = (value: Record<string, LLMResponse[]>) => {
  const result: LLMResponse[] = []
  Object.values(value || {}).forEach((list) => {
    if (Array.isArray(list)) result.push(...list)
  })
  return result
}

const fetchModels = async () => {
  loading.value = true
  try {
    const response = await getVisibleLLMsAPI()
    if (response.data.status_code === 200) {
      models.value = flattenModelMap(response.data.data || {})
      return
    }
    ElMessage.error(response.data.status_message || '加载模型列表失败')
  } catch (error) {
    console.error('加载模型列表失败:', error)
    ElMessage.error('加载模型列表失败')
  } finally {
    loading.value = false
  }
}

const searchModels = async (search: string) => {
  if (!search.trim()) {
    await fetchModels()
    return
  }

  loading.value = true
  try {
    const response = await searchLLMsAPI({ llm_name: search.trim() })
    if (response.data.status_code === 200) {
      models.value = flattenModelMap(response.data.data || {})
      return
    }
    ElMessage.error(response.data.status_message || '搜索模型失败')
  } catch (error) {
    console.error('搜索模型失败:', error)
    ElMessage.error('搜索模型失败')
  } finally {
    loading.value = false
  }
}

watch(keyword, (value) => {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    searchModels(value)
  }, 250)
})

const resetForm = () => {
  form.value = {
    model: '',
    api_key: '',
    base_url: '',
    provider: '',
    llm_type: 'LLM',
  }
  isEditMode.value = false
  showApiKey.value = false
}

const openCreateDialog = () => {
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (item: LLMResponse) => {
  if (isOfficial(item) && !isAdmin.value) {
    ElMessage.warning('只有管理员可以编辑官方模型')
    return
  }

  form.value = {
    llm_id: item.llm_id,
    model: item.model,
    api_key: item.api_key,
    base_url: item.base_url,
    provider: item.provider,
    llm_type: item.llm_type,
  }
  isEditMode.value = true
  showApiKey.value = false
  dialogVisible.value = true
}

const validateForm = () => {
  const required = ['model', 'api_key', 'base_url', 'provider', 'llm_type'] as const
  for (const key of required) {
    if (!String(form.value[key] || '').trim()) {
      ElMessage.warning('请先填写完整的模型信息')
      return false
    }
  }
  return true
}

const handleSave = async () => {
  if (!validateForm()) return

  dialogLoading.value = true
  try {
    if (isEditMode.value && form.value.llm_id) {
      const response = await updateLLMAPI({
        llm_id: form.value.llm_id,
        model: form.value.model.trim(),
        api_key: form.value.api_key.trim(),
        base_url: form.value.base_url.trim(),
        provider: form.value.provider.trim(),
        llm_type: form.value.llm_type.trim(),
      })
      if (response.data.status_code === 200) {
        ElMessage.success('模型已更新')
        dialogVisible.value = false
        await fetchModels()
        return
      }
      ElMessage.error(response.data.status_message || '更新模型失败')
      return
    }

    const response = await createLLMAPI({
      model: form.value.model.trim(),
      api_key: form.value.api_key.trim(),
      base_url: form.value.base_url.trim(),
      provider: form.value.provider.trim(),
      llm_type: form.value.llm_type.trim(),
    })
    if (response.data.status_code === 200) {
      ElMessage.success('模型已创建')
      dialogVisible.value = false
      await fetchModels()
      return
    }
    ElMessage.error(response.data.status_message || '创建模型失败')
  } catch (error) {
    console.error('保存模型失败:', error)
    ElMessage.error('保存模型失败')
  } finally {
    dialogLoading.value = false
  }
}

const handleDelete = async (item: LLMResponse) => {
  if (isOfficial(item) && !isAdmin.value) {
    ElMessage.warning('只有管理员可以删除官方模型')
    return
  }

  try {
    await ElMessageBox.confirm(
      `删除后，模型“${item.model}”不会再出现在可用模型列表中。`,
      '确认删除模型',
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
    const response = await deleteLLMAPI({ llm_id: item.llm_id })
    if (response.data.status_code === 200) {
      ElMessage.success('模型已删除')
      await fetchModels()
      return
    }
    ElMessage.error(response.data.status_message || '删除模型失败')
  } catch (error) {
    console.error('删除模型失败:', error)
    ElMessage.error('删除模型失败')
  }
}

const formatDate = (value: string) => {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN')
}

onMounted(fetchModels)
</script>

<template>
  <div class="model-page">
    <section class="page-header">
      <div class="title-block">
        <img :src="modelIcon" alt="模型" class="page-icon" />
        <div>
          <h1>模型管理</h1>
          <p>统一管理对话、嵌入和重排模型，把来源、地址和密钥信息收拢到同一页。</p>
        </div>
      </div>

      <div class="header-actions">
        <el-input v-model="keyword" clearable placeholder="搜索模型名称或供应商" class="search-input">
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button :icon="Refresh" @click="fetchModels">刷新</el-button>
        <el-button type="primary" :icon="Plus" @click="openCreateDialog">新建模型</el-button>
      </div>
    </section>

    <section class="content-card" v-loading="loading">
      <div class="section-head">
        <div>
          <h2>模型列表</h2>
          <p>官方模型优先展示。普通用户只能管理自定义模型，管理员可以维护官方模型。</p>
        </div>
      </div>

      <div v-if="sortedModels.length === 0" class="empty-state">
        <h3>还没有可展示的模型</h3>
        <p>先创建一个模型配置，工作台才能稳定切换到它。</p>
      </div>

      <div v-else class="model-grid">
        <article v-for="item in sortedModels" :key="item.llm_id" class="model-card">
          <div class="model-main">
            <div class="top-line">
              <h3>{{ item.model }}</h3>
              <span class="badge" :class="{ official: isOfficial(item) }">
                {{ isOfficial(item) ? '官方模型' : '自定义模型' }}
              </span>
            </div>

            <div class="meta-grid">
              <span>供应商 {{ item.provider }}</span>
              <span>类型 {{ item.llm_type }}</span>
              <span>地址 {{ item.base_url }}</span>
              <span>更新时间 {{ formatDate(item.update_time || item.create_time) }}</span>
            </div>
          </div>

          <div class="card-actions">
            <el-button :icon="Edit" @click="openEditDialog(item)">编辑</el-button>
            <el-button type="danger" plain :icon="Delete" @click="handleDelete(item)">
              删除
            </el-button>
          </div>
        </article>
      </div>
    </section>

    <el-dialog v-model="dialogVisible" :title="isEditMode ? '编辑模型' : '新建模型'" width="620px">
      <el-form label-position="top">
        <div class="dialog-grid">
          <el-form-item label="模型名称">
            <el-input v-model="form.model" placeholder="例如 minimax-m1" />
          </el-form-item>
          <el-form-item label="供应商">
            <el-input v-model="form.provider" placeholder="例如 MiniMax / OpenAI / SiliconFlow" />
          </el-form-item>
          <el-form-item label="模型类型">
            <el-select v-model="form.llm_type" class="full-width">
              <el-option label="LLM" value="LLM" />
              <el-option label="Embedding" value="Embedding" />
              <el-option label="Rerank" value="Rerank" />
            </el-select>
          </el-form-item>
          <el-form-item label="接口地址">
            <el-input v-model="form.base_url" placeholder="https://api.example.com/v1" />
          </el-form-item>
        </div>
        <el-form-item label="API Key">
          <el-input v-model="form.api_key" :type="showApiKey ? 'text' : 'password'" placeholder="输入模型密钥">
            <template #suffix>
              <el-icon class="toggle-icon" @click="showApiKey = !showApiKey">
                <View v-if="!showApiKey" />
                <Hide v-else />
              </el-icon>
            </template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="handleSave">
          {{ isEditMode ? '保存修改' : '创建模型' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.model-page {
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

.title-block {
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
  gap: 12px;
  align-items: flex-start;
}

.search-input {
  width: 320px;
}

.content-card {
  padding: 24px;
}

.section-head {
  margin-bottom: 16px;

  h2 {
    margin: 0;
    color: #5e3518;
  }

  p {
    margin: 8px 0 0;
    color: #8f7a68;
  }
}

.model-grid {
  display: grid;
  gap: 16px;
}

.model-card {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px;
  border-radius: 18px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 249, 243, 0.94);
}

.model-main {
  display: grid;
  gap: 14px;
}

.top-line {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;

  h3 {
    margin: 0;
    color: #5e3518;
    font-size: 20px;
  }
}

.badge {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(214, 132, 70, 0.1);
  color: #99663d;
  font-size: 13px;

  &.official {
    background: rgba(34, 197, 94, 0.1);
    color: #166534;
  }
}

.meta-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;

  span {
    padding: 6px 12px;
    border-radius: 999px;
    background: rgba(201, 108, 45, 0.08);
    color: #7e4b25;
    font-size: 13px;
  }
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dialog-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.full-width {
  width: 100%;
}

.toggle-icon {
  cursor: pointer;
}

.empty-state {
  padding: 36px;
  text-align: center;
  border-radius: 18px;
  background: rgba(255, 249, 243, 0.94);

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
  .model-card {
    flex-direction: column;
  }

  .dialog-grid {
    grid-template-columns: 1fr;
  }

  .search-input {
    width: 100%;
  }

  .header-actions,
  .card-actions {
    flex-wrap: wrap;
  }
}
</style>
