<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete, View, Hide, Check, Close } from '@element-plus/icons-vue'
import modelIcon from '../../assets/model.svg'
import {
  getVisibleLLMsAPI,
  searchLLMsAPI,
  createLLMAPI,
  updateLLMAPI,
  activateLLMAPI,
  deleteLLMAPI,
  type LLMResponse,
  type CreateLLMRequest,
} from '../../apis/llm'
import { useUserStore } from '../../store/user'
import ZunoMiniPager from '../../components/ZunoMiniPager.vue'
import ZunoEmptyState from '../../components/zuno-settings/ZunoEmptyState.vue'
import ZunoIconButton from '../../components/zuno-settings/ZunoIconButton.vue'
import ZunoLineInput from '../../components/zuno-settings/ZunoLineInput.vue'
import ZunoLineSelect from '../../components/zuno-settings/ZunoLineSelect.vue'
import ZunoSearchInput from '../../components/zuno-settings/ZunoSearchInput.vue'
import ZunoSettingsHeader from '../../components/zuno-settings/ZunoSettingsHeader.vue'

const loading = ref(false)
const keyword = ref('')
const models = ref<LLMResponse[]>([])
const userStore = useUserStore()
const LIST_PAGE_SIZE = 6
const listPage = ref(1)

const dialogVisible = ref(false)
const dialogLoading = ref(false)
const activationLoadingId = ref('')
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
    const slotDiff = Number(a.model_slot === 'conversation_model') === Number(b.model_slot === 'conversation_model')
      ? 0
      : a.model_slot === 'conversation_model'
        ? -1
        : 1

    if (slotDiff !== 0) return slotDiff

    const officialDiff = Number(a.user_id === '0') === Number(b.user_id === '0')
      ? 0
      : a.user_id === '0'
        ? -1
        : 1

    if (officialDiff !== 0) return officialDiff

    return new Date(b.update_time || b.create_time).getTime() - new Date(a.update_time || a.create_time).getTime()
  })
})
const paginatedModels = computed(() => sortedModels.value.slice(
  (listPage.value - 1) * LIST_PAGE_SIZE,
  listPage.value * LIST_PAGE_SIZE,
))

const isOfficial = (item: LLMResponse) => item.user_id === '0'
const isConversationModel = (item: LLMResponse) => item.model_slot === 'conversation_model'
const isAdmin = computed(() => String(userStore.userInfo?.id || '') === '1')
const canManageItem = (item: LLMResponse) => !isOfficial(item) || isAdmin.value
const isEditingItem = (item: LLMResponse) => dialogVisible.value && isEditMode.value && form.value.llm_id === item.llm_id
const canActivateConversationModel = (item: LLMResponse) => item.llm_type === 'LLM'

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
      listPage.value = 1
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
      listPage.value = 1
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

const closeInlineForm = () => {
  dialogVisible.value = false
  resetForm()
}

const isXiaomiMimoConfig = () => {
  const provider = String(form.value.provider || '').toLowerCase()
  const baseUrl = String(form.value.base_url || '').toLowerCase()
  const modelName = String(form.value.model || '').toLowerCase().replace(/_/g, '-')
  const officialEndpoint = baseUrl.includes('xiaomimimo.com') || baseUrl.includes('token-plan')
  return officialEndpoint || (provider.includes('mimo') && modelName.startsWith('mimo-'))
}

const normalizeModelForSave = (model: string) => {
  const raw = model.trim()
  if (!isXiaomiMimoConfig()) return raw
  const withoutProviderPrefix = raw.replace(/^(xiaomi|xiaomimimo)\//i, '')
  const normalized = withoutProviderPrefix.replace(/_/g, '-')
  if (/^mimo-/i.test(normalized)) return normalized.toLowerCase()
  return raw
}

const openCreateDialog = () => {
  if (dialogVisible.value && !isEditMode.value) {
    dialogVisible.value = false
    return
  }
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = async (item: LLMResponse) => {
  if (!canManageItem(item)) {
    ElMessage.warning('只有管理员可以编辑官方模型')
    return
  }

  if (isEditingItem(item)) {
    await handleSave()
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
      return false
    }
  }
  return true
}

const handleSave = async () => {
  if (!validateForm()) {
    ElMessage.warning('请先填写完整的模型信息')
    return
  }

  dialogLoading.value = true
  try {
    const modelName = normalizeModelForSave(form.value.model)
    if (isEditMode.value && form.value.llm_id) {
      const response = await updateLLMAPI({
        llm_id: form.value.llm_id,
        model: modelName,
        api_key: form.value.api_key.trim(),
        base_url: form.value.base_url.trim(),
        provider: form.value.provider.trim(),
        llm_type: form.value.llm_type.trim(),
      })
      if (response.data.status_code === 200) {
        ElMessage.success('模型已更新')
        closeInlineForm()
        await fetchModels()
        return
      }
      ElMessage.error(response.data.status_message || '更新模型失败')
      return
    }

    const response = await createLLMAPI({
      model: modelName,
      api_key: form.value.api_key.trim(),
      base_url: form.value.base_url.trim(),
      provider: form.value.provider.trim(),
      llm_type: form.value.llm_type.trim(),
    })
    if (response.data.status_code === 200) {
      ElMessage.success('模型已创建')
      closeInlineForm()
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

const handleActivateConversationModel = async (item: LLMResponse) => {
  if (!canActivateConversationModel(item) || isConversationModel(item)) return

  activationLoadingId.value = item.llm_id
  try {
    const response = await activateLLMAPI({
      llm_id: item.llm_id,
      model_slot: 'conversation_model',
    })
    if (response.data.status_code === 200) {
      ElMessage.success(`已切换聊天模型到 ${item.model}`)
      await fetchModels()
      return
    }
    ElMessage.error(response.data.status_message || '切换聊天模型失败')
  } catch (error) {
    console.error('切换聊天模型失败:', error)
    ElMessage.error('切换聊天模型失败')
  } finally {
    activationLoadingId.value = ''
  }
}

const handleDelete = async (item: LLMResponse) => {
  if (!canManageItem(item)) {
    ElMessage.warning('只有管理员可以删除官方模型')
    return
  }

  try {
    await ElMessageBox.confirm(
      `删除后，模型“${item.model}”将不再出现在模型资源池中。`,
      '确认删除模型',
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

onMounted(fetchModels)
</script>

<template>
  <div class="model-page">
    <ZunoSettingsHeader :icon="modelIcon" title="模型">
      <template #actions>
        <ZunoIconButton
          type="primary"
          :icon="Plus"
          :active="dialogVisible && !isEditMode"
          :title="dialogVisible && !isEditMode ? '收起新建模型' : '新建模型'"
          @click="openCreateDialog"
        />
      </template>
      <template #search>
        <ZunoSearchInput v-model="keyword" placeholder="搜索模型名称或供应商" />
      </template>
    </ZunoSettingsHeader>

    <section v-if="dialogVisible" class="model-form-panel">
      <header class="inline-form-head">
        <div>
          <h2>{{ isEditMode ? '编辑模型' : '新建模型' }}</h2>
          <p>创建模型后，还需要把它设为聊天模型，聊天页才会真正走这套配置。</p>
        </div>
        <div class="inline-form-actions">
          <ZunoIconButton :icon="Close" title="关闭" @click="closeInlineForm" />
          <ZunoIconButton class="save-action" type="primary" :icon="Check" :loading="dialogLoading" title="保存" @click="handleSave" />
        </div>
      </header>

      <el-form label-position="top" class="compact-model-form">
        <div class="dialog-grid">
          <ZunoLineInput v-model="form.model" label="模型名称" placeholder="接口 model id，例如 qwen-plus / mimo-v2.5" />
          <ZunoLineInput v-model="form.provider" label="供应商" placeholder="例如 MiniMax / 通义千问 / OpenAI" />
          <ZunoLineSelect v-model="form.llm_type" label="模型类型">
            <el-option label="LLM" value="LLM" />
            <el-option label="Embedding" value="Embedding" />
            <el-option label="Rerank" value="Rerank" />
          </ZunoLineSelect>
          <ZunoLineInput v-model="form.base_url" label="接口地址" placeholder="https://api.example.com/v1" />
        </div>
        <ZunoLineInput v-model="form.api_key" label="API Key" :type="showApiKey ? 'text' : 'password'" placeholder="输入模型密钥">
          <template #suffix>
            <el-icon class="toggle-icon" @click="showApiKey = !showApiKey">
              <View v-if="!showApiKey" />
              <Hide v-else />
            </el-icon>
          </template>
        </ZunoLineInput>
      </el-form>
    </section>

    <section class="content-card" v-loading="loading">
      <ZunoEmptyState v-if="sortedModels.length === 0">
        {{ keyword ? '没有匹配到模型，换个关键词试试看吧 (´･_･`)' : '模型池空空的，点右上角 + 放进第一颗引擎吧 (ง •̀_•́)ง' }}
      </ZunoEmptyState>

      <div v-else class="model-grid">
        <article v-for="item in paginatedModels" :key="item.llm_id" class="model-card">
          <div class="model-main">
            <div class="top-line">
              <h3>{{ item.model }}</h3>
              <span class="badge" :class="{ official: isOfficial(item) }">
                {{ isOfficial(item) ? '官方模型' : '自定义模型' }}
              </span>
              <span v-if="isConversationModel(item)" class="badge active-slot">
                当前聊天模型
              </span>
            </div>

            <div class="meta-grid">
              <span :title="`供应商：${item.provider}`">{{ item.provider || 'Unknown' }}</span>
              <span :title="`类型：${item.llm_type}`">{{ item.llm_type }}</span>
            </div>
          </div>

          <div class="card-actions">
            <el-button
              v-if="canActivateConversationModel(item)"
              class="slot-button"
              :type="isConversationModel(item) ? 'warning' : 'default'"
              :plain="!isConversationModel(item)"
              :loading="activationLoadingId === item.llm_id"
              :disabled="isConversationModel(item)"
              @click="handleActivateConversationModel(item)"
            >
              {{ isConversationModel(item) ? '当前聊天模型' : '设为聊天模型' }}
            </el-button>
            <el-button
              :class="['model-icon-button', { active: isEditingItem(item) }]"
              :icon="isEditingItem(item) ? Check : Edit"
              :loading="isEditingItem(item) && dialogLoading"
              circle
              :title="isEditingItem(item) ? '保存并收起' : '编辑'"
              :aria-label="isEditingItem(item) ? '保存并收起' : '编辑'"
              @click="openEditDialog(item)"
            />
            <el-button
              v-if="!isEditingItem(item)"
              class="model-icon-button danger"
              type="danger"
              plain
              :icon="Delete"
              circle
              title="删除"
              aria-label="删除"
              @click="handleDelete(item)"
            />
          </div>
        </article>
      </div>
      <ZunoMiniPager v-model:page="listPage" class="settings-list-pager" :total="sortedModels.length" :page-size="LIST_PAGE_SIZE" />
    </section>

  </div>
</template>

<style scoped lang="scss">
.model-page {
  display: grid;
  gap: 20px;
  padding: 24px;
}

.page-header,
.content-card,
.model-form-panel {
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

.content-card {
  padding: 24px;
}

.model-form-panel {
  display: grid;
  gap: 12px;
  padding: 18px 22px 20px;
  background:
    linear-gradient(180deg, rgba(255, 253, 250, 0.96), rgba(255, 250, 245, 0.88)),
    rgba(255, 255, 255, 0.84);
  animation: model-panel-rise 180ms cubic-bezier(.2, .8, .2, 1) both;
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

.compact-model-form :deep(.el-form-item) {
  margin-bottom: 10px;
}

.compact-model-form :deep(.el-form-item__label) {
  color: #7b6b5c;
  font-size: 12px;
  font-weight: 620;
}

.compact-model-form :deep(.el-input__wrapper),
.compact-model-form :deep(.el-select__wrapper) {
  min-height: 34px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 0 0 1px rgba(214, 132, 70, 0.12) inset;
}

@keyframes model-panel-rise {
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
  gap: 0;
}

.model-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 16px;
  padding: 12px 2px;
  border: 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.model-card:last-child {
  border-bottom: 0;
}

.model-main {
  display: grid;
  gap: 6px;
  min-width: 0;
}

.top-line {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  min-width: 0;

  h3 {
    min-width: 0;
    max-width: min(42vw, 320px);
    margin: 0;
    color: #0f172a;
    font-size: 15.5px;
    font-weight: 700;
    line-height: 1.25;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.badge {
  flex: 0 0 auto;
  min-height: 18px;
  padding: 0 7px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.07);
  color: #a16207;
  font-size: 10.5px;
  line-height: 18px;

  &.official {
    background: rgba(34, 197, 94, 0.08);
    color: #15803d;
  }

  &.active-slot {
    background: rgba(249, 115, 22, 0.1);
    color: #c2410c;
  }
}

.meta-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  min-width: 0;

  span {
    display: inline-flex;
    align-items: center;
    max-width: min(100%, 260px);
    min-height: 18px;
    padding: 0 7px;
    border-radius: 999px;
    background: rgba(245, 158, 11, 0.055);
    color: #8a6a45;
    font-size: 10.5px;
    line-height: 18px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
}

.url-pill {
  max-width: min(52vw, 360px) !important;
}

.card-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
  min-width: max-content;
  flex-wrap: wrap;
}

.card-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

.model-icon-button {
  width: 28px;
  height: 28px;
  min-width: 28px;
  padding: 0;
  border-radius: 999px;
  border: 1px solid rgba(245, 158, 11, 0.2);
  background: rgba(245, 158, 11, 0.08);
  color: #b45309;
}

.model-icon-button.active {
  border-color: rgba(245, 158, 11, 0.38);
  background: #f59e0b;
  color: #ffffff;
  box-shadow: 0 10px 22px rgba(245, 158, 11, 0.18);
}

.model-icon-button.danger {
  border-color: rgba(239, 68, 68, 0.16);
  background: rgba(239, 68, 68, 0.06);
  color: #b91c1c;
}

.slot-button {
  min-width: 104px;
  border-radius: 999px;
}

.dialog-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.toggle-icon {
  cursor: pointer;
}

@media (max-width: 960px) {
  .page-header,
  .model-card {
    grid-template-columns: minmax(0, 1fr);
    align-items: stretch;
  }

  .dialog-grid {
    grid-template-columns: 1fr;
  }

  .header-actions,
  .card-actions {
    flex-wrap: nowrap;
  }
}
</style>
