import request from '../utils/request.js'

const AUTH_BASE_URL = '/auth'

/**
 * 用户登录。
 */
export function loginApi(data) {
  return request.post(
    `${AUTH_BASE_URL}/login`,
    data,
  )
}

/**
 * 用户注册。
 */
export function registerApi(data) {
  return request.post(
    `${AUTH_BASE_URL}/register`,
    data,
  )
}

/**
 * 获取当前登录用户信息。
 */
export function getCurrentUserApi() {
  return request.get(
    `${AUTH_BASE_URL}/me`,
  )
}
