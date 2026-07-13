<script setup>
import {
  Collection,
  Delete,
  Edit,
  Link,
  Star,
  View,
} from '@element-plus/icons-vue'

import {
  getKnowledgeCategoryClass,
  getKnowledgeStatusClass,
} from '../../constants/knowledge.js'


const props = defineProps({
  item: {
    type: Object,
    required: true,
  },

  productList: {
    type: Array,
    default: () => [],
  },

  canWrite: {
    type: Boolean,
    default: false,
  },

  usingKnowledgeId: {
    type: [Number, String, null],
    default: null,
  },
})


const emit = defineEmits([
  'view',
  'edit',
  'delete',
  'use',
])


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
</script>


<template>
  <article
    class="knowledge-card"
    :class="{
      featured: item.is_featured,
    }"
  >
    <div class="card-top">
      <div
        class="category-icon"
        :class="
          getKnowledgeCategoryClass(
            item.category,
          )
        "
      >
        <el-icon>
          <Collection />
        </el-icon>
      </div>

      <div class="card-tags">
        <span
          class="status-badge"
          :class="
            getKnowledgeStatusClass(
              item.status,
            )
          "
        >
          {{ item.status }}
        </span>

        <span
          v-if="item.is_featured"
          class="featured-badge"
        >
          <el-icon>
            <Star />
          </el-icon>

          精选
        </span>
      </div>
    </div>

    <h3>
      {{ item.title }}
    </h3>

    <p class="knowledge-summary">
      {{
        item.summary ||
        item.content ||
        '暂无摘要'
      }}
    </p>

    <div class="tag-list">
      <span
        v-for="tag in (item.tags || []).slice(0, 4)"
        :key="tag"
        class="knowledge-tag"
      >
        {{ tag }}
      </span>

      <span
        v-if="(item.tags || []).length > 4"
        class="more-tags"
      >
        +{{ item.tags.length - 4 }}
      </span>
    </div>

    <div class="knowledge-meta">
      <span>
        {{ getProductName(item.product_id) }}
      </span>

      <span>
        {{ item.source_type || '手动录入' }}
      </span>
    </div>

    <div class="card-footer">
      <div class="usage-info">
        <el-icon>
          <Link />
        </el-icon>

        <span>
          引用 {{ item.usage_count || 0 }} 次
        </span>
      </div>

      <div class="card-actions">
        <el-button
          link
          :icon="View"
          @click="emit('view', item)"
        >
          查看
        </el-button>

        <el-button
          type="success"
          link
          :icon="Link"
          v-if="canWrite"
          :loading="
            usingKnowledgeId === item.id
          "
          @click="emit('use', item)"
        >
          引用
        </el-button>

        <el-button
          type="primary"
          link
          :icon="Edit"
          v-if="canWrite"
          @click="emit('edit', item)"
        >
          编辑
        </el-button>

        <el-button
          type="danger"
          link
          :icon="Delete"
          v-if="canWrite"
          @click="emit('delete', item)"
        >
          删除
        </el-button>
      </div>
    </div>
  </article>
</template>


<style scoped>
.knowledge-card {
  position: relative;
  display: flex;
  min-width: 0;
  min-height: 236px;
  flex-direction: column;
  padding: 13px;
  background:
    linear-gradient(
      145deg,
      rgba(255, 255, 255, 0.016),
      transparent 65%
    ),
    #141925;
  border: 1px solid #242c3a;
  border-radius: 7px;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease;
}

.knowledge-card:hover {
  border-color: #44386f;
  transform: translateY(-2px);
}

.knowledge-card.featured {
  border-color:
    rgba(118, 91, 255, 0.42);
  box-shadow:
    0 0 18px
    rgba(118, 91, 255, 0.08);
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.category-icon {
  display: flex;
  width: 33px;
  height: 33px;
  align-items: center;
  justify-content: center;
  color: #927dff;
  font-size: 16px;
  background:
    rgba(118, 91, 255, 0.11);
  border-radius: 8px;
}

.category-icon.script,
.category-icon.video {
  color: #48c5d2;
  background:
    rgba(72, 197, 210, 0.1);
}

.category-icon.selling {
  color: #55d6a2;
  background:
    rgba(45, 190, 135, 0.1);
}

.category-icon.traffic {
  color: #e2ae60;
  background:
    rgba(226, 174, 96, 0.1);
}

.category-icon.failure {
  color: #ee7a86;
  background:
    rgba(238, 122, 134, 0.1);
}

.card-tags {
  display: flex;
  align-items: center;
  gap: 5px;
}

.status-badge,
.featured-badge {
  display: inline-flex;
  height: 19px;
  align-items: center;
  gap: 3px;
  padding: 0 6px;
  font-size: 7px;
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

.knowledge-card h3 {
  margin: 13px 0 0;
  overflow: hidden;
  color: #e2e5eb;
  font-size: 10px;
  font-weight: 500;
  line-height: 16px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.knowledge-summary {
  display: -webkit-box;
  min-height: 42px;
  margin: 8px 0 0;
  overflow: hidden;
  color: #747d8e;
  font-size: 8px;
  line-height: 14px;
  text-overflow: ellipsis;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  line-clamp: 3;
}

.tag-list {
  display: flex;
  min-height: 22px;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 10px;
}

.knowledge-tag,
.more-tags {
  padding: 3px 6px;
  color: #8c7de2;
  font-size: 7px;
  background:
    rgba(118, 91, 255, 0.07);
  border:
    1px solid
    rgba(118, 91, 255, 0.12);
  border-radius: 4px;
}

.more-tags {
  color: #687184;
  background: #171c27;
  border-color: #282f3e;
}

.knowledge-meta {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-top: 10px;
  color: #616a7b;
  font-size: 7px;
}

.knowledge-meta span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: auto;
  padding-top: 10px;
  border-top:
    1px solid
    rgba(255, 255, 255, 0.04);
}

.usage-info {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #626b7c;
  font-size: 7px;
}

.card-actions {
  display: flex;
  align-items: center;
}

.card-actions :deep(.el-button) {
  height: 21px;
  margin-left: 0;
  padding: 0 4px;
  font-size: 7px;
}
</style>