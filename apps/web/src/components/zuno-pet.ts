const zunoPetMoods = [
  'idle',
  'listening',
  'thinking',
  'typing',
  'success',
  'confused',
  'error',
  'wake',
] as const

const zunoPetSizes = [
  'hero',
  'beacon',
  'avatar',
  'tiny',
] as const

export type ZunoPetMood = typeof zunoPetMoods[number]
type ZunoPetSize = typeof zunoPetSizes[number]
