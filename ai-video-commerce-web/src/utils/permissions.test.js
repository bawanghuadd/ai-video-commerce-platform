import { describe, expect, it } from 'vitest'

import { getPermissions, normalizeRole } from './permissions.js'


describe('permissions', () => {
  it('keeps legacy user compatible with editor', () => {
    expect(normalizeRole('user')).toBe('editor')
    expect(getPermissions({ role: 'user', is_active: true }).canCreate).toBe(true)
  })

  it('allows viewer reads but denies writes', () => {
    const permissions = getPermissions({ role: 'viewer', is_active: true })
    expect(permissions.canRead).toBe(true)
    expect(permissions.canCreate).toBe(false)
    expect(permissions.canManageSettings).toBe(false)
  })

  it('allows only admin to manage settings and users', () => {
    const permissions = getPermissions({ role: 'admin', is_active: true })
    expect(permissions.canManageSettings).toBe(true)
    expect(permissions.canManageUsers).toBe(true)
  })

  it('denies inactive and unknown users', () => {
    expect(getPermissions({ role: 'admin', is_active: false }).canRead).toBe(false)
    expect(getPermissions({ role: 'unknown', is_active: true }).canRead).toBe(false)
  })
})
