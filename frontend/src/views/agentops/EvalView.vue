<template>
  <div class="eval-view">
    <a-page-header title="评估中心" sub-title="查看 Agent Eval 指标、结果明细与版本表现" />

    <a-row :gutter="[16, 16]" class="summary-row">
      <a-col :xs="24" :sm="12" :md="6">
        <a-card :bordered="false"><a-statistic title="总通过率" :value="summary.pass_rate" suffix="%" /></a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card :bordered="false"><a-statistic title="检索命中率" :value="summary.retrieval_hit_rate" suffix="%" /></a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card :bordered="false"><a-statistic title="工具准确率" :value="summary.tool_accuracy" suffix="%" /></a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="6">
        <a-card :bordered="false"><a-statistic title="审批准确率" :value="summary.approval_accuracy" suffix="%" /></a-card>
      </a-col>
    </a-row>

    <a-card title="评估结果" :bordered="false" style="margin-top: 16px">
      <template #extra>
        <a-space>
          <a-button type="primary" :loading="running" @click="handleRunEval">运行全部评估</a-button>
          <a-button @click="loadAll">刷新</a-button>
        </a-space>
      </template>

      <a-table
        :columns="columns"
        :data-source="results"
        :loading="loading"
        :pagination="pagination"
        row-key="result_id"
        @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="['retrieval_hit', 'tool_call_correct', 'approval_routing_correct', 'task_success'].includes(column.dataIndex)">
            <a-tag :color="record[column.dataIndex] ? 'green' : record[column.dataIndex] === false ? 'red' : 'default'">
              {{ record[column.dataIndex] === null || record[column.dataIndex] === undefined ? '不适用' : record[column.dataIndex] ? '通过' : '失败' }}
            </a-tag>
          </template>
          <template v-else-if="column.dataIndex === 'estimated_cost'">
            ${{ Number(record.estimated_cost || 0).toFixed(4) }}
          </template>
          <template v-else-if="column.dataIndex === 'latency_ms'">
            {{ record.latency_ms }}ms
          </template>
        </template>
      </a-table>
    </a-card>

    <a-card title="Prompt 版本对比" :bordered="false" style="margin-top: 16px">
      <a-table :columns="versionColumns" :data-source="versions" :pagination="false" row-key="version">
        <template #bodyCell="{ column, record }">
          <template v-if="column.dataIndex === 'pass_rate'">
            <a-progress :percent="record.pass_rate" :show-info="true" />
          </template>
          <template v-else-if="column.dataIndex === 'avg_cost'">
            ${{ Number(record.avg_cost || 0).toFixed(4) }}
          </template>
          <template v-else-if="column.dataIndex === 'avg_latency_ms'">
            {{ record.avg_latency_ms }}ms
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { getEvalByVersion, getEvalResults, getEvalSummary, runEval } from '@/api/evals'

const loading = ref(false)
const running = ref(false)
const results = ref<any[]>([])
const versions = ref<any[]>([])
const summary = reactive({
  total: 0,
  pass_rate: 0,
  retrieval_hit_rate: 0,
  tool_accuracy: 0,
  approval_accuracy: 0,
})

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

const columns = [
  { title: 'Case ID', dataIndex: 'case_id', key: 'case_id', width: 120 },
  { title: '检索命中', dataIndex: 'retrieval_hit', key: 'retrieval_hit', width: 110 },
  { title: '工具准确', dataIndex: 'tool_call_correct', key: 'tool_call_correct', width: 110 },
  { title: '审批路由', dataIndex: 'approval_routing_correct', key: 'approval_routing_correct', width: 110 },
  { title: '任务成功', dataIndex: 'task_success', key: 'task_success', width: 110 },
  { title: '延迟', dataIndex: 'latency_ms', key: 'latency_ms', width: 100 },
  { title: '成本', dataIndex: 'estimated_cost', key: 'estimated_cost', width: 100 },
  { title: 'Prompt 版本', dataIndex: 'prompt_version', key: 'prompt_version', width: 120 },
  { title: '创建时间', dataIndex: 'created_at', key: 'created_at' },
]

const versionColumns = [
  { title: '版本', dataIndex: 'version', key: 'version' },
  { title: '样本数', dataIndex: 'total', key: 'total' },
  { title: '通过率', dataIndex: 'pass_rate', key: 'pass_rate' },
  { title: '平均延迟', dataIndex: 'avg_latency_ms', key: 'avg_latency_ms' },
  { title: '平均成本', dataIndex: 'avg_cost', key: 'avg_cost' },
]

function extractPayload(res: any) {
  const d = res.data?.data ?? res.data
  if (d && typeof d === 'object' && !Array.isArray(d) && d.code !== undefined) return d.data
  return d
}

async function loadSummary() {
  const res = await getEvalSummary()
  Object.assign(summary, extractPayload(res) || {})
}

async function loadResults() {
  loading.value = true
  try {
    const res = await getEvalResults(pagination.current, pagination.pageSize)
    const data = extractPayload(res) || {}
    results.value = data.records || []
    pagination.total = Number(data.total || 0)
  } finally {
    loading.value = false
  }
}

async function loadVersions() {
  const res = await getEvalByVersion()
  versions.value = extractPayload(res) || []
}

async function loadAll() {
  await Promise.all([loadSummary(), loadResults(), loadVersions()])
}

async function handleRunEval() {
  running.value = true
  try {
    await runEval()
    message.success('评估运行完成')
    await loadAll()
  } catch (error) {
    message.error('评估运行失败')
  } finally {
    running.value = false
  }
}

function handleTableChange(pag: any) {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadResults()
}

onMounted(() => {
  loadAll()
})
</script>

<style scoped>
.eval-view {
  min-height: 100%;
  padding: 24px;
  background: #f0f2f5;
}

.summary-row {
  margin-bottom: 0;
}
</style>
