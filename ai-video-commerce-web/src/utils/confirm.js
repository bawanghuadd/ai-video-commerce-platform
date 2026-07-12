import {
  ElMessageBox,
} from 'element-plus'

/**
 * 通用删除确认弹窗。
 *
 * 确认返回 true；
 * 取消或关闭返回 false。
 */
export async function confirmDelete(
  itemName,
  options = {},
) {
  const {
    title = '删除确认',
    prefix = '确定删除',
    confirmButtonText =
      '确定删除',
    cancelButtonText = '取消',
  } = options

  const displayName =
    itemName || '该记录'

  try {
    await ElMessageBox.confirm(
      `${prefix}“${displayName}”吗？删除后无法恢复。`,
      title,
      {
        confirmButtonText,
        cancelButtonText,
        type: 'warning',
        closeOnClickModal: false,
        closeOnPressEscape: true,
      },
    )

    return true
  } catch (error) {
    if (
      error === 'cancel' ||
      error === 'close'
    ) {
      return false
    }

    throw error
  }
}