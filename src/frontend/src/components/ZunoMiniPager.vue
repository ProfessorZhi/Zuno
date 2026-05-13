<script setup lang="ts">
import { computed, watch } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const props = withDefaults(defineProps<{
  page: number
  total: number
  pageSize?: number
  align?: 'start' | 'center' | 'end'
}>(), {
  pageSize: 6,
  align: 'end',
})

const emit = defineEmits<{
  (event: 'update:page', value: number): void
}>()

const pageCount = computed(() => Math.max(1, Math.ceil(props.total / props.pageSize)))
const safePage = computed(() => Math.min(Math.max(props.page || 1, 1), pageCount.value))
const visible = computed(() => props.total > props.pageSize)

watch([safePage, pageCount], () => {
  if (props.page !== safePage.value) emit('update:page', safePage.value)
})

const go = (offset: number) => {
  emit('update:page', Math.min(Math.max(safePage.value + offset, 1), pageCount.value))
}
</script>

<template>
  <nav v-if="visible" :class="['zuno-mini-pager', `align-${align}`]" aria-label="列表翻页">
    <button
      class="zuno-mini-page-button"
      type="button"
      :disabled="safePage <= 1"
      aria-label="上一页"
      @click="go(-1)"
    >
      <el-icon><ArrowLeft /></el-icon>
    </button>
    <span class="zuno-mini-page-status">{{ safePage }} / {{ pageCount }}</span>
    <button
      class="zuno-mini-page-button"
      type="button"
      :disabled="safePage >= pageCount"
      aria-label="下一页"
      @click="go(1)"
    >
      <el-icon><ArrowRight /></el-icon>
    </button>
  </nav>
</template>

<style scoped>
.zuno-mini-pager {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 28px;
  padding-top: 8px;
}

.zuno-mini-pager.align-start {
  justify-content: flex-start;
}

.zuno-mini-pager.align-center {
  justify-content: center;
}

.zuno-mini-pager.align-end {
  justify-content: flex-end;
}

.zuno-mini-page-button {
  width: 26px;
  height: 26px;
  display: inline-grid;
  place-items: center;
  padding: 0;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  transition:
    color 0.16s ease,
    background 0.16s ease,
    transform 0.16s cubic-bezier(0.2, 0.78, 0.22, 1);
}

.zuno-mini-page-button:hover:not(:disabled) {
  color: #b45309;
  background: rgba(245, 158, 11, 0.08);
  transform: translateY(-1px);
}

.zuno-mini-page-button:disabled {
  opacity: 0.34;
  cursor: default;
}

.zuno-mini-page-status {
  min-width: 42px;
  color: #94a3b8;
  font-size: 12px;
  font-variant-numeric: tabular-nums;
  text-align: center;
  user-select: none;
}
</style>
