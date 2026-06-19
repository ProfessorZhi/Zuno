<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'
import { getDomainPacksAPI, type DomainPackSummary } from '../../apis/domain-packs'
import {
  analyzeKnowledgeConfigImpactAPI,
  getKnowledgeConfigAPI,
  runKnowledgeReindexActionAPI,
  updateKnowledgeConfigAPI,
  type KnowledgeConfigImpactResponse,
  type KnowledgeConfigPayload,
  type KnowledgeReindexAction,
} from '../../apis/knowledge'
import { getVisibleLLMsAPI, type LLMResponse } from '../../apis/llm'
import { normalizeKnowledgeConfig } from '../../utils/knowledge-config'

const route = useRoute()
const loading = ref(false)
const saving = ref(false)
const reindexingAction = ref<KnowledgeReindexAction | ''>('')
const config = ref<KnowledgeConfigPayload>(normalizeKnowledgeConfig())
const impact = ref<KnowledgeConfigImpactResponse | null>(null)
const domainPacks = ref<DomainPackSummary[]>([])
const models = ref<LLMResponse[]>([])
const knowledgeId = computed(() => String(route.params.knowledgeId || ''))
const embeddingModels = computed(() => models.value.filter((item) => item.llm_type === 'Embedding'))
const rerankModels = computed(() => models.value.filter((item) => item.llm_type === 'Rerank'))

const statusItems = computed(() => [
  {
    title: '文本索引',
    status: config.value.index_settings.text_index_status || config.value.index_settings.health_status,
    copy: 'Embedding 变化后需要重建文本索引。',
  },
  {
    title: 'BM25',
    status: config.value.index_settings.bm25_index_status || 'ready',
    copy: '默认开启，关键词检索作为稳定兜底链路。',
  },
  {
    title: '图谱索引',
    status: config.value.graph_index_settings.graph_index_status || config.value.graph_index_settings.health_status,
    copy: '领域包 schema 或抽取策略变化后更新图谱。',
  },
  {
    title: '社区发现',
    status: config.value.graph_index_settings.community_detection_status || 'not_built',
    copy: '社区增强只在增强检索链路里作为全局分析能力。',
  },
  {
    title: '社区报告',
    status: config.value.graph_index_settings.community_report_status || 'not_built',
    copy: '当社区数据过期时，可单独重新生成社区报告。',
  },
])

const reindexActions: Array<{ action: KnowledgeReindexAction; label: string }> = [
  { action: 'text_index', label: '重建文本索引' },
  { action: 'image_index', label: '重建图片索引' },
  { action: 'bm25_index', label: '重建 BM25' },
  { action: 'graph_index', label: '更新图谱' },
  { action: 'community_detection', label: '重新发现社区' },
  { action: 'community_report', label: '重新生成社区报告' },
  { action: 'full_rebuild', label: '完整重建' },
]

const impactLines = computed(() => {
  if (!impact.value) return ['修改配置后会在这里显示影响预览。']
  const lines: string[] = []
  if (impact.value.immediate_effect_fields.length) lines.push('Rerank 或查询参数会在下次查询生效。')
  if (impact.value.text_reindex_required) lines.push('文本 Embedding 或分段变化需要重建文本索引。')
  if (impact.value.image_reindex_required) lines.push('VL Embedding 或图片策略变化需要重建图片/多模态索引。')
  if (impact.value.bm25_reindex_required) lines.push('分段变化需要重建 BM25。')
  if (impact.value.graph_update_required) lines.push('领域包或图谱抽取策略变化需要更新图谱。')
  if (impact.value.community_detection_required) lines.push('图谱结构变化后需要重新发现社区。')
  if (impact.value.community_report_required) lines.push('社区报告 Prompt 或社区数据变化后需要重新生成社区报告。')
  return lines.length ? lines : ['本次改动保存后立即生效，不需要重建索引。']
})

const loadPage = async () => {
  if (!knowledgeId.value) return
  loading.value = true
  try {
    const [configResponse, domainResponse, modelResponse] = await Promise.all([
      getKnowledgeConfigAPI(knowledgeId.value),
      getDomainPacksAPI(),
      getVisibleLLMsAPI(),
    ])
    if (configResponse.data.status_code === 200) {
      config.value = normalizeKnowledgeConfig(configResponse.data.data)
    }
    if (domainResponse.data.status_code === 200) {
      domainPacks.value = domainResponse.data.data || []
    }
    if (modelResponse.data.status_code === 200) {
      models.value = Object.values(modelResponse.data.data || {}).flat().filter(Boolean) as LLMResponse[]
    }
  } catch (error) {
    console.error('加载知识库配置失败', error)
    ElMessage.error('加载知识库配置失败')
  } finally {
    loading.value = false
  }
}

const previewImpact = async () => {
  if (!knowledgeId.value) return
  try {
    const response = await analyzeKnowledgeConfigImpactAPI(knowledgeId.value, config.value)
    if (response.data.status_code === 200) {
      impact.value = response.data.data || null
    }
  } catch (error) {
    console.error('预览配置影响失败', error)
  }
}

const saveConfig = async () => {
  if (!knowledgeId.value) return
  saving.value = true
  try {
    const response = await updateKnowledgeConfigAPI(knowledgeId.value, config.value)
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '保存配置失败')
    }
    ElMessage.success('配置已保存')
    await previewImpact()
  } catch (error) {
    console.error('保存配置失败', error)
    ElMessage.error(error instanceof Error ? error.message : '保存配置失败')
  } finally {
    saving.value = false
  }
}

const runAction = async (action: KnowledgeReindexAction) => {
  if (!knowledgeId.value) return
  reindexingAction.value = action
  try {
    const response = await runKnowledgeReindexActionAPI(knowledgeId.value, action)
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '触发重建失败')
    }
    ElMessage.success('重建任务已接收')
  } catch (error) {
    console.error('触发重建失败', error)
    ElMessage.error(error instanceof Error ? error.message : '触发重建失败')
  } finally {
    reindexingAction.value = ''
  }
}

watch(config, previewImpact, { deep: true })
onMounted(loadPage)
</script>

<template>
  <div class="knowledge-settings-page">
    <section class="hero-card" v-loading="loading">
      <p class="eyebrow">知识库维护页</p>
      <h1>{{ route.query.name || '知识库' }} · 配置维护</h1>
      <div class="config-grid">
        <label>
          <span>文本 Embedding</span>
          <select v-model="config.model_refs.text_embedding_model_id">
            <option :value="null">未选择</option>
            <option v-for="model in embeddingModels" :key="model.llm_id" :value="model.llm_id">{{ model.model }}</option>
          </select>
        </label>
        <label>
          <span>VL Embedding</span>
          <select v-model="config.model_refs.vl_embedding_model_id">
            <option :value="null">未选择</option>
            <option v-for="model in embeddingModels" :key="model.llm_id" :value="model.llm_id">{{ model.model }}</option>
          </select>
        </label>
        <label>
          <span>Rerank</span>
          <select v-model="config.model_refs.rerank_model_id">
            <option :value="null">未选择</option>
            <option v-for="model in rerankModels" :key="model.llm_id" :value="model.llm_id">{{ model.model }}</option>
          </select>
        </label>
        <label>
          <span>领域包</span>
          <select v-model="config.domain_pack_id">
            <option :value="null">暂不绑定</option>
            <option v-for="pack in domainPacks" :key="pack.pack_id" :value="pack.pack_id">{{ pack.name }}</option>
          </select>
        </label>
      </div>
    </section>

    <section class="status-grid">
      <article v-for="item in statusItems" :key="item.title" class="status-card">
        <strong>{{ item.title }}</strong>
        <span class="status-pill">{{ item.status }}</span>
        <p>{{ item.copy }}</p>
      </article>
    </section>

    <section class="action-panel">
      <h2>配置影响</h2>
      <p v-for="line in impactLines" :key="line" class="impact-line">{{ line }}</p>
    </section>

    <section class="action-panel">
      <h2>可执行动作</h2>
      <div class="action-row">
        <button type="button" :disabled="saving" @click="saveConfig">{{ saving ? '保存中...' : '保存配置' }}</button>
        <button
          v-for="item in reindexActions"
          :key="item.action"
          type="button"
          :disabled="reindexingAction === item.action"
          @click="runAction(item.action)"
        >
          {{ reindexingAction === item.action ? '提交中...' : item.label }}
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.knowledge-settings-page {
  display: grid;
  gap: 18px;
  padding: 24px;
  min-width: 0;
}

.hero-card,
.status-card,
.action-panel {
  padding: 22px;
  border: 1px solid rgba(214, 132, 70, 0.16);
  border-radius: 20px;
  background: rgba(255, 252, 247, 0.96);
  min-width: 0;
}

.eyebrow {
  margin: 0 0 6px;
  color: #a16207;
  font-size: 12px;
}

h1,
h2,
p {
  margin: 0;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

label {
  display: grid;
  gap: 8px;
  color: #5f3518;
  font-weight: 700;
}

select {
  height: 40px;
  min-width: 0;
  width: 100%;
  box-sizing: border-box;
  padding: 0 12px;
  border: 1px solid rgba(148, 163, 184, 0.26);
  border-radius: 12px;
  background: #fff;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.status-card strong {
  color: #5f3518;
}

.status-pill {
  display: inline-flex;
  margin-top: 10px;
  padding: 3px 8px;
  border-radius: 999px;
  background: #fff4e6;
  color: #8a4b16;
  font-size: 12px;
}

.status-card p {
  margin-top: 8px;
  color: #7c6b5c;
  line-height: 1.6;
}

.impact-line {
  margin-top: 8px;
  color: #7c6b5c;
  line-height: 1.6;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

button {
  min-height: 38px;
  padding: 0 16px;
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 999px;
  background: rgba(255, 244, 230, 0.94);
  color: #8a4b16;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.56;
}

@media (max-width: 1199px) {
  .knowledge-settings-page {
    padding: 18px;
  }

  .status-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .knowledge-settings-page {
    gap: 14px;
    padding: 0;
  }

  .hero-card,
  .status-card,
  .action-panel {
    padding: 18px;
    border-radius: 18px;
  }

  .status-grid {
    grid-template-columns: 1fr;
  }

  .config-grid {
    grid-template-columns: 1fr;
  }

  .action-row {
    display: grid;
    grid-template-columns: 1fr;
  }

  button {
    width: 100%;
  }
}
</style>
