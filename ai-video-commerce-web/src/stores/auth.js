import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import {
  getCurrentUserApi,
  loginApi,
  registerApi,
} from '../api/auth.js'

const ACCESS_TOKEN_KEY = 'access_token'
const LEGACY_TOKEN_KEY = 'token'
const TOKEN_TYPE_KEY = 'token_type'
const USER_KEY = 'user'

/**
 * 安全读取本地保存的用户信息。
 */
function getStoredUser() {
  const storedUser =
    localStorage.getItem(USER_KEY)

  if (!storedUser) {
    return null
  }

  try {
    return JSON.parse(storedUser)
  } catch {
    localStorage.removeItem(USER_KEY)
    return null
  }
}

/**
 * 清除本地认证数据。
 */
function clearAuthStorage() {
  localStorage.removeItem(
    ACCESS_TOKEN_KEY,
  )

  localStorage.removeItem(
    LEGACY_TOKEN_KEY,
  )

  localStorage.removeItem(
    TOKEN_TYPE_KEY,
  )

  localStorage.removeItem(
    USER_KEY,
  )
}

/**
 * 规范化不同格式的认证响应。
 */
function normalizeAuthData(authData) {
  return {
    accessToken:
      authData?.access_token ||
      authData?.token ||
      authData?.accessToken ||
      '',

    tokenType:
      authData?.token_type ||
      authData?.tokenType ||
      'bearer',

    user:
      authData?.user ||
      authData?.user_info ||
      authData?.profile ||
      null,
  }
}

export const useAuthStore =
  defineStore('auth', () => {
    const token = ref(
      localStorage.getItem(
        ACCESS_TOKEN_KEY,
      ) ||
        localStorage.getItem(
          LEGACY_TOKEN_KEY,
        ) ||
        '',
    )

    const user = ref(getStoredUser())

    const isLoggedIn = computed(
      () => Boolean(token.value),
    )

    /**
     * 统一保存认证状态。
     */
    function persistAuthData(authData) {
      const {
        accessToken,
        tokenType,
        user: userInfo,
      } = normalizeAuthData(authData)

      if (!accessToken) {
        throw new Error(
          '认证接口未返回访问令牌',
        )
      }

      token.value = accessToken
      user.value = userInfo

      localStorage.setItem(
        ACCESS_TOKEN_KEY,
        accessToken,
      )

      /*
       * 暂时保留 token 字段，
       * 用于兼容项目中的旧代码。
       */
      localStorage.setItem(
        LEGACY_TOKEN_KEY,
        accessToken,
      )

      localStorage.setItem(
        TOKEN_TYPE_KEY,
        tokenType,
      )

      if (userInfo) {
        localStorage.setItem(
          USER_KEY,
          JSON.stringify(userInfo),
        )
      } else {
        localStorage.removeItem(
          USER_KEY,
        )
      }
    }

    /**
     * 用户登录。
     */
    async function login(loginForm) {
      const authData =
        await loginApi(loginForm)

      persistAuthData(authData)

      return authData
    }

    /**
     * 用户注册。
     *
     * 注册接口返回 Token 时直接保存；
     * 未返回 Token 时自动调用登录接口。
     */
    async function register(registerForm) {
      const registerResult =
        await registerApi(registerForm)

      const {
        accessToken,
      } = normalizeAuthData(
        registerResult,
      )

      if (accessToken) {
        persistAuthData(
          registerResult,
        )

        return registerResult
      }

      return login({
        username:
          registerForm.username,

        password:
          registerForm.password,
      })
    }

    /**
     * 获取当前用户信息。
     */
    async function loadCurrentUser() {
      const currentUser =
        await getCurrentUserApi()

      user.value = currentUser

      localStorage.setItem(
        USER_KEY,
        JSON.stringify(currentUser),
      )

      return currentUser
    }

    /**
     * 用户退出登录。
     */
    function logout() {
      token.value = ''
      user.value = null

      clearAuthStorage()
    }

    return {
      token,
      user,
      isLoggedIn,
      login,
      register,
      loadCurrentUser,
      logout,
    }
  })