<script setup lang="ts">
import { Search } from '@element-plus/icons-vue'

const model = defineModel<string>({ default: '' })

withDefaults(defineProps<{
  placeholder?: string
  clearable?: boolean
}>(), {
  placeholder: '搜索',
  clearable: true,
})

const emit = defineEmits<{
  clear: []
  enter: [value: string]
}>()
</script>

<template>
  <el-input
    v-model="model"
    class="search-input"
    :clearable="clearable"
    :placeholder="placeholder"
    @clear="emit('clear')"
    @keyup.enter="emit('enter', model)"
  >
    <template #prefix>
      <el-icon><Search /></el-icon>
    </template>
  </el-input>
</template>

<style scoped>
.search-input {
  width: min(100%, 320px);
}
</style>
