<script setup lang="ts">
import { computed, onActivated, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Check,
  Document,
  FolderOpened,
  Histogram,
  Promotion,
  RefreshRight,
  Setting,
} from '@element-plus/icons-vue'
import {
  getKnowledgeListAPI,
  updateKnowledgeAPI,
  type KnowledgeConfigPayload,
  type KnowledgeResponse,
} from '../../apis/knowledge'
import { reindexKnowledgeFilesAPI } from '../../apis/knowledge-file'
import { getVisibleLLMsAPI, type LLMResponse } from '../../apis/llm'
import {
  buildKnowledgePreviewChunks,
  chunkModeOptions,
  createDefaultKnowledgeConfig,
  detectReindexImpact,
  describeKnowledgeConfig,
  findBindingById,
  getChunkModeLabel,
  getImageStrategyLabel,
  getRetrievalModeLabel,
  imageStrategyOptions,
  normalizeKnowledgeConfig,
  retrievalModeOptions,
  toKnowledgeConfigPatch,
} from '../../utils/knowledge-config'

const route = useRoute()
const router = useRouter()

const knowledgeId = computed(() => String(route.params.knowledgeId || ''))
const loading = ref(false)
const saving = ref(false)
const reindexing = ref(false)
const knowledge = ref<KnowledgeResponse | null>(null)
const modelOptions = ref<LLMResponse[]>([])
const config = ref<KnowledgeConfigPayload>(createDefaultKnowledgeConfig())
const originalConfig = ref<KnowledgeConfigPayload>(createDefaultKnowledgeConfig())

const textEmbeddingOptions = computed(() => (
  modelOptions.value.filter((item) => item.llm_type === 'Embedding')
))

const rerankOptions = computed(() => (
  modelOptions.value.filter((item) => item.llm_type === 'Rerank')
))

const textEmbeddingBinding = computed(() => (
  findBindingById(config.value.model_refs.text_embedding_model_id, textEmbeddingOptions.value)
))

const vlEmbeddingBinding = computed(() => (
  findBindingById(config.value.model_refs.vl_embedding_model_id, textEmbeddingOptions.value)
))

const rerankBinding = computed(() => (
  findBindingById(config.value.model_refs.rerank_model_id, rerankOptions.value)
))

const scoreThresholdEnabled = computed({
  get: () => config.value.retrieval_settings.score_threshold !== null,
  set: (enabled: boolean) => {
    config.value.retrieval_settings.score_threshold = enabled
      ? (config.value.retrieval_settings.score_threshold ?? 0.7)
      : null
  },
})

const summary = computed(() => describeKnowledgeConfig(config.value, {
  textEmbedding: textEmbeddingBinding.value,
  vlEmbedding: vlEmbeddingBinding.value,
  rerank: rerankBinding.value,
}))

const chunkPreview = computed(() => buildKnowledgePreviewChunks(
  knowledge.value?.name || String(route.query.name || ''),
  knowledge.value?.description || '',
  config.value,
))

const configImpact = computed(() => detectReindexImpact(originalConfig.value, config.value))

const impactCopy = computed(() => {
  if (configImpact.value.requiresReindex) {
    return {
      type: 'warning',
      title: '这次改动会影响已有索引',
      body: '分段、图片索引策略、文本 Embedding 和 VL Embedding 会改变切片或向量。保存参数后，需要重建已有文件索引才会完全生效。',
    }
  }

  if (configImpact.value.changedQueryFields.length > 0) {
    return {
      type: 'success',
      title: '这次改动会直接影响检索策略',
      body: '默认检索模式、Top K、Rerank 和阈值会在后续查询里立刻生效，不需要重建索引。',
    }
  }

  return {
    type: 'info',
    title: '当前还没有参数变化',
    body: '保存只会更新知识库配置。只有索引型参数变化时，后续才需要重建已有文件索引。',
  }
})

const pipelineSummary = computed(() => {
  const modeLabel = getRetrievalModeLabel(config.value.retrieval_settings.default_mode)
  const rerankLabel = config.value.retrieval_settings.rerank_enabled
    ? (rerankBinding.value?.model || '等待选择 Rerank 模型')
    : '未启用 Rerank'

  return [
    {
      title: '建立索引时',
      detail: `${getChunkModeLabel(config.value.index_settings.chunk_mode)} / 分块 ${config.value.index_settings.chunk_size} / 重叠 ${config.value.index_settings.overlap}`,
      icon: Document,
    },
    {
      title: '图片处理',
      detail: getImageStrategyLabel(config.value.index_settings.image_indexing_mode),
      icon: FolderOpened,
    },
    {
      title: '检索策略',
      detail: `${modeLabel} / 首轮不足时自动补检一轮 / Top K ${config.value.retrieval_settings.top_k} / ${rerankLabel}`,
      icon: Promotion,
    },
  ]
})

const ensureModelBinding = (
  target: 'text_embedding_model_id' | 'vl_embedding_model_id' | 'rerank_model_id',
  options: LLMResponse[],
) => {
  if (config.value.model_refs[target]) return
  const first = options[0]
  if (!first) return
  config.value.model_refs[target] = first.llm_id
}

const fetchKnowledgeContext = async () => {
  if (!knowledgeId.value) return

  loading.value = true
  try {
    const [knowledgeResponse, llmResponse] = await Promise.all([
      getKnowledgeListAPI(),
      getVisibleLLMsAPI(),
    ])

    if (knowledgeResponse.data.status_code === 200) {
      knowledge.value = (knowledgeResponse.data.data || []).find((item) => item.id === knowledgeId.value) || null
      const normalized = normalizeKnowledgeConfig(knowledge.value?.knowledge_config)
      config.value = normalized
      originalConfig.value = structuredClone(normalized)
    }

    if (llmResponse.data.status_code === 200) {
      const grouped = llmResponse.data.data || {}
      modelOptions.value = Object.values(grouped).flat().filter(Boolean) as LLMResponse[]
    }
  } catch (error) {
    console.error('加载知识库参数上下文失败', error)
    ElMessage.error('加载知识库参数失败')
  } finally {
    loading.value = false
  }
}

const saveKnowledgeConfig = async () => {
  const response = await updateKnowledgeAPI({
    knowledge_id: knowledgeId.value,
    knowledge_config: toKnowledgeConfigPatch(config.value),
  })

  if (response.data.status_code !== 200) {
    throw new Error(response.data.status_message || '保存知识库参数失败')
  }

  await fetchKnowledgeContext()
}

const reindexKnowledgeFiles = async () => {
  const response = await reindexKnowledgeFilesAPI({ knowledge_id: knowledgeId.value })
  if (response.data.status_code !== 200) {
    throw new Error(response.data.status_message || '重建索引失败')
  }
  return response.data.data || {
    summary: {
      knowledge_id: knowledgeId.value,
      total_files: 0,
      created_tasks: 0,
      dispatched_tasks: 0,
      failed_tasks: 0,
    },
    task_ids: [],
    file_ids: [],
  }
}

const handleSave = async () => {
  if (!knowledgeId.value) return

  saving.value = true
  try {
    await saveKnowledgeConfig()
    ElMessage.success(
      configImpact.value.requiresReindex
        ? '参数已保存；已有文件索引还没重建'
        : '知识库参数已保存',
    )
  } catch (error) {
    console.error('保存知识库参数失败', error)
    ElMessage.error(error instanceof Error ? error.message : '保存知识库参数失败')
  } finally {
    saving.value = false
  }
}

const handleSaveAndReindex = async () => {
  if (!knowledgeId.value || !configImpact.value.requiresReindex) return

  saving.value = true
  reindexing.value = true
  try {
    await saveKnowledgeConfig()
    const result = await reindexKnowledgeFiles()
    const summaryResult = result.summary || {
      total_files: 0,
      created_tasks: 0,
      dispatched_tasks: 0,
      failed_tasks: 0,
    }

    if (summaryResult.dispatched_tasks > 0) {
      ElMessage.success(`参数已保存，并开始重建 ${summaryResult.dispatched_tasks}/${summaryResult.total_files} 个文件索引`)
      router.push({
        name: 'knowledge-file',
        params: { knowledgeId: knowledgeId.value },
        query: { name: knowledge.value?.name || route.query.name || '知识库' },
      })
      return
    }

    if (summaryResult.failed_tasks > 0) {
      ElMessage.warning(`参数已保存，但 ${summaryResult.failed_tasks} 个文件索引任务启动失败`)
      return
    }

    ElMessage.success(`参数已保存，当前没有可重建的文件（共 ${summaryResult.total_files} 个）`)
  } catch (error) {
    console.error('保存并重建索引失败', error)
    ElMessage.error(error instanceof Error ? error.message : '保存并重建索引失败')
  } finally {
    reindexing.value = false
    saving.value = false
  }
}

const handleReset = () => {
  config.value = createDefaultKnowledgeConfig()
  ensureModelBinding('text_embedding_model_id', textEmbeddingOptions.value)
  ensureModelBinding('vl_embedding_model_id', textEmbeddingOptions.value)
  ensureModelBinding('rerank_model_id', rerankOptions.value)
  ElMessage.success('已恢复为系统默认值，请记得保存')
}

const openFiles = () => {
  router.push({
    name: 'knowledge-file',
    params: { knowledgeId: knowledgeId.value },
    query: { name: knowledge.value?.name || route.query.name || '知识库' },
  })
}

const goBack = () => {
  router.back()
}

watch(textEmbeddingOptions, (options) => {
  ensureModelBinding('text_embedding_model_id', options)
  ensureModelBinding('vl_embedding_model_id', options)
})

watch(rerankOptions, (options) => {
  ensureModelBinding('rerank_model_id', options)
})

onMounted(fetchKnowledgeContext)
onActivated(fetchKnowledgeContext)
</script>

<template>
  <div class="knowledge-config-page" v-loading="loading">
    <section class="page-hero">
      <div class="hero-copy">
        <el-button :icon="ArrowLeft" class="back-btn" @click="goBack">返回</el-button>
        <div class="eyebrow">知识库参数中心</div>
        <h1>{{ knowledge?.name || route.query.name || '知识库' }}</h1>
        <p>
          这里决定这个知识库怎么切片、怎么建索引、怎么做检索。
          首轮结果不够强时，会自动补检一轮；聊天页只选知识库，不再在聊天时改 Embedding、Rerank 和 Top K。
        </p>
        <div class="hero-pills">
          <span class="hero-pill">{{ summary.chunkModeLabel }}</span>
          <span class="hero-pill">{{ summary.retrievalModeLabel }}</span>
          <span class="hero-pill">{{ summary.imageStrategyLabel }}</span>
        </div>
      </div>

      <div class="hero-side">
        <div class="status-card">
          <div class="status-head">
            <span>当前生效说明</span>
            <el-icon><Check /></el-icon>
          </div>
          <strong>知识库按自己的检索策略运行，首轮不足时自动补检一轮</strong>
          <p>模型页只提供可选资源池。聊天页只选知识库，不再在聊天时改 Embedding、Rerank 和 Top K。</p>
          <div class="status-actions">
            <el-button :icon="FolderOpened" @click="openFiles">去看文件与进度</el-button>
          </div>
        </div>
      </div>
    </section>

    <div class="workspace">
      <div class="config-column">
        <section class="panel-card impact-panel" :class="`impact-${impactCopy.type}`">
          <div class="panel-head compact-head">
            <div>
              <h2>{{ impactCopy.title }}</h2>
              <p>{{ impactCopy.body }}</p>
            </div>
          </div>
        </section>

        <section class="panel-card">
          <div class="panel-head">
            <div>
              <h2>索引设置</h2>
              <p>决定这个知识库收什么资料、怎么切块、图片如何进入索引。</p>
            </div>
            <el-icon class="panel-icon"><Setting /></el-icon>
          </div>

          <div class="option-grid">
            <button
              v-for="mode in chunkModeOptions"
              :key="mode.value"
              type="button"
              class="mode-card"
              :class="{ active: config.index_settings.chunk_mode === mode.value }"
              @click="config.index_settings.chunk_mode = mode.value"
            >
              <strong>{{ mode.label }}</strong>
              <span>{{ mode.description }}</span>
            </button>
          </div>

          <div class="form-grid">
            <label class="field">
              <span>分段最大长度</span>
              <el-slider v-model="config.index_settings.chunk_size" :min="256" :max="2048" :step="64" />
              <small>{{ config.index_settings.chunk_size }} characters</small>
            </label>

            <label class="field">
              <span>分段重叠长度</span>
              <el-slider v-model="config.index_settings.overlap" :min="0" :max="400" :step="10" />
              <small>{{ config.index_settings.overlap }} characters</small>
            </label>
          </div>

          <div class="form-grid">
            <label class="field">
              <span>分段标识符</span>
              <el-input v-model="config.index_settings.separator" placeholder="\n\n" />
            </label>
          </div>

          <div class="switch-row">
            <label class="switch-card">
              <div>
                <strong>清理连续空格和换行</strong>
                <p>让切块更稳定，适合常规文档。</p>
              </div>
              <el-switch v-model="config.index_settings.replace_consecutive_spaces" />
            </label>
            <label class="switch-card">
              <div>
                <strong>删除 URL 和邮箱地址</strong>
                <p>适合客服和标准文档，减少噪声字段。</p>
              </div>
              <el-switch v-model="config.index_settings.remove_urls_emails" />
            </label>
          </div>

          <div class="subsection">
            <div class="subsection-head">
              <h3>图片处理策略</h3>
              <p>决定图片在构建索引时，是转文字、走 VL 索引，还是图文双通道。</p>
            </div>
            <div class="option-grid">
              <button
                v-for="strategy in imageStrategyOptions"
                :key="strategy.value"
                type="button"
                class="mode-card"
                :class="{ active: config.index_settings.image_indexing_mode === strategy.value }"
                @click="config.index_settings.image_indexing_mode = strategy.value"
              >
                <strong>{{ strategy.label }}</strong>
                <span>{{ strategy.description }}</span>
              </button>
            </div>
          </div>

          <div class="subsection">
            <div class="subsection-head">
              <h3>索引模型</h3>
              <p>这些模型直接绑定到这个知识库自己的索引链路，不再依赖全局默认。</p>
            </div>
            <div class="form-grid">
              <label class="field">
                <span>文本 Embedding</span>
                <el-select v-model="config.model_refs.text_embedding_model_id" placeholder="选择文本 Embedding">
                  <el-option
                    v-for="item in textEmbeddingOptions"
                    :key="item.llm_id"
                    :label="`${item.model} / ${item.provider}`"
                    :value="item.llm_id"
                  />
                </el-select>
              </label>

              <label class="field">
                <span>VL Embedding</span>
                <el-select v-model="config.model_refs.vl_embedding_model_id" placeholder="选择 VL Embedding">
                  <el-option
                    v-for="item in textEmbeddingOptions"
                    :key="item.llm_id"
                    :label="`${item.model} / ${item.provider}`"
                    :value="item.llm_id"
                  />
                </el-select>
              </label>
            </div>
          </div>
        </section>

        <section class="panel-card">
          <div class="panel-head">
            <div>
              <h2>检索策略</h2>
              <p>决定用户提问时，如何从这个知识库里召回内容、要不要重排，以及首轮不足时是否自动补检一轮。</p>
            </div>
            <el-icon class="panel-icon"><Histogram /></el-icon>
          </div>

          <div class="option-grid">
            <button
              v-for="item in retrievalModeOptions"
              :key="item.value"
              type="button"
              class="mode-card"
              :class="{ active: config.retrieval_settings.default_mode === item.value }"
              @click="config.retrieval_settings.default_mode = item.value"
            >
              <strong>{{ item.label }}</strong>
              <span>{{ item.description }}</span>
            </button>
          </div>

          <div class="form-grid">
            <label class="field">
              <span>默认 Top K</span>
              <el-slider v-model="config.retrieval_settings.top_k" :min="1" :max="12" :step="1" />
              <small>每次先召回 {{ config.retrieval_settings.top_k }} 个候选块</small>
            </label>

            <label class="field">
              <span>Rerank Top K</span>
              <el-slider
                v-model="config.retrieval_settings.rerank_top_k"
                :min="1"
                :max="10"
                :step="1"
                :disabled="!config.retrieval_settings.rerank_enabled"
              />
              <small>重排后优先保留 {{ config.retrieval_settings.rerank_top_k }} 条结果</small>
            </label>
          </div>

          <div class="switch-row">
            <label class="switch-card">
              <div>
                <strong>启用 Rerank</strong>
                <p>先用 Embedding 召回，再用排序模型重新排优先级。</p>
              </div>
              <el-switch v-model="config.retrieval_settings.rerank_enabled" />
            </label>
            <label class="switch-card">
              <div>
                <strong>启用 Score 阈值</strong>
                <p>低于阈值的结果不继续送入答案链路。</p>
              </div>
              <el-switch v-model="scoreThresholdEnabled" />
            </label>
          </div>

          <div class="form-grid">
            <label class="field">
              <span>Rerank 模型</span>
              <el-select
                v-model="config.model_refs.rerank_model_id"
                :disabled="!config.retrieval_settings.rerank_enabled"
                placeholder="选择 Rerank 模型"
              >
                <el-option
                  v-for="item in rerankOptions"
                  :key="item.llm_id"
                  :label="`${item.model} / ${item.provider}`"
                  :value="item.llm_id"
                />
              </el-select>
            </label>

            <label class="field">
              <span>Score 阈值</span>
              <el-slider
                :model-value="config.retrieval_settings.score_threshold ?? 0.7"
                :min="0.1"
                :max="1"
                :step="0.05"
                :disabled="config.retrieval_settings.score_threshold === null"
                @update:model-value="(value) => config.retrieval_settings.score_threshold = value"
              />
              <small>{{ (config.retrieval_settings.score_threshold ?? 0.7).toFixed(2) }}</small>
            </label>
          </div>
        </section>
      </div>

      <aside class="preview-column">
        <section class="panel-card sticky-card">
          <div class="panel-head">
            <div>
              <h2>即时预览</h2>
              <p>把“这套参数会怎样工作”直接翻译成可读摘要。</p>
            </div>
            <el-icon class="panel-icon"><RefreshRight /></el-icon>
          </div>

          <div class="summary-stack">
            <article class="summary-card">
              <div class="summary-title">当前模型</div>
              <div class="summary-lines">
                <span><strong>文本 Embedding</strong>{{ summary.textEmbeddingLabel }}</span>
                <span><strong>VL Embedding</strong>{{ summary.vlEmbeddingLabel }}</span>
                <span><strong>Rerank</strong>{{ summary.rerankLabel }}</span>
              </div>
            </article>

            <article class="summary-card">
              <div class="summary-title">这套链路会怎么走</div>
              <div class="pipeline-list">
                <div v-for="item in pipelineSummary" :key="item.title" class="pipeline-item">
                  <el-icon class="pipeline-icon"><component :is="item.icon" /></el-icon>
                  <div>
                    <strong>{{ item.title }}</strong>
                    <p>{{ item.detail }}</p>
                  </div>
                </div>
              </div>
            </article>

            <article class="summary-card">
              <div class="summary-title">示例切块</div>
              <div class="preview-chunks">
                <div v-for="(chunk, index) in chunkPreview" :key="index" class="preview-chunk">
                  <span class="chunk-index">Chunk {{ index + 1 }}</span>
                  <p>{{ chunk }}</p>
                </div>
              </div>
            </article>
          </div>

          <div class="footer-actions">
            <el-button @click="handleReset">恢复推荐默认值</el-button>
            <el-button v-if="configImpact.requiresReindex" :loading="saving || reindexing" @click="handleSave">
              仅保存参数
            </el-button>
            <el-button
              v-if="configImpact.requiresReindex"
              type="primary"
              :icon="Check"
              :loading="saving || reindexing"
              @click="handleSaveAndReindex"
            >
              保存并重建索引
            </el-button>
            <el-button v-else type="primary" :icon="Check" :loading="saving" @click="handleSave">
              保存知识库参数
            </el-button>
          </div>
        </section>
      </aside>
    </div>
  </div>
</template>

<style scoped lang="scss">
.knowledge-config-page {
  display: grid;
  gap: 20px;
  padding: 24px;
}

.page-hero,
.panel-card {
  border-radius: 24px;
  border: 1px solid rgba(214, 132, 70, 0.14);
  background: rgba(255, 252, 247, 0.96);
  box-shadow: 0 16px 36px rgba(160, 95, 42, 0.08);
}

.page-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(280px, 0.85fr);
  gap: 18px;
  padding: 28px;
}

.back-btn {
  margin-bottom: 14px;
}

.eyebrow {
  margin-bottom: 8px;
  font-size: 12px;
  letter-spacing: 0.12em;
  color: #ca7a35;
}

.hero-copy h1 {
  margin: 0;
  font-size: 34px;
  color: #5e3518;
}

.hero-copy p {
  margin: 12px 0 0;
  color: #8f7a68;
  line-height: 1.8;
}

.hero-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 18px;
}

.hero-pill {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(255, 245, 236, 0.92);
  border: 1px solid rgba(214, 132, 70, 0.14);
  color: #7c5835;
}

.status-card {
  display: grid;
  gap: 14px;
  height: 100%;
  padding: 22px;
  border-radius: 22px;
  background: linear-gradient(145deg, rgba(255, 249, 243, 0.98), rgba(255, 243, 232, 0.92));
  border: 1px solid rgba(214, 132, 70, 0.12);
}

.status-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #aa6b33;
}

.status-card strong {
  font-size: 28px;
  line-height: 1.3;
  color: #5e3518;
}

.status-card p {
  margin: 0;
  color: #8f7a68;
  line-height: 1.7;
}

.status-actions {
  display: flex;
  justify-content: flex-start;
}

.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  gap: 20px;
  align-items: start;
}

.config-column,
.preview-column {
  display: grid;
  gap: 20px;
}

.sticky-card {
  position: sticky;
  top: 20px;
}

.panel-card {
  padding: 24px;
}

.panel-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.panel-head h2 {
  margin: 0;
  color: #5e3518;
}

.panel-head p {
  margin: 8px 0 0;
  color: #8f7a68;
  line-height: 1.7;
}

.compact-head {
  margin-bottom: 0;
}

.panel-icon {
  font-size: 20px;
  color: #c97835;
}

.impact-panel {
  border-width: 1px;
}

.impact-warning {
  background: rgba(255, 248, 236, 0.98);
}

.impact-success {
  background: rgba(242, 251, 244, 0.98);
}

.impact-info {
  background: rgba(250, 250, 250, 0.98);
}

.option-grid,
.form-grid,
.switch-row,
.summary-stack {
  display: grid;
  gap: 14px;
}

.option-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.form-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 16px;
}

.mode-card,
.switch-card,
.summary-card,
.preview-chunk,
.field {
  border-radius: 20px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 249, 243, 0.94);
}

.mode-card {
  display: grid;
  gap: 8px;
  padding: 18px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-card strong {
  color: #5a3115;
}

.mode-card span {
  color: #826b59;
  line-height: 1.6;
}

.mode-card.active {
  border-color: rgba(201, 120, 53, 0.55);
  box-shadow: inset 0 0 0 1px rgba(201, 120, 53, 0.3);
  background: linear-gradient(180deg, rgba(255, 246, 236, 0.96), rgba(255, 240, 227, 0.94));
}

.field {
  display: grid;
  gap: 12px;
  padding: 18px;
}

.field span {
  font-weight: 600;
  color: #5a3115;
}

.field small {
  color: #8f7a68;
}

.switch-row {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 16px;
}

.switch-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 18px;
}

.switch-card strong {
  color: #5a3115;
}

.switch-card p {
  margin: 6px 0 0;
  color: #8f7a68;
  line-height: 1.6;
}

.subsection {
  margin-top: 22px;
}

.subsection-head {
  margin-bottom: 14px;
}

.subsection-head h3 {
  margin: 0;
  color: #5a3115;
}

.subsection-head p {
  margin: 8px 0 0;
  color: #8f7a68;
  line-height: 1.7;
}

.summary-title {
  margin-bottom: 12px;
  font-weight: 700;
  color: #5a3115;
}

.summary-lines {
  display: grid;
  gap: 10px;
}

.summary-lines span {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: #6f543d;
}

.summary-lines strong {
  min-width: 120px;
}

.pipeline-list,
.preview-chunks {
  display: grid;
  gap: 12px;
}

.pipeline-item {
  display: grid;
  grid-template-columns: 32px 1fr;
  gap: 12px;
  align-items: start;
}

.pipeline-item strong {
  color: #5a3115;
}

.pipeline-item p {
  margin: 4px 0 0;
  color: #806957;
  line-height: 1.6;
}

.pipeline-icon {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 12px;
  background: rgba(255, 243, 232, 0.96);
  color: #c97835;
}

.chunk-index {
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #c97835;
}

.preview-chunk p {
  margin: 8px 0 0;
  color: #806957;
  line-height: 1.7;
}

.summary-card,
.preview-chunk {
  padding: 18px;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 18px;
}

@media (max-width: 1200px) {
  .workspace,
  .page-hero,
  .form-grid,
  .switch-row {
    grid-template-columns: 1fr;
  }

  .sticky-card {
    position: static;
  }
}
</style>
