<script setup>
import {
  Collection,
  Link,
  Reading,
  Star,
} from '@element-plus/icons-vue'

import AppStatCard from '../components/common/AppStatCard.vue'
import KnowledgeCard from '../components/knowledge/KnowledgeCard.vue'
import KnowledgeDetailDrawer from '../components/knowledge/KnowledgeDetailDrawer.vue'
import KnowledgeFilterBar from '../components/knowledge/KnowledgeFilterBar.vue'
import KnowledgeFormDialog from '../components/knowledge/KnowledgeFormDialog.vue'

import {
  useKnowledgeBase,
} from '../composables/useKnowledgeBase.js'


import { useAuthStore } from '../stores/auth.js'

const authStore = useAuthStore()

/* ==============================
   知识库业务逻辑
================================ */

const {
  loading,
  usingKnowledgeId,

  formVisible,
  detailVisible,

  editingKnowledge,
  selectedKnowledge,

  filters,
  productList,
  pageList,

  currentPage,
  pageSize,
  totalRecords,
  changePageSize,

  publishedCount,
  featuredCount,
  totalUsageCount,

  searchKnowledge,
  resetFilters,
  refreshKnowledge,

  openCreate,
  openEdit,
  openDetail,

  deleteKnowledge,
  useKnowledge,
  handleFormSuccess,
} = useKnowledgeBase()


/* ==============================
   同步筛选条件
================================ */

function handleFilterUpdate(
  nextFilters,
) {
  if (
    !nextFilters ||
    typeof nextFilters !== 'object'
  ) {
    return
  }

  Object.assign(
    filters,
    nextFilters,
  )
}
</script>


<template>
  <div class="knowledge-page">
    <!-- 数据概览 -->
    <section class="summary-grid">
      <AppStatCard
        title="知识总数"
        :value="totalRecords"
        :icon="Collection"
        tone="purple"
      />

      <AppStatCard
        title="已发布"
        :value="publishedCount"
        :icon="Reading"
        tone="green"
      />

      <AppStatCard
        title="精选知识"
        :value="featuredCount"
        :icon="Star"
        tone="orange"
      />

      <AppStatCard
        title="累计引用"
        :value="totalUsageCount"
        :icon="Link"
        tone="cyan"
      />
    </section>

    <!-- 知识库主面板 -->
    <section class="knowledge-panel">
      <!-- 查询和操作栏 -->
      <KnowledgeFilterBar
        :model-value="filters"
        :product-list="productList"
        :loading="loading"
        :can-create="authStore.canCreate"
        @update:model-value="
          handleFilterUpdate
        "
        @search="searchKnowledge"
        @reset="resetFilters"
        @create="openCreate"
        @refresh="refreshKnowledge"
      />

      <!-- 知识卡片列表 -->
      <div
        v-loading="loading"
        class="knowledge-content"
      >
        <div
          v-if="pageList.length > 0"
          class="knowledge-grid"
        >
          <KnowledgeCard
            v-for="item in pageList"
            :key="item.id"
            :item="item"
            :product-list="productList"
            :can-write="authStore.canUpdate"
            :using-knowledge-id="
              usingKnowledgeId
            "
            @view="openDetail"
            @edit="openEdit"
            @delete="deleteKnowledge"
            @use="useKnowledge"
          />
        </div>

        <!-- 空状态 -->
        <div
          v-else-if="!loading"
          class="empty-state"
        >
          <div class="empty-icon">
            <el-icon>
              <Collection />
            </el-icon>
          </div>

          <strong>
            暂无知识库内容
          </strong>

          <p>
            当前查询条件下没有知识记录
          </p>

          <el-button
            type="primary"
            class="empty-create-button"
            v-if="authStore.canCreate"
            @click="openCreate"
          >
            新增知识
          </el-button>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination-section">
        <span class="total-text">
          共 {{ totalRecords }} 条
        </span>

        <el-pagination
          v-model:current-page="
            currentPage
          "
          v-model:page-size="
            pageSize
          "
          background
          layout="
            prev,
            pager,
            next,
            sizes
          "
          :page-sizes="
            [8, 16, 24]
          "
          :total="totalRecords"
          @size-change="
            changePageSize
          "
        />
      </div>
    </section>

    <!-- 新增和编辑弹窗 -->
    <KnowledgeFormDialog
      v-model="formVisible"
      :editing-item="
        editingKnowledge
      "
      :product-list="
        productList
      "
      @success="
        handleFormSuccess
      "
    />

    <!-- 详情抽屉 -->
    <KnowledgeDetailDrawer
      v-model="detailVisible"
      :item="
        selectedKnowledge
      "
      :product-list="
        productList
      "
      :can-write="authStore.canUpdate"
      @edit="openEdit"
      @use="useKnowledge"
    />
  </div>
</template>


<style scoped>
.knowledge-page {
  width: 100%;
  min-width: 0;
  color:
    var(
      --app-text-primary,
      #edf0f5
    );
}

/* ==============================
   统计卡片布局
================================ */

.summary-grid {
  display: grid;
  grid-template-columns:
    repeat(
      4,
      minmax(0, 1fr)
    );
  gap: 10px;
  margin-bottom: 10px;
}

/* ==============================
   主面板
================================ */

.knowledge-panel {
  display: flex;
  min-height:
    calc(100vh - 172px);
  flex-direction: column;
  overflow: hidden;
  background:
    var(
      --app-panel-bg,
      #0f141e
    );
  border:
    1px solid
    var(
      --app-border,
      #202736
    );
  border-radius:
    var(
      --app-radius-md,
      7px
    );
}

/* ==============================
   知识列表
================================ */

.knowledge-content {
  flex: 1;
  min-height: 330px;
  padding: 13px 16px;
}

.knowledge-grid {
  display: grid;
  grid-template-columns:
    repeat(
      4,
      minmax(0, 1fr)
    );
  gap: 11px;
}

/* ==============================
   空状态
================================ */

.empty-state {
  display: flex;
  min-height: 340px;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.empty-icon {
  display: flex;
  width: 54px;
  height: 54px;
  align-items: center;
  justify-content: center;
  color:
    var(
      --app-primary,
      #765bff
    );
  font-size: 25px;
  background:
    rgba(
      118,
      91,
      255,
      0.08
    );
  border:
    1px solid
    rgba(
      118,
      91,
      255,
      0.15
    );
  border-radius: 13px;
}

.empty-state strong {
  margin-top: 13px;
  color:
    var(
      --app-text-secondary,
      #abb2bf
    );
  font-size: 12px;
  font-weight: 500;
}

.empty-state p {
  margin: 6px 0 0;
  color:
    var(
      --app-text-muted,
      #687184
    );
  font-size: 9px;
}

.empty-create-button {
  height: 31px;
  margin-top: 14px;
  padding: 0 15px;
  color: #ffffff !important;
  font-size: 9px;
  background:
    linear-gradient(
      135deg,
      #765bff,
      #6348e8
    ) !important;
  border-color:
    #765bff !important;
}

/* ==============================
   分页
================================ */

.pagination-section {
  display: flex;
  min-height: 60px;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 0 17px;
  border-top:
    1px solid
    var(
      --app-border,
      #202736
    );
}

.total-text {
  flex: 0 0 auto;
  color:
    var(
      --app-text-muted,
      #818999
    );
  font-size: 9px;
}

/* ==============================
   加载状态
================================ */

.knowledge-content
  :deep(.el-loading-mask) {
  background:
    rgba(
      8,
      11,
      18,
      0.68
    );
  backdrop-filter:
    blur(2px);
}

.knowledge-content
  :deep(
    .el-loading-spinner
    .path
  ) {
  stroke:
    var(
      --app-primary,
      #765bff
    );
}

/* ==============================
   响应式
================================ */

@media (
  max-width: 1400px
) {
  .knowledge-grid {
    grid-template-columns:
      repeat(
        3,
        minmax(0, 1fr)
      );
  }
}

@media (
  max-width: 1050px
) {
  .summary-grid,
  .knowledge-grid {
    grid-template-columns:
      repeat(
        2,
        minmax(0, 1fr)
      );
  }
}

@media (
  max-width: 780px
) {
  .summary-grid,
  .knowledge-grid {
    grid-template-columns:
      1fr;
  }

  .pagination-section {
    align-items:
      flex-start;
    flex-direction:
      column;
    padding:
      14px 16px;
  }

  .pagination-section
    :deep(.el-pagination) {
    max-width: 100%;
    overflow-x: auto;
  }
}
</style>