<script setup>
import {
  computed,
  nextTick,
  onMounted,
  reactive,
  ref,
} from 'vue'

import {
  ElMessage,
} from 'element-plus'

import {
  Delete,
  Document,
  Edit,
  Plus,
  Refresh,
  Search,
} from '@element-plus/icons-vue'

import {
  createContentAnalysisApi,
  deleteContentAnalysisApi,
  getContentAnalysisListApi,
  updateContentAnalysisApi,
} from '../api/contentAnalysis.js'

import {
  getProductListApi,
} from '../api/products.js'

import {
  useAsyncList,
} from '../composables/useAsyncList.js'

import {
  usePagination,
} from '../composables/usePagination.js'

import {
  getApiErrorMessage,
} from '../utils/apiResponse.js'

import {
  confirmDelete,
} from '../utils/confirm.js'

import {
  formatDateTime as formatDate,
} from '../utils/date.js'
import {
  PLATFORM_OPTIONS as platformOptions,
} from '../constants/platforms.js'

import {
  CONTENT_ANALYSIS_STATUS_CLASS_MAP as STATUS_CLASS_MAP,
  CONTENT_ANALYSIS_STATUS_OPTIONS as statusOptions,
} from '../constants/contentAnalysis.js'

const FILTER_DEFAULTS = {
  keyword: '',
  product_id: null,
  status: '',
}

const ANALYSIS_FORM_DEFAULTS = {
  product_id: null,
  platform: '抖音',
  content_title: '',
  source_url: '',
  opening_hook: '',
  content_structure: '',
  selling_point_expression: '',
  target_audience: '',
  analysis_result: '',
  status: '待拆解',
}

/* ==============================
   页面状态
================================ */

const submitting = ref(false)

const dialogVisible = ref(false)
const dialogMode = ref('create')
const editingAnalysisId = ref(null)
const formRef = ref(null)

const {
  list: analysisList,
  loading,
  load: loadAnalysisData,
} = useAsyncList(
  getContentAnalysisListApi,
  {
    errorMessage:
      '内容拆解列表加载失败',
  },
)

const {
  list: productList,
  load: loadProductData,
} = useAsyncList(
  getProductListApi,
  {
    errorMessage:
      '商品列表加载失败',
  },
)

/* ==============================
   筛选条件
================================ */

const filterForm = reactive({
  ...FILTER_DEFAULTS,
})

const appliedFilters = reactive({
  ...FILTER_DEFAULTS,
})

/* ==============================
   表单数据
================================ */

const analysisForm = reactive({
  ...ANALYSIS_FORM_DEFAULTS,
})

const formRules = {
  product_id: [
    {
      required: true,
      message: '请选择关联商品',
      trigger: 'change',
    },
  ],

  platform: [
    {
      required: true,
      message: '请选择内容平台',
      trigger: 'change',
    },
  ],

  content_title: [
    {
      required: true,
      message: '请输入内容标题',
      trigger: 'blur',
    },
    {
      min: 1,
      max: 200,
      message:
        '内容标题长度为1到200个字符',
      trigger: 'blur',
    },
  ],

  status: [
    {
      required: true,
      message: '请选择拆解状态',
      trigger: 'change',
    },
  ],
}

/* ==============================
   固定选项
================================ */


/* ==============================
   计算属性
================================ */

const dialogTitle = computed(() => {
  return dialogMode.value === 'create'
    ? '新增内容拆解'
    : '编辑内容拆解'
})

const filteredAnalysisList =
  computed(() => {
    const keyword =
      appliedFilters.keyword
        .trim()
        .toLowerCase()

    return analysisList.value.filter(
      (item) => {
        const matchesProduct =
          !appliedFilters.product_id ||
          Number(item.product_id) ===
            Number(
              appliedFilters.product_id,
            )

        const matchesStatus =
          !appliedFilters.status ||
          item.status ===
            appliedFilters.status

        if (
          !matchesProduct ||
          !matchesStatus
        ) {
          return false
        }

        if (!keyword) {
          return true
        }

        const searchableText = [
          item.content_title,
          item.platform,
          item.opening_hook,
          item.content_structure,
          item.selling_point_expression,
          item.target_audience,
          item.analysis_result,
          getProductName(
            item.product_id,
          ),
        ]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()

        return searchableText.includes(
          keyword,
        )
      },
    )
  })

const {
  currentPage,
  pageSize,
  total: totalRecords,
  pageList: paginatedAnalysisList,
  resetPage,
  changePageSize,
} = usePagination(
  filteredAnalysisList,
  10,
)

/* ==============================
   数据处理
================================ */

function getProductName(productId) {
  const product =
    productList.value.find(
      (item) =>
        Number(item.id) ===
        Number(productId),
    )

  if (product?.product_name) {
    return product.product_name
  }

  if (
    productId === null ||
    productId === undefined ||
    productId === ''
  ) {
    return '未关联商品'
  }

  return `商品 ID：${productId}`
}

function getStatusClass(status) {
  return (
    STATUS_CLASS_MAP[status] ||
    'archived'
  )
}

/* ==============================
   加载数据
================================ */

async function loadProducts() {
  try {
    return await loadProductData()
  } catch {
    return []
  }
}

function buildAnalysisQuery() {
  const params = {}

  if (appliedFilters.product_id) {
    params.product_id =
      appliedFilters.product_id
  }

  if (appliedFilters.status) {
    params.status =
      appliedFilters.status
  }

  return params
}

async function loadAnalysisList() {
  try {
    return await loadAnalysisData(
      buildAnalysisQuery(),
    )
  } catch {
    return []
  }
}

/* ==============================
   查询和重置
================================ */

async function handleSearch() {
  Object.assign(
    appliedFilters,
    filterForm,
  )

  resetPage()

  await loadAnalysisList()
}

async function handleReset() {
  Object.assign(
    filterForm,
    FILTER_DEFAULTS,
  )

  Object.assign(
    appliedFilters,
    FILTER_DEFAULTS,
  )

  resetPage()

  await loadAnalysisList()
}

function handlePageSizeChange(size) {
  changePageSize(size)
}

/* ==============================
   表单处理
================================ */

function resetAnalysisForm() {
  editingAnalysisId.value = null

  Object.assign(
    analysisForm,
    ANALYSIS_FORM_DEFAULTS,
  )

  formRef.value
    ?.clearValidate()
}

function fillAnalysisForm(item) {
  Object.assign(analysisForm, {
    product_id:
      item.product_id ?? null,

    platform:
      item.platform || '抖音',

    content_title:
      item.content_title || '',

    source_url:
      item.source_url || '',

    opening_hook:
      item.opening_hook || '',

    content_structure:
      item.content_structure || '',

    selling_point_expression:
      item.selling_point_expression ||
      '',

    target_audience:
      item.target_audience || '',

    analysis_result:
      item.analysis_result || '',

    status:
      item.status || '待拆解',
  })
}

function buildAnalysisPayload() {
  return {
    product_id:
      Number(
        analysisForm.product_id,
      ),

    platform:
      analysisForm.platform,

    content_title:
      analysisForm.content_title
        .trim(),

    source_url:
      analysisForm.source_url
        .trim() || null,

    opening_hook:
      analysisForm.opening_hook
        .trim() || null,

    content_structure:
      analysisForm.content_structure
        .trim() || null,

    selling_point_expression:
      analysisForm
        .selling_point_expression
        .trim() || null,

    target_audience:
      analysisForm.target_audience
        .trim() || null,

    analysis_result:
      analysisForm.analysis_result
        .trim() || null,

    status:
      analysisForm.status,
  }
}

/* ==============================
   新增和编辑
================================ */

async function openCreateDialog() {
  dialogMode.value = 'create'

  resetAnalysisForm()

  dialogVisible.value = true

  await nextTick()

  formRef.value
    ?.clearValidate()
}

async function openEditDialog(item) {
  dialogMode.value = 'edit'

  editingAnalysisId.value =
    item.id

  fillAnalysisForm(item)

  dialogVisible.value = true

  await nextTick()

  formRef.value
    ?.clearValidate()
}

async function submitAnalysis() {
  if (!formRef.value) {
    return
  }

  try {
    await formRef.value
      .validate()
  } catch {
    return
  }

  submitting.value = true

  const submitData =
    buildAnalysisPayload()

  try {
    if (
      dialogMode.value ===
      'create'
    ) {
      await createContentAnalysisApi(
        submitData,
      )

      ElMessage.success(
        '内容拆解记录创建成功',
      )
    } else {
      await updateContentAnalysisApi(
        editingAnalysisId.value,
        submitData,
      )

      ElMessage.success(
        '内容拆解记录修改成功',
      )
    }

    dialogVisible.value = false

    await loadAnalysisList()
  } catch (error) {
    ElMessage.error(
      getApiErrorMessage(
        error,
        '内容拆解保存失败',
      ),
    )
  } finally {
    submitting.value = false
  }
}

/* ==============================
   删除
================================ */

async function handleDelete(item) {
  try {
    const confirmed =
      await confirmDelete(
        item.content_title,
        {
          title:
            '删除内容拆解',
        },
      )

    if (!confirmed) {
      return
    }

    await deleteContentAnalysisApi(
      item.id,
    )

    ElMessage.success(
      '内容拆解记录删除成功',
    )

    await loadAnalysisList()
  } catch (error) {
    ElMessage.error(
      getApiErrorMessage(
        error,
        '内容拆解删除失败',
      ),
    )
  }
}

/* ==============================
   生命周期
================================ */

onMounted(async () => {
  await Promise.all([
    loadProducts(),
    loadAnalysisList(),
  ])
})
</script>

<template>
  <div class="analysis-page">
    <section class="analysis-panel">
      <!-- 查询区域 -->
      <div class="filter-section">
        <div class="filter-control keyword-control">
          <span class="filter-label">
            内容标题
          </span>

          <el-input
            v-model="filterForm.keyword"
            clearable
            placeholder="请输入标题或关键词"
            @keyup.enter="handleSearch"
          />
        </div>

        <div class="filter-control product-control">
          <span class="filter-label">
            关联商品
          </span>

          <el-select
            v-model="filterForm.product_id"
            clearable
            filterable
            placeholder="请选择商品"
          >
            <el-option
              v-for="product in productList"
              :key="product.id"
              :label="product.product_name"
              :value="product.id"
            />
          </el-select>
        </div>

        <div class="filter-control status-control">
          <span class="filter-label">
            状态
          </span>

          <el-select
            v-model="filterForm.status"
            clearable
            placeholder="请选择状态"
          >
            <el-option
              v-for="status in statusOptions"
              :key="status"
              :label="status"
              :value="status"
            />
          </el-select>
        </div>

        <div class="filter-actions">
          <el-button
            type="primary"
            :icon="Search"
            @click="handleSearch"
          >
            查询
          </el-button>

          <el-button
            :icon="Refresh"
            @click="handleReset"
          >
            重置
          </el-button>
        </div>
      </div>

      <!-- 工具栏 -->
      <div class="toolbar-section">
        <el-button
          type="primary"
          :icon="Plus"
          class="create-button"
          @click="openCreateDialog"
        >
          新增拆解
        </el-button>

        <el-button
          :icon="Refresh"
          :loading="loading"
          class="refresh-button"
          @click="loadAnalysisList"
        >
          刷新
        </el-button>
      </div>

      <!-- 表格 -->
      <div class="table-wrapper">
        <el-table
          v-loading="loading"
          :data="paginatedAnalysisList"
          row-key="id"
          class="analysis-table"
        >
          <el-table-column
            label="内容信息"
            min-width="260"
          >
            <template #default="{ row }">
              <div class="content-information">
                <div class="content-icon">
                  <el-icon>
                    <Document />
                  </el-icon>
                </div>

                <div class="content-copy">
                  <strong>
                    {{ row.content_title }}
                  </strong>

                  <span>
                    {{ row.platform || '未设置平台' }}
                  </span>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column
            label="关联商品"
            min-width="175"
          >
            <template #default="{ row }">
              <span class="product-name">
                {{ getProductName(row.product_id) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            label="开场钩子"
            min-width="235"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <span class="secondary-text">
                {{ row.opening_hook || '-' }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            label="状态"
            width="105"
            align="center"
          >
            <template #default="{ row }">
              <span
                class="status-badge"
                :class="getStatusClass(row.status)"
              >
                {{ row.status }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            label="创建时间"
            width="165"
          >
            <template #default="{ row }">
              <span class="date-value">
                {{ formatDate(row.created_at) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            label="操作"
            width="145"
            fixed="right"
            align="center"
          >
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                :icon="Edit"
                class="operation-button"
                @click="openEditDialog(row)"
              >
                编辑
              </el-button>

              <el-button
                type="danger"
                link
                :icon="Delete"
                class="operation-button"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>

          <template #empty>
            <div class="empty-state">
              <div class="empty-icon">
                <el-icon>
                  <Document />
                </el-icon>
              </div>

              <strong>
                暂无内容拆解数据
              </strong>

              <span>
                点击“新增拆解”创建第一条记录
              </span>
            </div>
          </template>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-section">
        <span class="pagination-total">
          共 {{ totalRecords }} 条
        </span>

        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          background
          layout="prev, pager, next, sizes"
          :page-sizes="[10, 20, 50]"
          :total="totalRecords"
          @size-change="handlePageSizeChange"
        />
      </div>
    </section>

    <!-- 新增与编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="720px"
      destroy-on-close
      class="analysis-dialog"
      @closed="resetAnalysisForm"
    >
      <el-form
        ref="formRef"
        :model="analysisForm"
        :rules="formRules"
        label-position="top"
      >
        <div class="form-grid">
          <el-form-item
            label="关联商品"
            prop="product_id"
          >
            <el-select
              v-model="analysisForm.product_id"
              filterable
              placeholder="请选择关联商品"
              style="width: 100%"
            >
              <el-option
                v-for="product in productList"
                :key="product.id"
                :label="product.product_name"
                :value="product.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item
            label="内容平台"
            prop="platform"
          >
            <el-select
              v-model="analysisForm.platform"
              style="width: 100%"
            >
              <el-option
                v-for="platform in platformOptions"
                :key="platform"
                :label="platform"
                :value="platform"
              />
            </el-select>
          </el-form-item>

          <el-form-item
            label="内容标题"
            prop="content_title"
            class="full-column"
          >
            <el-input
              v-model="analysisForm.content_title"
              maxlength="200"
              show-word-limit
              placeholder="请输入爆款内容标题"
            />
          </el-form-item>

          <el-form-item
            label="内容链接"
            class="full-column"
          >
            <el-input
              v-model="analysisForm.source_url"
              maxlength="500"
              placeholder="请输入原视频或参考内容链接"
            />
          </el-form-item>

          <el-form-item
            label="开场钩子"
            class="full-column"
          >
            <el-input
              v-model="analysisForm.opening_hook"
              type="textarea"
              :rows="3"
              resize="none"
              placeholder="例如：地铁太吵听不清音乐？"
            />
          </el-form-item>

          <el-form-item
            label="内容结构"
            class="full-column"
          >
            <el-input
              v-model="analysisForm.content_structure"
              type="textarea"
              :rows="3"
              resize="none"
              placeholder="例如：痛点引入—产品展示—效果测试—购买引导"
            />
          </el-form-item>

          <el-form-item
            label="卖点表达"
            class="full-column"
          >
            <el-input
              v-model="analysisForm.selling_point_expression"
              type="textarea"
              :rows="3"
              resize="none"
              placeholder="例如：主动降噪、长续航、低延迟"
            />
          </el-form-item>

          <el-form-item label="目标用户">
            <el-input
              v-model="analysisForm.target_audience"
              maxlength="200"
              placeholder="例如：大学生、通勤上班族"
            />
          </el-form-item>

          <el-form-item
            label="拆解状态"
            prop="status"
          >
            <el-select
              v-model="analysisForm.status"
              style="width: 100%"
            >
              <el-option
                v-for="status in statusOptions"
                :key="status"
                :label="status"
                :value="status"
              />
            </el-select>
          </el-form-item>

          <el-form-item
            label="拆解结论"
            class="full-column"
          >
            <el-input
              v-model="analysisForm.analysis_result"
              type="textarea"
              :rows="4"
              resize="none"
              placeholder="填写对该内容的完整拆解结论"
            />
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <el-button
          @click="dialogVisible = false"
        >
          取消
        </el-button>

        <el-button
          type="primary"
          :loading="submitting"
          @click="submitAnalysis"
        >
          {{
            dialogMode === 'create'
              ? '确认新增'
              : '保存修改'
          }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>


<style scoped>
.analysis-page {
  width: 100%;
  min-width: 0;
  color: var(--app-text-primary);
}

.analysis-panel {
  display: flex;
  min-width: 0;
  min-height: calc(100vh - 88px);
  flex-direction: column;
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
   查询区域
================================ */

.filter-section {
  display: flex;
  min-height: 72px;
  align-items: center;
  gap: 17px;
  padding: 14px 16px;
  background: rgba(17, 22, 33, 0.92);
  border-bottom: 1px solid #202736;
}

.filter-control {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 9px;
}

.keyword-control {
  width: 285px;
}

.product-control {
  width: 275px;
}

.status-control {
  width: 220px;
}

.filter-label {
  flex: 0 0 auto;
  color: #a4abb8;
  font-size: 10px;
  white-space: nowrap;
}

.filter-control :deep(.el-input),
.filter-control :deep(.el-select) {
  flex: 1;
  min-width: 0;
}

.filter-control :deep(.el-input__wrapper),
.filter-control :deep(.el-select__wrapper) {
  min-height: 32px;
  background: #0b1019;
  border-radius: 5px;
  box-shadow:
    0 0 0 1px #242b39 inset;
  transition:
    box-shadow 0.2s ease,
    background 0.2s ease;
}

.filter-control :deep(.el-input__wrapper:hover),
.filter-control :deep(.el-select__wrapper:hover) {
  background: #0d121c;
  box-shadow:
    0 0 0 1px #363f52 inset;
}

.filter-control :deep(.el-input__wrapper.is-focus),
.filter-control :deep(.el-select__wrapper.is-focused) {
  background: #0d121c;
  box-shadow:
    0 0 0 1px #765bff inset,
    0 0 0 3px rgba(118, 91, 255, 0.08);
}

.filter-control :deep(.el-input__inner),
.filter-control :deep(.el-select__placeholder),
.filter-control :deep(.el-select__selected-item) {
  color: #abb2bf;
  font-size: 9px;
}

.filter-control :deep(.el-input__inner::placeholder) {
  color: #555e6f;
}

.filter-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.filter-actions :deep(.el-button) {
  height: 32px;
  margin: 0;
  padding: 0 16px;
  font-size: 9px;
  border-radius: 5px;
}

.filter-actions :deep(.el-button--primary) {
  color: #ffffff;
  background:
    linear-gradient(
      135deg,
      #765bff,
      #6348e8
    );
  border-color: #765bff;
  box-shadow:
    0 4px 12px rgba(118, 91, 255, 0.22);
}

.filter-actions :deep(.el-button--primary:hover) {
  background:
    linear-gradient(
      135deg,
      #846cff,
      #7055ef
    );
  border-color: #8b74ff;
}

.filter-actions
  :deep(.el-button:not(.el-button--primary)) {
  color: #9aa2b2;
  background: #151a25;
  border-color: #303747;
}

.filter-actions
  :deep(.el-button:not(.el-button--primary):hover) {
  color: #c4baff;
  background: rgba(118, 91, 255, 0.09);
  border-color: #56468d;
}

/* ==============================
   工具栏
================================ */

.toolbar-section {
  display: flex;
  min-height: 54px;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  background: #10151f;
  border-bottom: 1px solid #202736;
}

.create-button,
.refresh-button {
  height: 30px;
  padding: 0 13px;
  font-size: 9px;
  border-radius: 5px;
}

.create-button {
  color: #ffffff !important;
  background:
    linear-gradient(
      135deg,
      #765bff,
      #6348e8
    ) !important;
  border-color: #765bff !important;
  box-shadow:
    0 4px 12px rgba(118, 91, 255, 0.22);
}

.create-button:hover {
  background:
    linear-gradient(
      135deg,
      #846cff,
      #7055ef
    ) !important;
  border-color: #8b74ff !important;
}

.refresh-button {
  color: #929aaa !important;
  background: #151a25 !important;
  border-color: #303747 !important;
}

.refresh-button:hover {
  color: #c4baff !important;
  background:
    rgba(118, 91, 255, 0.09) !important;
  border-color: #56468d !important;
}

/* ==============================
   表格
================================ */

.table-wrapper {
  padding: 8px 16px 0;
}

.analysis-table {
  width: 100%;
  overflow: hidden;
  border: 1px solid #202736;
  border-radius: 6px;
}

.analysis-table :deep(
  .el-table__inner-wrapper::before
) {
  display: none;
}

.analysis-table :deep(th.el-table__cell) {
  height: 43px;
  padding: 0;
  color: #747d8e;
  font-size: 9px;
  font-weight: 500;
  background: #141925;
  border-bottom-color: #202736;
}

.analysis-table :deep(td.el-table__cell) {
  height: 64px;
  padding: 0;
  color: #aeb5c2;
  font-size: 9px;
  background: #111621;
  border-bottom-color:
    rgba(255, 255, 255, 0.038);
}

.analysis-table
  :deep(.el-table__row:hover td.el-table__cell) {
  background:
    rgba(118, 91, 255, 0.045);
}

.analysis-table :deep(.cell) {
  padding-right: 17px;
  padding-left: 17px;
}

.analysis-table
  :deep(.el-table-fixed-column--right) {
  background: #111621;
}

.analysis-table
  :deep(th.el-table-fixed-column--right) {
  background: #141925;
}

/* ==============================
   内容信息
================================ */

.content-information {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 11px;
}

.content-icon {
  display: flex;
  width: 39px;
  height: 39px;
  flex: 0 0 39px;
  align-items: center;
  justify-content: center;
  color: #826de8;
  font-size: 18px;
  background:
    radial-gradient(
      circle at 50% 35%,
      rgba(118, 91, 255, 0.14),
      transparent 70%
    ),
    #1a2030;
  border: 1px solid #30394a;
  border-radius: 6px;
}

.content-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.content-copy strong {
  max-width: 210px;
  overflow: hidden;
  color: #e0e3e9;
  font-size: 9px;
  font-weight: 500;
  line-height: 15px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.content-copy span {
  margin-top: 3px;
  color: #7567ba;
  font-size: 8px;
}

.product-name {
  display: block;
  overflow: hidden;
  color: #c7cbd4;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.secondary-text {
  display: block;
  overflow: hidden;
  color: #8f97a6;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.date-value {
  color: #a0a7b4;
  font-size: 8px;
}

/* ==============================
   状态标签
================================ */

.status-badge {
  display: inline-flex;
  height: 20px;
  align-items: center;
  justify-content: center;
  padding: 0 7px;
  font-size: 8px;
  border: 1px solid transparent;
  border-radius: 4px;
}

.status-badge.pending {
  color: #e2ae60;
  background: rgba(226, 174, 96, 0.1);
  border-color: rgba(226, 174, 96, 0.17);
}

.status-badge.processing {
  color: #8c76ff;
  background: rgba(118, 91, 255, 0.11);
  border-color: rgba(118, 91, 255, 0.18);
}

.status-badge.completed {
  color: #55d6a2;
  background: rgba(45, 190, 135, 0.11);
  border-color: rgba(45, 190, 135, 0.17);
}

.status-badge.archived {
  color: #929bab;
  background: rgba(146, 155, 171, 0.09);
  border-color: rgba(146, 155, 171, 0.15);
}

/* ==============================
   操作按钮
================================ */

.operation-button {
  height: 22px;
  margin-left: 0 !important;
  padding: 0 5px;
  font-size: 8px;
  border-radius: 4px;
}

.operation-button.el-button--primary {
  color: #8b75ff !important;
}

.operation-button.el-button--primary:hover {
  color: #b2a5ff !important;
  background:
    rgba(118, 91, 255, 0.09) !important;
}

.operation-button.el-button--danger {
  color: #d9687e !important;
}

.operation-button.el-button--danger:hover {
  color: #f08b9e !important;
  background:
    rgba(217, 104, 126, 0.08) !important;
}

/* ==============================
   分页
================================ */

.pagination-section {
  display: flex;
  min-height: 62px;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding: 0 17px;
  border-top: 1px solid #202736;
}

.pagination-total {
  color: #818999;
  font-size: 8px;
}

.pagination-section :deep(.el-pagination) {
  --el-pagination-button-bg-color: #151b27;
  --el-pagination-hover-color: #ab9eff;
  --el-pagination-text-color: #808899;

  font-size: 8px;
}

.pagination-section :deep(.btn-prev),
.pagination-section :deep(.btn-next),
.pagination-section :deep(.el-pager li) {
  min-width: 25px;
  height: 25px;
  color: #808899;
  font-size: 8px;
  line-height: 25px;
  background: #171c27;
  border: 1px solid #262d3c;
  border-radius: 4px;
}

.pagination-section
  :deep(.el-pager li.is-active) {
  color: #ffffff !important;
  background:
    linear-gradient(
      135deg,
      #765bff,
      #6348e8
    ) !important;
  border-color: #765bff !important;
}

/* ==============================
   空状态
================================ */

.empty-state {
  display: flex;
  min-height: 280px;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.empty-icon {
  display: flex;
  width: 50px;
  height: 50px;
  align-items: center;
  justify-content: center;
  color: #7863df;
  font-size: 23px;
  background:
    rgba(118, 91, 255, 0.08);
  border:
    1px solid rgba(118, 91, 255, 0.14);
  border-radius: 12px;
}

.empty-state strong {
  margin-top: 12px;
  color: #abb2bf;
  font-size: 11px;
  font-weight: 500;
}

.empty-state span {
  margin-top: 5px;
  color: #596273;
  font-size: 8px;
}

/* ==============================
   弹窗
================================ */

.form-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 0 16px;
}

.full-column {
  grid-column: 1 / -1;
}

.analysis-dialog :deep(.el-form-item) {
  margin-bottom: 17px;
}

.analysis-dialog
  :deep(.el-form-item__label) {
  margin-bottom: 6px;
  color: #aeb5c2;
  font-size: 10px;
  line-height: 15px;
}

.analysis-dialog :deep(.el-input__wrapper),
.analysis-dialog :deep(.el-select__wrapper) {
  min-height: 34px;
  background: #0d121c;
  border-radius: 5px;
}

.analysis-dialog
  :deep(.el-input__wrapper.is-focus),
.analysis-dialog
  :deep(.el-select__wrapper.is-focused) {
  box-shadow:
    0 0 0 1px #765bff inset,
    0 0 0 3px rgba(118, 91, 255, 0.08);
}

.analysis-dialog
  :deep(.el-textarea__inner) {
  color: #b8bfcc;
  background: #0d121c;
}

.analysis-dialog
  :deep(.el-textarea__inner:focus) {
  box-shadow:
    0 0 0 1px #765bff inset,
    0 0 0 3px rgba(118, 91, 255, 0.08);
}

/* ==============================
   窄屏适配
================================ */

@media (max-width: 1250px) {
  .filter-section {
    flex-wrap: wrap;
  }

  .filter-actions {
    margin-left: 0;
  }

  .keyword-control,
  .product-control,
  .status-control {
    width: calc(33.333% - 12px);
  }
}

@media (max-width: 980px) {
  .keyword-control,
  .product-control,
  .status-control {
    width: calc(50% - 9px);
  }

  .filter-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .full-column {
    grid-column: auto;
  }
}
</style>