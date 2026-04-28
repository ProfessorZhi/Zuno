<script lang="ts" setup>
import { computed } from "vue"
import type { HistoryListType } from "../../type"
import { zunoAgentAvatar } from "../../utils/brand"

const emits = defineEmits<{
  (event: "delete"): void
  (event: "select"): void
}>()

const props = withDefaults(
  defineProps<{
    item: HistoryListType
    timeLabel?: string
  }>(),
  {
    timeLabel: ""
  }
)

const relativeTime = computed(() => {
  if (props.timeLabel) return props.timeLabel

  try {
    const date = new Date(props.item.updatedTime || props.item.createTime)
    if (Number.isNaN(date.getTime())) return "未知时间"

    const now = new Date()
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60)

    if (diffInHours < 1) return "刚刚"
    if (diffInHours < 24) return `${Math.floor(diffInHours)} 小时前`
    if (diffInHours < 24 * 7) return `${Math.floor(diffInHours / 24)} 天前`

    return date.toLocaleDateString("zh-CN", {
      month: "short",
      day: "numeric"
    })
  } catch {
    return "未知时间"
  }
})

const sourceLabel = computed(() => (
  props.item.sourceType === "workspace"
    ? "工作台"
    : "Agent"
))

const deleteCard = (event: Event) => {
  event.stopPropagation()
  emits("delete")
}

const selectCard = () => {
  emits("select")
}

const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault()
    selectCard()
  }
}
</script>

<template>
  <div class="history-card" tabindex="0" role="button" @click="selectCard" @keydown="handleKeydown">
    <div class="card-main">
      <div class="card-left">
        <div class="avatar">
          <img :src="props.item.logo || zunoAgentAvatar" alt="" />
        </div>
        <div class="content">
          <div class="title-row">
            <div class="title" :title="props.item.name">
              {{ props.item.name || "未命名会话" }}
            </div>
          </div>
          <div class="subtitle-row">
            <div class="subtitle">{{ props.item.agent || "智能助手" }}</div>
            <span class="source-badge">{{ sourceLabel }}</span>
          </div>
        </div>
      </div>

      <div class="card-right">
        <div class="time">{{ props.item.absoluteTime }}</div>
        <div class="time-secondary">{{ relativeTime }}</div>
        <button class="delete-btn" type="button" aria-label="删除会话" @click="deleteCard">
          ×
        </button>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.history-card {
  width: 100%;
  margin-bottom: 8px;
  padding: 0;
  border: 1px solid transparent;
  border-radius: var(--zuno-radius-lg);
  background: transparent;
  text-align: left;
  cursor: pointer;
  transition: var(--zuno-transition-base);

  &:hover {
    background: rgba(255, 255, 255, 0.72);
  }

  &:focus-visible {
    outline: none;
    box-shadow: var(--zuno-focus-ring);
  }
}

.card-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 76px;
  padding: 14px;
  border-radius: var(--zuno-radius-lg);
}

.card-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  min-width: 0;
}

.avatar {
  width: 42px;
  height: 42px;
  overflow: hidden;
  border: 1px solid var(--zuno-border-soft);
  border-radius: 14px;
  background: var(--zuno-bg-muted);
  flex-shrink: 0;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.content {
  min-width: 0;
  flex: 1;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--zuno-text-primary);
  font-size: 14px;
  font-weight: 600;
  line-height: 1.35;
}

.subtitle-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.subtitle {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--zuno-text-secondary);
  font-size: 12px;
  line-height: 1.4;
}

.source-badge {
  flex-shrink: 0;
  min-height: 18px;
  padding: 0 8px;
  border-radius: 999px;
  background: rgba(200, 117, 61, 0.08);
  color: #9d5f34;
  font-size: 11px;
  line-height: 18px;
}

.card-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
}

.time {
  color: var(--zuno-text-secondary);
  font-size: 11px;
  line-height: 1.2;
}

.time-secondary {
  color: var(--zuno-text-muted);
  font-size: 11px;
  line-height: 1;
}

.delete-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: 1px solid transparent;
  border-radius: 999px;
  background: transparent;
  color: var(--zuno-text-muted);
  font-size: 18px;
  line-height: 1;
  opacity: 0;
  cursor: pointer;
  transition: var(--zuno-transition-base);
}

.history-card:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  border-color: rgba(188, 120, 103, 0.24);
  background: rgba(188, 120, 103, 0.08);
  color: #8f5144;
}

.history-card.active {
  border-color: var(--zuno-border-strong);
  background: var(--zuno-selected);
  box-shadow: 0 10px 24px rgba(48, 43, 38, 0.06);

  .card-main {
    box-shadow: inset 0 0 0 1px rgba(164, 149, 133, 0.28);
  }

  .title {
    color: #1f2329;
  }

  .subtitle {
    color: var(--zuno-text-tertiary);
  }

  .time {
    color: var(--zuno-text-primary);
  }

  .delete-btn {
    opacity: 1;
  }
}

@media (max-width: 480px) {
  .card-main {
    min-height: 68px;
    padding: 12px;
  }

  .avatar {
    width: 38px;
    height: 38px;
  }

  .title {
    font-size: 13px;
  }
}
</style>
