<script setup lang="ts">
import { computed } from 'vue'
import { RefreshRight } from '@element-plus/icons-vue'
import { saveSettingsUiMode, type SettingsUiMode } from '../../../utils/settings-preferences'

const props = withDefaults(defineProps<{
  mode: SettingsUiMode
  compact?: boolean
}>(), {
  compact: false,
})

const modeOptions: Array<{ key: SettingsUiMode; label: string; description: string }> = [
  { key: 'traditional', label: '传统窗口', description: '左侧导航 + 独立设置页，默认推荐。' },
  { key: 'chat-flow', label: '聊天流', description: '把设置页作为对话内容打开。' },
]

const containerClass = computed(() => ({
  compact: props.compact,
}))

const applyMode = (mode: SettingsUiMode) => {
  if (mode === props.mode) return
  saveSettingsUiMode(mode)
  window.location.reload()
}
</script>

<template>
  <section class="settings-ui-mode-card" :class="containerClass">
    <div class="settings-ui-mode-copy">
      <strong>设置界面</strong>
      <span>切换后会自动刷新当前页面。</span>
    </div>
    <div class="settings-ui-mode-options" role="radiogroup" aria-label="设置界面模式">
      <button
        v-for="option in modeOptions"
        :key="option.key"
        type="button"
        class="settings-ui-mode-option"
        :class="{ active: mode === option.key }"
        :aria-checked="mode === option.key"
        role="radio"
        @click="applyMode(option.key)"
      >
        <span class="settings-ui-mode-label">{{ option.label }}</span>
        <small>{{ option.description }}</small>
      </button>
    </div>
    <div v-if="!compact" class="settings-ui-mode-hint">
      <el-icon><RefreshRight /></el-icon>
      <span>默认模式为传统窗口，聊天流适合临时把设置当作对话的一部分查看。</span>
    </div>
  </section>
</template>

<style scoped>
.settings-ui-mode-card {
  display: grid;
  gap: 14px;
  padding: 16px 18px;
  border: 1px solid rgba(214, 162, 86, 0.2);
  border-radius: 20px;
  background: rgba(255, 250, 244, 0.92);
}

.settings-ui-mode-card.compact {
  gap: 8px;
  padding: 10px;
  border-radius: 12px;
  border-color: rgba(188, 198, 208, 0.48);
  background: rgba(255, 255, 255, 0.62);
}

.settings-ui-mode-copy {
  display: grid;
  gap: 4px;
}

.settings-ui-mode-copy strong {
  font-size: 14px;
  color: #3d2b18;
}

.settings-ui-mode-copy span,
.settings-ui-mode-hint,
.settings-ui-mode-option small {
  font-size: 12px;
  line-height: 1.6;
  color: #7f6a53;
}

.settings-ui-mode-options {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.settings-ui-mode-card.compact .settings-ui-mode-options {
  gap: 6px;
}

.settings-ui-mode-option {
  display: grid;
  gap: 4px;
  min-height: 74px;
  padding: 12px 14px;
  border: 1px solid rgba(191, 147, 86, 0.24);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.88);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
}

.settings-ui-mode-card.compact .settings-ui-mode-option {
  min-height: 52px;
  padding: 8px 10px;
  border-radius: 10px;
}

.settings-ui-mode-option:hover {
  border-color: rgba(213, 139, 35, 0.46);
  box-shadow: 0 12px 30px rgba(212, 163, 86, 0.12);
  transform: translateY(-1px);
}

.settings-ui-mode-option.active {
  border-color: #d58b23;
  background: linear-gradient(180deg, rgba(255, 244, 228, 0.98), rgba(255, 250, 243, 0.96));
  box-shadow: 0 14px 34px rgba(213, 139, 35, 0.14);
}

.settings-ui-mode-label {
  font-size: 14px;
  font-weight: 600;
  color: #3d2b18;
}

.settings-ui-mode-card.compact .settings-ui-mode-copy strong,
.settings-ui-mode-card.compact .settings-ui-mode-label {
  font-size: 12px;
}

.settings-ui-mode-card.compact .settings-ui-mode-copy span,
.settings-ui-mode-card.compact .settings-ui-mode-option small {
  font-size: 11px;
  line-height: 1.4;
}

.settings-ui-mode-hint {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

@media (max-width: 720px) {
  .settings-ui-mode-options {
    grid-template-columns: 1fr;
  }
}
</style>
