<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import {
  createDomainPackDraftAPI,
  createDomainPackDraftFromKnowledgeAPI,
} from '../../apis/domain-packs'
import { getKnowledgeListAPI, type KnowledgeResponse } from '../../apis/knowledge'

const router = useRouter()
const route = useRoute()
const saving = ref(false)
const sourceMode = ref<'blank' | 'knowledge'>('blank')
const knowledges = ref<KnowledgeResponse[]>([])
const form = ref({
  pack_id: 'contract_review_draft',
  name: '合同审查草稿',
  description: '用于领域包构建审查的草稿。',
  knowledge_id: '',
})

const buildSettingsQuery = () => ({
  ...route.query,
  settings_turn: String(Date.now()),
})

const loadKnowledges = async () => {
  try {
    const response = await getKnowledgeListAPI()
    if (response.data.status_code === 200) {
      knowledges.value = response.data.data || []
    }
  } catch (error) {
    console.error('加载知识库失败', error)
  }
}

const submitDraft = async () => {
  saving.value = true
  try {
    const payload = {
      pack_id: form.value.pack_id.trim(),
      name: form.value.name.trim(),
      description: form.value.description.trim(),
    }
    const response = sourceMode.value === 'knowledge'
      ? await createDomainPackDraftFromKnowledgeAPI({
        ...payload,
        knowledge_id: form.value.knowledge_id,
        file_ids: [],
      })
      : await createDomainPackDraftAPI(payload)
    if (response.data.status_code !== 200 || !response.data.data) {
      throw new Error(response.data.status_message || '创建领域包草稿失败')
    }
    ElMessage.success('领域包草稿已创建')
    router.push({
      name: 'workspaceSettingsKnowledgeDomainPackDetail',
      params: { packId: response.data.data.pack_id },
      query: buildSettingsQuery(),
    })
  } catch (error) {
    console.error('创建领域包草稿失败', error)
    ElMessage.error(error instanceof Error ? error.message : '创建领域包草稿失败')
  } finally {
    saving.value = false
  }
}

onMounted(loadKnowledges)
</script>

<template>
  <div class="domain-pack-create-page">
    <section class="hero-card">
      <p class="eyebrow">领域包构建页</p>
      <h1>先用代表性文件生成草稿，再人工审核后发布</h1>
    </section>

    <section class="panel">
      <h2>创建新的领域包</h2>
      <div class="form-grid">
        <label>
          <span>创建方式</span>
          <select v-model="sourceMode">
            <option value="blank">空白草稿</option>
            <option value="knowledge">从已有知识库选择代表性文件</option>
          </select>
        </label>
        <label>
          <span>Pack ID</span>
          <input v-model="form.pack_id" type="text" />
        </label>
        <label>
          <span>名称</span>
          <input v-model="form.name" type="text" />
        </label>
        <label>
          <span>说明</span>
          <input v-model="form.description" type="text" />
        </label>
        <label v-if="sourceMode === 'knowledge'">
          <span>来源知识库</span>
          <select v-model="form.knowledge_id">
            <option value="">选择知识库</option>
            <option v-for="item in knowledges" :key="item.id" :value="item.id">{{ item.name }}</option>
          </select>
        </label>
      </div>
      <div class="grid">
        <article class="card">
          <strong>代表性文件</strong>
          <p>从上传样本或已有知识库中挑代表性文件生成草稿，不直接改动正式知识库。</p>
        </article>
        <article class="card">
          <strong>审核 schema / prompt</strong>
          <p>审核实体、关系、extraction prompt、retrieval policy、community report prompt。</p>
        </article>
        <article class="card">
          <strong>发布领域包</strong>
          <p>确认后发布一个可绑定到多个知识库的领域包版本。</p>
        </article>
      </div>
      <div class="action-row">
        <button type="button" :disabled="saving || !form.pack_id || !form.name || (sourceMode === 'knowledge' && !form.knowledge_id)" @click="submitDraft">
          {{ saving ? '创建中...' : '创建草稿' }}
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.domain-pack-create-page {
  display: grid;
  gap: 18px;
  padding: 24px;
  min-width: 0;
}

.hero-card,
.panel,
.card {
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

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 14px;
}

label {
  display: grid;
  gap: 8px;
  color: #5f3518;
  font-weight: 700;
}

input,
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

.action-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
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

.card strong {
  color: #5f3518;
}

.card p {
  margin-top: 8px;
  color: #7c6b5c;
  line-height: 1.6;
}

@media (max-width: 1199px) {
  .domain-pack-create-page {
    padding: 18px;
  }
}

@media (max-width: 767px) {
  .domain-pack-create-page {
    gap: 14px;
    padding: 0;
  }

  .hero-card,
  .panel,
  .card {
    padding: 18px;
    border-radius: 18px;
  }

  .grid {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .action-row button {
    width: 100%;
  }
}
</style>
