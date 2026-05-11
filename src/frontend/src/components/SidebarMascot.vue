<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

type MascotState = 'idle' | 'listening' | 'thinking' | 'typing' | 'success' | 'confused' | 'error' | 'hover' | 'click'

const props = withDefaults(defineProps<{
  showDemo?: boolean
}>(), {
  showDemo: false,
})

const currentState = ref<MascotState>('idle')
const persistentState = ref<MascotState>('idle')
const faceExpression = ref('')
let step = 0
let expressionTimer: ReturnType<typeof window.setTimeout> | null = null
let stateTimer: ReturnType<typeof window.setTimeout> | null = null

const sequence = [
  { state: '', duration: 3000 },
  { state: 'blink', duration: 150 },
  { state: 'tension', duration: 2500 },
  { state: 'blink', duration: 150 },
  { state: 'happy', duration: 2500 },
  { state: 'blink', duration: 150 },
]

const demoStates: Array<{ state: MascotState; label: string }> = [
  { state: 'idle', label: 'idle' },
  { state: 'listening', label: 'listening' },
  { state: 'thinking', label: 'thinking' },
  { state: 'typing', label: 'typing' },
  { state: 'success', label: 'success' },
  { state: 'confused', label: 'confused' },
  { state: 'error', label: 'error' },
  { state: 'hover', label: 'hover' },
  { state: 'click', label: 'click' },
]

const petClass = computed(() => ['yu-pet', `state-${currentState.value}`])
const faceClass = computed(() => ['yu-face', faceExpression.value, `state-${currentState.value}`])
const starClass = computed(() => ['yu-star', `state-${currentState.value}`])

const clearExpressionTimer = () => {
  if (expressionTimer) window.clearTimeout(expressionTimer)
  expressionTimer = null
}

const clearStateTimer = () => {
  if (stateTimer) window.clearTimeout(stateTimer)
  stateTimer = null
}

const nextExpression = () => {
  if (currentState.value !== 'idle') return
  const current = sequence[step]
  faceExpression.value = current.state
  step = (step + 1) % sequence.length
  expressionTimer = window.setTimeout(nextExpression, current.duration)
}

const startIdleLoop = () => {
  clearExpressionTimer()
  step = 0
  faceExpression.value = ''
  expressionTimer = window.setTimeout(nextExpression, sequence[0].duration)
}

const setPersistentState = (state: MascotState) => {
  if (state === 'idle' || state === 'listening' || state === 'thinking' || state === 'typing' || state === 'confused') {
    persistentState.value = state
  }
}

const applySteadyState = (state: MascotState) => {
  currentState.value = state
  setPersistentState(state)
  faceExpression.value = ''
  if (state === 'idle') {
    startIdleLoop()
    return
  }
  clearExpressionTimer()
}

const setMascotState = (state: MascotState) => {
  clearStateTimer()

  if (state === 'idle' || state === 'listening' || state === 'thinking' || state === 'typing' || state === 'confused') {
    applySteadyState(state)
    return
  }

  const returnState = persistentState.value
  clearExpressionTimer()
  currentState.value = state

  if (state === 'success') {
    faceExpression.value = 'happy'
    stateTimer = window.setTimeout(() => setMascotState('idle'), 950)
    return
  }

  if (state === 'error') {
    faceExpression.value = 'tension'
    stateTimer = window.setTimeout(() => setMascotState('confused'), 920)
    return
  }

  if (state === 'hover') {
    faceExpression.value = 'happy'
    stateTimer = window.setTimeout(() => setMascotState(returnState), 680)
    return
  }

  if (state === 'click') {
    faceExpression.value = ''
    stateTimer = window.setTimeout(() => setMascotState(returnState), 520)
  }
}

const handleHover = () => {
  setMascotState('hover')
}

const handleClick = () => {
  setMascotState('click')
}

onMounted(() => {
  startIdleLoop()
})

onBeforeUnmount(() => {
  clearExpressionTimer()
  clearStateTimer()
})

defineExpose({
  setMascotState,
  getMascotState: () => currentState.value,
})
</script>

<template>
  <div
    :class="petClass"
    role="img"
    aria-label="Zuno AI"
    @mouseenter="handleHover"
    @click="handleClick"
  >
    <div :class="starClass"></div>
    <div id="face" :class="faceClass">
      <div class="yu-eye left"></div>
      <div class="yu-eye right"></div>
    </div>
  </div>

  <div v-if="props.showDemo" class="mascot-demo-controls" aria-label="吉祥物状态演示">
    <button
      v-for="item in demoStates"
      :key="item.state"
      type="button"
      :class="{ active: currentState === item.state }"
      @click="setMascotState(item.state)"
    >
      {{ item.label }}
    </button>
  </div>
</template>

<style scoped>
:host,
:root {
  --zuno-mascot-fill: #f59e0b;
}

.yu-pet {
  position: relative;
  width: 120px;
  height: 120px;
  color: #f59e0b;
}

.yu-face {
  width: 100px;
  height: 90px;
  background: var(--zuno-mascot-fill, #f59e0b);
  border-radius: 35px;
  position: relative;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  padding: 0 15px;
  box-sizing: border-box;
}

.yu-star {
  position: absolute;
  top: -5px;
  right: 0px;
  width: 30px;
  height: 30px;
  background: var(--zuno-mascot-fill, #f59e0b);
  clip-path: polygon(50% 0%, 65% 35%, 100% 50%, 65% 65%, 50% 100%, 35% 65%, 0% 50%, 35% 35%);
}

.yu-eye {
  width: 16px;
  height: 28px;
  background: white;
  border-radius: 50px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  border: 0px solid white;
}

.yu-face.blink .yu-eye {
  height: 4px;
  width: 20px;
  border-radius: 10px;
  background: white;
  transform: translateY(0px);
}

.yu-face.tension .yu-eye {
  height: 6px;
  width: 20px;
  background: white;
  border-radius: 10px;
}

.yu-face.tension .yu-eye.left {
  transform: rotate(35deg);
}

.yu-face.tension .yu-eye.right {
  transform: rotate(-35deg);
}

.yu-face.happy .yu-eye {
  height: 12px;
  width: 24px;
  background: transparent;
  border: 4px solid white;
  border-bottom: none;
  border-radius: 50px 50px 0 0;
  transform: translateY(-4px);
}

.yu-face.state-listening .yu-eye {
  width: 12px;
  height: 32px;
  transform: translateY(-1px);
}

.yu-face.state-thinking .yu-eye {
  animation: mascot-eye-look 1.65s ease-in-out infinite;
}

.yu-face.state-typing {
  animation: mascot-face-float 1.35s ease-in-out infinite;
}

.yu-face.state-typing .yu-eye {
  width: 14px;
  height: 26px;
}

.yu-face.state-confused .yu-eye {
  width: 18px;
  height: 22px;
}

.yu-face.state-confused .yu-eye.left {
  transform: rotate(-12deg) translateY(1px);
}

.yu-face.state-confused .yu-eye.right {
  transform: rotate(12deg) translateY(-1px);
}

.yu-face.state-error {
  animation: mascot-face-shake 0.46s ease-in-out 2;
}

.yu-star.state-thinking {
  animation: mascot-star-rotate 3.8s linear infinite;
}

.yu-star.state-typing {
  animation: mascot-star-pulse 1.15s ease-in-out infinite;
}

.yu-star.state-click {
  animation: mascot-star-pop 0.42s cubic-bezier(0.16, 0.84, 0.18, 1.2) both;
}

.mascot-demo-controls {
  width: min(100%, 236px);
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 6px;
  margin-top: 18px;
}

.mascot-demo-controls button {
  height: 24px;
  padding: 0 8px;
  border: 1px solid rgba(26, 26, 26, 0.12);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.66);
  color: rgba(26, 26, 26, 0.62);
  font-size: 11px;
  font-weight: 700;
  line-height: 1;
  cursor: pointer;
  transition: color 0.18s ease, background 0.18s ease, border-color 0.18s ease, transform 0.18s ease;
}

.mascot-demo-controls button:hover,
.mascot-demo-controls button.active {
  border-color: rgba(26, 26, 26, 0.28);
  background: rgba(26, 26, 26, 0.9);
  color: white;
  transform: translateY(-1px);
}

@keyframes mascot-eye-look {
  0%,
  100% {
    transform: translateX(0);
  }
  28% {
    transform: translateX(-5px);
  }
  58% {
    transform: translateX(5px);
  }
}

@keyframes mascot-face-float {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}

@keyframes mascot-face-shake {
  0%,
  100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-4px);
  }
  50% {
    transform: translateX(4px);
  }
  75% {
    transform: translateX(-2px);
  }
}

@keyframes mascot-star-rotate {
  to {
    transform: rotate(360deg);
  }
}

@keyframes mascot-star-pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(0.88);
  }
}

@keyframes mascot-star-pop {
  0% {
    transform: scale(1);
  }
  45% {
    transform: scale(1.32) rotate(18deg);
  }
  100% {
    transform: scale(1);
  }
}

@media (prefers-reduced-motion: reduce) {
  .yu-face.state-thinking .yu-eye,
  .yu-face.state-typing,
  .yu-face.state-error,
  .yu-star.state-thinking,
  .yu-star.state-typing,
  .yu-star.state-click {
    animation: none;
  }
}
</style>
