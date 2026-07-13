import {
  readFileSync,
} from 'node:fs'
import {
  describe,
  expect,
  it,
} from 'vitest'

import {
  KNOWLEDGE_STATUS_OPTIONS,
} from './knowledge.js'
import {
  SCRIPT_STATUS_OPTIONS,
} from './scripts.js'
import {
  VIDEO_TASK_STATUS_OPTIONS,
} from './videoTasks.js'

function readBackendSchema(fileName) {
  return readFileSync(
    new URL(
      `../../../ai-video-commerce-api/app/schemas/${fileName}`,
      import.meta.url,
    ),
    'utf8',
  )
}

describe('frontend status contract', () => {
  it.each([
    ['script.py', SCRIPT_STATUS_OPTIONS],
    ['video_task.py', VIDEO_TASK_STATUS_OPTIONS],
    ['knowledge.py', KNOWLEDGE_STATUS_OPTIONS],
  ])('keeps %s status values aligned', (schemaFile, statuses) => {
    const schema = readBackendSchema(schemaFile)

    for (const status of statuses) {
      expect(schema).toContain(`"${status}"`)
    }
  })
})
