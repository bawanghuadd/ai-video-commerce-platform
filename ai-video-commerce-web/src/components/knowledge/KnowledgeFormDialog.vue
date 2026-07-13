<script setup>
import {
  computed,
  nextTick,
  reactive,
  ref,
  watch,
} from 'vue'

import {
  ElMessage,
} from 'element-plus'

import {
  createKnowledgeApi,
  updateKnowledgeApi,
} from '../../api/knowledge.js'

import {
  getApiErrorMessage,
} from '../../utils/apiResponse.js'

import {
  getStoredUser,
} from '../../utils/authStorage.js'

import {
  KNOWLEDGE_CATEGORY_OPTIONS,
  KNOWLEDGE_SOURCE_TYPE_OPTIONS,
  KNOWLEDGE_STATUS_OPTIONS,
} from '../../constants/knowledge.js'


/* ==============================
   Props 和事件
================================ */

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },

  editingItem: {
    type: Object,
    default: null,
  },

  productList: {
    type: Array,
    default: () => [],
  },
})


const emit = defineEmits([
  'update:modelValue',
  'success',
])


/* ==============================
   页面状态
================================ */

const formRef = ref(null)
const submitting = ref(false)


/* ==============================
   双向绑定弹窗显示状态
================================ */

const visible = computed({
  get() {
    return props.modelValue
  },

  set(value) {
    emit(
      'update:modelValue',
      value,
    )
  },
})


/* ==============================
   判断新增或编辑
================================ */

const isEditMode = computed(() => {
  return Boolean(
    props.editingItem?.id,
  )
})


const dialogTitle = computed(() => {
  return isEditMode.value
    ? '编辑知识'
    : '新增知识'
})


const submitButtonText = computed(() => {
  return isEditMode.value
    ? '保存修改'
    : '确认新增'
})


/* ==============================
   表单数据
================================ */

const knowledgeForm = reactive({
  product_id: null,
  title: '',
  category: '爆款开场钩子',
  summary: '',
  content: '',
  tags: [],
  source_type: '手动录入',
  source_id: null,
  status: '草稿',
  is_featured: false,
  usage_count: 0,
  created_by: '系统管理员',
})


/* ==============================
   表单校验
================================ */

const formRules = {
  title: [
    {
      required: true,
      message: '请输入知识标题',
      trigger: 'blur',
    },
    {
      min: 1,
      max: 200,
      message: '知识标题长度为1到200个字符',
      trigger: 'blur',
    },
  ],

  category: [
    {
      required: true,
      message: '请选择知识分类',
      trigger: 'change',
    },
  ],

  content: [
    {
      required: true,
      message: '请输入知识正文',
      trigger: 'blur',
    },
  ],

  source_type: [
    {
      required: true,
      message: '请选择来源类型',
      trigger: 'change',
    },
  ],

  status: [
    {
      required: true,
      message: '请选择知识状态',
      trigger: 'change',
    },
  ],

  created_by: [
    {
      required: true,
      message: '请输入创建人',
      trigger: 'blur',
    },
  ],
}


/* ==============================
   工具函数
================================ */

function getStoredUserName() {
  const user = getStoredUser() || {}

  return (
    user.display_name ||
    user.username ||
    '系统管理员'
  )
}


function normalizeTags(tags) {
  if (!Array.isArray(tags)) {
    return []
  }

  return [
    ...new Set(
      tags
        .map((tag) => {
          return String(tag).trim()
        })
        .filter(Boolean),
    ),
  ]
}


/* ==============================
   初始化新增表单
================================ */

function applyCreateForm() {
  Object.assign(knowledgeForm, {
    product_id: null,
    title: '',
    category: '爆款开场钩子',
    summary: '',
    content: '',
    tags: [],
    source_type: '手动录入',
    source_id: null,
    status: '草稿',
    is_featured: false,
    usage_count: 0,
    created_by: getStoredUserName(),
  })
}


/* ==============================
   初始化编辑表单
================================ */

function applyEditForm(item) {
  Object.assign(knowledgeForm, {
    product_id:
      item?.product_id ?? null,

    title:
      item?.title || '',

    category:
      item?.category ||
      '爆款开场钩子',

    summary:
      item?.summary || '',

    content:
      item?.content || '',

    tags:
      normalizeTags(item?.tags),

    source_type:
      item?.source_type ||
      '手动录入',

    source_id:
      item?.source_id ?? null,

    status:
      item?.status || '草稿',

    is_featured:
      Boolean(item?.is_featured),

    usage_count:
      Number(
        item?.usage_count || 0,
      ),

    created_by:
      item?.created_by ||
      getStoredUserName(),
  })
}


/* ==============================
   根据模式初始化表单
================================ */

async function initializeForm() {
  if (isEditMode.value) {
    applyEditForm(
      props.editingItem,
    )
  } else {
    applyCreateForm()
  }

  await nextTick()

  formRef.value?.clearValidate()
}


/* ==============================
   生成提交数据
================================ */

function buildSubmitData() {
  return {
    product_id:
      knowledgeForm.product_id
        ? Number(
            knowledgeForm.product_id,
          )
        : null,

    title:
      knowledgeForm.title.trim(),

    category:
      knowledgeForm.category,

    summary:
      knowledgeForm.summary.trim() ||
      null,

    content:
      knowledgeForm.content.trim(),

    tags:
      normalizeTags(
        knowledgeForm.tags,
      ),

    source_type:
      knowledgeForm.source_type,

    source_id:
      knowledgeForm.source_id
        ? Number(
            knowledgeForm.source_id,
          )
        : null,

    status:
      knowledgeForm.status,

    is_featured:
      Boolean(
        knowledgeForm.is_featured,
      ),

    usage_count:
      Number(
        knowledgeForm.usage_count || 0,
      ),

    created_by:
      knowledgeForm.created_by.trim(),
  }
}


/* ==============================
   提交表单
================================ */

async function submitForm() {
  if (!formRef.value) {
    return
  }

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true

  const submitData =
    buildSubmitData()

  try {
    let response

    if (isEditMode.value) {
      response =
        await updateKnowledgeApi(
          props.editingItem.id,
          submitData,
        )

      ElMessage.success(
        '知识库条目修改成功',
      )
    } else {
      response =
        await createKnowledgeApi(
          submitData,
        )

      ElMessage.success(
        '知识库条目创建成功',
      )
    }

    emit('success', {
      mode:
        isEditMode.value
          ? 'edit'
          : 'create',

      response,
    })

    visible.value = false
  } catch (error) {
    ElMessage.error(
      getApiErrorMessage(
        error,
        isEditMode.value
          ? '知识库条目修改失败'
          : '知识库条目创建失败',
      ),
    )
  } finally {
    submitting.value = false
  }
}


/* ==============================
   关闭弹窗
================================ */

function closeDialog() {
  if (submitting.value) {
    return
  }

  visible.value = false
}


/* ==============================
   弹窗关闭后清理
================================ */

function handleClosed() {
  formRef.value?.clearValidate()

  applyCreateForm()
}


/* ==============================
   监听弹窗和编辑数据
================================ */

watch(
  [
    () => props.modelValue,
    () => props.editingItem,
  ],
  async ([isVisible]) => {
    if (!isVisible) {
      return
    }

    await initializeForm()
  },
  {
    immediate: true,
    deep: true,
  },
)
</script>


<template>
  <el-dialog
    v-model="visible"
    :title="dialogTitle"
    width="760px"
    destroy-on-close
    class="knowledge-form-dialog"
    :close-on-click-modal="false"
    :close-on-press-escape="!submitting"
    :show-close="!submitting"
    @closed="handleClosed"
  >
    <el-form
      ref="formRef"
      :model="knowledgeForm"
      :rules="formRules"
      label-position="top"
    >
      <div class="form-grid">
        <!-- 标题 -->
        <el-form-item
          label="知识标题"
          prop="title"
          class="full-column"
        >
          <el-input
            v-model="knowledgeForm.title"
            maxlength="200"
            show-word-limit
            clearable
            placeholder="请输入知识标题"
          />
        </el-form-item>

        <!-- 分类 -->
        <el-form-item
          label="知识分类"
          prop="category"
        >
          <el-select
            v-model="knowledgeForm.category"
            filterable
            allow-create
            default-first-option
            placeholder="请选择知识分类"
            style="width: 100%"
          >
            <el-option
              v-for="category in KNOWLEDGE_CATEGORY_OPTIONS"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </el-form-item>

        <!-- 关联商品 -->
        <el-form-item label="关联商品">
          <el-select
            v-model="knowledgeForm.product_id"
            clearable
            filterable
            placeholder="不选择表示通用知识"
            style="width: 100%"
          >
            <el-option
              v-for="product in productList"
              :key="product.id"
              :label="
                product.product_name ||
                product.name ||
                `商品 ${product.id}`
              "
              :value="product.id"
            />
          </el-select>
        </el-form-item>

        <!-- 摘要 -->
        <el-form-item
          label="知识摘要"
          class="full-column"
        >
          <el-input
            v-model="knowledgeForm.summary"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
            resize="none"
            placeholder="简要概括这条知识的核心内容"
          />
        </el-form-item>

        <!-- 正文 -->
        <el-form-item
          label="知识正文"
          prop="content"
          class="full-column"
        >
          <el-input
            v-model="knowledgeForm.content"
            type="textarea"
            :rows="8"
            maxlength="30000"
            show-word-limit
            resize="vertical"
            placeholder="请输入完整知识内容、经验总结或使用方法"
          />
        </el-form-item>

        <!-- 标签 -->
        <el-form-item
          label="知识标签"
          class="full-column"
        >
          <el-select
            v-model="knowledgeForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            collapse-tags
            collapse-tags-tooltip
            placeholder="输入标签后按回车"
            style="width: 100%"
          />
        </el-form-item>

        <!-- 来源类型 -->
        <el-form-item
          label="来源类型"
          prop="source_type"
        >
          <el-select
            v-model="knowledgeForm.source_type"
            placeholder="请选择来源类型"
            style="width: 100%"
          >
            <el-option
              v-for="sourceType in KNOWLEDGE_SOURCE_TYPE_OPTIONS"
              :key="sourceType"
              :label="sourceType"
              :value="sourceType"
            />
          </el-select>
        </el-form-item>

        <!-- 来源记录 -->
        <el-form-item label="来源记录ID">
          <el-input-number
            v-model="knowledgeForm.source_id"
            :min="1"
            :step="1"
            controls-position="right"
            placeholder="可不填写"
            style="width: 100%"
          />
        </el-form-item>

        <!-- 状态 -->
        <el-form-item
          label="知识状态"
          prop="status"
        >
          <el-select
            v-model="knowledgeForm.status"
            placeholder="请选择知识状态"
            style="width: 100%"
          >
            <el-option
              v-for="status in KNOWLEDGE_STATUS_OPTIONS"
              :key="status"
              :label="status"
              :value="status"
            />
          </el-select>
        </el-form-item>

        <!-- 创建人 -->
        <el-form-item
          label="创建人"
          prop="created_by"
        >
          <el-input
            v-model="knowledgeForm.created_by"
            maxlength="100"
            clearable
            placeholder="请输入创建人"
          />
        </el-form-item>

        <!-- 引用次数 -->
        <el-form-item
          v-if="isEditMode"
          label="引用次数"
        >
          <el-input-number
            v-model="knowledgeForm.usage_count"
            :min="0"
            :step="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>

        <!-- 精选 -->
        <el-form-item
          label="精选知识"
          class="
            full-column
            featured-form-item
          "
        >
          <div class="featured-setting">
            <div class="featured-description">
              <strong>设为精选知识</strong>

              <p>
                精选内容会在知识库中获得更明显的展示位置。
              </p>
            </div>

            <el-switch
              v-model="knowledgeForm.is_featured"
              active-text="精选"
              inactive-text="普通"
            />
          </div>
        </el-form-item>
      </div>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button
          :disabled="submitting"
          @click="closeDialog"
        >
          取消
        </el-button>

        <el-button
          type="primary"
          :loading="submitting"
          @click="submitForm"
        >
          {{ submitButtonText }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>


<style scoped>
.form-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 0 16px;
}

.full-column {
  grid-column: 1 / -1;
}

.knowledge-form-dialog
  :deep(.el-form-item) {
  margin-bottom: 17px;
}

.knowledge-form-dialog
  :deep(.el-form-item__label) {
  margin-bottom: 6px;
  color:
    var(
      --app-text-secondary,
      #aeb5c2
    );
  font-size: 10px;
  line-height: 16px;
}

.knowledge-form-dialog
  :deep(.el-input__wrapper),
.knowledge-form-dialog
  :deep(.el-select__wrapper),
.knowledge-form-dialog
  :deep(.el-input-number) {
  min-height: 34px;
  background:
    var(
      --app-input-bg,
      #0d121c
    );
  box-shadow:
    0 0 0 1px
    var(
      --app-border-light,
      #293142
    )
    inset;
}

.knowledge-form-dialog
  :deep(.el-input__wrapper:hover),
.knowledge-form-dialog
  :deep(.el-select__wrapper:hover) {
  box-shadow:
    0 0 0 1px
    #3b4354
    inset;
}

.knowledge-form-dialog
  :deep(.el-input__wrapper.is-focus),
.knowledge-form-dialog
  :deep(.el-select__wrapper.is-focused) {
  box-shadow:
    0 0 0 1px
    var(
      --app-primary,
      #765bff
    )
    inset;
}

.knowledge-form-dialog
  :deep(.el-textarea__inner) {
  color: #b8bfcc;
  background:
    var(
      --app-input-bg,
      #0d121c
    );
  border: none;
  box-shadow:
    0 0 0 1px
    var(
      --app-border-light,
      #293142
    )
    inset;
}

.knowledge-form-dialog
  :deep(.el-textarea__inner:hover) {
  box-shadow:
    0 0 0 1px
    #3b4354
    inset;
}

.knowledge-form-dialog
  :deep(.el-textarea__inner:focus) {
  box-shadow:
    0 0 0 1px
    var(
      --app-primary,
      #765bff
    )
    inset;
}

.knowledge-form-dialog
  :deep(.el-input__inner),
.knowledge-form-dialog
  :deep(.el-select__selected-item),
.knowledge-form-dialog
  :deep(.el-select__placeholder),
.knowledge-form-dialog
  :deep(.el-textarea__inner) {
  font-size: 10px;
}

.featured-form-item {
  margin-top: 2px;
  padding: 11px 13px;
  background:
    var(
      --app-card-bg,
      #111621
    );
  border:
    1px solid
    var(
      --app-border,
      #252d3c
    );
  border-radius: 7px;
}

.featured-setting {
  display: flex;
  width: 100%;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.featured-description {
  min-width: 0;
}

.featured-description strong {
  color: #c7ccd5;
  font-size: 10px;
  font-weight: 500;
}

.featured-description p {
  margin: 4px 0 0;
  color:
    var(
      --app-text-muted,
      #687184
    );
  font-size: 8px;
  line-height: 14px;
}

.featured-setting
  :deep(.el-switch) {
  --el-switch-on-color: #765bff;
  --el-switch-off-color: #303747;

  flex: 0 0 auto;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.dialog-footer :deep(.el-button) {
  min-width: 82px;
  height: 34px;
  margin: 0;
  font-size: 10px;
}

.dialog-footer
  :deep(.el-button--primary) {
  color: #ffffff;
  background:
    linear-gradient(
      135deg,
      #765bff,
      #6348e8
    );
  border-color: #765bff;
}

@media (max-width: 780px) {
  .form-grid {
    grid-template-columns: 1fr;
  }

  .full-column {
    grid-column: auto;
  }

  .featured-setting {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
