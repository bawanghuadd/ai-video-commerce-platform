# Codex Phase 1 全栈架构重构主指令

你现在担任本项目的高级全栈架构师、重构负责人、安全审查负责人和代码审查负责人。

你的任务不是给建议，而是在当前工作区中自主执行 Phase 1。除非遇到会导致数据丢失、无法判断的产品语义冲突、缺少必要凭据或外部权限，否则不要等待用户逐步确认。

---

## 一、项目与 Git 上下文

项目根目录：

```text
D:\ai-video-commerce-platform
```

前端：

```text
D:\ai-video-commerce-platform\ai-video-commerce-web
```

后端：

```text
D:\ai-video-commerce-platform\ai-video-commerce-api
```

当前目标分支：

```text
refactor/architecture-standardization
```

Phase 0 基线提交：

```text
60f385715e8858cd768f0edb33eb1a7bccc73907
```

Phase 0 计划文档：

```text
docs/REFACTOR_PLAN.md
```

远程仓库已经配置，仓库为公开仓库。严禁提交真实 `.env`、数据库密码、JWT Secret、访问令牌、私钥或其他凭据。

重要事实：

1. Phase 0 是基于基线提交完成的。
2. Phase 0 之后，用户可能已经手工修改了前端文件。
3. 你必须以“当前工作区真实代码”为准，不能盲目按 Phase 0 的旧结论覆盖现有有效修改。
4. 不允许丢弃用户当前未提交的修改。
5. 不允许直接 reset、checkout 丢弃、clean 删除或覆盖用户工作。
6. 不允许在未检查 Git diff 前自动提交。
7. 不允许将 `node_modules`、`dist`、`.venv`、`.env`、缓存和 `.bak` 加入提交。

---

## 二、项目技术栈

前端：

- Vue 3
- Vite
- JavaScript
- Vue Router
- Pinia
- Axios
- Element Plus
- ECharts

后端：

- FastAPI
- SQLAlchemy 2
- MySQL / PyMySQL
- Pydantic v2
- pydantic-settings
- PyJWT
- pwdlib / Argon2
- Uvicorn

业务链路：

```text
商品管理
→ 内容拆解
→ 内容创作
→ 脚本分镜
→ 视频任务
→ 投流分析
→ 数据复盘
→ 知识库
→ 系统设置
```

现有核心功能：

- 登录、注册、当前用户
- 商品 CRUD
- 内容拆解 CRUD
- 脚本与分镜 CRUD
- 视频任务 CRUD
- 知识库 CRUD 与引用次数
- 系统设置读取与保存
- Dashboard、内容创作、投流分析页面

---

## 三、最终工程目标

在不破坏现有业务行为、API 路径、请求字段、响应字段、路由名称、数据库数据和 UI 样式的前提下：

1. 建立唯一、稳定、可持续的前端基础设施。
2. 统一请求、响应、错误、认证存储、分页、日期、确认弹窗和常量。
3. 消除重复实现、注释旧代码、乱码代码、死代码和多套兼容逻辑。
4. 建立自动架构守卫，防止后续开发重新产生同类冗余。
5. 建立最小回归测试和只读质量检查。
6. 为后续模块化拆分和后端 Service/Repository 分层建立安全网。
7. 每一步都可构建、可测试、可回滚、可审查。
8. 不进行 Big Bang Refactor。
9. 不为追求 DRY 进行过度抽象。
10. 不在 Phase 1 进行全仓目录大迁移。

遵守：

- KISS
- DRY
- YAGNI
- SRP
- Separation of Concerns
- Behavior-preserving Refactor
- Single Source of Truth
- Dependency Direction
- Thin View / Thin Route

---

## 四、开始前必须自主完成的工作区保护

你必须首先执行并记录：

```powershell
cd D:\ai-video-commerce-platform
git branch --show-current
git status --short
git diff --stat
git diff
git log --oneline -5
git remote -v
```

然后执行以下规则：

### 1. 当前有未提交修改时

- 不得丢弃。
- 先判断是用户有效修改、生成文件、备份文件还是错误文件。
- 检查是否存在真实密钥或敏感信息。
- 检查前端是否能构建、后端是否能编译。
- 如果用户修改有效且可构建，创建一个独立保护提交：

```text
chore: preserve pre-phase1 working changes
```

- 不要把 Phase 1 修改混入该保护提交。
- 如果当前修改无法构建，先定位最小语法、导入或文件粘贴错误；只做恢复到可构建状态所必需的修复，然后单独提交。
- 不允许为了让工作区 clean 而删除有效代码。

### 2. 当前存在未跟踪文件时

分类处理：

- 业务源码、文档：检查后按用途提交。
- `.bak`、临时文本、生成文件：移出源码或删除，但删除前确认不是唯一版本。
- `.env`、密钥：不得提交。
- `dist`、`node_modules`、`.venv`、缓存：必须保持忽略。

### 3. 推送

每个阶段提交后执行：

```powershell
git push
```

如果远程认证失败，保留本地提交并报告真实错误；不得声称已推送。

---

## 五、Phase 1 总范围

Phase 1 只处理：

1. 当前状态复核与安全保护。
2. 前端响应契约冻结。
3. 认证存储统一。
4. 请求层、API 层和公共工具唯一化。
5. 架构守卫。
6. 非写入式 lint、format check、build、test 命令。
7. 最小回归测试。
8. 清理已确认的备份、注释旧实现、乱码和死代码。
9. 高风险安全问题的最小安全补丁和独立文档。
10. 更新重构文档。

Phase 1 不处理：

- 全量迁移到 `src/features` / `src/shared` / `src/app`
- 全量拆分大型 Vue 页面
- 服务端分页契约切换
- Alembic 正式数据库迁移
- 金额 Decimal 数据迁移
- 完整 RBAC 体系
- Cookie 认证迁移
- ECharts 深度性能优化
- 大规模后端 Service/Repository 迁移
- UI 重设计
- 数据库数据变更

保持当前前端物理目录：

```text
src/api
src/components
src/composables
src/constants
src/layouts
src/router
src/stores
src/utils
src/views
```

Phase 1 不创建第二套同职责目录和实现。

---

# Phase 1.0：重新复核 Phase 0 结论

读取：

```text
docs/REFACTOR_PLAN.md
```

重新扫描当前工作区，并把问题标记为：

- 已修复
- 仍存在
- 部分修复
- Phase 0 后新增
- 审计结论已失效

重点确认：

- `ProductView.vue` 是否仍有多段注释脚本。
- `products.js` 是否仍使用旧 request config 写法。
- `request.js` 实际返回的是 `response.data` 还是 `response.data.data`。
- `LoginView.vue` 是否已经只调用 Pinia。
- `stores/auth.js` 是否包含 login/register/loadCurrentUser/logout。
- 内容拆解、脚本、视频页面是否已经使用公共 composables/utils。
- 中文乱码是否仍存在于活动代码。
- `.bak` 是否被 Git 跟踪。
- 计划中记录的问题是否已经被人工修复。

更新：

```text
docs/REFACTOR_PLAN.md
```

只补充“当前状态更新”章节，不要重写全部 Phase 0 文档。

---

# Phase 1.1：冻结前端成功响应契约

这是本阶段最重要的技术契约。

后端保持：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

前端成功响应唯一契约：

```text
src/utils/request.js 的成功响应拦截器返回业务 data。
```

因此：

```javascript
const products = await getProductListApi()
```

直接得到业务数组。

禁止：

```javascript
response.data
response.data.data
result.data
res.data
```

规则：

1. `request.js` 是唯一 Axios 实例。
2. 不得创建 `httpClient.js`、第二个 Axios 实例或重复拦截器。
3. API 模块只发请求，不解析 UI 状态。
4. 页面、组件、composable 不处理 Axios Response。
5. API 函数返回业务对象或业务数组。
6. 普通业务错误不在 Axios 拦截器中统一弹 `ElMessage`，防止重复提示。
7. 401 统一处理，但必须防止多请求并发导致多次清理和多次跳转。
8. `Promise.reject(error)` 必须保留。
9. `VITE_API_BASE_URL` 作为 baseURL，提供 `.env.example`。
10. 不能硬编码生产地址。

检查并统一：

```text
src/utils/request.js
src/utils/apiResponse.js
src/api/*.js
src/views/*.vue
src/components/**/*.vue
src/composables/*.js
```

兼容策略：

- `resolveApiData`、`resolveApiList` 可以暂时保留。
- 它们只能作为迁移兼容层。
- 先全局搜索调用方。
- 已经直接接收业务数据的模块不得再二次解包。
- 不得静默改变 API 路径和字段。

为以下内容添加最小单元测试：

- 成功 envelope 解包
- 直接业务数据兼容
- 401 清理只执行一次
- FastAPI 字符串 detail
- FastAPI 422 detail 数组
- 列表数组
- `{ items: [] }`
- `{ list: [] }`

---

# Phase 1.2：统一认证存储

新增并使用唯一认证存储适配器：

```text
ai-video-commerce-web/src/utils/authStorage.js
```

只有该文件允许直接维护这些 key：

```text
access_token
token
token_type
user
remembered_login_account
```

建议 API：

```javascript
getAccessToken()
getTokenType()
getStoredUser()
setAuthData(authData)
clearAuthData()
getRememberedAccount()
setRememberedAccount(account)
clearRememberedAccount()
migrateLegacyAuthData()
```

要求：

1. `request.js` 通过 `authStorage` 获取 Token。
2. `router/index.js` 通过 `authStorage` 判断登录。
3. `stores/auth.js` 通过 `authStorage` 持久化和清理。
4. `LoginView.vue` 不直接保存 Token。
5. `MainLayout.vue` 不直接清理多个 localStorage key。
6. 记住账号也通过适配器。
7. 旧 `token` 只保留一次性迁移兼容。
8. 迁移成功后标准存储使用 `access_token`。
9. 损坏的 user JSON 必须安全清理。
10. request 层不得直接依赖 Pinia，避免循环依赖。
11. 不在本阶段迁移为 HttpOnly Cookie。
12. 不改变登录、注册 API 契约。
13. 退出必须清除全部认证字段。
14. 401 清理必须幂等。
15. 路由 redirect 只允许站内单斜杠路径，拒绝 `//example.com`。

为 authStorage 和 auth store 添加测试：

- 正常登录数据保存
- 旧 token 迁移
- user JSON 损坏
- logout 清理
- remember account
- register 返回 token
- register 不返回 token 时自动 login
- loadCurrentUser
- 401 后状态清理

---

# Phase 1.3：统一 API 模块规范

所有资源 API 文件统一：

```javascript
import request from '../utils/request.js'

const RESOURCE_BASE_URL = '/resource'

export function getResourceListApi(params = {}) {
  return request.get(RESOURCE_BASE_URL, { params })
}

export function getResourceDetailApi(id) {
  return request.get(`${RESOURCE_BASE_URL}/${id}`)
}

export function createResourceApi(data) {
  return request.post(RESOURCE_BASE_URL, data)
}

export function updateResourceApi(id, data) {
  return request.put(`${RESOURCE_BASE_URL}/${id}`, data)
}

export function deleteResourceApi(id) {
  return request.delete(`${RESOURCE_BASE_URL}/${id}`)
}
```

统一检查：

```text
auth.js
products.js
contentAnalysis.js
scripts.js
videoTasks.js
knowledge.js
system.js
systemSettings.js
```

规则：

- 保留现有被调用的函数名。
- 修改前全局搜索引用。
- 兼容别名只有在存在真实调用时保留。
- 没有调用的 detail API 不要直接删除，先记录为候选死导出。
- API 文件禁止 `ElMessage`、Router、Pinia、localStorage、表单转换。
- 不改变 URL、HTTP Method、请求体字段。
- 本地 JS 扩展名风格统一。
- 不混用 `@/` 和相对路径；先检查 Vite alias，再选择一种主风格。

---

# Phase 1.4：公共工具唯一化

现有文件优先复用，不创建同职责新文件：

```text
src/utils/apiResponse.js
src/utils/date.js
src/utils/confirm.js
src/composables/useAsyncList.js
src/composables/usePagination.js
```

### apiResponse.js

职责：

```javascript
resolveApiData()
resolveApiList()
getApiErrorMessage()
```

要求：

- 修复乱码和语法错误。
- FastAPI 422 数组错误合并为可读信息。
- 普通页面不再重复定义 `getErrorMessage`。
- 页面不再重复定义 `resolveListResponse`。

### date.js

职责：

```javascript
formatDate()
formatDateTime()
```

要求：

- `Intl.DateTimeFormat` 模块级复用。
- 页面不得重复定义通用日期格式化。
- 无效日期安全返回原值或 `-`。

### confirm.js

职责：

```javascript
confirmDelete()
```

可增加通用但语义明确的：

```javascript
confirmAction()
```

仅当系统设置“恢复默认设置”等非删除确认确实需要时添加。

禁止把所有弹窗行为塞进万能函数。

### useAsyncList.js

统一提供：

```javascript
list
loading
error
load
reset
```

要求：

- 可配置是否自动提示错误。
- 不重复提示。
- 不静默吞掉错误。
- 调用方可以捕获错误并决定页面行为。

### usePagination.js

统一提供：

```javascript
currentPage
pageSize
total
maxPage
pageList
resetPage
changePageSize
changeCurrentPage
```

要求：

- 支持 ref/computed。
- 源数据不是数组时安全降级。
- 删除最后一页数据后页码自动修正。
- 页面不得重复写 `slice + maxPage watch`。

---

# Phase 1.5：统一常量并防止漂移

现有：

```text
src/constants/platforms.js
src/constants/knowledge.js
```

按当前目录渐进补充：

```text
src/constants/contentAnalysis.js
src/constants/scripts.js
src/constants/videoTasks.js
src/constants/storage.js
```

要求：

1. 平台列表只在一个前端文件定义。
2. 状态值、标签类型、CSS class 映射在对应领域常量文件定义。
3. 页面引用常量，不重复声明数组和映射。
4. 后端 Schema/Enum 是契约权威。
5. 前端常量与后端契约通过测试检查漂移。
6. 不宣称 JavaScript 与 Python 共享同一个运行时常量。
7. 不在本阶段修改数据库枚举或 CHECK 约束。
8. 不改变现有合法状态字符串。

---

# Phase 1.6：建立架构守卫

新增：

```text
ai-video-commerce-web/scripts/check-architecture.mjs
```

至少检查：

1. `axios` 只能在 `src/utils/request.js` 直接导入。
2. `views`、`components`、`composables` 中不得出现成功响应的 `response.data`。
3. 认证 key 只能在 `src/utils/authStorage.js` 直接读写。
4. 删除确认必须通过 `utils/confirm.js`。
5. 页面不得声明通用 `formatDate` / `formatDateTime`。
6. 页面不得声明 `resolveListResponse` / `getErrorMessage`。
7. 检测常见中文乱码特征。
8. 检测 `src` 中 `.bak`。
9. 检测整段注释掉的 `<script setup>`。
10. 检测业务页面直接 import axios。
11. 检测多个 Axios 实例。
12. 检测 `localStorage` 认证 key 散落。
13. 检测 API 文件中的 UI 依赖。
14. 检测 View 直接导入 `ElMessageBox` 做删除确认。
15. 输出准确文件、行号、规则名称和违反内容。
16. 支持少量精确 allowlist。
17. 禁止整目录忽略。
18. 脚本必须只读，不修改源码。

---

# Phase 1.7：质量命令与最小测试

检查当前 `package.json`。

调整为：

```text
lint            只检查，不修改
lint:fix        允许修复
format          执行格式化
format:check    只检查
check:architecture
test
test:run
build
check
```

`check` 至少执行：

```text
lint
format:check
check:architecture
test:run
build
```

要求：

- `npm run lint` 不得包含 `--fix`。
- 不得全仓无关格式化。
- 添加依赖时使用当前包管理器。
- 不升级 Vue、Vite、Element Plus、Axios 等核心依赖。
- 仅增加与当前版本兼容的最小测试依赖。
- 保持 lockfile 一致。
- 测试不得连接真实开发/生产数据库。
- 前端优先使用 Vitest（若与当前 Vite 兼容）。
- 后端只有在可安全隔离时才添加 pytest 基础；不要连接当前 MySQL 真实数据。

前端最小测试范围：

- request 成功解包
- apiResponse
- authStorage
- auth store
- date
- pagination
- confirm 的取消/确认行为
- 典型 API 模块参数透传

后端 Phase 1 最小测试范围：

- 配置加载
- JWT 创建/解析
- 密码 hash/verify
- 固定弱口令初始化被禁用的行为
- 不访问真实数据库的 Schema 测试

后端检查必须使用：

```powershell
D:\ai-video-commerce-platform\ai-video-commerce-api\.venv\Scripts\python.exe -m compileall app
```

不要使用 WindowsApps 的系统 `python.exe`。

---

# Phase 1.8：安全问题最小补丁

Phase 0 已发现：

1. 应用启动隐式 `create_all()`。
2. 自动创建固定 `admin/123456`。
3. 普通登录用户可写多数业务数据和系统设置。
4. 缺少迁移机制。
5. JWT 存储分散。
6. 事务回滚不统一。
7. 仓库公开。

本阶段允许实施的安全补丁：

### A. 禁止固定弱口令管理员

- 移除源码中的固定 `admin/123456` 默认行为。
- 不得再在应用启动时无条件创建该账号。
- 如需开发初始化，必须通过显式环境开关和环境变量提供用户名/密码。
- 默认关闭。
- 缺失环境变量时不得创建用户。
- 不修改现有数据库已有账号。
- 不自动重置已有管理员密码。
- 添加测试和文档。

### B. 限制自动建表

- 生产模式不得在应用启动时执行 `create_all()`。
- 开发模式若保留，必须有显式环境开关且默认安全。
- 不删除现有数据库表。
- 不运行迁移。
- 不修改现有数据。
- 添加 `.env.example`，不包含真实密码。

### C. 凭据审查

扫描：

```text
SECRET_KEY
DATABASE_URL
password
123456
admin
token
private key
```

规则：

- 不在输出中回显真实秘密。
- 发现已提交真实秘密时，删除硬编码并记录“必须人工轮换”。
- 不得声称已完成外部服务密钥轮换。
- 不得自动修改 Git 历史，除非用户明确要求。

### D. RBAC

本阶段不实现完整 RBAC，除非当前 User 模型、角色字段和产品语义已经明确且已有测试。

必须创建：

```text
docs/SECURITY_REMEDIATION.md
```

包含：

- 当前权限矩阵
- 应当限制的写接口
- 管理员角色定义
- 403 响应契约
- 后续实施顺序
- 数据迁移需求
- 风险和回滚

只有在角色语义完全明确时，才允许用独立 commit 限制系统设置写接口；否则只设计，不做不完整授权。

### E. 数据库事务

Phase 1 不重构全部 Service/Repository。

但可：

- 为现有写操作建立统一 rollback 辅助或异常处理策略。
- 仅在不改变成功响应和业务逻辑的前提下修复明显缺少 rollback 的路径。
- 每个模块单独验证。
- 不进行大规模 Router 搬迁。

---

# Phase 1.9：清理

在全局引用搜索和构建通过后清理：

- Git 跟踪的 `.bak`
- `src` 内备份文件
- 大段注释掉的旧 `<script setup>`
- 已确认无引用的旧 import
- 乱码注释和乱码字符串
- 失效兼容函数
- 无引用且确定无产品用途的脚手架代码

禁止直接删除：

- 空 `__init__.py`
- 可能有路由用途的页面
- 未确认的 detail API
- 未确认产品需求的模块
- 唯一备份版本

候选死代码必须先用：

- 静态引用搜索
- Router 检查
- 动态 import 检查
- 构建
- 测试

清理必须单独 commit，不与功能重构混合。

---

## 六、Phase 1 提交划分

至少拆分为以下提交，实际可根据当前状态调整：

```text
chore: preserve pre-phase1 working changes
docs(refactor): update phase 1 current-state notes
test(web): add response auth and utility characterization tests
chore(web): add non-mutating quality scripts
refactor(web-auth): centralize authentication storage
refactor(web-api): freeze response and API contracts
refactor(web-common): standardize shared utilities and constants
chore(web): add architecture guard
chore(cleanup): remove confirmed backups and legacy code
security(api): disable unsafe default admin bootstrap
security(api): gate automatic schema creation by environment
docs(security): add remediation and authorization plan
```

规则：

- 每个提交必须能构建。
- 不把目录移动和逻辑修改混在一个提交。
- 不把全仓格式化和业务修改混在一个提交。
- 不把安全行为变更和普通重构混在一个提交。
- 每个提交后检查 `git diff`、执行对应测试并推送。

---

## 七、每一步真实验证

前端：

```powershell
cd D:\ai-video-commerce-platform\ai-video-commerce-web
npm run lint
npm run format:check
npm run check:architecture
npm run test:run
npm run build
npm run check
```

后端：

```powershell
cd D:\ai-video-commerce-platform\ai-video-commerce-api
.\.venv\Scripts\python.exe -m compileall app
```

如添加安全隔离的 pytest：

```powershell
.\.venv\Scripts\python.exe -m pytest
```

功能冒烟：

- 登录
- 注册
- 当前用户
- 记住账号
- 刷新保持登录
- 退出登录
- 401 清理与跳转
- redirect 返回原页面
- 商品 CRUD
- 内容拆解 CRUD
- 脚本与分镜 CRUD
- 视频任务 CRUD
- 知识库 CRUD
- 系统设置读取与保存
- 商品、脚本、拆解关联下拉框
- 筛选
- 分页
- 日期
- 删除确认
- 取消删除
- 错误提示只出现一次

如果无法自动执行浏览器交互：

- 不得声称通过。
- 记录为“未自动验证”。
- 使用单元测试、构建和静态检查覆盖可验证部分。
- 给出最小人工验证清单。

---

## 八、Phase 1 验收标准

必须全部满足：

1. 当前用户修改未丢失。
2. 工作区中的有效手工重构被保留。
3. 前端构建通过。
4. 后端 compileall 通过。
5. lint 为只读且通过。
6. format check 通过。
7. architecture check 通过。
8. 最小测试通过。
9. API 路径不变。
10. 请求字段不变。
11. 成功响应统一为业务 data。
12. 页面不再读取成功响应 `response.data`。
13. 认证 key 只有 authStorage 直接读写。
14. 401 清理幂等且不重复跳转。
15. 页面不重复定义通用错误解析。
16. 页面不重复定义通用日期格式化。
17. 页面不重复实现删除确认。
18. 页面不重复实现前端分页。
19. 平台常量只有一个前端来源。
20. 业务状态常量按领域集中。
21. 不存在活动代码中文乱码。
22. `src` 中无 `.bak`。
23. 不存在整段注释旧脚本。
24. 不存在第二个 Axios 实例。
25. API 模块不依赖 UI。
26. 默认弱口令管理员不会被自动创建。
27. 生产模式不会自动 `create_all()`。
28. 没有修改现有数据库数据。
29. 未实施不完整的 RBAC。
30. 所有真实执行命令和结果被记录。
31. 每个提交已推送，或明确报告推送失败。
32. `git status` 最终 clean。

---

## 九、文档更新

更新或新增：

```text
docs/REFACTOR_PLAN.md
docs/ARCHITECTURE.md
docs/CODING_STANDARDS.md
docs/DEVELOPMENT.md
docs/SECURITY_REMEDIATION.md
docs/PHASE1_REPORT.md
```

`PHASE1_REPORT.md` 必须包含：

- Phase 1 前工作区状态
- 保留了哪些用户修改
- 修改文件
- 删除文件
- 响应契约
- 认证契约
- 架构守卫规则
- 安全补丁
- 兼容逻辑
- 未解决风险
- 实际命令
- 每条命令真实 exit code
- 测试结果
- 未执行测试
- Git commit 列表
- push 结果
- 最终 git status

---

## 十、禁止事项

绝对禁止：

- 丢弃用户未提交修改
- `git reset --hard`
- `git clean -fd`
- 未确认覆盖文件
- 修改或清空数据库
- 自动迁移当前数据库
- 提交 `.env`
- 输出真实 Secret
- 修改 API 路径
- 修改请求字段
- 静默改变列表返回结构
- 全量迁移到 features/shared/app
- 创建第二套 request/httpClient
- 全仓无关格式化
- 整体迁移 TypeScript
- 升级核心框架
- 改变 UI
- 删除未确认功能
- 过度抽象
- 空 catch 隐藏错误
- 重复 ElMessage
- 声称未执行测试通过
- 在一个提交中混入多类高风险变更

---

## 十一、执行方式

现在立即开始 Phase 1。

执行顺序：

1. 保护当前工作区。
2. 重新复核当前代码。
3. 冻结响应契约并补测试。
4. 统一认证存储。
5. 统一 API 和公共工具。
6. 建立架构守卫。
7. 建立只读质量命令。
8. 处理安全最小补丁。
9. 清理确认的旧代码和备份。
10. 运行完整验证。
11. 更新文档。
12. 分阶段提交并推送。
13. 完成后停止，不进入 Phase 2。

除非存在数据丢失风险、产品语义无法判断、缺少外部权限或无法访问远程仓库，否则不要向用户逐项询问。

遇到问题时优先：

- 搜索全部引用
- 保持兼容
- 最小改动
- 添加测试
- 独立提交
- 如实报告
