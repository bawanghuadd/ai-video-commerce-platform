import request from '../utils/request'

export function getProductListApi() {
  return request({
    url: '/products',
    method: 'get',
  })
}

export function getProductDetailApi(productId) {
  return request({
    url: `/products/${productId}`,
    method: 'get',
  })
}

export function createProductApi(data) {
  return request({
    url: '/products',
    method: 'post',
    data,
  })
}

export function updateProductApi(productId, data) {
  return request({
    url: `/products/${productId}`,
    method: 'put',
    data,
  })
}

export function deleteProductApi(productId) {
  return request({
    url: `/products/${productId}`,
    method: 'delete',
  })
}