<script setup lang="ts">
defineProps<{
  icon?: string
  title: string
  iconAlt?: string
}>()
</script>

<template>
  <section class="page-header zuno-settings-header">
    <div class="title-block">
      <img v-if="icon" :src="icon" :alt="iconAlt || title" class="page-icon" />
      <div>
        <h1>{{ title }}</h1>
        <slot name="subtitle" />
      </div>
    </div>

    <div v-if="$slots.actions" class="header-actions">
      <slot name="actions" />
    </div>

    <div v-if="$slots.search" class="settings-search-row">
      <slot name="search" />
    </div>
  </section>
</template>
