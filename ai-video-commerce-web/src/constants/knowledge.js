export const KNOWLEDGE_CATEGORY_OPTIONS = [
  '爆款开场钩子',
  '高转化脚本',
  '商品卖点模板',
  'AI提示词',
  '投流复盘经验',
  '失败案例',
  '视频制作规范',
]

export const KNOWLEDGE_STATUS_OPTIONS = [
  '草稿',
  '已发布',
  '已归档',
]

export const KNOWLEDGE_SOURCE_TYPE_OPTIONS = [
  '手动录入',
  '内容拆解',
  '脚本分镜',
  '视频任务',
  '投流复盘',
  'AI自动沉淀',
]

export const KNOWLEDGE_STATUS_CLASS_MAP = {
  草稿: 'draft',
  已发布: 'published',
  已归档: 'archived',
}

export const KNOWLEDGE_CATEGORY_CLASS_MAP = {
  爆款开场钩子: 'hook',
  高转化脚本: 'script',
  商品卖点模板: 'selling',
  AI提示词: 'prompt',
  投流复盘经验: 'traffic',
  失败案例: 'failure',
  视频制作规范: 'video',
}

export function getKnowledgeStatusClass(status) {
  return (
    KNOWLEDGE_STATUS_CLASS_MAP[status] ||
    'draft'
  )
}

export function getKnowledgeCategoryClass(category) {
  return (
    KNOWLEDGE_CATEGORY_CLASS_MAP[category] ||
    'default'
  )
}