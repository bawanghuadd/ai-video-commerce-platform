const ROLE_ALIASES = {
  user: 'editor',
}

const ROLE_PERMISSIONS = {
  admin: {
    canRead: true,
    canCreate: true,
    canUpdate: true,
    canDelete: true,
    canManageSettings: true,
    canManageUsers: true,
  },
  editor: {
    canRead: true,
    canCreate: true,
    canUpdate: true,
    canDelete: true,
    canManageSettings: false,
    canManageUsers: false,
  },
  viewer: {
    canRead: true,
    canCreate: false,
    canUpdate: false,
    canDelete: false,
    canManageSettings: false,
    canManageUsers: false,
  },
}

const NO_PERMISSIONS = Object.freeze({
  canRead: false,
  canCreate: false,
  canUpdate: false,
  canDelete: false,
  canManageSettings: false,
  canManageUsers: false,
})

export function normalizeRole(role) {
  const value = String(role || '').trim().toLowerCase()
  return ROLE_ALIASES[value] || value
}

export function getPermissions(user) {
  if (!user || user.is_active === false) {
    return NO_PERMISSIONS
  }
  return ROLE_PERMISSIONS[normalizeRole(user.role)] || NO_PERMISSIONS
}

export const canRead = (user) => getPermissions(user).canRead
export const canCreate = (user) => getPermissions(user).canCreate
export const canUpdate = (user) => getPermissions(user).canUpdate
export const canDelete = (user) => getPermissions(user).canDelete
export const canManageSettings = (user) => getPermissions(user).canManageSettings
export const canManageUsers = (user) => getPermissions(user).canManageUsers
