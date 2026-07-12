import {
  describe,
  expect,
  it,
} from 'vitest'

import {
  getApiErrorMessage,
  resolveApiData,
  resolveApiList,
} from './apiResponse.js'

describe('apiResponse', () => {
  it('resolves an Axios-style backend envelope', () => {
    const data = [{ id: 1 }]

    expect(
      resolveApiData({
        data: {
          code: 200,
          message: 'ok',
          data,
        },
      }),
    ).toBe(data)
  })

  it('keeps direct business data compatible', () => {
    const data = { id: 1 }

    expect(resolveApiData(data)).toBe(data)
  })

  it.each([
    [[{ id: 1 }], [{ id: 1 }]],
    [{ items: [{ id: 2 }] }, [{ id: 2 }]],
    [{ list: [{ id: 3 }] }, [{ id: 3 }]],
  ])('resolves supported list shapes', (input, expected) => {
    expect(resolveApiList(input)).toEqual(expected)
  })

  it('resolves a FastAPI string detail', () => {
    expect(
      getApiErrorMessage(
        {
          response: {
            data: {
              detail: '用户名或密码错误',
            },
          },
        },
        'fallback',
      ),
    ).toBe('用户名或密码错误')
  })

  it('combines FastAPI validation details', () => {
    expect(
      getApiErrorMessage(
        {
          response: {
            data: {
              detail: [
                { msg: '标题不能为空' },
                { msg: '状态无效' },
              ],
            },
          },
        },
        'fallback',
      ),
    ).toBe('标题不能为空；状态无效')
  })
})
