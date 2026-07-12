<script setup>
import {
  reactive,
  watch,
} from 'vue'

import {
  Plus,
  Refresh,
  Search,
} from '@element-plus/icons-vue'

import {
  KNOWLEDGE_CATEGORY_OPTIONS,
  KNOWLEDGE_STATUS_OPTIONS,
} from '../../constants/knowledge.js'


const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      keyword: '',
      category: '',
      status: '',
      product_id: null,
      is_featured: null,
    }),
  },

  productList: {
    type: Array,
    default: () => [],
  },

  loading: {
    type: Boolean,
    default: false,
  },
})


const emit = defineEmits([
  'update:modelValue',
  'search',
  'reset',
  'create',
  'refresh',
])


const localFilters = reactive({
  keyword: '',
  category: '',
  status: '',
  product_id: null,
  is_featured: null,
})


function applyModelValue(value) {
  Object.assign(localFilters, {
    keyword:
      value?.keyword || '',

    category:
      value?.category || '',

    status:
      value?.status || '',

    product_id:
      value?.product_id ?? null,

    is_featured:
      value?.is_featured ?? null,
  })
}


function getFilterData() {
  return {
    keyword:
      localFilters.keyword,

    category:
      localFilters.category,

    status:
      localFilters.status,

    product_id:
      localFilters.product_id,

    is_featured:
      localFilters.is_featured,
  }
}


function syncModelValue() {
  emit(
    'update:modelValue',
    getFilterData(),
  )
}


function handleSearch() {
  syncModelValue()

  emit(
    'search',
    getFilterData(),
  )
}


function handleReset() {
  Object.assign(localFilters, {
    keyword: '',
    category: '',
    status: '',
    product_id: null,
    is_featured: null,
  })

  syncModelValue()

  emit(
    'reset',
    getFilterData(),
  )
}


function handleCreate() {
  emit('create')
}


function handleRefresh() {
  emit('refresh')
}


watch(
  () => props.modelValue,
  (value) => {
    applyModelValue(value)
  },
  {
    immediate: true,
    deep: true,
  },
)
</script>


<template>
  <div class="knowledge-toolbar">
    <!-- 筛选区域 -->
    <div class="filter-section">
      <div
        class="
          filter-control
          keyword-control
        "
      >
        <span class="filter-label">
          关键词
        </span>

        <el-input
          v-model="localFilters.keyword"
          clearable
          placeholder="搜索标题、摘要或正文"
          @keyup.enter="handleSearch"
        />
      </div>

      <div class="filter-control">
        <span class="filter-label">
          分类
        </span>

        <el-select
          v-model="localFilters.category"
          clearable
          placeholder="全部分类"
        >
          <el-option
            v-for="category in KNOWLEDGE_CATEGORY_OPTIONS"
            :key="category"
            :label="category"
            :value="category"
          />
        </el-select>
      </div>

      <div class="filter-control">
        <span class="filter-label">
          状态
        </span>

        <el-select
          v-model="localFilters.status"
          clearable
          placeholder="全部状态"
        >
          <el-option
            v-for="status in KNOWLEDGE_STATUS_OPTIONS"
            :key="status"
            :label="status"
            :value="status"
          />
        </el-select>
      </div>

      <div
        v-if="productList.length"
        class="filter-control product-control"
      >
        <span class="filter-label">
          商品
        </span>

        <el-select
          v-model="localFilters.product_id"
          clearable
          filterable
          placeholder="全部商品"
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
      </div>

      <div class="filter-control featured-control">
        <span class="filter-label">
          精选
        </span>

        <el-select
          v-model="localFilters.is_featured"
          clearable
          placeholder="全部知识"
        >
          <el-option
            label="精选知识"
            :value="true"
          />

          <el-option
            label="普通知识"
            :value="false"
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

    <!-- 操作区域 -->
    <div class="action-section">
      <el-button
        type="primary"
        :icon="Plus"
        class="create-button"
        @click="handleCreate"
      >
        新增知识
      </el-button>

      <el-button
        :icon="Refresh"
        :loading="loading"
        class="refresh-button"
        @click="handleRefresh"
      >
        刷新
      </el-button>
    </div>
  </div>
</template>


<style scoped>
.knowledge-toolbar {
  width: 100%;
}

/* 筛选区域 */

.filter-section {
  display: flex;
  min-height: 72px;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  background:
    var(
      --app-card-bg,
      #111621
    );
  border-bottom:
    1px solid
    var(
      --app-border,
      #202736
    );
}

.filter-control {
  display: flex;
  width: 190px;
  min-width: 0;
  align-items: center;
  gap: 8px;
}

.keyword-control {
  width: 275px;
}

.product-control {
  width: 220px;
}

.featured-control {
  width: 180px;
}

.filter-label {
  flex: 0 0 auto;
  color:
    var(
      --app-text-secondary,
      #a4abb8
    );
  font-size: 9px;
}

.filter-control :deep(.el-input),
.filter-control :deep(.el-select) {
  flex: 1;
  min-width: 0;
}

.filter-control
  :deep(.el-input__wrapper),
.filter-control
  :deep(.el-select__wrapper) {
  min-height: 32px;
  background:
    var(
      --app-input-bg,
      #0b1019
    );
  box-shadow:
    0 0 0 1px
    var(
      --app-border-light,
      #242b39
    )
    inset;
}

.filter-control
  :deep(.el-input__wrapper:hover),
.filter-control
  :deep(.el-select__wrapper:hover) {
  box-shadow:
    0 0 0 1px
    #3b4354
    inset;
}

.filter-control
  :deep(.el-input__wrapper.is-focus),
.filter-control
  :deep(.el-select__wrapper.is-focused) {
  box-shadow:
    0 0 0 1px
    var(
      --app-primary,
      #765bff
    )
    inset;
}

.filter-control
  :deep(.el-input__inner),
.filter-control
  :deep(.el-select__selected-item),
.filter-control
  :deep(.el-select__placeholder) {
  font-size: 9px;
}

.filter-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.filter-actions :deep(.el-button) {
  height: 32px;
  margin: 0;
  padding: 0 15px;
  font-size: 9px;
  border-radius: 5px;
}

.filter-actions
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

/* 操作区域 */

.action-section {
  display: flex;
  min-height: 54px;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  border-bottom:
    1px solid
    var(
      --app-border,
      #202736
    );
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
  border-color:
    #765bff !important;
}

.refresh-button {
  color: #929aaa !important;
  background:
    #151a25 !important;
  border-color:
    #303747 !important;
}

/* 响应式 */

@media (max-width: 1500px) {
  .filter-section {
    flex-wrap: wrap;
  }

  .filter-actions {
    margin-left: 0;
  }
}

@media (max-width: 900px) {
  .filter-control,
  .keyword-control,
  .product-control,
  .featured-control {
    width: calc(50% - 6px);
  }

  .filter-actions {
    width: 100%;
  }
}

@media (max-width: 620px) {
  .filter-control,
  .keyword-control,
  .product-control,
  .featured-control {
    width: 100%;
  }

  .filter-actions {
    justify-content: flex-end;
  }
}
</style>