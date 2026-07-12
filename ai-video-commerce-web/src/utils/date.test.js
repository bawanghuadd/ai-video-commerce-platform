import {
  describe,
  expect,
  it,
} from 'vitest'

import {
  formatDate,
  formatDateTime,
} from './date.js'

describe('date utilities', () => {
  it('formats a local date consistently', () => {
    const value = new Date(2026, 6, 13, 15, 30)

    expect(formatDate(value)).toBe('2026-07-13')
    expect(formatDateTime(value)).toBe('2026-07-13 15:30')
  })

  it('handles empty and invalid values safely', () => {
    expect(formatDate(null)).toBe('-')
    expect(formatDateTime('not-a-date')).toBe('not-a-date')
  })
})
