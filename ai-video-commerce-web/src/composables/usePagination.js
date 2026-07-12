import {
  computed,
  ref,
  unref,
  watch,
} from 'vue'

/**
 * 通用前端分页。
 *
 * sourceList 支持 ref 或 computed。
 */
export function usePagination(
  sourceList,
  defaultPageSize = 10,
) {
  const initialPageSize =
    Number(defaultPageSize) > 0
      ? Number(defaultPageSize)
      : 10

  const currentPage = ref(1)
  const pageSize = ref(
    initialPageSize,
  )

  /**
   * 获取安全的源数组。
   */
  const normalizedList =
    computed(() => {
      const list =
        unref(sourceList)

      return Array.isArray(list)
        ? list
        : []
    })

  const total = computed(
    () =>
      normalizedList.value
        .length,
  )

  const maxPage = computed(() => {
    return Math.max(
      1,
      Math.ceil(
        total.value /
          pageSize.value,
      ),
    )
  })

  const pageList = computed(() => {
    const start =
      (currentPage.value - 1) *
      pageSize.value

    return normalizedList
      .value
      .slice(
        start,
        start + pageSize.value,
      )
  })

  /**
   * 将当前页重置为第一页。
   */
  function resetPage() {
    currentPage.value = 1
  }

  /**
   * 修改每页数量。
   */
  function changePageSize(size) {
    const normalizedSize =
      Number(size)

    if (
      !Number.isFinite(
        normalizedSize,
      ) ||
      normalizedSize <= 0
    ) {
      return
    }

    pageSize.value =
      normalizedSize

    resetPage()
  }

  /**
   * 安全修改当前页。
   */
  function changeCurrentPage(page) {
    const normalizedPage =
      Number(page)

    if (
      !Number.isFinite(
        normalizedPage,
      )
    ) {
      return
    }

    currentPage.value =
      Math.min(
        Math.max(
          1,
          normalizedPage,
        ),
        maxPage.value,
      )
  }

  /**
   * 当数据量或每页数量变化时，
   * 保证当前页不会超过最大页数。
   */
  function syncCurrentPage() {
    if (
      currentPage.value >
      maxPage.value
    ) {
      currentPage.value =
        maxPage.value
    }

    if (
      currentPage.value < 1
    ) {
      currentPage.value = 1
    }
  }

  watch(
    [
      total,
      pageSize,
    ],
    syncCurrentPage,
    {
      immediate: true,
    },
  )

  return {
    currentPage,
    pageSize,
    total,
    maxPage,
    pageList,
    resetPage,
    changePageSize,
    changeCurrentPage,
  }
}