<script setup>
import {
  computed,
  onMounted,
  reactive,
  ref,
} from 'vue'

import {
  useRoute,
  useRouter,
} from 'vue-router'

import {
  ElMessage,
} from 'element-plus'

import {
  Check,
  DataAnalysis,
  Goods,
  Hide,
  Lock,
  Opportunity,
  ShoppingBag,
  User,
  VideoPlay,
  View,
} from '@element-plus/icons-vue'

import {
  useAuthStore,
} from '../stores/auth.js'

import {
  getApiErrorMessage,
} from '../utils/apiResponse.js'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('login')

const loginLoading = ref(false)
const registerLoading = ref(false)

const loginFormRef = ref(null)
const registerFormRef = ref(null)

const showLoginPassword = ref(false)
const showRegisterPassword = ref(false)

const showRegisterConfirmPassword =
  ref(false)

/* ==============================
   登录表单
================================ */

const loginForm = reactive({
  username: '',
  password: '',
  remember: true,
})

/* ==============================
   注册表单
================================ */

const registerForm = reactive({
  username: '',
  display_name: '',
  password: '',
  confirm_password: '',
})

/* ==============================
   左侧功能介绍
================================ */

const featureList = [
  {
    icon: Goods,
    title: '商品管理',
    desc:
      '高效管理商品库、库存与订单，提升运营效率',
  },
  {
    icon: VideoPlay,
    title: '内容创作',
    desc:
      'AI智能脚本生成、多模态素材创作，激发创意灵感',
  },
  {
    icon: ShoppingBag,
    title: '视频任务',
    desc:
      '批量生成与自动发布，提升内容生产与分发效率',
  },
  {
    icon: DataAnalysis,
    title: '数据分析',
    desc:
      '多维数据洞察与可视化分析，驱动业务持续增长',
  },
]

/* ==============================
   登录校验
================================ */

const loginRules = {
  username: [
    {
      required: true,
      message: '请输入账号',
      trigger: 'blur',
    },
  ],

  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur',
    },
    {
      min: 6,
      max: 100,
      message:
        '密码至少需要6个字符',
      trigger: 'blur',
    },
  ],
}

/* ==============================
   注册校验
================================ */

const registerRules = {
  username: [
    {
      required: true,
      message: '请输入注册账号',
      trigger: 'blur',
    },
    {
      min: 3,
      max: 50,
      message:
        '账号长度为3到50个字符',
      trigger: 'blur',
    },
    {
      pattern:
        /^[A-Za-z0-9_]+$/,
      message:
        '账号只能包含英文字母、数字和下划线',
      trigger: 'blur',
    },
  ],

  display_name: [
    {
      required: true,
      message: '请输入用户昵称',
      trigger: 'blur',
    },
    {
      min: 1,
      max: 50,
      message:
        '昵称不能超过50个字符',
      trigger: 'blur',
    },
  ],

  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur',
    },
    {
      min: 6,
      max: 100,
      message:
        '密码长度为6到100个字符',
      trigger: 'blur',
    },
  ],

  confirm_password: [
    {
      required: true,
      message: '请再次输入密码',
      trigger: 'blur',
    },
    {
      validator(
        _rule,
        value,
        callback,
      ) {
        if (
          value !==
          registerForm.password
        ) {
          callback(
            new Error(
              '两次输入的密码不一致',
            ),
          )

          return
        }

        callback()
      },
      trigger: 'blur',
    },
  ],
}

const currentYear = computed(
  () => new Date().getFullYear(),
)

/* ==============================
   页面切换
================================ */

function switchTab(tab) {
  activeTab.value = tab

  loginFormRef.value
    ?.clearValidate()

  registerFormRef.value
    ?.clearValidate()
}

/* ==============================
   进入系统
================================ */

async function enterSystem() {
  const redirectPath =
    route.query.redirect

  const isValidRedirect =
    typeof redirectPath ===
      'string' &&
    redirectPath.startsWith('/') &&
    !redirectPath.startsWith('//')

  if (isValidRedirect) {
    await router.replace(
      redirectPath,
    )

    return
  }

  await router.replace({
    name: 'dashboard',
  })
}

/* ==============================
   记住账号
================================ */

function saveRememberedAccount() {
  const username =
    loginForm.username.trim()

  if (loginForm.remember) {
    localStorage.setItem(
      'remembered_login_account',
      username,
    )

    return
  }

  localStorage.removeItem(
    'remembered_login_account',
  )
}

/* ==============================
   登录
================================ */

async function handleLogin() {
  if (!loginFormRef.value) {
    return
  }

  try {
    await loginFormRef.value
      .validate()
  } catch {
    return
  }

  loginLoading.value = true

  try {
    await authStore.login({
      username:
        loginForm.username.trim(),

      password:
        loginForm.password,
    })

    saveRememberedAccount()

    ElMessage.success(
      '登录成功',
    )

    await enterSystem()
  } catch (error) {
    ElMessage.error(
      getApiErrorMessage(
        error,
        '登录失败',
      ),
    )
  } finally {
    loginLoading.value = false
  }
}

/* ==============================
   注册并自动登录
================================ */

async function handleRegister() {
  if (!registerFormRef.value) {
    return
  }

  try {
    await registerFormRef.value
      .validate()
  } catch {
    return
  }

  registerLoading.value = true

  try {
    const username =
      registerForm.username.trim()

    await authStore.register({
      username,

      display_name:
        registerForm
          .display_name
          .trim(),

      password:
        registerForm.password,
    })

    localStorage.setItem(
      'remembered_login_account',
      username,
    )

    ElMessage.success(
      '注册成功，正在进入系统',
    )

    await enterSystem()
  } catch (error) {
    ElMessage.error(
      getApiErrorMessage(
        error,
        '注册失败',
      ),
    )
  } finally {
    registerLoading.value = false
  }
}

/* ==============================
   忘记密码
================================ */

function handleForgotPassword() {
  ElMessage.info(
    '当前版本暂未开放密码找回，请联系系统管理员重置密码。',
  )
}

/* ==============================
   初始化
================================ */

onMounted(() => {
  const rememberedAccount =
    localStorage.getItem(
      'remembered_login_account',
    )

  if (!rememberedAccount) {
    return
  }

  loginForm.username =
    rememberedAccount

  loginForm.remember = true
})
</script>

<template>
  <div class="login-page">
    <div class="login-page__bg-grid"></div>
    <div class="login-page__bg-wave"></div>
    <div class="login-page__bg-glow"></div>

    <div class="login-shell">
      <!-- 左侧品牌区 -->
      <section class="brand-panel">
        <div class="brand-top">
          <div class="brand-logo">
            <span>AI</span>
          </div>

          <div class="brand-title-wrap">
            <h1 class="brand-title-mini">AI短视频电商平台</h1>
          </div>
        </div>

        <div class="brand-content">
          <h2 class="brand-main-title">AI短视频电商平台</h2>

          <p class="brand-subtitle">
            AI驱动的短视频内容创作与电商增长平台
          </p>

          <div class="brand-divider">
            <span></span>
            <i></i>
          </div>

          <div class="feature-list">
            <div
              v-for="item in featureList"
              :key="item.title"
              class="feature-item"
            >
              <div class="feature-icon">
                <el-icon>
                  <component :is="item.icon" />
                </el-icon>
              </div>

              <div class="feature-text">
                <h3>{{ item.title }}</h3>
                <p>{{ item.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- 右侧登录卡片 -->
      <section class="auth-panel">
        <div class="auth-card">
          <div class="auth-card__halo"></div>

          <div class="auth-header">
            <div class="auth-logo">
              <span>AI</span>
            </div>

            <h2>欢迎登录</h2>

            <div class="auth-sub-line">
              <span></span>
              <p>AI短视频电商平台</p>
              <span></span>
            </div>
          </div>

          <!-- tab -->
          <div class="auth-tabs">
            <button
              class="auth-tab"
              :class="{ active: activeTab === 'login' }"
              @click="switchTab('login')"
            >
              登录
            </button>

            <button
              class="auth-tab"
              :class="{ active: activeTab === 'register' }"
              @click="switchTab('register')"
            >
              注册
            </button>
          </div>

          <!-- 登录 -->
          <div v-if="activeTab === 'login'" class="auth-body">
            <el-form
              ref="loginFormRef"
              :model="loginForm"
              :rules="loginRules"
              label-position="top"
              class="auth-form"
            >
              <el-form-item label="账号" prop="username">
                <el-input
                  v-model="loginForm.username"
                  placeholder="请输入账号/手机号/邮箱"
                  :prefix-icon="User"
                  size="large"
                />
              </el-form-item>

              <el-form-item label="密码" prop="password">
                <el-input
                  v-model="loginForm.password"
                  :type="showLoginPassword ? 'text' : 'password'"
                  placeholder="请输入密码"
                  :prefix-icon="Lock"
                  size="large"
                >
                  <template #suffix>
                    <el-icon
                      class="password-eye"
                      @click="showLoginPassword = !showLoginPassword"
                    >
                      <View v-if="!showLoginPassword" />
                      <Hide v-else />
                    </el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <div class="auth-extra">
                <el-checkbox v-model="loginForm.remember">
                  记住我
                </el-checkbox>

                <button
                  type="button"
                  class="text-action"
                  @click="handleForgotPassword"
                >
                  忘记密码？
                </button>
              </div>

              <el-button
                type="primary"
                size="large"
                class="submit-btn"
                :loading="loginLoading"
                @click="handleLogin"
              >
                登录
              </el-button>

              <div class="split-line">
                <span></span>
                <p>或</p>
                <span></span>
              </div>

              <button
                class="secondary-btn"
                type="button"
                @click="switchTab('register')"
              >
                注册新账号
              </button>

              <div class="bottom-switch">
                还没有账号？
                <button
                  type="button"
                  class="text-action strong"
                  @click="switchTab('register')"
                >
                  立即注册
                </button>
              </div>

              <div class="safe-tip">
                <el-icon>
                  <Check />
                </el-icon>
                <span>安全登录，数据加密传输</span>
              </div>
            </el-form>
          </div>

          <!-- 注册 -->
          <div v-else class="auth-body">
            <el-form
              ref="registerFormRef"
              :model="registerForm"
              :rules="registerRules"
              label-position="top"
              class="auth-form"
            >
              <el-form-item label="账号" prop="username">
                <el-input
                  v-model="registerForm.username"
                  placeholder="请输入注册账号"
                  :prefix-icon="User"
                  size="large"
                />
              </el-form-item>

              <el-form-item label="昵称" prop="display_name">
                <el-input
                  v-model="registerForm.display_name"
                  placeholder="请输入昵称"
                  :prefix-icon="Opportunity"
                  size="large"
                />
              </el-form-item>

              <el-form-item label="密码" prop="password">
                <el-input
                  v-model="registerForm.password"
                  :type="showRegisterPassword ? 'text' : 'password'"
                  placeholder="请输入密码"
                  :prefix-icon="Lock"
                  size="large"
                >
                  <template #suffix>
                    <el-icon
                      class="password-eye"
                      @click="showRegisterPassword = !showRegisterPassword"
                    >
                      <View v-if="!showRegisterPassword" />
                      <Hide v-else />
                    </el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="确认密码" prop="confirm_password">
                <el-input
                  v-model="registerForm.confirm_password"
                  :type="showRegisterConfirmPassword ? 'text' : 'password'"
                  placeholder="请再次输入密码"
                  :prefix-icon="Lock"
                  size="large"
                >
                  <template #suffix>
                    <el-icon
                      class="password-eye"
                      @click="
                        showRegisterConfirmPassword =
                          !showRegisterConfirmPassword
                      "
                    >
                      <View v-if="!showRegisterConfirmPassword" />
                      <Hide v-else />
                    </el-icon>
                  </template>
                </el-input>
              </el-form-item>

              <el-button
                type="primary"
                size="large"
                class="submit-btn"
                :loading="registerLoading"
                @click="handleRegister"
              >
                注册
              </el-button>

              <div class="bottom-switch">
                已有账号？
                <button
                  type="button"
                  class="text-action strong"
                  @click="switchTab('login')"
                >
                  立即登录
                </button>
              </div>

              <div class="safe-tip">
                <el-icon>
                  <Check />
                </el-icon>
                <span>安全注册，账号信息加密保护</span>
              </div>
            </el-form>
          </div>
        </div>
      </section>
    </div>

    <footer class="login-footer">
      © {{ currentYear }} AI短视频电商平台
      <span class="footer-dot">|</span>
      智能创作
      <span class="footer-dot">·</span>
      高效运营
      <span class="footer-dot">·</span>
      数据驱动增长
    </footer>
  </div>
</template>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(circle at 20% 20%, rgba(90, 79, 255, 0.08), transparent 30%),
    radial-gradient(circle at 80% 20%, rgba(105, 70, 255, 0.1), transparent 28%),
    linear-gradient(135deg, #040814 0%, #070d1c 50%, #050a15 100%);
  color: #ffffff;
}

.login-page__bg-grid {
  position: absolute;
  right: 8%;
  bottom: 10%;
  width: 520px;
  height: 320px;
  background-image:
    linear-gradient(rgba(112, 98, 255, 0.12) 1px, transparent 1px),
    linear-gradient(90deg, rgba(112, 98, 255, 0.12) 1px, transparent 1px);
  background-size: 36px 36px;
  opacity: 0.28;
  mask-image: linear-gradient(to top, rgba(0, 0, 0, 1), transparent);
  transform: perspective(600px) rotateX(70deg);
  pointer-events: none;
}

.login-page__bg-wave {
  position: absolute;
  left: -10%;
  bottom: 6%;
  width: 78%;
  height: 260px;
  background:
    radial-gradient(circle at center, rgba(113, 83, 255, 0.95) 0%, rgba(113, 83, 255, 0.15) 32%, transparent 62%);
  filter: blur(18px);
  opacity: 0.9;
  border-radius: 50%;
  transform: rotate(-8deg);
  pointer-events: none;
}

.login-page__bg-wave::after {
  position: absolute;
  inset: 48% 8% auto 8%;
  height: 3px;
  content: '';
  background: linear-gradient(90deg, transparent, #916aff, #6c8dff, #916aff, transparent);
  box-shadow:
    0 0 18px rgba(133, 104, 255, 0.9),
    0 0 42px rgba(86, 97, 255, 0.55);
  border-radius: 999px;
}

.login-page__bg-glow {
  position: absolute;
  right: 12%;
  top: 16%;
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, rgba(127, 95, 255, 0.2), transparent 70%);
  filter: blur(24px);
  pointer-events: none;
}

.login-shell {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: 1.08fr 0.92fr;
  min-height: calc(100vh - 54px);
  gap: 48px;
  padding: 48px 56px 22px;
}

.brand-panel {
  display: flex;
  min-width: 0;
  flex-direction: column;
  justify-content: flex-start;
  padding-top: 8px;
}

.brand-top {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-logo {
  display: flex;
  width: 44px;
  height: 44px;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 700;
  color: #ffffff;
  background: linear-gradient(135deg, #7d62ff, #4a5dff);
  border: 1px solid rgba(180, 165, 255, 0.45);
  box-shadow: 0 0 22px rgba(109, 89, 255, 0.36);
  clip-path: polygon(25% 6.7%, 75% 6.7%, 100% 50%, 75% 93.3%, 25% 93.3%, 0% 50%);
}

.brand-title-mini {
  margin: 0;
  color: #ffffff;
  font-size: 18px;
  font-weight: 700;
}

.brand-content {
  margin-top: 88px;
  max-width: 620px;
}

.brand-main-title {
  margin: 0;
  color: #f6f7fb;
  font-size: 66px;
  font-weight: 800;
  line-height: 1.12;
  letter-spacing: 1px;
}

.brand-subtitle {
  margin: 26px 0 0;
  color: rgba(255, 255, 255, 0.72);
  font-size: 24px;
  line-height: 1.6;
}

.brand-divider {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 38px;
}

.brand-divider span {
  width: 76px;
  height: 4px;
  background: linear-gradient(90deg, #9f71ff, #5f6fff);
  border-radius: 999px;
}

.brand-divider i {
  display: block;
  width: 7px;
  height: 7px;
  background: #6f67ff;
  border-radius: 50%;
  box-shadow: 0 0 14px rgba(111, 103, 255, 0.9);
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
  margin-top: 40px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 18px;
}

.feature-icon {
  display: flex;
  width: 60px;
  height: 60px;
  flex: 0 0 60px;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  color: #7c69ff;
  background: linear-gradient(180deg, rgba(16, 23, 42, 0.96), rgba(8, 12, 24, 0.96));
  border: 1px solid rgba(105, 111, 183, 0.42);
  border-radius: 16px;
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.03),
    0 0 18px rgba(70, 72, 155, 0.16);
}

.feature-text h3 {
  margin: 4px 0 8px;
  color: #f4f6fa;
  font-size: 22px;
  font-weight: 700;
}

.feature-text p {
  margin: 0;
  color: rgba(255, 255, 255, 0.62);
  font-size: 16px;
  line-height: 1.75;
}

.auth-panel {
  display: flex;
  align-items: center;
  justify-content: center;
}

.auth-card {
  position: relative;
  width: 100%;
  max-width: 620px;
  padding: 34px 44px 30px;
  background: linear-gradient(180deg, rgba(17, 24, 43, 0.92), rgba(7, 11, 21, 0.94));
  border: 1px solid rgba(132, 121, 255, 0.58);
  border-radius: 28px;
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.03) inset,
    0 0 40px rgba(98, 85, 255, 0.16),
    0 0 110px rgba(95, 83, 255, 0.08);
  backdrop-filter: blur(12px);
  overflow: hidden;
}

.auth-card__halo {
  position: absolute;
  right: -40px;
  top: -40px;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(154, 112, 255, 0.22), transparent 68%);
  pointer-events: none;
}

.auth-header {
  position: relative;
  z-index: 1;
  text-align: center;
}

.auth-logo {
  display: flex;
  width: 92px;
  height: 92px;
  margin: 0 auto 18px;
  align-items: center;
  justify-content: center;
  font-size: 42px;
  font-weight: 800;
  color: #ffffff;
  background: linear-gradient(135deg, #7a61ff, #4c5eff);
  border: 1px solid rgba(204, 196, 255, 0.45);
  box-shadow: 0 0 28px rgba(102, 85, 255, 0.4);
  clip-path: polygon(25% 6.7%, 75% 6.7%, 100% 50%, 75% 93.3%, 25% 93.3%, 0% 50%);
}

.auth-header h2 {
  margin: 0;
  color: #ffffff;
  font-size: 34px;
  font-weight: 800;
}

.auth-sub-line {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-top: 12px;
}

.auth-sub-line span {
  width: 84px;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(116, 99, 255, 0.9), transparent);
}

.auth-sub-line p {
  margin: 0;
  color: rgba(255, 255, 255, 0.62);
  font-size: 16px;
}

.auth-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  margin-top: 34px;
  border: 1px solid rgba(111, 119, 170, 0.36);
  border-radius: 14px;
  overflow: hidden;
}

.auth-tab {
  height: 56px;
  color: #e7e8ee;
  font-size: 18px;
  font-weight: 700;
  background: rgba(12, 16, 28, 0.58);
  border: 0;
  cursor: pointer;
  transition: all 0.2s ease;
}

.auth-tab.active {
  color: #ffffff;
  background: linear-gradient(90deg, #8162ff, #4e56ff);
  box-shadow: inset 0 -1px 0 rgba(255, 255, 255, 0.08);
}

.auth-body {
  position: relative;
  z-index: 1;
  margin-top: 28px;
}

.auth-form :deep(.el-form-item) {
  margin-bottom: 24px;
}

.auth-form :deep(.el-form-item__label) {
  margin-bottom: 10px;
  color: #ffffff;
  font-size: 16px;
  font-weight: 600;
}

.auth-form :deep(.el-input__wrapper) {
  height: 56px;
  background: rgba(10, 15, 26, 0.72);
  border-radius: 14px;
  box-shadow: 0 0 0 1px rgba(93, 100, 145, 0.58) inset;
  transition: all 0.2s ease;
}

.auth-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(116, 107, 255, 0.66) inset;
}

.auth-form :deep(.el-input__wrapper.is-focus) {
  box-shadow:
    0 0 0 1px #765bff inset,
    0 0 0 4px rgba(118, 91, 255, 0.1);
}

.auth-form :deep(.el-input__inner) {
  color: #ffffff;
  font-size: 17px;
}

.auth-form :deep(.el-input__prefix-inner),
.auth-form :deep(.el-input__suffix-inner) {
  color: rgba(255, 255, 255, 0.56);
  font-size: 18px;
}

.password-eye {
  cursor: pointer;
}

.auth-extra {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: -4px 0 18px;
}

.auth-extra :deep(.el-checkbox) {
  color: rgba(255, 255, 255, 0.82);
  font-size: 15px;
}

.auth-extra :deep(.el-checkbox__label) {
  color: rgba(255, 255, 255, 0.82);
}

.auth-extra :deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background-color: #6f63ff;
  border-color: #6f63ff;
}

.text-action {
  padding: 0;
  color: #7b6dff;
  font-size: 15px;
  background: transparent;
  border: none;
  cursor: pointer;
}

.text-action:hover {
  color: #9a8cff;
}

.text-action.strong {
  font-weight: 700;
}

.submit-btn {
  width: 100%;
  height: 58px;
  font-size: 24px;
  font-weight: 700;
  border: none !important;
  border-radius: 16px !important;
  background: linear-gradient(90deg, #7d61ff, #4e56ff) !important;
  box-shadow: 0 14px 28px rgba(92, 76, 255, 0.24);
}

.submit-btn:hover {
  background: linear-gradient(90deg, #8b72ff, #6168ff) !important;
}

.split-line {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

.split-line span {
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.12);
}

.split-line p {
  margin: 0;
  color: rgba(255, 255, 255, 0.58);
  font-size: 15px;
}

.secondary-btn {
  width: 100%;
  height: 58px;
  color: #7d6bff;
  font-size: 20px;
  font-weight: 700;
  background: rgba(7, 11, 21, 0.22);
  border: 1px solid rgba(92, 88, 255, 0.74);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.secondary-btn:hover {
  color: #9b8dff;
  border-color: #786cff;
  box-shadow: 0 0 18px rgba(118, 91, 255, 0.18);
}

.bottom-switch {
  margin-top: 18px;
  text-align: center;
  color: rgba(255, 255, 255, 0.68);
  font-size: 15px;
}

.safe-tip {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 26px;
  padding-top: 18px;
  color: rgba(255, 255, 255, 0.52);
  font-size: 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.login-footer {
  position: relative;
  z-index: 2;
  padding: 0 20px 18px;
  text-align: center;
  color: rgba(255, 255, 255, 0.54);
  font-size: 14px;
}

.footer-dot {
  display: inline-block;
  margin: 0 10px;
  opacity: 0.45;
}

/* 响应式 */
@media (max-width: 1400px) {
  .login-shell {
    grid-template-columns: 1fr 0.95fr;
    gap: 30px;
    padding: 36px 34px 18px;
  }

  .brand-main-title {
    font-size: 54px;
  }

  .brand-subtitle {
    font-size: 20px;
  }

  .feature-text h3 {
    font-size: 20px;
  }

  .feature-text p {
    font-size: 15px;
  }
}

@media (max-width: 1100px) {
  .login-shell {
    grid-template-columns: 1fr;
    gap: 24px;
  }

  .brand-panel {
    padding-top: 0;
  }

  .brand-content {
    margin-top: 32px;
    max-width: none;
  }

  .auth-panel {
    justify-content: flex-start;
  }

  .auth-card {
    max-width: none;
  }

  .login-page__bg-grid,
  .login-page__bg-wave {
    display: none;
  }
}

@media (max-width: 768px) {
  .login-shell {
    padding: 22px 16px 14px;
  }

  .brand-main-title {
    font-size: 38px;
  }

  .brand-subtitle {
    font-size: 16px;
  }

  .feature-list {
    gap: 18px;
  }

  .feature-item {
    gap: 12px;
  }

  .feature-icon {
    width: 48px;
    height: 48px;
    flex-basis: 48px;
    font-size: 22px;
    border-radius: 14px;
  }

  .feature-text h3 {
    font-size: 18px;
  }

  .feature-text p {
    font-size: 14px;
  }

  .auth-card {
    padding: 24px 18px 22px;
    border-radius: 22px;
  }

  .auth-logo {
    width: 76px;
    height: 76px;
    font-size: 34px;
  }

  .auth-header h2 {
    font-size: 28px;
  }

  .auth-sub-line p {
    font-size: 14px;
  }

  .auth-sub-line span {
    width: 48px;
  }

  .auth-tab {
    height: 50px;
    font-size: 17px;
  }

  .auth-form :deep(.el-form-item__label) {
    font-size: 15px;
  }

  .auth-form :deep(.el-input__wrapper) {
    height: 52px;
    border-radius: 12px;
  }

  .submit-btn,
  .secondary-btn {
    height: 54px;
    font-size: 20px;
    border-radius: 14px !important;
  }

  .safe-tip,
  .bottom-switch,
  .text-action,
  .auth-extra :deep(.el-checkbox) {
    font-size: 14px;
  }

  .login-footer {
    font-size: 12px;
  }
}
</style>