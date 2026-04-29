import { computed, onBeforeUnmount, ref, watch, type CSSProperties } from "vue"

interface ResizablePanelOptions {
  storageKey: string
  cssVariable: string
  defaultWidth: number
  minWidth: number
  maxWidth: number
  keyboardStep?: number
  minAvailableContentWidth?: number
}

const canUseStorage = () => typeof window !== "undefined" && !!window.localStorage

const clamp = (value: number, min: number, max: number) => {
  return Math.min(Math.max(value, min), max)
}

const readStoredWidth = (storageKey: string) => {
  if (!canUseStorage()) return undefined

  const storedValue = window.localStorage.getItem(storageKey)
  if (storedValue === null) return undefined

  const value = Number(storedValue)
  return Number.isFinite(value) ? value : undefined
}

export const useResizablePanel = (options: ResizablePanelOptions) => {
  const keyboardStep = options.keyboardStep ?? 8
  const getEffectiveMaxWidth = () => {
    if (typeof window === "undefined" || !options.minAvailableContentWidth) {
      return options.maxWidth
    }

    const availableWidth = window.innerWidth - options.minAvailableContentWidth
    return Math.max(options.minWidth, Math.min(options.maxWidth, availableWidth))
  }

  const getClampedWidth = (value: number) => {
    return clamp(value, options.minWidth, getEffectiveMaxWidth())
  }

  const width = ref(
    getClampedWidth(
      readStoredWidth(options.storageKey) ?? options.defaultWidth,
    )
  )

  let startX = 0
  let startWidth = 0

  const panelStyle = computed<CSSProperties>(() => ({
    [options.cssVariable]: `${width.value}px`,
  } as CSSProperties))

  const setWidth = (nextWidth: number) => {
    width.value = getClampedWidth(nextWidth)
  }

  const handleWindowResize = () => {
    setWidth(width.value)
  }

  const stopResize = () => {
    document.body.classList.remove("zuno-is-resizing")
    window.removeEventListener("pointermove", handlePointerMove)
    window.removeEventListener("pointerup", stopResize)
  }

  const handlePointerMove = (event: PointerEvent) => {
    setWidth(startWidth + event.clientX - startX)
  }

  const startResize = (event: PointerEvent) => {
    if (event.button !== 0) return

    event.preventDefault()
    startX = event.clientX
    startWidth = width.value
    document.body.classList.add("zuno-is-resizing")
    window.addEventListener("pointermove", handlePointerMove)
    window.addEventListener("pointerup", stopResize)
  }

  const handleSeparatorKeydown = (event: KeyboardEvent) => {
    if (event.key === "ArrowLeft") {
      event.preventDefault()
      setWidth(width.value - keyboardStep)
      return
    }

    if (event.key === "ArrowRight") {
      event.preventDefault()
      setWidth(width.value + keyboardStep)
      return
    }

    if (event.key === "Home") {
      event.preventDefault()
      setWidth(options.minWidth)
      return
    }

    if (event.key === "End") {
      event.preventDefault()
      setWidth(options.maxWidth)
    }
  }

  watch(
    width,
    (nextWidth) => {
      const clampedWidth = getClampedWidth(nextWidth)
      if (clampedWidth !== nextWidth) {
        width.value = clampedWidth
        return
      }

      if (canUseStorage()) {
        window.localStorage.setItem(options.storageKey, String(nextWidth))
      }
    },
    { immediate: true }
  )

  if (typeof window !== "undefined") {
    window.addEventListener("resize", handleWindowResize)
  }

  onBeforeUnmount(() => {
    stopResize()
    if (typeof window !== "undefined") {
      window.removeEventListener("resize", handleWindowResize)
    }
  })

  return {
    width,
    panelStyle,
    startResize,
    handleSeparatorKeydown,
  }
}
