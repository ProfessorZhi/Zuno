<script setup lang="ts">
import { computed, onActivated, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ArrowLeft,
  Check,
  Connection,
  Document,
  FolderOpened,
  Histogram,
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
  getAllowedRetrievalModeOptions,
  getChunkModeLabel,
  getImageStrategyLabel,
  getIndexCapabilityLabel,
  getRetrievalModeLabel,
  getVectorBackendLabel,
  imageStrategyOptions,
  indexCapabilityOptions,
  normalizeKnowledgeConfig,
  refillPolicyOptions,
  toKnowledgeConfigPatch,
  vectorBackendOptions,
} from '../../utils/knowledge-config'
import ZunoIconButton from '../../components/zuno-settings/ZunoIconButton.vue'

const route = useRoute()
const router = useRouter()

const knowledgeId = computed(() => String(route.params.knowledgeId || ''))
const inWorkspaceSettings = computed(() => route.name === 'workspaceSettingsKnowledgeConfig')
const knowledgeListRoute = computed(() => (
  inWorkspaceSettings.value ? { name: 'workspaceSettingsKnowledge' } : '/knowledge'
))

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

const graphEnabled = computed(() => config.value.index_capability === 'rag_graph')
const allowedRetrievalModeOptions = computed(() => (
  getAllowedRetrievalModeOptions(config.value.index_capability)
))

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
      title: '索引结构已变化',
      body: '建库模式、分段、Embedding、图片索引、向量库或图谱索引参数变更后，需要重建或补建索引才能完全生效。',
    }
  }

  if (configImpact.value.changedQueryFields.length > 0) {
    return {
      type: 'success',
      title: '查询参数将即时生效',
      body: '检索模式、补检策略、Top K、Rerank、Score 阈值和 GraphRAG 查询参数会影响下一次查询，不需要重建索引。',
    }
  }

  return {
    type: 'info',
    title: '当前配置未变化',
    body: '保存只会更新知识库参数。只有索引型参数变化时，才需要重新构建已有文件索引。',
  }
})

const pipelineSummary = computed(() => {
  const modeLabel = getRetrievalModeLabel(config.value.retrieval_settings.default_mode)
  const vectorLabel = getVectorBackendLabel(config.value.index_settings.vector_backend)
  const rerankLabel = config.value.retrieval_settings.rerank_enabled
    ? (rerankBinding.value?.model || '已启用 Rerank')
    : '未启用 Rerank'
  const graphLabel = graphEnabled.value
    ? `GraphRAG ${config.value.retrieval_settings.graph_hop_limit}-hop / 每实体最多 ${config.value.retrieval_settings.max_paths_per_entity} 条路径`
    : '不构建图谱索引'

  return [
    {
      title: '建立索引时',
      detail: `${getIndexCapabilityLabel(config.value.index_capability)} / ${getChunkModeLabel(config.value.index_settings.chunk_mode)} / 分块 ${config.value.index_settings.chunk_size} / 重叠 ${config.value.index_settings.overlap}`,
      icon: Document,
    },
    {
      title: '存储与图片',
      detail: `${vectorLabel} / ${getImageStrategyLabel(config.value.index_settings.image_indexing_mode)}`,
      icon: FolderOpened,
    },
    {
      title: '查询时',
      detail: `${modeLabel} / Top K ${config.value.retrieval_settings.top_k} / ${rerankLabel} / ${graphLabel}`,
      icon: Histogram,
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
    console.error('加载知识库配置失败', error)
    ElMessage.error('加载知识库配置失败')
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
    throw new Error(response.data.status_message || '保存知识库配置失败')
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
    ElMessage.success(configImpact.value.requiresReindex ? '配置已保存，已有文件索引尚未重建' : '知识库配置已保存')
  } catch (error) {
    console.error('保存知识库配置失败', error)
    ElMessage.error(error instanceof Error ? error.message : '保存知识库配置失败')
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
      ElMessage.success(`配置已保存，已开始重建 ${summaryResult.dispatched_tasks}/${summaryResult.total_files} 个文件索引`)
      router.push({
        name: inWorkspaceSettings.value ? 'workspaceSettingsKnowledgeFile' : 'knowledge-file',
        params: { knowledgeId: knowledgeId.value },
        query: { name: knowledge.value?.name || route.query.name || '知识库' },
      })
      return
    }

    if (summaryResult.failed_tasks > 0) {
      ElMessage.warning(`配置已保存，但 ${summaryResult.failed_tasks} 个索引任务启动失败`)
      return
    }

    ElMessage.success(`配置已保存，当前没有可重建的文件（共 ${summaryResult.total_files} 个）`)
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
  ElMessage.success('已恢复推荐默认值，请记得保存')
}

const openFiles = () => {
  router.push({
    name: inWorkspaceSettings.value ? 'workspaceSettingsKnowledgeFile' : 'knowledge-file',
    params: { knowledgeId: knowledgeId.value },
    query: { name: knowledge.value?.name || route.query.name || '知识库' },
  })
}

const goBack = () => {
  router.push(knowledgeListRoute.value)
}

watch(
  () => config.value.index_capability,
  (capability) => {
    if (capability === 'rag') {
      config.value.retrieval_settings.default_mode = 'rag'
    }
  },
)

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
    <section class="page-head">
      <div class="title-block">
        <div class="title-row">
          <ZunoIconButton v-if="!inWorkspaceSettings" :icon="ArrowLeft" title="返回知识库" @click="goBack" />
          <div>
            <p class="eyebrow">知识库配置</p>
            <h1>{{ knowledge?.name || route.query.name || '知识库' }}</h1>
          </div>
        </div>
        <div class="summary-tags">
          <span>{{ summary.indexCapabilityLabel }}</span>
          <span>{{ summary.chunkModeLabel }}</span>
          <span>{{ summary.retrievalModeLabel }}</span>
          <span>{{ summary.vectorBackendLabel }}</span>
        </div>
      </div>
      <div class="head-actions">
        <ZunoIconButton :icon="FolderOpened" title="文件与索引进度" @click="openFiles" />
      </div>
    </section>

    <div class="layout">
      <main class="main-column">
        <section class="panel impact-panel" :class="`impact-${impactCopy.type}`">
          <h2>{{ impactCopy.title }}</h2>
          <p>{{ impactCopy.body }}</p>
        </section>

        <section class="panel">
          <div class="panel-title">
            <div>
              <h2>建库方式</h2>
              <p>建库方式决定要不要建立图谱索引；改动后通常需要重建或补建索引。</p>
            </div>
            <el-icon><Connection /></el-icon>
          </div>

          <div class="option-grid">
            <button
              v-for="item in indexCapabilityOptions"
              :key="item.value"
              type="button"
              class="option-card"
              :class="{ active: config.index_capability === item.value }"
              @click="config.index_capability = item.value"
            >
              <strong>{{ item.label }}</strong>
              <span>{{ item.description }}</span>
            </button>
          </div>
        </section>

        <section class="panel">
          <div class="panel-title">
            <div>
              <h2>索引设置</h2>
              <p>这些参数会影响切块、向量写入和图文索引方式，修改后需要重建索引。</p>
            </div>
            <el-icon><Setting /></el-icon>
          </div>

          <div class="option-grid">
            <button
              v-for="mode in chunkModeOptions"
              :key="mode.value"
              type="button"
              class="option-card"
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

            <label class="field">
              <span>分段标识符</span>
              <el-input v-model="config.index_settings.separator" placeholder="\n\n" />
            </label>

            <label class="field">
              <span>向量库</span>
              <el-select v-model="config.index_settings.vector_backend">
                <el-option
                  v-for="item in vectorBackendOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </label>
          </div>

          <div class="switch-grid">
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
                <p>减少噪声字段，适合标准问答类文档。</p>
              </div>
              <el-switch v-model="config.index_settings.remove_urls_emails" />
            </label>
          </div>

          <div class="section-block">
            <h3>图片处理策略</h3>
            <div class="option-grid">
              <button
                v-for="strategy in imageStrategyOptions"
                :key="strategy.value"
                type="button"
                class="option-card"
                :class="{ active: config.index_settings.image_indexing_mode === strategy.value }"
                @click="config.index_settings.image_indexing_mode = strategy.value"
              >
                <strong>{{ strategy.label }}</strong>
                <span>{{ strategy.description }}</span>
              </button>
            </div>
          </div>
        </section>

        <section class="panel" :class="{ disabled: !graphEnabled }">
          <div class="panel-title">
            <div>
              <h2>GraphRAG 索引参数</h2>
              <p>仅在建库方式为 RAG + GraphRAG 时生效，修改后需要重建或补建图谱索引。</p>
            </div>
            <el-icon><Connection /></el-icon>
          </div>

          <div class="form-grid">
            <label class="field">
              <span>实体抽取方式</span>
              <el-select v-model="config.graph_index_settings.entity_extraction_mode" :disabled="!graphEnabled">
                <el-option label="规则" value="rule" />
                <el-option label="LLM" value="llm" />
                <el-option label="规则 + LLM 辅助" value="rule_llm" />
              </el-select>
            </label>

            <label class="field">
              <span>关系 Schema</span>
              <el-select v-model="config.graph_index_settings.relation_schema" :disabled="!graphEnabled">
                <el-option label="开放关系" value="open" />
                <el-option label="类型约束关系" value="typed" />
              </el-select>
            </label>
          </div>

          <div class="switch-grid">
            <label class="switch-card">
              <div>
                <strong>实体归一化</strong>
                <p>合并同义实体，减少图谱中的重复节点。</p>
              </div>
              <el-switch v-model="config.graph_index_settings.entity_normalization" :disabled="!graphEnabled" />
            </label>
            <label class="switch-card">
              <div>
                <strong>建立 Chunk -> Entity 证据回链</strong>
                <p>让图谱路径能够回到原始文本证据，方便引用和审计。</p>
              </div>
              <el-switch v-model="config.graph_index_settings.evidence_backlink" :disabled="!graphEnabled" />
            </label>
            <label class="switch-card">
              <div>
                <strong>查询时优先使用 RAG 命中 chunk 作为图谱入口</strong>
                <p>先找可靠文本入口，再沿实体关系扩展，避免纯实体匹配漂移。</p>
              </div>
              <el-switch v-model="config.graph_index_settings.use_rag_entry_chunk" :disabled="!graphEnabled" />
            </label>
          </div>
        </section>

        <section class="panel">
          <div class="panel-title">
            <div>
              <h2>查询设置</h2>
              <p>这些参数只影响提问时的召回、排序和补检，保存后即时生效。</p>
            </div>
            <el-icon><Histogram /></el-icon>
          </div>

          <div class="option-grid compact">
            <button
              v-for="item in allowedRetrievalModeOptions"
              :key="item.value"
              type="button"
              class="option-card"
              :class="{ active: config.retrieval_settings.default_mode === item.value }"
              @click="config.retrieval_settings.default_mode = item.value"
            >
              <strong>{{ item.label }}</strong>
              <span>{{ item.description }}</span>
            </button>
          </div>

          <div class="form-grid">
            <label class="field">
              <span>补检策略</span>
              <el-select v-model="config.retrieval_settings.refill_policy">
                <el-option
                  v-for="item in refillPolicyOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </label>

            <label class="field">
              <span>默认 Top K</span>
              <el-slider v-model="config.retrieval_settings.top_k" :min="1" :max="12" :step="1" />
              <small>{{ config.retrieval_settings.top_k }}</small>
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
              <small>{{ config.retrieval_settings.rerank_top_k }}</small>
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

          <div class="switch-grid">
            <label class="switch-card">
              <div>
                <strong>启用 Rerank</strong>
                <p>先用 Embedding 召回，再用排序模型重排优先级。</p>
              </div>
              <el-switch v-model="config.retrieval_settings.rerank_enabled" />
            </label>
            <label class="switch-card">
              <div>
                <strong>启用 Score 阈值</strong>
                <p>低于阈值的结果不会进入最终上下文。</p>
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
              <span>GraphRAG 最大跳数</span>
              <el-select v-model="config.retrieval_settings.graph_hop_limit" :disabled="!graphEnabled">
                <el-option label="1-hop" :value="1" />
                <el-option label="2-hop" :value="2" />
                <el-option label="3-hop" :value="3" />
              </el-select>
            </label>

            <label class="field">
              <span>每实体最大路径数</span>
              <el-input-number
                v-model="config.retrieval_settings.max_paths_per_entity"
                :min="1"
                :max="20"
                :disabled="!graphEnabled"
              />
            </label>
          </div>
        </section>

        <section class="panel">
          <div class="panel-title">
            <div>
              <h2>索引模型</h2>
              <p>Embedding 模型变化会影响向量空间，修改后需要重建索引。</p>
            </div>
            <el-icon><Setting /></el-icon>
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
        </section>
      </main>

      <aside class="side-column">
        <section class="panel sticky-panel">
          <div class="panel-title">
            <div>
              <h2>即时预览</h2>
              <p>配置保存前先看链路会怎么走。</p>
            </div>
            <el-icon><RefreshRight /></el-icon>
          </div>

          <div class="summary-card">
            <h3>当前模型</h3>
            <dl>
              <div><dt>文本 Embedding</dt><dd>{{ summary.textEmbeddingLabel }}</dd></div>
              <div><dt>VL Embedding</dt><dd>{{ summary.vlEmbeddingLabel }}</dd></div>
              <div><dt>Rerank</dt><dd>{{ summary.rerankLabel }}</dd></div>
            </dl>
          </div>

          <div class="summary-card">
            <h3>这套链路会怎么走</h3>
            <div class="pipeline-list">
              <div v-for="item in pipelineSummary" :key="item.title" class="pipeline-item">
                <el-icon><component :is="item.icon" /></el-icon>
                <div>
                  <strong>{{ item.title }}</strong>
                  <p>{{ item.detail }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="summary-card">
            <h3>示例切块</h3>
            <div class="preview-chunks">
              <div v-for="(chunk, index) in chunkPreview" :key="index" class="preview-chunk">
                <span>Chunk {{ index + 1 }}</span>
                <p>{{ chunk }}</p>
              </div>
            </div>
          </div>

          <div class="footer-actions">
            <ZunoIconButton :icon="RefreshRight" title="恢复推荐默认值" @click="handleReset" />
            <ZunoIconButton
              v-if="configImpact.requiresReindex"
              :icon="Check"
              :loading="saving || reindexing"
              title="仅保存配置"
              @click="handleSave"
            />
            <el-button
              v-if="configImpact.requiresReindex"
              class="primary-action"
              type="primary"
              :icon="Check"
              :loading="saving || reindexing"
              @click="handleSaveAndReindex"
            >
              保存并重建索引
            </el-button>
            <el-button
              v-else
              class="primary-action"
              type="primary"
              :icon="Check"
              :loading="saving"
              @click="handleSave"
            >
              保存配置
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
  gap: 14px;
  padding: 20px;
  color: #1f2937;
}

.page-head,
.panel {
  border: 1px solid rgba(214, 132, 70, 0.14);
  border-radius: 20px;
  background: rgba(255, 252, 247, 0.96);
  box-shadow: 0 12px 28px rgba(160, 95, 42, 0.07);
}

.page-head {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 20px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.eyebrow {
  margin: 0 0 4px;
  color: #a16207;
  font-size: 12px;
}

h1,
h2,
h3,
p {
  margin: 0;
}

h1 {
  color: #111827;
  font-size: 24px;
}

h2 {
  color: #5e3518;
  font-size: 17px;
}

h3 {
  color: #5e3518;
  font-size: 14px;
}

.summary-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.summary-tags span {
  padding: 3px 10px;
  border: 1px solid rgba(214, 132, 70, 0.16);
  border-radius: 999px;
  color: #7c5835;
  background: rgba(255, 245, 236, 0.9);
  font-size: 12px;
}

.head-actions {
  display: flex;
  align-items: center;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 390px;
  gap: 14px;
  align-items: start;
}

.main-column,
.side-column {
  display: grid;
  gap: 14px;
}

.panel {
  padding: 18px 20px;
}

.panel.disabled {
  opacity: 0.72;
}

.panel-title {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.panel-title p,
.impact-panel p,
.section-block p {
  margin-top: 4px;
  color: #8f7a68;
  font-size: 12px;
  line-height: 1.5;
}

.panel-title :deep(.el-icon) {
  color: #c97835;
  font-size: 20px;
}

.impact-warning {
  background: #fff8ec;
}

.impact-success {
  background: #f2fbf4;
}

.impact-info {
  background: #fafafa;
}

.option-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.option-grid.compact {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.option-card,
.switch-card,
.summary-card,
.preview-chunk {
  border: 1px solid rgba(214, 132, 70, 0.12);
  border-radius: 16px;
  background: rgba(255, 249, 243, 0.94);
}

.option-card {
  display: grid;
  gap: 5px;
  padding: 12px 14px;
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
}

.option-card strong,
.switch-card strong,
.pipeline-item strong {
  color: #5a3115;
}

.option-card span,
.switch-card p,
.pipeline-item p,
.preview-chunk p {
  color: #806957;
  font-size: 12px;
  line-height: 1.55;
}

.option-card.active {
  border-color: rgba(201, 120, 53, 0.6);
  background: linear-gradient(180deg, rgba(255, 246, 236, 0.96), rgba(255, 240, 227, 0.94));
  box-shadow: inset 0 0 0 1px rgba(201, 120, 53, 0.24);
}

.form-grid,
.switch-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px 18px;
  margin-top: 16px;
}

.field {
  display: grid;
  grid-template-columns: 128px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  min-height: 42px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.12);
}

.field span {
  color: #5a3115;
  font-weight: 600;
}

.field small {
  color: #8f7a68;
  min-width: 58px;
  text-align: right;
}

.switch-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 14px;
}

.section-block {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.sticky-panel {
  position: sticky;
  top: 16px;
}

.summary-card {
  padding: 14px;
}

.summary-card + .summary-card {
  margin-top: 12px;
}

dl {
  display: grid;
  gap: 10px;
  margin: 12px 0 0;
}

dl div {
  display: grid;
  grid-template-columns: 112px minmax(0, 1fr);
  gap: 10px;
}

dt {
  color: #806957;
  font-weight: 600;
}

dd {
  margin: 0;
  color: #5a3115;
  word-break: break-word;
}

.pipeline-list,
.preview-chunks {
  display: grid;
  gap: 10px;
  margin-top: 12px;
}

.pipeline-item {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  gap: 10px;
  align-items: start;
}

.pipeline-item :deep(.el-icon) {
  display: grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 10px;
  color: #c97835;
  background: rgba(255, 243, 232, 0.96);
}

.preview-chunk {
  padding: 12px;
}

.preview-chunk span {
  color: #c97835;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
}

.preview-chunk p {
  margin-top: 6px;
}

.footer-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 14px;
}

.primary-action {
  height: 34px;
  border-radius: 999px;
  border-color: #f59e0b;
  background: #f59e0b;
  box-shadow: 0 10px 24px rgba(245, 158, 11, 0.18);
}

.footer-actions :deep(.el-button + .el-button) {
  margin-left: 0;
}

@media (max-width: 1180px) {
  .layout,
  .form-grid,
  .switch-grid {
    grid-template-columns: 1fr;
  }

  .sticky-panel {
    position: static;
  }
}

@media (max-width: 720px) {
  .knowledge-config-page {
    padding: 12px;
  }

  .page-head {
    flex-direction: column;
  }

  .field {
    grid-template-columns: 1fr;
    align-items: stretch;
    padding-bottom: 10px;
  }

  .field small {
    text-align: left;
  }
}
</style>
