<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

type MascotState = 'idle' | 'listening' | 'thinking' | 'typing' | 'success' | 'confused' | 'error' | 'hover' | 'click'

const props = withDefaults(defineProps<{
  size?: 'avatar' | 'beacon' | 'tiny'
  animated?: boolean
  interactive?: boolean
  ariaLabel?: string
  state?: MascotState
}>(), {
  size: 'avatar',
  animated: false,
  interactive: false,
  ariaLabel: 'Zuno',
  state: undefined,
})

const emit = defineEmits<{
  (event: 'pet-click'): void
}>()

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

const rootTag = computed(() => props.interactive ? 'button' : 'div')
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

const startExpressionLoop = () => {
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
    startExpressionLoop()
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
    stateTimer = window.setTimeout(() => setMascotState(props.state || returnState), 680)
    return
  }

  if (state === 'click') {
    faceExpression.value = ''
    stateTimer = window.setTimeout(() => setMascotState(props.state || returnState), 520)
  }
}

const syncFromProps = () => {
  if (props.state) {
    setMascotState(props.state)
    return
  }
  clearStateTimer()
  if (props.animated) {
    setMascotState('idle')
    return
  }
  clearExpressionTimer()
  currentState.value = 'idle'
  persistentState.value = 'idle'
  faceExpression.value = ''
}

const handleClick = () => {
  setMascotState('click')
  if (!props.interactive) return
  emit('pet-click')
}

const handleHover = () => {
  setMascotState('hover')
}

watch(() => props.animated, syncFromProps)
watch(() => props.state, syncFromProps)

onMounted(syncFromProps)

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
  <component
    :is="rootTag"
    :class="['mascot-presence', `size-${props.size}`, `state-${currentState}`, { 'is-animated': props.animated, 'is-interactive': props.interactive }]"
    :aria-label="props.ariaLabel"
    :type="props.interactive ? 'button' : undefined"
    :role="props.interactive ? undefined : 'img'"
    @mouseenter="handleHover"
    @click="handleClick"
  >
    <div class="mascot-stage">
      <div class="yu-pet">
        <div :class="starClass"></div>
        <div :class="faceClass">
          <div class="yu-eye left"></div>
          <div class="yu-eye right"></div>
        </div>
      </div>
    </div>
  </component>
</template>

<style scoped>
.mascot-presence {
  --mascot-slot-size: 44px;
  --mascot-scale: 0.3666667;
  --zuno-mascot-fill: #f59e0b;
  position: relative;
  width: var(--mascot-slot-size);
  height: var(--mascot-slot-size);
  display: block;
  border: 0;
  padding: 0;
  background: transparent;
  overflow: visible;
}

.mascot-presence.size-beacon {
  --mascot-slot-size: 96px;
  --mascot-scale: 0.8;
}

.mascot-presence.size-tiny {
  --mascot-slot-size: 32px;
  --mascot-scale: 0.2666667;
}

.mascot-presence.is-interactive {
  cursor: pointer;
}

.mascot-stage {
  position: absolute;
  top: 0;
  left: 0;
  width: 120px;
  height: 120px;
  transform: scale(var(--mascot-scale));
  transform-origin: 0 0;
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
