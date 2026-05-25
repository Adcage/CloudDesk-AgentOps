<template>
  <div class="tickets-view">
    <a-page-header title="工单运营中心" sub-title="按优先级、SLA 与责任人协同处理客户问题" />

    <a-row :gutter="16" class="ticket-stats">
      <a-col :span="6">
        <a-card>
          <a-statistic title="今日待办" :value="stats.todayTodo" :value-style="{ color: '#1890ff' }" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="超时工单" :value="stats.overdue" :value-style="{ color: '#cf1322' }" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="我负责" :value="stats.myAssigned" :value-style="{ color: '#fa8c16' }" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="批量操作" :value="selectedRowKeys.length" suffix="项选中" :value-style="{ color: '#52c41a' }" />
        </a-card>
      </a-col>
    </a-row>

    <a-card class="toolbar-card">
      <a-tabs v-model:activeKey="activeTab" @change="onTabChange">
        <a-tab-pane key="all" tab="全部工单" />
        <a-tab-pane key="mine" tab="我的待办" />
        <a-tab-pane key="overdue" tab="超时工单" />
      </a-tabs>

      <div class="filter-bar">
        <a-space :size="12" wrap>
          <a-select v-model:value="filters.status" placeholder="状态筛选" allow-clear style="width: 160px" @change="loadTickets">
            <a-select-option value="open">待处理</a-select-option>
            <a-select-option value="in_progress">处理中</a-select-option>
            <a-select-option value="resolved">已解决</a-select-option>
            <a-select-option value="closed">已关闭</a-select-option>
          </a-select>
          <a-select v-model:value="filters.priority" placeholder="优先级筛选" allow-clear style="width: 160px" @change="loadTickets">
            <a-select-option value="low">低</a-select-option>
            <a-select-option value="medium">中</a-select-option>
            <a-select-option value="high">高</a-select-option>
            <a-select-option value="urgent">紧急</a-select-option>
          </a-select>
          <a-select v-model:value="filters.category" placeholder="类别筛选" allow-clear style="width: 160px" @change="loadTickets">
            <a-select-option value="billing">账单问题</a-select-option>
            <a-select-option value="account">账号问题</a-select-option>
            <a-select-option value="technical">技术问题</a-select-option>
            <a-select-option value="policy">政策咨询</a-select-option>
            <a-select-option value="other">其他</a-select-option>
          </a-select>
          <a-button @click="resetFilters">重置</a-button>
          <a-button type="primary" :disabled="selectedRowKeys.length === 0" @click="batchAssignModalVisible = true">批量分配</a-button>
          <a-button danger :disabled="selectedRowKeys.length === 0" @click="batchCloseModalVisible = true">批量关闭</a-button>
        </a-space>
      </div>

      <a-table
        :columns="columns"
        :data-source="currentTableData"
        :loading="loading"
        :pagination="pagination"
        @change="handleTableChange"
        row-key="ticketId"
        :scroll="{ x: 1500 }"
        :row-selection="{ selectedRowKeys, onChange: onSelectionChange }"
        :expandedRowKeys="expandedRowKeys"
        @expand="(expanded, record) => expandedRowKeys = expanded ? [record.ticketId] : []"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'priority'">
            <a-tag :color="priorityColor(record.priority)">{{ priorityLabel(record.priority) }}</a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'status'">
            <a-tag :color="statusColor(record.status)">{{ statusLabel(record.status) }}</a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'slaDeadline'">
            <a-tag :color="slaDeadlineColor(record.slaDeadline, record.status)">{{ formatDate(record.slaDeadline) }}</a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'createdAt'">
            {{ formatDate(record.createdAt) }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="viewDetail(record)">查看</a-button>
              <router-link :to="`/agentops?traceId=${record.traceId}`" target="_blank">
                <a-button type="link" size="small" :disabled="!record.traceId">Trace</a-button>
              </router-link>
            </a-space>
          </template>
        </template>
        <template #expandedRowRender="{ record }">
          <div class="expand-content">
            <a-descriptions :column="2" size="small" bordered>
              <a-descriptions-item label="问题描述" :span="2">{{ record.description || '暂无' }}</a-descriptions-item>
              <a-descriptions-item label="处理摘要">{{ record.agentSummary || '暂无' }}</a-descriptions-item>
              <a-descriptions-item label="首次响应时间">{{ formatDate(record.firstResponseAt) }}</a-descriptions-item>
              <a-descriptions-item label="解决时间">{{ formatDate(record.resolvedAt) }}</a-descriptions-item>
              <a-descriptions-item label="关联订单">{{ record.orderId || '暂无' }}</a-descriptions-item>
              <a-descriptions-item label="Trace 链路">
                <router-link v-if="record.traceId" :to="`/agentops?traceId=${record.traceId}`" target="_blank">
                  {{ record.traceId }}
                </router-link>
                <span v-else>暂无</span>
              </a-descriptions-item>
            </a-descriptions>
          </div>
        </template>
      </a-table>
    </a-card>

    <a-modal
      v-model:open="batchAssignModalVisible"
      title="批量分配工单"
      @ok="handleBatchAssign"
      ok-text="确认分配"
      cancel-text="取消"
      :confirm-loading="batchAssignLoading"
    >
      <a-form layout="vertical">
        <a-form-item label="分配给">
          <a-input v-model:value="batchAssignTo" placeholder="请输入责任人" />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal
      v-model:open="batchCloseModalVisible"
      title="批量关闭工单"
      @ok="handleBatchClose"
      ok-text="确认关闭"
      cancel-text="取消"
      :confirm-loading="batchCloseLoading"
    >
      <a-form layout="vertical">
        <a-form-item label="关闭原因">
          <a-textarea v-model:value="batchCloseReason" placeholder="请输入关闭原因" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { getTickets, getMyTodoTickets, batchAssignTickets, batchCloseTickets } from '@/api/tickets'
import { getStoredUserId } from '@/stores/user'

const router = useRouter()

const columns = [
  { title: '工单编号', dataIndex: 'ticketId', key: 'ticketId', width: 140 },
  { title: '客户', dataIndex: 'customerId', key: 'customerId', width: 120 },
  { title: '主题', dataIndex: 'subject', key: 'subject', ellipsis: true },
  { title: '分类', dataIndex: 'category', key: 'category', width: 120 },
  { title: '优先级', dataIndex: 'priority', key: 'priority', width: 100 },
  { title: '当前状态', dataIndex: 'status', key: 'status', width: 110 },
  { title: '责任人', dataIndex: 'assignedTo', key: 'assignedTo', width: 120 },
  { title: 'SLA 截止', dataIndex: 'slaDeadline', key: 'slaDeadline', width: 180 },
  { title: '升级次数', dataIndex: 'escalationCount', key: 'escalationCount', width: 100 },
  { title: '创建时间', dataIndex: 'createdAt', key: 'createdAt', width: 180 },
  { title: '操作', key: 'action', width: 160, fixed: 'right' },
]

const allTickets = ref<any[]>([])
const myTickets = ref<any[]>([])
const loading = ref(false)
const activeTab = ref('all')
const selectedRowKeys = ref<string[]>([])

const stats = computed(() => {
  const now = Date.now()
  const todayStart = new Date()
  todayStart.setHours(0, 0, 0, 0)
  const todayTodo = allTickets.value.filter(t =>
    ['open', 'in_progress'].includes(t.status) && new Date(t.createdAt).getTime() >= todayStart.getTime()
  ).length
  const overdue = allTickets.value.filter(t =>
    t.slaDeadline && new Date(t.slaDeadline).getTime() < now && ['open', 'in_progress'].includes(t.status)
  ).length
  const myAssigned = myTickets.value.length
  return { todayTodo, overdue, myAssigned }
})

const currentTableData = computed(() => {
  if (activeTab.value === 'mine') return myTickets.value
  if (activeTab.value === 'overdue') {
    return allTickets.value.filter(item => item.slaDeadline && new Date(item.slaDeadline).getTime() < Date.now() && ['open', 'in_progress'].includes(item.status))
  }
  return allTickets.value
})

const filters = ref({
  status: undefined as string | undefined,
  priority: undefined as string | undefined,
  category: undefined as string | undefined,
})

const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

const batchAssignModalVisible = ref(false)
const batchAssignTo = ref('')
const batchAssignLoading = ref(false)

const batchCloseModalVisible = ref(false)
const batchCloseReason = ref('')
const batchCloseLoading = ref(false)

const priorityColor = (priority: string) => {
  const map: Record<string, string> = { urgent: 'red', high: 'orange', medium: 'blue', low: 'default' }
  return map[priority] || 'default'
}

const priorityLabel = (priority: string) => {
  const map: Record<string, string> = { urgent: '紧急', high: '高', medium: '中', low: '低' }
  return map[priority] || priority
}

const statusColor = (status: string) => {
  const map: Record<string, string> = { open: 'orange', in_progress: 'blue', resolved: 'green', closed: 'default' }
  return map[status] || 'default'
}

const statusLabel = (status: string) => {
  const map: Record<string, string> = { open: '待处理', in_progress: '处理中', resolved: '已解决', closed: '已关闭' }
  return map[status] || status
}

const slaDeadlineColor = (slaDeadline: string, status: string) => {
  if (!slaDeadline || ['resolved', 'closed'].includes(status)) return 'green'
  const diff = new Date(slaDeadline).getTime() - Date.now()
  if (diff < 0) return 'red'
  if (diff < 3600000) return 'orange'
  return 'green'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const onSelectionChange = (keys: string[]) => {
  selectedRowKeys.value = keys
}

const onTabChange = () => {
  selectedRowKeys.value = []
  pagination.value.current = 1
}

const extractPayload = (res: any) => {
  const d = res.data?.data ?? res.data
  if (d && typeof d === 'object' && !Array.isArray(d) && d.code !== undefined) return d.data
  return d
}

const getCurrentUserId = () => getStoredUserId() || 'U001'

const loadTickets = async () => {
  loading.value = true
  try {
    const params: any = {
      current: pagination.value.current,
      pageSize: pagination.value.pageSize,
    }
    if (filters.value.status) params.status = filters.value.status
    if (filters.value.priority) params.priority = filters.value.priority
    if (filters.value.category) params.category = filters.value.category

    const [allRes, myRes] = await Promise.allSettled([
      getTickets(params),
      getMyTodoTickets(getCurrentUserId()),
    ])

    if (allRes.status === 'fulfilled') {
      const data = extractPayload(allRes.value)
      if (data) {
        allTickets.value = data.records ?? (Array.isArray(data) ? data : [])
        pagination.value.total = Number(data.total ?? 0)
      }
    } else {
      console.error('加载全部工单失败', allRes.reason)
      message.error('加载工单失败，请刷新重试')
    }

    if (myRes.status === 'fulfilled') {
      const myData = extractPayload(myRes.value)
      if (myData) {
        myTickets.value = Array.isArray(myData) ? myData : (myData.records ?? [])
      }
    }
  } catch (err: any) {
    console.error('加载工单失败', err)
    message.error('加载工单失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag: any) => {
  pagination.value.current = pag.current
  pagination.value.pageSize = pag.pageSize
  loadTickets()
}

const resetFilters = () => {
  filters.value = { status: undefined, priority: undefined, category: undefined }
  pagination.value.current = 1
  loadTickets()
}

const expandedRowKeys = ref<string[]>([])

const viewDetail = (record: any) => {
  const id = record.ticketId
  if (expandedRowKeys.value.includes(id)) {
    expandedRowKeys.value = expandedRowKeys.value.filter(k => k !== id)
  } else {
    expandedRowKeys.value = [id]
  }
}

const handleBatchAssign = async () => {
  if (!batchAssignTo.value.trim()) {
    message.warning('请输入责任人')
    return
  }
  batchAssignLoading.value = true
  try {
    await batchAssignTickets({ ticketIds: selectedRowKeys.value, assignedTo: batchAssignTo.value.trim() })
    message.success('批量分配成功')
    batchAssignModalVisible.value = false
    batchAssignTo.value = ''
    selectedRowKeys.value = []
    loadTickets()
  } catch (err: any) {
    message.error('批量分配失败: ' + (err.message || '未知错误'))
  } finally {
    batchAssignLoading.value = false
  }
}

const handleBatchClose = async () => {
  if (!batchCloseReason.value.trim()) {
    message.warning('请输入关闭原因')
    return
  }
  batchCloseLoading.value = true
  try {
    await batchCloseTickets({ ticketIds: selectedRowKeys.value, closureReason: batchCloseReason.value.trim() })
    message.success('批量关闭成功')
    batchCloseModalVisible.value = false
    batchCloseReason.value = ''
    selectedRowKeys.value = []
    loadTickets()
  } catch (err: any) {
    message.error('批量关闭失败: ' + (err.message || '未知错误'))
  } finally {
    batchCloseLoading.value = false
  }
}

onMounted(() => {
  loadTickets()
})
</script>

<style scoped>
.tickets-view {
  min-height: 100%;
  padding: 24px;
  background: #f0f2f5;
}

.ticket-stats {
  margin-bottom: 16px;
}

.toolbar-card {
  margin-bottom: 16px;
}

.filter-bar {
  margin-bottom: 16px;
  padding: 16px;
  background: #fafafa;
  border-radius: 6px;
}

.expand-content {
  padding: 8px 0;
}
</style>
