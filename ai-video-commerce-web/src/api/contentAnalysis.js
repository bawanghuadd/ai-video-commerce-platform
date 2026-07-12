import request from '../utils/request.js'

const CONTENT_ANALYSIS_BASE_URL =
  '/content-analyses'

/**
 * 获取内容拆解列表。
 */
export function getContentAnalysisListApi(
  params = {},
) {
  return request.get(
    CONTENT_ANALYSIS_BASE_URL,
    {
      params,
    },
  )
}

/**
 * 获取内容拆解详情。
 */
export function getContentAnalysisDetailApi(
  analysisId,
) {
  return request.get(
    `${CONTENT_ANALYSIS_BASE_URL}/${analysisId}`,
  )
}

/**
 * 新增内容拆解记录。
 */
export function createContentAnalysisApi(data) {
  return request.post(
    CONTENT_ANALYSIS_BASE_URL,
    data,
  )
}

/**
 * 修改内容拆解记录。
 */
export function updateContentAnalysisApi(
  analysisId,
  data,
) {
  return request.put(
    `${CONTENT_ANALYSIS_BASE_URL}/${analysisId}`,
    data,
  )
}

/**
 * 删除内容拆解记录。
 */
export function deleteContentAnalysisApi(
  analysisId,
) {
  return request.delete(
    `${CONTENT_ANALYSIS_BASE_URL}/${analysisId}`,
  )
}