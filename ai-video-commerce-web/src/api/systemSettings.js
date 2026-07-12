import request from '../utils/request.js'

const SYSTEM_SETTINGS_BASE_URL =
  '/system-settings'

/**
 * 获取系统设置。
 */
export function getSystemSettingsApi() {
  return request.get(
    SYSTEM_SETTINGS_BASE_URL,
  )
}

/**
 * 更新系统设置。
 */
export function updateSystemSettingsApi(
  data,
) {
  return request.put(
    SYSTEM_SETTINGS_BASE_URL,
    data,
  )
}