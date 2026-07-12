<!-- <script setup>
import {
  computed,
  nextTick,
  onMounted,
  reactive,
  ref,
  watch,
} from 'vue'

import {
  ElMessage,
  ElMessageBox,
} from 'element-plus'

import {
  Delete,
  Edit,
  Goods,
  Plus,
  Refresh,
  Search,
} from '@element-plus/icons-vue'

import {
  createProductApi,
  deleteProductApi,
  getProductListApi,
  updateProductApi,
} from '../api/products'


/* ==============================
   基础状态
================================ */

const loading = ref(false)
const submitting = ref(false)

const productList = ref([])

const dialogVisible = ref(false)
const dialogMode = ref('create')
const editingProductId = ref(null)
const formRef = ref(null)

const currentPage = ref(1)
const pageSize = ref(10)


/* ==============================
   查询条件
================================ */

const filterForm = reactive({
  keyword: '',
  category: '',
  status: '',
})

const appliedFilters = reactive({
  keyword: '',
  category: '',
  status: '',
})


/* ==============================
   商品表单
================================ */

const productForm = reactive({
  product_name: '',
  category: '',
  price: 0.01,
  stock: 0,
  selling_points: '',
  target_audience: '',
})

const formRules = {
  product_name: [
    {
      required: true,
      message: '请输入商品名称',
      trigger: 'blur',
    },
    {
      min: 1,
      max: 100,
      message: '商品名称长度为1到100个字符',
      trigger: 'blur',
    },
  ],

  category: [
    {
      required: true,
      message: '请选择或输入商品分类',
      trigger: 'change',
    },
  ],

  price: [
    {
      required: true,
      message: '请输入商品价格',
      trigger: 'change',
    },
  ],

  stock: [
    {
      required: true,
      message: '请输入商品库存',
      trigger: 'change',
    },
  ],
}


/* ==============================
   计算属性
================================ */

const dialogTitle = computed(() => {
  return dialogMode.value === 'create'
    ? '新增商品'
    : '编辑商品'
})

const categoryOptions = computed(() => {
  const categories = productList.value
    .map((item) => item.category)
    .filter(Boolean)

  return [...new Set(categories)]
})

const filteredProductList = computed(() => {
  const keyword =
    appliedFilters.keyword.trim().toLowerCase()

  return productList.value.filter((product) => {
    const productName =
      String(product.product_name || '')
        .toLowerCase()

    const category =
      String(product.category || '')
        .toLowerCase()

    const productStatus =
      resolveProductStatus(product)

    const matchesKeyword =
      !keyword ||
      productName.includes(keyword) ||
      category.includes(keyword)

    const matchesCategory =
      !appliedFilters.category ||
      product.category === appliedFilters.category

    const matchesStatus =
      !appliedFilters.status ||
      productStatus === appliedFilters.status

    return (
      matchesKeyword &&
      matchesCategory &&
      matchesStatus
    )
  })
})

const totalProducts = computed(() => {
  return filteredProductList.value.length
})

const paginatedProductList = computed(() => {
  const start =
    (currentPage.value - 1) *
    pageSize.value

  return filteredProductList.value.slice(
    start,
    start + pageSize.value,
  )
})


/* ==============================
   数据处理
================================ */

function resolveProductStatus(product) {
  /*
   * 后端以后返回 status 时直接使用。
   * 当前没有 status 字段时，根据库存临时判断。
   */
  if (product.status) {
    return product.status
  }

  return Number(product.stock) > 0
    ? '上架'
    : '下架'
}

function getStatusType(product) {
  const status = resolveProductStatus(product)

  const typeMap = {
    上架: 'success',
    下架: 'warning',
    缺货: 'danger',
    草稿: 'info',
  }

  return typeMap[status] || 'info'
}

function formatPrice(value) {
  const number = Number(value || 0)

  return `¥${number.toFixed(2)}`
}

function formatDate(value) {
  if (!value) {
    return '-'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  const pad = (number) => {
    return String(number).padStart(2, '0')
  }

  return [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
  ].join('-') +
    ` ${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function getErrorMessage(
  error,
  fallbackMessage,
) {
  const detail =
    error?.response?.data?.detail

  if (typeof detail === 'string') {
    return detail
  }

  return (
    error?.response?.data?.message ||
    error?.message ||
    fallbackMessage
  )
}

function resolveListResponse(response) {
  /*
   * 兼容不同 Axios 拦截器返回结构：
   *
   * response.data = [...]
   * response.data.data = [...]
   * response = [...]
   */

  if (Array.isArray(response)) {
    return response
  }

  if (Array.isArray(response?.data)) {
    return response.data
  }

  if (
    Array.isArray(response?.data?.data)
  ) {
    return response.data.data
  }

  return []
}


/* ==============================
   查询商品
================================ */

async function loadProducts() {
  loading.value = true

  try {
    const response =
      await getProductListApi()

    productList.value =
      resolveListResponse(response)
  } catch (error) {
    ElMessage.error(
      getErrorMessage(
        error,
        '商品列表加载失败',
      ),
    )
  } finally {
    loading.value = false
  }
}


/* ==============================
   筛选操作
================================ */

function handleSearch() {
  Object.assign(appliedFilters, {
    keyword: filterForm.keyword,
    category: filterForm.category,
    status: filterForm.status,
  })

  currentPage.value = 1
}

function handleReset() {
  Object.assign(filterForm, {
    keyword: '',
    category: '',
    status: '',
  })

  Object.assign(appliedFilters, {
    keyword: '',
    category: '',
    status: '',
  })

  currentPage.value = 1
}

function handlePageSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1
}


/* ==============================
   新增与编辑
================================ */

function resetProductForm() {
  editingProductId.value = null

  Object.assign(productForm, {
    product_name: '',
    category: '',
    price: 0.01,
    stock: 0,
    selling_points: '',
    target_audience: '',
  })

  formRef.value?.clearValidate()
}

async function openCreateDialog() {
  dialogMode.value = 'create'
  resetProductForm()

  dialogVisible.value = true

  await nextTick()

  formRef.value?.clearValidate()
}

async function openEditDialog(product) {
  dialogMode.value = 'edit'
  editingProductId.value = product.id

  Object.assign(productForm, {
    product_name:
      product.product_name || '',

    category:
      product.category || '',

    price:
      Number(product.price || 0),

    stock:
      Number(product.stock || 0),

    selling_points:
      product.selling_points || '',

    target_audience:
      product.target_audience || '',
  })

  dialogVisible.value = true

  await nextTick()

  formRef.value?.clearValidate()
}

async function submitProduct() {
  if (!formRef.value) {
    return
  }

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  submitting.value = true

  /*
   * 当前只提交后端已经支持的字段。
   * image_url 和 status 等字段后续完善后端后再加入。
   */
  const submitData = {
    product_name:
      productForm.product_name.trim(),

    category:
      productForm.category.trim(),

    price:
      Number(productForm.price),

    stock:
      Number(productForm.stock),

    selling_points:
      productForm.selling_points.trim() ||
      null,

    target_audience:
      productForm.target_audience.trim() ||
      null,
  }

  try {
    if (dialogMode.value === 'create') {
      await createProductApi(submitData)

      ElMessage.success('商品创建成功')
    } else {
      await updateProductApi(
        editingProductId.value,
        submitData,
      )

      ElMessage.success('商品修改成功')
    }

    dialogVisible.value = false

    await loadProducts()
  } catch (error) {
    ElMessage.error(
      getErrorMessage(
        error,
        '商品保存失败',
      ),
    )
  } finally {
    submitting.value = false
  }
}


/* ==============================
   删除商品
================================ */

async function handleDelete(product) {
  try {
    await ElMessageBox.confirm(
      `确定删除商品“${product.product_name}”吗？`,
      '删除商品',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )

    await deleteProductApi(product.id)

    ElMessage.success('商品删除成功')

    await loadProducts()
  } catch (error) {
    if (
      error === 'cancel' ||
      error === 'close'
    ) {
      return
    }

    ElMessage.error(
      getErrorMessage(
        error,
        '商品删除失败',
      ),
    )
  }
}


/* ==============================
   图片处理
================================ */

function handleImageError(event) {
  /*
   * 商品图片加载失败时隐藏图片，
   * 自动显示下面的占位图标。
   */
  event.target.style.display = 'none'
}


/* ==============================
   生命周期
================================ */

watch(
  () => totalProducts.value,
  () => {
    const maxPage = Math.max(
      1,
      Math.ceil(
        totalProducts.value /
        pageSize.value,
      ),
    )

    if (currentPage.value > maxPage) {
      currentPage.value = maxPage
    }
  },
)

onMounted(() => {
  loadProducts()
})
</script> -->
<!-- <script setup>
import {
  computed,
  nextTick,
  onMounted,
  reactive,
  ref,
  watch,
} from 'vue'

import {
  ElMessage,
  ElMessageBox,
} from 'element-plus'

import {
  Delete,
  Edit,
  Goods,
  Plus,
  Refresh,
  Search,
} from '@element-plus/icons-vue'

import {
  createProductApi,
  deleteProductApi,
  getProductListApi,
  updateProductApi,
} from '../api/products.js'

import {
  useAsyncList,
} from '../composables/useAsyncList.js'

import {
  getApiErrorMessage,
} from '../utils/apiResponse.js'

const FILTER_DEFAULTS = {
  keyword: '',
  category: '',
  status: '',
}

const PRODUCT_FORM_DEFAULTS = {
  product_name: '',
  category: '',
  price: 0.01,
  stock: 0,
  selling_points: '',
  target_audience: '',
}

const STATUS_TYPE_MAP = {
  上架: 'success',
  下架: 'warning',
  缺货: 'danger',
  草稿: 'info',
}

/* ==============================
   基础状态
================================ */

const submitting = ref(false)

const dialogVisible = ref(false)
const dialogMode = ref('create')
const editingProductId = ref(null)
const formRef = ref(null)

const currentPage = ref(1)
const pageSize = ref(10)

/*
 * 商品列表、加载状态及接口错误提示，
 * 统一交给通用列表组合函数管理。
 */
const {
  list: productList,
  loading,
  load: loadProductList,
} = useAsyncList(
  getProductListApi,
  {
    errorMessage:
      '商品列表加载失败',
  },
)

/* ==============================
   查询条件
================================ */

const filterForm = reactive({
  ...FILTER_DEFAULTS,
})

const appliedFilters = reactive({
  ...FILTER_DEFAULTS,
})

/* ==============================
   商品表单
================================ */

const productForm = reactive({
  ...PRODUCT_FORM_DEFAULTS,
})

const formRules = {
  product_name: [
    {
      required: true,
      message: '请输入商品名称',
      trigger: 'blur',
    },
    {
      min: 1,
      max: 100,
      message:
        '商品名称长度为1到100个字符',
      trigger: 'blur',
    },
  ],

  category: [
    {
      required: true,
      message:
        '请选择或输入商品分类',
      trigger: 'change',
    },
  ],

  price: [
    {
      required: true,
      message: '请输入商品价格',
      trigger: 'change',
    },
  ],

  stock: [
    {
      required: true,
      message: '请输入商品库存',
      trigger: 'change',
    },
  ],
}

/* ==============================
   计算属性
================================ */

const dialogTitle = computed(() => {
  return dialogMode.value === 'create'
    ? '新增商品'
    : '编辑商品'
})

const categoryOptions = computed(() => {
  const categories =
    productList.value
      .map(
        (product) =>
          product.category,
      )
      .filter(Boolean)

  return [...new Set(categories)]
})

const filteredProductList =
  computed(() => {
    const keyword =
      appliedFilters.keyword
        .trim()
        .toLowerCase()

    return productList.value.filter(
      (product) => {
        const productName =
          String(
            product.product_name ||
              '',
          ).toLowerCase()

        const category =
          String(
            product.category || '',
          ).toLowerCase()

        const productStatus =
          resolveProductStatus(
            product,
          )

        const matchesKeyword =
          !keyword ||
          productName.includes(
            keyword,
          ) ||
          category.includes(keyword)

        const matchesCategory =
          !appliedFilters.category ||
          product.category ===
            appliedFilters.category

        const matchesStatus =
          !appliedFilters.status ||
          productStatus ===
            appliedFilters.status

        return (
          matchesKeyword &&
          matchesCategory &&
          matchesStatus
        )
      },
    )
  })

const totalProducts = computed(
  () =>
    filteredProductList.value
      .length,
)

const paginatedProductList =
  computed(() => {
    const start =
      (currentPage.value - 1) *
      pageSize.value

    return filteredProductList
      .value
      .slice(
        start,
        start + pageSize.value,
      )
  })

/* ==============================
   商品数据处理
================================ */

function resolveProductStatus(
  product,
) {
  /*
   * 后端返回 status 时优先使用。
   * 当前没有 status 时，根据库存临时判断。
   */
  if (product.status) {
    return product.status
  }

  return Number(product.stock) > 0
    ? '上架'
    : '下架'
}

function getStatusType(product) {
  const status =
    resolveProductStatus(product)

  return (
    STATUS_TYPE_MAP[status] ||
    'info'
  )
}

function formatPrice(value) {
  const numberValue =
    Number(value || 0)

  return `¥${numberValue.toFixed(
    2,
  )}`
}

function formatDate(value) {
  if (!value) {
    return '-'
  }

  const date = new Date(value)

  if (
    Number.isNaN(date.getTime())
  ) {
    return String(value)
  }

  const pad = (number) =>
    String(number).padStart(2, '0')

  const datePart = [
    date.getFullYear(),
    pad(date.getMonth() + 1),
    pad(date.getDate()),
  ].join('-')

  const timePart = [
    pad(date.getHours()),
    pad(date.getMinutes()),
  ].join(':')

  return `${datePart} ${timePart}`
}

/* ==============================
   查询商品
================================ */

async function loadProducts() {
  try {
    return await loadProductList()
  } catch {
    /*
     * useAsyncList 已经统一显示错误提示，
     * 此处阻止未处理的 Promise 错误继续传播。
     */
    return []
  }
}

/* ==============================
   筛选操作
================================ */

function handleSearch() {
  Object.assign(
    appliedFilters,
    filterForm,
  )

  currentPage.value = 1
}

function handleReset() {
  Object.assign(
    filterForm,
    FILTER_DEFAULTS,
  )

  Object.assign(
    appliedFilters,
    FILTER_DEFAULTS,
  )

  currentPage.value = 1
}

function handlePageSizeChange(size) {
  pageSize.value = size
  currentPage.value = 1
}

/* ==============================
   商品表单处理
================================ */

function resetProductForm() {
  editingProductId.value = null

  Object.assign(
    productForm,
    PRODUCT_FORM_DEFAULTS,
  )

  formRef.value
    ?.clearValidate()
}

function fillProductForm(product) {
  Object.assign(productForm, {
    product_name:
      product.product_name || '',

    category:
      product.category || '',

    price:
      Number(product.price || 0),

    stock:
      Number(product.stock || 0),

    selling_points:
      product.selling_points || '',

    target_audience:
      product.target_audience || '',
  })
}

function buildProductPayload() {
  return {
    product_name:
      productForm.product_name
        .trim(),

    category:
      productForm.category.trim(),

    price:
      Number(productForm.price),

    stock:
      Number(productForm.stock),

    selling_points:
      productForm.selling_points
        .trim() || null,

    target_audience:
      productForm.target_audience
        .trim() || null,
  }
}

/* ==============================
   新增与编辑
================================ */

async function openCreateDialog() {
  dialogMode.value = 'create'

  resetProductForm()

  dialogVisible.value = true

  await nextTick()

  formRef.value
    ?.clearValidate()
}

async function openEditDialog(
  product,
) {
  dialogMode.value = 'edit'
  editingProductId.value =
    product.id

  fillProductForm(product)

  dialogVisible.value = true

  await nextTick()

  formRef.value
    ?.clearValidate()
}

async function submitProduct() {
  if (!formRef.value) {
    return
  }

  try {
    await formRef.value
      .validate()
  } catch {
    return
  }

  submitting.value = true

  const submitData =
    buildProductPayload()

  try {
    if (
      dialogMode.value ===
      'create'
    ) {
      await createProductApi(
        submitData,
      )

      ElMessage.success(
        '商品创建成功',
      )
    } else {
      await updateProductApi(
        editingProductId.value,
        submitData,
      )

      ElMessage.success(
        '商品修改成功',
      )
    }

    dialogVisible.value = false

    await loadProducts()
  } catch (error) {
    ElMessage.error(
      getApiErrorMessage(
        error,
        '商品保存失败',
      ),
    )
  } finally {
    submitting.value = false
  }
}

/* ==============================
   删除商品
================================ */

function isConfirmCanceled(error) {
  return (
    error === 'cancel' ||
    error === 'close'
  )
}

async function handleDelete(product) {
  try {
    await ElMessageBox.confirm(
      `确定删除商品“${product.product_name}”吗？`,
      '删除商品',
      {
        confirmButtonText:
          '确定删除',

        cancelButtonText: '取消',
        type: 'warning',
      },
    )

    await deleteProductApi(
      product.id,
    )

    ElMessage.success(
      '商品删除成功',
    )

    await loadProducts()
  } catch (error) {
    if (
      isConfirmCanceled(error)
    ) {
      return
    }

    ElMessage.error(
      getApiErrorMessage(
        error,
        '商品删除失败',
      ),
    )
  }
}

/* ==============================
   图片处理
================================ */

function handleImageError(event) {
  const imageElement =
    event?.target

  if (imageElement) {
    imageElement.style.display =
      'none'
  }
}

/* ==============================
   分页同步
================================ */

function syncCurrentPage() {
  const maxPage = Math.max(
    1,
    Math.ceil(
      totalProducts.value /
        pageSize.value,
    ),
  )

  if (
    currentPage.value > maxPage
  ) {
    currentPage.value = maxPage
  }
}

watch(
  [
    totalProducts,
    pageSize,
  ],
  syncCurrentPage,
)

/* ==============================
   生命周期
================================ */

onMounted(() => {
  void loadProducts()
})
</script> -->
<script setup>
import {
  computed,
  nextTick,
  onMounted,
  reactive,
  ref,
} from 'vue'

import {
  ElMessage,
} from 'element-plus'

import {
  Delete,
  Edit,
  Goods,
  Plus,
  Refresh,
  Search,
} from '@element-plus/icons-vue'

import {
  createProductApi,
  deleteProductApi,
  getProductListApi,
  updateProductApi,
} from '../api/products.js'

import {
  useAsyncList,
} from '../composables/useAsyncList.js'

import {
  usePagination,
} from '../composables/usePagination.js'

import {
  getApiErrorMessage,
} from '../utils/apiResponse.js'

import {
  confirmDelete,
} from '../utils/confirm.js'

import {
  formatDateTime as formatDate,
} from '../utils/date.js'

const FILTER_DEFAULTS = {
  keyword: '',
  category: '',
  status: '',
}

const PRODUCT_FORM_DEFAULTS = {
  product_name: '',
  category: '',
  price: 0.01,
  stock: 0,
  selling_points: '',
  target_audience: '',
}

const STATUS_TYPE_MAP = {
  上架: 'success',
  下架: 'warning',
  缺货: 'danger',
  草稿: 'info',
}

/* ==============================
   基础状态
================================ */

const submitting = ref(false)

const dialogVisible = ref(false)
const dialogMode = ref('create')
const editingProductId = ref(null)
const formRef = ref(null)

const {
  list: productList,
  loading,
  load: loadProductList,
} = useAsyncList(
  getProductListApi,
  {
    errorMessage:
      '商品列表加载失败',
  },
)

/* ==============================
   查询条件
================================ */

const filterForm = reactive({
  ...FILTER_DEFAULTS,
})

const appliedFilters = reactive({
  ...FILTER_DEFAULTS,
})

/* ==============================
   商品表单
================================ */

const productForm = reactive({
  ...PRODUCT_FORM_DEFAULTS,
})

const formRules = {
  product_name: [
    {
      required: true,
      message: '请输入商品名称',
      trigger: 'blur',
    },
    {
      min: 1,
      max: 100,
      message:
        '商品名称长度为1到100个字符',
      trigger: 'blur',
    },
  ],

  category: [
    {
      required: true,
      message:
        '请选择或输入商品分类',
      trigger: 'change',
    },
  ],

  price: [
    {
      required: true,
      message: '请输入商品价格',
      trigger: 'change',
    },
  ],

  stock: [
    {
      required: true,
      message: '请输入商品库存',
      trigger: 'change',
    },
  ],
}

/* ==============================
   计算属性
================================ */

const dialogTitle = computed(() => {
  return dialogMode.value === 'create'
    ? '新增商品'
    : '编辑商品'
})

const categoryOptions = computed(() => {
  const categories =
    productList.value
      .map(
        (product) =>
          product.category,
      )
      .filter(Boolean)

  return [
    ...new Set(categories),
  ]
})

const filteredProductList =
  computed(() => {
    const keyword =
      appliedFilters.keyword
        .trim()
        .toLowerCase()

    return productList.value.filter(
      (product) => {
        const productName =
          String(
            product.product_name ||
              '',
          ).toLowerCase()

        const category =
          String(
            product.category || '',
          ).toLowerCase()

        const productStatus =
          resolveProductStatus(
            product,
          )

        const matchesKeyword =
          !keyword ||
          productName.includes(
            keyword,
          ) ||
          category.includes(keyword)

        const matchesCategory =
          !appliedFilters.category ||
          product.category ===
            appliedFilters.category

        const matchesStatus =
          !appliedFilters.status ||
          productStatus ===
            appliedFilters.status

        return (
          matchesKeyword &&
          matchesCategory &&
          matchesStatus
        )
      },
    )
  })

/*
 * 统一使用通用分页组合函数。
 *
 * totalProducts 和 paginatedProductList
 * 保留原名称，模板无需修改。
 */
const {
  currentPage,
  pageSize,
  total: totalProducts,
  pageList: paginatedProductList,
  resetPage,
  changePageSize,
} = usePagination(
  filteredProductList,
  10,
)

/* ==============================
   商品数据处理
================================ */

function resolveProductStatus(
  product,
) {
  if (product.status) {
    return product.status
  }

  return Number(product.stock) > 0
    ? '上架'
    : '下架'
}

function getStatusType(product) {
  const status =
    resolveProductStatus(product)

  return (
    STATUS_TYPE_MAP[status] ||
    'info'
  )
}

function formatPrice(value) {
  const numberValue =
    Number(value || 0)

  return `¥${numberValue.toFixed(
    2,
  )}`
}

/* ==============================
   查询商品
================================ */

async function loadProducts() {
  try {
    return await loadProductList()
  } catch {
    /*
     * useAsyncList 已经显示错误提示。
     */
    return []
  }
}

/* ==============================
   筛选操作
================================ */

function handleSearch() {
  Object.assign(
    appliedFilters,
    filterForm,
  )

  resetPage()
}

function handleReset() {
  Object.assign(
    filterForm,
    FILTER_DEFAULTS,
  )

  Object.assign(
    appliedFilters,
    FILTER_DEFAULTS,
  )

  resetPage()
}

function handlePageSizeChange(size) {
  changePageSize(size)
}

/* ==============================
   商品表单处理
================================ */

function resetProductForm() {
  editingProductId.value = null

  Object.assign(
    productForm,
    PRODUCT_FORM_DEFAULTS,
  )

  formRef.value
    ?.clearValidate()
}

function fillProductForm(product) {
  Object.assign(productForm, {
    product_name:
      product.product_name || '',

    category:
      product.category || '',

    price:
      Number(product.price || 0),

    stock:
      Number(product.stock || 0),

    selling_points:
      product.selling_points || '',

    target_audience:
      product.target_audience || '',
  })
}

function buildProductPayload() {
  return {
    product_name:
      productForm.product_name
        .trim(),

    category:
      productForm.category
        .trim(),

    price:
      Number(productForm.price),

    stock:
      Number(productForm.stock),

    selling_points:
      productForm.selling_points
        .trim() || null,

    target_audience:
      productForm.target_audience
        .trim() || null,
  }
}

/* ==============================
   新增与编辑
================================ */

async function openCreateDialog() {
  dialogMode.value = 'create'

  resetProductForm()

  dialogVisible.value = true

  await nextTick()

  formRef.value
    ?.clearValidate()
}

async function openEditDialog(
  product,
) {
  dialogMode.value = 'edit'

  editingProductId.value =
    product.id

  fillProductForm(product)

  dialogVisible.value = true

  await nextTick()

  formRef.value
    ?.clearValidate()
}

async function submitProduct() {
  if (!formRef.value) {
    return
  }

  try {
    await formRef.value
      .validate()
  } catch {
    return
  }

  submitting.value = true

  const submitData =
    buildProductPayload()

  try {
    if (
      dialogMode.value ===
      'create'
    ) {
      await createProductApi(
        submitData,
      )

      ElMessage.success(
        '商品创建成功',
      )
    } else {
      await updateProductApi(
        editingProductId.value,
        submitData,
      )

      ElMessage.success(
        '商品修改成功',
      )
    }

    dialogVisible.value = false

    await loadProducts()
  } catch (error) {
    ElMessage.error(
      getApiErrorMessage(
        error,
        '商品保存失败',
      ),
    )
  } finally {
    submitting.value = false
  }
}

/* ==============================
   删除商品
================================ */

async function handleDelete(product) {
  try {
    const confirmed =
      await confirmDelete(
        product.product_name,
        {
          title: '删除商品',
        },
      )

    if (!confirmed) {
      return
    }

    await deleteProductApi(
      product.id,
    )

    ElMessage.success(
      '商品删除成功',
    )

    await loadProducts()
  } catch (error) {
    ElMessage.error(
      getApiErrorMessage(
        error,
        '商品删除失败',
      ),
    )
  }
}

/* ==============================
   图片处理
================================ */

function handleImageError(event) {
  const imageElement =
    event?.target

  if (imageElement) {
    imageElement.style.display =
      'none'
  }
}

/* ==============================
   生命周期
================================ */

onMounted(() => {
  void loadProducts()
})
</script>
<template>
  <div class="product-page">
    <section class="product-panel">
      <!-- 查询条件 -->
      <div class="filter-section">
        <div class="filter-control name-control">
          <span class="filter-label">
            商品名称
          </span>

          <el-input
            v-model="filterForm.keyword"
            clearable
            placeholder="请输入商品名称"
            @keyup.enter="handleSearch"
          />
        </div>

        <div class="filter-control">
          <span class="filter-label">
            商品分类
          </span>

          <el-select
            v-model="filterForm.category"
            clearable
            placeholder="请选择分类"
          >
            <el-option
              v-for="category in categoryOptions"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </div>

        <div class="filter-control">
          <span class="filter-label">
            状态
          </span>

          <el-select
            v-model="filterForm.status"
            clearable
            placeholder="请选择状态"
          >
            <el-option
              label="上架"
              value="上架"
            />

            <el-option
              label="下架"
              value="下架"
            />

            <el-option
              label="缺货"
              value="缺货"
            />

            <el-option
              label="草稿"
              value="草稿"
            />
          </el-select>
        </div>

        <div class="filter-actions">
          <el-button
            type="primary"
            :icon="Search"
            @click="handleSearch"
          >
            查询
          </el-button>

          <el-button
            :icon="Refresh"
            @click="handleReset"
          >
            重置
          </el-button>
        </div>
      </div>

      <!-- 工具栏 -->
      <div class="toolbar-section">
        <el-button
          type="primary"
          :icon="Plus"
          class="create-button"
          @click="openCreateDialog"
        >
          新增商品
        </el-button>

        <el-button
          :icon="Refresh"
          :loading="loading"
          class="refresh-button"
          @click="loadProducts"
        >
          刷新
        </el-button>
      </div>

      <!-- 商品表格 -->
      <div class="table-wrapper">
        <el-table
          v-loading="loading"
          :data="paginatedProductList"
          row-key="id"
          class="product-table"
        >
          <el-table-column
            label="商品信息"
            min-width="280"
          >
            <template #default="{ row }">
              <div class="product-information">
                <div class="product-image">
                  <img
                    v-if="row.image_url"
                    :src="row.image_url"
                    :alt="row.product_name"
                    @error="handleImageError"
                  />

                  <div class="image-placeholder">
                    <el-icon>
                      <Goods />
                    </el-icon>
                  </div>
                </div>

                <div class="product-copy">
                  <strong>
                    {{ row.product_name }}
                  </strong>

                  <span>
                    {{ row.category || '未分类' }}
                  </span>
                </div>
              </div>
            </template>
          </el-table-column>

          <el-table-column
            label="价格"
            width="135"
          >
            <template #default="{ row }">
              <span class="price-value">
                {{ formatPrice(row.price) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            label="库存"
            width="120"
          >
            <template #default="{ row }">
              <span
                class="stock-value"
                :class="{
                  danger:
                    Number(row.stock) <= 0,
                }"
              >
                {{ row.stock }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            label="状态"
            width="120"
            align="center"
          >
            <template #default="{ row }">
              <el-tag
                :type="getStatusType(row)"
                effect="dark"
                class="status-tag"
              >
                {{ resolveProductStatus(row) }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column
            label="创建时间"
            width="190"
          >
            <template #default="{ row }">
              <span class="date-value">
                {{ formatDate(row.created_at) }}
              </span>
            </template>
          </el-table-column>

          <el-table-column
            label="操作"
            width="145"
            fixed="right"
            align="center"
          >
            <template #default="{ row }">
              <el-button
                type="primary"
                link
                :icon="Edit"
                class="operation-button"
                @click="openEditDialog(row)"
              >
                编辑
              </el-button>

              <el-button
                type="danger"
                link
                :icon="Delete"
                class="operation-button"
                @click="handleDelete(row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>

          <template #empty>
            <div class="empty-state">
              <div class="empty-icon">
                <el-icon>
                  <Goods />
                </el-icon>
              </div>

              <strong>暂无商品数据</strong>

              <span>
                点击“新增商品”创建商品记录
              </span>
            </div>
          </template>
        </el-table>
      </div>

      <!-- 分页 -->
      <div class="pagination-section">
        <span class="pagination-total">
          共 {{ totalProducts }} 条
        </span>

        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          background
          layout="prev, pager, next, sizes"
          :page-sizes="[10, 20, 50]"
          :total="totalProducts"
          @size-change="handlePageSizeChange"
        />
      </div>
    </section>

    <!-- 新增与编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="620px"
      destroy-on-close
      class="product-dialog"
      @closed="resetProductForm"
    >
      <el-form
        ref="formRef"
        :model="productForm"
        :rules="formRules"
        label-position="top"
      >
        <div class="form-grid">
          <el-form-item
            label="商品名称"
            prop="product_name"
            class="full-column"
          >
            <el-input
              v-model="productForm.product_name"
              maxlength="100"
              show-word-limit
              placeholder="请输入商品名称"
            />
          </el-form-item>

          <el-form-item
            label="商品分类"
            prop="category"
          >
            <el-select
              v-model="productForm.category"
              allow-create
              filterable
              default-first-option
              placeholder="请选择或输入分类"
              style="width: 100%"
            >
              <el-option
                v-for="category in categoryOptions"
                :key="category"
                :label="category"
                :value="category"
              />

              <el-option
                label="数码"
                value="数码"
              />

              <el-option
                label="服装"
                value="服装"
              />

              <el-option
                label="美妆"
                value="美妆"
              />

              <el-option
                label="食品"
                value="食品"
              />

              <el-option
                label="家居"
                value="家居"
              />
            </el-select>
          </el-form-item>

          <el-form-item
            label="商品价格"
            prop="price"
          >
            <el-input-number
              v-model="productForm.price"
              :min="0.01"
              :precision="2"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item
            label="商品库存"
            prop="stock"
          >
            <el-input-number
              v-model="productForm.stock"
              :min="0"
              :precision="0"
              controls-position="right"
              style="width: 100%"
            />
          </el-form-item>

          <el-form-item label="目标用户">
            <el-input
              v-model="productForm.target_audience"
              maxlength="200"
              placeholder="例如：大学生、通勤上班族"
            />
          </el-form-item>

          <el-form-item
            label="商品卖点"
            class="full-column"
          >
            <el-input
              v-model="productForm.selling_points"
              type="textarea"
              :rows="4"
              maxlength="1000"
              show-word-limit
              resize="none"
              placeholder="例如：主动降噪、长续航、低延迟"
            />
          </el-form-item>
        </div>
      </el-form>

      <template #footer>
        <el-button
          @click="dialogVisible = false"
        >
          取消
        </el-button>

        <el-button
          type="primary"
          :loading="submitting"
          @click="submitProduct"
        >
          {{
            dialogMode === 'create'
              ? '确认新增'
              : '保存修改'
          }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>


<style scoped>
.product-page {
  width: 100%;
  min-width: 0;
  color: var(--app-text-primary);
}

.product-panel {
  display: flex;
  min-width: 0;
  min-height: calc(100vh - 88px);
  flex-direction: column;
  overflow: hidden;
  background:
    linear-gradient(
      145deg,
      rgba(255, 255, 255, 0.012),
      transparent 55%
    ),
    #0f141e;
  border: 1px solid #202736;
  border-radius: 7px;
  box-shadow:
    0 10px 28px rgba(0, 0, 0, 0.15);
}

/* ==============================
   查询区域
================================ */

.filter-section {
  display: flex;
  min-height: 72px;
  align-items: center;
  gap: 17px;
  padding: 14px 16px;
  background: rgba(17, 22, 33, 0.92);
  border-bottom: 1px solid #202736;
}

.filter-control {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 9px;
}

.filter-control.name-control {
  width: 265px;
}

.filter-control:not(.name-control) {
  width: 235px;
}

.filter-label {
  flex: 0 0 auto;
  color: #a4abb8;
  font-size: 10px;
  white-space: nowrap;
}

.filter-control :deep(.el-input),
.filter-control :deep(.el-select) {
  flex: 1;
  min-width: 0;
}

.filter-control :deep(.el-input__wrapper),
.filter-control :deep(.el-select__wrapper) {
  min-height: 32px;
  background: #0b1019;
  border-radius: 5px;
  box-shadow:
    0 0 0 1px #242b39 inset;
  transition:
    box-shadow 0.2s ease,
    background 0.2s ease;
}

.filter-control :deep(.el-input__wrapper:hover),
.filter-control :deep(.el-select__wrapper:hover) {
  background: #0d121c;
  box-shadow:
    0 0 0 1px #363f52 inset;
}

.filter-control :deep(.el-input__wrapper.is-focus),
.filter-control :deep(.el-select__wrapper.is-focused) {
  background: #0d121c;
  box-shadow:
    0 0 0 1px #765bff inset,
    0 0 0 3px rgba(118, 91, 255, 0.08);
}

.filter-control :deep(.el-input__inner),
.filter-control :deep(.el-select__placeholder),
.filter-control :deep(.el-select__selected-item) {
  color: #abb2bf;
  font-size: 9px;
}

.filter-control :deep(.el-input__inner::placeholder) {
  color: #555e6f;
}

.filter-control :deep(.el-input__prefix),
.filter-control :deep(.el-input__suffix),
.filter-control :deep(.el-select__caret) {
  color: #667083;
}

/* ==============================
   查询按钮
================================ */

.filter-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.filter-actions :deep(.el-button) {
  height: 32px;
  margin: 0;
  padding: 0 16px;
  font-size: 9px;
  border-radius: 5px;
  transition:
    background 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.15s ease;
}

.filter-actions :deep(.el-button--primary) {
  color: #ffffff;
  background:
    linear-gradient(
      135deg,
      #765bff 0%,
      #6348e8 100%
    );
  border-color: #765bff;
  box-shadow:
    0 4px 12px rgba(118, 91, 255, 0.22);
}

.filter-actions :deep(.el-button--primary:hover) {
  color: #ffffff;
  background:
    linear-gradient(
      135deg,
      #846cff 0%,
      #7055ef 100%
    );
  border-color: #8b74ff;
  box-shadow:
    0 6px 16px rgba(118, 91, 255, 0.32);
  transform: translateY(-1px);
}

.filter-actions :deep(.el-button--primary:active) {
  background: #5d43d4;
  border-color: #5d43d4;
  box-shadow:
    0 2px 7px rgba(118, 91, 255, 0.2);
  transform: translateY(0);
}

.filter-actions
  :deep(.el-button:not(.el-button--primary)) {
  color: #9aa2b2;
  background: #151a25;
  border-color: #303747;
  box-shadow: none;
}

.filter-actions
  :deep(.el-button:not(.el-button--primary):hover) {
  color: #c4baff;
  background: rgba(118, 91, 255, 0.09);
  border-color: #56468d;
}

.filter-actions
  :deep(.el-button:not(.el-button--primary):active) {
  color: #aa9cff;
  background: rgba(118, 91, 255, 0.13);
  border-color: #6653a7;
}

/* ==============================
   工具栏
================================ */

.toolbar-section {
  display: flex;
  min-height: 54px;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  background: #10151f;
  border-bottom: 1px solid #202736;
}

.create-button,
.refresh-button {
  height: 30px;
  padding: 0 13px;
  font-size: 9px;
  border-radius: 5px;
  transition:
    background 0.2s ease,
    border-color 0.2s ease,
    color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.15s ease;
}

.create-button {
  color: #ffffff !important;
  background:
    linear-gradient(
      135deg,
      #765bff 0%,
      #6348e8 100%
    ) !important;
  border-color: #765bff !important;
  box-shadow:
    0 4px 12px rgba(118, 91, 255, 0.22);
}

.create-button:hover {
  color: #ffffff !important;
  background:
    linear-gradient(
      135deg,
      #846cff 0%,
      #7055ef 100%
    ) !important;
  border-color: #8b74ff !important;
  box-shadow:
    0 6px 16px rgba(118, 91, 255, 0.32);
  transform: translateY(-1px);
}

.create-button:active {
  background: #5d43d4 !important;
  border-color: #5d43d4 !important;
  transform: translateY(0);
}

.create-button :deep(.el-icon) {
  color: #ffffff;
}

.refresh-button {
  color: #929aaa !important;
  background: #151a25 !important;
  border-color: #303747 !important;
  box-shadow: none !important;
}

.refresh-button:hover {
  color: #c4baff !important;
  background:
    rgba(118, 91, 255, 0.09) !important;
  border-color: #56468d !important;
}

.refresh-button:active {
  color: #aa9cff !important;
  background:
    rgba(118, 91, 255, 0.13) !important;
  border-color: #6653a7 !important;
}

.refresh-button :deep(.el-icon) {
  color: #7d8697;
}

/* ==============================
   表格容器
================================ */

.table-wrapper {
  padding: 8px 16px 0;
}

.product-table {
  width: 100%;
  overflow: hidden;
  border: 1px solid #202736;
  border-radius: 6px;
}

.product-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.product-table :deep(.el-table__border-left-patch) {
  background: #141925;
}

/* ==============================
   表头和数据行
================================ */

.product-table :deep(th.el-table__cell) {
  height: 43px;
  padding: 0;
  color: #747d8e;
  font-size: 9px;
  font-weight: 500;
  background: #141925;
  border-bottom-color: #202736;
}

.product-table :deep(td.el-table__cell) {
  height: 64px;
  padding: 0;
  color: #aeb5c2;
  font-size: 9px;
  background: #111621;
  border-bottom-color:
    rgba(255, 255, 255, 0.038);
}

.product-table
  :deep(.el-table__row:hover td.el-table__cell) {
  background:
    rgba(118, 91, 255, 0.045);
}

.product-table :deep(.cell) {
  padding-right: 17px;
  padding-left: 17px;
}

.product-table
  :deep(.el-table-fixed-column--right) {
  background: #111621;
}

.product-table
  :deep(th.el-table-fixed-column--right) {
  background: #141925;
}

.product-table
  :deep(
    .el-table__row:hover
      .el-table-fixed-column--right
  ) {
  background:
    rgba(118, 91, 255, 0.045);
}

/* ==============================
   商品信息
================================ */

.product-information {
  display: flex;
  min-width: 0;
  align-items: center;
  gap: 11px;
}

.product-image {
  position: relative;
  display: flex;
  width: 39px;
  height: 39px;
  flex: 0 0 39px;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background:
    linear-gradient(
      135deg,
      #313b4d,
      #181e2a
    );
  border: 1px solid #30394a;
  border-radius: 6px;
}

.product-image::after {
  position: absolute;
  inset: 0;
  z-index: 3;
  pointer-events: none;
  border: 1px solid rgba(255, 255, 255, 0.035);
  border-radius: inherit;
  content: "";
}

.product-image img {
  position: relative;
  z-index: 2;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-placeholder {
  position: absolute;
  inset: 0;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #826de8;
  font-size: 18px;
  background:
    radial-gradient(
      circle at 50% 35%,
      rgba(118, 91, 255, 0.12),
      transparent 68%
    );
}

.product-copy {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.product-copy strong {
  max-width: 210px;
  overflow: hidden;
  color: #e0e3e9;
  font-size: 9px;
  font-weight: 500;
  line-height: 15px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-copy span {
  margin-top: 3px;
  color: #626b7c;
  font-size: 8px;
  line-height: 12px;
}

.price-value {
  color: #e0e3e9;
  font-size: 9px;
  font-weight: 500;
}

.stock-value {
  color: #c4cad4;
  font-size: 9px;
}

.stock-value.danger {
  color: #ed777c;
}

.date-value {
  color: #a0a7b4;
  font-size: 8px;
}

/* ==============================
   状态标签
================================ */

.status-tag {
  height: 20px;
  padding: 0 7px;
  font-size: 8px;
  border-width: 1px;
  border-radius: 4px;
}

.status-tag.el-tag--success {
  color: #55d6a2 !important;
  background:
    rgba(45, 190, 135, 0.11) !important;
  border-color:
    rgba(45, 190, 135, 0.17) !important;
}

.status-tag.el-tag--warning {
  color: #e2ae60 !important;
  background:
    rgba(226, 174, 96, 0.1) !important;
  border-color:
    rgba(226, 174, 96, 0.17) !important;
}

.status-tag.el-tag--danger {
  color: #ee7a86 !important;
  background:
    rgba(238, 122, 134, 0.1) !important;
  border-color:
    rgba(238, 122, 134, 0.17) !important;
}

.status-tag.el-tag--info {
  color: #929bab !important;
  background:
    rgba(146, 155, 171, 0.09) !important;
  border-color:
    rgba(146, 155, 171, 0.15) !important;
}

/* ==============================
   编辑和删除按钮
================================ */

.operation-button {
  height: 22px;
  margin-left: 0 !important;
  padding: 0 5px;
  font-size: 8px;
  border-radius: 4px;
}

.operation-button.el-button--primary {
  color: #8b75ff !important;
}

.operation-button.el-button--primary:hover {
  color: #b2a5ff !important;
  background:
    rgba(118, 91, 255, 0.09) !important;
}

.operation-button.el-button--danger {
  color: #d9687e !important;
}

.operation-button.el-button--danger:hover {
  color: #f08b9e !important;
  background:
    rgba(217, 104, 126, 0.08) !important;
}

/* ==============================
   分页
================================ */

.pagination-section {
  display: flex;
  min-height: 62px;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding: 0 17px;
  border-top: 1px solid #202736;
}

.pagination-total {
  color: #818999;
  font-size: 8px;
}

.pagination-section :deep(.el-pagination) {
  --el-pagination-button-bg-color: #151b27;
  --el-pagination-hover-color: #ab9eff;
  --el-pagination-text-color: #808899;

  font-size: 8px;
}

.pagination-section :deep(.btn-prev),
.pagination-section :deep(.btn-next),
.pagination-section :deep(.el-pager li) {
  min-width: 25px;
  height: 25px;
  color: #808899;
  font-size: 8px;
  line-height: 25px;
  background: #171c27;
  border: 1px solid #262d3c;
  border-radius: 4px;
}

.pagination-section :deep(.btn-prev:hover),
.pagination-section :deep(.btn-next:hover),
.pagination-section
  :deep(.el-pager li:not(.is-active):hover) {
  color: #b3a6ff;
  background:
    rgba(118, 91, 255, 0.08);
  border-color: #584890;
}

.pagination-section
  :deep(.el-pager li.is-active) {
  color: #ffffff !important;
  background:
    linear-gradient(
      135deg,
      #765bff,
      #6348e8
    ) !important;
  border-color: #765bff !important;
  box-shadow:
    0 3px 9px rgba(118, 91, 255, 0.2);
}

.pagination-section
  :deep(.el-pagination__sizes .el-select__wrapper) {
  min-height: 28px;
  color: #9199a8;
  background: #151b27;
  box-shadow:
    0 0 0 1px #293142 inset;
}

.pagination-section
  :deep(.el-pagination__sizes .el-select__selected-item) {
  color: #9199a8;
  font-size: 8px;
}

/* ==============================
   空状态
================================ */

.empty-state {
  display: flex;
  min-height: 280px;
  align-items: center;
  justify-content: center;
  flex-direction: column;
}

.empty-icon {
  display: flex;
  width: 50px;
  height: 50px;
  align-items: center;
  justify-content: center;
  color: #7863df;
  font-size: 23px;
  background:
    rgba(118, 91, 255, 0.08);
  border:
    1px solid rgba(118, 91, 255, 0.14);
  border-radius: 12px;
}

.empty-state strong {
  margin-top: 12px;
  color: #abb2bf;
  font-size: 11px;
  font-weight: 500;
}

.empty-state span {
  margin-top: 5px;
  color: #596273;
  font-size: 8px;
}

/* ==============================
   商品弹窗表单
================================ */

.form-grid {
  display: grid;
  grid-template-columns:
    repeat(2, minmax(0, 1fr));
  gap: 0 16px;
}

.full-column {
  grid-column: 1 / -1;
}

.product-dialog :deep(.el-form-item) {
  margin-bottom: 17px;
}

.product-dialog
  :deep(.el-form-item__label) {
  margin-bottom: 6px;
  color: #aeb5c2;
  font-size: 10px;
  line-height: 15px;
}

.product-dialog :deep(.el-input__wrapper),
.product-dialog :deep(.el-select__wrapper),
.product-dialog :deep(.el-input-number) {
  min-height: 34px;
  background: #0d121c;
  border-radius: 5px;
}

.product-dialog
  :deep(.el-input-number .el-input__wrapper) {
  width: 100%;
}

.product-dialog
  :deep(.el-input__wrapper:hover),
.product-dialog
  :deep(.el-select__wrapper:hover) {
  box-shadow:
    0 0 0 1px #374053 inset;
}

.product-dialog
  :deep(.el-input__wrapper.is-focus),
.product-dialog
  :deep(.el-select__wrapper.is-focused) {
  box-shadow:
    0 0 0 1px #765bff inset,
    0 0 0 3px rgba(118, 91, 255, 0.08);
}

.product-dialog
  :deep(.el-textarea__inner) {
  color: #b8bfcc;
  background: #0d121c;
}

.product-dialog
  :deep(.el-textarea__inner:focus) {
  box-shadow:
    0 0 0 1px #765bff inset,
    0 0 0 3px rgba(118, 91, 255, 0.08);
}

/* ==============================
   弹窗底部按钮
================================ */

.product-dialog
  :deep(.el-dialog__footer .el-button) {
  height: 32px;
  padding: 0 17px;
  font-size: 9px;
  border-radius: 5px;
}

.product-dialog
  :deep(.el-dialog__footer .el-button--primary) {
  color: #ffffff;
  background:
    linear-gradient(
      135deg,
      #765bff,
      #6348e8
    );
  border-color: #765bff;
  box-shadow:
    0 4px 12px rgba(118, 91, 255, 0.22);
}

.product-dialog
  :deep(
    .el-dialog__footer
      .el-button--primary:hover
  ) {
  background:
    linear-gradient(
      135deg,
      #846cff,
      #7055ef
    );
  border-color: #8b74ff;
}

.product-dialog
  :deep(
    .el-dialog__footer
      .el-button:not(.el-button--primary)
  ) {
  color: #9aa2b2;
  background: #151a25;
  border-color: #303747;
}

.product-dialog
  :deep(
    .el-dialog__footer
      .el-button:not(.el-button--primary):hover
  ) {
  color: #c4baff;
  background:
    rgba(118, 91, 255, 0.09);
  border-color: #56468d;
}

/* ==============================
   加载遮罩
================================ */

.product-table
  :deep(.el-loading-mask) {
  background:
    rgba(11, 15, 24, 0.78);
  backdrop-filter: blur(2px);
}

.product-table
  :deep(.el-loading-spinner .path) {
  stroke: #765bff;
}

.product-table
  :deep(.el-loading-text) {
  color: #9c8cff;
}

/* ==============================
   窄屏适配
================================ */

@media (max-width: 1250px) {
  .filter-section {
    flex-wrap: wrap;
  }

  .filter-actions {
    margin-left: 0;
  }

  .filter-control.name-control {
    width: 235px;
  }

  .filter-control:not(.name-control) {
    width: 205px;
  }
}

@media (max-width: 980px) {
  .filter-control.name-control,
  .filter-control:not(.name-control) {
    width: calc(50% - 9px);
  }

  .filter-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .full-column {
    grid-column: auto;
  }
}
</style>