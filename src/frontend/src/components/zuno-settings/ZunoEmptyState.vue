<script setup lang="ts">
import emptyDataIcon from '../../assets/dashboard/空数据.svg'

withDefaults(defineProps<{
  icon?: string
  alt?: string
}>(), {
  icon: emptyDataIcon,
  alt: '空数据',
})
</script>

<template>
  <div class="empty-state settings-empty-hint">
    <img :src="icon" :alt="alt" class="empty-state-icon" />
    <slot />
  </div>
</template>
