import {
  nextTick,
  ref,
} from 'vue'
import {
  describe,
  expect,
  it,
} from 'vitest'

import {
  usePagination,
} from './usePagination.js'

describe('usePagination', () => {
  it('paginates a ref list and changes pages safely', () => {
    const source = ref([1, 2, 3, 4, 5])
    const pagination = usePagination(source, 2)

    expect(pagination.total.value).toBe(5)
    expect(pagination.pageList.value).toEqual([1, 2])

    pagination.changeCurrentPage(2)

    expect(pagination.pageList.value).toEqual([3, 4])
  })

  it('moves back after deleting the last page', async () => {
    const source = ref([1, 2, 3])
    const pagination = usePagination(source, 2)

    pagination.changeCurrentPage(2)
    source.value.pop()
    await nextTick()

    expect(pagination.currentPage.value).toBe(1)
    expect(pagination.pageList.value).toEqual([1, 2])
  })

  it('degrades a non-array source to an empty list', () => {
    const pagination = usePagination(ref(null), 10)

    expect(pagination.total.value).toBe(0)
    expect(pagination.pageList.value).toEqual([])
  })
})
