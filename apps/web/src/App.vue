<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { Plus, Setting } from '@element-plus/icons-vue'
import { zunoAgentAvatar } from './utils/brand'
import defaultUserAvatar from './assets/user.svg'

const routeMaskVisible = ref(false)
const routeMaskActive = ref(false)
let routeMaskTimer = 0
let routeMaskEnterFrame = 0

const clearRouteMaskTimers = () => {
  window.clearTimeout(routeMaskTimer)
  window.cancelAnimationFrame(routeMaskEnterFrame)
}

const showRouteMask = (event: Event) => {
  const duration = Number((event as CustomEvent<{ duration?: number }>).detail?.duration || 1300)
  clearRouteMaskTimers()
  routeMaskVisible.value = true
  routeMaskActive.value = false
  routeMaskEnterFrame = window.requestAnimationFrame(() => {
    routeMaskActive.value = true
  })
  routeMaskTimer = window.setTimeout(() => {
    routeMaskActive.value = false
    routeMaskTimer = window.setTimeout(() => {
      routeMaskVisible.value = false
    }, 520)
  }, duration)
}

onMounted(() => {
  window.addEventListener('zuno-auth-route-mask', showRouteMask)
})

onBeforeUnmount(() => {
  window.removeEventListener('zuno-auth-route-mask', showRouteMask)
  clearRouteMaskTimers()
})
</script>

<template>
  <router-view></router-view>
  <div v-if="routeMaskVisible" class="route-mask" :class="{ active: routeMaskActive }" aria-hidden="true">
    <aside class="route-mask-sidebar">
      <div class="route-mask-brand">
        <img :src="zunoAgentAvatar" alt="" />
        <div>
          <strong>Zuno AI</strong>
          <span>Intelligence Workspace</span>
        </div>
      </div>
      <div class="route-mask-new">
        <el-icon><Plus /></el-icon>
        <span>New Chat</span>
      </div>
      <div class="route-mask-nav">
        <section>
          <div class="route-mask-title">
            <span>Zuno</span>
            <el-icon><Plus /></el-icon>
          </div>
          <div class="route-mask-row active">安全进入工作台</div>
        </section>
        <section>
          <div class="route-mask-title">
            <span>CHAT</span>
            <el-icon><Plus /></el-icon>
          </div>
          <div class="route-mask-row">New Chat</div>
          <div class="route-mask-row muted">工作区正在同步...</div>
        </section>
      </div>
      <div class="route-mask-footer">
        <span><el-icon><Setting /></el-icon>设置</span>
        <img :src="defaultUserAvatar" alt="" />
      </div>
    </aside>
    <main class="route-mask-main">
      <div class="route-mask-hero">
        <img :src="zunoAgentAvatar" alt="" />
        <h1>How can I help you today?</h1>
        <p>Your intelligent workspace is ready.</p>
      </div>
      <div class="route-mask-composer">
        <span>输入你的问题，直接开始对话。</span>
        <button type="button">发送</button>
      </div>
    </main>
  </div>
</template>

<style lang="scss" scoped>
.route-mask {
  position: fixed;
  inset: 0;
  z-index: 9999;
  display: flex;
  overflow: hidden;
  pointer-events: none;
  opacity: 0;
  background:
    radial-gradient(circle at 74% 20%, rgba(255, 255, 255, 0.88), transparent 34%),
    radial-gradient(circle at 12% 92%, rgba(245, 158, 11, 0.055), transparent 30%),
    #f9f9fb;
  filter: blur(10px);
  transform: scale(1.006);
  transition: opacity 0.42s ease, filter 0.52s ease, transform 0.52s ease;
}

.route-mask.active {
  opacity: 1;
  filter: blur(0);
  transform: scale(1);
}

.route-mask-sidebar {
  width: 264px;
  flex: 0 0 264px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.7);
  border-right: 1px solid rgba(255, 255, 255, 0.72);
  box-shadow: 40px 0 80px -20px rgba(15, 23, 42, 0.06);
  backdrop-filter: blur(30px);
}

.route-mask-brand {
  display: grid;
  grid-template-columns: 34px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
}

.route-mask-brand img {
  width: 34px;
  height: 34px;
  object-fit: contain;
}

.route-mask-brand div {
  display: grid;
  gap: 2px;
}

.route-mask-brand strong {
  color: #0f172a;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.18;
}

.route-mask-brand span {
  color: #94a3b8;
  font-size: 11px;
}

.route-mask-new {
  min-height: 36px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #ffffff;
  background: #f59e0b;
  font-size: 13px;
  font-weight: 600;
  box-shadow: 0 10px 20px rgba(245, 158, 11, 0.18);
}

.route-mask-nav {
  flex: 1;
  display: grid;
  align-content: start;
  gap: 16px;
  padding-top: 2px;
}

.route-mask-nav section {
  display: grid;
  gap: 6px;
}

.route-mask-title {
  min-height: 20px;
  padding: 0 2px 0 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #f59e0b;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.route-mask-row {
  min-height: 28px;
  border-radius: 8px;
  padding: 0 10px;
  display: flex;
  align-items: center;
  color: #94a3b8;
  font-size: 12px;
  font-weight: 500;
}

.route-mask-row.active {
  color: #b45309;
  background: rgba(245, 158, 11, 0.075);
}

.route-mask-row.muted {
  color: #a3b1c2;
}

.route-mask-footer {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid rgba(226, 232, 240, 0.58);
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #64748b;
  font-size: 12.5px;
}

.route-mask-footer span {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.route-mask-footer img {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: rgba(255, 251, 245, 0.96);
  border: 1px solid rgba(226, 232, 240, 0.78);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
}

.route-mask-main {
  flex: 1;
  position: relative;
  display: grid;
  place-items: center;
  background: #fffdf9;
}

.route-mask-hero {
  display: grid;
  justify-items: center;
  gap: 10px;
  margin-bottom: 120px;
  text-align: center;
}

.route-mask-hero img {
  width: 58px;
  height: 58px;
  object-fit: contain;
  filter: drop-shadow(0 14px 24px rgba(245, 158, 11, 0.18));
}

.route-mask-hero h1 {
  margin: 0;
  color: #171717;
  font-size: 32px;
  font-weight: 520;
  line-height: 1.2;
}

.route-mask-hero p {
  margin: 0;
  color: #94a3b8;
  font-size: 13px;
}

.route-mask-composer {
  position: absolute;
  left: 50%;
  bottom: 132px;
  width: min(720px, calc(100% - 48px));
  min-height: 112px;
  transform: translateX(-50%);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 24px;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.78);
  background: rgba(255, 255, 255, 0.74);
  box-shadow:
    0 30px 80px rgba(15, 23, 42, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.94);
  backdrop-filter: blur(26px) saturate(1.2);
}

.route-mask-composer span {
  color: #94a3b8;
  font-size: 15px;
}

.route-mask-composer button {
  align-self: flex-end;
  min-width: 74px;
  height: 36px;
  border: none;
  border-radius: 999px;
  color: #ffffff;
  background: #f59e0b;
  font-weight: 650;
}
</style>
