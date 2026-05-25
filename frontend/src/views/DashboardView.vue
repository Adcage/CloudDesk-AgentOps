<template>
  <div class="dashboard-view">
    <a-page-header title="运营看板" sub-title="实时监控业务指标与异常告警" />

    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card :bordered="false" :loading="loading">
          <a-statistic 
            title="今日新增工单" 
            :value="metrics.todayNewTickets" 
            :value-style="{ color: '#1890ff' }"
          >
            <template #suffix>
              <span class="stat-suffix">/ {{ metrics.todayResolvedTickets }} 已解决</span>
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card :bordered="false" :loading="loading">
          <a-statistic 
            title="待处理工单" 
            :value="metrics.openTickets" 
            :value-style="{ color: metrics.overdueTickets > 0 ? '#ff4d4f' : '#52c41a' }"
          >
            <template #suffix>
              <a-tag v-if="metrics.overdueTickets > 0" color="error">{{ metrics.overdueTickets }} 超时</a-tag>
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card :bordered="false" :loading="loading">
          <a-statistic 
            title="待审批" 
            :value="metrics.pendingApprovals" 
            :value-style="{ color: '#faad14' }"
          >
            <template #suffix>
              <a-tag v-if="metrics.highRiskApprovals > 0" color="warning">{{ metrics.highRiskApprovals }} 高风险</a-tag>
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card :bordered="false" :loading="loading">
          <a-statistic 
            title="SLA 达标率" 
            :value="metrics.slaComplianceRate" 
            suffix="%" 
            :precision="2"
            :value-style="{ color: metrics.slaComplianceRate >= 90 ? '#52c41a' : '#ff4d4f' }"
          />
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="[16, 16]" class="content-row">
      <a-col :xs="24" :lg="12">
        <a-card title="关键指标" :bordered="false">
          <a-descriptions :column="1" size="small">
            <a-descriptions-item label="平均响应时长">
              <a-tag :color="metrics.avgResponseTimeHours < 2 ? 'success' : 'warning'">
                {{ metrics.avgResponseTimeHours }} 小时
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="工单升级率">
              <a-tag :color="metrics.ticketEscalationRate < 10 ? 'success' : 'error'">
                {{ metrics.ticketEscalationRate }}%
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="审批通过率">
              <a-tag color="processing">{{ metrics.approvalApprovalRate }}%</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="总工单数">
              <span>{{ metrics.totalTickets }}</span>
            </a-descriptions-item>
            <a-descriptions-item label="总审批数">
              <span>{{ metrics.totalApprovals }}</span>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>
      </a-col>

      <a-col :xs="24" :lg="12">
        <a-card title="异常告警" :bordered="false">
          <a-list size="small" :data-source="alerts">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #avatar>
                    <a-badge :status="item.level" />
                  </template>
                  <template #title>{{ item.title }}</template>
                  <template #description>{{ item.description }}</template>
                </a-list-item-meta>
              </a-list-item>
            </template>
            <template #locale>
              <a-empty v-if="alerts.length === 0" description="暂无异常" :image="simpleImage" />
            </template>
          </a-list>
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="[16, 16]" class="content-row">
      <a-col :span="24">
        <a-card title="今日待办事项" :bordered="false">
          <a-table 
            :columns="todoColumns" 
            :data-source="todos" 
            :loading="loading"
            :pagination="false"
            size="small"
          >
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'priority'">
                <a-tag :color="priorityColors[record.priority]">{{ priorityLabels[record.priority] }}</a-tag>
              </template>
              <template v-if="column.key === 'slaStatus'">
                <a-tag :color="record.slaStatus === 'overdue' ? 'error' : 'success'">
                  {{ record.slaStatus === 'overdue' ? '已超时' : '正常' }}
                </a-tag>
              </template>
              <template v-if="column.key === 'action'">
                <a-button type="link" size="small" @click="router.push('/tickets')">前往处理</a-button>
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Empty } from 'ant-design-vue'
import request from '@/request'
import { getMyTodoTickets } from '@/api/tickets'
import { getStoredUserId } from '@/stores/user'

const router = useRouter()

const loading = ref(true)
const simpleImage = Empty.PRESENTED_IMAGE_SIMPLE

interface DashboardMetrics {
  totalTickets: number
  openTickets: number
  overdueTickets: number
  totalApprovals: number
  pendingApprovals: number
  highRiskApprovals: number
  slaComplianceRate: number
  avgResponseTimeHours: number
  ticketEscalationRate: number
  approvalApprovalRate: number
  todayNewTickets: number
  todayResolvedTickets: number
  todayNewApprovals: number
  todayProcessedApprovals: number
}

const metrics = ref<DashboardMetrics>({
  totalTickets: 0,
  openTickets: 0,
  overdueTickets: 0,
  totalApprovals: 0,
  pendingApprovals: 0,
  highRiskApprovals: 0,
  slaComplianceRate: 0,
  avgResponseTimeHours: 0,
  ticketEscalationRate: 0,
  approvalApprovalRate: 0,
  todayNewTickets: 0,
  todayResolvedTickets: 0,
  todayNewApprovals: 0,
  todayProcessedApprovals: 0,
})

const alerts = ref<Array<{ level: string; title: string; description: string }>>([])
const todos = ref<any[]>([])

const todoColumns = [
  { title: '工单编号', dataIndex: 'ticketId', key: 'ticketId', width: 120 },
  { title: '标题', dataIndex: 'subject', key: 'subject' },
  { title: '优先级', dataIndex: 'priority', key: 'priority', width: 100 },
  { title: 'SLA状态', dataIndex: 'slaStatus', key: 'slaStatus', width: 100 },
  { title: '操作', key: 'action', width: 80 },
]

const priorityColors: Record<string, string> = {
  urgent: 'error',
  high: 'warning',
  medium: 'processing',
  low: 'default',
}

const priorityLabels: Record<string, string> = {
  urgent: '紧急',
  high: '高',
  medium: '中',
  low: '低',
}

const extractData = (res: any) => {
  const d = res.data?.data ?? res.data
  if (d && typeof d === 'object' && !Array.isArray(d) && d.code !== undefined) return d.data
  return d
}

const getCurrentUserId = () => getStoredUserId() || 'U001'

const loadDashboard = async () => {
  loading.value = true
  try {
    alerts.value = []
    const metricsRes = await request.get('/metrics/dashboard')
    const data = extractData(metricsRes)
    if (data) metrics.value = data

    if (metrics.value.overdueTickets > 0) {
      alerts.value.push({
        level: 'error',
        title: `${metrics.value.overdueTickets} 个工单已超时`,
        description: '请尽快处理以避免 SLA 违约',
      })
    }

    if (metrics.value.highRiskApprovals > 0) {
      alerts.value.push({
        level: 'warning',
        title: `${metrics.value.highRiskApprovals} 个高风险审批待处理`,
        description: '风险评分 ≥ 60，建议优先审核',
      })
    }

    if (metrics.value.slaComplianceRate < 90) {
      alerts.value.push({
        level: 'warning',
        title: 'SLA 达标率低于 90%',
        description: `当前达标率 ${metrics.value.slaComplianceRate}%，需改进响应效率`,
      })
    }

    const todosRes = await getMyTodoTickets(getCurrentUserId())
    const todosData = extractData(todosRes)
    const todoList = Array.isArray(todosData) ? todosData : (todosData?.records ?? [])
    todos.value = todoList.slice(0, 5).map((t: any) => ({
      ...t,
      slaStatus: t.slaDeadline && new Date(t.slaDeadline) < new Date() ? 'overdue' : 'normal',
    }))
  } catch (error) {
    console.error('加载看板数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
.dashboard-view {
  min-height: 100%;
  padding: 24px;
  background: #f0f2f5;
}

.content-row {
  margin-top: 16px;
}

.stat-suffix {
  font-size: 14px;
  color: #8c8c8c;
  margin-left: 8px;
}
</style>
