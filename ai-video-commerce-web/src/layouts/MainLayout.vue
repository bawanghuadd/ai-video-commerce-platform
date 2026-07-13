<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth.js'

import {
  Bell,
  Collection,
  DataBoard,
  Document,
  Goods,
  Search,
  Setting,
  TrendCharts,
  VideoCamera,
} from '@element-plus/icons-vue'


/* ==============================
   路由
================================ */

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()


/* ==============================
   顶部搜索
================================ */

const globalKeyword = ref('')


/* ==============================
   工作台菜单
================================ */

const mainMenuItems = [
  {
    routeName: 'dashboard',
    label: '数据概览',
    icon: DataBoard,
  },
  {
    routeName: 'products',
    label: '商品管理',
    icon: Goods,
  },
  {
    routeName: 'content-creation',
    label: '内容创作',
    icon: Document,
  },
  {
    routeName: 'content-analysis',
    label: '拆解记录',
    icon: Collection,
  },
]


/* ==============================
   业务模块菜单
================================ */

const businessMenuItems = [
  {
    routeName: 'scripts',
    label: '脚本分镜',
    icon: Collection,
    disabled: false,
  },
  {
    routeName: 'videos',
    label: '视频管理',
    icon: VideoCamera,
    disabled: false,
  },
  {
    routeName: 'traffic-analysis',
    label: '投流分析',
    icon: TrendCharts,
    disabled: false,
  },
  {
    routeName: 'knowledge-base',
    label: '知识库',
    icon: Collection,
    disabled: false,
  },
  {
    routeName: 'settings',
    label: '系统设置',
    icon: Setting,
    disabled: false,
  },
]

/* ==============================
   当前菜单
================================ */

const activeMenu = computed(() => {
  return String(route.name || 'dashboard')
})


/* ==============================
   用户信息
================================ */

const storedUser = computed(() => authStore.user || {})

const displayName = computed(() => {
  return (
    storedUser.value.display_name ||
    storedUser.value.username ||
    '系统管理员'
  )
})

const roleName = computed(() => {
  const roleMap = {
    admin: '管理员',
    manager: '运营主管',
    user: '普通用户',
  }

  return (
    roleMap[storedUser.value.role] ||
    '管理员'
  )
})


/* ==============================
   菜单跳转
================================ */

async function handleMenuSelect(routeName) {
  if (!routeName) {
    return
  }

  if (route.name === routeName) {
    return
  }

  try {
    await router.push({
      name: routeName,
    })
  } catch (error) {
    console.error(
      `路由跳转失败：${routeName}`,
      error,
    )
  }
}


/* ==============================
   全局搜索
================================ */

function handleGlobalSearch() {
  const keyword =
    globalKeyword.value.trim()

  if (!keyword) {
    return
  }

  console.log(
    '全局搜索关键词：',
    keyword,
  )
}


/* ==============================
   退出登录
================================ */

function handleLogout() {
  authStore.logout()

  router.replace('/login')
}
</script>


<template>
  <div class="app-shell">
    <!-- 左侧导航栏 -->
    <aside class="app-sidebar">
      <!-- 品牌区域 -->
      <div class="brand">
        <div class="brand-icon">
          AI
        </div>

        <div class="brand-text">
          <strong>AI Video</strong>
          <span>Commerce Platform</span>
        </div>
      </div>

      <!-- 工作台 -->
      <section class="menu-section">
        <div class="menu-label">
          工作台
        </div>

        <el-menu
          class="sidebar-menu"
          :default-active="activeMenu"
          @select="handleMenuSelect"
        >
          <el-menu-item
            v-for="item in mainMenuItems"
            :key="item.routeName"
            :index="item.routeName"
          >
            <el-icon>
              <component :is="item.icon" />
            </el-icon>

            <span>{{ item.label }}</span>
          </el-menu-item>
        </el-menu>
      </section>

      <!-- 业务模块 -->
      <section class="menu-section business-section">
        <div class="menu-label">
          业务模块
        </div>

        <el-menu
          class="sidebar-menu"
          :default-active="activeMenu"
          @select="handleMenuSelect"
        >
          <el-menu-item
            v-for="item in businessMenuItems"
            :key="item.routeName"
            :index="item.routeName"
            :disabled="item.disabled"
          >
            <el-icon>
              <component :is="item.icon" />
            </el-icon>

            <span>{{ item.label }}</span>

            <span
              v-if="item.disabled"
              class="developing-tag"
            >
              开发中
            </span>
          </el-menu-item>
        </el-menu>
      </section>

      <!-- 系统状态 -->
      <div class="sidebar-footer">
        <div class="system-status">
          <span class="status-dot" />

          <div class="status-text">
            <strong>系统运行正常</strong>
            <span>FastAPI · MySQL</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- 右侧主体 -->
    <section class="app-main">
      <!-- 顶部导航栏 -->
      <header class="app-header">
        <div class="header-actions">
          <el-input
            v-model="globalKeyword"
            class="global-search"
            placeholder="搜索商品、内容、任务..."
            :prefix-icon="Search"
            clearable
            @keyup.enter="handleGlobalSearch"
          />

          <button
            class="header-icon-button"
            type="button"
            aria-label="消息通知"
          >
            <el-icon>
              <Bell />
            </el-icon>

            <span class="notification-dot" />
          </button>

          <el-dropdown trigger="click">
            <div class="user-panel">
              <div class="user-avatar">
                {{ displayName.slice(0, 1) }}
              </div>

              <div class="user-info">
                <strong>
                  {{ displayName }}
                </strong>

                <span>
                  {{ roleName }}
                </span>
              </div>

              <span class="user-arrow">
                ▾
              </span>
            </div>

            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>
                  个人信息
                </el-dropdown-item>

                <el-dropdown-item divided>
                  <span
                    class="logout-item"
                    @click="handleLogout"
                  >
                    退出登录
                  </span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 路由页面 -->
      <main class="page-content">
        <router-view />
      </main>
    </section>
  </div>
</template>


<style scoped>
.app-shell {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  color: var(--app-text-primary);
  background: var(--app-bg);
}


/* ==============================
   左侧导航栏
================================ */

.app-sidebar {
  position: relative;
  display: flex;
  width: 180px;
  height: 100vh;
  flex: 0 0 180px;
  flex-direction: column;
  overflow: hidden;
  background:
    linear-gradient(
      180deg,
      rgba(118, 91, 255, 0.045),
      transparent 24%
    ),
    #0b0f18;
  border-right: 1px solid #252c3b;
}


/* ==============================
   品牌区域
================================ */

.brand {
  display: flex;
  height: 56px;
  flex: 0 0 56px;
  align-items: center;
  gap: 9px;
  padding: 0 14px;
  border-bottom: 1px solid #252c3b;
}

.brand-icon {
  display: flex;
  width: 27px;
  height: 27px;
  flex: 0 0 27px;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 10px;
  font-weight: 700;
  background:
    linear-gradient(
      135deg,
      #9a7dff,
      #6545ed
    );
  border-radius: 8px;
  box-shadow:
    0 0 16px rgba(118, 91, 255, 0.34);
}

.brand-text {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.brand-text strong {
  overflow: hidden;
  color: #f3f4f8;
  font-size: 12px;
  line-height: 17px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.brand-text span {
  overflow: hidden;
  color: #687184;
  font-size: 7px;
  line-height: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}


/* ==============================
   菜单
================================ */

.menu-section {
  padding-top: 11px;
}

.business-section {
  padding-top: 5px;
}

.menu-label {
  padding: 0 16px 7px;
  color: #525b6c;
  font-size: 9px;
  letter-spacing: 0.7px;
}

.sidebar-menu {
  background: transparent;
  border-right: 0;
}

.sidebar-menu :deep(.el-menu-item) {
  position: relative;
  display: flex;
  height: 36px;
  margin: 2px 9px;
  padding: 0 11px !important;
  color: #939bab;
  font-size: 11px;
  border-radius: 6px;
  transition:
    color 0.2s ease,
    background 0.2s ease;
}

.sidebar-menu :deep(.el-menu-item .el-icon) {
  margin-right: 8px;
  font-size: 14px;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  color: #ffffff;
  background:
    rgba(118, 91, 255, 0.08);
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  color: #c1b6ff;
  background:
    linear-gradient(
      90deg,
      rgba(118, 91, 255, 0.28),
      rgba(118, 91, 255, 0.1)
    );
}

.sidebar-menu
  :deep(.el-menu-item.is-active::before) {
  position: absolute;
  top: 7px;
  left: 0;
  width: 2px;
  height: 22px;
  background: #765bff;
  border-radius: 0 3px 3px 0;
  content: "";
}

.sidebar-menu
  :deep(.el-menu-item.is-disabled) {
  color: #626a79;
  cursor: not-allowed;
  opacity: 0.63;
}

.developing-tag {
  margin-left: auto;
  color: #4e5665;
  font-size: 7px;
}


/* ==============================
   系统状态
================================ */

.sidebar-footer {
  margin-top: auto;
  padding: 10px;
}

.system-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 10px;
  background:
    rgba(255, 255, 255, 0.025);
  border: 1px solid #252c3b;
  border-radius: 7px;
}

.status-dot {
  width: 6px;
  height: 6px;
  flex: 0 0 6px;
  background: #35d49a;
  border-radius: 50%;
  box-shadow:
    0 0 9px rgba(53, 212, 154, 0.58);
}

.status-text {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.status-text strong {
  overflow: hidden;
  color: #aeb5c3;
  font-size: 8px;
  font-weight: 500;
  line-height: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-text span {
  margin-top: 1px;
  overflow: hidden;
  color: #596273;
  font-size: 7px;
  line-height: 10px;
  text-overflow: ellipsis;
  white-space: nowrap;
}


/* ==============================
   右侧主体
================================ */

.app-main {
  display: flex;
  min-width: 0;
  height: 100vh;
  flex: 1;
  flex-direction: column;
  overflow: hidden;
}


/* ==============================
   顶部栏
================================ */

.app-header {
  z-index: 20;
  display: flex;
  height: 56px;
  flex: 0 0 56px;
  align-items: center;
  justify-content: flex-end;
  padding: 0 15px;
  background:
    rgba(11, 15, 24, 0.9);
  border-bottom: 1px solid #252c3b;
  backdrop-filter: blur(18px);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 9px;
}

.global-search {
  width: 250px;
}

.global-search :deep(.el-input__wrapper) {
  height: 31px;
  padding: 0 10px;
  background:
    rgba(255, 255, 255, 0.025);
  border-radius: 6px;
  box-shadow:
    0 0 0 1px #252c3b inset;
}

.global-search
  :deep(.el-input__wrapper:hover) {
  box-shadow:
    0 0 0 1px #343d50 inset;
}

.global-search
  :deep(.el-input__wrapper.is-focus) {
  box-shadow:
    0 0 0 1px #765bff inset,
    0 0 0 3px
      rgba(118, 91, 255, 0.07);
}

.global-search :deep(.el-input__inner) {
  color: #b8bfcc;
  font-size: 10px;
}

.global-search
  :deep(.el-input__inner::placeholder) {
  color: #596273;
}

.global-search
  :deep(.el-input__prefix-inner) {
  color: #60697a;
}

.header-icon-button {
  position: relative;
  display: flex;
  width: 31px;
  height: 31px;
  flex: 0 0 31px;
  align-items: center;
  justify-content: center;
  padding: 0;
  color: #8991a1;
  cursor: pointer;
  background:
    rgba(255, 255, 255, 0.025);
  border: 1px solid #252c3b;
  border-radius: 6px;
}

.header-icon-button:hover {
  color: #ffffff;
  border-color: #353e50;
}

.notification-dot {
  position: absolute;
  top: 6px;
  right: 6px;
  width: 5px;
  height: 5px;
  background: #ef7075;
  border: 1px solid #0b0f18;
  border-radius: 50%;
}


/* ==============================
   用户信息
================================ */

.user-panel {
  display: flex;
  min-width: 108px;
  align-items: center;
  gap: 7px;
  padding: 3px 5px;
  cursor: pointer;
  border-radius: 7px;
  outline: none;
}

.user-panel:hover {
  background:
    rgba(255, 255, 255, 0.035);
}

.user-avatar {
  display: flex;
  width: 29px;
  height: 29px;
  flex: 0 0 29px;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 10px;
  font-weight: 600;
  background:
    linear-gradient(
      135deg,
      #8a6dff,
      #5c3ddd
    );
  border-radius: 50%;
}

.user-info {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.user-info strong {
  max-width: 72px;
  overflow: hidden;
  color: #e7e9ef;
  font-size: 9px;
  font-weight: 500;
  line-height: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-info span {
  margin-top: 1px;
  color: #687184;
  font-size: 7px;
  line-height: 10px;
}

.user-arrow {
  color: #596273;
  font-size: 8px;
}

.logout-item {
  display: block;
  width: 100%;
  color: #ef7075;
}


/* ==============================
   页面内容
================================ */

.page-content {
  flex: 1;
  min-width: 0;
  padding: 14px 16px 18px;
  overflow: auto;
  background:
    radial-gradient(
      circle at 35% 0%,
      rgba(118, 91, 255, 0.025),
      transparent 26%
    ),
    #080b12;
}

.page-content::-webkit-scrollbar {
  width: 7px;
  height: 7px;
}

.page-content::-webkit-scrollbar-track {
  background: transparent;
}

.page-content::-webkit-scrollbar-thumb {
  background: #2a3140;
  border-radius: 8px;
}

.page-content::-webkit-scrollbar-thumb:hover {
  background: #363f51;
}


/* ==============================
   窄屏适配
================================ */

@media (max-width: 1200px) {
  .app-sidebar {
    width: 170px;
    flex-basis: 170px;
  }

  .global-search {
    width: 220px;
  }

  .page-content {
    padding-right: 12px;
    padding-left: 12px;
  }
}
</style>
