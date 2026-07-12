const DATE_FORMATTER =
  new Intl.DateTimeFormat(
    'zh-CN',
    {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    },
  )

const DATE_TIME_FORMATTER =
  new Intl.DateTimeFormat(
    'zh-CN',
    {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hourCycle: 'h23',
    },
  )

/**
 * 将输入值转换成有效日期。
 */
function parseDate(value) {
  if (!value) {
    return null
  }

  const date =
    value instanceof Date
      ? value
      : new Date(value)

  if (Number.isNaN(date.getTime())) {
    return null
  }

  return date
}

/**
 * 将日期格式化结果转换为字段对象。
 */
function getDateParts(
  formatter,
  date,
) {
  return Object.fromEntries(
    formatter
      .formatToParts(date)
      .filter(
        (part) =>
          part.type !== 'literal',
      )
      .map(
        (part) => [
          part.type,
          part.value,
        ],
      ),
  )
}

/**
 * 格式化为：
 * 2026-07-13
 */
export function formatDate(value) {
  const date = parseDate(value)

  if (!date) {
    return value
      ? String(value)
      : '-'
  }

  const {
    year,
    month,
    day,
  } = getDateParts(
    DATE_FORMATTER,
    date,
  )

  return `${year}-${month}-${day}`
}

/**
 * 格式化为：
 * 2026-07-13 15:30
 */
export function formatDateTime(value) {
  const date = parseDate(value)

  if (!date) {
    return value
      ? String(value)
      : '-'
  }

  const {
    year,
    month,
    day,
    hour,
    minute,
  } = getDateParts(
    DATE_TIME_FORMATTER,
    date,
  )

  return (
    `${year}-${month}-${day}` +
    ` ${hour}:${minute}`
  )
}