<script setup>
import {
  computed,
  nextTick,
  onMounted,
  reactive,
  ref,
  watch,
} from 'vue'

import {
  ElMessage,
} from 'element-plus'

import {
  Delete,
  Edit,
  Plus,
  Refresh,
  Search,
  VideoCamera,
  VideoPlay,
} from '@element-plus/icons-vue'

import {
  createVideoTaskApi,
  deleteVideoTaskApi,
  getVideoTaskListApi,
  updateVideoTaskApi,
} from '../api/videoTasks.js'

import {
  getProductListApi,
} from '../api/products.js'

import {
  getScriptListApi,
} from '../api/scripts.js'

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

const FILTER_DEFAULTS = {
  keyword: '',
  product_id: null,
  status: '',
}

const VIDEO_FORM_DEFAULTS = {
  product_id: null,
  script_id: null,
  title: '',
  platform: '抖音',
  assignee: '未分配',
  status: '待制作',
  duration_seconds: 30,
  resolution: '1080P',
  cover_url: '',
  video_url: '',
  notes: '',
  published_at: null,
}

const STATUS_CLASS_MAP = {
  待制作: 'waiting',
  制作中: 'processing',
  待审核: 'reviewing',
  已完成: 'completed',
  已发布: 'published',
  已驳回: 'rejected',
}

/* ==============================
   页面状态
================================ */

const submitting = ref(false)

const dialogVisible = ref(false)
const dialogMode = ref('create')
const editingTaskId = ref(null)
const formRef = ref(null)

const {
  list: videoTaskList,
  loading,
  load: loadVideoTaskData,
} = useAsyncList(
  getVideoTaskListApi,
  {
    errorMessage:
      '视频任务列表加载失败',
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

const {
  list: scriptList,
  load: loadScriptData,
} = useAsyncList(
  getScriptListApi,
  {
    errorMessage:
      '脚本列表加载失败',
  },
)

/* ==============================
   查询条件
================================ */

const filterForm = reactive({
  ...FILTER_DEFAULTS,
})

const appliedFilters = reactive({
  ...FILTER_DEFAULTS,
})

/* ==============================
   视频任务表单
================================ */

const videoForm = reactive({
  ...VIDEO_FORM_DEFAULTS,
})

const formRules = {
  product_id: [
    {
      required: true,
      message: '请选择关联商品',
      trigger: 'change',
    },
  ],

  script_id: [
    {
      required: true,
      message: '请选择关联脚本',
      trigger: 'change',
    },
  ],

  title: [
    {
      required: true,
      message: '请输入视频任务名称',
      trigger: 'blur',
    },
    {
      min: 1,
      max: 200,
      message:
        '任务名称长度为1到200个字符',
      trigger: 'blur',
    },
  ],

  platform: [
    {
      required: true,
      message: '请选择发布平台',
      trigger: 'change',
    },
  ],

  assignee: [
    {
      required: true,
      message: '请输入负责人',
      trigger: 'blur',
    },
  ],

  status: [
    {
      required: true,
      message: '请选择任务状态',
      trigger: 'change',
    },
  ],

  duration_seconds: [
    {
      required: true,
      message: '请输入视频时长',
      trigger: 'change',
    },
  ],

  resolution: [
    {
      required: true,
      message: '请选择视频分辨率',
      trigger: 'change',
    },
  ],
}

/* ==============================
   固定选项
================================ */

const platformOptions = [
  '抖音',
  '快手',
  '小红书',
  '视频号',
  'B站',
]

const statusOptions = [
  '待制作',
  '制作中',
  '待审核',
  '已完成',
  '已发布',
  '已驳回',
]

const resolutionOptions = [
  '720P',
  '1080P',
  '2K',
  '4K',
]

/* ==============================
   计算属性
================================ */

const dialogTitle = computed(() => {
  return dialogMode.value === 'create'
    ? '新增视频任务'
    : '编辑视频任务'
})

const availableScriptList =
  computed(() => {
    if (!videoForm.product_id) {
      return []
    }

    return scriptList.value.filter(
      (script) =>
        Number(script.product_id) ===
        Number(
          videoForm.product_id,
        ),
    )
  })

const filteredVideoTaskList =
  computed(() => {
    const keyword =
      appliedFilters.keyword
        .trim()
        .toLowerCase()

    return videoTaskList.value.filter(
      (task) => {
        const matchesProduct =
          !appliedFilters.product_id ||
          Number(task.product_id) ===
            Number(
              appliedFilters.product_id,
            )

        const matchesStatus =
          !appliedFilters.status ||
          task.status ===
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
          task.title,
          task.assignee,
          task.platform,
          task.resolution,
          task.notes,
          getProductName(
            task.product_id,
          ),
          getScriptName(
            task.script_id,
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
  pageList:
    paginatedVideoTaskList,
  resetPage,
  changePageSize,
} = usePagination(
  filteredVideoTaskList,
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

function getScriptName(scriptId) {
  const script =
    scriptList.value.find(
      (item) =>
        Number(item.id) ===
        Number(scriptId),
    )

  if (script?.title) {
    return script.title
  }

  if (
    scriptId === null ||
    scriptId === undefined ||
    scriptId === ''
  ) {
    return '未关联脚本'
  }

  return `脚本 ID：${scriptId}`
}

function formatDuration(seconds) {
  const totalSeconds =
    Math.max(
      0,
      Math.floor(
        Number(seconds || 0),
      ),
    )

  const minutes =
    Math.floor(
      totalSeconds / 60,
    )

  const remainingSeconds =
    totalSeconds % 60

  if (minutes <= 0) {
    return `${remainingSeconds}秒`
  }

  if (remainingSeconds === 0) {
    return `${minutes}分`
  }

  return (
    `${minutes}分` +
    `${remainingSeconds}秒`
  )
}

function getStatusClass(status) {
  return (
    STATUS_CLASS_MAP[status] ||
    'waiting'
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

async function loadScripts() {
  try {
    return await loadScriptData()
  } catch {
    return []
  }
}

async function loadVideoTasks() {
  try {
    return await loadVideoTaskData()
  } catch {
    return []
  }
}

/* ==============================
   查询
================================ */

function handleSearch() {
  Object.assign(
    appliedFilters,
    filterForm,
  )

  resetPage()
}

function handleReset() {
  Object.assign(
    filterForm,
    FILTER_DEFAULTS,
  )

  Object.assign(
    appliedFilters,
    FILTER_DEFAULTS,
  )

  resetPage()
}

function handlePageSizeChange(size) {
  changePageSize(size)
}

/* ==============================
   表单处理
================================ */

function resetVideoForm() {
  editingTaskId.value = null

  Object.assign(
    videoForm,
    VIDEO_FORM_DEFAULTS,
  )

  formRef.value
    ?.clearValidate()
}

function fillVideoForm(task) {
  Object.assign(videoForm, {
    product_id:
      task.product_id ?? null,

    script_id:
      task.script_id ?? null,

    title:
      task.title || '',

    platform:
      task.platform || '抖音',

    assignee:
      task.assignee || '未分配',

    status:
      task.status || '待制作',

    duration_seconds:
      Number(
        task.duration_seconds ||
          30,
      ),

    resolution:
      task.resolution || '1080P',

    cover_url:
      task.cover_url || '',

    video_url:
      task.video_url || '',

    notes:
      task.notes || '',

    published_at:
      task.published_at || null,
  })
}

function buildVideoTaskPayload() {
  return {
    product_id:
      Number(
        videoForm.product_id,
      ),

    script_id:
      Number(
        videoForm.script_id,
      ),

    title:
      videoForm.title.trim(),

    platform:
      videoForm.platform,

    assignee:
      videoForm.assignee
        .trim(),

    status:
      videoForm.status,

    duration_seconds:
      Number(
        videoForm.duration_seconds,
      ),

    resolution:
      videoForm.resolution,

    cover_url:
      videoForm.cover_url
        .trim() || null,

    video_url:
      videoForm.video_url
        .trim() || null,

    notes:
      videoForm.notes
        .trim() || null,

    published_at:
      videoForm.published_at ||
      null,
  }
}

/* ==============================
   新增与编辑
================================ */

async function openCreateDialog() {
  dialogMode.value = 'create'

  resetVideoForm()

  dialogVisible.value = true

  await nextTick()

  formRef.value
    ?.clearValidate()
}

async function openEditDialog(task) {
  dialogMode.value = 'edit'

  editingTaskId.value =
    task.id

  fillVideoForm(task)

  dialogVisible.value = true

  await nextTick()

  formRef.value
    ?.clearValidate()
}

/* ==============================
   保存任务
================================ */

async function submitVideoTask() {
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
    buildVideoTaskPayload()

  try {
    if (
      dialogMode.value ===
      'create'
    ) {
      await createVideoTaskApi(
        submitData,
      )

      ElMessage.success(
        '视频任务创建成功',
      )
    } else {
      await updateVideoTaskApi(
        editingTaskId.value,
        submitData,
      )

      ElMessage.success(
        '视频任务修改成功',
      )
    }

    dialogVisible.value = false

    await loadVideoTasks()
  } catch (error) {
    ElMessage.error(
      getApiErrorMessage(
        error,
        '视频任务保存失败',
      ),
    )
  } finally {
    submitting.value = false
  }
}

/* ==============================
   删除任务
================================ */

async function handleDelete(task) {
  try {
    const confirmed =
      await confirmDelete(
        task.title,
        {
          title:
            '删除视频任务',
          prefix:
            '确定删除视频任务',
        },
      )

    if (!confirmed) {
      return
    }

    await deleteVideoTaskApi(
      task.id,
    )

    ElMessage.success(
      '视频任务删除成功',
    )

    await loadVideoTasks()
  } catch (error) {
    ElMessage.error(
      getApiErrorMessage(
        error,
        '视频任务删除失败',
      ),
    )
  }
}

/* ==============================
   视频预览
================================ */

function previewVideo(task) {
  if (!task.video_url) {
    ElMessage.warning(
      '当前任务还没有视频地址',
    )

    return
  }

  const previewWindow =
    window.open(
      task.video_url,
      '_blank',
      'noopener,noreferrer',
    )

  if (previewWindow) {
    previewWindow.opener = null
  }
}

function handleImageError(event) {
  const imageElement =
    event?.target

  if (imageElement) {
    imageElement.style.display =
      'none'
  }
}

/* ==============================
   关联数据监听
================================ */

watch(
  () => videoForm.product_id,
  () => {
    const selectedScript =
      scriptList.value.find(
        (script) =>
          Number(script.id) ===
          Number(
            videoForm.script_id,
          ),
      )

    if (
      selectedScript &&
      Number(
        selectedScript.product_id,
      ) !==
        Number(
          videoForm.product_id,
        )
    ) {
      videoForm.script_id = null
    }
  },
)

watch(
  () => videoForm.script_id,
  () => {
    const script =
      scriptList.value.find(
        (item) =>
          Number(item.id) ===
          Number(
            videoForm.script_id,
          ),
      )

    if (
      dialogMode.value !==
        'create' ||
      !script
    ) {
      return
    }

    videoForm.duration_seconds =
      Number(
        script.duration_seconds ||
          30,
      )

    if (
      !videoForm.title.trim()
    ) {
      videoForm.title =
        `${script.title}视频任务`
    }

    videoForm.platform =
      script.platform ||
      videoForm.platform
  },
)

/* ==============================
   生命周期
================================ */

onMounted(async () => {
  await Promise.all([
    loadProducts(),
    loadScripts(),
    loadVideoTasks(),
  ])
})
</script>

<template>
  <div class="video-page">
    <section class="video-panel">
      <!-- 查询区域 -->
      <div class="filter-section">
        <div class="filter-control keyword-control">
          <span class="filter-label">
            任务名称
          </span>

          <el-input
            v-model="filterForm.keyword"
            clearable
            placeholder="请输入任务名称"
            @keyup.enter="handleSearch"
          />
        </div>

        <div class="filter-control">
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

        <div class="filter-control">
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
          新增视频任务
        </el-button>

        <el-button
          :icon="Refresh"
          :loading="loading"
          class="refresh-button"
          @click="loadVideoTasks"
        >
          刷新
        </el-button>
      </div>

      <!-- 表格 -->
      <div class="table-wrapper">
        <el-table
          v-loading="loading"
          :data="paginatedVideoTaskList"
          row-key="id"
          class="video-table"
        >
          <el-table-column
            label="视频任务"
            min-width="270"
          >
            <template #default="{ row }">
              <div class="video-information">
                <div class="video-cover">
                  <img
                    v-if="row.cover_url"
                    :src="row.cover_url"
                    :alt="row.title"
                    @error="handleImageError"
                  />

                  <div class="cover-placeholder">
                    <el-icon>
                      <VideoCamera />
                    </el-icon>
                  </div>
                </div>

                <div class="video-copy">
                  <strong>
                    {{ row.title }}
                  </strong>

                  <span>
                    {{ row.platform }}
                    ·
                    {{ row.resolution }}
                  </span>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column
            label="关联商品"
            min-width="155"
          >
            <template #default="{ row }">
              <span class="secondary-text">
                {{ getProductName(row.product_id) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            label="关联脚本"
            min-width="210"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <span class="secondary-text">
                {{ getScriptName(row.script_id) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            prop="assignee"
            label="负责人"
            width="110"
          />

          <el-table-column
            label="时长"
            width="90"
            align="center"
          >
            <template #default="{ row }">
              {{ formatDuration(row.duration_seconds) }}
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
            label="更新时间"
            width="155"
          >
            <template #default="{ row }">
              <span class="date-value">
                {{ formatDate(row.updated_at) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            label="操作"
            width="205"
            fixed="right"
            align="center"
          >
            <template #default="{ row }">
              <el-button
                type="success"
                link
                :icon="VideoPlay"
                class="operation-button preview-button"
                @click="previewVideo(row)"
              >
                预览
              </el-button>

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
                  <VideoCamera />
                </el-icon>
              </div>

              <strong>
                暂无视频任务
              </strong>

              <span>
                点击“新增视频任务”创建第一条记录
              </span>
            </div>
          </template>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-section">
        <span>
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

    <!-- 新增和编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="760px"
      destroy-on-close
      class="video-dialog"
      @closed="resetVideoForm"
    >
      <el-form
        ref="formRef"
        :model="videoForm"
        :rules="formRules"
        label-position="top"
      >
        <div class="form-grid">
          <el-form-item
            label="关联商品"
            prop="product_id"
          >
            <el-select
              v-model="videoForm.product_id"
              filterable
              placeholder="请选择商品"
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
            label="关联脚本"
            prop="script_id"
          >
            <el-select
              v-model="videoForm.script_id"
              filterable
              placeholder="请选择脚本"
              style="width: 100%"
            >
              <el-option
                v-for="script in availableScriptList"
                :key="script.id"
                :label="script.title"
                :value="script.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item
            label="任务名称"
            prop="title"
            class="full-column"
          >
            <el-input
              v-model="videoForm.title"
              maxlength="200"
              show-word-limit
              placeholder="请输入视频任务名称"
            />
          </el-form-item>

          <el-form-item
            label="发布平台"
            prop="platform"
          >
            <el-select
              v-model="videoForm.platform"
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
            label="负责人"
            prop="assignee"
          >
            <el-input
              v-model="videoForm.assignee"
              maxlength="100"
              placeholder="请输入负责人姓名"
            />
          </el-form-item>

          <el-form-item
            label="任务状态"
            prop="status"
          >
            <el-select
              v-model="videoForm.status"
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
            label="视频分辨率"
            prop="resolution"
          >
            <el-select
              v-model="videoForm.resolution"
              style="width: 100%"
            >
              <el-option
                v-for="resolution in resolutionOptions"
                :key="resolution"
                :label="resolution"
                :value="resolution"
              />
            </el-select>
          </el-form-item>

          <el-form-item
            label="视频时长（秒）"
            prop="duration_seconds"
          >
            <el-input-number
              v-model="videoForm.duration_seconds"
              :min="1"
              :max="3600"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="发布时间">
            <el-date-picker
              v-model="videoForm.published_at"
              type="datetime"
              value-format="YYYY-MM-DDTHH:mm:ss"
              format="YYYY-MM-DD HH:mm:ss"
              placeholder="请选择发布时间"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item
            label="视频封面地址"
            class="full-column"
          >
            <el-input
              v-model="videoForm.cover_url"
              maxlength="500"
              placeholder="请输入视频封面图片地址"
            />
          </el-form-item>

          <el-form-item
            label="视频文件地址"
            class="full-column"
          >
            <el-input
              v-model="videoForm.video_url"
              maxlength="500"
              placeholder="请输入视频文件或在线播放地址"
            />
          </el-form-item>

          <el-form-item
            label="制作说明"
            class="full-column"
          >
            <el-input
              v-model="videoForm.notes"
              type="textarea"
              :rows="4"
              maxlength="5000"
              show-word-limit
              resize="none"
              placeholder="请输入视频制作要求、审核意见或备注"
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
          @click="submitVideoTask"
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
.video-page {
  width: 100%;
  min-width: 0;
}

.video-panel {
  display: flex;
  min-height: calc(100vh - 88px);
  flex-direction: column;
  overflow: hidden;
  background: #0f141e;
  border: 1px solid #202736;
  border-radius: 7px;
}


/* ==============================
   筛选区
================================ */

.filter-section {
  display: flex;
  min-height: 72px;
  align-items: center;
  gap: 17px;
  padding: 14px 16px;
  background: #111621;
  border-bottom: 1px solid #202736;
}

.filter-control {
  display: flex;
  width: 235px;
  align-items: center;
  gap: 9px;
}

.keyword-control {
  width: 285px;
}

.filter-label {
  flex: 0 0 auto;
  color: #a4abb8;
  font-size: 10px;
}

.filter-control :deep(.el-input),
.filter-control :deep(.el-select) {
  flex: 1;
}

.filter-control :deep(.el-input__wrapper),
.filter-control :deep(.el-select__wrapper) {
  min-height: 32px;
  background: #0b1019;
  box-shadow:
    0 0 0 1px #242b39 inset;
}

.filter-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.filter-actions :deep(.el-button) {
  height: 32px;
  margin: 0;
  padding: 0 16px;
  font-size: 9px;
}

.filter-actions :deep(.el-button--primary),
.create-button {
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
   工具栏
================================ */

.toolbar-section {
  display: flex;
  min-height: 54px;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  border-bottom: 1px solid #202736;
}

.create-button,
.refresh-button {
  height: 30px;
  padding: 0 13px;
  font-size: 9px;
  border-radius: 5px;
}

.refresh-button {
  color: #929aaa !important;
  background: #151a25 !important;
  border-color: #303747 !important;
}


/* ==============================
   表格
================================ */

.table-wrapper {
  padding: 8px 16px 0;
}

.video-table {
  width: 100%;
  overflow: hidden;
  border: 1px solid #202736;
  border-radius: 6px;
}

.video-table :deep(
  .el-table__inner-wrapper::before
) {
  display: none;
}

.video-table :deep(th.el-table__cell) {
  height: 43px;
  padding: 0;
  color: #747d8e;
  font-size: 9px;
  font-weight: 500;
  background: #141925;
  border-bottom-color: #202736;
}

.video-table :deep(td.el-table__cell) {
  height: 64px;
  padding: 0;
  color: #aeb5c2;
  font-size: 9px;
  background: #111621;
  border-bottom-color:
    rgba(255, 255, 255, 0.04);
}

.video-table
  :deep(.el-table__row:hover td.el-table__cell) {
  background:
    rgba(118, 91, 255, 0.045);
}

.video-table :deep(.cell) {
  padding-right: 14px;
  padding-left: 14px;
}

.video-table
  :deep(.el-table-fixed-column--right) {
  background: #111621;
}


/* ==============================
   视频信息
================================ */

.video-information {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 11px;
}

.video-cover {
  position: relative;
  display: flex;
  width: 54px;
  height: 38px;
  flex: 0 0 54px;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background:
    linear-gradient(
      135deg,
      #30394a,
      #181e2a
    );
  border: 1px solid #30394a;
  border-radius: 6px;
}

.video-cover img {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  z-index: 1;
  align-items: center;
  justify-content: center;
  color: #826de8;
  font-size: 19px;
}

.video-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.video-copy strong {
  max-width: 200px;
  overflow: hidden;
  color: #e0e3e9;
  font-size: 9px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-copy span,
.secondary-text,
.date-value {
  margin-top: 4px;
  overflow: hidden;
  color: #70798a;
  font-size: 8px;
  text-overflow: ellipsis;
  white-space: nowrap;
}


/* ==============================
   状态
================================ */

.status-badge {
  display: inline-flex;
  height: 20px;
  align-items: center;
  padding: 0 7px;
  font-size: 8px;
  border: 1px solid transparent;
  border-radius: 4px;
}

.status-badge.waiting {
  color: #929bab;
  background: rgba(146, 155, 171, 0.1);
}

.status-badge.processing {
  color: #8e79ff;
  background: rgba(118, 91, 255, 0.12);
}

.status-badge.reviewing {
  color: #e2ae60;
  background: rgba(226, 174, 96, 0.1);
}

.status-badge.completed {
  color: #43c9d5;
  background: rgba(67, 201, 213, 0.1);
}

.status-badge.published {
  color: #55d6a2;
  background: rgba(45, 190, 135, 0.11);
}

.status-badge.rejected {
  color: #ee7a86;
  background: rgba(238, 122, 134, 0.1);
}


/* ==============================
   操作
================================ */

.operation-button {
  margin-left: 0 !important;
  padding: 0 4px;
  font-size: 8px;
}

.preview-button {
  color: #55d6a2 !important;
}


/* ==============================
   分页与空状态
================================ */

.pagination-section {
  display: flex;
  min-height: 62px;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding: 0 17px;
  color: #818999;
  font-size: 8px;
  border-top: 1px solid #202736;
}

.empty-state {
  display: flex;
  min-height: 280px;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.empty-icon {
  display: flex;
  width: 52px;
  height: 52px;
  align-items: center;
  justify-content: center;
  color: #7863df;
  font-size: 24px;
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
}

.empty-state span {
  margin-top: 5px;
  color: #596273;
  font-size: 8px;
}


/* ==============================
   弹窗表单
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

.video-dialog :deep(.el-form-item) {
  margin-bottom: 17px;
}

.video-dialog
  :deep(.el-form-item__label) {
  margin-bottom: 6px;
  color: #aeb5c2;
  font-size: 10px;
}

.video-dialog :deep(.el-input__wrapper),
.video-dialog :deep(.el-select__wrapper),
.video-dialog :deep(.el-input-number) {
  min-height: 34px;
  background: #0d121c;
}

.video-dialog
  :deep(.el-textarea__inner) {
  color: #b8bfcc;
  background: #0d121c;
}


/* ==============================
   响应式
================================ */

@media (max-width: 1150px) {
  .filter-section {
    flex-wrap: wrap;
  }

  .filter-actions {
    margin-left: 0;
  }
}

@media (max-width: 900px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .full-column {
    grid-column: auto;
  }
}
</style>