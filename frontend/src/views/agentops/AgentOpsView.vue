<template>
  <div class="agentops-view">
    <a-page-header title="Agent 运行保障台" sub-title="监控链路健康、异常 Trace 与工具调用质量" />

    <a-tabs v-model:activeKey="activeTab" @change="handleTabChange">
      <a-tab-pane key="traces" tab="Trace 链路" />
      <a-tab-pane key="eval" tab="评估中心" />
      <a-tab-pane key="costs" tab="成本分析" />
    </a-tabs>

    <a-row :gutter="[16, 16]" class="ops-stats">
      <a-col :xs="24" :sm="6">
        <a-card :bordered="false">
          <a-statistic title="总请求数" :value="stats.total" :value-style="{ color: '#1f5fae' }">
            <template #prefix><api-outlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="6">
        <a-card :bordered="false">
          <a-statistic title="平均延迟" :value="stats.avgLatency" suffix="ms" :value-style="{ color: '#52c41a' }">
            <template #prefix><clock-circle-outlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="6">
        <a-card :bordered="false">
          <a-statistic title="工具成功率" :value="stats.toolRate" suffix="%" :value-style="{ color: '#faad14' }">
            <template #prefix><check-circle-outlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="6">
        <a-card :bordered="false">
          <a-statistic title="异常 Trace 数" :value="stats.anomalyCount" :value-style="{ color: '#ff4d4f' }">
            <template #prefix><warning-outlined /></template>
          </a-statistic>
        </a-card>
      </a-col>
    </a-row>

    <div class="filter-bar">
      <a-space :size="12" wrap>
        <a-select v-model:value="filters.anomalyType" placeholder="异常类型筛选" allow-clear style="width: 180px">
          <a-select-option value="slow">高延迟</a-select-option>
          <a-select-option value="tool_failed">工具失败</a-select-option>
          <a-select-option value="no_citation">无知识引用</a-select-option>
        </a-select>
        <a-input-search v-model:value="traceSearchId" placeholder="搜索 Trace ID" style="width: 280px" @search="handleSearchTrace" allow-clear />
        <a-button @click="resetFilters">重置</a-button>
      </a-space>
    </div>

    <a-card title="Trace 列表" :bordered="false">
      <a-table
        :columns="columns"
        :data-source="filteredTraces"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="traceId"
        :scroll="{ x: 1200 }"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'latencyMs'">
            {{ record.latencyMs != null ? `${record.latencyMs}ms` : '-' }}
          </template>
          <template v-else-if="column.dataIndex === 'riskLevel'">
            <a-badge :color="record.riskLevel === 'high' ? 'red' : record.riskLevel === 'medium' ? 'orange' : 'green'" :text="record.riskLevel || '-'" />
          </template>
          <template v-else-if="column.key === 'toolCount'">
            {{ (record.toolCalls || []).length }}
          </template>
          <template v-else-if="column.key === 'anomalyTag'">
            <a-space>
              <a-tag v-if="record.isSlow" color="error">高延迟</a-tag>
              <a-tag v-if="record.hasFailedTool" color="warning">工具失败</a-tag>
              <a-tag v-if="record.hasNoCitation" color="default">无知识引用</a-tag>
            </a-space>
          </template>
          <template v-else-if="column.dataIndex === 'createdAt'">
            {{ formatDate(record.createdAt) }}
          </template>
        </template>
        <template #expandedRowRender="{ record }">
          <div class="trace-detail">
            <a-alert v-if="record.hasFailedTool" type="warning" message="检测到工具调用失败，建议优先检查下游依赖与参数映射" show-icon style="margin-bottom: 12px;" />
            <a-alert v-if="record.isSlow" type="error" message="检测到高延迟链路，建议核查模型响应和工具超时" show-icon style="margin-bottom: 12px;" />

            <a-descriptions :column="2" size="small" bordered style="margin-bottom: 16px">
              <a-descriptions-item label="模型">{{ record.modelUsed || '-' }}</a-descriptions-item>
              <a-descriptions-item label="意图">{{ record.intent || '-' }}</a-descriptions-item>
              <a-descriptions-item label="风险等级">
                <a-badge :color="record.riskLevel === 'high' ? 'red' : record.riskLevel === 'medium' ? 'orange' : 'green'" :text="record.riskLevel || '-'" />
              </a-descriptions-item>
              <a-descriptions-item label="审批">
                <a-tag v-if="record.approvalRequired" color="orange">需审批 {{ record.approvalId || '' }}</a-tag>
                <span v-else>无需审批</span>
              </a-descriptions-item>
              <a-descriptions-item label="实体" :span="2" v-if="record.entities && Object.keys(record.entities).length > 0">
                <span v-for="(val, key) in record.entities" :key="key" style="margin-right: 8px;">
                  <a-tag v-if="val != null">{{ key }}={{ val }}</a-tag>
                </span>
              </a-descriptions-item>
              <a-descriptions-item label="Token 使用量">{{ record.tokenUsage ?? '-' }}</a-descriptions-item>
              <a-descriptions-item label="预估成本">{{ record.estimatedCost != null ? `\$${record.estimatedCost}` : '-' }}</a-descriptions-item>
            </a-descriptions>

            <div v-if="record.workflowSteps && record.workflowSteps.length > 0" style="margin-bottom: 16px">
              <div class="section-label">工作流步骤</div>
              <a-timeline>
                <a-timeline-item
                  v-for="(step, idx) in record.workflowSteps"
                  :key="idx"
                  :color="step.agent === 'approval_agent' ? 'red' : step.agent === 'supervisor_agent' ? 'blue' : step.agent === 'check_guardrails' ? 'purple' : 'green'"
                >
                  <div>
                    <a-tag :color="step.agent === 'approval_agent' ? 'red' : step.agent === 'supervisor_agent' ? 'blue' : 'cyan'" size="small">{{ step.agent }}</a-tag>
                    <span style="font-weight: 500;">{{ step.action }}</span>
                    <div v-if="step.detail && Object.keys(step.detail).length > 0" style="margin-top: 4px; font-size: 12px; color: rgba(0,0,0,0.45);">
                      <span v-for="(val, key) in step.detail" :key="key" style="margin-right: 10px;">
                        {{ key }}: {{ typeof val === 'object' ? JSON.stringify(val) : val }}
                      </span>
                    </div>
                  </div>
                </a-timeline-item>
              </a-timeline>
            </div>

            <div v-if="record.handoffs && record.handoffs.length > 0" style="margin-bottom: 16px">
              <div class="section-label">Handoff 链路</div>
              <a-steps :current="record.handoffs.length" size="small">
                <a-step
                  v-for="(hf, idx) in record.handoffs"
                  :key="idx"
                  :title="`${hf.fromAgent} → ${hf.toAgent}`"
                  :description="hf.reason || ''"
                />
              </a-steps>
            </div>

            <div v-if="record.handoffGraph" style="margin-bottom: 16px">
              <div class="section-label">执行流程图</div>
              <HandoffGraph :graph="record.handoffGraph" />
            </div>

            <div v-if="record.toolCalls && record.toolCalls.length > 0">
              <div class="section-label">工具调用</div>
              <a-timeline>
                <a-timeline-item
                  v-for="(tc, idx) in record.toolCalls"
                  :key="idx"
                  :color="tc.status === 'success' ? 'green' : 'red'"
                >
                  <div class="tool-call-item">
                    <span class="tool-name">{{ tc.toolName || tc.tool_name }}</span>
                    <span class="tool-agent" v-if="tc.agentName || tc.agent_name">({{ tc.agentName || tc.agent_name }})</span>
                    <div class="tool-detail" v-if="tc.input || tc.toolInput">
                      <span class="tool-label">输入:</span>
                      {{ formatJson(tc.input || tc.toolInput) }}
                    </div>
                    <div class="tool-detail" v-if="tc.output || tc.toolOutput">
                      <span class="tool-label">输出:</span>
                      {{ formatJson(tc.output || tc.toolOutput) }}
                    </div>
                    <div class="tool-meta" v-if="tc.latencyMs != null">{{ tc.latencyMs }}ms</div>
                  </div>
                </a-timeline-item>
              </a-timeline>
            </div>

            <div v-if="record.finalAnswer" style="margin-top: 12px">
              <div class="section-label">最终回答</div>
              <div class="final-answer">{{ record.finalAnswer }}</div>
            </div>
          </div>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ApiOutlined, ClockCircleOutlined, CheckCircleOutlined, WarningOutlined } from '@ant-design/icons-vue'
import { message as antMessage } from 'ant-design-vue'
import { getTraces, getTraceDetail } from '@/api/traces'
import HandoffGraph from '@/components/HandoffGraph.vue'

const route = useRoute()
const router = useRouter()

const activeTab = ref('traces')

const handleTabChange = (key: string) => {
  if (key === 'costs') {
    router.push('/agentops/costs')
  } else if (key === 'eval') {
    router.push('/agentops/eval')
  } else {
    router.push('/agentops')
  }
}

const columns = [
  { title: 'Trace ID', dataIndex: 'traceId', key: 'traceId', width: 200, ellipsis: true },
  { title: '意图', dataIndex: 'intent', key: 'intent', width: 140, ellipsis: true },
  { title: '风险等级', dataIndex: 'riskLevel', key: 'riskLevel', width: 100 },
  { title: '延迟(ms)', dataIndex: 'latencyMs', key: 'latencyMs', width: 110 },
  { title: '工具调用数', key: 'toolCount', width: 110 },
  { title: '异常标签', key: 'anomalyTag', width: 140 },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt', width: 180 },
]

const traces = ref<any[]>([])
const loading = ref(false)
const traceSearchId = ref('')

const filters = ref<{ anomalyType: string | undefined }>({
  anomalyType: undefined,
})

const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

const normalizeTrace = (t: any) => ({
  traceId: t.traceId ?? t.trace_id ?? '',
  sessionId: t.sessionId ?? t.session_id ?? '',
  userQuery: t.userQuery ?? t.user_query ?? '',
  selectedAgent: t.selectedAgent ?? t.selected_agent ?? '',
  intent: t.intent ?? '',
  riskLevel: t.riskLevel ?? t.risk_level ?? '',
  entities: t.entities ?? null,
  modelUsed: t.modelUsed ?? t.model_used ?? '',
  latencyMs: t.latencyMs ?? t.latency_ms,
  tokenUsage: t.tokenUsage ?? t.token_usage,
  estimatedCost: t.estimatedCost ?? t.estimated_cost,
  approvalRequired: t.approvalRequired ?? t.approval_required ?? false,
  approvalId: t.approvalId ?? t.approval_id ?? null,
  handoffCount: t.handoffCount ?? t.handoff_count ?? 0,
  citations: t.citations ?? [],
  workflowSteps: t.workflowSteps ?? t.workflow_steps ?? [],
  toolCalls: t.toolCalls ?? t.tool_calls ?? [],
  handoffs: t.handoffs ?? [],
  handoffGraph: t.handoffGraph ?? t.handoff_graph ?? null,
  finalAnswer: t.finalAnswer ?? t.final_answer ?? '',
  createdAt: t.createdAt ?? t.created_at ?? '',
})

const normalizedTraces = computed(() => {
  return traces.value.map(item => ({
    ...item,
    hasFailedTool: (item.toolCalls || []).some((tool: any) => tool.status !== 'success'),
    hasNoCitation: !(item.finalAnswer || '').includes('来源'),
    isSlow: Number(item.latencyMs || 0) >= 5000,
  }))
})

const filteredTraces = computed(() => {
  let result = normalizedTraces.value
  if (filters.value.anomalyType === 'slow') result = result.filter(t => t.isSlow)
  if (filters.value.anomalyType === 'tool_failed') result = result.filter(t => t.hasFailedTool)
  if (filters.value.anomalyType === 'no_citation') result = result.filter(t => t.hasNoCitation)
  return result
})

const stats = computed(() => {
  const total = traces.value.length
  const avgLatency = total > 0 ? Math.round(traces.value.reduce((sum, t) => sum + Number(t.latencyMs || 0), 0) / total) : 0
  const toolSuccess = traces.value.reduce((sum, t) => {
    const calls = t.toolCalls || []
    if (calls.length === 0) return sum
    return sum + calls.filter((c: any) => c.status === 'success').length / calls.length
  }, 0)
  const toolRate = total > 0 ? Math.round(toolSuccess / total * 100) : 100
  const anomalyCount = normalizedTraces.value.filter(t => t.hasFailedTool || t.hasNoCitation || t.isSlow).length
  return { total, avgLatency, toolRate, anomalyCount }
})

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const formatJson = (data: any) => {
  if (!data) return '-'
  if (typeof data === 'string') {
    try { return JSON.stringify(JSON.parse(data), null, 0).slice(0, 300) } catch { return data.slice(0, 300) }
  }
  return JSON.stringify(data, null, 0).slice(0, 300)
}

const extractPayload = (res: any) => {
  const d = res.data?.data ?? res.data
  if (d && typeof d === 'object' && !Array.isArray(d) && d.code !== undefined) return d.data
  return d
}

const loadTraces = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.value.current,
      page_size: pagination.value.pageSize,
    }
    const res = await getTraces(params)
    const data = extractPayload(res)
    if (data) {
      const rawList = data.records ?? (Array.isArray(data) ? data : [])
      traces.value = rawList.map(normalizeTrace)
      pagination.value.total = Number(data.total ?? 0)
    }
  } catch (err: any) {
    console.error('加载 Trace 列表失败', err)
    antMessage.error('加载 Trace 列表失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag: any) => {
  pagination.value.current = pag.current
  pagination.value.pageSize = pag.pageSize
  loadTraces()
}

const handleSearchTrace = async (value: string) => {
  if (!value.trim()) {
    loadTraces()
    return
  }
  loading.value = true
  try {
    const res = await getTraceDetail(value.trim())
    const data = extractPayload(res)
    if (data) {
      traces.value = [normalizeTrace(data)]
      pagination.value.total = 1
    } else {
      traces.value = []
      pagination.value.total = 0
    }
  } catch (err: any) {
    traces.value = []
    pagination.value.total = 0
  } finally {
    loading.value = false
  }
}

const resetFilters = () => {
  filters.value.anomalyType = undefined
  traceSearchId.value = ''
  loadTraces()
}

onMounted(() => {
  const traceId = route.query.traceId as string
  if (traceId) {
    traceSearchId.value = traceId
    handleSearchTrace(traceId)
  } else {
    loadTraces()
  }
})
</script>

<style scoped>
.agentops-view {
  min-height: 100%;
  padding: 24px;
  background: #f0f2f5;
}

.ops-stats {
  margin-bottom: 16px;
}

.filter-bar {
  margin-bottom: 16px;
}

.trace-detail {
  padding: 8px 0;
}

.section-label {
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
  margin-bottom: 8px;
}

.tool-call-item {
  font-size: 13px;
}

.tool-name {
  font-weight: 600;
  color: #1f5fae;
}

.tool-agent {
  color: rgba(0, 0, 0, 0.45);
  margin-left: 4px;
}

.tool-detail {
  color: rgba(0, 0, 0, 0.65);
  margin-top: 2px;
}

.tool-label {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
}

.tool-meta {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
}

.final-answer {
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
  font-size: 13px;
  color: rgba(0, 0, 0, 0.65);
  line-height: 1.6;
}
</style>
