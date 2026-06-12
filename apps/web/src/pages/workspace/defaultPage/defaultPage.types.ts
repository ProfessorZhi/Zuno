import type { Component } from 'vue'
import type { WorkspaceAttachment } from '../../../apis/workspace'
import type { WorkspaceMode } from '../../../utils/workspace-defaults'

export type MessageMotion = 'sending' | 'thinking' | 'streaming' | 'complete' | 'error'

interface ChatAttachment extends WorkspaceAttachment {
  id?: string
  preview_url?: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  attachments?: ChatAttachment[]
  uiOrder?: number
  motion?: MessageMotion
}

export interface SettingsThreadItem {
  id: string
  order: number
  section: string
  label: string
  command: string
  commandTurns: SettingsCommandTurn[]
  icon: string
  component: Component
  routeName: string
  routeKey: string
  routeSnapshot: SettingsRouteSnapshot | null
  detail: boolean
  history: SettingsRouteSnapshot[]
  commandVisible: boolean
  assistantVisible: boolean
  ready: boolean
  switching: boolean
}

interface SettingsCommandTurn {
  id: string
  command: string
}

export interface SettingsRouteSnapshot {
  name: string
  fullPath: string
  params: Record<string, any>
  query: Record<string, any>
}

export type ConversationBlock =
  | { type: 'message'; order: number; message: ChatMessage; index: number }
  | { type: 'settings'; order: number; thread: SettingsThreadItem }

interface RetrievalRoundTrace {
  round: number
  mode: string
  trigger?: string
  qualityReason?: string
  query?: string
}

export interface RetrievalTraceSummary {
  firstMode: string
  finalMode: string
  roundCount: number
  fallbackReason: string
  rewrittenQueryUsed: boolean
  rounds: RetrievalRoundTrace[]
}

export interface TraceRecord {
  id: string
  title: string
  detail: string
  at: string
  phase?: string
  status?: string
  accent?: 'default' | 'tool' | 'graph' | 'retrieval' | 'answer' | 'error'
  retrieval?: RetrievalTraceSummary | null
}

export interface PendingAttachment extends WorkspaceAttachment {
  id: string
  preview_url?: string
}

export interface ProgressStep {
  key: string
  label: string
  done: boolean
  active: boolean
  accent?: 'default' | 'tool' | 'graph' | 'retrieval' | 'answer' | 'error'
}

export interface NewConversationDetail {
  mode?: WorkspaceMode
  agentId?: string
  agentName?: string
}

export interface AgentOption {
  id: string
  name: string
  description: string
  avatar: string
}

export type MascotPresenceState = 'idle' | 'listening' | 'thinking' | 'typing' | 'success' | 'confused' | 'error' | 'hover' | 'click'

export type SlashSuggestion = {
  key: string
  label: string
  detail: string
  insertValue: string
}

export type ToolCreationKind = 'general' | 'api' | 'cli'
