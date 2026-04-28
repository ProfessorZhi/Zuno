<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const selectedMode = ref<'normal' | 'agent'>('normal')
const draft = ref('')

const modes = [
  { id: 'normal' as const, label: '聊天模式', description: '轻量对话、图片理解和快速问答。' },
  { id: 'agent' as const, label: 'Agent 模式', description: '调用工具、MCP、Skill 和附件分析。' },
]

const quickLinks = [
  { key: 'agent', label: '智能体', target: '/agent' },
  { key: 'mcp', label: 'MCP', target: '/mcp-server' },
  { key: 'tool', label: '工具', target: '/tool' },
  { key: 'skill', label: 'Skill', target: '/agent-skill' },
  { key: 'knowledge', label: '知识库', target: '/knowledge' },
  { key: 'model', label: '模型', target: '/model' },
  { key: 'dashboard', label: '数据看板', target: '/dashboard' },
]

const activeMode = computed(() => modes.find((mode) => mode.id === selectedMode.value) || modes[0])

const openWorkspace = () => {
  const query: Record<string, string> = {
    mode: selectedMode.value,
    execution_mode: 'tool',
    access_scope: 'workspace',
  }

  const message = draft.value.trim()
  if (message) query.message = message

  router.push({ name: 'workspaceDefaultPage', query })
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault()
    openWorkspace()
  }
}

const go = (target: string) => {
  router.push(target)
}
</script>

<template>
  <div class="homepage">
    <section class="home-center">
      <div class="brand-pill">Zuno Platform</div>
      <h1>准备开始什么？</h1>
      <p class="subtitle">从这里进入工作台，或先配置智能体、MCP、工具、Skill、知识库和模型。</p>

      <div class="composer-card">
        <textarea
          v-model="draft"
          class="composer-input"
          :placeholder="selectedMode === 'agent' ? '描述一个任务，Zuno 会进入 Agent 模式处理。' : '输入一个问题，开始聊天。'"
          rows="3"
          @keydown="handleKeydown"
        />

        <div class="composer-footer">
          <div class="mode-switcher" aria-label="选择模式">
            <button
              v-for="mode in modes"
              :key="mode.id"
              type="button"
              :class="['mode-pill', { active: selectedMode === mode.id }]"
              @click="selectedMode = mode.id"
            >
              {{ mode.label }}
            </button>
          </div>
          <button type="button" class="composer-action" @click="openWorkspace">进入</button>
        </div>
      </div>

      <div class="mode-copy">{{ activeMode.description }}</div>

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
  display: grid;
  place-items: center;
  padding: 56px 24px 72px;
  background:
    radial-gradient(circle at 50% 16%, rgba(209, 140, 82, 0.08), transparent 28%),
    linear-gradient(180deg, #f8f4ed 0%, #fcfaf6 100%);
}

.home-center {
  width: min(920px, 100%);
  text-align: center;
}

.brand-pill {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 14px;
  border-radius: 999px;
  background: rgba(207, 128, 70, 0.1);
  color: #a76234;
  font-size: 13px;
  letter-spacing: 0.08em;
}

h1 {
  margin: 24px 0 10px;
  color: #302820;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: clamp(42px, 5.6vw, 68px);
  font-weight: 400;
  line-height: 1.06;
  letter-spacing: -0.055em;
}

.subtitle {
  margin: 0 auto 32px;
  max-width: 620px;
  color: #76685b;
  font-size: 16px;
  line-height: 1.7;
}

.composer-card {
  width: min(820px, 100%);
  margin: 0 auto;
  padding: 22px 24px 18px;
  border: 1px solid rgba(219, 197, 177, 0.78);
  border-radius: 28px;
  background: rgba(255, 253, 249, 0.92);
  box-shadow: 0 24px 60px rgba(83, 57, 34, 0.07);
  text-align: left;
}

.composer-input {
  width: 100%;
  min-height: 112px;
  border: none;
  resize: none;
  outline: none;
  background: transparent;
  color: #342920;
  font-size: 18px;
  line-height: 1.55;
}

.composer-input::placeholder {
  color: rgba(72, 58, 47, 0.42);
}

.composer-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.mode-switcher {
  display: inline-flex;
  gap: 8px;
  padding: 5px;
  border: 1px solid rgba(219, 197, 177, 0.74);
  border-radius: 999px;
  background: rgba(250, 246, 239, 0.82);
}

.mode-pill {
  border: none;
  border-radius: 999px;
  background: transparent;
  color: #756455;
  padding: 9px 16px;
  font-size: 14px;
  cursor: pointer;
}

.mode-pill.active {
  background: #c8753d;
  color: #fffaf4;
  box-shadow: 0 10px 22px rgba(172, 98, 47, 0.16);
}

.composer-action {
  border: none;
  border-radius: 999px;
  background: #c8753d;
  color: #fffaf4;
  min-width: 82px;
  height: 42px;
  padding: 0 20px;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 12px 24px rgba(172, 98, 47, 0.18);
}

.mode-copy {
  margin-top: 14px;
  color: #8a7765;
  font-size: 13px;
}

.quick-links {
  margin-top: 24px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
}

.quick-chip {
  border: 1px solid rgba(219, 197, 177, 0.74);
  border-radius: 999px;
  background: rgba(255, 253, 249, 0.78);
  color: #564639;
  padding: 10px 18px;
  font-size: 14px;
  cursor: pointer;
}

@media (max-width: 720px) {
  .homepage {
    padding: 36px 16px 48px;
  }

  .composer-card {
    padding: 18px 18px 16px;
  }

  .composer-footer {
    align-items: stretch;
    flex-direction: column;
  }

  .composer-action {
    width: 100%;
  }
}
</style>
