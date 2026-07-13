import { beforeEach, describe, expect, it } from 'vitest'

import {
  clearAuthData,
  clearRememberedAccount,
  getAccessToken,
  getRememberedAccount,
  getStoredUser,
  getTokenType,
  migrateLegacyAuthData,
  setAuthData,
  setRememberedAccount,
} from './authStorage.js'

function createStorage() {
  const values = new Map()

  return {
    getItem(key) {
      return values.has(key) ? values.get(key) : null
    },
    setItem(key, value) {
      values.set(key, String(value))
    },
    removeItem(key) {
      values.delete(key)
    },
    clear() {
      values.clear()
    },
  }
}

describe('authStorage', () => {
  beforeEach(() => {
    Object.defineProperty(globalThis, 'localStorage', {
      configurable: true,
      value: createStorage(),
    })
  })

  it('stores normalized login data without the legacy key', () => {
    setAuthData({
      access_token: 'access-token',
      token_type: 'bearer',
      user: { id: 1, username: 'admin' },
    })

    expect(getAccessToken()).toBe('access-token')
    expect(getTokenType()).toBe('bearer')
    expect(getStoredUser()).toEqual({ id: 1, username: 'admin' })
    expect(localStorage.getItem('token')).toBeNull()
  })

  it('migrates and removes a legacy token once', () => {
    localStorage.setItem('token', 'legacy-token')

    expect(migrateLegacyAuthData()).toBe('legacy-token')
    expect(localStorage.getItem('access_token')).toBe('legacy-token')
    expect(localStorage.getItem('token')).toBeNull()
  })

  it('cleans invalid user JSON safely', () => {
    localStorage.setItem('user', '{invalid')

    expect(getStoredUser()).toBeNull()
    expect(localStorage.getItem('user')).toBeNull()
  })

  it('clears all authentication fields on logout', () => {
    localStorage.setItem('access_token', 'token')
    localStorage.setItem('token', 'legacy')
    localStorage.setItem('token_type', 'bearer')
    localStorage.setItem('user', '{}')

    clearAuthData()

    expect(getAccessToken()).toBe('')
    expect(localStorage.getItem('token_type')).toBeNull()
    expect(getStoredUser()).toBeNull()
  })

  it('stores and clears the remembered account', () => {
    setRememberedAccount('  demo_user  ')
    expect(getRememberedAccount()).toBe('demo_user')

    clearRememberedAccount()
    expect(getRememberedAccount()).toBe('')
  })
})
