import { describe, expect, it, vi } from 'vitest'

import {
  createUnauthorizedHandler,
  resolveSuccessData,
} from './request.js'

describe('request unauthorized handling', () => {
  it('clears and redirects only once for concurrent 401 errors', () => {
    const clearAuth = vi.fn()
    const navigate = vi.fn()
    const handleUnauthorized = createUnauthorizedHandler({
      clearAuth,
      getPath: () => '/products',
      navigate,
    })
    const error = { response: { status: 401 } }

    expect(handleUnauthorized(error)).toBe(true)
    expect(handleUnauthorized(error)).toBe(false)
    expect(clearAuth).toHaveBeenCalledTimes(1)
    expect(navigate).toHaveBeenCalledOnce()
    expect(navigate).toHaveBeenCalledWith('/login')
  })

  it('does not redirect a failed login request', () => {
    const clearAuth = vi.fn()
    const navigate = vi.fn()
    const handleUnauthorized = createUnauthorizedHandler({
      clearAuth,
      getPath: () => '/login',
      navigate,
    })

    expect(handleUnauthorized({ response: { status: 401 } })).toBe(false)
    expect(clearAuth).not.toHaveBeenCalled()
    expect(navigate).not.toHaveBeenCalled()
  })
})
describe('request success handling', () => {
  it('unwraps the backend envelope to business data', () => {
    const data = [{ id: 1 }]

    expect(
      resolveSuccessData({
        data: {
          code: 200,
          message: 'ok',
          data,
        },
      }),
    ).toBe(data)
  })

  it('keeps a direct Axios business payload compatible', () => {
    const data = { id: 1 }

    expect(resolveSuccessData({ data })).toBe(data)
  })
})