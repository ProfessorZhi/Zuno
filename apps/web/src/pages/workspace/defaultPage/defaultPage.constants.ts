export const ALWAYS_WEB_SEARCH = true
export const MAX_ATTACHMENTS = 5
export const MAX_ATTACHMENT_SIZE = 20 * 1024 * 1024
export const CHAT_IMAGE_EXTENSIONS = new Set(['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'])
export const AGENT_DOCUMENT_EXTENSIONS = new Set(['pdf', 'doc', 'docx', 'ppt', 'pptx', 'txt', 'md', 'csv', 'xls', 'xlsx'])

export const fallbackDescription = '暂无描述'
export const fallbackKnowledgeDescription = (count?: number) => `共 ${count || 0} 个文件`

export const modes = [
  { id: 'normal' as const, label: '聊天模式', description: '适合轻量对话、图片理解与快速问答。' },
  { id: 'agent' as const, label: 'Agent 模式', description: '可调用工具、分析附件，并执行更完整的任务流程。' },
]

export const settingsLabels: Record<string, string> = {
  agent: '智能体',
  model: '模型',
  knowledge: '知识库',
  mcp: 'MCP',
  tool: '工具',
  skill: 'Skill',
  dashboard: '数据看板',
  profile: '个人资料',
  conversations: '对话记录',
}

export const settingsCommandSections = [
  { section: 'agent', names: ['智能体', 'agent', 'agent管理', '智能体管理'] },
  { section: 'model', names: ['模型', 'model', '模型管理', '模型资源池'] },
  { section: 'knowledge', names: ['知识库', 'knowledge', '知识库管理'] },
  { section: 'mcp', names: ['mcp', 'mcp管理', 'mcp服务', 'mcp服务管理'] },
  { section: 'tool', names: ['工具', 'tool', '工具管理'] },
  { section: 'skill', names: ['skill', 'skill管理'] },
  { section: 'dashboard', names: ['数据看板', '看板', 'dashboard', '数据'] },
]

export const settingsRouteBySection: Record<string, string> = {
  agent: 'workspaceSettingsAgent',
  model: 'workspaceSettingsModel',
  knowledge: 'workspaceSettingsKnowledge',
  mcp: 'workspaceSettingsMcp',
  tool: 'workspaceSettingsTool',
  skill: 'workspaceSettingsSkill',
  dashboard: 'workspaceSettingsDashboard',
}
