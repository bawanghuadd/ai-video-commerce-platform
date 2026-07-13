import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import { getCurrentUserApi, loginApi, registerApi } from '../api/auth.js'
import {
  clearAuthData,
  getAccessToken,
  getStoredUser,
  migrateLegacyAuthData,
  setAuthData,
  setStoredUser,
} from '../utils/authStorage.js'

function hasAccessToken(authData) {
  return Boolean(authData?.access_token || authData?.token || authData?.accessToken)
}

export const useAuthStore = defineStore('auth', () => {
  migrateLegacyAuthData()

  const token = ref(getAccessToken())
  const user = ref(getStoredUser())
  const isLoggedIn = computed(() => Boolean(token.value))

  function persistAuthData(authData) {
    const normalized = setAuthData(authData)

    token.value = normalized.accessToken
    user.value = normalized.user
  }

  async function login(loginForm) {
    const authData = await loginApi(loginForm)

    persistAuthData(authData)
    return authData
  }

  async function register(registerForm) {
    const registerResult = await registerApi(registerForm)

    if (hasAccessToken(registerResult)) {
      persistAuthData(registerResult)
      return registerResult
    }

    return login({
      username: registerForm.username,
      password: registerForm.password,
    })
  }

  async function loadCurrentUser() {
    const currentUser = await getCurrentUserApi()

    user.value = currentUser
    setStoredUser(currentUser)

    return currentUser
  }

  function logout() {
    token.value = ''
    user.value = null
    clearAuthData()
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
