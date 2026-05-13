const USER_AVATAR_ASSET_VERSION = '20260511-clean3'

export const withUserAvatarVersion = (value: string) => {
  if (value.startsWith('/avatars/user/zuno-user-') && !value.includes('?')) {
    return `${value}?v=${USER_AVATAR_ASSET_VERSION}`
  }
  return value
}

export const USER_AVATAR_PRESETS = Array.from(
  { length: 20 },
  (_, index) => withUserAvatarVersion(`/avatars/user/zuno-user-${String(index + 1).padStart(2, '0')}.png`)
)

export const DEFAULT_USER_AVATAR = USER_AVATAR_PRESETS[0]

export const isLegacyRemoteUserAvatar = (value: string) => (
  value.includes('agentchat.oss-cn-beijing.aliyuncs.com/icons/user/')
  || value.includes('/agentchat/icons/user/')
  || value.includes('/icons/user/')
)
