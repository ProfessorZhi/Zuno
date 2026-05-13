export const zunoPetMoods = [
  'idle',
  'listening',
  'thinking',
  'typing',
  'success',
  'confused',
  'error',
  'wake',
] as const

export const zunoPetSizes = [
  'hero',
  'beacon',
  'avatar',
  'tiny',
] as const

export type ZunoPetMood = typeof zunoPetMoods[number]
export type ZunoPetSize = typeof zunoPetSizes[number]
