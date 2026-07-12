<script setup>
import {
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
} from 'vue'
import * as echarts from 'echarts'

import {
  DataAnalysis,
  Document,
  MoreFilled,
  VideoCamera,
  Warning,
} from '@element-plus/icons-vue'


/* ==============================
   页面数据
================================ */

const dateRange = ref([
  '2024-01-09',
  '2024-01-15',
])

const metricCards = [
  {
    label: '今日消耗(元)',
    value: '12,345',
    change: '+12.5%',
    comparison: '较昨日',
    type: 'danger',
  },
  {
    label: '今日订单数',
    value: '256',
    change: '+8.2%',
    comparison: '较昨日',
    type: 'success',
  },
  {
    label: '今日GMV(元)',
    value: '45,678',
    change: '+15.3%',
    comparison: '较昨日',
    type: 'success',
  },
  {
    label: 'ROI',
    value: '1.23',
    change: '+5.7%',
    comparison: '较昨日',
    type: 'success',
  },
]

const pendingTasks = [
  {
    icon: Document,
    label: '脚本待审核',
    count: 12,
    type: 'primary',
  },
  {
    icon: VideoCamera,
    label: '视频待发布',
    count: 8,
    type: 'danger',
  },
  {
    icon: DataAnalysis,
    label: '投流待优化',
    count: 15,
    type: 'primary',
  },
  {
    icon: Warning,
    label: '商品待处理',
    count: 23,
    type: 'danger',
  },
]

const workflowList = [
  {
    name: '爆款内容分析助手',
    status: '运行中',
    statusType: 'running',
  },
  {
    name: '脚本生成助手',
    status: '运行中',
    statusType: 'running',
  },
  {
    name: '视频创意生成助手',
    status: '已完成',
    statusType: 'completed',
  },
  {
    name: '投流优化助手',
    status: '运行中',
    statusType: 'running',
  },
]

const recentActivities = [
  {
    text: '商品「智能手表」创建了视频任务',
    time: '5分钟前',
  },
  {
    text: '脚本「夏季穿搭指南」已生成',
    time: '15分钟前',
  },
  {
    text: '视频「智能手表评测」发布成功',
    time: '30分钟前',
  },
  {
    text: '投流计划「智能手表-潜力计划」已启动',
    time: '1小时前',
  },
]


/* ==============================
   图表实例
================================ */

const trendChartRef = ref(null)
const distributionChartRef = ref(null)

let trendChart = null
let distributionChart = null
let resizeObserver = null


/* ==============================
   消耗趋势折线图
================================ */

function createTrendChart() {
  if (!trendChartRef.value) {
    return
  }

  trendChart?.dispose()
  trendChart = echarts.init(trendChartRef.value)

  trendChart.setOption({
    animationDuration: 700,

    tooltip: {
      trigger: 'axis',
      backgroundColor: '#171c29',
      borderColor: '#30384a',
      borderWidth: 1,
      padding: 10,
      textStyle: {
        color: '#f3f4f8',
        fontSize: 11,
      },
      axisPointer: {
        type: 'line',
        lineStyle: {
          color: 'rgba(124, 92, 255, 0.45)',
          width: 1,
        },
      },
    },

    legend: {
      top: 1,
      right: 2,
      itemWidth: 8,
      itemHeight: 6,
      itemGap: 14,
      icon: 'circle',
      textStyle: {
        color: '#717a8c',
        fontSize: 9,
      },
      data: [
        '消耗(元)',
        'GMV(元)',
      ],
    },

    grid: {
      top: 39,
      left: 8,
      right: 24,
      bottom: 5,
      containLabel: true,
    },

    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: [
        '01-09',
        '01-10',
        '01-11',
        '01-12',
        '01-13',
        '01-14',
        '01-15',
      ],
      axisLine: {
        lineStyle: {
          color: '#252c3b',
        },
      },
      axisTick: {
        show: false,
      },
      axisLabel: {
        color: '#687184',
        fontSize: 9,
        margin: 12,
        interval: 0,
        hideOverlap: true,
      },
    },

    yAxis: {
      type: 'value',
      min: 0,
      max: 20000,
      interval: 5000,
      axisLine: {
        show: false,
      },
      axisTick: {
        show: false,
      },
      axisLabel: {
        color: '#687184',
        fontSize: 9,
        formatter(value) {
          if (value === 0) {
            return '0'
          }

          return `${value / 1000}K`
        },
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(255, 255, 255, 0.045)',
        },
      },
    },

    series: [
      {
        name: '消耗(元)',
        type: 'line',
        smooth: 0.42,
        symbol: 'circle',
        symbolSize: 5,
        showSymbol: true,
        data: [
          8500,
          11300,
          8800,
          10400,
          14600,
          16800,
          10200,
        ],
        lineStyle: {
          width: 2,
          color: '#765bff',
        },
        itemStyle: {
          color: '#765bff',
          borderColor: '#c7bcff',
          borderWidth: 1,
        },
        emphasis: {
          scale: 1.4,
        },
      },
      {
        name: 'GMV(元)',
        type: 'line',
        smooth: 0.42,
        symbol: 'circle',
        symbolSize: 5,
        showSymbol: true,
        data: [
          4800,
          7600,
          5100,
          6900,
          9200,
          8300,
          14400,
        ],
        lineStyle: {
          width: 2,
          color: '#39bdd7',
        },
        itemStyle: {
          color: '#39bdd7',
          borderColor: '#a1e9f2',
          borderWidth: 1,
        },
        emphasis: {
          scale: 1.4,
        },
      },
    ],
  })
}


/* ==============================
   流量渠道环形图
================================ */

function createDistributionChart() {
  if (!distributionChartRef.value) {
    return
  }

  distributionChart?.dispose()

  distributionChart = echarts.init(
    distributionChartRef.value,
  )

  const channelMap = {
    抖音: {
      value: '35.6%',
      color: '#765bff',
    },
    快手: {
      value: '25.8%',
      color: '#ef7075',
    },
    视频号: {
      value: '20.1%',
      color: '#f0ad52',
    },
    其他: {
      value: '18.5%',
      color: '#44c9a5',
    },
  }

  distributionChart.setOption({
    animationDuration: 700,

    tooltip: {
      trigger: 'item',
      backgroundColor: '#171c29',
      borderColor: '#30384a',
      borderWidth: 1,
      padding: 10,
      textStyle: {
        color: '#f3f4f8',
        fontSize: 11,
      },
      formatter(params) {
        return `${params.name}<br/>占比：${params.value}%`
      },
    },

    legend: {
      orient: 'vertical',
      right: 2,
      top: 'center',
      itemWidth: 7,
      itemHeight: 7,
      itemGap: 14,
      icon: 'circle',
      selectedMode: false,
      textStyle: {
        color: '#9098a8',
        fontSize: 9,
        rich: {
          value: {
            color: '#f3f4f8',
            fontSize: 11,
            fontWeight: 600,
            lineHeight: 16,
          },
          name: {
            color: '#687184',
            fontSize: 8,
            lineHeight: 12,
          },
        },
      },
      formatter(name) {
        const item = channelMap[name]

        return `{value|${item.value}}\n{name|${name}}`
      },
    },

    graphic: [
      {
        type: 'text',
        left: '31%',
        top: '42%',
        silent: true,
        style: {
          text: '总消耗',
          fill: '#7f8797',
          fontSize: 9,
          textAlign: 'center',
        },
      },
      {
        type: 'text',
        left: '27%',
        top: '51%',
        silent: true,
        style: {
          text: '12,345',
          fill: '#f3f4f8',
          fontSize: 16,
          fontWeight: 600,
          textAlign: 'center',
        },
      },
    ],

    series: [
      {
        name: '流量渠道',
        type: 'pie',
        radius: [
          '46%',
          '65%',
        ],
        center: [
          '35%',
          '53%',
        ],
        avoidLabelOverlap: true,
        label: {
          show: false,
        },
        labelLine: {
          show: false,
        },
        itemStyle: {
          borderColor: '#131824',
          borderWidth: 2,
        },
        emphasis: {
          scale: true,
          scaleSize: 5,
        },
        data: [
          {
            value: 35.6,
            name: '抖音',
            itemStyle: {
              color: '#765bff',
            },
          },
          {
            value: 25.8,
            name: '快手',
            itemStyle: {
              color: '#ef7075',
            },
          },
          {
            value: 20.1,
            name: '视频号',
            itemStyle: {
              color: '#f0ad52',
            },
          },
          {
            value: 18.5,
            name: '其他',
            itemStyle: {
              color: '#44c9a5',
            },
          },
        ],
      },
    ],
  })
}


/* ==============================
   图表尺寸调整
================================ */

function resizeCharts() {
  trendChart?.resize()
  distributionChart?.resize()
}


/* ==============================
   生命周期
================================ */

onMounted(async () => {
  await nextTick()

  createTrendChart()
  createDistributionChart()

  window.addEventListener(
    'resize',
    resizeCharts,
  )

  if (typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => {
      resizeCharts()
    })

    if (trendChartRef.value) {
      resizeObserver.observe(
        trendChartRef.value,
      )
    }

    if (distributionChartRef.value) {
      resizeObserver.observe(
        distributionChartRef.value,
      )
    }
  }
})

onBeforeUnmount(() => {
  window.removeEventListener(
    'resize',
    resizeCharts,
  )

  resizeObserver?.disconnect()

  trendChart?.dispose()
  distributionChart?.dispose()

  trendChart = null
  distributionChart = null
})
</script>


<template>
  <div class="dashboard-page">
    <!-- 页面标题与日期 -->
    <section class="dashboard-heading">
      <h2>数据概览</h2>

      <el-date-picker
        v-model="dateRange"
        type="daterange"
        value-format="YYYY-MM-DD"
        format="YYYY-MM-DD"
        range-separator="—"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        :clearable="false"
        class="date-picker"
      />
    </section>

    <!-- 核心指标 -->
    <section class="metric-grid">
      <article
        v-for="item in metricCards"
        :key="item.label"
        class="metric-card"
      >
        <span class="metric-label">
          {{ item.label }}
        </span>

        <strong class="metric-value">
          {{ item.value }}
        </strong>

        <div class="metric-change">
          <span
            class="change-value"
            :class="item.type"
          >
            <span class="change-arrow">
              ◆
            </span>

            {{ item.change }}
          </span>

          <span class="comparison-text">
            {{ item.comparison }}
          </span>
        </div>
      </article>
    </section>

    <!-- 图表区域 -->
    <section class="chart-grid">
      <article class="dashboard-card trend-card">
        <div class="card-header">
          <h3>消耗趋势</h3>

          <button
            type="button"
            class="more-button"
            aria-label="查看更多"
          >
            <el-icon>
              <MoreFilled />
            </el-icon>
          </button>
        </div>

        <div
          ref="trendChartRef"
          class="trend-chart"
        />
      </article>

      <article class="dashboard-card distribution-card">
        <div class="card-header">
          <h3>流量渠道分布</h3>

          <button
            type="button"
            class="more-button"
            aria-label="查看更多"
          >
            <el-icon>
              <MoreFilled />
            </el-icon>
          </button>
        </div>

        <div
          ref="distributionChartRef"
          class="distribution-chart"
        />
      </article>
    </section>

    <!-- 底部信息区域 -->
    <section class="bottom-grid">
      <!-- 任务待办 -->
      <article class="dashboard-card list-card">
        <div class="card-header">
          <h3>任务待办</h3>

          <button
            type="button"
            class="more-text"
          >
            更多
            <span>›</span>
          </button>
        </div>

        <div class="task-list">
          <div
            v-for="task in pendingTasks"
            :key="task.label"
            class="task-row"
          >
            <div class="row-main">
              <span
                class="row-icon"
                :class="task.type"
              >
                <el-icon>
                  <component :is="task.icon" />
                </el-icon>
              </span>

              <span class="row-label">
                {{ task.label }}
              </span>
            </div>

            <div class="task-count">
              <strong>
                {{ task.count }}
              </strong>

              <span>›</span>
            </div>
          </div>
        </div>
      </article>

      <!-- AI 工作流 -->
      <article class="dashboard-card list-card">
        <div class="card-header">
          <h3>AI工作流运行状态</h3>

          <button
            type="button"
            class="more-button"
            aria-label="查看更多"
          >
            <el-icon>
              <MoreFilled />
            </el-icon>
          </button>
        </div>

        <div class="workflow-list">
          <div
            v-for="workflow in workflowList"
            :key="workflow.name"
            class="workflow-row"
          >
            <div class="row-main">
              <span class="workflow-icon">
                AI
              </span>

              <span class="row-label">
                {{ workflow.name }}
              </span>
            </div>

            <span
              class="workflow-status"
              :class="workflow.statusType"
            >
              {{ workflow.status }}
            </span>
          </div>
        </div>
      </article>

      <!-- 最近活动 -->
      <article class="dashboard-card activity-card">
        <div class="card-header">
          <h3>最近活动</h3>

          <button
            type="button"
            class="more-button"
            aria-label="查看更多"
          >
            <el-icon>
              <MoreFilled />
            </el-icon>
          </button>
        </div>

        <div class="activity-list">
          <div
            v-for="(activity, index) in recentActivities"
            :key="activity.text"
            class="activity-row"
          >
            <div class="activity-line">
              <span class="activity-dot" />

              <span
                v-if="
                  index <
                  recentActivities.length - 1
                "
                class="activity-connector"
              />
            </div>

            <p>
              {{ activity.text }}
            </p>

            <time>
              {{ activity.time }}
            </time>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>


<style scoped>
.dashboard-page {
  width: 100%;
  min-width: 0;
  min-height: 100%;
  color: var(--app-text-primary);
}

/* ==============================
   页面标题
================================ */

.dashboard-heading {
  display: flex;
  min-height: 34px;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 12px;
}

.dashboard-heading h2 {
  margin: 0;
  color: #f1f3f8;
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
}

.date-picker.el-date-editor {
  width: 220px !important;
  flex: 0 0 220px;
}

.date-picker:deep(
  .el-range-editor.el-input__wrapper
) {
  width: 220px;
  height: 31px;
  padding: 0 10px;
  background: #101520;
  border-radius: 6px;
  box-shadow:
    0 0 0 1px #242b3a inset;
}

.date-picker:deep(.el-range-input) {
  width: 75px;
  color: #9199aa;
  font-size: 9px;
  background: transparent;
}

.date-picker:deep(.el-range-separator) {
  width: 20px;
  color: #596273;
  font-size: 9px;
}

.date-picker:deep(.el-input__icon) {
  color: #596273;
  font-size: 11px;
}

/* ==============================
   指标卡片
================================ */

.metric-grid {
  display: grid;
  grid-template-columns:
    repeat(4, minmax(0, 1fr));
  gap: 11px;
  margin-bottom: 11px;
}

.metric-card {
  display: flex;
  min-width: 0;
  height: 84px;
  flex-direction: column;
  justify-content: center;
  padding: 12px 14px;
  background:
    linear-gradient(
      145deg,
      rgba(255, 255, 255, 0.016),
      transparent 65%
    ),
    #121722;
  border: 1px solid #202736;
  border-radius: 6px;
  box-shadow:
    0 7px 18px rgba(0, 0, 0, 0.11);
}

.metric-label {
  overflow: hidden;
  color: #8991a1;
  font-size: 9px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.metric-value {
  display: block;
  margin-top: 5px;
  color: #f4f5f9;
  font-size: 22px;
  font-weight: 500;
  letter-spacing: -0.5px;
  line-height: 26px;
}

.metric-change {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 5px;
  overflow: hidden;
  font-size: 8px;
  white-space: nowrap;
}

.change-value {
  display: inline-flex;
  align-items: center;
  gap: 2px;
  font-weight: 600;
}

.change-value.success {
  color: #37ce93;
}

.change-value.danger {
  color: #ef7377;
}

.change-arrow {
  display: inline-block;
  font-size: 5px;
  transform: rotate(45deg);
}

.comparison-text {
  color: #596273;
}

/* ==============================
   公共卡片
================================ */

.dashboard-card {
  min-width: 0;
  overflow: hidden;
  background:
    linear-gradient(
      145deg,
      rgba(255, 255, 255, 0.014),
      transparent 60%
    ),
    #111621;
  border: 1px solid #202736;
  border-radius: 6px;
  box-shadow:
    0 8px 22px rgba(0, 0, 0, 0.12);
}

.card-header {
  display: flex;
  min-height: 20px;
  align-items: center;
  justify-content: space-between;
}

.card-header h3 {
  margin: 0;
  color: #e4e6ed;
  font-size: 10px;
  font-weight: 600;
}

.more-button {
  display: flex;
  width: 23px;
  height: 23px;
  align-items: center;
  justify-content: center;
  padding: 0;
  color: #586173;
  cursor: pointer;
  background: transparent;
  border: 0;
  border-radius: 5px;
}

.more-button:hover {
  color: #a89aff;
  background: rgba(124, 92, 255, 0.08);
}

/* ==============================
   图表区域
================================ */

.chart-grid {
  display: grid;
  grid-template-columns:
    minmax(0, 1.62fr)
    minmax(280px, 1fr);
  gap: 11px;
  margin-bottom: 11px;
}

.trend-card,
.distribution-card {
  height: 198px;
  padding: 12px 13px 7px;
}

.trend-chart,
.distribution-chart {
  width: 100%;
  height: 164px;
}

/* ==============================
   底部区域
================================ */

.bottom-grid {
  display: grid;
  grid-template-columns:
    minmax(0, 0.95fr)
    minmax(0, 1.07fr)
    minmax(0, 1.15fr);
  gap: 11px;
}

.list-card,
.activity-card {
  height: 137px;
  padding: 10px 12px;
}

/* ==============================
   任务待办
================================ */

.more-text {
  display: flex;
  align-items: center;
  gap: 3px;
  padding: 0;
  color: #5f6879;
  font-size: 8px;
  cursor: pointer;
  background: transparent;
  border: 0;
}

.more-text:hover {
  color: #a99cff;
}

.task-list,
.workflow-list {
  margin-top: 6px;
}

.task-row,
.workflow-row {
  display: flex;
  min-height: 25px;
  align-items: center;
  justify-content: space-between;
  border-bottom:
    1px solid rgba(255, 255, 255, 0.035);
}

.task-row:last-child,
.workflow-row:last-child {
  border-bottom: 0;
}

.row-main {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 7px;
}

.row-icon {
  display: flex;
  width: 16px;
  height: 16px;
  flex: 0 0 16px;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  background: rgba(124, 92, 255, 0.13);
  border-radius: 4px;
}

.row-icon.primary {
  color: #8b75ff;
}

.row-icon.danger {
  color: #ef6d76;
  background: rgba(239, 109, 118, 0.11);
}

.row-label {
  min-width: 0;
  overflow: hidden;
  color: #afb5c2;
  font-size: 8px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-count {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #596273;
  font-size: 8px;
}

.task-count strong {
  color: #e36d72;
  font-size: 8px;
  font-weight: 500;
}

/* ==============================
   AI 工作流
================================ */

.workflow-icon {
  display: flex;
  width: 16px;
  height: 16px;
  flex: 0 0 16px;
  align-items: center;
  justify-content: center;
  color: #41c8cc;
  font-size: 6px;
  font-weight: 700;
  background: rgba(65, 200, 204, 0.1);
  border-radius: 4px;
}

.workflow-status {
  padding: 2px 5px;
  font-size: 7px;
  border-radius: 3px;
  white-space: nowrap;
}

.workflow-status.running {
  color: #36bdcb;
  background: rgba(54, 189, 203, 0.1);
}

.workflow-status.completed {
  color: #36c28b;
  background: rgba(54, 194, 139, 0.1);
}

/* ==============================
   最近活动
================================ */

.activity-list {
  margin-top: 6px;
}

.activity-row {
  position: relative;
  display: grid;
  min-height: 25px;
  grid-template-columns:
    13px
    minmax(0, 1fr)
    auto;
  align-items: center;
}

.activity-line {
  position: relative;
  align-self: stretch;
}

.activity-dot {
  position: absolute;
  top: 10px;
  left: 2px;
  z-index: 2;
  width: 5px;
  height: 5px;
  background: #7559ff;
  border-radius: 50%;
  box-shadow:
    0 0 7px rgba(117, 89, 255, 0.62);
}

.activity-connector {
  position: absolute;
  top: 15px;
  bottom: -10px;
  left: 4px;
  width: 1px;
  background: rgba(124, 92, 255, 0.24);
}

.activity-row p {
  min-width: 0;
  margin: 0;
  overflow: hidden;
  color: #aeb4c1;
  font-size: 8px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.activity-row time {
  margin-left: 8px;
  color: #555e70;
  font-size: 7px;
  white-space: nowrap;
}

/* ==============================
   较窄屏幕适配
================================ */

@media (max-width: 1200px) {
  .metric-grid {
    gap: 8px;
  }

  .metric-card {
    padding-right: 10px;
    padding-left: 10px;
  }

  .metric-value {
    font-size: 19px;
  }

  .chart-grid {
    grid-template-columns:
      minmax(0, 1.55fr)
      minmax(260px, 1fr);
    gap: 8px;
  }

  .bottom-grid {
    gap: 8px;
  }
}
</style>