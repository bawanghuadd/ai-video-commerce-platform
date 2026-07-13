import { ElMessageBox } from 'element-plus'

export async function confirmAction(
  message,
  title = '操作确认',
  options = {},
) {
  try {
    await ElMessageBox.confirm(message, title, {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning',
      closeOnClickModal: false,
      closeOnPressEscape: true,
      ...options,
    })

    return true
  } catch (error) {
    if (error === 'cancel' || error === 'close') {
      return false
    }

    throw error
  }
}

export function confirmDelete(itemName, options = {}) {
  const {
    title = '删除确认',
    prefix = '确定删除',
    confirmButtonText = '确定删除',
    cancelButtonText = '取消',
  } = options
  const displayName = itemName || '该记录'

  return confirmAction(
    `${prefix}“${displayName}”吗？删除后无法恢复。`,
    title,
    {
      confirmButtonText,
      cancelButtonText,
    },
  )
}