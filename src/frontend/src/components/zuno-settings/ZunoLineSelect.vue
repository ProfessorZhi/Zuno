<script setup lang="ts">
defineOptions({ inheritAttrs: false })

const model = defineModel<any>()

withDefaults(defineProps<{
  label?: string
  placeholder?: string
  multiple?: boolean
  filterable?: boolean
  collapseTags?: boolean
  collapseTagsTooltip?: boolean
  noDataText?: string
}>(), {
  label: '',
  placeholder: '选择',
  multiple: false,
  filterable: false,
  collapseTags: false,
  collapseTagsTooltip: false,
  noDataText: '暂无数据',
})
</script>

<template>
  <el-form-item v-bind="$attrs" :label="label">
    <el-select
      v-model="model"
      class="full-width"
      :placeholder="placeholder"
      :multiple="multiple"
      :filterable="filterable"
      :collapse-tags="collapseTags"
      :collapse-tags-tooltip="collapseTagsTooltip"
      :no-data-text="noDataText"
    >
      <slot />
    </el-select>
  </el-form-item>
</template>
