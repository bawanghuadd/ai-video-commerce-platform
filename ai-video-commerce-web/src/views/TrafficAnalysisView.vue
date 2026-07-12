<script setup>
import {
  nextTick,
  onBeforeUnmount,
  onMounted,
  ref,
} from 'vue'

import * as echarts from 'echarts'

import {
  MoreFilled,
  Picture,
} from '@element-plus/icons-vue'


/* ==============================
   页面状态
================================ */

const activeTab = ref('traffic')

const dateRange = ref([
  '2024-01-09',
  '2024-01-15',
])

const trendChartRef = ref(null)
const funnelChartRef = ref(null)

let trendChart = null
let funnelChart = null
let resizeObserver = null


/* ==============================
   顶部标签
================================ */

const tabs = [
  {
    key: 'traffic',
    label: '投流分析',
  },
  {
    key: 'product',
    label: '商品分析',
  },
  {
    key: 'user',
    label: '用户分析',
  },
]


/* ==============================
   核心指标
================================ */

const metricCards = [
  {
    label: '消耗(元)',
    value: '12,345',
    change: '+12.0%',
    comparison: '较昨日',
    type: 'danger',
  },
  {
    label: '展现量',
    value: '123.4w',
    change: '+8.3%',
    comparison: '较昨日',
    type: 'danger',
  },
  {
    label: '点击量',
    value: '2.4w',
    change: '+18.5%',
    comparison: '较昨日',
    type: 'success',
  },
  {
    label: '转化率',
    value: '2.3%',
    change: '+3.7%',
    comparison: '较昨日',
    extraChange: '+6.7%',
    type: 'danger',
  },
  {
    label: 'ROI',
    value: '1.23',
    change: '+12.8%',
    comparison: '较昨日',
    type: 'danger',
  },
]


/* ==============================
   投放计划数据
================================ */

const campaignRanking = [
  {
    name: '智能手表-核心计划',
    spend: '2,345',
    conversionRate: '2.45%',
    roi: '1.23',
  },
  {
    name: '无线耳机-潜力计划',
    spend: '1,234',
    conversionRate: '1.98%',
    roi: '1.12',
  },
  {
    name: '迷你暖手宝-测试计划',
    spend: '986',
    conversionRate: '1.76%',
    roi: '1.08',
  },
  {
    name: '便携充电宝-放量计划',
    spend: '764',
    conversionRate: '1.53%',
    roi: '0.96',
  },
  {
    name: '运动水杯-人群计划',
    spend: '628',
    conversionRate: '1.32%',
    roi: '0.88',
  },
]


/* ==============================
   素材排行数据
================================ */

const creativeRanking = [
  {
    name: '智能手表深度评测',
    product: '智能手表 X1',
    spend: '125.6w',
    conversionRate: '2.2%',
    orders: '700',
    roi: '1.45',
    imageUrl: '',
  },
  {
    name: '通勤降噪挑战',
    product: '降噪蓝牙耳机',
    spend: '98.7w',
    conversionRate: '1.9%',
    orders: '526',
    roi: '1.31',
    imageUrl: '',
  },
  {
    name: '冬季随身取暖测试',
    product: '迷你暖手宝',
    spend: '87.3w',
    conversionRate: '1.7%',
    orders: '438',
    roi: '1.19',
    imageUrl: '',
  },
  {
    name: '充电速度真实测试',
    product: '便携充电宝',
    spend: '76.5w',
    conversionRate: '1.5%',
    orders: '365',
    roi: '1.07',
    imageUrl: '',
  },
  {
    name: '运动水杯防漏挑战',
    product: '运动水杯',
    spend: '65.8w',
    conversionRate: '1.3%',
    orders: '296',
    roi: '0.94',
    imageUrl: '',
  },
]


/* ==============================
   投流趋势图
================================ */

function createTrendChart() {
  if (!trendChartRef.value) {
    return
  }

  trendChart?.dispose()

  trendChart = echarts.init(
    trendChartRef.value,
  )

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
        fontSize: 10,
      },
      axisPointer: {
        type: 'line',
        lineStyle: {
          color: 'rgba(118, 91, 255, 0.42)',
        },
      },
    },

    legend: {
      top: 2,
      right: 4,
      itemWidth: 8,
      itemHeight: 6,
      itemGap: 15,
      icon: 'diamond',
      data: [
        '消耗(元)',
        'ROI',
      ],
      textStyle: {
        color: '#737c8d',
        fontSize: 8,
      },
    },

    grid: {
      top: 42,
      left: 8,
      right: 12,
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
        fontSize: 8,
        margin: 12,
        interval: 0,
      },
    },

    yAxis: [
      {
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
          fontSize: 8,
          formatter(value) {
            if (value === 0) {
              return '0'
            }

            return `${value / 1000}K`
          },
        },
        splitLine: {
          lineStyle: {
            color: 'rgba(255, 255, 255, 0.04)',
          },
        },
      },
      {
        type: 'value',
        min: 0,
        max: 3,
        interval: 0.5,
        axisLine: {
          show: false,
        },
        axisTick: {
          show: false,
        },
        axisLabel: {
          color: '#687184',
          fontSize: 8,
          formatter(value) {
            return value.toFixed(1)
          },
        },
        splitLine: {
          show: false,
        },
      },
    ],

    series: [
      {
        name: '消耗(元)',
        type: 'line',
        smooth: 0.42,
        symbol: 'circle',
        symbolSize: 5,
        yAxisIndex: 0,
        data: [
          9800,
          15300,
          11800,
          14200,
          14700,
          16200,
          8900,
        ],
        lineStyle: {
          width: 2,
          color: '#765bff',
        },
        itemStyle: {
          color: '#765bff',
          borderColor: '#c1b5ff',
          borderWidth: 1,
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              {
                offset: 0,
                color:
                  'rgba(118, 91, 255, 0.20)',
              },
              {
                offset: 1,
                color:
                  'rgba(118, 91, 255, 0)',
              },
            ],
          },
        },
      },
      {
        name: 'ROI',
        type: 'line',
        smooth: 0.42,
        symbol: 'circle',
        symbolSize: 5,
        yAxisIndex: 1,
        data: [
          0.8,
          1.2,
          0.9,
          1.15,
          1.02,
          1.35,
          1.7,
        ],
        lineStyle: {
          width: 2,
          color: '#ef765f',
        },
        itemStyle: {
          color: '#ef765f',
          borderColor: '#ffc2b5',
          borderWidth: 1,
        },
      },
    ],
  })
}


/* ==============================
   转化漏斗图
================================ */

function createFunnelChart() {
  if (!funnelChartRef.value) {
    return
  }

  funnelChart?.dispose()

  funnelChart = echarts.init(
    funnelChartRef.value,
  )

  funnelChart.setOption({
    animationDuration: 700,

    tooltip: {
      trigger: 'item',
      backgroundColor: '#171c29',
      borderColor: '#30384a',
      borderWidth: 1,
      textStyle: {
        color: '#f3f4f8',
        fontSize: 10,
      },
      formatter(params) {
        return `${params.name}<br/>${params.data.display}`
      },
    },

    series: [
      {
        type: 'funnel',
        left: '12%',
        top: 20,
        bottom: 10,
        width: '62%',
        min: 0,
        max: 1234000,
        minSize: '30%',
        maxSize: '100%',
        sort: 'descending',
        gap: 3,
        label: {
          show: true,
          position: 'inside',
          color: '#e9ebf2',
          fontSize: 9,
          formatter: '{b}',
        },
        labelLine: {
          length: 12,
          lineStyle: {
            width: 1,
            color: '#4c5567',
          },
        },
        itemStyle: {
          borderColor: '#111621',
          borderWidth: 1,
        },
        emphasis: {
          label: {
            fontSize: 10,
          },
        },
        data: [
          {
            value: 1234000,
            name: '展现',
            display: '123.4w（100%）',
            itemStyle: {
              color: '#7357ed',
            },
          },
          {
            value: 24000,
            name: '点击',
            display: '2.4w（1.94%）',
            itemStyle: {
              color: '#4560cf',
            },
          },
          {
            value: 2345,
            name: '加购',
            display: '2345（9.77%）',
            itemStyle: {
              color: '#3f94e8',
            },
          },
          {
            value: 1234,
            name: '下单',
            display: '1234（52.62%）',
            itemStyle: {
              color: '#28a9bc',
            },
          },
          {
            value: 567,
            name: '成交',
            display: '567（45.95%）',
            itemStyle: {
              color: '#32b987',
            },
          },
        ],
      },
    ],

    graphic: [
      {
        type: 'group',
        right: 10,
        top: 30,
        children: [
          {
            type: 'text',
            top: 0,
            style: {
              text: '123.4w（100%）',
              fill: '#aeb5c2',
              fontSize: 8,
            },
          },
          {
            type: 'text',
            top: 42,
            style: {
              text: '2.4w（1.94%）',
              fill: '#aeb5c2',
              fontSize: 8,
            },
          },
          {
            type: 'text',
            top: 84,
            style: {
              text: '2345（9.77%）',
              fill: '#aeb5c2',
              fontSize: 8,
            },
          },
          {
            type: 'text',
            top: 126,
            style: {
              text: '1234（52.62%）',
              fill: '#aeb5c2',
              fontSize: 8,
            },
          },
          {
            type: 'text',
            top: 168,
            style: {
              text: '567（45.95%）',
              fill: '#aeb5c2',
              fontSize: 8,
            },
          },
        ],
      },
    ],
  })
}


/* ==============================
   标签切换
================================ */

function handleTabChange(tabKey) {
  activeTab.value = tabKey
}


/* ==============================
   图表调整
================================ */

function resizeCharts() {
  trendChart?.resize()
  funnelChart?.resize()
}


/* ==============================
   生命周期
================================ */

onMounted(async () => {
  await nextTick()

  createTrendChart()
  createFunnelChart()

  window.addEventListener(
    'resize',
    resizeCharts,
  )

  if (
    typeof ResizeObserver !==
    'undefined'
  ) {
    resizeObserver =
      new ResizeObserver(() => {
        resizeCharts()
      })

    if (trendChartRef.value) {
      resizeObserver.observe(
        trendChartRef.value,
      )
    }

    if (funnelChartRef.value) {
      resizeObserver.observe(
        funnelChartRef.value,
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
  funnelChart?.dispose()

  trendChart = null
  funnelChart = null
})
</script>


<template>
  <div class="traffic-page">
    <section class="traffic-panel">
      <!-- 页面顶部 -->
      <header class="page-header">
        <nav class="analysis-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            type="button"
            class="analysis-tab"
            :class="{
              active:
                activeTab === tab.key,
            }"
            @click="
              handleTabChange(tab.key)
            "
          >
            {{ tab.label }}
          </button>
        </nav>

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
      </header>

      <!-- 投流分析内容 -->
      <template v-if="activeTab === 'traffic'">
        <!-- 指标卡片 -->
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
                ◆ {{ item.change }}
              </span>

              <span class="comparison-text">
                {{ item.comparison }}
              </span>

              <span
                v-if="item.extraChange"
                class="extra-change"
              >
                ◆ {{ item.extraChange }}
              </span>
            </div>
          </article>
        </section>

        <!-- 中部图表 -->
        <section class="chart-grid">
          <article class="analysis-card trend-card">
            <div class="card-header">
              <h3>投流趋势</h3>

              <button
                type="button"
                class="more-button"
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

          <article class="analysis-card funnel-card">
            <div class="card-header">
              <h3>转化漏斗</h3>

              <button
                type="button"
                class="more-button"
              >
                <el-icon>
                  <MoreFilled />
                </el-icon>
              </button>
            </div>

            <div
              ref="funnelChartRef"
              class="funnel-chart"
            />
          </article>
        </section>

        <!-- 底部排行 -->
        <section class="ranking-grid">
          <!-- 投放计划 -->
          <article class="analysis-card ranking-card">
            <div class="card-header">
              <h3>计划投放TOP5</h3>

              <button
                type="button"
                class="more-button"
              >
                <el-icon>
                  <MoreFilled />
                </el-icon>
              </button>
            </div>

            <div class="ranking-table">
              <div class="ranking-header">
                <span>计划名称</span>
                <span>消耗</span>
                <span>转化率</span>
                <span>ROI</span>
              </div>

              <div
                v-for="(
                  campaign,
                  index
                ) in campaignRanking"
                :key="campaign.name"
                class="ranking-row"
              >
                <div class="ranking-name">
                  <span class="ranking-number">
                    {{ index + 1 }}
                  </span>

                  <strong>
                    {{ campaign.name }}
                  </strong>
                </div>

                <span>
                  {{ campaign.spend }}
                </span>

                <span>
                  {{
                    campaign.conversionRate
                  }}
                </span>

                <span class="roi-value">
                  {{ campaign.roi }}
                </span>
              </div>
            </div>
          </article>

          <!-- 素材排行 -->
          <article class="analysis-card ranking-card creative-card">
            <div class="card-header">
              <h3>投放素材TOP5</h3>

              <button
                type="button"
                class="more-button"
              >
                <el-icon>
                  <MoreFilled />
                </el-icon>
              </button>
            </div>

            <div class="creative-table">
              <div class="creative-header">
                <span>素材信息</span>
                <span>播放量</span>
                <span>转化率</span>
                <span>订单</span>
                <span>ROI</span>
              </div>

              <div
                v-for="creative in creativeRanking"
                :key="creative.name"
                class="creative-row"
              >
                <div class="creative-information">
                  <div class="creative-image">
                    <img
                      v-if="creative.imageUrl"
                      :src="creative.imageUrl"
                      :alt="creative.name"
                    />

                    <el-icon v-else>
                      <Picture />
                    </el-icon>
                  </div>

                  <div class="creative-copy">
                    <strong>
                      {{ creative.name }}
                    </strong>

                    <span>
                      {{ creative.product }}
                    </span>
                  </div>
                </div>

                <span>
                  {{ creative.spend }}
                </span>

                <span>
                  {{
                    creative.conversionRate
                  }}
                </span>

                <span>
                  {{ creative.orders }}
                </span>

                <span class="roi-value">
                  {{ creative.roi }}
                </span>
              </div>
            </div>
          </article>
        </section>
      </template>

      <!-- 后续分析标签占位 -->
      <section
        v-else
        class="tab-placeholder"
      >
        <div class="placeholder-number">
          {{
            activeTab === 'product'
              ? 'P'
              : 'U'
          }}
        </div>

        <h3>
          {{
            activeTab === 'product'
              ? '商品分析'
              : '用户分析'
          }}
        </h3>

        <p>
          页面结构已经预留，后续接入对应统计接口。
        </p>

        <el-button
          type="primary"
          @click="activeTab = 'traffic'"
        >
          返回投流分析
        </el-button>
      </section>
    </section>
  </div>
</template>


<style scoped>
.traffic-page {
  width: 100%;
  min-width: 0;
  color: var(--app-text-primary);
}

.traffic-panel {
  min-height: calc(100vh - 88px);
  overflow: hidden;
  background:
    linear-gradient(
      145deg,
      rgba(255, 255, 255, 0.012),
      transparent 55%
    ),
    #0f141e;
  border: 1px solid #202736;
  border-radius: 7px;
  box-shadow:
    0 10px 28px rgba(0, 0, 0, 0.15);
}


/* ==============================
   顶部标签
================================ */

.page-header {
  display: flex;
  min-height: 57px;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: #10151f;
  border-bottom: 1px solid #202736;
}

.analysis-tabs {
  display: flex;
  height: 57px;
  align-items: stretch;
  gap: 22px;
}

.analysis-tab {
  position: relative;
  padding: 0 5px;
  color: #70798a;
  font-size: 10px;
  cursor: pointer;
  background: transparent;
  border: 0;
}

.analysis-tab:hover {
  color: #aaa0e8;
}

.analysis-tab.active {
  color: #e8e4ff;
}

.analysis-tab.active::after {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 2px;
  background:
    linear-gradient(
      90deg,
      #765bff,
      #997fff
    );
  border-radius: 2px 2px 0 0;
  content: "";
}

.date-picker.el-date-editor {
  width: 220px !important;
  flex: 0 0 220px;
}

.date-picker :deep(
  .el-range-editor.el-input__wrapper
) {
  height: 31px;
  padding: 0 10px;
  background: #0c111a;
  border-radius: 5px;
  box-shadow:
    0 0 0 1px #262e3e inset;
}

.date-picker :deep(.el-range-input) {
  width: 75px;
  color: #9098a8;
  font-size: 8px;
  background: transparent;
}

.date-picker :deep(.el-range-separator),
.date-picker :deep(.el-input__icon) {
  color: #596273;
  font-size: 9px;
}


/* ==============================
   指标卡
================================ */

.metric-grid {
  display: grid;
  grid-template-columns:
    repeat(5, minmax(0, 1fr));
  gap: 10px;
  padding: 12px 12px 0;
}

.metric-card {
  display: flex;
  height: 82px;
  min-width: 0;
  flex-direction: column;
  justify-content: center;
  padding: 11px 13px;
  background:
    linear-gradient(
      145deg,
      rgba(255, 255, 255, 0.018),
      transparent 65%
    ),
    #151a25;
  border: 1px solid #202736;
  border-radius: 6px;
}

.metric-label {
  color: #8991a1;
  font-size: 8px;
}

.metric-value {
  margin-top: 5px;
  color: #f2f3f7;
  font-size: 21px;
  font-weight: 500;
  line-height: 25px;
}

.metric-change {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 4px;
  overflow: hidden;
  font-size: 7px;
  white-space: nowrap;
}

.change-value.success {
  color: #40ce98;
}

.change-value.danger {
  color: #ef756f;
}

.comparison-text {
  color: #596273;
}

.extra-change {
  color: #4ac99a;
}


/* ==============================
   公共卡片
================================ */

.analysis-card {
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
}

.card-header {
  display: flex;
  min-height: 33px;
  align-items: center;
  justify-content: space-between;
  padding: 0 12px;
}

.card-header h3 {
  margin: 0;
  color: #e1e4eb;
  font-size: 9px;
  font-weight: 600;
}

.more-button {
  display: flex;
  width: 22px;
  height: 22px;
  align-items: center;
  justify-content: center;
  padding: 0;
  color: #596273;
  cursor: pointer;
  background: transparent;
  border: 0;
  border-radius: 4px;
}

.more-button:hover {
  color: #a69aff;
  background:
    rgba(118, 91, 255, 0.08);
}


/* ==============================
   中部图表
================================ */

.chart-grid {
  display: grid;
  grid-template-columns:
    minmax(0, 1.55fr)
    minmax(310px, 1fr);
  gap: 10px;
  padding: 10px 12px 0;
}

.trend-card,
.funnel-card {
  height: 238px;
}

.trend-chart,
.funnel-chart {
  width: 100%;
  height: 198px;
}


/* ==============================
   底部排行
================================ */

.ranking-grid {
  display: grid;
  grid-template-columns:
    minmax(310px, 0.9fr)
    minmax(0, 1.35fr);
  gap: 10px;
  padding: 10px 12px 12px;
}

.ranking-card {
  height: 192px;
}

.ranking-table,
.creative-table {
  padding: 0 12px;
}

.ranking-header,
.ranking-row {
  display: grid;
  grid-template-columns:
    minmax(145px, 1.6fr)
    0.7fr
    0.7fr
    0.55fr;
  align-items: center;
}

.creative-header,
.creative-row {
  display: grid;
  grid-template-columns:
    minmax(210px, 1.8fr)
    0.75fr
    0.65fr
    0.55fr
    0.5fr;
  align-items: center;
}

.ranking-header,
.creative-header {
  min-height: 30px;
  color: #697284;
  font-size: 7px;
  border-bottom:
    1px solid rgba(255, 255, 255, 0.04);
}

.ranking-row,
.creative-row {
  min-height: 28px;
  color: #adb4c1;
  font-size: 8px;
  border-bottom:
    1px solid rgba(255, 255, 255, 0.032);
}

.ranking-row:last-child,
.creative-row:last-child {
  border-bottom: 0;
}

.ranking-name {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 7px;
}

.ranking-number {
  display: inline-flex;
  width: 15px;
  height: 15px;
  flex: 0 0 15px;
  align-items: center;
  justify-content: center;
  color: #8e7cf2;
  font-size: 7px;
  background:
    rgba(118, 91, 255, 0.1);
  border-radius: 4px;
}

.ranking-name strong {
  overflow: hidden;
  color: #c7ccd5;
  font-size: 8px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.roi-value {
  color: #55d6a2;
}


/* ==============================
   素材信息
================================ */

.creative-information {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 8px;
}

.creative-image {
  display: flex;
  width: 31px;
  height: 31px;
  flex: 0 0 31px;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  color: #806be4;
  font-size: 15px;
  background:
    linear-gradient(
      135deg,
      #30394a,
      #191f2b
    );
  border: 1px solid #30394a;
  border-radius: 5px;
}

.creative-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.creative-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.creative-copy strong {
  overflow: hidden;
  color: #d0d4dc;
  font-size: 8px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.creative-copy span {
  margin-top: 2px;
  overflow: hidden;
  color: #626b7c;
  font-size: 7px;
  text-overflow: ellipsis;
  white-space: nowrap;
}


/* ==============================
   标签占位
================================ */

.tab-placeholder {
  display: flex;
  min-height: 545px;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.placeholder-number {
  display: flex;
  width: 54px;
  height: 54px;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 17px;
  font-weight: 600;
  background:
    linear-gradient(
      135deg,
      #8067ff,
      #6044dd
    );
  border-radius: 50%;
}

.tab-placeholder h3 {
  margin: 14px 0 0;
  color: #dfe2e9;
  font-size: 13px;
}

.tab-placeholder p {
  margin: 7px 0 0;
  color: #687184;
  font-size: 8px;
}

.tab-placeholder :deep(.el-button) {
  margin-top: 18px;
  background: #765bff;
  border-color: #765bff;
}


/* ==============================
   窄屏适配
================================ */

@media (max-width: 1150px) {
  .metric-grid {
    gap: 7px;
  }

  .metric-card {
    padding-right: 9px;
    padding-left: 9px;
  }

  .metric-value {
    font-size: 18px;
  }

  .chart-grid {
    grid-template-columns:
      minmax(0, 1.4fr)
      minmax(280px, 1fr);
  }

  .ranking-grid {
    grid-template-columns:
      minmax(280px, 0.9fr)
      minmax(0, 1.25fr);
  }
}
</style>