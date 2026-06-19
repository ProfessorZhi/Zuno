const USER_AVATAR_ASSET_VERSION = '20260511-clean3'

const resolveDesktopAvatarPath = (value: string) => {
  if (typeof window === 'undefined') return value
  if (window.location.protocol !== 'file:') return value
  if (!value.startsWith('/avatars/')) return value
  return `.${value}`
}

export const withUserAvatarVersion = (value: string) => {
  if (value.startsWith('/avatars/user/zuno-user-') && !value.includes('?')) {
    const withVersion = `${value}?v=${USER_AVATAR_ASSET_VERSION}`
    return resolveDesktopAvatarPath(withVersion)
  }
  return resolveDesktopAvatarPath(value)
}

export const USER_AVATAR_PRESETS = Array.from(
  { length: 20 },
  (_, index) => withUserAvatarVersion(`/avatars/user/zuno-user-${String(index + 1).padStart(2, '0')}.png`)
)

export const DEFAULT_USER_AVATAR = USER_AVATAR_PRESETS[0]

export const isLegacyRemoteUserAvatar = (value: string) => (
  value.includes('zuno.oss-cn-beijing.aliyuncs.com/icons/user/')
  || value.includes('/zuno/icons/user/')
  || value.includes('/icons/user/')
)
