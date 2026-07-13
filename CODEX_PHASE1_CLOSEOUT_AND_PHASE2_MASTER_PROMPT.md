# Codex：Phase 1 收尾 + Phase 2 全量执行主指令

你现在负责连续完成两项工作：

1. 完成 Phase 1 最后一次 Git push 收尾。
2. 收尾成功后立即进入并完整执行 Phase 2。

除非涉及真实数据库数据、不可逆迁移、真实凭据、远程权限缺失或无法判断的产品权限语义，否则不要等待用户逐项确认。不要让用户手动执行命令。

## 项目位置

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

Phase 1 分支：

```text
refactor/architecture-standardization
```

Phase 1 报告：

```text
docs/PHASE1_REPORT.md
```

已知情况：

- Phase 1 实现和大部分文档已推送。
- 本地可能领先远程 1 个提交，该提交应只包含 Phase 1 报告。
- 工作区应为 clean。
- Phase 1 已完成 34 项前端测试和 9 项后端隔离测试。
- 已冻结前端成功响应契约、统一 authStorage、建立架构守卫、关闭不安全默认建表和弱口令管理员。

必须以当前仓库真实状态为准。

---

# 一、必须保持的兼容边界

## 前端成功响应

后端继续返回：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

`src/utils/request.js` 成功拦截器返回业务 `data`。

因此 View、Component、Composable 不得重新读取：

```text
response.data
response.data.data
```

不得创建第二个 Axios 实例。

## 认证存储

唯一认证存储适配器：

```text
src/utils/authStorage.js
```

Router、Store、Layout、页面和组件不得重新散落认证 localStorage 操作。

## API

保持以下现有路径、HTTP Method、请求字段和响应 envelope：

```text
/api/auth
/api/products
/api/content-analyses
/api/scripts
/api/video-tasks
/api/knowledge-items
/api/system-settings
```

不得静默改变列表接口 `data` 为数组的现有结构。

## 数据安全

- 不访问、清空或修改用户当前真实数据库。
- 不对真实库执行 Alembic upgrade。
- 不提交 `.env`、数据库密码、JWT Secret、Token 或私钥。
- 测试只能使用隔离数据库、dependency override、临时数据库或显式 `TEST_DATABASE_URL`。
- 测试数据库名称不含 `test/testing/ci` 时，拒绝运行破坏性测试。

---

# 二、Phase 1 Git 收尾

先执行并记录：

```powershell
cd D:\ai-video-commerce-platform
git branch --show-current
git status --short
git log --oneline -5
git branch -vv
git remote -v
git rev-list --left-right --count origin/refactor/architecture-standardization...refactor/architecture-standardization
```

确认：

1. 当前分支是 `refactor/architecture-standardization`。
2. 工作区 clean。
3. 本地领先远程的提交仅为 `docs/PHASE1_REPORT.md` 报告提交。
4. 没有未推送业务源码。
5. 没有未跟踪凭据或临时文件。

符合预期后执行：

```powershell
git push origin refactor/architecture-standardization
git fetch origin
git rev-list --left-right --count origin/refactor/architecture-standardization...refactor/architecture-standardization
git status --short
```

同步成功标准：

```text
0 0
working tree clean
```

网络失败最多合理重试 3 次；禁止 force push、重复提交、reset、rebase 已推送历史。若仍失败，保留本地提交并如实记录，然后继续本地 Phase 2，在后续每次 push 时重试。

Phase 1 收尾后创建独立 Phase 2 分支：

```powershell
git switch -c refactor/phase2-backend-standardization
git push -u origin refactor/phase2-backend-standardization
```

如果分支已存在，先核对来源和历史，禁止覆盖未知工作。不要直接在 main 开发，不自动合并 main。

---

# 三、Phase 2 总目标

完整执行：

1. 建立隔离 API 集成测试基础。
2. 建立后端标准分层：Router → Service → Repository → Database。
3. 迁移全部现有业务模块。
4. 统一事务边界、rollback、领域异常和 HTTP 错误映射。
5. 统一 FastAPI response_model 和 OpenAPI 契约，保持真实响应兼容。
6. 建立最小完整 RBAC 和 401/403 语义。
7. 建立安全管理员创建/晋升流程。
8. 建立 Alembic 基础和可审查迁移，但不运行到用户真实数据库。
9. 建立真实 live/ready 健康检查和安全日志。
10. 补齐前端权限判断与 403 处理。
11. 完成完整业务链 API 集成测试。
12. 建立 CI 质量门禁。
13. 完成文档、分阶段 commit、push 和 Phase 2 报告。

Phase 2 不处理：

- 服务端分页切换
- 列表响应结构变更
- Float → Decimal/Numeric
- HttpOnly Cookie / Refresh Token
- ECharts 深度优化
- 全前端目录大迁移
- UI 重设计
- 自动合并 main

---

# 四、Phase 2.0 当前状态复核

读取：

```text
docs/REFACTOR_PLAN.md
docs/PHASE1_REPORT.md
docs/ARCHITECTURE.md
docs/CODING_STANDARDS.md
docs/DEVELOPMENT.md
docs/SECURITY_REMEDIATION.md
```

扫描后端 main、config、database、security、init_db、全部 Router、Model、Schema；扫描前端 request、authStorage、auth store、router、API、相关页面。

创建：

```text
docs/PHASE2_PLAN.md
```

必须包含：

- 当前真实目录和依赖方向
- 当前表关系和认证字段
- Router 直接 ORM/commit 的位置
- 当前异常和 rollback 状态
- 测试数据库策略
- 权限矩阵
- 模块迁移顺序
- Alembic 策略
- API 兼容风险
- commit 划分
- 回滚方案

计划完成后直接继续执行，不需暂停等待。

---

# 五、隔离测试基础设施

测试数据库优先级：

1. 显式 `TEST_DATABASE_URL`，且数据库名包含 `test/testing/ci`。
2. SQLAlchemy 模型兼容时使用临时 SQLite 和 dependency override。
3. Docker 可用时创建临时 MySQL 测试容器，使用临时数据卷和专用端口。
4. 都不可用时，完成单元测试和静态分层，但明确标记 MySQL 集成测试未执行。

绝对禁止回退使用 `DATABASE_URL`。

建立：

```text
tests/
├─ conftest.py
├─ unit/
├─ integration/
├─ api/
└─ fixtures/
```

提供：

- TestClient/ASGI client
- 测试 Session fixture
- dependency override
- admin/editor/viewer 测试用户
- 测试 Token
- 每次测试 rollback 或临时库重建
- 非测试数据库硬门禁

至少验证：

```text
200/201
401
403
404
409
422
500
成功 envelope
事务 rollback
```

---

# 六、后端公共基础设施

渐进建立：

```text
app/
├─ core/
│  ├─ config.py
│  ├─ security.py
│  ├─ exceptions.py
│  └─ logging.py
├─ database/
│  ├─ base.py
│  ├─ session.py
│  └─ unit_of_work.py（仅确有必要时）
├─ dependencies/
│  ├─ auth.py
│  ├─ permissions.py
│  └─ database.py
├─ api/
│  ├─ router.py
│  └─ routers/
├─ repositories/
├─ services/
├─ models/
├─ schemas/
└─ constants/
```

规则：

- 只能保留一套 Session 工厂。
- 只能保留一套 security 实现。
- Router 不直接查询 ORM，不 commit/rollback。
- Repository 只查询、add、delete、flush，不 commit。
- Service 编排业务和事务，负责 commit/rollback。
- Service 不依赖 FastAPI Request/Response，不抛 HTTPException。
- Repository 不组装 HTTP 响应。
- 旧路径只允许短期 re-export，不能长期双实现。

建立领域异常：

```text
DomainError
NotFoundError
ConflictError
ValidationError
PermissionDeniedError
AuthenticationError
```

通过全局处理器映射 401/403/404/409/422/500，并保持前端现有错误解析兼容。

建立泛型响应 Schema：

```text
ApiResponse[T]
ErrorResponse
```

现有列表端点的 `data` 继续是数组，不引入分页对象。

---

# 七、全部业务模块分层迁移

按顺序逐模块完成；每个模块独立测试、commit、push。

## 1. Products

建立 Product Repository、Service、薄 Router。覆盖 list/detail/create/update/delete、404、冲突、rollback、字段和 envelope 兼容。

## 2. Content Analysis

覆盖商品关联、平台、状态、CRUD、非法关联、删除策略和 rollback。

## 3. Scripts / Scenes

覆盖 Script 与 Scene 原子事务、Scene 顺序、全量替换失败回滚、商品与内容拆解关联、状态和完整 CRUD。

## 4. Video Tasks

覆盖 Script 关联、状态转换、平台、视频字段、CRUD 和 rollback。

## 5. Knowledge

覆盖 CRUD、usage count 原子增加、分类、状态、优先级和 rollback。

## 6. System Settings

覆盖读取、更新、恢复默认、全局单例策略、管理员权限和 rollback；禁止启动时隐式写入。

## 7. Auth

覆盖注册、登录、当前用户、停用用户、角色、JWT、密码、管理员创建/晋升和 rollback；不得返回密码字段。

每个模块完成标准：

- Router 不直接 import ORM Model。
- Router 不 commit/rollback。
- Service 不抛 HTTPException。
- API 路径、Method、字段、envelope 不变。
- 测试、compileall、前端 check 通过。
- 独立 commit 和 push。

---

# 八、RBAC

先检查 User 模型是否已有：

```text
role
is_admin
permissions
is_active
status
```

不得假设。

若已有角色字段，集中实现权限依赖。

若没有，允许增加最小角色，但必须：

1. 通过 Alembic migration。
2. 不对用户真实库执行。
3. 在隔离库验证 upgrade/downgrade。
4. 不硬编码用户名为管理员。
5. 不恢复 admin/123456。
6. 提供显式管理员创建/晋升 CLI。
7. 不自动修改用户当前真实数据。

建议角色：

```text
admin
editor
viewer
```

建议矩阵：

- admin：全部读取、全部业务 CRUD、系统设置、角色管理。
- editor：业务读取和 CRUD；系统设置只读；不能管理角色。
- viewer：只读。

兼容策略：

- 既有普通用户迁移方案可默认 editor，以保持原业务能力。
- 新注册用户默认 viewer。
- 管理员通过显式 CLI 创建或晋升。
- 如果实际产品语义冲突，不运行真实迁移；完成代码、迁移、测试和文档，并明确需产品确认。

服务端权限检查必须是权威。前端隐藏按钮仅用于体验。

测试至少覆盖：

- viewer 读成功、写 403
- editor 业务 CRUD 成功、系统设置写 403
- admin 全部成功
- 未登录 401
- 停用用户失败
- 伪造角色 Token 不得绕过服务端

---

# 九、Alembic

建立标准 Alembic：

```text
alembic.ini
alembic/
├─ env.py
├─ script.py.mako
└─ versions/
```

要求：

- 不硬编码真实 URL。
- 导入全部 metadata。
- 迁移支持 upgrade/downgrade。
- 在临时空库和模拟既有库验证。
- 不对用户真实数据库执行。
- 不用 create_all 代替 migration。
- 应用启动不自动 migration。

新增：

```text
docs/DATABASE_MIGRATIONS.md
```

说明新库初始化、既有库 stamp、upgrade、downgrade、备份、恢复和生产审批。

---

# 十、健康检查和日志

保留现有健康接口兼容，新增或标准化：

```text
/health/live
/health/ready
```

要求：

- live 只表示进程可响应。
- ready 执行轻量数据库探测。
- DB 不可用时 ready 失败。
- 不泄露 URL、用户名、Secret、堆栈。
- 日志包含 method、path、status、duration，可含 request id。
- 不记录 Authorization、密码、Token。
- 500 对外返回通用信息。

---

# 十一、前端权限兼容

只做必要修改，不重设计 UI。

建立集中权限判断，禁止页面散落角色字符串，例如：

```text
canRead
canCreate
canUpdate
canDelete
canManageSettings
canManageUsers
```

要求：

- User 支持 role/is_active。
- 403 显示“当前账号无权限执行此操作”。
- 403 不清理登录状态。
- 401 才清理并跳转。
- 按钮可隐藏/禁用，但服务端必须检查。
- 增加权限单元测试。
- 不改变页面布局和路由。

---

# 十二、完整业务链 API 集成测试

在隔离数据库验证：

```text
创建测试用户/管理员
→ 登录
→ 当前用户
→ 商品
→ 内容拆解
→ 脚本与分镜
→ 视频任务
→ 知识库
→ 系统设置
→ 更新
→ 删除
→ 关联检查
→ rollback
```

覆盖：

- 正常链路
- 缺少 Token
- 无权限
- 非法关联 ID
- 非法状态
- 重复冲突
- 删除不存在
- 事务中途失败
- 401/403/404/409/422/500

SQLite 测试不能宣称已验证 MySQL 外键、锁、字符集和约束。

---

# 十三、CI

新增：

```text
.github/workflows/ci.yml
```

前端执行：

```text
npm ci
npm run lint
npm run format:check
npm run check:architecture
npm run test:run
npm run build
```

后端执行：

```text
compileall
pytest
```

可使用 CI 临时 MySQL service，但不能使用真实 Secret。

禁止：

- `|| true`
- 写入式 lint/format
- 自动部署
- 自动修改数据库
- 隐藏测试失败

Node/Python 版本必须与项目依赖兼容。

---

# 十四、Git 提交建议

至少拆分为：

```text
docs(phase2): add execution plan
test(api): add isolated integration foundation
refactor(api-core): standardize session responses and exceptions
refactor(api-products): add product service and repository
refactor(api-content): add content service and repository
refactor(api-scripts): add script and scene service and repository
refactor(api-videos): add video task service and repository
refactor(api-knowledge): add knowledge service and repository
refactor(api-settings): add system settings service and repository
refactor(api-auth): add auth service and repository
feat(authz): add centralized roles and permissions
feat(db): add alembic foundation and role migration
feat(health): add liveness readiness and safe logging
refactor(web-authz): add centralized frontend permissions
test(api-flow): add full business-chain integration tests
ci: add frontend and backend quality gates
docs(phase2): add completion report
```

每个提交必须可构建、可测试，并执行 push。禁止 force push、自动合并 main、全仓无关格式化。

---

# 十五、验证命令

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
.\.venv\Scripts\python.exe -m pytest -q
```

Alembic 只能对隔离测试库：

```powershell
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\alembic.exe downgrade -1
.\.venv\Scripts\alembic.exe upgrade head
```

Git：

```powershell
git status --short
git diff --check
git log --oneline -10
git branch -vv
```

---

# 十六、Phase 2 验收标准

必须满足：

1. Phase 1 最后报告提交已推送，或真实记录仍失败。
2. Phase 2 使用独立分支。
3. 最终工作区 clean。
4. 前端全部检查、测试和 build 通过。
5. 后端 compileall 和 pytest 通过。
6. 测试未连接用户真实数据库。
7. 全部 Router 为薄层。
8. Router 不直接 ORM，不 commit/rollback。
9. Repository 不 commit。
10. Service 统一事务边界，不抛 HTTPException。
11. 领域异常统一映射。
12. API 路径、Method、字段和 envelope 不变。
13. 列表 `data` 仍为数组。
14. 全部业务模块完成分层和测试。
15. Scripts/Scenes 原子事务通过。
16. System Settings 受管理员权限控制。
17. 401/403 语义明确。
18. 服务端 RBAC 有效。
19. 前端 403 不清理登录。
20. 无固定弱口令管理员。
21. 有安全管理员创建/晋升方式。
22. Alembic 可用且只在隔离库验证。
23. 未对真实数据库运行 migration。
24. live/ready 正确。
25. 日志不泄密。
26. CI 为只读质量门禁。
27. 不改 UI。
28. 不切换服务端分页。
29. 不迁移 Float 金额。
30. 不迁移 Cookie 认证。
31. 所有提交已 push，或逐项记录失败。
32. 完成后停止，不进入 Phase 3。

---

# 十七、文档交付

新增或更新：

```text
docs/PHASE2_PLAN.md
docs/ARCHITECTURE.md
docs/CODING_STANDARDS.md
docs/DEVELOPMENT.md
docs/SECURITY_REMEDIATION.md
docs/DATABASE_MIGRATIONS.md
docs/API_CONTRACTS.md
docs/PERMISSIONS.md
docs/PHASE2_REPORT.md
```

`PHASE2_REPORT.md` 必须记录：

- Phase 1 push 收尾
- Phase 2 分支
- 前后状态
- 实际目录
- 模块迁移
- API 兼容
- 事务策略
- 权限矩阵
- Alembic
- 测试数据库类型
- 前端/后端/API 测试真实结果
- 未执行测试
- CI 状态
- 每条命令和 exit code
- commit 列表
- push 结果
- 最终远程同步状态
- 剩余风险
- 最终 git status

---

# 十八、绝对禁止

- 修改用户当前真实数据库
- 对真实库执行 Alembic upgrade
- 使用 DATABASE_URL 作为测试库
- 删除用户数据
- 提交或输出真实 Secret
- hardcode 管理员用户名
- 恢复 admin/123456
- force push
- reset --hard
- git clean -fd
- 自动合并 main
- 修改 API 路径或请求字段
- 改变列表 data 数组
- 创建第二套 Axios、Session 或 Security
- Router/Service 双重 commit
- Service 抛 HTTPException
- Repository 返回 HTTP Response
- 只做前端权限隐藏
- 全仓无关格式化
- 静默吞异常
- 用 `|| true` 隐藏失败
- 声称未执行测试通过
- 把 SQLite 测试宣传为完整 MySQL 验证
- 进入 Phase 3

---

# 十九、立即开始

现在连续完成：

1. Phase 1 最后一次 push。
2. 创建 Phase 2 分支。
3. 生成 Phase 2 计划。
4. 建立隔离测试环境。
5. 建立公共后端基础设施。
6. 逐模块完成全部 Service/Repository 分层。
7. 完成权限体系和管理员安全流程。
8. 建立并测试 Alembic。
9. 完成健康检查和安全日志。
10. 完成前端权限兼容。
11. 完成完整 API 集成测试。
12. 建立 CI。
13. 更新文档。
14. 分阶段 commit 和 push。
15. 生成 `docs/PHASE2_REPORT.md`。
16. 最终确认远程同步和 clean 状态。
17. 停止，不进入 Phase 3。

不要要求用户逐条执行命令。你负责完整实施、验证、提交、推送和报告。
