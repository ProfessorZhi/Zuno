<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { createKnowledgeAPI } from '../../apis/knowledge'
import { getVisibleLLMsAPI, type LLMResponse } from '../../apis/llm'
import {
  createDefaultKnowledgeConfig,
  toProductKnowledgeConfig,
  type KnowledgeProductMode,
} from '../../utils/knowledge-config'

const retrievalModes = [
  {
    value: 'standard',
    title: '标准检索',
    subtitle: '普通文档问答、FAQ、具体内容查找',
  },
  {
    value: 'enhanced',
    title: '增强检索',
    subtitle: '关系推理、跨文档分析、图谱增强问答',
  },
] as const

const router = useRouter()
const route = useRoute()
const saving = ref(false)
const loadingOptions = ref(false)
const productMode = ref<KnowledgeProductMode>('standard')
const models = ref<LLMResponse[]>([])
const form = ref({
  knowledge_name: '新知识库',
  knowledge_desc: '用于 Product Wiring V1 的知识库说明。',
  text_embedding_model_id: '',
  vl_embedding_model_id: '',
  rerank_model_id: '',
  graphrag_project_id: String(route.query.graphrag_project_id || route.query.domain_pack_id || ''),
})

const embeddingModels = computed(() => models.value.filter((item) => item.llm_type === 'Embedding'))
const rerankModels = computed(() => models.value.filter((item) => item.llm_type === 'Rerank'))
const canSubmit = computed(() => (
  form.value.knowledge_name.trim().length >= 2
  && form.value.knowledge_desc.trim().length >= 10
))

const loadOptions = async () => {
  loadingOptions.value = true
  try {
    const modelResponse = await getVisibleLLMsAPI()
    if (modelResponse.data.status_code === 200) {
      models.value = Object.values(modelResponse.data.data || {}).flat().filter(Boolean) as LLMResponse[]
    }
  } catch (error) {
    console.error('加载创建选项失败', error)
    ElMessage.error('加载创建选项失败')
  } finally {
    loadingOptions.value = false
  }
}

const buildConfig = () => {
  const base = createDefaultKnowledgeConfig()
  base.model_refs.text_embedding_model_id = form.value.text_embedding_model_id || null
  base.model_refs.vl_embedding_model_id = form.value.vl_embedding_model_id || null
  base.model_refs.rerank_model_id = form.value.rerank_model_id || null
  base.graphrag_project_id = productMode.value === 'enhanced' ? (form.value.graphrag_project_id || null) : null
  return toProductKnowledgeConfig(productMode.value, base)
}

const submit = async () => {
  if (!canSubmit.value) {
    ElMessage.warning('请填写 2 个字以上名称和 10 个字以上说明')
    return
  }
  saving.value = true
  try {
    const response = await createKnowledgeAPI({
      knowledge_name: form.value.knowledge_name.trim(),
      knowledge_desc: form.value.knowledge_desc.trim(),
      knowledge_config: buildConfig(),
    })
    if (response.data.status_code !== 200) {
      throw new Error(response.data.status_message || '创建知识库失败')
    }
    ElMessage.success('知识库已创建')
    const knowledgeId = response.data.data?.id
    if (knowledgeId) {
      router.push({
        name: 'workspaceSettingsKnowledgeFile',
        params: { knowledgeId },
        query: {
          name: form.value.knowledge_name.trim(),
          settings_turn: String(Date.now()),
        },
      })
      return
    }
    router.push({ name: 'workspaceSettingsKnowledge', query: { settings_turn: String(Date.now()) } })
  } catch (error) {
    console.error('创建知识库失败', error)
    ElMessage.error(error instanceof Error ? error.message : '创建知识库失败')
  } finally {
    saving.value = false
  }
}

watch(
  () => route.query.graphrag_project_id,
  (value) => {
    if (value) {
      form.value.graphrag_project_id = String(value)
      productMode.value = 'enhanced'
    }
  },
)

onMounted(loadOptions)
</script>

<template>
  <div class="knowledge-create-page">
    <section class="hero-card">
      <p class="eyebrow">知识库创建向导</p>
      <h1>先选产品模式，再决定模型、GraphRAG Project 和构建计划</h1>
      <p class="copy">
        这里把知识库创建和后续参数维护拆开。创建时只做一次性的构建决策，后续调参放到维护页。
      </p>
    </section>

    <section class="panel" v-loading="loadingOptions">
      <h2>1. 选择检索模式</h2>
      <div class="mode-grid">
        <button
          v-for="item in retrievalModes"
          :key="item.title"
          type="button"
          class="mode-card"
          :class="{ active: productMode === item.value }"
          @click="productMode = item.value"
        >
          <strong>{{ item.title }}</strong>
          <p>{{ item.subtitle }}</p>
        </button>
      </div>
    </section>

    <section class="panel form-panel">
      <h2>2. 选择索引与领域模板</h2>
      <div class="form-grid">
        <label>
          <span>知识库名称</span>
          <input v-model="form.knowledge_name" type="text" placeholder="2-10 个字" />
        </label>
        <label>
          <span>说明</span>
          <input v-model="form.knowledge_desc" type="text" placeholder="说明这个知识库收什么资料" />
        </label>
        <label>
          <span>Embedding</span>
          <select v-model="form.text_embedding_model_id">
            <option value="">稍后选择</option>
            <option v-for="model in embeddingModels" :key="model.llm_id" :value="model.llm_id">
              {{ model.model }} · {{ model.provider }}
            </option>
          </select>
        </label>
        <label>
          <span>Rerank</span>
          <select v-model="form.rerank_model_id">
            <option value="">稍后选择</option>
            <option v-for="model in rerankModels" :key="model.llm_id" :value="model.llm_id">
              {{ model.model }} · {{ model.provider }}
            </option>
          </select>
        </label>
        <label :class="{ muted: productMode === 'standard' }">
          <span>GraphRAG Project</span>
          <input
            v-model="form.graphrag_project_id"
            type="text"
            :disabled="productMode === 'standard'"
            placeholder="可选 GraphRAG Project ID"
          />
        </label>
        <label>
          <span>构建计划</span>
          <input
            type="text"
            readonly
            :value="productMode === 'enhanced'
              ? `增强检索 · ${form.graphrag_project_id || '未绑定 GraphRAG Project'} · 创建后进入文件管理上传资料`
              : '标准检索 · 向量 + BM25 · 创建后进入文件管理上传资料'"
          />
        </label>
      </div>
      <div class="action-row">
        <button type="button" :disabled="saving || !canSubmit" @click="submit">
          {{ saving ? '创建中...' : '创建知识库' }}
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.knowledge-create-page {
  display: grid;
  gap: 18px;
  padding: 24px;
  min-width: 0;
}

.hero-card,
.panel {
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

h1 {
  font-size: 28px;
  color: #171717;
}

.copy {
  margin-top: 10px;
  color: #7c6b5c;
  line-height: 1.7;
}

.mode-grid,
.form-grid {
  display: grid;
  gap: 12px;
  margin-top: 14px;
}

.mode-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.mode-card {
  cursor: pointer;
  text-align: left;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid rgba(214, 132, 70, 0.16);
  background: rgba(255, 248, 240, 0.92);
}

.mode-card.active {
  border-color: rgba(245, 158, 11, 0.5);
  box-shadow: inset 0 0 0 1px rgba(245, 158, 11, 0.3);
}

.mode-card strong {
  color: #5f3518;
}

.mode-card p {
  margin-top: 8px;
  color: #7c6b5c;
  line-height: 1.6;
}

.form-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

label {
  display: grid;
  gap: 8px;
  min-width: 0;
}

label span {
  color: #5f3518;
  font-weight: 700;
}

input {
  height: 40px;
  padding: 0 12px;
  border: 1px solid rgba(148, 163, 184, 0.26);
  border-radius: 12px;
  min-width: 0;
  width: 100%;
  box-sizing: border-box;
}

select {
  height: 40px;
  padding: 0 12px;
  border: 1px solid rgba(148, 163, 184, 0.26);
  border-radius: 12px;
  min-width: 0;
  width: 100%;
  box-sizing: border-box;
  background: #fff;
}

.muted {
  opacity: 0.58;
}

.action-row {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 16px;
}

.action-row button {
  min-height: 38px;
  padding: 0 16px;
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 999px;
  background: rgba(255, 244, 230, 0.94);
  color: #8a4b16;
}

.action-row button:disabled {
  cursor: not-allowed;
  opacity: 0.56;
}

@media (max-width: 1199px) {
  .knowledge-create-page {
    padding: 18px;
  }

  h1 {
    font-size: 24px;
  }

  .form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 767px) {
  .knowledge-create-page {
    gap: 14px;
    padding: 0;
  }

  .hero-card,
  .panel {
    padding: 18px;
    border-radius: 18px;
  }

  h1 {
    font-size: 21px;
    line-height: 1.25;
  }

  .mode-grid,
  .form-grid {
    grid-template-columns: 1fr;
  }

  .mode-card {
    padding: 14px;
  }

  .action-row {
    display: grid;
  }

  .action-row button {
    width: 100%;
  }
}
</style>
