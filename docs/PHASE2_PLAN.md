# Phase 2 后端标准化执行计划

> 执行分支：`refactor/phase2-backend-standardization`  
> 审计日期：2026-07-13  
> 基线：Phase 1 本地完成提交 `8200548`；远程推送因 GitHub 连接失败待后续重试  
> 安全边界：不连接或修改用户真实数据库，不对真实库运行 Alembic，不改变现有 API 路径、请求字段、成功 envelope 或列表数组结构。

## 1. 当前真实架构与依赖方向

前端当前为 `views/components/composables -> src/api -> src/utils/request.js -> Axios`。`request.js` 是唯一 Axios 实例，成功拦截器把 `{code,message,data}` 解包为业务 `data`；`authStorage.js` 是认证 localStorage 的唯一适配器。

后端当前为：

```text
app/main.py
  -> app/api/{auth,products,content_analysis,scripts,video_tasks,knowledge,system_settings}.py
       -> app/security.py + app/database.py
       -> app/models/*（直接查询和写入）
       -> app/schemas/*
  -> MySQL
```

目标依赖方向：

```text
main -> api.router -> api.routers -> services -> repositories -> database/models
                    -> dependencies -> core
                    -> schemas
```

- Router 只适配 HTTP、依赖和 response schema，不 import ORM Model，不 commit/rollback。
- Service 编排业务规则和事务；成功 commit，任何异常 rollback；不依赖 FastAPI，不抛 `HTTPException`。
- Repository 只做查询、add、delete、flush，不 commit，不返回 HTTP Response。
- `app/database/session.py` 是唯一 Engine、Session 工厂和请求 Session 来源；旧 `app/database.py` 仅短期 re-export。
- `app/core/security.py` 是唯一密码/JWT 实现；旧 `app/security.py` 仅短期 re-export。

## 2. 当前表关系和认证字段

```text
users (id, username unique, display_name, password_hash, role, is_active)
products
  <- content_analyses.product_id CASCADE
  <- scripts.product_id CASCADE
       <- script_scenes.script_id CASCADE + (script_id, scene_number) unique
       <- video_tasks.script_id CASCADE
  <- video_tasks.product_id CASCADE
  <- knowledge_items.product_id SET NULL
system_settings (固定 id=1 的全局单例)
```

认证以 `users.username` 作为 JWT `sub`，Token 当前还携带 `user_id` 和 `role`，但服务端每次请求重新查询 User，因此授权必须以数据库最新 `role/is_active` 为准，不能信任 Token 中伪造或过期的角色。现有角色列是 `String(30)`，默认值为 `user`，没有数据库枚举或权限表。

## 3. Router 直接 ORM/事务位置

| 模块 | 当前直接职责 | 事务与异常现状 | 严重级别 |
|---|---|---|---|
| `api/auth.py` | 查用户、构造 User、hash、JWT、commit | 注册仅捕获 `IntegrityError` 并 rollback | P0 |
| `api/products.py` | 全 CRUD、字段赋值 | 所有写操作直接 commit，无统一 rollback | P1 |
| `api/content_analysis.py` | 商品关联校验、筛选、CRUD | 直接 commit，无统一 rollback | P1 |
| `api/scripts.py` | 商品/拆解关联、场景替换、CRUD | 仅重复分镜捕获 `IntegrityError`；其他数据库错误无统一映射 | P0 |
| `api/video_tasks.py` | 商品/脚本匹配、筛选、CRUD | 直接 commit，无状态转换领域规则 | P1 |
| `api/knowledge.py` | 商品校验、筛选、CRUD、usage_count 自增 | Python 读改写存在并发丢更新风险；无统一 rollback | P1 |
| `api/system_settings.py` | GET 时隐式创建单例、更新、commit | 读取接口会写数据库；任意登录用户可更新 | P0 |

当前 `security.py` 同时负责密码、JWT、认证依赖和 User 查询，并直接抛 `HTTPException`。`main.py` 未配置统一领域异常处理，500 可能暴露默认行为；健康检查固定声称数据库运行。

## 4. 测试数据库策略

优先使用临时 SQLite 文件/内存库和 FastAPI dependency override，因为当前模型使用 SQLAlchemy 通用类型，可覆盖接口、事务和权限行为。测试会显式创建独立 Engine/Session，并通过 `app.dependency_overrides` 替换请求 Session；每项测试重建临时 schema 或在事务中回滚。

硬门禁：

- 绝不读取 `DATABASE_URL` 作为测试回退。
- 若提供 `TEST_DATABASE_URL`，解析后的数据库名必须包含 `test`、`testing` 或 `ci`，否则测试立即拒绝。
- SQLite 结果只证明应用层契约和事务，不宣称覆盖 MySQL 外键执行、锁、字符集或隔离级别。
- 若当前环境没有安全的临时 MySQL，不执行 MySQL 集成测试并在报告中明确记录。

测试目录按 `tests/{unit,integration,api,fixtures}` 建立，提供 app client、Session、admin/editor/viewer、Token 和依赖覆盖。覆盖 200/201、401、403、404、409、422、500、成功 envelope、rollback 和完整业务链。

## 5. 权限矩阵

| 能力 | admin | editor | viewer |
|---|---:|---:|---:|
| 业务资源读取 | 是 | 是 | 是 |
| 商品/拆解/脚本/视频/知识库 CRUD | 是 | 是 | 否（403） |
| 知识引用计数 | 是 | 是 | 否（写操作） |
| 系统设置读取 | 是 | 是 | 是 |
| 系统设置更新/恢复默认 | 是 | 否（403） | 否（403） |
| 用户角色管理 | 是 | 否 | 否 |

兼容方案：迁移将既有 `user` 转为 `editor` 以保持原业务写能力，新注册用户默认 `viewer`；未知角色不提升为管理员。迁移只在隔离库验证，真实数据迁移需部署审批。管理员仅通过显式 CLI 创建或晋升，要求显式强密码/目标用户名，不硬编码账号，不在启动时自动执行。

401 表示无有效身份、用户不存在或已停用；403 表示身份有效但权限不足。前端只在 401 清理登录，403 显示“当前账号无权限执行此操作”。

## 6. 模块迁移顺序与预计文件

1. 计划：新增本文件。
2. 隔离测试与核心：新增 `tests/conftest.py`、fixtures、`app/core/*`、`app/database/*`、`app/dependencies/*`、`app/schemas/common.py`、`app/api/router.py`，调整 `main.py` 及旧路径 re-export。
3. Products：新增 `repositories/product.py`、`services/product.py`，改薄 `api/products.py`，新增 API/Service 测试。
4. Content Analysis：对应 repository/service/router/tests，补平台/状态校验与非法关联。
5. Scripts/Scenes：对应 repository/service/router/tests，验证场景全量替换原子性和顺序。
6. Video Tasks：对应 repository/service/router/tests，集中状态集合/转换和关联校验。
7. Knowledge：对应 repository/service/router/tests，使用数据库原子 update 增加 usage count。
8. System Settings：对应 repository/service/router/tests，读取不隐式写入，更新仅 admin；恢复默认仅在显式 API 存在时实现，不新增破坏兼容的路径。
9. Auth/RBAC：User repository/service、集中权限依赖、角色常量、注册/login/me、管理员 CLI 与测试。
10. Alembic：新增 `alembic.ini`、`alembic/*`、角色兼容迁移；只在临时空库和模拟旧库验证 upgrade/downgrade。
11. Health/logging：`/health/live`、`/health/ready`、兼容 `/api/health`、请求 ID/耗时安全日志。
12. 前端权限：新增集中 permission utility/composable，更新 auth store、request 403 行为和必要按钮条件，补 Vitest；不改布局和路由。
13. 业务链、CI、文档：完整 API 流程测试、`.github/workflows/ci.yml` 和 Phase 2 文档集。

每一模块独立 commit；每次提交后至少运行相关 pytest、`compileall` 和前端架构检查，并尝试 push。最终运行完整前后端门禁。

## 7. 领域异常、响应和事务策略

领域异常为 `DomainError`、`AuthenticationError`、`PermissionDeniedError`、`NotFoundError`、`ConflictError`、`ValidationError`。全局处理器映射到 401/403/404/409/422；未处理异常 rollback 后对外返回通用 500，不回传堆栈或敏感配置。

成功继续返回：

```json
{"code": 200, "message": "操作成功", "data": {}}
```

使用泛型 `ApiResponse[T]` 和 `ErrorResponse` 声明 OpenAPI；真实 message 和 code 保持各端点现状，列表 `data` 始终为数组。Service 方法以一次调用为事务边界；Repository 允许 flush 获取主键，但禁止 commit。

## 8. Alembic 策略

- Alembic URL 从显式配置注入，不硬编码或输出真实 URL。
- `target_metadata` 导入全部模型的同一 `Base.metadata`。
- 初始迁移表达当前 schema；角色迁移单独提交，将 `user -> editor`，新默认改为 `viewer`，upgrade/downgrade 可审查。
- 临时 SQLite 空库验证完整 upgrade/downgrade；模拟旧角色数据验证数据迁移。SQLite 限制单独记录。
- 真实环境只提供 `stamp/upgrade/downgrade` 操作文档，不自动执行。

## 9. API 兼容风险

- 引入 response_model 时 Pydantic 序列化可能改变 datetime/None 表现；用契约测试锁定。
- 统一异常可能把历史 400 改成 409/422；仅对主指令明确的语义采用新状态，并在测试/文档记录。
- 角色默认从 `user` 迁移为 editor/viewer 涉及产品权限语义；代码和迁移完成但不触碰真实库。
- SQLite 默认不执行 MySQL `ON DELETE` 语义，测试需显式启用 foreign keys；仍不能代替 MySQL 验证。
- System Settings 读取不再自动建行：缺失单例应返回可识别错误或显式默认展示，不能在 GET 隐式写库。
- Token 中的 role 不能作为授权来源；每请求查询数据库可能影响性能，但保持安全兼容。

## 10. Commit 划分

采用主指令建议的 docs/test/core/逐模块/authz/db/health/web/test-flow/ci/docs 提交序列。用户已有执行指令文档已由独立保护提交保存。每次仅暂存当前阶段文件，提交前运行 `git diff --cached --check` 和凭据扫描；禁止 force push、reset、rebase 已推送历史和自动合并 main。

## 11. 回滚方案

- 代码回滚按独立模块 commit 反向 revert，不回滚 Phase 1 的单 Axios、authStorage 或安全启动门禁。
- 分层迁移保留旧 import 路径 re-export，出现部署问题可回滚单 Router/Service 提交。
- Alembic 迁移具有 downgrade；生产回滚必须先备份、审批并验证，Codex 本阶段不在真实库执行。
- RBAC 如造成兼容问题，只回滚授权代码/迁移提交，不把未知用户提升为 admin，不恢复弱口令或启动种子。
- 远程网络失败时保留本地提交和精确 hash，后续阶段 push 一并重试，不改写历史。

## 12. Phase 2 验收

- 独立 Phase 2 分支；最终工作区 clean，提交可追溯并尽可能推送。
- 全部 Router 薄层、无 ORM/commit/rollback；Repository 不 commit；Service 统一事务和领域异常。
- API 路径、Method、字段、envelope 和列表数组兼容；OpenAPI 有 response_model。
- 七个业务模块和完整业务链在隔离数据库测试；覆盖 401/403/404/409/422/500 与 rollback。
- RBAC 服务端权威，前端 403 不退出；管理员流程显式且无固定弱口令。
- Alembic 仅在隔离库验证；没有访问或修改真实数据库。
- live/ready 语义正确，日志不记录 Authorization、密码、Token、Secret。
- 前端全部检查/build、后端 compileall/pytest 通过；未执行项真实记录。
- CI 只做质量门禁，不部署或迁移数据库；完成报告后停止，不进入 Phase 3。
