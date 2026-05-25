export type ChatMessage = {
  role: 'user' | 'agent'
  content: string
}

export type Citation = {
  source: string
  text: string
}

export type ToolCall = {
  toolName: string
  input: string
  output?: string
  status: string
}

export type ApprovalInfo = {
  approvalId: string
  status: string
}

export type CustomerContext = {
  customerId: string
  customerName: string
  plan: string
  riskLevel: string
}

export type OrderContext = {
  orderId: string
  amount: number
  status: string
}

export type WorkflowStep = {
  agent: string
  action: string
  detail?: Record<string, any>
}

export type ChatSessionSnapshot = {
  id: string
  title: string
  updatedAt: string
  messages: ChatMessage[]
  customerContext: CustomerContext | null
  orderContext: OrderContext | null
  citations: Citation[]
  toolCalls: ToolCall[]
  approvalInfo: ApprovalInfo | null
  traceId: string
  intent: string
  riskLevel: string
  entities: Record<string, any> | null
  workflowSteps: WorkflowStep[]
}

const SESSIONS_KEY = 'chat_workspace_sessions'
const ACTIVE_SESSION_KEY = 'chat_workspace_active_session'

export function loadChatSessions(): ChatSessionSnapshot[] {
  try {
    const raw = sessionStorage.getItem(SESSIONS_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function saveChatSessions(sessions: ChatSessionSnapshot[]): void {
  try {
    sessionStorage.setItem(SESSIONS_KEY, JSON.stringify(sessions))
  } catch {}
}

export function loadActiveChatSessionId(): string {
  try {
    return sessionStorage.getItem(ACTIVE_SESSION_KEY) || ''
  } catch {
    return ''
  }
}

export function saveActiveChatSessionId(id: string): void {
  try {
    sessionStorage.setItem(ACTIVE_SESSION_KEY, id)
  } catch {}
}

export function clearChatSessions(): void {
  try {
    sessionStorage.removeItem(SESSIONS_KEY)
    sessionStorage.removeItem(ACTIVE_SESSION_KEY)
  } catch {}
}
