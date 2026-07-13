function isBackendEnvelope(value) {
  return Boolean(
    value &&
      typeof value === 'object' &&
      Object.prototype.hasOwnProperty.call(value, 'code') &&
      Object.prototype.hasOwnProperty.call(value, 'data'),
  )
}

function isAxiosResponse(value) {
  return Boolean(
    value &&
      typeof value === 'object' &&
      Object.prototype.hasOwnProperty.call(value, 'data') &&
      (
        Object.prototype.hasOwnProperty.call(value, 'status') ||
        Object.prototype.hasOwnProperty.call(value, 'headers') ||
        Object.prototype.hasOwnProperty.call(value, 'config')
      ),
  )
}

/**
 * Transitional compatibility for legacy callers.
 * New API callers already receive business data from request.js.
 */
export function resolveApiData(response) {
  if (isBackendEnvelope(response)) {
    return response.data
  }

  if (isAxiosResponse(response)) {
    return isBackendEnvelope(response.data)
      ? response.data.data
      : response.data
  }

  return response
}

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