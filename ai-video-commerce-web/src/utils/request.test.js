import { describe, expect, it, vi } from 'vitest'

import { createUnauthorizedHandler } from './request.js'

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
