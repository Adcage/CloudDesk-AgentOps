<template>
  <div class="cost-view">
    <a-row :gutter="[16, 16]" class="cost-stats">
      <a-col :xs="24" :sm="6">
        <a-card :bordered="false">
          <a-statistic
            title="今日成本"
            :value="todayCost"
            prefix="$"
            :precision="4"
            :value-style="{ color: '#1f5fae' }"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="6">
        <a-card :bordered="false">
          <a-statistic
            title="本月累计"
            :value="monthCost"
            prefix="$"
            :precision="2"
            :value-style="{ color: '#52c41a' }"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="6">
        <a-card :bordered="false">
          <a-statistic
            title="日均成本"
            :value="avgDailyCost"
            prefix="$"
            :precision="3"
            :value-style="{ color: '#faad14' }"
          />
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="6">
        <a-card :bordered="false">
          <a-statistic
            title="预算占比"
            :value="budgetPercent"
            suffix="%"
            :value-style="{ color: budgetPercent > 80 ? '#ff4d4f' : '#52c41a' }"
          />
        </a-card>
      </a-col>
    </a-row>

    <a-row :gutter="[16, 16]" style="margin-top: 16px">
      <a-col :xs="24" :lg="12">
        <a-card title="各 Agent 成本占比（近 7 天）" :bordered="false">
          <div ref="agentChartRef" style="height: 300px"></div>
        </a-card>
      </a-col>
      <a-col :xs="24" :lg="12">
        <a-card title="成本趋势（近 30 天）" :bordered="false">
          <div ref="trendChartRef" style="height: 300px"></div>
        </a-card>
      </a-col>
    </a-row>

    <a-card title="模型调用明细（近 7 天）" :bordered="false" style="margin-top: 16px">
      <a-table
        :columns="modelColumns"
        :data-source="modelData"
        :loading="loading"
        row-key="model_name"
        :pagination="false"
        size="small"
      />
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick, computed } from 'vue'
import * as echarts from 'echarts'
import { getCostsToday, getCostsByAgent, getCostsHistory } from '@/api/costs'
import type { CostByAgent, CostByModel, DailyTrend } from '@/api/costs'

const loading = ref(false)
const todayCost = ref(0)
const monthCost = ref(0)
const byAgentData = ref<CostByAgent[]>([])
const trendData = ref<DailyTrend[]>([])
const modelData = ref<CostByModel[]>([])

const agentChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
let agentChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null

const modelColumns = [
  { title: '模型', dataIndex: 'model_name', key: 'model_name', width: 160 },
  { title: '调用次数', dataIndex: 'call_count', key: 'call_count', width: 100 },
  { title: '输入 Token', dataIndex: 'total_input_tokens', key: 'total_input_tokens', width: 120 },
  { title: '输出 Token', dataIndex: 'total_output_tokens', key: 'total_output_tokens', width: 120 },
  { title: '成本 ($)', dataIndex: 'total_cost', key: 'total_cost', width: 120 },
]

const avgDailyCost = computed(() => {
  if (trendData.value.length === 0) return 0
  return trendData.value.reduce((s, i) => s + i.daily_cost, 0) / trendData.value.length
})

const budgetPercent = computed(() => {
  if (monthCost.value === 0) return 0
  return Math.round((monthCost.value / 5.0) * 100)
})

async function loadData() {
  loading.value = true
  try {
    const [todayRes, agentRes, historyRes] = await Promise.allSettled([
      getCostsToday(),
      getCostsByAgent(7),
      getCostsHistory(30),
    ])

    if (todayRes.status === 'fulfilled') {
      const d = todayRes.value.data
      todayCost.value = d.total_cost
      modelData.value = d.by_model
    }

    if (agentRes.status === 'fulfilled') {
      byAgentData.value = agentRes.value.data.by_agent
    }

    if (historyRes.status === 'fulfilled') {
      trendData.value = historyRes.value.data.daily_trend
      monthCost.value = trendData.value.reduce((s, i) => s + i.daily_cost, 0)
    }

    await nextTick()
    renderCharts()
  } finally {
    loading.value = false
  }
}

function renderCharts() {
  if (agentChartRef.value) {
    agentChart?.dispose()
    agentChart = echarts.init(agentChartRef.value)
    agentChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: ${c}' },
      series: [
        {
          type: 'pie',
          radius: ['40%', '70%'],
          data: byAgentData.value.map((i) => ({
            name: i.agent_name,
            value: i.total_cost,
          })),
          label: { formatter: '{b}\n${c}' },
        },
      ],
    })
  }

  if (trendChartRef.value) {
    trendChart?.dispose()
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'category', data: trendData.value.map((i) => i.date) },
      yAxis: { type: 'value', name: 'USD' },
      series: [
        {
          type: 'line',
          data: trendData.value.map((i) => i.daily_cost),
          smooth: true,
          areaStyle: { opacity: 0.15 },
        },
      ],
      grid: { left: 60, right: 20, top: 20, bottom: 30 },
    })
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.cost-view {
  padding: 0;
}
.cost-stats {
  margin-bottom: 0;
}
</style>
