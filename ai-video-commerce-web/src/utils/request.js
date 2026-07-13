import axios from 'axios'

import { clearAuthData, getAccessToken } from './authStorage.js'

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
  baseURL: 'http://127.0.0.1:8000/api',
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
  (response) => response.data,
  (error) => {
    handleUnauthorized(error)
    return Promise.reject(error)
  },
)

export default request
