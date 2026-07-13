import {
  describe,
  expect,
  it,
  vi,
} from 'vitest'

vi.mock('../utils/request.js', () => ({
  default: {
    delete: vi.fn(),
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
  },
}))

import request from '../utils/request.js'
import {
  createProductApi,
  deleteProductApi,
  getProductListApi,
  updateProductApi,
} from './products.js'

describe('products API', () => {
  it('passes list filters as query params', () => {
    const params = { keyword: '耳机' }

    getProductListApi(params)

    expect(request.get).toHaveBeenCalledWith('/products', { params })
  })

  it('keeps create, update and delete contracts', () => {
    const data = { product_name: '耳机' }

    createProductApi(data)
    updateProductApi(3, data)
    deleteProductApi(3)

    expect(request.post).toHaveBeenCalledWith('/products', data)
    expect(request.put).toHaveBeenCalledWith('/products/3', data)
    expect(request.delete).toHaveBeenCalledWith('/products/3')
  })
})
