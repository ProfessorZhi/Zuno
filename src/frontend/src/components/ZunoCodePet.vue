<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { ZunoPetMood, ZunoPetSize } from './zuno-pet'

const props = withDefaults(defineProps<{
  mood?: ZunoPetMood
  size?: ZunoPetSize
  interactive?: boolean
  ariaLabel?: string
}>(), {
  mood: 'idle',
  size: 'hero',
  interactive: false,
  ariaLabel: 'Zuno AI',
})

const emit = defineEmits<{
  (event: 'pet-click'): void
}>()

const blinking = ref(false)
const pressed = ref(false)
let blinkTimer: ReturnType<typeof window.setTimeout> | null = null
let blinkResetTimer: ReturnType<typeof window.setTimeout> | null = null
let pressTimer: ReturnType<typeof window.setTimeout> | null = null

const canBlink = computed(() => ['idle', 'listening', 'thinking', 'typing'].includes(props.mood))
const isReducedMotion = () => window.matchMedia?.('(prefers-reduced-motion: reduce)').matches
const randomBetween = (min: number, max: number) => Math.round(min + Math.random() * (max - min))

const clearBlinkTimers = () => {
  if (blinkTimer) window.clearTimeout(blinkTimer)
  if (blinkResetTimer) window.clearTimeout(blinkResetTimer)
  blinkTimer = null
  blinkResetTimer = null
}

const scheduleBlink = () => {
  clearBlinkTimers()
  if (isReducedMotion() || !canBlink.value) return
  const delay = props.mood === 'listening'
    ? randomBetween(2600, 4600)
    : randomBetween(3600, 6800)

  blinkTimer = window.setTimeout(() => {
    blinking.value = true
    blinkResetTimer = window.setTimeout(() => {
      blinking.value = false
      scheduleBlink()
    }, props.mood === 'thinking' ? 96 : 118)
  }, delay)
}

const triggerPetClick = () => {
  if (!props.interactive) return
  pressed.value = true
  emit('pet-click')
  if (pressTimer) window.clearTimeout(pressTimer)
  pressTimer = window.setTimeout(() => {
    pressed.value = false
    pressTimer = null
  }, 520)
}

const handleKeydown = (event: KeyboardEvent) => {
  if (!props.interactive || (event.key !== 'Enter' && event.key !== ' ')) return
  event.preventDefault()
  triggerPetClick()
}

watch(() => props.mood, () => {
  blinking.value = false
  scheduleBlink()
})

onMounted(scheduleBlink)

onBeforeUnmount(() => {
  clearBlinkTimers()
  if (pressTimer) window.clearTimeout(pressTimer)
})
</script>

<template>
  <div
    class="zuno-code-pet"
    :class="[
      `size-${props.size}`,
      `mood-${props.mood}`,
      {
        'is-blinking': blinking,
        'is-interactive': props.interactive,
        'is-pressed': pressed,
      },
    ]"
    :aria-label="props.ariaLabel"
    :role="props.interactive ? 'button' : 'img'"
    :tabindex="props.interactive ? 0 : undefined"
    @click="triggerPetClick"
    @keydown="handleKeydown"
  >
    <div class="pet-orbit" aria-hidden="true">
      <span class="orbit-ring ring-one"></span>
      <span class="orbit-ring ring-two"></span>
      <span class="orbit-dot dot-one"></span>
      <span class="orbit-dot dot-two"></span>
    </div>

    <div class="pet-head" aria-hidden="true">
      <span class="pet-star"></span>
      <div class="pet-face">
        <span class="pet-eye left"></span>
        <span class="pet-eye right"></span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.zuno-code-pet {
  --pet-size: clamp(148px, 68cqw, 232px);
  --pet-orange: #f59e0b;
  --pet-orange-dark: #d97706;
  --pet-eye: #fff7ed;
  --pet-motion: 7.8s;
  position: relative;
  width: var(--pet-size);
  aspect-ratio: 1;
  display: grid;
  place-items: center;
  color: var(--pet-orange);
  filter: drop-shadow(0 24px 42px rgba(245, 158, 11, 0.12));
  transform-origin: center;
  container-type: inline-size;
}

.zuno-code-pet.size-hero {
  --pet-size: clamp(148px, 68cqw, 232px);
}

.zuno-code-pet.size-beacon {
  --pet-size: clamp(68px, 7.2vw, 96px);
  filter: drop-shadow(0 18px 34px rgba(245, 158, 11, 0.1));
}

.zuno-code-pet.size-avatar {
  --pet-size: 32px;
  filter: drop-shadow(0 8px 14px rgba(245, 158, 11, 0.12));
}

.zuno-code-pet.size-tiny {
  --pet-size: 24px;
  filter: none;
}

.pet-orbit,
.pet-head {
  grid-area: 1 / 1;
}

.pet-orbit {
  display: none;
}

.orbit-ring {
  position: absolute;
  inset: 12%;
  border: 1px solid rgba(245, 158, 11, 0.16);
  border-radius: 50%;
  transform: rotate(-12deg) scaleX(1.16);
}

.ring-two {
  inset: 20% 10% 18%;
  opacity: 0.72;
  transform: rotate(18deg) scaleX(1.1);
}

.orbit-dot {
  position: absolute;
  width: 4.8%;
  aspect-ratio: 1;
  border-radius: 50%;
  background: rgba(245, 158, 11, 0.42);
  box-shadow: 0 0 18px rgba(245, 158, 11, 0.28);
}

.dot-one {
  top: 18%;
  right: 18%;
}

.dot-two {
  left: 16%;
  bottom: 28%;
}

.pet-head {
  position: relative;
  width: 100%;
  height: 100%;
  aspect-ratio: auto;
  align-self: center;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  transition:
    transform 260ms cubic-bezier(0.2, 0.8, 0.2, 1),
    filter 260ms ease;
}

.pet-head::after {
  display: none;
}

.pet-star {
  position: absolute;
  top: -4.1667%;
  right: 0;
  z-index: 3;
  width: 25%;
  aspect-ratio: 1;
  background: var(--pet-orange);
  clip-path: polygon(50% 0%, 64% 35%, 100% 50%, 64% 65%, 50% 100%, 36% 65%, 0% 50%, 36% 35%);
  filter: drop-shadow(0 10px 20px rgba(245, 158, 11, 0.18));
  transition:
    opacity 220ms ease,
    transform 260ms cubic-bezier(0.2, 0.8, 0.2, 1),
    filter 220ms ease;
}

.pet-face {
  position: absolute;
  top: 0;
  left: 0;
  width: 83.333%;
  height: 75%;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: space-evenly;
  gap: 0;
  padding: 0 15%;
  box-sizing: border-box;
  border-radius: calc(var(--pet-size) * 35 / 120);
  background: var(--pet-orange);
  box-shadow: none;
  overflow: hidden;
}

.pet-face::before {
  display: none;
}

.pet-eye {
  position: relative;
  z-index: 2;
  width: 24%;
  height: 31.111%;
  border: 0 solid var(--pet-eye);
  border-radius: 999px;
  background: var(--pet-eye);
  box-shadow: none;
  transition:
    width 200ms cubic-bezier(0.2, 0.8, 0.2, 1),
    height 200ms cubic-bezier(0.2, 0.8, 0.2, 1),
    border 200ms cubic-bezier(0.2, 0.8, 0.2, 1),
    border-radius 200ms cubic-bezier(0.2, 0.8, 0.2, 1),
    background 200ms cubic-bezier(0.2, 0.8, 0.2, 1),
    transform 200ms cubic-bezier(0.2, 0.8, 0.2, 1);
}

.zuno-code-pet.size-avatar .pet-orbit,
.zuno-code-pet.size-tiny .pet-orbit {
  opacity: 0;
}

.zuno-code-pet.size-avatar .pet-star {
  width: 25%;
  top: -4.1667%;
  right: 0;
}

.zuno-code-pet.size-tiny .pet-star {
  width: 25%;
  top: -4.1667%;
  right: 0;
}

.zuno-code-pet.is-interactive {
  cursor: pointer;
}

.zuno-code-pet.is-interactive:hover .pet-head,
.zuno-code-pet.is-pressed .pet-head {
  transform: scale(1.018);
  filter: saturate(1.05);
}

.zuno-code-pet.is-pressed .pet-head {
  animation: zuno-pet-press 520ms cubic-bezier(0.18, 0.86, 0.24, 1) both;
}

.zuno-code-pet.is-pressed .pet-eye {
  width: 16%;
  height: 18%;
  border-radius: 999px;
  transform: scaleX(1.12);
}

.zuno-code-pet.is-interactive:hover .pet-star,
.zuno-code-pet.is-pressed .pet-star {
  opacity: 1;
  filter: drop-shadow(0 12px 22px rgba(245, 158, 11, 0.28));
}

.zuno-code-pet.is-interactive:hover .pet-star {
  transform: scale(1.16) rotate(10deg);
}

.zuno-code-pet.is-pressed .pet-star {
  animation: zuno-pet-star-press 520ms cubic-bezier(0.18, 0.86, 0.24, 1) both;
}

.zuno-code-pet.is-interactive:focus-visible {
  outline: none;
  filter:
    drop-shadow(0 0 0 rgba(245, 158, 11, 0))
    drop-shadow(0 0 18px rgba(245, 158, 11, 0.24));
}

.zuno-code-pet.is-blinking .pet-eye {
  width: 18%;
  height: max(3px, 6%);
  border-radius: 999px;
  transform: translateY(8%);
}

.zuno-code-pet.mood-listening .pet-head {
  transform: scale(1.025);
  filter: saturate(1.06);
}

.zuno-code-pet.mood-listening .pet-eye {
  width: 14.5%;
  height: 41%;
  animation: zuno-pet-eye-listen 2.8s ease-in-out infinite;
}

.zuno-code-pet.mood-listening .pet-star {
  opacity: 0.96;
  animation: zuno-pet-star-listen 2.8s ease-in-out infinite;
}

.zuno-code-pet.mood-thinking .pet-orbit {
  opacity: 0.9;
  animation: zuno-pet-orbit-think 4.6s ease-in-out infinite;
}

.zuno-code-pet.mood-thinking .pet-eye {
  animation: zuno-pet-eye-think 1.35s ease-in-out infinite;
}

.zuno-code-pet.mood-thinking .pet-star {
  animation: zuno-pet-star-think 1.9s ease-in-out infinite;
}

.zuno-code-pet.mood-typing {
  --pet-motion: 3.2s;
}

.zuno-code-pet.mood-typing .pet-head {
  animation: zuno-pet-typing-head 1.02s ease-in-out infinite;
}

.zuno-code-pet.mood-typing .pet-eye {
  animation: zuno-pet-eye-type 1.02s ease-in-out infinite;
}

.zuno-code-pet.mood-typing .pet-star {
  animation: zuno-pet-star-type 1.02s ease-in-out infinite;
}

.zuno-code-pet.mood-success .pet-head {
  animation: zuno-pet-success-pop 860ms cubic-bezier(0.18, 0.86, 0.24, 1) both;
}

.zuno-code-pet.mood-success .pet-eye {
  width: 19%;
  height: 15%;
  border: max(2px, 0.08em) solid var(--pet-eye);
  border-bottom: 0;
  border-radius: 999px 999px 0 0;
  background: transparent;
  box-shadow: none;
  transform: translateY(-26%);
}

.zuno-code-pet.mood-success .pet-star {
  animation: zuno-pet-star-success 860ms cubic-bezier(0.18, 0.86, 0.24, 1) both;
}

.zuno-code-pet.mood-confused .pet-head {
  transform: rotate(-2deg);
}

.zuno-code-pet.mood-confused .pet-eye.left {
  width: 11%;
  height: 26%;
  transform: rotate(16deg) translateY(3%);
}

.zuno-code-pet.mood-confused .pet-eye.right {
  width: 15%;
  height: 34%;
  transform: rotate(-10deg) translateY(-4%);
}

.zuno-code-pet.mood-confused .pet-star {
  opacity: 0.68;
  transform: scale(0.86) rotate(-8deg);
}

.zuno-code-pet.mood-error .pet-head {
  animation: zuno-pet-error-shake 720ms cubic-bezier(0.3, 0.7, 0.2, 1) both;
}

.zuno-code-pet.mood-error .pet-eye {
  width: 20%;
  height: max(4px, 7%);
  border-radius: 999px;
}

.zuno-code-pet.mood-error .pet-eye.left {
  transform: rotate(34deg);
}

.zuno-code-pet.mood-error .pet-eye.right {
  transform: rotate(-34deg);
}

.zuno-code-pet.mood-error .pet-star {
  opacity: 0.52;
  transform: scale(0.74);
}

.zuno-code-pet.mood-wake .pet-head {
  animation: zuno-pet-wake 920ms cubic-bezier(0.18, 0.86, 0.24, 1) both;
}

.zuno-code-pet.mood-wake .pet-eye {
  width: 14%;
  height: 40%;
}

.zuno-code-pet.mood-wake .pet-star {
  animation: zuno-pet-star-wake 920ms cubic-bezier(0.18, 0.86, 0.24, 1) both;
}

@keyframes zuno-pet-orbit-think {
  0%,
  100% {
    transform: rotate(-4deg) scale(1);
  }
  50% {
    transform: rotate(14deg) scale(1.025);
  }
}

@keyframes zuno-pet-eye-listen {
  0%,
  100% {
    transform: translateY(0) scaleY(1);
  }
  48% {
    transform: translateY(-4%) scaleY(1.08);
  }
}

@keyframes zuno-pet-star-listen {
  0%,
  100% {
    opacity: 0.84;
    transform: scale(0.96) rotate(0deg);
  }
  48% {
    opacity: 1;
    transform: scale(1.2) rotate(10deg);
  }
}

@keyframes zuno-pet-eye-think {
  0%,
  100% {
    transform: translateX(-26%) translateY(-2%);
  }
  50% {
    transform: translateX(26%) translateY(2%);
  }
}

@keyframes zuno-pet-star-think {
  0%,
  100% {
    opacity: 0.72;
    transform: rotate(0deg) scale(0.92);
  }
  50% {
    opacity: 1;
    transform: rotate(26deg) scale(1.16);
  }
}

@keyframes zuno-pet-typing-head {
  0%,
  100% {
    transform: scaleX(1) scaleY(1);
  }
  50% {
    transform: scaleX(1.014) scaleY(0.99);
  }
}

@keyframes zuno-pet-press {
  0%,
  100% {
    transform: scale(1);
  }
  36% {
    transform: scaleX(1.045) scaleY(0.965);
  }
  68% {
    transform: scaleX(0.988) scaleY(1.018);
  }
}

@keyframes zuno-pet-star-press {
  0%,
  100% {
    transform: scale(1) rotate(0deg);
  }
  42% {
    transform: scale(1.48) rotate(18deg);
  }
  72% {
    transform: scale(0.94) rotate(-5deg);
  }
}

@keyframes zuno-pet-eye-type {
  0%,
  100% {
    height: 34%;
  }
  46% {
    height: 24%;
  }
  58% {
    height: 38%;
  }
}

@keyframes zuno-pet-star-type {
  0%,
  100% {
    opacity: 0.72;
    transform: scale(0.92);
  }
  50% {
    opacity: 1;
    transform: scale(1.12);
  }
}

@keyframes zuno-pet-success-pop {
  0% {
    transform: scale(1);
  }
  42% {
    transform: scale(1.04);
  }
  100% {
    transform: scale(1.012);
  }
}

@keyframes zuno-pet-star-success {
  0%,
  100% {
    opacity: 0.86;
    transform: scale(1);
  }
  44% {
    opacity: 1;
    transform: scale(1.32) rotate(12deg);
  }
}

@keyframes zuno-pet-error-shake {
  0%,
  100% {
    transform: translateX(0) rotate(0deg);
  }
  20% {
    transform: translateX(-3%) rotate(-2deg);
  }
  42% {
    transform: translateX(3%) rotate(2deg);
  }
  62% {
    transform: translateX(-1.4%) rotate(-1deg);
  }
}

@keyframes zuno-pet-wake {
  0% {
    transform: scale(0.94);
    filter: saturate(0.96);
  }
  44% {
    transform: scale(1.055);
    filter: saturate(1.08);
  }
  100% {
    transform: scale(1);
    filter: saturate(1);
  }
}

@keyframes zuno-pet-star-wake {
  0% {
    opacity: 0.54;
    transform: scale(0.62) rotate(-10deg);
  }
  46% {
    opacity: 1;
    transform: scale(1.42) rotate(16deg);
  }
  100% {
    opacity: 0.9;
    transform: scale(1) rotate(0deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .zuno-code-pet,
  .pet-head,
  .pet-eye,
  .pet-star,
  .pet-orbit {
    animation: none !important;
    transition-duration: 1ms !important;
  }
}
</style>
