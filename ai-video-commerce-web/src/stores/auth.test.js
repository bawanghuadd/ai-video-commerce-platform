import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

vi.mock('../api/auth.js', () => ({
  getCurrentUserApi: vi.fn(),
  loginApi: vi.fn(),
  registerApi: vi.fn(),
}))

import { getCurrentUserApi, loginApi, registerApi } from '../api/auth.js'
import { useAuthStore } from './auth.js'

function createStorage() {
  const values = new Map()

  return {
    getItem: (key) => (values.has(key) ? values.get(key) : null),
    setItem: (key, value) => values.set(key, String(value)),
    removeItem: (key) => values.delete(key),
    clear: () => values.clear(),
  }
}

describe('auth store', () => {
  beforeEach(() => {
    Object.defineProperty(globalThis, 'localStorage', {
      configurable: true,
      value: createStorage(),
    })
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('persists normal login data', async () => {
    loginApi.mockResolvedValue({
      access_token: 'login-token',
      user: { id: 1, username: 'admin' },
    })

    const store = useAuthStore()
    await store.login({ username: 'admin', password: 'secret' })

    expect(store.token).toBe('login-token')
    expect(store.user).toEqual({ id: 1, username: 'admin' })
  })

  it('uses a register response that already contains a token', async () => {
    registerApi.mockResolvedValue({
      access_token: 'register-token',
      user: { id: 2, username: 'new_user' },
    })

    const store = useAuthStore()
    await store.register({ username: 'new_user', password: 'secret' })

    expect(store.token).toBe('register-token')
    expect(loginApi).not.toHaveBeenCalled()
  })

  it('logs in when register does not return a token', async () => {
    registerApi.mockResolvedValue({ user: { id: 2 } })
    loginApi.mockResolvedValue({
      access_token: 'fallback-token',
      user: { id: 2, username: 'new_user' },
    })

    const store = useAuthStore()
    await store.register({ username: 'new_user', password: 'secret' })

    expect(loginApi).toHaveBeenCalledWith({
      username: 'new_user',
      password: 'secret',
    })
    expect(store.token).toBe('fallback-token')
  })

  it('loads the current user and clears state on logout', async () => {
    getCurrentUserApi.mockResolvedValue({ id: 3, username: 'viewer' })

    const store = useAuthStore()
    await store.loadCurrentUser()
    expect(store.user).toEqual({ id: 3, username: 'viewer' })

    store.logout()
    expect(store.token).toBe('')
    expect(store.user).toBeNull()
  })
})
