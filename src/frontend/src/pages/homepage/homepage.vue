<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const quickLinks = [
  { key: 'workspace', label: '工作台', target: '/workspace' },
  { key: 'agent', label: '智能体', target: '/agent' },
  { key: 'mcp', label: 'MCP', target: '/mcp-server' },
  { key: 'tool', label: '工具', target: '/tool' },
  { key: 'skill', label: 'Skill', target: '/agent-skill' },
  { key: 'knowledge', label: '知识库', target: '/knowledge' },
  { key: 'model', label: '模型', target: '/model' },
  { key: 'dashboard', label: '数据看板', target: '/dashboard' },
]

const openWorkspace = () => {
  router.push('/workspace')
}

const go = (target: string) => {
  router.push(target)
}
</script>

<template>
  <div class="homepage">
    <section class="hero">
      <div class="status-pill">Zuno Platform</div>
      <h1>准备开始什么？</h1>
      <p>先在这里进入工作台，或快速打开需要配置的能力模块。</p>

      <button type="button" class="composer-card" @click="openWorkspace">
        <div class="composer-placeholder">进入工作台，开始对话或发起 Agent 任务</div>
        <div class="composer-footer">
          <span class="composer-plus">+</span>
          <span class="composer-hint">聊天、Agent、附件分析、工具调用</span>
          <span class="composer-action">进入</span>
        </div>
      </button>

      <div class="quick-links">
        <button
          v-for="entry in quickLinks"
          :key="entry.key"
          type="button"
          class="quick-chip"
          @click="go(entry.target)"
        >
          {{ entry.label }}
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
.homepage {
  min-height: 100%;
  padding: 40px 24px 56px;
  background:
    radial-gradient(circle at top, rgba(219, 171, 129, 0.1), transparent 28%),
    linear-gradient(180deg, #f8f4ee 0%, #fcfaf7 100%);
}

.hero {
  width: min(860px, 100%);
  margin: 0 auto;
  padding-top: 56px;
  text-align: center;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(214, 132, 70, 0.1);
  color: #bf6d37;
  font-size: 13px;
  letter-spacing: 0.08em;
}

.hero h1 {
  margin: 22px 0 12px;
  color: #2d241c;
  font-size: clamp(34px, 4.6vw, 56px);
  line-height: 1.14;
  font-weight: 500;
  letter-spacing: -0.03em;
  font-family: 'Iowan Old Style', 'Palatino Linotype', 'Book Antiqua', Georgia, serif;
}

.hero p {
  margin: 0 auto;
  max-width: 560px;
  color: #766252;
  font-size: 17px;
  line-height: 1.7;
}

.composer-card {
  width: min(840px, 100%);
  margin: 34px auto 0;
  padding: 26px 28px 18px;
  border: 1px solid rgba(214, 132, 70, 0.12);
  border-radius: 28px;
  background: rgba(255, 252, 248, 0.92);
  box-shadow: 0 18px 40px rgba(120, 80, 42, 0.06);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.16s ease, box-shadow 0.16s ease, transform 0.16s ease;
}

.composer-card:hover {
  border-color: rgba(201, 109, 49, 0.24);
  box-shadow: 0 22px 44px rgba(120, 80, 42, 0.08);
  transform: translateY(-1px);
}

.composer-placeholder {
  color: rgba(70, 54, 43, 0.46);
  font-size: 18px;
  line-height: 1.5;
  min-height: 92px;
}

.composer-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #7b6857;
  font-size: 14px;
}

.composer-plus {
  width: 28px;
  height: 28px;
  display: inline-grid;
  place-items: center;
  border-radius: 999px;
  border: 1px solid rgba(214, 132, 70, 0.18);
  color: #9d7757;
  font-size: 18px;
  flex: 0 0 auto;
}

.composer-hint {
  flex: 1;
}

.composer-action {
  color: #3f3328;
  font-weight: 500;
}

.quick-links {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 12px;
}

.quick-chip {
  border: 1px solid rgba(214, 132, 70, 0.14);
  border-radius: 999px;
  background: rgba(255, 252, 248, 0.88);
  color: #4b3a2d;
  padding: 10px 18px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.16s ease, border-color 0.16s ease, transform 0.16s ease;
}

.quick-chip:hover {
  background: #fff7ef;
  border-color: rgba(201, 109, 49, 0.24);
  transform: translateY(-1px);
}

@media (max-width: 900px) {
  .homepage {
    padding: 28px 18px 42px;
  }

  .hero {
    padding-top: 28px;
  }

  .composer-card {
    padding: 22px 20px 16px;
  }

  .composer-placeholder {
    min-height: 72px;
    font-size: 16px;
  }
}
</style>
