import axios from 'axios'

import { clearAuthData, getAccessToken } from './authStorage.js'

export function resolveSuccessData(response) {
  const payload = response?.data

  if (
    payload &&
    typeof payload === 'object' &&
    Object.prototype.hasOwnProperty.call(payload, 'code') &&
    Object.prototype.hasOwnProperty.call(payload, 'data')
  ) {
    return payload.data
  }

  return payload
}
export function createUnauthorizedHandler(options = {}) {
  const clearAuth = options.clearAuth || clearAuthData
  const getPath = options.getPath || (() => window.location.pathname)
  const navigate = options.navigate || ((path) => window.location.replace(path))

  let isHandlingUnauthorized = false

  return function handleUnauthorized(error) {
    if (error?.response?.status !== 401 || getPath() === '/login' || isHandlingUnauthorized) {
      return false
    }

    isHandlingUnauthorized = true
    clearAuth()
    navigate('/login')

    return true
  }
}

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
})

const handleUnauthorized = createUnauthorizedHandler()

request.interceptors.request.use(
  (config) => {
    const token = getAccessToken()

    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    return config
  },
  (error) => Promise.reject(error),
)

request.interceptors.response.use(
  resolveSuccessData,
  (error) => {
    handleUnauthorized(error)
    return Promise.reject(error)
  },
)

export default request
