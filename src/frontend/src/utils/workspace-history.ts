const USER_INPUT_PATTERN = /(?:用户输入|user\s*input)\s*[:：]/gi
const WRAPPED_HISTORY_HINTS = ['<chat_history>', 'web_search', 'read_webpage', 'tool_code', '对话历史']

export const stripWorkspaceWrapper = (content: string) => {
  if (!content) return ''

  const cleaned = String(content).replace(/\r/g, '')
  const matches = Array.from(cleaned.matchAll(USER_INPUT_PATTERN))
  if (!matches.length) return cleaned.trim()

  const lastMatch = matches[matches.length - 1]
  const matchText = lastMatch[0] ?? ''
  const matchIndex = lastMatch.index ?? -1

  if (matchIndex < 0) return cleaned.trim()
  return cleaned.slice(matchIndex + matchText.length).trim()
}

export const looksLikeWrappedWorkspaceMessage = (content: string) => {
  if (!content) return false

  const cleaned = String(content).trim()
  const lowered = cleaned.replace(/\s+/g, '').toLowerCase()
  return (
    stripWorkspaceWrapper(cleaned) !== cleaned ||
    WRAPPED_HISTORY_HINTS.some((hint) => lowered.includes(hint))
  )
}

export const sanitizeWorkspaceContext = <T extends { query?: string; answer?: string }>(context: T) => {
  const nextContext = { ...context }
  const query = String(nextContext.query || '')
  if (query) {
    nextContext.query = stripWorkspaceWrapper(query)
  }
  return nextContext
}

export const sanitizeWorkspaceContexts = <T extends { query?: string; answer?: string }>(contexts: T[] = []) =>
  contexts
    .map((context) => sanitizeWorkspaceContext(context))
    .filter((context) => String(context.query || '').trim() || String(context.answer || '').trim())
