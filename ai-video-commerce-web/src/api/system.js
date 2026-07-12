import request from '../utils/request.js'

const SYSTEM_BASE_URL = '/health'

/**
 * 获取后端服务健康状态。
 */
export function getHealthStatusApi() {
  return request.get(SYSTEM_BASE_URL)
}

/**
 * 兼容旧函数名称。
 */
export const getHealthStatus =
  getHealthStatusApi