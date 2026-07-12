<script setup>
import {
  computed,
  onMounted,
  ref,
  watch,
} from 'vue'

import {
  ElMessage,
} from 'element-plus'

import {
  DataAnalysis,
  Goods,
} from '@element-plus/icons-vue'

import {
  getProductListApi,
} from '../api/products'

import {
  createContentAnalysisApi,
  getContentAnalysisListApi,
} from '../api/contentAnalysis'


/* ==============================
   流程步骤
================================ */

const steps = [
  {
    id: 1,
    title: '爆款分析',
    description: '分析爆款内容',
  },
  {
    id: 2,
    title: '脚本生成',
    description: '生成视频脚本',
  },
  {
    id: 3,
    title: '分镜生成',
    description: '生成视频分镜',
  },
  {
    id: 4,
    title: '视频制作',
    description: '创建视频任务',
  },
  {
    id: 5,
    title: '发布投流',
    description: '发布并投放',
  },
]

const currentStep = ref(1)


/* ==============================
   分析维度
================================ */

const analysisDimensions = [
  {
    key: 'high_views',
    label: '播放量高',
  },
  {
    key: 'high_likes',
    label: '点赞数高',
  },
  {
    key: 'high_conversion',
    label: '转化率高',
  },
  {
    key: 'high_comments',
    label: '评论量高',
  },
]

const selectedDimensions = ref([
  'high_views',
  'high_likes',
  'high_conversion',
])


/* ==============================
   页面数据
================================ */

const productList = ref([])
const analysisList = ref([])

const selectedProductId = ref(null)

const loadingProducts = ref(false)
const loadingResults = ref(false)
const analyzing = ref(false)


/* ==============================
   计算属性
================================ */

const selectedProduct = computed(() => {
  return productList.value.find(
    (product) =>
      Number(product.id) ===
      Number(selectedProductId.value),
  )
})

const selectedDimensionLabels = computed(() => {
  return analysisDimensions
    .filter((dimension) =>
      selectedDimensions.value.includes(
        dimension.key,
      ),
    )
    .map((dimension) => dimension.label)
})

const currentStepInfo = computed(() => {
  return steps.find(
    (step) => step.id === currentStep.value,
  )
})


/* ==============================
   接口数据兼容处理
================================ */

function resolveListResponse(response) {
  if (Array.isArray(response)) {
    return response
  }

  /*
   * Axios 拦截器已经返回 response.data 时：
   * {
   *   code: 200,
   *   data: [...]
   * }
   */
  if (Array.isArray(response?.data)) {
    return response.data
  }

  /*
   * Axios 返回完整响应时：
   * {
   *   data: {
   *     code: 200,
   *     data: [...]
   *   }
   * }
   */
  if (Array.isArray(response?.data?.data)) {
    return response.data.data
  }

  return []
}

function getErrorMessage(
  error,
  fallbackMessage,
) {
  const detail =
    error?.response?.data?.detail

  if (typeof detail === 'string') {
    return detail
  }

  if (
    Array.isArray(detail) &&
    detail.length > 0
  ) {
    return (
      detail[0]?.msg ||
      fallbackMessage
    )
  }

  return (
    error?.response?.data?.message ||
    error?.message ||
    fallbackMessage
  )
}


/* ==============================
   加载商品
================================ */

async function loadProducts() {
  loadingProducts.value = true

  try {
    const response =
      await getProductListApi()

    productList.value =
      resolveListResponse(response)

    if (
      !selectedProductId.value &&
      productList.value.length > 0
    ) {
      selectedProductId.value =
        productList.value[0].id
    }
  } catch (error) {
    ElMessage.error(
      getErrorMessage(
        error,
        '商品列表加载失败',
      ),
    )
  } finally {
    loadingProducts.value = false
  }
}


/* ==============================
   加载分析结果
================================ */

async function loadAnalysisResults() {
  if (!selectedProductId.value) {
    analysisList.value = []
    return
  }

  loadingResults.value = true

  try {
    const response =
      await getContentAnalysisListApi({
        product_id:
          selectedProductId.value,
      })

    analysisList.value =
      resolveListResponse(response)
  } catch (error) {
    ElMessage.error(
      getErrorMessage(
        error,
        '分析结果加载失败',
      ),
    )
  } finally {
    loadingResults.value = false
  }
}


/* ==============================
   分析维度切换
================================ */

function toggleDimension(dimensionKey) {
  const index =
    selectedDimensions.value.indexOf(
      dimensionKey,
    )

  if (index >= 0) {
    selectedDimensions.value.splice(
      index,
      1,
    )
  } else {
    selectedDimensions.value.push(
      dimensionKey,
    )
  }
}


/* ==============================
   构建分析内容
================================ */

function createAnalysisPayload() {
  const product = selectedProduct.value

  const sellingPoints =
    product?.selling_points ||
    '产品核心功能、使用体验和价格优势'

  const targetAudience =
    product?.target_audience ||
    '潜在消费用户'

  const dimensions =
    selectedDimensionLabels.value.join('、')

  return {
    product_id: Number(product.id),

    platform: '抖音',

    content_title:
      `${product.product_name}爆款内容分析`,

    source_url: null,

    opening_hook:
      `前三秒直接展示${targetAudience}的核心痛点，并快速露出${product.product_name}。`,

    content_structure:
      '用户痛点引入—商品亮相—核心卖点展示—效果证明—使用场景—购买引导',

    selling_point_expression:
      sellingPoints,

    target_audience:
      targetAudience,

    analysis_result:
      `本次按照${dimensions}等维度进行分析。建议围绕真实使用场景强化前三秒吸引力，突出“${sellingPoints}”，并在结尾加入明确的购买行动引导。`,

    status: '已拆解',
  }
}


/* ==============================
   开始分析
================================ */

async function startAnalysis() {
  if (!selectedProduct.value) {
    ElMessage.warning(
      '请先选择需要分析的商品',
    )
    return
  }

  if (
    selectedDimensions.value.length === 0
  ) {
    ElMessage.warning(
      '请至少选择一个分析维度',
    )
    return
  }

  analyzing.value = true

  try {
    const payload =
      createAnalysisPayload()

    await createContentAnalysisApi(
      payload,
    )

    ElMessage.success(
      '爆款内容分析完成，结果已保存',
    )

    await loadAnalysisResults()
  } catch (error) {
    ElMessage.error(
      getErrorMessage(
        error,
        '内容分析失败',
      ),
    )
  } finally {
    analyzing.value = false
  }
}


/* ==============================
   商品与结果工具方法
================================ */

function getProductById(productId) {
  return productList.value.find(
    (product) =>
      Number(product.id) ===
      Number(productId),
  )
}

function getProductName(productId) {
  return (
    getProductById(productId)
      ?.product_name ||
    `商品 ID：${productId}`
  )
}

function getProductImage(productId) {
  return (
    getProductById(productId)
      ?.image_url ||
    ''
  )
}

function handleImageError(event) {
  event.target.style.display = 'none'
}


/* ==============================
   演示指标
================================ */

/*
 * 当前 content_analyses 表还没有：
 * views、likes、conversion_rate。
 *
 * 这里暂时根据记录 ID 生成稳定演示数值，
 * 后端增加字段后直接替换为接口数据。
 */
function getDemoMetrics(record, index) {
  const seed =
    Number(record.id || index + 1)

  const views =
    87.3 +
    (seed % 6) * 9.8

  const likes =
    3.8 +
    (seed % 5) * 0.7

  const conversion =
    2.1 +
    (seed % 4) * 0.35

  return {
    views:
      `${views.toFixed(1)}w`,

    likes:
      `${likes.toFixed(1)}w`,

    conversion:
      `${conversion.toFixed(1)}%`,
  }
}


/* ==============================
   流程步骤切换
================================ */

function handleStepClick(stepId) {
  currentStep.value = stepId
}


/* ==============================
   监听与生命周期
================================ */

watch(
  selectedProductId,
  () => {
    loadAnalysisResults()
  },
)

onMounted(async () => {
  await loadProducts()
  await loadAnalysisResults()
})
</script>


<template>
  <div class="creation-page">
    <section class="creation-panel">
      <!-- 流程步骤 -->
      <header class="process-header">
        <div
          v-for="(step, index) in steps"
          :key="step.id"
          class="process-step-wrapper"
        >
          <button
            type="button"
            class="process-step"
            :class="{
              active:
                currentStep === step.id,
              completed:
                currentStep > step.id,
            }"
            @click="
              handleStepClick(step.id)
            "
          >
            <span class="step-number">
              {{ step.id }}
            </span>

            <span class="step-title">
              {{ step.title }}
            </span>
          </button>

          <span
            v-if="
              index <
              steps.length - 1
            "
            class="step-connector"
            :class="{
              completed:
                currentStep > step.id,
            }"
          >
            <span class="connector-arrow">
              →
            </span>
          </span>
        </div>
      </header>

      <!-- 第一步：爆款分析 -->
      <div
        v-if="currentStep === 1"
        class="analysis-workspace"
      >
        <!-- 左侧配置 -->
        <aside class="analysis-config">
          <div class="section-heading">
            <h3>爆款内容分析</h3>
          </div>

          <div class="config-content">
            <div class="form-section">
              <label class="form-label">
                商品选择
              </label>

              <el-select
                v-model="selectedProductId"
                v-loading="loadingProducts"
                filterable
                placeholder="请选择商品"
                class="product-select"
              >
                <el-option
                  v-for="product in productList"
                  :key="product.id"
                  :label="product.product_name"
                  :value="product.id"
                >
                  <div class="select-product">
                    <span>
                      {{ product.product_name }}
                    </span>

                    <small>
                      {{ product.category }}
                    </small>
                  </div>
                </el-option>
              </el-select>
            </div>

            <div class="form-section">
              <label class="form-label">
                分析维度
              </label>

              <div class="dimension-grid">
                <button
                  v-for="dimension in analysisDimensions"
                  :key="dimension.key"
                  type="button"
                  class="dimension-button"
                  :class="{
                    selected:
                      selectedDimensions.includes(
                        dimension.key,
                      ),
                  }"
                  @click="
                    toggleDimension(
                      dimension.key,
                    )
                  "
                >
                  {{ dimension.label }}
                </button>
              </div>
            </div>

            <div
              v-if="selectedProduct"
              class="selected-summary"
            >
              <span>当前商品</span>

              <strong>
                {{
                  selectedProduct.product_name
                }}
              </strong>

              <p>
                {{
                  selectedProduct.selling_points ||
                  '暂未填写商品卖点'
                }}
              </p>
            </div>

            <el-button
              type="primary"
              :icon="DataAnalysis"
              :loading="analyzing"
              class="analysis-button"
              @click="startAnalysis"
            >
              开始分析
            </el-button>
          </div>
        </aside>

        <!-- 右侧结果 -->
        <main class="analysis-results">
          <div class="section-heading result-heading">
            <div>
              <h3>分析结果</h3>

              <p>
                分析记录将自动保存到内容拆解表
              </p>
            </div>

            <span class="demo-label">
              部分指标为演示数据
            </span>
          </div>

          <div
            v-loading="loadingResults"
            class="result-list"
          >
            <article
              v-for="(record, index) in analysisList.slice(0, 3)"
              :key="record.id"
              class="result-card"
            >
              <div class="result-image">
                <img
                  v-if="
                    getProductImage(
                      record.product_id,
                    )
                  "
                  :src="
                    getProductImage(
                      record.product_id,
                    )
                  "
                  :alt="
                    getProductName(
                      record.product_id,
                    )
                  "
                  @error="handleImageError"
                />

                <div class="result-placeholder">
                  <el-icon>
                    <Goods />
                  </el-icon>
                </div>
              </div>

              <div class="result-main">
                <div class="result-title-row">
                  <div>
                    <h4>
                      {{
                        record.content_title
                      }}
                    </h4>

                    <span>
                      {{
                        getProductName(
                          record.product_id,
                        )
                      }}
                      ·
                      {{
                        record.platform
                      }}
                    </span>
                  </div>

                  <span class="result-status">
                    {{ record.status }}
                  </span>
                </div>

                <div class="metric-row">
                  <div class="metric-item">
                    <span>播放量</span>

                    <strong>
                      {{
                        getDemoMetrics(
                          record,
                          index,
                        ).views
                      }}
                    </strong>
                  </div>

                  <div class="metric-item">
                    <span>点赞量</span>

                    <strong>
                      {{
                        getDemoMetrics(
                          record,
                          index,
                        ).likes
                      }}
                    </strong>
                  </div>

                  <div class="metric-item">
                    <span>转化率</span>

                    <strong>
                      {{
                        getDemoMetrics(
                          record,
                          index,
                        ).conversion
                      }}
                    </strong>
                  </div>
                </div>

                <p class="analysis-summary">
                  {{
                    record.analysis_result ||
                    record.opening_hook ||
                    '暂无分析结论'
                  }}
                </p>
              </div>
            </article>

            <div
              v-if="
                !loadingResults &&
                analysisList.length === 0
              "
              class="empty-results"
            >
              <div class="empty-result-icon">
                <el-icon>
                  <DataAnalysis />
                </el-icon>
              </div>

              <strong>
                暂无分析结果
              </strong>

              <p>
                选择商品和分析维度后，点击“开始分析”
              </p>
            </div>
          </div>
        </main>
      </div>

      <!-- 后续步骤占位 -->
      <div
        v-else
        class="stage-placeholder"
      >
        <div class="stage-icon">
          {{ currentStep }}
        </div>

        <h3>
          {{ currentStepInfo.title }}
        </h3>

        <p>
          {{ currentStepInfo.description }}
        </p>

        <span>
          当前先完成爆款分析，后续将接入对应的数据表和接口。
        </span>

        <el-button
          type="primary"
          @click="currentStep = 1"
        >
          返回爆款分析
        </el-button>
      </div>
    </section>
  </div>
</template>


<style scoped>
.creation-page {
  width: 100%;
  min-width: 0;
  color: var(--app-text-primary);
}

.creation-panel {
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
   流程步骤
================================ */

.process-header {
  display: flex;
  min-height: 58px;
  align-items: center;
  padding: 0 22px;
  background: #10151f;
  border-bottom: 1px solid #202736;
}

.process-step-wrapper {
  display: flex;
  flex: 1;
  align-items: center;
}

.process-step-wrapper:last-child {
  flex: 0 0 auto;
}

.process-step {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  gap: 8px;
  padding: 5px 7px;
  color: #788191;
  cursor: pointer;
  background: transparent;
  border: 0;
  border-radius: 5px;
}

.process-step:hover {
  color: #b9adff;
  background: rgba(118, 91, 255, 0.06);
}

.step-number {
  display: inline-flex;
  width: 21px;
  height: 21px;
  align-items: center;
  justify-content: center;
  color: #d6d9e1;
  font-size: 9px;
  font-weight: 600;
  background: #3a4150;
  border-radius: 50%;
}

.step-title {
  font-size: 9px;
  font-weight: 500;
  white-space: nowrap;
}

.process-step.active {
  color: #e7e3ff;
}

.process-step.active .step-number {
  color: #ffffff;
  background:
    linear-gradient(
      135deg,
      #8269ff,
      #674be7
    );
  box-shadow:
    0 0 11px rgba(118, 91, 255, 0.35);
}

.process-step.completed {
  color: #9f91f1;
}

.process-step.completed .step-number {
  color: #ffffff;
  background: #6047cd;
}

.step-connector {
  position: relative;
  flex: 1;
  height: 1px;
  margin: 0 8px;
  background: #272e3d;
}

.connector-arrow {
  position: absolute;
  top: -7px;
  right: -2px;
  color: #343c4d;
  font-size: 10px;
}

.step-connector.completed {
  background:
    rgba(118, 91, 255, 0.55);
}

.step-connector.completed .connector-arrow {
  color: #7862e6;
}


/* ==============================
   工作区域
================================ */

.analysis-workspace {
  display: grid;
  grid-template-columns:
    minmax(235px, 0.78fr)
    minmax(0, 2.15fr);
  min-height: 545px;
}

.analysis-config {
  min-width: 0;
  background:
    linear-gradient(
      180deg,
      rgba(118, 91, 255, 0.018),
      transparent 55%
    ),
    #111621;
  border-right: 1px solid #202736;
}

.analysis-results {
  min-width: 0;
  background: #0f141e;
}

.section-heading {
  display: flex;
  min-height: 49px;
  align-items: center;
  justify-content: space-between;
  padding: 0 17px;
  border-bottom: 1px solid #202736;
}

.section-heading h3 {
  margin: 0;
  color: #e5e7ed;
  font-size: 10px;
  font-weight: 600;
}

.result-heading p {
  margin: 3px 0 0;
  color: #616a7a;
  font-size: 7px;
}

.demo-label {
  padding: 3px 6px;
  color: #8475d4;
  font-size: 7px;
  background:
    rgba(118, 91, 255, 0.08);
  border:
    1px solid rgba(118, 91, 255, 0.14);
  border-radius: 4px;
}


/* ==============================
   左侧分析配置
================================ */

.config-content {
  padding: 17px;
}

.form-section + .form-section {
  margin-top: 22px;
}

.form-label {
  display: block;
  margin-bottom: 9px;
  color: #9fa6b4;
  font-size: 8px;
}

.product-select {
  width: 100%;
}

.product-select :deep(.el-select__wrapper) {
  min-height: 34px;
  background: #0b1019;
  border-radius: 5px;
  box-shadow:
    0 0 0 1px #30384a inset;
}

.product-select :deep(
  .el-select__wrapper.is-focused
) {
  box-shadow:
    0 0 0 1px #765bff inset,
    0 0 0 3px rgba(118, 91, 255, 0.08);
}

.product-select :deep(
  .el-select__selected-item
),
.product-select :deep(
  .el-select__placeholder
) {
  font-size: 8px;
}

.select-product {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
}

.select-product small {
  color: #687184;
}

.dimension-grid {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.dimension-button {
  height: 31px;
  color: #6d7585;
  font-size: 8px;
  cursor: pointer;
  background: #151a25;
  border: 1px solid #272f3e;
  border-radius: 5px;
  transition:
    color 0.2s ease,
    border-color 0.2s ease,
    background 0.2s ease;
}

.dimension-button:hover {
  color: #b8adf7;
  border-color: #55468b;
}

.dimension-button.selected {
  color: #c1b6ff;
  background:
    rgba(118, 91, 255, 0.11);
  border-color:
    rgba(118, 91, 255, 0.42);
}

.selected-summary {
  margin-top: 22px;
  padding: 12px;
  background:
    rgba(255, 255, 255, 0.018);
  border: 1px solid #242b39;
  border-radius: 6px;
}

.selected-summary span {
  display: block;
  color: #616a7b;
  font-size: 7px;
}

.selected-summary strong {
  display: block;
  margin-top: 5px;
  overflow: hidden;
  color: #d6d9e0;
  font-size: 9px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.selected-summary p {
  margin: 6px 0 0;
  overflow: hidden;
  color: #747d8e;
  font-size: 8px;
  line-height: 14px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.analysis-button {
  width: 100%;
  height: 34px;
  margin-top: 24px;
  color: #ffffff !important;
  font-size: 9px;
  background:
    linear-gradient(
      135deg,
      #765bff,
      #6247e8
    ) !important;
  border-color: #765bff !important;
  border-radius: 5px;
  box-shadow:
    0 5px 15px rgba(118, 91, 255, 0.24);
}

.analysis-button:hover {
  background:
    linear-gradient(
      135deg,
      #866eff,
      #7054ed
    ) !important;
  border-color: #866eff !important;
}


/* ==============================
   右侧分析结果
================================ */

.result-list {
  min-height: 470px;
  padding: 13px;
}

.result-card {
  display: flex;
  min-width: 0;
  padding: 12px;
  background:
    linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.018),
      transparent 65%
    ),
    #151a25;
  border: 1px solid #222a38;
  border-radius: 6px;
}

.result-card + .result-card {
  margin-top: 10px;
}

.result-card:hover {
  border-color: #343d50;
  background:
    linear-gradient(
      135deg,
      rgba(118, 91, 255, 0.035),
      transparent 65%
    ),
    #161b27;
}

.result-image {
  position: relative;
  display: flex;
  width: 66px;
  height: 66px;
  flex: 0 0 66px;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background:
    linear-gradient(
      135deg,
      #30394b,
      #191f2b
    );
  border: 1px solid #323b4c;
  border-radius: 6px;
}

.result-image img {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-placeholder {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #846fe9;
  font-size: 24px;
}

.result-main {
  min-width: 0;
  flex: 1;
  margin-left: 13px;
}

.result-title-row {
  display: flex;
  min-width: 0;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.result-title-row > div {
  min-width: 0;
}

.result-title-row h4 {
  margin: 0;
  overflow: hidden;
  color: #dfe2e9;
  font-size: 9px;
  font-weight: 500;
  line-height: 14px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.result-title-row span {
  display: block;
  margin-top: 3px;
  color: #687184;
  font-size: 7px;
}

.result-status {
  flex: 0 0 auto;
  padding: 3px 6px;
  color: #55d6a2 !important;
  font-size: 7px !important;
  background:
    rgba(45, 190, 135, 0.1);
  border:
    1px solid rgba(45, 190, 135, 0.16);
  border-radius: 4px;
}

.metric-row {
  display: grid;
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.metric-item {
  display: flex;
  flex-direction: column;
}

.metric-item span {
  color: #626b7c;
  font-size: 7px;
}

.metric-item strong {
  margin-top: 3px;
  color: #e6e8ed;
  font-size: 10px;
  font-weight: 500;
}

.analysis-summary {
  margin: 9px 0 0;
  overflow: hidden;
  color: #7d8595;
  font-size: 7px;
  line-height: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}


/* ==============================
   空结果
================================ */

.empty-results {
  display: flex;
  min-height: 390px;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.empty-result-icon {
  display: flex;
  width: 52px;
  height: 52px;
  align-items: center;
  justify-content: center;
  color: #7c66e4;
  font-size: 24px;
  background:
    rgba(118, 91, 255, 0.08);
  border:
    1px solid rgba(118, 91, 255, 0.14);
  border-radius: 13px;
}

.empty-results strong {
  margin-top: 12px;
  color: #aeb5c2;
  font-size: 10px;
  font-weight: 500;
}

.empty-results p {
  margin: 5px 0 0;
  color: #5e6778;
  font-size: 8px;
}


/* ==============================
   后续步骤占位
================================ */

.stage-placeholder {
  display: flex;
  min-height: 545px;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.stage-icon {
  display: flex;
  width: 56px;
  height: 56px;
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
  box-shadow:
    0 0 25px rgba(118, 91, 255, 0.22);
}

.stage-placeholder h3 {
  margin: 15px 0 0;
  color: #dfe2e9;
  font-size: 14px;
}

.stage-placeholder p {
  margin: 7px 0 0;
  color: #8a92a2;
  font-size: 9px;
}

.stage-placeholder span {
  margin-top: 6px;
  color: #596273;
  font-size: 8px;
}

.stage-placeholder :deep(.el-button) {
  margin-top: 20px;
  background: #765bff;
  border-color: #765bff;
}


/* ==============================
   响应式
================================ */

@media (max-width: 1100px) {
  .analysis-workspace {
    grid-template-columns:
      minmax(220px, 0.9fr)
      minmax(0, 1.8fr);
  }

  .dimension-grid {
    grid-template-columns:
      repeat(2, minmax(0, 1fr));
  }

  .step-title {
    font-size: 8px;
  }
}
</style>