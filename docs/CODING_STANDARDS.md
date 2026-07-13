# 编码规范

## 1. 通用原则

- 保持行为兼容，重构与产品行为变化分开提交。
- 优先复用现有公共文件，不创建第二套同职责实现。
- 不用注释保存旧代码；使用 Git 历史。
- 不提交 `.env`、Token、Secret、私钥、数据库密码、构建产物或缓存。
- 不使用空 catch 隐藏错误；若公共层已提示，调用层可捕获并返回安全降级值，但应保留说明。

## 2. 前端 API

统一模板：

```javascript
import request from '../utils/request.js'

const RESOURCE_BASE_URL = '/resources'

export function getResourceListApi(params = {}) {
  return request.get(RESOURCE_BASE_URL, { params })
}

export function createResourceApi(data) {
  return request.post(RESOURCE_BASE_URL, data)
}
```

- 不在 API 文件中弹消息、操作 Router/Pinia/localStorage 或转换表单。
- 不改变既有 URL、Method 和请求字段。
- 调用方直接接收业务 data。
- 未确认无调用的 detail API 保留并记录为候选死导出。

## 3. 前端认证

- 禁止在 authStorage 之外直接操作 localStorage。
- Login 只调用 Auth Store 和记住账号适配器。
- Layout 通过 Auth Store 退出。
- 站内 redirect 必须以单 `/` 开头，拒绝 `//` 和登录页循环跳转。
- Request 不依赖 Pinia。

## 4. 公共能力

- 错误：`getApiErrorMessage()`。
- 列表兼容：迁移期可用 `resolveApiList()`，新 API data 为数组时直接使用亦可。
- 日期：`formatDate()`、`formatDateTime()`。
- 删除确认：`confirmDelete()`；非删除确认仅用语义明确的 `confirmAction()`。
- 前端分页：`usePagination()`。
- 异步列表：`useAsyncList()`。
- 平台和领域状态：从 `src/constants` 导入。

## 5. 后端

- Schema 是外部契约；ORM Model 不承担 HTTP 响应职责。
- 401 表示未认证，403 表示身份有效但权限不足。
- 数据库写入失败必须 rollback；全面事务标准化留待 Service/Repository 阶段。
- 生产环境不得自动建表或写入种子。
- 不在源码提供默认管理员密码。
- 正式结构变更使用 Alembic，不使用 `create_all()` 代替迁移。

## 6. 质量门禁

提交前运行：

```powershell
cd ai-video-commerce-web
npm run check

cd ..\ai-video-commerce-api
.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m pytest -q
```

`npm run lint` 和 `format:check` 必须只读。修复命令必须由开发者显式执行，且只处理当前任务涉及的文件。

## 7. Git 提交

- 一个提交只表达一类变化。
- 清理、契约、安全和文档分别提交。
- 提交前检查 `git diff`、`git diff --cached` 和凭据。
- 每个提交应保持可构建、可测试、可回滚。
