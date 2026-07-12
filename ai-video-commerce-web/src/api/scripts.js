import request from '../utils/request.js'

const SCRIPTS_BASE_URL = '/scripts'

/**
 * 获取脚本列表。
 */
export function getScriptListApi(
  params = {},
) {
  return request.get(
    SCRIPTS_BASE_URL,
    {
      params,
    },
  )
}

/**
 * 获取脚本详情。
 */
export function getScriptDetailApi(
  scriptId,
) {
  return request.get(
    `${SCRIPTS_BASE_URL}/${scriptId}`,
  )
}

/**
 * 新增脚本及分镜。
 */
export function createScriptApi(data) {
  return request.post(
    SCRIPTS_BASE_URL,
    data,
  )
}

/**
 * 修改脚本及分镜。
 */
export function updateScriptApi(
  scriptId,
  data,
) {
  return request.put(
    `${SCRIPTS_BASE_URL}/${scriptId}`,
    data,
  )
}

/**
 * 删除脚本。
 */
export function deleteScriptApi(
  scriptId,
) {
  return request.delete(
    `${SCRIPTS_BASE_URL}/${scriptId}`,
  )
}