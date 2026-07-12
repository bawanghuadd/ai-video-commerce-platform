import { ref } from 'vue'
import { ElMessage } from 'element-plus'

import {
  getApiErrorMessage,
  resolveApiList,
} from '../utils/apiResponse.js'

/**
 * 通用异步列表加载逻辑。
 *
 * @param {Function} requestFunction 列表接口函数
 * @param {Object} options 配置项
 * @param {string} options.errorMessage 默认错误提示
 * @param {boolean} options.showError 是否自动显示错误提示
 */
export function useAsyncList(
  requestFunction,
  options = {},
) {
  const {
    errorMessage = '数据加载失败',
    showError = true,
  } = options

  const list = ref([])
  const loading = ref(false)
  const error = ref(null)

  async function load(params = {}) {
    loading.value = true
    error.value = null

    try {
      const data =
        await requestFunction(params)

      list.value =
        resolveApiList(data)

      return list.value
    } catch (requestError) {
      error.value = requestError

      if (showError) {
        ElMessage.error(
          getApiErrorMessage(
            requestError,
            errorMessage,
          ),
        )
      }

      throw requestError
    } finally {
      loading.value = false
    }
  }

  function reset() {
    list.value = []
    error.value = null
  }

  return {
    list,
    loading,
    error,
    load,
    reset,
  }
}