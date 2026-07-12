<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Tools } from '@element-plus/icons-vue'

const route = useRoute()

const title = computed(() => {
  return route.meta.title || '功能模块'
})

const description = computed(() => {
  return route.meta.description || '该模块正在开发中'
})
</script>

<template>
  <el-card class="placeholder-card">
    <el-empty>
      <template #image>
        <el-icon
          class="placeholder-icon"
          size="72"
        >
          <Tools />
        </el-icon>
      </template>

      <template #description>
        <h2>{{ title }}</h2>
        <p>{{ description }}</p>
      </template>
    </el-empty>
  </el-card>
</template>

<style scoped>
.placeholder-card {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-icon {
  color: #409eff;
}

h2 {
  margin: 10px 0;
  color: #303133;
}

p {
  margin: 0;
  color: #909399;
}
</style>