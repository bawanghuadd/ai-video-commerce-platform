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

/**
 * 兼容项目中可能存在的旧函数名称。
 * 后续确认没有旧调用后，可以删除这些别名。
 */
export const getMeApi =
  getCurrentUserApi

export const getMyProfileApi =
  getCurrentUserApi