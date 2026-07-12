import request from '../utils/request.js'

const KNOWLEDGE_BASE_URL = '/knowledge-items'

/**
 * 获取知识列表。
 */
export function getKnowledgeListApi(params = {}) {
  return request.get(
    KNOWLEDGE_BASE_URL,
    {
      params,
    },
  )
}

/**
 * 获取单条知识详情。
 */
export function getKnowledgeDetailApi(knowledgeId) {
  return request.get(
    `${KNOWLEDGE_BASE_URL}/${knowledgeId}`,
  )
}

/**
 * 新增知识。
 */
export function createKnowledgeApi(data) {
  return request.post(
    KNOWLEDGE_BASE_URL,
    data,
  )
}

/**
 * 修改知识。
 */
export function updateKnowledgeApi(
  knowledgeId,
  data,
) {
  return request.put(
    `${KNOWLEDGE_BASE_URL}/${knowledgeId}`,
    data,
  )
}

/**
 * 记录知识引用次数。
 */
export function recordKnowledgeUsageApi(
  knowledgeId,
) {
  return request.post(
    `${KNOWLEDGE_BASE_URL}/${knowledgeId}/use`,
  )
}

/**
 * 删除知识。
 */
export function deleteKnowledgeApi(knowledgeId) {
  return request.delete(
    `${KNOWLEDGE_BASE_URL}/${knowledgeId}`,
  )
}