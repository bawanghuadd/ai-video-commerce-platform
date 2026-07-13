import {
  createRouter,
  createWebHistory,
} from 'vue-router'

import {
  getAccessToken,
  migrateLegacyAuthData,
} from '../utils/authStorage.js'

const APP_TITLE =
  'AI短视频电商平台'

/**
 * 校验登录后的返回地址。
 *
 * 只允许站内绝对路径，避免跳转到外部地址。
 */
function getSafeRedirectPath(value) {
  if (typeof value !== 'string') {
    return null
  }

  if (
    !value.startsWith('/') ||
    value.startsWith('//') ||
    value.startsWith('/login')
  ) {
    return null
  }

  return value
}

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () =>
      import(
        '../views/LoginView.vue'
      ),
    meta: {
      title: '用户登录',
      guestOnly: true,
    },
  },

  {
    path: '/',
    component: () =>
      import(
        '../layouts/MainLayout.vue'
      ),
    meta: {
      requiresAuth: true,
    },

    children: [
      {
        path: '',
        redirect: {
          name: 'dashboard',
        },
      },

      {
        path: 'dashboard',
        name: 'dashboard',
        component: () =>
          import(
            '../views/DashboardView.vue'
          ),
        meta: {
          title: '数据概览',
        },
      },

      {
        path: 'products',
        name: 'products',
        component: () =>
          import(
            '../views/ProductView.vue'
          ),
        meta: {
          title: '商品管理',
        },
      },

      {
        path: 'content-creation',
        name: 'content-creation',
        component: () =>
          import(
            '../views/ContentCreationView.vue'
          ),
        meta: {
          title: '内容创作',
        },
      },

      {
        path: 'content-analysis',
        name: 'content-analysis',
        component: () =>
          import(
            '../views/ContentAnalysisView.vue'
          ),
        meta: {
          title: '内容拆解',
        },
      },

      {
        path: 'scripts',
        name: 'scripts',
        component: () =>
          import(
            '../views/ScriptManagementView.vue'
          ),
        meta: {
          title: '脚本分镜',
        },
      },

      {
        path: 'videos',
        name: 'videos',
        component: () =>
          import(
            '../views/VideoManagementView.vue'
          ),
        meta: {
          title: '视频管理',
        },
      },

      {
        path: 'traffic-analysis',
        name: 'traffic-analysis',
        component: () =>
          import(
            '../views/TrafficAnalysisView.vue'
          ),
        meta: {
          title: '投流分析',
          description:
            '管理广告投放数据和投流优化结果',
        },
      },

      {
        path: 'knowledge-base',
        name: 'knowledge-base',
        component: () =>
          import(
            '../views/KnowledgeBaseView.vue'
          ),
        meta: {
          title: '知识库',
        },
      },

      {
        path: 'settings',
        name: 'settings',
        component: () =>
          import(
            '../views/SystemSettingsView.vue'
          ),
        meta: {
          title: '系统设置',
        },
      },
    ],
  },

  {
    path: '/:pathMatch(.*)*',
    redirect: {
      name: 'dashboard',
    },
  },
]

migrateLegacyAuthData()

const router = createRouter({
  history: createWebHistory(
    import.meta.env.BASE_URL,
  ),

  routes,

  scrollBehavior() {
    return {
      top: 0,
      left: 0,
    }
  },
})

/**
 * 登录权限守卫。
 */
router.beforeEach((to) => {
  const token = getAccessToken()

  const requiresAuth =
    to.matched.some(
      (routeRecord) =>
        routeRecord.meta
          .requiresAuth === true,
    )

  /*
   * 未登录访问后台页面：
   * 跳转登录页，并记录原访问地址。
   */
  if (requiresAuth && !token) {
    return {
      name: 'login',
      query: {
        redirect: to.fullPath,
      },
      replace: true,
    }
  }

  /*
   * 已登录用户访问登录页：
   * 优先返回原页面，否则进入数据概览。
   */
  if (
    to.meta.guestOnly === true &&
    token
  ) {
    const redirectPath =
      getSafeRedirectPath(
        to.query.redirect,
      )

    if (redirectPath) {
      return {
        path: redirectPath,
        replace: true,
      }
    }

    return {
      name: 'dashboard',
      replace: true,
    }
  }

  return true
})

/**
 * 设置浏览器页面标题。
 */
router.afterEach((to) => {
  const routeWithTitle =
    [...to.matched]
      .reverse()
      .find(
        (routeRecord) =>
          typeof routeRecord
            .meta.title ===
          'string',
      )

  const pageTitle =
    routeWithTitle?.meta.title

  document.title = pageTitle
    ? `${pageTitle} - ${APP_TITLE}`
    : APP_TITLE
})

export default router
