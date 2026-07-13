<script setup>
import { computed } from 'vue'

import {
  Collection,
  Link,
  Star,
  User,
} from '@element-plus/icons-vue'

import {
  getKnowledgeStatusClass,
} from '../../constants/knowledge.js'

import {
  formatDateTime,
} from '../../utils/date.js'


const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false,
  },

  item: {
    type: Object,
    default: null,
  },

  canWrite: {
    type: Boolean,
    default: false,
  },

  productList: {
    type: Array,
    default: () => [],
  },
})


const emit = defineEmits([
  'update:modelValue',
  'edit',
  'use',
])


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


const knowledgeTags = computed(() => {
  return Array.isArray(props.item?.tags)
    ? props.item.tags
    : []
})


function getProductName(productId) {
  if (!productId) {
    return '通用知识'
  }

  const product = props.productList.find(
    (item) => {
      return (
        Number(item.id) ===
        Number(productId)
      )
    },
  )

  return (
    product?.product_name ||
    product?.name ||
    `商品 ID：${productId}`
  )
}


function closeDrawer() {
  visible.value = false
}


function handleEdit() {
  if (!props.item) {
    return
  }

  emit('edit', props.item)
  closeDrawer()
}


function handleUse() {
  if (!props.item) {
    return
  }

  emit('use', props.item)
}
</script>


<template>
  <el-drawer
    v-model="visible"
    title="知识详情"
    size="520px"
    destroy-on-close
    class="knowledge-detail-drawer"
  >
    <div
      v-if="item"
      class="detail-content"
    >
      <!-- 状态 -->
      <div class="detail-heading">
        <span
          class="status-badge"
          :class="
            getKnowledgeStatusClass(
              item.status,
            )
          "
        >
          {{ item.status || '草稿' }}
        </span>

        <span
          v-if="item.is_featured"
          class="featured-badge"
        >
          <el-icon>
            <Star />
          </el-icon>

          精选知识
        </span>
      </div>

      <!-- 标题 -->
      <h2 class="detail-title">
        {{ item.title || '未命名知识' }}
      </h2>

      <!-- 摘要 -->
      <p class="detail-summary">
        {{
          item.summary ||
          '暂无知识摘要'
        }}
      </p>

      <!-- 基础信息 -->
      <div class="detail-meta">
        <div class="meta-item">
          <span class="meta-label">
            分类
          </span>

          <strong>
            {{ item.category || '-' }}
          </strong>
        </div>

        <div class="meta-item">
          <span class="meta-label">
            关联商品
          </span>

          <strong>
            {{
              getProductName(
                item.product_id,
              )
            }}
          </strong>
        </div>

        <div class="meta-item">
          <span class="meta-label">
            来源类型
          </span>

          <strong>
            {{
              item.source_type ||
              '手动录入'
            }}
          </strong>
        </div>

        <div class="meta-item">
          <span class="meta-label">
            来源记录
          </span>

          <strong>
            {{
              item.source_id
                ? `ID ${item.source_id}`
                : '-'
            }}
          </strong>
        </div>

        <div class="meta-item">
          <span class="meta-label">
            创建人
          </span>

          <strong>
            {{
              item.created_by ||
              '系统管理员'
            }}
          </strong>
        </div>

        <div class="meta-item">
          <span class="meta-label">
            引用次数
          </span>

          <strong>
            {{ item.usage_count || 0 }} 次
          </strong>
        </div>

        <div class="meta-item full-meta">
          <span class="meta-label">
            创建时间
          </span>

          <strong>
            {{
              formatDateTime(
                item.created_at,
              )
            }}
          </strong>
        </div>

        <div class="meta-item full-meta">
          <span class="meta-label">
            更新时间
          </span>

          <strong>
            {{
              formatDateTime(
                item.updated_at,
              )
            }}
          </strong>
        </div>
      </div>

      <!-- 标签 -->
      <section class="detail-section">
        <div class="section-title">
          <el-icon>
            <Collection />
          </el-icon>

          <span>知识标签</span>
        </div>

        <div
          v-if="knowledgeTags.length"
          class="detail-tags"
        >
          <span
            v-for="tag in knowledgeTags"
            :key="tag"
          >
            {{ tag }}
          </span>
        </div>

        <p
          v-else
          class="empty-copy"
        >
          暂无标签
        </p>
      </section>

      <!-- 正文 -->
      <section class="detail-section">
        <div class="section-title">
          <el-icon>
            <Collection />
          </el-icon>

          <span>知识正文</span>
        </div>

        <div class="detail-body">
          {{
            item.content ||
            '暂无知识正文'
          }}
        </div>
      </section>

      <!-- 底部操作 -->
      <div class="drawer-actions">
        <el-button
          :icon="User"
          v-if="canWrite"
          @click="handleEdit"
        >
          编辑知识
        </el-button>

        <el-button
          type="primary"
          :icon="Link"
          v-if="canWrite"
          @click="handleUse"
        >
          引用知识
        </el-button>
      </div>
    </div>

    <div
      v-else
      class="empty-detail"
    >
      暂无知识详情
    </div>
  </el-drawer>
</template>


<style scoped>
.detail-content {
  padding: 0 4px 20px;
}

.detail-heading {
  display: flex;
  align-items: center;
  gap: 7px;
}

.status-badge,
.featured-badge {
  display: inline-flex;
  height: 21px;
  align-items: center;
  gap: 4px;
  padding: 0 7px;
  font-size: 8px;
  border-radius: 4px;
}

.status-badge.draft {
  color: #929bab;
  background:
    rgba(146, 155, 171, 0.1);
}

.status-badge.published {
  color: #55d6a2;
  background:
    rgba(45, 190, 135, 0.1);
}

.status-badge.archived {
  color: #e2ae60;
  background:
    rgba(226, 174, 96, 0.1);
}

.featured-badge {
  color: #ad9fff;
  background:
    rgba(118, 91, 255, 0.11);
}

.detail-title {
  margin: 16px 0 0;
  color:
    var(
      --app-text-primary,
      #edf0f5
    );
  font-size: 18px;
  font-weight: 600;
  line-height: 28px;
}

.detail-summary {
  margin: 12px 0 0;
  color:
    var(
      --app-text-secondary,
      #8c94a3
    );
  font-size: 11px;
  line-height: 19px;
}

.detail-meta {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 18px;
  padding: 12px;
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

.meta-item {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 5px;
  padding: 8px;
  background: #0d121c;
  border: 1px solid #202736;
  border-radius: 5px;
}

.full-meta {
  grid-column: 1 / -1;
}

.meta-label {
  color:
    var(
      --app-text-muted,
      #687184
    );
  font-size: 8px;
}

.meta-item strong {
  overflow: hidden;
  color: #b9c0cc;
  font-size: 9px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.detail-section {
  margin-top: 18px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #c5cad3;
  font-size: 10px;
  font-weight: 500;
}

.section-title .el-icon {
  color:
    var(
      --app-primary,
      #765bff
    );
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.detail-tags span {
  padding: 4px 8px;
  color: #9f91ed;
  font-size: 8px;
  background:
    rgba(118, 91, 255, 0.09);
  border:
    1px solid
    rgba(118, 91, 255, 0.15);
  border-radius: 4px;
}

.empty-copy {
  margin: 10px 0 0;
  color: #626b7c;
  font-size: 9px;
}

.detail-body {
  min-height: 130px;
  margin-top: 10px;
  padding: 14px;
  color: #b6bdc9;
  font-size: 11px;
  line-height: 22px;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  background: #0d121c;
  border: 1px solid #202736;
  border-radius: 7px;
}

.drawer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 22px;
  padding-top: 16px;
  border-top: 1px solid #202736;
}

.drawer-actions :deep(.el-button) {
  height: 32px;
  margin: 0;
  padding: 0 14px;
  font-size: 9px;
}

.drawer-actions
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

.empty-detail {
  display: flex;
  min-height: 280px;
  align-items: center;
  justify-content: center;
  color: #687184;
  font-size: 10px;
}

@media (max-width: 620px) {
  .detail-meta {
    grid-template-columns: 1fr;
  }

  .full-meta {
    grid-column: auto;
  }

  .drawer-actions {
    flex-direction: column;
  }

  .drawer-actions :deep(.el-button) {
    width: 100%;
  }
}
</style>