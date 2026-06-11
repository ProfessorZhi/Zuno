export type SettingsUiMode = 'traditional' | 'chat-flow'

const SETTINGS_UI_MODE_KEY = 'zuno.workspace.settingsUiMode'

export const loadSettingsUiMode = (): SettingsUiMode => {
  if (typeof window === 'undefined') return 'traditional'

  try {
    const raw = window.localStorage.getItem(SETTINGS_UI_MODE_KEY)
    return raw === 'chat-flow' ? 'chat-flow' : 'traditional'
  } catch {
    return 'traditional'
  }
}

export const saveSettingsUiMode = (mode: SettingsUiMode) => {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(SETTINGS_UI_MODE_KEY, mode === 'chat-flow' ? 'chat-flow' : 'traditional')
}
