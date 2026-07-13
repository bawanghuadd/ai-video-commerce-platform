const ACCESS_TOKEN_KEY = 'access_token'
const LEGACY_TOKEN_KEY = 'token'
const TOKEN_TYPE_KEY = 'token_type'
const USER_KEY = 'user'
const REMEMBERED_ACCOUNT_KEY = 'remembered_login_account'

function normalizeAuthData(authData) {
  return {
    accessToken: authData?.access_token || authData?.token || authData?.accessToken || '',
    tokenType: authData?.token_type || authData?.tokenType || 'bearer',
    user: authData?.user || authData?.user_info || authData?.profile || null,
  }
}

export function migrateLegacyAuthData() {
  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY)
  const legacyToken = localStorage.getItem(LEGACY_TOKEN_KEY)

  if (!accessToken && legacyToken) {
    localStorage.setItem(ACCESS_TOKEN_KEY, legacyToken)
  }

  if (legacyToken) {
    localStorage.removeItem(LEGACY_TOKEN_KEY)
  }

  return accessToken || legacyToken || ''
}

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY) || migrateLegacyAuthData()
}

export function getTokenType() {
  return localStorage.getItem(TOKEN_TYPE_KEY) || 'bearer'
}

export function getStoredUser() {
  const storedUser = localStorage.getItem(USER_KEY)

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

export function setStoredUser(user) {
  if (!user) {
    localStorage.removeItem(USER_KEY)
    return
  }

  localStorage.setItem(USER_KEY, JSON.stringify(user))
}

export function setAuthData(authData) {
  const normalized = normalizeAuthData(authData)

  if (!normalized.accessToken) {
    throw new Error('认证接口未返回访问令牌')
  }

  localStorage.setItem(ACCESS_TOKEN_KEY, normalized.accessToken)
  localStorage.setItem(TOKEN_TYPE_KEY, normalized.tokenType)
  localStorage.removeItem(LEGACY_TOKEN_KEY)
  setStoredUser(normalized.user)

  return normalized
}

export function clearAuthData() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(LEGACY_TOKEN_KEY)
  localStorage.removeItem(TOKEN_TYPE_KEY)
  localStorage.removeItem(USER_KEY)
}

export function getRememberedAccount() {
  return localStorage.getItem(REMEMBERED_ACCOUNT_KEY) || ''
}

export function setRememberedAccount(account) {
  const normalizedAccount = String(account || '').trim()

  if (!normalizedAccount) {
    clearRememberedAccount()
    return
  }

  localStorage.setItem(REMEMBERED_ACCOUNT_KEY, normalizedAccount)
}

export function clearRememberedAccount() {
  localStorage.removeItem(REMEMBERED_ACCOUNT_KEY)
}
