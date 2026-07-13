import {
  readdir,
  readFile,
} from 'node:fs/promises'
import {
  relative,
  resolve,
} from 'node:path'
import {
  fileURLToPath,
} from 'node:url'

const projectRoot = resolve(
  fileURLToPath(new URL('..', import.meta.url)),
)
const sourceRoot = resolve(projectRoot, 'src')
const violations = []

async function collectFiles(directory) {
  const entries = await readdir(directory, {
    withFileTypes: true,
  })
  const files = []

  for (const entry of entries) {
    const path = resolve(directory, entry.name)

    if (entry.isDirectory()) {
      files.push(...await collectFiles(path))
    } else {
      files.push(path)
    }
  }

  return files
}

function normalizePath(path) {
  return relative(projectRoot, path).replaceAll('\\', '/')
}

function addViolation(rule, file, content, index, message) {
  const beforeMatch = content.slice(0, index)
  const lineNumber = beforeMatch.split(/\r?\n/).length
  const line = content.split(/\r?\n/)[lineNumber - 1]?.trim() || ''

  violations.push({
    rule,
    file: normalizePath(file),
    line,
    lineNumber,
    message,
  })
}

function findMatches(rule, file, content, pattern, message) {
  for (const match of content.matchAll(pattern)) {
    addViolation(rule, file, content, match.index, message)
  }
}

const files = await collectFiles(sourceRoot)
const productionFiles = files.filter((file) => {
  const normalized = normalizePath(file)

  return (
    /\.(?:js|mjs|vue)$/.test(normalized) &&
    !normalized.endsWith('.test.js')
  )
})

for (const file of files) {
  if (file.endsWith('.bak')) {
    violations.push({
      rule: 'no-source-backups',
      file: normalizePath(file),
      line: '',
      lineNumber: 1,
      message: 'src 中禁止保留 .bak 文件',
    })
  }
}

let axiosInstanceCount = 0

for (const file of productionFiles) {
  const normalized = normalizePath(file)
  const content = await readFile(file, 'utf8')
  const isRequestModule = normalized === 'src/utils/request.js'
  const isAuthStorage = normalized === 'src/utils/authStorage.js'
  const isApiModule = normalized.startsWith('src/api/')
  const isUiLogic = /src\/(?:views|components|composables)\//.test(normalized)
  const isView = normalized.startsWith('src/views/')

  const axiosImports = [...content.matchAll(/from\s+['"]axios['"]/g)]

  if (!isRequestModule) {
    for (const match of axiosImports) {
      addViolation(
        'single-axios-import',
        file,
        content,
        match.index,
        'Axios 只能由 src/utils/request.js 直接导入',
      )
    }
  }

  for (const match of content.matchAll(/\baxios\.create\s*\(/g)) {
    axiosInstanceCount += 1

    if (!isRequestModule) {
      addViolation(
        'single-axios-instance',
        file,
        content,
        match.index,
        '禁止创建第二个 Axios 实例',
      )
    }
  }

  if (isUiLogic) {
    findMatches(
      'business-data-only',
      file,
      content,
      /\b(?:response|result|res)\??\.data\b/g,
      '页面、组件和 composable 不得解析成功响应 response.data',
    )
  }

  if (!isAuthStorage) {
    findMatches(
      'central-auth-storage',
      file,
      content,
      /\blocalStorage\b/g,
      'localStorage 认证数据只能由 src/utils/authStorage.js 维护',
    )
  }

  if (isView) {
    findMatches(
      'shared-date-formatters',
      file,
      content,
      /function\s+formatDate(?:Time)?\s*\(/g,
      'View 不得声明通用日期格式化函数',
    )
    findMatches(
      'shared-response-utils',
      file,
      content,
      /function\s+(?:resolveListResponse|getErrorMessage)\s*\(/g,
      'View 不得声明通用响应或错误解析函数',
    )
    findMatches(
      'shared-confirmation',
      file,
      content,
      /\bElMessageBox(?:\.confirm)?\b/g,
      'View 必须通过 utils/confirm.js 执行确认操作',
    )

    if (
      content.includes('.slice(') &&
      content.includes('currentPage') &&
      content.includes('pageSize')
    ) {
      addViolation(
        'shared-pagination',
        file,
        content,
        content.indexOf('.slice('),
        'View 不得重复实现 slice + 页码分页',
      )
    }
  }

  if (isApiModule) {
    findMatches(
      'api-without-ui-dependencies',
      file,
      content,
      /from\s+['"](?:element-plus|vue-router|pinia)['"]|\blocalStorage\b/g,
      'API 模块不得依赖 UI、Router、Pinia 或存储实现',
    )
  }

  findMatches(
    'no-commented-script',
    file,
    content,
    /<!--\s*<script\s+setup[\s>]/g,
    '禁止整段注释掉的 <script setup>',
  )

  findMatches(
    'no-mojibake',
    file,
    content,
    /锟斤拷|�|鈥|鈫/g,
    '检测到常见中文乱码特征',
  )
}

if (axiosInstanceCount !== 1) {
  violations.push({
    rule: 'single-axios-instance',
    file: 'src/utils/request.js',
    line: '',
    lineNumber: 1,
    message: `项目必须且只能有一个 Axios 实例，当前检测到 ${axiosInstanceCount} 个`,
  })
}

if (violations.length > 0) {
  for (const violation of violations) {
    console.error(
      `[${violation.rule}] ${violation.file}:${violation.lineNumber} ${violation.message}`,
    )

    if (violation.line) {
      console.error(`  ${violation.line}`)
    }
  }

  process.exitCode = 1
} else {
  console.log(
    `Architecture check passed (${productionFiles.length} production source files).`,
  )
}
