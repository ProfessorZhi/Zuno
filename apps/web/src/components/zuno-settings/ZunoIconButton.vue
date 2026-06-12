<script setup lang="ts">
import type { Component } from 'vue'

defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<{
  icon?: Component
  type?: '' | 'default' | 'primary' | 'success' | 'warning' | 'info' | 'danger'
  title?: string
  ariaLabel?: string
  loading?: boolean
  disabled?: boolean
  active?: boolean
}>(), {
  type: 'default',
  title: '',
  ariaLabel: '',
  loading: false,
  disabled: false,
  active: false,
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()
</script>

<template>
  <el-button
    v-bind="$attrs"
    :class="['settings-icon-button', { 'is-create-open': props.active }]"
    :type="props.type || undefined"
    :icon="props.icon"
    :loading="props.loading"
    :disabled="props.disabled"
    :title="props.title"
    :aria-label="props.ariaLabel || props.title"
    circle
    @click="emit('click', $event)"
  />
</template>

<style scoped>
.settings-icon-button {
  width: 34px;
  height: 34px;
  min-width: 34px;
  padding: 0;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(255, 255, 255, 0.74);
  color: #64748b;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.04);
}

.settings-icon-button.el-button--primary {
  border-color: rgba(245, 158, 11, 0.26);
  background: #f59e0b;
  color: #fff;
}

.settings-icon-button :deep(.el-icon) {
  transition: transform 0.22s ease;
}

.settings-icon-button.is-create-open :deep(.el-icon) {
  transform: rotate(45deg);
}
</style>
