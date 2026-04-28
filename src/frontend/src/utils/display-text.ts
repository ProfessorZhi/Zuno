const QUESTION_CLUSTER_RE = /\?{5,}/
const REPLACEMENT_CHAR_RE = /\ufffd/

export const looksCorruptedText = (value: string | null | undefined) => {
  if (!value) return false
  const text = String(value).trim()
  if (!text) return false
  if (REPLACEMENT_CHAR_RE.test(text)) return true

  const questionCount = (text.match(/\?/g) || []).length
  return QUESTION_CLUSTER_RE.test(text) && questionCount / Math.max(text.length, 1) > 0.3
}

export const safeDisplayText = (
  value: string | null | undefined,
  fallback = '',
) => {
  const text = String(value || '').trim()
  if (!text || looksCorruptedText(text)) return fallback
  return text
}
