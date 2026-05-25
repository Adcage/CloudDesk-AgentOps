<template>
  <div class="approvals-view">
    <a-page-header title="审批中心" sub-title="按风险评分、审批层级与 SLA 优先处理" />

    <a-row :gutter="[16, 16]" class="approval-stats">
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card :bordered="false">
          <a-statistic title="待审批" :value="stats.pending" :value-style="{ color: '#faad14' }" />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card :bordered="false">
          <a-statistic title="高风险" :value="stats.highRisk" :value-style="{ color: '#ff4d4f' }" />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card :bordered="false">
          <a-statistic title="今日处理" :value="stats.todayProcessed" :value-style="{ color: '#1890ff' }" />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :lg="6">
        <a-card :bordered="false">
          <a-statistic title="通过率" :value="stats.approvalRate" suffix="%" :value-style="{ color: '#52c41a' }" />
        </a-card>
      </a-col>
    </a-row>

    <a-card :bordered="false" class="toolbar-card">
      <a-space :size="12" wrap>
        <a-select v-model:value="statusFilter" placeholder="状态筛选" allow-clear style="width: 160px" @change="loadApprovals">
          <a-select-option value="pending">待审批</a-select-option>
          <a-select-option value="approved">已通过</a-select-option>
          <a-select-option value="rejected">已驳回</a-select-option>
        </a-select>
        <a-select v-model:value="levelFilter" placeholder="审批层级筛选" allow-clear style="width: 160px" @change="loadApprovals">
          <a-select-option :value="1">普通</a-select-option>
          <a-select-option :value="2">主管</a-select-option>
          <a-select-option :value="3">总监</a-select-option>
        </a-select>
        <a-select v-model:value="riskFilter" placeholder="风险等级筛选" allow-clear style="width: 160px" @change="loadApprovals">
          <a-select-option value="low">低</a-select-option>
          <a-select-option value="mid">中</a-select-option>
          <a-select-option value="high">高</a-select-option>
        </a-select>
        <a-button @click="resetFilter">重置</a-button>
      </a-space>
    </a-card>

    <a-table
      :columns="columns"
      :data-source="approvals"
      :loading="loading"
      :pagination="pagination"
      @change="handleTableChange"
      row-key="approvalId"
      :scroll="{ x: 1300 }"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'amount'">
          {{ record.amount != null ? `\$${Number(record.amount).toFixed(2)}` : '-' }}
        </template>
        <template v-else-if="column.dataIndex === 'approvalLevel'">
          <a-tag :color="levelColor(record.approvalLevel)">{{ approvalLevelLabel(record.approvalLevel) }}</a-tag>
        </template>
        <template v-else-if="column.dataIndex === 'riskScore'">
          <a-badge :status="riskColor(record.riskScore)" :text="record.riskScore ?? '-'" />
        </template>
        <template v-else-if="column.dataIndex === 'status'">
          <a-tag :color="statusColor(record.status)">{{ statusLabel(record.status) }}</a-tag>
        </template>
        <template v-else-if="column.dataIndex === 'slaDeadline'">
          {{ formatDate(record.slaDeadline) }}
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space v-if="record.status === 'pending'">
            <a-button type="primary" size="small" @click="handleApprove(record)">通过</a-button>
            <a-button danger size="small" @click="openRejectModal(record)">驳回</a-button>
          </a-space>
          <span v-else>-</span>
        </template>
      </template>
      <template #expandedRowRender="{ record }">
        <div class="expand-content">
          <a-descriptions :column="2" size="small" bordered>
            <a-descriptions-item label="审批原因">{{ record.reason || '暂无' }}</a-descriptions-item>
            <a-descriptions-item label="Trace ID">
              <router-link v-if="record.traceId" :to="`/agentops?traceId=${record.traceId}`" target="_blank">
                {{ record.traceId }}
              </router-link>
              <span v-else>暂无</span>
            </a-descriptions-item>
            <a-descriptions-item label="申请人">{{ record.requestedBy || '-' }}</a-descriptions-item>
            <a-descriptions-item label="审核人">{{ record.reviewedBy || '-' }}</a-descriptions-item>
            <a-descriptions-item label="审核时间">{{ formatDate(record.reviewedAt) }}</a-descriptions-item>
            <a-descriptions-item label="建议动作">
              <a-tag :color="Number(record.riskScore) >= 60 ? 'warning' : 'success'">
                {{ Number(record.riskScore) >= 60 ? '建议主管优先审核' : '可按常规流程处理' }}
              </a-tag>
            </a-descriptions-item>
          </a-descriptions>
        </div>
      </template>
    </a-table>

    <a-modal
      v-model:open="rejectModalVisible"
      title="驳回审批"
      @ok="handleReject"
      ok-text="确认驳回"
      cancel-text="取消"
      :confirm-loading="rejectLoading"
    >
      <a-form layout="vertical">
        <a-form-item label="驳回原因">
          <a-textarea v-model:value="rejectReason" placeholder="请输入驳回原因" :rows="3" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { getApprovals, approveApproval, rejectApproval } from '@/api/approvals'
import DateUtil from '@/utils/date'

const columns = [
  { title: '审批编号', dataIndex: 'approvalId', key: 'approvalId', width: 140 },
  { title: '客户', dataIndex: 'customerId', key: 'customerId', width: 120 },
  { title: '订单编号', dataIndex: 'orderId', key: 'orderId', width: 140 },
  { title: '金额', dataIndex: 'amount', key: 'amount', width: 120 },
  { title: '审批层级', dataIndex: 'approvalLevel', key: 'approvalLevel', width: 100 },
  { title: '风险评分', dataIndex: 'riskScore', key: 'riskScore', width: 100 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: 'SLA 截止', dataIndex: 'slaDeadline', key: 'slaDeadline', width: 180 },
  { title: '申请原因', dataIndex: 'reason', key: 'reason', ellipsis: true },
  { title: '操作', key: 'action', width: 160, fixed: 'right' },
]

const approvals = ref<any[]>([])
const loading = ref(false)
const statusFilter = ref<string | undefined>(undefined)
const levelFilter = ref<number | undefined>(undefined)
const riskFilter = ref<string | undefined>(undefined)

const rejectModalVisible = ref(false)
const rejectReason = ref('')
const rejectTargetId = ref('')
const rejectLoading = ref(false)

const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

const stats = computed(() => {
  const pending = approvals.value.filter(a => a.status === 'pending').length
  const highRisk = approvals.value.filter(a => Number(a.riskScore) >= 60 && a.status === 'pending').length
  const todayProcessed = approvals.value.filter(a => a.reviewedAt && DateUtil.isToday(a.reviewedAt)).length
  const approved = approvals.value.filter(a => a.status === 'approved').length
  const total = approvals.value.filter(a => ['approved', 'rejected'].includes(a.status)).length
  const approvalRate = total > 0 ? Math.round(approved / total * 100) : 0
  return { pending, highRisk, todayProcessed, approvalRate }
})

const riskColor = (score: number) => {
  if (score >= 80) return 'error'
  if (score >= 60) return 'warning'
  if (score >= 30) return 'processing'
  return 'success'
}

const approvalLevelLabel = (level: number) => ({ 1: '普通', 2: '主管', 3: '总监' }[level] || '-')

const levelColor = (level: number) => ({ 1: 'default', 2: 'blue', 3: 'red' }[level] || 'default')

const statusColor = (status: string) => {
  const map: Record<string, string> = { pending: 'orange', approved: 'green', rejected: 'red' }
  return map[status] || 'default'
}

const statusLabel = (status: string) => {
  const map: Record<string, string> = { pending: '待审批', approved: '已通过', rejected: '已驳回' }
  return map[status] || status
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

const extractPayload = (res: any) => {
  const d = res.data?.data ?? res.data
  if (d && typeof d === 'object' && !Array.isArray(d) && d.code !== undefined) return d.data
  return d
}

const loadApprovals = async () => {
  loading.value = true
  try {
    const params: any = {
      current: pagination.value.current,
      pageSize: pagination.value.pageSize,
    }
    if (statusFilter.value) params.status = statusFilter.value
    if (levelFilter.value != null) params.approvalLevel = levelFilter.value
    if (riskFilter.value) params.riskLevel = riskFilter.value

    const res = await getApprovals(params)
    const data = extractPayload(res)
    if (data) {
      approvals.value = data.records ?? (Array.isArray(data) ? data : [])
      pagination.value.total = Number(data.total ?? 0)
    }
  } catch (err: any) {
    console.error('加载审批列表失败', err)
    message.error('加载审批列表失败，请刷新重试')
  } finally {
    loading.value = false
  }
}

const handleTableChange = (pag: any) => {
  pagination.value.current = pag.current
  pagination.value.pageSize = pag.pageSize
  loadApprovals()
}

const resetFilter = () => {
  statusFilter.value = undefined
  levelFilter.value = undefined
  riskFilter.value = undefined
  pagination.value.current = 1
  loadApprovals()
}

const handleApprove = async (record: any) => {
  try {
    await approveApproval(record.approvalId)
    message.success('审批已通过')
    loadApprovals()
  } catch (err: any) {
    message.error('审批操作失败，请稍后重试')
  }
}

const openRejectModal = (record: any) => {
  rejectTargetId.value = record.approvalId
  rejectReason.value = ''
  rejectModalVisible.value = true
}

const handleReject = async () => {
  if (!rejectReason.value.trim()) {
    message.warning('请输入驳回原因')
    return
  }
  rejectLoading.value = true
  try {
    await rejectApproval(rejectTargetId.value, { reason: rejectReason.value })
    message.success('审批已驳回')
    rejectModalVisible.value = false
    loadApprovals()
  } catch (err: any) {
    message.error('审批操作失败，请稍后重试')
  } finally {
    rejectLoading.value = false
  }
}

onMounted(() => {
  loadApprovals()
})
</script>

<style scoped>
.approvals-view {
  min-height: 100%;
  padding: 24px;
  background: #f0f2f5;
}

.approval-stats {
  margin-bottom: 16px;
}

.toolbar-card {
  margin-bottom: 16px;
}

.expand-content {
  padding: 8px 0;
}
</style>
