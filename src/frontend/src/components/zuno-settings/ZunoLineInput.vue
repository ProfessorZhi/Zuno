<script setup lang="ts">
import type { InputAutoSize } from 'element-plus'

defineOptions({ inheritAttrs: false })

const model = defineModel<string | number | undefined>({ default: '' })

withDefaults(defineProps<{
  label?: string
  placeholder?: string
  type?: string
  maxlength?: number | string
  showWordLimit?: boolean
  textarea?: boolean
  autosize?: InputAutoSize
  resize?: 'none' | 'both' | 'horizontal' | 'vertical'
}>(), {
  label: '',
  placeholder: '',
  type: 'text',
  showWordLimit: false,
  textarea: false,
  resize: 'none',
})
</script>

<template>
  <el-form-item v-bind="$attrs" :label="label">
    <el-input
      v-model="model"
      :type="textarea ? 'textarea' : type"
      :placeholder="placeholder"
      :maxlength="maxlength"
      :show-word-limit="showWordLimit"
      :autosize="autosize"
      :resize="resize"
    >
      <template v-if="$slots.suffix" #suffix>
        <slot name="suffix" />
      </template>
      <template v-if="$slots.prefix" #prefix>
        <slot name="prefix" />
      </template>
    </el-input>
  </el-form-item>
</template>
