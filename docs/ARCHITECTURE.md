# 项目架构约定

## 1. 系统边界

项目采用 Vue 3 前端与 FastAPI 后端分离架构：

```text
Browser
  -> Vue Router / Pinia / Views
  -> src/api/*.js
  -> src/utils/request.js (唯一 Axios 实例)
  -> /api/*
  -> FastAPI Router / Dependencies
  -> Services
  -> Repositories
  -> SQLAlchemy Session / Models
  -> MySQL
```

> 历史说明：Phase 1 保持了当时的物理目录，没有进行
> features/shared/app 大迁移。该说明只描述 Phase 1 基线；当前后端依赖方向
> 已由 Phase 2 的 Router → Service → Repository 分层取代，见第 5、8 节。

## 2. 前端依赖方向

```text
main -> router -> layouts/views
views -> components/composables/api/constants/utils
components -> constants/utils（展示组件原则上不请求 API）
composables -> api/constants/utils
api -> utils/request.js
request.js -> Axios + authStorage
```

约束：

- `src/utils/request.js` 是唯一 Axios 实例和响应拦截器。
- API 模块只描述 URL、Method、params 和 data，不依赖 Element Plus、Router、Pinia 或 localStorage。
- View、Component 和 Composable 只接收业务 data，不解析成功响应 `response.data`。
- 认证相关 localStorage key 只由 `src/utils/authStorage.js` 维护。
- 通用错误、日期、确认和前端分页分别由现有公共工具负责。
- 平台选项只有 `constants/platforms.js` 一个前端来源；业务状态按领域常量文件维护。

## 3. 成功与错误响应契约

后端成功 envelope 保持：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

请求拦截器将 envelope 解包为业务 data。因此：

```javascript
const products = await getProductListApi()
```

`products` 是业务数组，而不是 Axios Response 或 envelope。

普通业务错误由调用页面通过 `getApiErrorMessage()` 解析和显示；请求层不统一弹普通错误，避免重复消息。401 由请求层幂等清理认证数据并跳转登录页。

## 4. 认证契约

`authStorage.js` 负责：

- 标准 `access_token`、`token_type` 和 `user` 存取。
- 旧 `token` 一次性迁移并删除。
- 损坏 user JSON 安全清理。
- 记住账号存取。
- 退出和 401 的幂等清理。

Pinia Auth Store 管理响应式状态；Router 和 Request 通过 authStorage 读取会话，Request 不依赖 Pinia，以避免循环依赖。

当前仍使用 localStorage Bearer Token。HttpOnly Cookie、刷新令牌和会话撤销不属于 Phase 2。

## 5. 后端依赖方向

```text
main.py -> api.router -> api modules -> services -> repositories -> database/models
                         |             |
                         v             v
                   dependencies      core/domain
```

Phase 1 曾采用 Router 直接依赖 Schema、Model、Database 和 Security 的结构，
并把 Service/Repository 留待后续阶段；这是历史基线，不是当前架构。
Phase 2 已完成 Service/Repository 分层，Router 不再直接操作 ORM 或提交事务。

## 6. 数据库启动安全

默认启动：

- 不执行 `create_all()`。
- 不打开种子 Session。
- 不创建管理员或系统设置。

仅非生产环境可通过显式开关执行开发初始化。生产环境开启任一自动数据库写入开关会在 Settings 校验阶段失败。正式数据库演进使用 Phase 2 已引入的 Alembic，并且必须显式提供 `ALEMBIC_DATABASE_URL`；应用启动不会自动迁移。

## 7. 自动架构守卫

`scripts/check-architecture.mjs` 阻止：

- 第二个 Axios 导入或实例。
- UI 层成功响应二次解包。
- 认证 localStorage 访问散落。
- View 内通用日期、错误、响应、删除确认或分页重复实现。
- API 层 UI 依赖。
- `src` 下 `.bak`、注释旧脚本和常见乱码。

守卫只读并输出规则、文件、行号和命中内容。

## 8. Phase 2 后端实际架构细则

```text
main -> api.router -> api modules -> services -> repositories -> database/models
                         |             |
                         v             v
                   dependencies      core/domain
```

- `app/database/session.py` 是唯一生产 Session 工厂；`app/database.py` 已删除。
- `app/core/security.py` 是唯一密码/JWT 实现；旧 `app/security.py` 仅 re-export。
- Router 只处理 HTTP、Depends、Schema 和 envelope，不 import ORM、不提交事务。
- Repository 查询、add/delete/flush，不 commit。
- Service 是写事务边界，统一 commit/rollback，并抛领域异常而非 HTTPException。
- `app/core/exceptions.py` 由全局 handler 映射 401/403/404/409/422/500。
- 全部现有业务路径使用 `ApiResponse[T]` response_model，列表 data 仍为数组。
- `/health/live` 不访问数据库；`/health/ready` 执行 `SELECT 1`；兼容 `/api/health`。
- Alembic 不随应用启动，必须显式提供 `ALEMBIC_DATABASE_URL`。