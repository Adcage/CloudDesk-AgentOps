<template>
  <div class="chat-view">
    <div class="workspace-header">
      <div class="workspace-title">客服协同工作台</div>
      <a-space>
        <a-tag color="blue">当前会话</a-tag>
        <a-tag color="processing">智能辅助已开启</a-tag>
      </a-space>
    </div>

    <div class="workspace-body">
      <div class="column-left">
        <a-card title="历史会话" size="small" :bordered="false">
          <a-empty v-if="sessions.length === 0" description="暂无历史会话" />
          <div v-else class="session-list">
            <button
              v-for="session in sessions"
              :key="session.id"
              type="button"
              class="session-item"
              :class="{ 'session-item-active': session.id === activeSessionId }"
              @click="applySession(session.id)"
            >
              <div class="session-title">{{ session.title }}</div>
              <div class="session-meta">{{ formatDateTime(session.updatedAt) }}</div>
            </button>
          </div>
        </a-card>

        <a-card title="客户画像" size="small" :bordered="false">
          <a-empty v-if="!customerContext" description="暂无识别到客户信息" />
          <a-descriptions v-else :column="1" size="small">
            <a-descriptions-item label="客户编号">{{ customerContext.customerId }}</a-descriptions-item>
            <a-descriptions-item label="客户名称">{{ customerContext.customerName }}</a-descriptions-item>
            <a-descriptions-item label="套餐">
              <a-tag :color="customerContext.plan === 'enterprise' ? 'purple' : 'blue'">
                {{ customerContext.plan || '-' }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="风险等级">
              <a-badge :color="riskBadgeColor(customerContext.riskLevel)" :text="customerContext.riskLevel || '-'" />
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="订单上下文" size="small" :bordered="false">
          <a-empty v-if="!orderContext" description="暂无识别到订单信息" />
          <a-descriptions v-else :column="1" size="small">
            <a-descriptions-item label="订单编号">{{ orderContext.orderId }}</a-descriptions-item>
            <a-descriptions-item label="金额">
              <span class="amount-text">¥{{ Number(orderContext.amount || 0).toFixed(2) }}</span>
            </a-descriptions-item>
            <a-descriptions-item label="状态">
              <a-tag :color="orderStatusColor(orderContext.status)">{{ orderContext.status || '-' }}</a-tag>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <a-card title="快捷动作" size="small" :bordered="false">
          <a-space direction="vertical" style="width: 100%;">
            <a-button block @click="handleQuickAction('生成工单摘要')">生成工单摘要</a-button>
            <a-button block @click="handleQuickAction('创建审批单')">创建审批单</a-button>
            <a-button block @click="handleQuickAction('转人工专家')">转人工专家</a-button>
            <a-button block @click="handleQuickAction('复制标准回复')">复制标准回复</a-button>
          </a-space>
        </a-card>
      </div>

      <div class="column-middle">
        <div class="chat-messages" ref="messagesRef">
          <div v-if="messages.length === 0" class="empty-hint">
            <a-empty description="请输入客户问题，系统将自动给出回复建议、知识引用与后续动作" />
          </div>
          <div
            v-for="(msg, idx) in messages"
            :key="`${idx}-${msg.role}`"
            class="message-row"
            :class="msg.role === 'user' ? 'message-right' : 'message-left'"
          >
            <div class="message-bubble" :class="msg.role === 'user' ? 'bubble-user' : 'bubble-agent'">
              <div v-if="msg.resultCard" class="result-card">
                <div class="result-card-title">{{ msg.resultCard.title }}</div>
                <div class="result-card-body">
                  <div v-for="row in msg.resultCard.rows" :key="row.label" class="result-card-row">
                    <span class="result-card-label">{{ row.label }}</span>
                    <span class="result-card-value">
                      <a-tag v-if="row.isTag" :color="row.tagColor || 'default'">{{ row.value }}</a-tag>
                      <span v-else>{{ row.value }}</span>
                    </span>
                  </div>
                </div>
                <div v-if="msg.resultCard.note" class="result-card-note">{{ msg.resultCard.note }}</div>
              </div>
              <div v-if="msg.role === 'agent' && msg.content" class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
              <div v-else-if="msg.role === 'agent' && !msg.resultCard" class="markdown-body" v-html="renderMarkdown(msg.content)"></div>
              <div v-else-if="msg.role === 'user'">{{ msg.content }}</div>
            </div>
          </div>
          <div v-if="isStreaming" class="message-row message-left">
            <div class="message-bubble bubble-agent">
              <div class="markdown-body" v-html="renderMarkdown(streamingContent || '')"></div>
              <span class="streaming-cursor">|</span>
            </div>
          </div>
          <div v-if="loading && !isStreaming" class="message-row message-left">
            <div class="message-bubble bubble-agent">
              <a-spin size="small" />
              <span class="thinking-text">正在思考...</span>
            </div>
          </div>
        </div>

        <div class="chat-input-area">
          <a-alert type="info" show-icon message="当前对话会自动提取引用知识、工具调用与审批建议" style="margin-bottom: 12px;" />
          <div class="chat-input">
            <a-textarea
              v-model:value="inputMessage"
              :auto-size="{ minRows: 2, maxRows: 4 }"
              placeholder="输入您的问题..."
              @pressEnter="handlePressEnter"
              :disabled="loading"
            />
            <a-button type="primary" :loading="loading" @click="sendMessageStream" style="margin-left: 12px;">
              发送
            </a-button>
          </div>
        </div>
      </div>

      <div class="column-right">
        <a-card title="辅助决策信息" size="small" :bordered="false">
          <a-collapse v-model:activeKey="activePanelKeys" size="small">
            <a-collapse-panel key="citations" header="引用知识">
              <a-empty v-if="citations.length === 0" description="当前对话暂无知识引用" />
              <div v-else class="citation-list">
                <div
                  v-for="(cite, idx) in citations"
                  :key="`cite-${idx}`"
                  class="citation-item"
                >
                  <div class="citation-header">
                    <span class="citation-source">{{ cite.source }}</span>
                    <a-button type="link" size="small" @click="openCitationDetail(cite)">查看详情</a-button>
                  </div>
                  <div v-if="cite.text" class="citation-preview">{{ cite.text.slice(0, 120) }}{{ cite.text.length > 120 ? '...' : '' }}</div>
                  <div v-else class="citation-preview citation-no-text">该引用仅返回了文档名称，暂无全文内容</div>
                </div>
              </div>
            </a-collapse-panel>

            <a-collapse-panel key="toolCalls" header="工具调用记录">
              <a-empty v-if="toolCalls.length === 0" description="当前对话暂无工具调用" />
              <a-timeline v-else>
                <a-timeline-item v-for="(tc, idx) in toolCalls" :key="`tool-${idx}`" :color="tc.status === 'success' ? 'green' : 'red'">
                  <div class="tool-call-item">
                    <div class="tool-name">{{ tc.toolName }}</div>
                    <div class="tool-summary" v-if="tc.input">{{ formatToolData(tc.input) }}</div>
                    <div class="tool-summary" v-else>本次调用未返回额外输入参数</div>
                  </div>
                </a-timeline-item>
              </a-timeline>
            </a-collapse-panel>

            <a-collapse-panel key="approval" header="审批状态">
              <a-empty v-if="!approvalInfo" description="当前对话暂无审批建议" />
              <a-descriptions v-else :column="1" size="small">
                <a-descriptions-item label="审批单号">{{ approvalInfo.approvalId }}</a-descriptions-item>
                <a-descriptions-item label="状态">
                  <a-tag :color="approvalInfo.status === 'pending' ? 'orange' : approvalInfo.status === 'approved' ? 'green' : 'red'">
                    {{ approvalInfo.status }}
                  </a-tag>
                </a-descriptions-item>
              </a-descriptions>
            </a-collapse-panel>

            <a-collapse-panel key="trace" header="Trace 链路">
              <a-empty v-if="!traceId" description="当前对话暂无 Trace 链路" />
              <router-link v-else :to="`/agentops?traceId=${traceId}`" target="_blank">
                {{ traceId }}
              </router-link>
            </a-collapse-panel>

            <a-collapse-panel key="debug" header="调试信息">
              <a-descriptions :column="1" size="small">
                <a-descriptions-item label="意图">
                  <a-tag v-if="intent" :color="intent === 'high_risk_action' ? 'red' : intent === 'refund_request' ? 'orange' : 'blue'">{{ intent }}</a-tag>
                  <span v-else>-</span>
                </a-descriptions-item>
                <a-descriptions-item label="风险等级">
                  <a-badge :color="riskBadgeColor(riskLevel)" :text="riskLevel || '-'" />
                </a-descriptions-item>
                <a-descriptions-item label="实体" v-if="entities">
                  <span v-for="(val, key) in entities" :key="key" style="margin-right: 8px;">
                    <a-tag v-if="val != null">{{ key }}={{ val }}</a-tag>
                  </span>
                </a-descriptions-item>
              </a-descriptions>
            </a-collapse-panel>

            <a-collapse-panel key="workflow" header="工作流步骤">
              <a-empty v-if="workflowSteps.length === 0" description="暂无工作流步骤记录" />
              <a-timeline v-else>
                <a-timeline-item v-for="(step, idx) in workflowSteps" :key="idx" :color="step.agent === 'approval_agent' ? 'red' : step.agent === 'supervisor_agent' ? 'blue' : 'green'">
                  <div class="workflow-step-item">
                    <div class="workflow-step-header">
                      <a-tag :color="step.agent === 'approval_agent' ? 'red' : step.agent === 'supervisor_agent' ? 'blue' : step.agent === 'check_guardrails' ? 'purple' : 'cyan'" size="small">{{ step.agent }}</a-tag>
                      <span class="workflow-step-action">{{ step.action }}</span>
                    </div>
                    <div v-if="step.detail && Object.keys(step.detail).length > 0" class="workflow-step-detail">
                      <span v-for="(val, key) in step.detail" :key="key" class="workflow-detail-item">
                        <span class="workflow-detail-key">{{ key }}:</span>
                        <span class="workflow-detail-val">{{ typeof val === 'object' ? JSON.stringify(val) : val }}</span>
                      </span>
                    </div>
                  </div>
                </a-timeline-item>
              </a-timeline>
            </a-collapse-panel>
          </a-collapse>
        </a-card>
      </div>
    </div>

    <a-modal
      v-model:open="citationModalVisible"
      title="引用知识详情"
      :footer="null"
      width="640px"
    >
      <div v-if="selectedCitation" class="citation-detail">
        <div class="citation-detail-source">来源：{{ selectedCitation.source }}</div>
        <div v-if="selectedCitation.text" class="citation-detail-text">{{ selectedCitation.text }}</div>
        <div v-else class="citation-detail-text citation-no-text">该引用仅返回了文档名称，暂无全文内容。如需查看完整文档，请前往知识库页面。</div>
        <a-button v-if="selectedCitation.text" type="primary" size="small" @click="copyCitationText">复制全文</a-button>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref } from 'vue'
import { message as antMessage } from 'ant-design-vue'
import { marked } from 'marked'
import { postChat } from '@/api/chat'
import { getOrder } from '@/api/orders'
import { getCustomer } from '@/api/customers'
import {
  clearChatSessions,
  loadActiveChatSessionId,
  loadChatSessions,
  saveActiveChatSessionId,
  saveChatSessions,
  type ApprovalInfo,
  type ChatMessage,
  type ChatSessionSnapshot,
  type Citation,
  type CustomerContext,
  type OrderContext,
  type ToolCall,
  type WorkflowStep,
} from './chatSessionStorage'

type ResultCard = { title: string; rows: Array<{ label: string; value: string; isTag?: boolean; tagColor?: string }>; note?: string }

type ExtendedChatMessage = ChatMessage & { resultCard?: ResultCard }

const messages = ref<ExtendedChatMessage[]>([])
const inputMessage = ref('')
const loading = ref(false)
const isStreaming = ref(false)
const streamingContent = ref('')
const conversationId = ref('')
const activeSessionId = ref('')
const sessions = ref<ChatSessionSnapshot[]>([])
const citations = ref<Citation[]>([])
const toolCalls = ref<ToolCall[]>([])
const approvalInfo = ref<ApprovalInfo | null>(null)
const traceId = ref('')
const customerContext = ref<CustomerContext | null>(null)
const orderContext = ref<OrderContext | null>(null)
const activePanelKeys = ref<string[]>(['citations', 'toolCalls', 'approval', 'trace', 'workflow'])
const messagesRef = ref<HTMLDivElement | null>(null)
const citationModalVisible = ref(false)
const selectedCitation = ref<Citation | null>(null)
const intent = ref('')
const riskLevel = ref('low')
const entities = ref<Record<string, any> | null>(null)
const workflowSteps = ref<WorkflowStep[]>([])
let streamAbortController: AbortController | null = null

const renderMarkdown = (text: string): string => marked.parse(text, { async: false }) as string

const riskBadgeColor = (riskLevel?: string) => {
  if (riskLevel === 'high') return 'red'
  if (riskLevel === 'medium') return 'orange'
  return 'green'
}

const orderStatusColor = (status?: string) => {
  if (status === 'processing') return 'orange'
  if (status === 'completed') return 'green'
  if (status === 'failed') return 'red'
  return 'default'
}

const formatToolData = (data: string): string => {
  try {
    const obj = JSON.parse(data)
    return JSON.stringify(obj, null, 2).slice(0, 200)
  } catch {
    return data?.slice(0, 200) || ''
  }
}

const formatDateTime = (value: string) => {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN')
}

const scrollToBottom = async () => {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

const resetContextState = () => {
  citations.value = []
  toolCalls.value = []
  approvalInfo.value = null
  traceId.value = ''
  customerContext.value = null
  orderContext.value = null
  intent.value = ''
  riskLevel.value = 'low'
  entities.value = null
  workflowSteps.value = []
}

const extractPayload = (res: any) => {
  const data = res.data?.data ?? res.data
  if (data && typeof data === 'object' && !Array.isArray(data) && data.code !== undefined) return data.data
  return data
}

const normalizeCitations = (raw: any): Citation[] => {
  if (!Array.isArray(raw)) return []
  return raw
    .map((item) => {
      if (typeof item === 'string') {
        return { source: item, text: '' }
      }
      if (item && typeof item === 'object') {
        const source = item.source || item.document || item.title || '引用资料'
        const text = item.text || item.content || item.snippet || ''
        return { source, text }
      }
      return null
    })
    .filter(Boolean) as Citation[]
}

const normalizeToolCalls = (raw: any): ToolCall[] => {
  if (!Array.isArray(raw)) return []
  return raw
    .map((item) => {
      if (typeof item === 'string') return { toolName: item, input: '', status: 'success' }
      if (item && typeof item === 'object') {
        return {
          toolName: item.toolName || item.tool_name || item.name || item.tool || '工具调用',
          input: typeof item.input === 'string' ? item.input : JSON.stringify(item.input || {}),
          output: typeof item.output === 'string' ? item.output : item.output ? JSON.stringify(item.output) : undefined,
          status: item.status || 'success',
        }
      }
      return null
    })
    .filter(Boolean) as ToolCall[]
}

const buildResultCard = (data: any): ResultCard | undefined => {
  const order = data.orderContext || data.order_context
  const customer = data.customerContext || data.customer_context
  if (!order && !customer) return undefined

  const rows: ResultCard['rows'] = []
  if (order) {
    rows.push({ label: '订单编号', value: order.orderId || order.order_id || '-' })
    rows.push({ label: '金额', value: `¥${Number(order.amount || 0).toFixed(2)}` })
    rows.push({
      label: '状态',
      value: order.status || '-',
      isTag: true,
      tagColor: orderStatusColor(order.status),
    })
  }
  if (customer) {
    const name = customer.customerName || customer.customer_name || customer.name || '-'
    rows.push({ label: '客户', value: name })
    const plan = customer.plan || '-'
    if (plan !== '-') rows.push({ label: '套餐', value: plan, isTag: true, tagColor: plan === 'enterprise' ? 'purple' : 'blue' })
    const risk = customer.riskLevel || customer.risk_level || '-'
    if (risk !== '-') rows.push({ label: '风险等级', value: risk, isTag: true, tagColor: riskBadgeColor(risk) })
  }
  const approval = data.approvalRequired || data.approval_required
  const approvalId = data.approvalId || data.approval_id
  const title = approval && approvalId ? '审批结果' : order ? '订单查询结果' : '客户信息'

  return {
    title,
    rows,
    note: approval && approvalId ? '该操作已触发审批流程，请关注审批状态。' : undefined,
  }
}

const buildSessionTitle = (list: ChatMessage[]) => {
  const firstUserMessage = list.find((item) => item.role === 'user')?.content || '新会话'
  return firstUserMessage.length > 24 ? `${firstUserMessage.slice(0, 24)}...` : firstUserMessage
}

const upsertSession = (overrideId?: string) => {
  const sessionId = overrideId || conversationId.value || activeSessionId.value
  if (!sessionId) return
  const snapshot: ChatSessionSnapshot = {
    id: sessionId,
    title: buildSessionTitle(messages.value),
    updatedAt: new Date().toISOString(),
    messages: messages.value,
    customerContext: customerContext.value,
    orderContext: orderContext.value,
    citations: citations.value,
    toolCalls: toolCalls.value,
    approvalInfo: approvalInfo.value,
    traceId: traceId.value,
    intent: intent.value,
    riskLevel: riskLevel.value,
    entities: entities.value,
    workflowSteps: workflowSteps.value,
  }
  const next = sessions.value.filter((item) => item.id !== sessionId)
  next.unshift(snapshot)
  sessions.value = next
  saveChatSessions(sessions.value)
  activeSessionId.value = sessionId
  saveActiveChatSessionId(sessionId)
}

const applySession = (sessionId: string) => {
  const session = sessions.value.find((item) => item.id === sessionId)
  if (!session) return
  activeSessionId.value = session.id
  conversationId.value = session.id
  messages.value = session.messages
  customerContext.value = session.customerContext
  orderContext.value = session.orderContext
  citations.value = session.citations
  toolCalls.value = session.toolCalls
  approvalInfo.value = session.approvalInfo
  traceId.value = session.traceId
  intent.value = session.intent || ''
  riskLevel.value = session.riskLevel || 'low'
  entities.value = session.entities || null
  workflowSteps.value = session.workflowSteps || []
  saveActiveChatSessionId(session.id)
  scrollToBottom()
}

const ensureLocalSession = () => {
  if (activeSessionId.value) return activeSessionId.value
  const localId = `local-${Date.now()}`
  activeSessionId.value = localId
  conversationId.value = localId
  saveActiveChatSessionId(localId)
  return localId
}

const openCitationDetail = (citation: Citation) => {
  selectedCitation.value = citation
  citationModalVisible.value = true
}

const copyCitationText = async () => {
  if (!selectedCitation.value) return
  try {
    await navigator.clipboard.writeText(selectedCitation.value.text)
    antMessage.success('已复制引用全文')
  } catch {
    antMessage.error('复制失败')
  }
}

const fetchCustomerContext = async (customerId: string) => {
  try {
    const res = await getCustomer(customerId)
    const data = extractPayload(res)
    if (data) {
      customerContext.value = {
        customerId: data.customerId || customerId,
        customerName: data.name || '未知客户',
        plan: data.plan || '',
        riskLevel: data.riskLevel || 'low',
      }
    }
  } catch {}
}

const fetchOrderContext = async (orderId: string) => {
  try {
    const res = await getOrder(orderId)
    const data = extractPayload(res)
    if (data) {
      orderContext.value = {
        orderId: data.orderId || orderId,
        amount: Number(data.amount || 0),
        status: data.status || '',
      }
      if (data.customerId) {
        await fetchCustomerContext(data.customerId)
      }
    }
  } catch {}
}

const applyStructuredContext = async (data: any) => {
  const customer = data.customerContext || data.customer_context
  const order = data.orderContext || data.order_context

  if (customer && typeof customer === 'object') {
    customerContext.value = {
      customerId: customer.customerId || customer.customer_id || '',
      customerName: customer.customerName || customer.customer_name || '',
      plan: customer.plan || '',
      riskLevel: customer.riskLevel || customer.risk_level || 'low',
    }
    if (customerContext.value.customerId && !customerContext.value.customerName) {
      await fetchCustomerContext(customerContext.value.customerId)
    }
  }

  if (order && typeof order === 'object') {
    orderContext.value = {
      orderId: order.orderId || order.order_id || '',
      amount: Number(order.amount || 0),
      status: order.status || '',
    }
  }

  if (orderContext.value && !customerContext.value && customer?.customerId) {
    await fetchCustomerContext(customer.customerId)
  }
}

const hydrateContextFromText = async (text: string) => {
  const orderMatch = text.match(/O\d+/i)
  const customerMatch = text.match(/C\d+/i)
  if (orderMatch) {
    await fetchOrderContext(orderMatch[0].toUpperCase())
  }
  if (!customerContext.value && customerMatch) {
    await fetchCustomerContext(customerMatch[0].toUpperCase())
  }
}

const handleQuickAction = (action: string) => {
  antMessage.info(`${action} 功能待接入业务动作`)
}

const applyStreamedReply = (data: any) => {
  const citeDetails = data.citationDetails || data.citation_details
  citations.value = citeDetails && Array.isArray(citeDetails) && citeDetails.length > 0
    ? normalizeCitations(citeDetails)
    : normalizeCitations(data.citations)
  toolCalls.value = normalizeToolCalls(data.toolCallResults || data.tool_call_results || data.toolCalls || data.tool_calls)
  approvalInfo.value = data.approvalRequired || data.approval_required
    ? { approvalId: data.approvalId || data.approval_id || '', status: 'pending' }
    : null
  traceId.value = data.traceId || data.trace_id || ''
  intent.value = data.intent || ''
  riskLevel.value = data.riskLevel || data.risk_level || 'low'
  entities.value = data.entities || null
  workflowSteps.value = Array.isArray(data.workflowSteps || data.workflow_steps) ? (data.workflowSteps || data.workflow_steps) : []
  applyStructuredContext(data)
  hydrateContextFromText(data.answer || '')
}

const sendMessageStream = async () => {
  const msg = inputMessage.value.trim()
  if (!msg || loading.value) return
  resetContextState()
  const localId = ensureLocalSession()
  inputMessage.value = ''
  messages.value.push({ role: 'user', content: msg })
  upsertSession(localId)
  loading.value = true
  isStreaming.value = false
  streamingContent.value = ''
  scrollToBottom()

  try {
    await tryStreamChat(msg, localId)
  } catch (streamErr: any) {
    console.warn('SSE 流式失败，回退到普通请求:', streamErr.message)
    try {
      await fallbackNonStreamChat(msg, localId)
    } catch (fallbackErr: any) {
      antMessage.error(`请求失败: ${fallbackErr.message || streamErr.message || '未知错误'}`)
    }
  } finally {
    loading.value = false
    isStreaming.value = false
    streamingContent.value = ''
    scrollToBottom()
  }
}

const tryStreamChat = async (msg: string, localId: string) => {
  const baseURL = import.meta.env.VITE_API_BASE_URL || ''
  const url = `${baseURL}/chat/stream`
  streamAbortController = new AbortController()

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      conversationId: conversationId.value.startsWith('local-') ? undefined : conversationId.value,
      message: msg,
    }),
    signal: streamAbortController.signal,
  })

  if (!response.ok) throw new Error(`服务器返回 ${response.status}`)
  const reader = response.body?.getReader()
  if (!reader) throw new Error('不支持流式响应')

  const decoder = new TextDecoder()
  let buffer = ''
  isStreaming.value = true
  let resolvedConversationId = ''
  let finalData: any = null

  const processEvents = (text: string) => {
    const lines = text.split('\n')
    for (const line of lines) {
      if (line.startsWith('event:')) continue
      if (line.startsWith('data:')) {
        const payload = line.slice(5).trimStart()
        try {
          const eventData = JSON.parse(payload)
          if (eventData.type === 'chunk') {
            streamingContent.value += eventData.content || ''
          } else if (eventData.type === 'done') {
            finalData = eventData
            resolvedConversationId = eventData.conversationId || eventData.conversation_id || ''
            if (resolvedConversationId && resolvedConversationId !== conversationId.value) {
              conversationId.value = resolvedConversationId
              activeSessionId.value = resolvedConversationId
            }
          }
        } catch {
          streamingContent.value += payload.replace(/^"|"$/g, '')
        }
      }
    }
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const parts = buffer.split('\n\n')
    buffer = parts.pop() || ''
    for (const part of parts) processEvents(part)
    scrollToBottom()
  }
  if (buffer.trim()) processEvents(buffer)

  const displayContent = streamingContent.value
  if (!displayContent && !finalData) throw new Error('未获取到有效回复')

  const resultCard = finalData ? buildResultCard(finalData) : undefined
  messages.value.push({ role: 'agent', content: displayContent || finalData?.answer || '', resultCard })
  if (finalData) applyStreamedReply(finalData)
  if (localId.startsWith('local-') && localId !== resolvedConversationId) {
    sessions.value = sessions.value.filter((item) => item.id !== localId)
  }
  upsertSession(resolvedConversationId || undefined)
}

const fallbackNonStreamChat = async (msg: string, localId: string) => {
  const res = await postChat({
    conversationId: conversationId.value.startsWith('local-') ? undefined : conversationId.value,
    message: msg,
  })
  const data = extractPayload(res)
  if (!data) throw new Error('未获取到有效回复')

  const resolvedConversationId = data.conversationId || data.conversation_id || conversationId.value || localId
  conversationId.value = resolvedConversationId
  activeSessionId.value = resolvedConversationId

  const resultCard = buildResultCard(data)
  messages.value.push({ role: 'agent', content: data.answer || '', resultCard })

  applyStreamedReply(data)
  await hydrateContextFromText(`${msg}\n${data.answer || ''}`)

  if (localId.startsWith('local-') && localId !== resolvedConversationId) {
    sessions.value = sessions.value.filter((item) => item.id !== localId)
  }
  upsertSession(resolvedConversationId)
}

const handlePressEnter = (e: KeyboardEvent) => {
  if (!e.shiftKey) {
    e.preventDefault()
    sendMessageStream()
  }
}

onMounted(() => {
  sessions.value = loadChatSessions()
  const activeId = loadActiveChatSessionId()
  if (activeId && sessions.value.some((item) => item.id === activeId)) {
    applySession(activeId)
  } else if (sessions.value.length > 0) {
    applySession(sessions.value[0].id)
  } else {
    resetContextState()
  }
})

onUnmounted(() => {
  streamAbortController?.abort()
})
</script>

<style scoped>
.chat-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: #f0f2f5;
}

.workspace-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 24px;
  background: #fff;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.workspace-title {
  font-size: 18px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
}

.workspace-body {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr) 360px;
  gap: 16px;
  flex: 1;
  min-height: 0;
  padding: 16px 24px;
  overflow: hidden;
}

.column-left,
.column-right {
  overflow-y: auto;
}

.column-left {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.column-middle {
  display: flex;
  flex-direction: column;
  min-height: 0;
  background: #fff;
  border-radius: 6px;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px 20px;
  background: #fafafa;
}

.empty-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.message-row {
  display: flex;
  margin-bottom: 16px;
}

.message-left {
  justify-content: flex-start;
}

.message-right {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 70%;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
}

.bubble-user {
  background: #1f5fae;
  color: #fff;
  border-bottom-right-radius: 2px;
}

.bubble-agent {
  background: #fff;
  color: rgba(0, 0, 0, 0.85);
  border: 1px solid #f0f0f0;
  border-bottom-left-radius: 2px;
}

.thinking-text {
  margin-left: 8px;
  color: rgba(0, 0, 0, 0.45);
}

.streaming-cursor {
  display: inline-block;
  animation: blink 1s step-end infinite;
  color: #1f5fae;
  font-weight: 700;
}

@keyframes blink {
  50% { opacity: 0; }
}

.result-card {
  margin-bottom: 12px;
  padding: 12px 14px;
  background: #f6ffed;
  border: 1px solid #b7eb8f;
  border-radius: 8px;
}

.result-card-title {
  font-size: 14px;
  font-weight: 600;
  color: #389e0d;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1px dashed #b7eb8f;
}

.result-card-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result-card-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.result-card-label {
  color: rgba(0, 0, 0, 0.45);
}

.result-card-value {
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

.result-card-note {
  margin-top: 8px;
  padding-top: 6px;
  border-top: 1px dashed #b7eb8f;
  font-size: 12px;
  color: #faad14;
}

.chat-input-area {
  padding: 12px 20px;
  border-top: 1px solid #f0f0f0;
  background: #fff;
  flex-shrink: 0;
}

.chat-input {
  display: flex;
  align-items: flex-end;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.session-item {
  width: 100%;
  padding: 10px 12px;
  text-align: left;
  border: 1px solid #f0f0f0;
  border-radius: 8px;
  background: #fff;
  cursor: pointer;
}

.session-item-active {
  border-color: #1f5fae;
  background: #f0f6ff;
}

.session-title {
  font-size: 14px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

.session-meta {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.amount-text {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
}

.citation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.citation-item {
  padding: 8px 10px;
  background: #fafafa;
  border-radius: 6px;
}

.citation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.citation-source {
  font-size: 13px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

.citation-preview {
  margin-top: 4px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  line-height: 1.5;
}

.citation-detail-source {
  margin-bottom: 12px;
  font-size: 14px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.65);
}

.citation-detail-text {
  margin-bottom: 16px;
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
  font-size: 13px;
  line-height: 1.8;
  white-space: pre-wrap;
  color: rgba(0, 0, 0, 0.85);
  max-height: 400px;
  overflow-y: auto;
}

.citation-no-text {
  font-style: italic;
  color: rgba(0, 0, 0, 0.3);
}

.tool-call-item {
  font-size: 13px;
}

.tool-name {
  font-weight: 600;
  color: #1f5fae;
}

.tool-summary {
  color: rgba(0, 0, 0, 0.45);
  margin-top: 4px;
  white-space: pre-wrap;
  font-size: 12px;
}

.workflow-step-item {
  font-size: 13px;
}

.workflow-step-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
}

.workflow-step-action {
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

.workflow-step-detail {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 12px;
  margin-top: 4px;
}

.workflow-detail-item {
  font-size: 12px;
}

.workflow-detail-key {
  color: rgba(0, 0, 0, 0.45);
}

.workflow-detail-val {
  color: rgba(0, 0, 0, 0.65);
  margin-left: 2px;
}

.markdown-body :deep(p) {
  margin-bottom: 8px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 20px;
}

.markdown-body :deep(code) {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 13px;
}

.markdown-body :deep(pre) {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 6px;
  overflow-x: auto;
}

.markdown-body :deep(pre code) {
  background: none;
  padding: 0;
}

@media (max-width: 1280px) {
  .workspace-body {
    grid-template-columns: 1fr;
  }

  .column-middle {
    min-height: calc(100vh - 320px);
  }
}
</style>
