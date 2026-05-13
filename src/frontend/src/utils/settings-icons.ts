import agentIcon from '../assets/settings-icons/agent.svg'
import dashboardIcon from '../assets/settings-icons/dashboard.svg'
import knowledgeIcon from '../assets/settings-icons/knowledge.svg'
import mcpIcon from '../assets/settings-icons/mcp.svg'
import modelIcon from '../assets/settings-icons/model.svg'
import skillIcon from '../assets/settings-icons/skill.svg'
import toolIcon from '../assets/settings-icons/tool.svg'
import profileIcon from '../assets/user.svg'

export type SettingsSectionKey = 'agent' | 'model' | 'knowledge' | 'mcp' | 'tool' | 'skill' | 'dashboard' | 'profile'

export const settingsIconBySection: Record<SettingsSectionKey, string> = {
  agent: agentIcon,
  model: modelIcon,
  knowledge: knowledgeIcon,
  mcp: mcpIcon,
  tool: toolIcon,
  skill: skillIcon,
  dashboard: dashboardIcon,
  profile: profileIcon,
}

export const getSettingsIcon = (section: string) => {
  return settingsIconBySection[section as SettingsSectionKey] || agentIcon
}
