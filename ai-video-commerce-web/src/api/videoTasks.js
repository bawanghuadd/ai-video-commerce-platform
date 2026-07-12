import request from '../utils/request.js'

const VIDEO_TASKS_BASE_URL = '/video-tasks'

/**
 * 获取视频任务列表。
 */
export function getVideoTaskListApi(
  params = {},
) {
  return request.get(
    VIDEO_TASKS_BASE_URL,
    {
      params,
    },
  )
}

/**
 * 获取视频任务详情。
 */
export function getVideoTaskDetailApi(
  videoTaskId,
) {
  return request.get(
    `${VIDEO_TASKS_BASE_URL}/${videoTaskId}`,
  )
}

/**
 * 新增视频任务。
 */
export function createVideoTaskApi(data) {
  return request.post(
    VIDEO_TASKS_BASE_URL,
    data,
  )
}

/**
 * 修改视频任务。
 */
export function updateVideoTaskApi(
  videoTaskId,
  data,
) {
  return request.put(
    `${VIDEO_TASKS_BASE_URL}/${videoTaskId}`,
    data,
  )
}

/**
 * 删除视频任务。
 */
export function deleteVideoTaskApi(
  videoTaskId,
) {
  return request.delete(
    `${VIDEO_TASKS_BASE_URL}/${videoTaskId}`,
  )
}