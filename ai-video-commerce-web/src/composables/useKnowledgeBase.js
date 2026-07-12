import {
  computed,
  onMounted,
  reactive,
  ref,
} from 'vue'

import {
  ElMessage,
} from 'element-plus'

import {
  deleteKnowledgeApi,
  getKnowledgeListApi,
  recordKnowledgeUsageApi,
} from '../api/knowledge.js'

import {
  getProductListApi,
} from '../api/products.js'

import {
  useAsyncList,
} from './useAsyncList.js'

import {
  usePagination,
} from './usePagination.js'

import {
  getApiErrorMessage,
} from '../utils/apiResponse.js'

import {
  confirmDelete,
} from '../utils/confirm.js'


export function useKnowledgeBase() {
  /* ==============================
     页面状态
  ================================ */

  const formVisible = ref(false)
  const detailVisible = ref(false)

  const editingKnowledge = ref(null)
  const selectedKnowledge = ref(null)

  const usingKnowledgeId = ref(null)


  /* ==============================
     筛选条件
  ================================ */

  const filters = reactive({
    keyword: '',
    category: '',
    status: '',
    product_id: null,
    is_featured: null,
  })


  /* ==============================
     知识列表
  ================================ */

  const {
    list: knowledgeList,
    loading,
    load: requestKnowledgeList,
  } = useAsyncList(
    getKnowledgeListApi,
    {
      errorMessage: '知识库加载失败',
    },
  )


  /* ==============================
     商品列表
  ================================ */

  const {
    list: productList,
    loading: productLoading,
    load: requestProductList,
  } = useAsyncList(
    getProductListApi,
    {
      errorMessage: '商品列表加载失败',
    },
  )


  /* ==============================
     分页
  ================================ */

  const {
    currentPage,
    pageSize,
    total: totalRecords,
    pageList,
    resetPage,
    changePageSize,
  } = usePagination(
    knowledgeList,
    8,
  )


  /* ==============================
     统计数据
  ================================ */

  const publishedCount = computed(() => {
    return knowledgeList.value.filter(
      (item) => {
        return item.status === '已发布'
      },
    ).length
  })


  const featuredCount = computed(() => {
    return knowledgeList.value.filter(
      (item) => {
        return Boolean(
          item.is_featured,
        )
      },
    ).length
  })


  const totalUsageCount = computed(() => {
    return knowledgeList.value.reduce(
      (total, item) => {
        return (
          total +
          Number(
            item.usage_count || 0,
          )
        )
      },
      0,
    )
  })


  /* ==============================
     构建查询参数
  ================================ */

  function buildQueryParams() {
    const params = {}

    const keyword =
      String(
        filters.keyword || '',
      ).trim()

    if (keyword) {
      params.keyword = keyword
    }

    if (filters.category) {
      params.category =
        filters.category
    }

    if (filters.status) {
      params.status =
        filters.status
    }

    if (filters.product_id) {
      params.product_id =
        Number(
          filters.product_id,
        )
    }

    if (
      filters.is_featured !== null &&
      filters.is_featured !== undefined
    ) {
      params.is_featured =
        Boolean(
          filters.is_featured,
        )
    }

    return params
  }


  /* ==============================
     加载知识列表
  ================================ */

  async function loadKnowledgeList() {
    const params =
      buildQueryParams()

    try {
      await requestKnowledgeList(
        params,
      )
    } catch {
      /*
       * useAsyncList 内部已经显示错误提示，
       * 这里不再重复提示。
       */
    }
  }


  /* ==============================
     加载商品列表
  ================================ */

  async function loadProductList() {
    try {
      await requestProductList()
    } catch {
      /*
       * useAsyncList 内部已经显示错误提示。
       */
    }
  }


  /* ==============================
     查询知识
  ================================ */

  async function searchKnowledge(
    nextFilters = null,
  ) {
    if (
      nextFilters &&
      typeof nextFilters === 'object'
    ) {
      Object.assign(
        filters,
        nextFilters,
      )
    }

    resetPage()

    await loadKnowledgeList()
  }


  /* ==============================
     重置筛选
  ================================ */

  async function resetFilters(
    nextFilters = null,
  ) {
    if (
      nextFilters &&
      typeof nextFilters === 'object'
    ) {
      Object.assign(
        filters,
        nextFilters,
      )
    } else {
      Object.assign(filters, {
        keyword: '',
        category: '',
        status: '',
        product_id: null,
        is_featured: null,
      })
    }

    resetPage()

    await loadKnowledgeList()
  }


  /* ==============================
     刷新知识列表
  ================================ */

  async function refreshKnowledge() {
    await loadKnowledgeList()
  }


  /* ==============================
     打开新增弹窗
  ================================ */

  function openCreate() {
    editingKnowledge.value = null
    formVisible.value = true
  }


  /* ==============================
     打开编辑弹窗
  ================================ */

  function openEdit(item) {
    if (!item) {
      return
    }

    editingKnowledge.value = {
      ...item,

      tags:
        Array.isArray(item.tags)
          ? [...item.tags]
          : [],
    }

    detailVisible.value = false
    formVisible.value = true
  }


  /* ==============================
     打开详情抽屉
  ================================ */

  function openDetail(item) {
    if (!item) {
      return
    }

    selectedKnowledge.value = {
      ...item,

      tags:
        Array.isArray(item.tags)
          ? [...item.tags]
          : [],
    }

    detailVisible.value = true
  }


  /* ==============================
     删除知识
  ================================ */

  async function deleteKnowledge(item) {
    if (!item?.id) {
      ElMessage.warning(
        '当前知识记录不存在',
      )
      return
    }

    const confirmed =
      await confirmDelete(
        item.title || '未命名知识',
        {
          title:
            '删除知识库条目',
        },
      )

    if (!confirmed) {
      return
    }

    try {
      await deleteKnowledgeApi(
        item.id,
      )

      if (
        selectedKnowledge.value?.id ===
        item.id
      ) {
        selectedKnowledge.value = null
        detailVisible.value = false
      }

      if (
        editingKnowledge.value?.id ===
        item.id
      ) {
        editingKnowledge.value = null
        formVisible.value = false
      }

      ElMessage.success(
        '知识库条目删除成功',
      )

      await loadKnowledgeList()
    } catch (error) {
      ElMessage.error(
        getApiErrorMessage(
          error,
          '知识库条目删除失败',
        ),
      )
    }
  }


  /* ==============================
     引用知识
  ================================ */

  async function useKnowledge(item) {
    if (!item?.id) {
      ElMessage.warning(
        '当前知识记录不存在',
      )
      return
    }

    if (
      usingKnowledgeId.value !== null
    ) {
      return
    }

    usingKnowledgeId.value =
      item.id

    try {
      await recordKnowledgeUsageApi(
        item.id,
      )

      ElMessage.success(
        '知识引用成功',
      )

      /*
       * 先更新详情中的引用次数，
       * 避免用户等待列表刷新。
       */
      if (
        selectedKnowledge.value?.id ===
        item.id
      ) {
        selectedKnowledge.value = {
          ...selectedKnowledge.value,

          usage_count:
            Number(
              selectedKnowledge.value
                .usage_count || 0,
            ) + 1,
        }
      }

      await loadKnowledgeList()
    } catch (error) {
      ElMessage.error(
        getApiErrorMessage(
          error,
          '知识引用失败',
        ),
      )
    } finally {
      usingKnowledgeId.value = null
    }
  }


  /* ==============================
     表单提交成功
  ================================ */

  async function handleFormSuccess() {
    editingKnowledge.value = null

    await loadKnowledgeList()
  }


  /* ==============================
     关闭表单
  ================================ */

  function closeForm() {
    formVisible.value = false
    editingKnowledge.value = null
  }


  /* ==============================
     关闭详情
  ================================ */

  function closeDetail() {
    detailVisible.value = false
    selectedKnowledge.value = null
  }


  /* ==============================
     获取商品名称
  ================================ */

  function getProductName(
    productId,
  ) {
    if (!productId) {
      return '通用知识'
    }

    const product =
      productList.value.find(
        (item) => {
          return (
            Number(item.id) ===
            Number(productId)
          )
        },
      )

    return (
      product?.product_name ||
      product?.name ||
      `商品 ID：${productId}`
    )
  }


  /* ==============================
     初始化
  ================================ */

  async function initializeKnowledgeBase() {
    await Promise.all([
      loadProductList(),
      loadKnowledgeList(),
    ])
  }


  onMounted(() => {
    initializeKnowledgeBase()
  })


  /* ==============================
     对外暴露
  ================================ */

  return {
    /* 状态 */
    loading,
    productLoading,
    usingKnowledgeId,

    formVisible,
    detailVisible,

    editingKnowledge,
    selectedKnowledge,

    /* 数据 */
    filters,
    knowledgeList,
    productList,
    pageList,

    /* 分页 */
    currentPage,
    pageSize,
    totalRecords,
    resetPage,
    changePageSize,

    /* 统计 */
    publishedCount,
    featuredCount,
    totalUsageCount,

    /* 数据加载 */
    loadKnowledgeList,
    loadProductList,
    refreshKnowledge,
    initializeKnowledgeBase,

    /* 筛选 */
    searchKnowledge,
    resetFilters,

    /* 弹窗 */
    openCreate,
    openEdit,
    openDetail,
    closeForm,
    closeDetail,

    /* 业务操作 */
    deleteKnowledge,
    useKnowledge,
    handleFormSuccess,

    /* 工具 */
    getProductName,
  }
}