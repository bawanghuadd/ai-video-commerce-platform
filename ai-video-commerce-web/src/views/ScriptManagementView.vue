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
  Document,
  Edit,
  Plus,
  Refresh,
  Search,
} from '@element-plus/icons-vue'

import {
  createScriptApi,
  deleteScriptApi,
  getScriptListApi,
  updateScriptApi,
} from '../api/scripts.js'

import {
  getProductListApi,
} from '../api/products.js'

import {
  getContentAnalysisListApi,
} from '../api/contentAnalysis.js'

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
  SCRIPT_STATUS_CLASS_MAP as STATUS_CLASS_MAP,
  SCRIPT_STATUS_OPTIONS as statusOptions,
  SCRIPT_TYPE_OPTIONS as scriptTypeOptions,
  SHOT_TYPE_OPTIONS as shotTypeOptions,
} from '../constants/scripts.js'

import { useAuthStore } from '../stores/auth.js'

const authStore = useAuthStore()

const FILTER_DEFAULTS = {
  keyword: '',
  product_id: null,
  status: '',
}

const SCRIPT_FORM_DEFAULTS = {
  product_id: null,
  content_analysis_id: null,
  title: '',
  platform: '抖音',
  script_type: '带货短视频',
  opening_hook: '',
  full_script: '',
  duration_seconds: 30,
  status: '草稿',
}

/* ==============================
   页面状态
================================ */

const submitting = ref(false)

const dialogVisible = ref(false)
const dialogMode = ref('create')
const editingScriptId = ref(null)
const formRef = ref(null)

const {
  list: scriptList,
  loading,
  load: loadScriptData,
} = useAsyncList(
  getScriptListApi,
  {
    errorMessage:
      '脚本列表加载失败',
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
  list: analysisList,
  load: loadAnalysisData,
} = useAsyncList(
  getContentAnalysisListApi,
  {
    errorMessage:
      '内容拆解记录加载失败',
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
   脚本表单
================================ */

const scriptForm = reactive({
  ...SCRIPT_FORM_DEFAULTS,
  scenes: [],
})

const formRules = {
  product_id: [
    {
      required: true,
      message: '请选择关联商品',
      trigger: 'change',
    },
  ],

  title: [
    {
      required: true,
      message: '请输入脚本标题',
      trigger: 'blur',
    },
    {
      min: 1,
      max: 200,
      message:
        '脚本标题长度为1到200个字符',
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

  script_type: [
    {
      required: true,
      message: '请选择脚本类型',
      trigger: 'change',
    },
  ],

  duration_seconds: [
    {
      required: true,
      message: '请输入脚本时长',
      trigger: 'change',
    },
  ],

  status: [
    {
      required: true,
      message: '请选择脚本状态',
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
    ? '新增脚本分镜'
    : '编辑脚本分镜'
})

const availableAnalysisList =
  computed(() => {
    if (!scriptForm.product_id) {
      return []
    }

    return analysisList.value.filter(
      (item) =>
        Number(item.product_id) ===
        Number(
          scriptForm.product_id,
        ),
    )
  })

const filteredScriptList =
  computed(() => {
    const keyword =
      appliedFilters.keyword
        .trim()
        .toLowerCase()

    return scriptList.value.filter(
      (script) => {
        const matchesProduct =
          !appliedFilters.product_id ||
          Number(script.product_id) ===
            Number(
              appliedFilters.product_id,
            )

        const matchesStatus =
          !appliedFilters.status ||
          script.status ===
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
          script.title,
          script.platform,
          script.script_type,
          script.opening_hook,
          script.full_script,
          getProductName(
            script.product_id,
          ),
          getAnalysisTitle(
            script.content_analysis_id,
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
  pageList: paginatedScriptList,
  resetPage,
  changePageSize,
} = usePagination(
  filteredScriptList,
  10,
)

const sceneDurationTotal =
  computed(() => {
    return scriptForm.scenes.reduce(
      (total, scene) => {
        return (
          total +
          Number(
            scene.duration_seconds ||
              0,
          )
        )
      },
      0,
    )
  })

/* ==============================
   基础数据处理
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

function getAnalysisTitle(
  analysisId,
) {
  if (!analysisId) {
    return '未关联拆解记录'
  }

  const analysis =
    analysisList.value.find(
      (item) =>
        Number(item.id) ===
        Number(analysisId),
    )

  return (
    analysis?.content_title ||
    `拆解记录 ID：${analysisId}`
  )
}

function getStatusClass(status) {
  return (
    STATUS_CLASS_MAP[status] ||
    'draft'
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

async function loadAnalyses() {
  try {
    return await loadAnalysisData()
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
   分镜操作
================================ */

function createEmptyScene(
  sceneNumber,
) {
  return {
    scene_number: sceneNumber,
    duration_seconds: 5,
    shot_type: '中景',
    visual_content: '',
    voiceover: '',
    subtitle: '',
    camera_movement: '',
  }
}

function addScene() {
  scriptForm.scenes.push(
    createEmptyScene(
      scriptForm.scenes.length +
        1,
    ),
  )
}

function removeScene(index) {
  scriptForm.scenes.splice(
    index,
    1,
  )

  reindexScenes()
}

function reindexScenes() {
  scriptForm.scenes.forEach(
    (scene, index) => {
      scene.scene_number =
        index + 1
    },
  )
}

function syncScriptDuration() {
  if (
    sceneDurationTotal.value <= 0
  ) {
    ElMessage.warning(
      '请先填写分镜时长',
    )

    return
  }

  scriptForm.duration_seconds =
    sceneDurationTotal.value

  ElMessage.success(
    '脚本总时长已同步',
  )
}

/* ==============================
   表单处理
================================ */

function resetScriptForm() {
  editingScriptId.value = null

  Object.assign(
    scriptForm,
    SCRIPT_FORM_DEFAULTS,
    {
      scenes: [
        createEmptyScene(1),
      ],
    },
  )

  formRef.value
    ?.clearValidate()
}

function normalizeScene(
  scene,
  index,
) {
  return {
    scene_number:
      index + 1,

    duration_seconds:
      Number(
        scene.duration_seconds ||
          5,
      ),

    shot_type:
      scene.shot_type ||
      '中景',

    visual_content:
      scene.visual_content || '',

    voiceover:
      scene.voiceover || '',

    subtitle:
      scene.subtitle || '',

    camera_movement:
      scene.camera_movement || '',
  }
}

function fillScriptForm(script) {
  const scenes =
    Array.isArray(script.scenes) &&
    script.scenes.length > 0
      ? script.scenes.map(
          normalizeScene,
        )
      : [
          createEmptyScene(1),
        ]

  Object.assign(scriptForm, {
    product_id:
      script.product_id ?? null,

    content_analysis_id:
      script.content_analysis_id ??
      null,

    title:
      script.title || '',

    platform:
      script.platform || '抖音',

    script_type:
      script.script_type ||
      '带货短视频',

    opening_hook:
      script.opening_hook || '',

    full_script:
      script.full_script || '',

    duration_seconds:
      Number(
        script.duration_seconds ||
          30,
      ),

    status:
      script.status || '草稿',

    scenes,
  })
}

function buildScriptPayload() {
  return {
    product_id:
      Number(
        scriptForm.product_id,
      ),

    content_analysis_id:
      scriptForm
        .content_analysis_id
        ? Number(
            scriptForm
              .content_analysis_id,
          )
        : null,

    title:
      scriptForm.title.trim(),

    platform:
      scriptForm.platform,

    script_type:
      scriptForm.script_type,

    opening_hook:
      scriptForm.opening_hook
        .trim() || null,

    full_script:
      scriptForm.full_script
        .trim() || null,

    duration_seconds:
      Number(
        scriptForm.duration_seconds,
      ),

    status:
      scriptForm.status,

    scenes:
      scriptForm.scenes.map(
        (scene, index) => ({
          scene_number:
            index + 1,

          duration_seconds:
            Number(
              scene.duration_seconds,
            ),

          shot_type:
            scene.shot_type ||
            null,

          visual_content:
            String(
              scene.visual_content ||
                '',
            ).trim(),

          voiceover:
            String(
              scene.voiceover || '',
            ).trim() || null,

          subtitle:
            String(
              scene.subtitle || '',
            ).trim() || null,

          camera_movement:
            String(
              scene.camera_movement ||
                '',
            ).trim() || null,
        }),
      ),
  }
}

/* ==============================
   新增与编辑
================================ */

async function openCreateDialog() {
  dialogMode.value = 'create'

  resetScriptForm()

  dialogVisible.value = true

  await nextTick()

  formRef.value
    ?.clearValidate()
}

async function openEditDialog(script) {
  dialogMode.value = 'edit'

  editingScriptId.value =
    script.id

  fillScriptForm(script)

  dialogVisible.value = true

  await nextTick()

  formRef.value
    ?.clearValidate()
}

/* ==============================
   保存
================================ */

function validateScenes() {
  if (
    scriptForm.scenes.length === 0
  ) {
    ElMessage.warning(
      '请至少添加一个分镜',
    )

    return false
  }

  const invalidIndex =
    scriptForm.scenes.findIndex(
      (scene) =>
        !String(
          scene.visual_content ||
            '',
        ).trim(),
    )

  if (invalidIndex >= 0) {
    ElMessage.warning(
      `请填写第${invalidIndex + 1}个分镜的画面内容`,
    )

    return false
  }

  const invalidDurationIndex =
    scriptForm.scenes.findIndex(
      (scene) =>
        Number(
          scene.duration_seconds,
        ) <= 0,
    )

  if (
    invalidDurationIndex >= 0
  ) {
    ElMessage.warning(
      `第${invalidDurationIndex + 1}个分镜的时长必须大于0`,
    )

    return false
  }

  return true
}

async function submitScript() {
  if (!formRef.value) {
    return
  }

  try {
    await formRef.value
      .validate()
  } catch {
    return
  }

  if (!validateScenes()) {
    return
  }

  submitting.value = true

  const submitData =
    buildScriptPayload()

  try {
    if (
      dialogMode.value ===
      'create'
    ) {
      await createScriptApi(
        submitData,
      )

      ElMessage.success(
        '脚本分镜创建成功',
      )
    } else {
      await updateScriptApi(
        editingScriptId.value,
        submitData,
      )

      ElMessage.success(
        '脚本分镜修改成功',
      )
    }

    dialogVisible.value = false

    await loadScripts()
  } catch (error) {
    ElMessage.error(
      getApiErrorMessage(
        error,
        '脚本保存失败',
      ),
    )
  } finally {
    submitting.value = false
  }
}

/* ==============================
   删除
================================ */

async function handleDelete(script) {
  try {
    const confirmed =
      await confirmDelete(
        script.title,
        {
          title: '删除脚本',
          prefix:
            '确定删除脚本',
        },
      )

    if (!confirmed) {
      return
    }

    await deleteScriptApi(
      script.id,
    )

    ElMessage.success(
      '脚本删除成功',
    )

    await loadScripts()
  } catch (error) {
    ElMessage.error(
      getApiErrorMessage(
        error,
        '脚本删除失败',
      ),
    )
  }
}

/* ==============================
   监听
================================ */

watch(
  () => scriptForm.product_id,
  () => {
    const selectedAnalysis =
      analysisList.value.find(
        (item) =>
          Number(item.id) ===
          Number(
            scriptForm
              .content_analysis_id,
          ),
      )

    if (
      selectedAnalysis &&
      Number(
        selectedAnalysis.product_id,
      ) !==
        Number(
          scriptForm.product_id,
        )
    ) {
      scriptForm.content_analysis_id =
        null
    }
  },
)

/* ==============================
   生命周期
================================ */

onMounted(async () => {
  await Promise.all([
    loadProducts(),
    loadAnalyses(),
    loadScripts(),
  ])
})
</script>

<template>
  <div class="script-page">
    <section class="script-panel">
      <!-- 筛选区域 -->
      <div class="filter-section">
        <div class="filter-control keyword-control">
          <span class="filter-label">
            脚本标题
          </span>

          <el-input
            v-model="filterForm.keyword"
            clearable
            placeholder="请输入脚本标题"
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
          v-if="authStore.canCreate"
          @click="openCreateDialog"
        >
          新增脚本
        </el-button>

        <el-button
          :icon="Refresh"
          :loading="loading"
          class="refresh-button"
          @click="loadScripts"
        >
          刷新
        </el-button>
      </div>

      <!-- 表格 -->
      <div class="table-wrapper">
        <el-table
          v-loading="loading"
          :data="paginatedScriptList"
          row-key="id"
          class="script-table"
        >
          <el-table-column
            type="expand"
            width="42"
          >
            <template #default="{ row }">
              <div class="scene-expand">
                <div class="expand-heading">
                  <div>
                    <strong>分镜明细</strong>

                    <span>
                      共
                      {{ row.scenes?.length || 0 }}
                      个镜头
                    </span>
                  </div>

                  <span>
                    分镜合计
                    {{
                      (row.scenes || []).reduce(
                        (total, scene) =>
                          total +
                          Number(
                            scene.duration_seconds ||
                              0,
                          ),
                        0,
                      )
                    }}
                    秒
                  </span>
                </div>

                <div class="scene-list">
                  <article
                    v-for="scene in row.scenes"
                    :key="scene.id"
                    class="scene-card"
                  >
                    <div class="scene-number">
                      {{ scene.scene_number }}
                    </div>

                    <div class="scene-content">
                      <div class="scene-meta">
                        <span>
                          {{ scene.shot_type || '未设置景别' }}
                        </span>

                        <span>
                          {{ scene.duration_seconds }}秒
                        </span>

                        <span>
                          {{ scene.camera_movement || '未设置运镜' }}
                        </span>
                      </div>

                      <strong>
                        {{ scene.visual_content }}
                      </strong>

                      <p>
                        口播：
                        {{ scene.voiceover || '-' }}
                      </p>

                      <p>
                        字幕：
                        {{ scene.subtitle || '-' }}
                      </p>
                    </div>
                  </article>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column
            label="脚本信息"
            min-width="260"
          >
            <template #default="{ row }">
              <div class="script-information">
                <div class="script-icon">
                  <el-icon>
                    <Document />
                  </el-icon>
                </div>

                <div class="script-copy">
                  <strong>
                    {{ row.title }}
                  </strong>

                  <span>
                    {{ row.platform }}
                    ·
                    {{ row.script_type }}
                  </span>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column
            label="关联商品"
            min-width="165"
          >
            <template #default="{ row }">
              <span class="secondary-text">
                {{ getProductName(row.product_id) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            label="关联拆解"
            min-width="180"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <span class="secondary-text">
                {{
                  getAnalysisTitle(
                    row.content_analysis_id,
                  )
                }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            label="时长"
            width="85"
            align="center"
          >
            <template #default="{ row }">
              {{ row.duration_seconds }}秒
            </template>
          </el-table-column>

          <el-table-column
            label="分镜数"
            width="85"
            align="center"
          >
            <template #default="{ row }">
              {{ row.scenes?.length || 0 }}
            </template>
          </el-table-column>

          <el-table-column
            label="状态"
            width="100"
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
                v-if="authStore.canUpdate"
                @click="openEditDialog(row)"
              >
                编辑
              </el-button>

              <el-button
                type="danger"
                link
                :icon="Delete"
                class="operation-button"
                v-if="authStore.canDelete"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>

          <template #empty>
            <div class="empty-state">
              <el-icon>
                <Document />
              </el-icon>

              <strong>暂无脚本分镜数据</strong>

              <span>
                点击“新增脚本”创建第一条记录
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

    <!-- 新增与编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="920px"
      destroy-on-close
      class="script-dialog"
      @closed="resetScriptForm"
    >
      <el-form
        ref="formRef"
        :model="scriptForm"
        :rules="formRules"
        label-position="top"
      >
        <div class="base-form-grid">
          <el-form-item
            label="关联商品"
            prop="product_id"
          >
            <el-select
              v-model="scriptForm.product_id"
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

          <el-form-item label="关联拆解记录">
            <el-select
              v-model="scriptForm.content_analysis_id"
              clearable
              filterable
              placeholder="可不选择"
              style="width: 100%"
            >
              <el-option
                v-for="analysis in availableAnalysisList"
                :key="analysis.id"
                :label="analysis.content_title"
                :value="analysis.id"
              />
            </el-select>
          </el-form-item>

          <el-form-item
            label="脚本标题"
            prop="title"
            class="full-column"
          >
            <el-input
              v-model="scriptForm.title"
              maxlength="200"
              show-word-limit
              placeholder="请输入脚本标题"
            />
          </el-form-item>

          <el-form-item
            label="发布平台"
            prop="platform"
          >
            <el-select
              v-model="scriptForm.platform"
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
            label="脚本类型"
            prop="script_type"
          >
            <el-select
              v-model="scriptForm.script_type"
              style="width: 100%"
            >
              <el-option
                v-for="type in scriptTypeOptions"
                :key="type"
                :label="type"
                :value="type"
              />
            </el-select>
          </el-form-item>

          <el-form-item
            label="脚本总时长"
            prop="duration_seconds"
          >
            <el-input-number
              v-model="scriptForm.duration_seconds"
              :min="1"
              :max="3600"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item
            label="脚本状态"
            prop="status"
          >
            <el-select
              v-model="scriptForm.status"
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
            label="开场钩子"
            class="full-column"
          >
            <el-input
              v-model="scriptForm.opening_hook"
              type="textarea"
              :rows="2"
              resize="none"
              placeholder="请输入前三秒开场钩子"
            />
          </el-form-item>

          <el-form-item
            label="完整脚本文案"
            class="full-column"
          >
            <el-input
              v-model="scriptForm.full_script"
              type="textarea"
              :rows="4"
              resize="none"
              placeholder="请输入完整口播或脚本文案"
            />
          </el-form-item>
        </div>

        <div class="scene-editor-heading">
          <div>
            <h3>分镜编辑</h3>

            <span>
              分镜合计 {{ sceneDurationTotal }} 秒
            </span>
          </div>

          <div>
            <el-button
              @click="syncScriptDuration"
            >
              同步总时长
            </el-button>

            <el-button
              type="primary"
              :icon="Plus"
              @click="addScene"
            >
              添加分镜
            </el-button>
          </div>
        </div>

        <div class="scene-editor-list">
          <article
            v-for="(scene, index) in scriptForm.scenes"
            :key="index"
            class="scene-editor-card"
          >
            <div class="scene-card-header">
              <strong>
                分镜 {{ index + 1 }}
              </strong>

              <el-button
                v-if="scriptForm.scenes.length > 1"
                type="danger"
                link
                :icon="Delete"
                @click="removeScene(index)"
              >
                删除
              </el-button>
            </div>

            <div class="scene-form-grid">
              <el-form-item label="景别">
                <el-select
                  v-model="scene.shot_type"
                  allow-create
                  filterable
                  style="width: 100%"
                >
                  <el-option
                    v-for="shotType in shotTypeOptions"
                    :key="shotType"
                    :label="shotType"
                    :value="shotType"
                  />
                </el-select>
              </el-form-item>

              <el-form-item label="时长（秒）">
                <el-input-number
                  v-model="scene.duration_seconds"
                  :min="1"
                  :max="600"
                  style="width: 100%"
                />
              </el-form-item>

              <el-form-item label="运镜方式">
                <el-input
                  v-model="scene.camera_movement"
                  placeholder="例如：缓慢推进"
                />
              </el-form-item>

              <el-form-item
                label="画面内容"
                class="full-column"
                required
              >
                <el-input
                  v-model="scene.visual_content"
                  type="textarea"
                  :rows="2"
                  resize="none"
                  placeholder="描述该分镜中的人物、商品、场景和动作"
                />
              </el-form-item>

              <el-form-item label="口播/旁白">
                <el-input
                  v-model="scene.voiceover"
                  type="textarea"
                  :rows="2"
                  resize="none"
                  placeholder="请输入口播或旁白"
                />
              </el-form-item>

              <el-form-item label="字幕">
                <el-input
                  v-model="scene.subtitle"
                  type="textarea"
                  :rows="2"
                  resize="none"
                  placeholder="请输入画面字幕"
                />
              </el-form-item>
            </div>
          </article>
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
          @click="submitScript"
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
.script-page {
  width: 100%;
  min-width: 0;
}

.script-panel {
  display: flex;
  min-height: calc(100vh - 88px);
  flex-direction: column;
  overflow: hidden;
  background: #0f141e;
  border: 1px solid #202736;
  border-radius: 7px;
}

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

.filter-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.filter-actions :deep(.el-button--primary),
.create-button {
  color: #fff;
  background: linear-gradient(
    135deg,
    #765bff,
    #6348e8
  );
  border-color: #765bff;
}

.toolbar-section {
  display: flex;
  min-height: 54px;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  border-bottom: 1px solid #202736;
}

.table-wrapper {
  padding: 8px 16px 0;
}

.script-table {
  border: 1px solid #202736;
  border-radius: 6px;
}

.script-table :deep(th.el-table__cell) {
  height: 43px;
  color: #747d8e;
  font-size: 9px;
  background: #141925;
}

.script-table :deep(td.el-table__cell) {
  height: 64px;
  color: #aeb5c2;
  font-size: 9px;
  background: #111621;
  border-bottom-color:
    rgba(255, 255, 255, 0.04);
}

.script-information {
  display: flex;
  align-items: center;
  gap: 11px;
}

.script-icon {
  display: flex;
  width: 39px;
  height: 39px;
  flex: 0 0 39px;
  align-items: center;
  justify-content: center;
  color: #826de8;
  font-size: 18px;
  background: #1a2030;
  border: 1px solid #30394a;
  border-radius: 6px;
}

.script-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.script-copy strong {
  max-width: 210px;
  overflow: hidden;
  color: #e0e3e9;
  font-size: 9px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.script-copy span,
.secondary-text,
.date-value {
  margin-top: 3px;
  color: #70798a;
  font-size: 8px;
}

.status-badge {
  display: inline-flex;
  height: 20px;
  align-items: center;
  padding: 0 7px;
  font-size: 8px;
  border-radius: 4px;
}

.status-badge.draft {
  color: #929bab;
  background: rgba(146, 155, 171, 0.1);
}

.status-badge.pending {
  color: #e2ae60;
  background: rgba(226, 174, 96, 0.1);
}

.status-badge.approved {
  color: #55d6a2;
  background: rgba(45, 190, 135, 0.11);
}

.status-badge.rejected {
  color: #ee7a86;
  background: rgba(238, 122, 134, 0.1);
}

.operation-button {
  margin-left: 0 !important;
  padding: 0 5px;
  font-size: 8px;
}

.scene-expand {
  padding: 15px 24px 18px 64px;
  background: #0d121b;
}

.expand-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  color: #778092;
  font-size: 8px;
}

.expand-heading strong {
  color: #d8dbe3;
  font-size: 10px;
}

.expand-heading span {
  margin-left: 8px;
}

.scene-list {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 9px;
  margin-top: 12px;
}

.scene-card {
  display: flex;
  gap: 10px;
  padding: 11px;
  background: #151a25;
  border: 1px solid #242c3a;
  border-radius: 6px;
}

.scene-number {
  display: flex;
  width: 24px;
  height: 24px;
  flex: 0 0 24px;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 9px;
  background: #765bff;
  border-radius: 50%;
}

.scene-content {
  min-width: 0;
}

.scene-meta {
  display: flex;
  gap: 8px;
  color: #8d7ef0;
  font-size: 7px;
}

.scene-content strong {
  display: block;
  margin-top: 5px;
  color: #d3d7df;
  font-size: 9px;
}

.scene-content p {
  margin: 5px 0 0;
  color: #747d8e;
  font-size: 8px;
  line-height: 13px;
}

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
  min-height: 260px;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  color: #7863df;
  font-size: 28px;
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

.base-form-grid,
.scene-form-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 0 16px;
}

.scene-form-grid {
  grid-template-columns:
    repeat(3, minmax(0, 1fr));
}

.full-column {
  grid-column: 1 / -1;
}

.scene-editor-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 8px 0 12px;
  padding-top: 15px;
  border-top: 1px solid #252c3b;
}

.scene-editor-heading h3 {
  margin: 0;
  color: #e3e5eb;
  font-size: 12px;
}

.scene-editor-heading span {
  display: block;
  margin-top: 4px;
  color: #687184;
  font-size: 8px;
}

.scene-editor-card {
  padding: 14px;
  background: #111621;
  border: 1px solid #252d3c;
  border-radius: 7px;
}

.scene-editor-card + .scene-editor-card {
  margin-top: 12px;
}

.scene-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.scene-card-header strong {
  color: #c8cdd6;
  font-size: 10px;
}

@media (max-width: 1150px) {
  .filter-section {
    flex-wrap: wrap;
  }

  .filter-actions {
    margin-left: 0;
  }

  .scene-list {
    grid-template-columns: 1fr;
  }
}
</style>