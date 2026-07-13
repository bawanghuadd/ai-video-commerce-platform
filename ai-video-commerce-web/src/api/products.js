import request from '../utils/request.js'

const PRODUCTS_BASE_URL = '/products'

export function getProductListApi(params = {}) {
  return request.get(PRODUCTS_BASE_URL, { params })
}

export function getProductDetailApi(productId) {
  return request.get(`${PRODUCTS_BASE_URL}/${productId}`)
}

export function createProductApi(data) {
  return request.post(PRODUCTS_BASE_URL, data)
}

export function updateProductApi(productId, data) {
  return request.put(`${PRODUCTS_BASE_URL}/${productId}`, data)
}

export function deleteProductApi(productId) {
  return request.delete(`${PRODUCTS_BASE_URL}/${productId}`)
}