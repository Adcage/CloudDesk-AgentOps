<template>
  <div class="date-util-demo">
    <a-card title="DateUtil 日期工具演示" :bordered="false">
      <a-tabs v-model:activeKey="activeTab">
        <!-- 基础格式化 -->
        <a-tab-pane key="format" tab="格式化">
          <a-space direction="vertical" :size="16" style="width: 100%">
            <a-card title="基础格式化" size="small">
              <a-descriptions :column="1" bordered size="small">
                <a-descriptions-item label="当前时间">
                  {{ currentTime }}
                </a-descriptions-item>
                <a-descriptions-item label="format()">
                  {{ DateUtil.format(currentTime, 'YYYY-MM-DD HH:mm:ss') }}
                </a-descriptions-item>
                <a-descriptions-item label="formatDate()">
                  {{ DateUtil.formatDate(currentTime) }}
                </a-descriptions-item>
                <a-descriptions-item label="formatTime()">
                  {{ DateUtil.formatTime(currentTime) }}
                </a-descriptions-item>
                <a-descriptions-item label="formatChinese()">
                  {{ DateUtil.formatChinese(currentTime) }}
                </a-descriptions-item>
                <a-descriptions-item label="formatChineseDateTime()">
                  {{ DateUtil.formatChineseDateTime(currentTime) }}
                </a-descriptions-item>
              </a-descriptions>
            </a-card>

            <a-card title="智能格式化" size="small">
              <a-descriptions :column="1" bordered size="small">
                <a-descriptions-item label="刚刚">
                  {{ DateUtil.smartFormat(new Date()) }}
                </a-descriptions-item>
                <a-descriptions-item label="5分钟前">
                  {{ DateUtil.smartFormat(DateUtil.subtract(new Date(), 5, 'minute')) }}
                </a-descriptions-item>
                <a-descriptions-item label="2小时前">
                  {{ DateUtil.smartFormat(DateUtil.subtract(new Date(), 2, 'hour')) }}
                </a-descriptions-item>
                <a-descriptions-item label="3天前">
                  {{ DateUtil.smartFormat(DateUtil.subtract(new Date(), 3, 'day')) }}
                </a-descriptions-item>
                <a-descriptions-item label="1个月前">
                  {{ DateUtil.smartFormat(DateUtil.subtract(new Date(), 1, 'month')) }}
                </a-descriptions-item>
              </a-descriptions>
            </a-card>
          </a-space>
        </a-tab-pane>

        <!-- 相对时间 -->
        <a-tab-pane key="relative" tab="相对时间">
          <a-space direction="vertical" :size="16" style="width: 100%">
            <a-card title="相对时间" size="small">
              <a-descriptions :column="1" bordered size="small">
                <a-descriptions-item label="3天前">
                  {{ DateUtil.timeAgo(DateUtil.subtract(new Date(), 3, 'day')) }}
                </a-descriptions-item>
                <a-descriptions-item label="2小时前">
                  {{ DateUtil.timeAgo(DateUtil.subtract(new Date(), 2, 'hour')) }}
                </a-descriptions-item>
                <a-descriptions-item label="5分钟前">
                  {{ DateUtil.timeAgo(DateUtil.subtract(new Date(), 5, 'minute')) }}
                </a-descriptions-item>
                <a-descriptions-item label="3天后">
                  {{ DateUtil.toNow(DateUtil.add(new Date(), 3, 'day')) }}
                </a-descriptions-item>
                <a-descriptions-item label="2小时后">
                  {{ DateUtil.toNow(DateUtil.add(new Date(), 2, 'hour')) }}
                </a-descriptions-item>
              </a-descriptions>
            </a-card>
          </a-space>
        </a-tab-pane>

        <!-- 日期判断 -->
        <a-tab-pane key="check" tab="日期判断">
          <a-space direction="vertical" :size="16" style="width: 100%">
            <a-card title="时间判断" size="small">
              <a-descriptions :column="2" bordered size="small">
                <a-descriptions-item label="是否是今天">
                  <a-tag :color="DateUtil.isToday(new Date()) ? 'green' : 'red'">
                    {{ DateUtil.isToday(new Date()) ? '是' : '否' }}
                  </a-tag>
                </a-descriptions-item>
                <a-descriptions-item label="是否是昨天">
                  <a-tag :color="DateUtil.isYesterday(DateUtil.subtract(new Date(), 1, 'day')) ? 'green' : 'red'">
                    {{ DateUtil.isYesterday(DateUtil.subtract(new Date(), 1, 'day')) ? '是' : '否' }}
                  </a-tag>
                </a-descriptions-item>
                <a-descriptions-item label="是否是本周">
                  <a-tag :color="DateUtil.isThisWeek(new Date()) ? 'green' : 'red'">
                    {{ DateUtil.isThisWeek(new Date()) ? '是' : '否' }}
                  </a-tag>
                </a-descriptions-item>
                <a-descriptions-item label="是否是本月">
                  <a-tag :color="DateUtil.isThisMonth(new Date()) ? 'green' : 'red'">
                    {{ DateUtil.isThisMonth(new Date()) ? '是' : '否' }}
                  </a-tag>
                </a-descriptions-item>
                <a-descriptions-item label="是否是本年">
                  <a-tag :color="DateUtil.isThisYear(new Date()) ? 'green' : 'red'">
                    {{ DateUtil.isThisYear(new Date()) ? '是' : '否' }}
                  </a-tag>
                </a-descriptions-item>
                <a-descriptions-item label="星期几">
                  <a-tag color="blue">{{ DateUtil.getDayName() }}</a-tag>
                </a-descriptions-item>
              </a-descriptions>
            </a-card>

            <a-card title="日期范围判断" size="small">
              <p>判断 2026-03-06 是否在 2026-03-01 到 2026-03-10 之间：</p>
              <a-tag :color="DateUtil.isBetween('2026-03-06', '2026-03-01', '2026-03-10') ? 'green' : 'red'">
                {{ DateUtil.isBetween('2026-03-06', '2026-03-01', '2026-03-10') ? '在范围内' : '不在范围内' }}
              </a-tag>
            </a-card>
          </a-space>
        </a-tab-pane>

        <!-- 日期计算 -->
        <a-tab-pane key="calculate" tab="日期计算">
          <a-space direction="vertical" :size="16" style="width: 100%">
            <a-card title="添加/减少时间" size="small">
              <a-descriptions :column="1" bordered size="small">
                <a-descriptions-item label="当前时间">
                  {{ DateUtil.format(currentTime) }}
                </a-descriptions-item>
                <a-descriptions-item label="7天后">
                  {{ DateUtil.format(DateUtil.add(currentTime, 7, 'day')) }}
                </a-descriptions-item>
                <a-descriptions-item label="2个月后">
                  {{ DateUtil.format(DateUtil.add(currentTime, 2, 'month')) }}
                </a-descriptions-item>
                <a-descriptions-item label="3天前">
                  {{ DateUtil.format(DateUtil.subtract(currentTime, 3, 'day')) }}
                </a-descriptions-item>
                <a-descriptions-item label="1年前">
                  {{ DateUtil.format(DateUtil.subtract(currentTime, 1, 'year')) }}
                </a-descriptions-item>
              </a-descriptions>
            </a-card>

            <a-card title="时间差计算" size="small">
              <a-descriptions :column="1" bordered size="small">
                <a-descriptions-item label="距离2026-03-10还有">
                  {{ DateUtil.diff('2026-03-10', currentTime, 'day') }} 天
                </a-descriptions-item>
                <a-descriptions-item label="距离2026-01-01已过">
                  {{ DateUtil.diff(currentTime, '2026-01-01', 'day') }} 天
                </a-descriptions-item>
                <a-descriptions-item label="本月已过">
                  {{ DateUtil.diff(currentTime, DateUtil.startOfMonth(), 'day') }} 天
                </a-descriptions-item>
              </a-descriptions>
            </a-card>
          </a-space>
        </a-tab-pane>

        <!-- 时间范围 -->
        <a-tab-pane key="range" tab="时间范围">
          <a-space direction="vertical" :size="16" style="width: 100%">
            <a-card title="开始/结束时间" size="small">
              <a-descriptions :column="1" bordered size="small">
                <a-descriptions-item label="今天开始">
                  {{ DateUtil.format(DateUtil.startOfToday()) }}
                </a-descriptions-item>
                <a-descriptions-item label="今天结束">
                  {{ DateUtil.format(DateUtil.endOfToday()) }}
                </a-descriptions-item>
                <a-descriptions-item label="本周开始">
                  {{ DateUtil.format(DateUtil.startOfWeek()) }}
                </a-descriptions-item>
                <a-descriptions-item label="本周结束">
                  {{ DateUtil.format(DateUtil.endOfWeek()) }}
                </a-descriptions-item>
                <a-descriptions-item label="本月开始">
                  {{ DateUtil.format(DateUtil.startOfMonth()) }}
                </a-descriptions-item>
                <a-descriptions-item label="本月结束">
                  {{ DateUtil.format(DateUtil.endOfMonth()) }}
                </a-descriptions-item>
                <a-descriptions-item label="本年开始">
                  {{ DateUtil.format(DateUtil.startOfYear()) }}
                </a-descriptions-item>
                <a-descriptions-item label="本年结束">
                  {{ DateUtil.format(DateUtil.endOfYear()) }}
                </a-descriptions-item>
              </a-descriptions>
            </a-card>

            <a-card title="最近N天" size="small">
              <p>最近7天的日期范围：</p>
              <a-tag color="blue">
                {{ DateUtil.formatDate(recentDays[0]) }} 至 {{ DateUtil.formatDate(recentDays[1]) }}
              </a-tag>
            </a-card>
          </a-space>
        </a-tab-pane>

        <!-- 时长格式化 -->
        <a-tab-pane key="duration" tab="时长格式化">
          <a-space direction="vertical" :size="16" style="width: 100%">
            <a-card title="时长格式化" size="small">
              <a-descriptions :column="1" bordered size="small">
                <a-descriptions-item label="30秒">
                  {{ DateUtil.formatDuration(30000) }}
                </a-descriptions-item>
                <a-descriptions-item label="5分钟">
                  {{ DateUtil.formatDuration(300000) }}
                </a-descriptions-item>
                <a-descriptions-item label="1小时30分钟">
                  {{ DateUtil.formatDuration(5400000) }}
                </a-descriptions-item>
                <a-descriptions-item label="1天2小时30分钟">
                  {{ DateUtil.formatDuration(95400000) }}
                </a-descriptions-item>
                <a-descriptions-item label="7天">
                  {{ DateUtil.formatDuration(604800000) }}
                </a-descriptions-item>
              </a-descriptions>
            </a-card>
          </a-space>
        </a-tab-pane>

        <!-- 时间戳 -->
        <a-tab-pane key="timestamp" tab="时间戳">
          <a-space direction="vertical" :size="16" style="width: 100%">
            <a-card title="时间戳操作" size="small">
              <a-descriptions :column="1" bordered size="small">
                <a-descriptions-item label="当前时间戳（毫秒）">
                  {{ DateUtil.timestamp() }}
                </a-descriptions-item>
                <a-descriptions-item label="当前时间戳（秒）">
                  {{ DateUtil.timestampSecond() }}
                </a-descriptions-item>
                <a-descriptions-item label="时间戳转日期">
                  {{ DateUtil.format(DateUtil.fromTimestamp(DateUtil.timestamp())) }}
                </a-descriptions-item>
              </a-descriptions>
            </a-card>
          </a-space>
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { DateUtil } from '@/utils'

const activeTab = ref('format')
const currentTime = ref(new Date())

// 最近7天
const recentDays = computed(() => DateUtil.getRecentDays(7))

// 每秒更新当前时间
setInterval(() => {
  currentTime.value = new Date()
}, 1000)
</script>

<style scoped>
.date-util-demo {
  padding: 24px;
}
</style>
