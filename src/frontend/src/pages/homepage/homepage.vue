<script setup lang="ts">
import { useRouter } from 'vue-router'
import {
  Box,
  CollectionTag,
  Connection,
  Cpu,
  DataAnalysis,
  FolderOpened,
  Grid,
  SuitcaseLine,
} from '@element-plus/icons-vue'

const router = useRouter()

const platformEntries = [
  { key: 'agent', title: '智能体', description: '创建和管理 Agent，配置系统提示词、模型、知识和执行边界。', icon: Cpu, target: '/agent' },
  { key: 'mcp', title: 'MCP', description: '接入和管理外部 MCP Server，把第三方能力挂到平台里。', icon: Connection, target: '/mcp-server' },
  { key: 'tool', title: '工具', description: '决定 Agent 能调哪些工具，以及每个工具如何配置。', icon: Grid, target: '/tool' },
  { key: 'skill', title: 'Skill', description: '沉淀可复用的技能模板，把常见任务的执行方式标准化。', icon: CollectionTag, target: '/agent-skill' },
  { key: 'knowledge', title: '知识库', description: '接入资料和文档，为知识问答和 RAG 检索提供上下文。', icon: FolderOpened, target: '/knowledge' },
  { key: 'model', title: '模型', description: '管理模型和密钥，为不同 Agent 分配合适的大模型。', icon: Box, target: '/model' },
  { key: 'dashboard', title: '数据看板', description: '查看调用量、运行状态和平台整体的使用情况。', icon: DataAnalysis, target: '/dashboard' },
  { key: 'workspace', title: '工作台', description: '进入聊天模式和 Agent 模式，开始真实对话与执行。', icon: SuitcaseLine, target: '/workspace' },
]

const go = (target: string) => {
  router.push(target)
}
</script>

<template>
  <div class="homepage">
    <section class="hero-card">
      <div class="hero-eyebrow">ZUNO PLATFORM HOME</div>
      <h1>首页负责配置平台，工作台负责执行任务。</h1>
      <p>
        这里是平台总入口，用来统一管理智能体、MCP、工具、Skill、知识库、模型和数据看板。
        配置完成后，再进入工作台执行聊天和 Agent 任务。
      </p>
      <div class="hero-actions">
        <el-button type="primary" size="large" @click="go('/workspace')">进入工作台</el-button>
        <el-button size="large" @click="go('/agent')">配置智能体</el-button>
      </div>
    </section>

    <section class="entry-section">
      <div class="section-head">
        <h2>平台入口</h2>
        <p>这里是平台配置首页，不是聊天页。你可以从这里进入所有管理与配置模块。</p>
      </div>

      <div class="entry-grid">
        <button
          v-for="entry in platformEntries"
          :key="entry.key"
          type="button"
          class="entry-card"
          @click="go(entry.target)"
        >
          <span class="entry-icon">
            <el-icon><component :is="entry.icon" /></el-icon>
          </span>
          <strong>{{ entry.title }}</strong>
          <p>{{ entry.description }}</p>
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
.homepage {
  min-height: 100%;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background: linear-gradient(180deg, #f7f2ea 0%, #fbf8f3 100%);
}

.hero-card,
.entry-section {
  border-radius: 28px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  background: rgba(255, 252, 248, 0.92);
  box-shadow: 0 18px 40px rgba(120, 80, 42, 0.08);
}

.hero-card { padding: 32px; }

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(218, 135, 73, 0.12);
  color: #bf6d37;
  font-size: 13px;
  letter-spacing: 0.14em;
}

.hero-card h1 {
  margin: 16px 0 12px;
  font-size: 46px;
  line-height: 1.08;
  color: #2f241b;
}

.hero-card p {
  max-width: 900px;
  margin: 0;
  font-size: 17px;
  line-height: 1.8;
  color: #6d5a49;
}

.hero-actions {
  margin-top: 24px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.entry-section { padding: 26px; }
.section-head { margin-bottom: 18px; }
.section-head h2 { margin: 0; font-size: 26px; color: #32261d; }
.section-head p { margin: 8px 0 0; color: #7a6655; }

.entry-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.entry-card {
  border: 1px solid rgba(214, 132, 70, 0.14);
  border-radius: 22px;
  background: linear-gradient(180deg, #fffdf9 0%, #fff7ef 100%);
  padding: 20px;
  text-align: left;
  cursor: pointer;
  transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
}

.entry-card:hover {
  transform: translateY(-2px);
  border-color: rgba(201, 109, 49, 0.3);
  box-shadow: 0 14px 24px rgba(120, 80, 42, 0.08);
}

.entry-icon {
  width: 44px;
  height: 44px;
  display: inline-grid;
  place-items: center;
  border-radius: 14px;
  background: rgba(218, 135, 73, 0.1);
  color: #c56f36;
  font-size: 20px;
}

.entry-card strong {
  display: block;
  margin-top: 14px;
  font-size: 20px;
  color: #34271f;
}

.entry-card p {
  margin: 10px 0 0;
  font-size: 14px;
  line-height: 1.75;
  color: #715e4e;
}

@media (max-width: 1200px) {
  .entry-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
}

@media (max-width: 900px) {
  .entry-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .hero-card h1 { font-size: 36px; }
}

@media (max-width: 640px) {
  .homepage { padding: 18px; }
  .entry-grid { grid-template-columns: 1fr; }
  .hero-card h1 { font-size: 30px; }
}
</style>
