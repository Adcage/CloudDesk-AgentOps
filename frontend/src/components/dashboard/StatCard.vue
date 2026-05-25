<template>
  <a-card :bordered="false" class="stat-card">
    <div class="card-header">
      <span class="card-title">{{ title }}</span>
      <a-tooltip :title="subtitle">
        <component :is="QuestionCircleOutlined" class="info-icon" />
      </a-tooltip>
    </div>
    <div class="card-content">
      <div class="stat-value">
        <span v-if="prefix" class="prefix">{{ prefix }}</span>
        <span class="value">{{ formatValue(value) }}</span>
      </div>
      <div class="chart-mini" v-if="chartData">
        <MiniChart :data="chartData" :type="chartType" />
      </div>
      <div class="progress-bar" v-if="progress !== undefined">
        <a-progress :percent="progress" :show-info="false" stroke-color="#52c41a" />
        <span class="progress-text">{{ progress }}%</span>
      </div>
    </div>
    <div class="card-footer">
      <div v-if="dailyValue" class="footer-item">
        <span class="footer-label">日访问量</span>
        <span class="footer-value">{{ dailyValue.toLocaleString() }}</span>
      </div>
      <div v-if="trend" class="footer-item">
        <span class="footer-label">周同比</span>
        <span class="trend-value">
          {{ trend.week }}%
          <component :is="CaretUpOutlined" style="color: #f5222d" />
        </span>
      </div>
      <div v-if="trend" class="footer-item">
        <span class="footer-label">日同比</span>
        <span class="trend-value">
          {{ trend.day }}%
          <component :is="CaretUpOutlined" style="color: #52c41a" />
        </span>
      </div>
      <div v-if="conversion" class="footer-item">
        <span class="footer-label">转化率</span>
        <span class="footer-value">{{ conversion }}</span>
      </div>
    </div>
  </a-card>
</template>

<script setup lang="ts">
import { QuestionCircleOutlined, CaretUpOutlined } from '@ant-design/icons-vue';
import MiniChart from './MiniChart.vue';

interface Trend {
  week: number
  day: number
}

interface Props {
  title?: string
  subtitle?: string
  value?: number | string
  prefix?: string
  dailyValue?: number
  trend?: Trend
  conversion?: string
  chartData?: number[]
  chartType?: 'line' | 'area' | 'bar'
  progress?: number
}

withDefaults(defineProps<Props>(), {
  title: '',
  subtitle: '',
  value: 0,
  prefix: '',
  dailyValue: undefined,
  trend: undefined,
  conversion: '',
  chartData: undefined,
  chartType: 'line',
  progress: undefined
});

const formatValue = (val: number | string): string => {
  if (typeof val === 'number') {
    return val.toLocaleString();
  }
  return String(val);
};
</script>

<style scoped>
.stat-card {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.card-title {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.65);
}

.info-icon {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  cursor: help;
}

.card-content {
  margin-bottom: 16px;
}

.stat-value {
  display: flex;
  align-items: baseline;
  margin-bottom: 8px;
}

.prefix {
  font-size: 16px;
  color: rgba(0, 0, 0, 0.85);
  margin-right: 4px;
}

.value {
  font-size: 30px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
  line-height: 1.2;
}

.chart-mini {
  height: 46px;
  margin-top: 8px;
}

.progress-bar {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-text {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.85);
  min-width: 40px;
}

.card-footer {
  display: flex;
  gap: 16px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.footer-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.footer-label {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.footer-value,
.trend-value {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>

