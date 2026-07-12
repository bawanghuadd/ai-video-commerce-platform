<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { getHealthStatus } from '../api/system'

const loading = ref(false)
const backendStatus = ref('等待检查')
const serviceName = ref('')
const connectionSuccess = ref(false)

async function checkBackend() {
  loading.value = true
  connectionSuccess.value = false

  try {
    const response = await getHealthStatus()

    backendStatus.value = response.message
    serviceName.value = response.data.service
    connectionSuccess.value = true

    ElMessage.success('前后端连接成功')
  } catch (error) {
    backendStatus.value = '后端连接失败'
    serviceName.value = ''

    ElMessage.error('无法连接 FastAPI 后端')
    console.error(error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  checkBackend()
})
</script>

<template>
  <main class="page-container">
    <el-card class="status-card">
      <template #header>
        <div class="card-header">
          <div>
            <h1>AI短视频电商内容生产与质量管理平台</h1>
            <p>Vue3 + FastAPI 前后端分离项目</p>
          </div>

          <el-tag
            :type="connectionSuccess ? 'success' : 'danger'"
            size="large"
          >
            {{ connectionSuccess ? '后端在线' : '等待连接' }}
          </el-tag>
        </div>
      </template>

      <el-descriptions :column="1" border>
        <el-descriptions-item label="后端状态">
          {{ backendStatus }}
        </el-descriptions-item>

        <el-descriptions-item label="服务名称">
          {{ serviceName || '暂无数据' }}
        </el-descriptions-item>

        <el-descriptions-item label="后端地址">
          http://127.0.0.1:8000
        </el-descriptions-item>
      </el-descriptions>

      <el-button
        class="check-button"
        type="primary"
        :loading="loading"
        @click="checkBackend"
      >
        重新检查后端
      </el-button>
    </el-card>
  </main>
</template>

<style scoped>
.page-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.status-card {
  width: 720px;
  max-width: 100%;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

h1 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

p {
  margin: 12px 0 0;
  color: #909399;
}

.check-button {
  margin-top: 24px;
}
</style>