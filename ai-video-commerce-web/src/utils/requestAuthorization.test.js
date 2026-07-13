import { describe, expect, it, vi } from 'vitest'

import { createUnauthorizedHandler } from './request.js'


describe('request authorization handling', () => {
  it('does not clear or redirect the session for a 403 response', () => {
    const clearAuth = vi.fn()
    const navigate = vi.fn()
    const handleUnauthorized = createUnauthorizedHandler({
      clearAuth,
      getPath: () => '/products',
      navigate,
    })

    expect(handleUnauthorized({ response: { status: 403 } })).toBe(false)
    expect(clearAuth).not.toHaveBeenCalled()
    expect(navigate).not.toHaveBeenCalled()
  })
})
