/**
 * 从不同格式的接口响应中提取业务数据。
 *
 * 当前 Axios 拦截器已经自动解包 data，
 * 这里暂时保留兼容逻辑，避免旧页面立即报错。
 */
export function resolveApiData(response) {
  if (response?.data?.data !== undefined) {
    return response.data.data
  }

  if (response?.data !== undefined) {
    return response.data
  }

  return response
}

/**
 * 从接口响应中提取列表数据。
 *
 * 兼容以下结构：
 * - 数组
 * - { items: [] }
 * - { list: [] }
 */
export function resolveApiList(response) {
  const data = resolveApiData(response)

  if (Array.isArray(data)) {
    return data
  }

  if (Array.isArray(data?.items)) {
    return data.items
  }

  if (Array.isArray(data?.list)) {
    return data.list
  }

  return []
}

/**
 * 从 Axios 或 FastAPI 错误中提取可读信息。
 */
export function getApiErrorMessage(
  error,
  fallbackMessage = '请求失败',
) {
  const responseData = error?.response?.data
  const detail = responseData?.detail

  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const messages = detail
      .map((item) => item?.msg)
      .filter(Boolean)

    if (messages.length > 0) {
      return messages.join('；')
    }
  }

  return (
    responseData?.message ||
    error?.message ||
    fallbackMessage
  )
}