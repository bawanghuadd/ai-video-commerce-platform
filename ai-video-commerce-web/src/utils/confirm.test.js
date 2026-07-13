import {
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vitest'

vi.mock('element-plus', () => ({
  ElMessageBox: {
    confirm: vi.fn(),
  },
}))

import {
  ElMessageBox,
} from 'element-plus'
import {
  confirmAction,
  confirmDelete,
} from './confirm.js'

describe('confirmation utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns true after confirmation', async () => {
    ElMessageBox.confirm.mockResolvedValue('confirm')

    await expect(
      confirmDelete('商品'),
    ).resolves.toBe(true)
  })

  it.each(['cancel', 'close'])('returns false after %s', async (reason) => {
    ElMessageBox.confirm.mockRejectedValue(reason)

    await expect(
      confirmAction('继续操作吗？', '操作确认'),
    ).resolves.toBe(false)
  })

  it('rethrows unexpected confirmation errors', async () => {
    const error = new Error('dialog failed')
    ElMessageBox.confirm.mockRejectedValue(error)

    await expect(
      confirmAction('继续操作吗？', '操作确认'),
    ).rejects.toBe(error)
  })
})
