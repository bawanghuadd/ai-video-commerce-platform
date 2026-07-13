# 开发与验证指南

## 1. 前端

```powershell
cd D:\ai-video-commerce-platform\ai-video-commerce-web
npm install
Copy-Item .env.example .env.local
npm run dev
```

默认 `VITE_API_BASE_URL=/api`，Vite 开发服务器把 `/api` 代理到本机 FastAPI 端口。生产环境应通过部署配置设置实际 API Base URL 或使用同源 `/api`，不要把生产地址硬编码进源码。

常用命令：

```powershell
npm run lint                # 只读
npm run lint:fix            # 显式修复
npm run format:check        # 只读
npm run format              # 显式格式化
npm run check:architecture
npm run test
npm run test:run
npm run build
npm run check
```

`npm run check` 顺序执行 lint、format check、架构守卫、测试和构建。

## 2. 后端

```powershell
cd D:\ai-video-commerce-platform\ai-video-commerce-api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

填写本地数据库连接和唯一高熵 `SECRET_KEY`。真实 `.env` 已被 Git 忽略，禁止提交。

检查：

```powershell
.\.venv\Scripts\python.exe -m compileall app
.\.venv\Scripts\python.exe -m pytest -q
```

测试不会启动应用、连接当前 MySQL 或修改数据库。

## 3. 安全数据库初始化

默认配置不会建表或写种子。已有数据库按原样使用。

仅本地、全新开发数据库确实需要临时初始化时，显式设置：

```dotenv
APP_ENV=development
AUTO_CREATE_SCHEMA=true
SEED_ADMIN=true
SEED_SYSTEM_SETTINGS=true
ADMIN_BOOTSTRAP_USERNAME=local_admin
ADMIN_BOOTSTRAP_PASSWORD=replace-with-a-strong-local-password
```

注意：

- 这些开关默认必须为 false。
- 生产环境启用会导致配置校验失败。
- 管理员密码至少 12 位且必须从环境提供。
- 已存在管理员不会被重置密码。
- 正式环境应由 Alembic 和独立受控账号创建流程管理，不使用开发初始化。

## 4. 启动

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

启动前确保所需表已经存在。默认安全配置不会自动创建缺失表。

## 5. 手工冒烟清单

自动检查不连接真实业务数据库，因此合并或发布前应在隔离测试环境手工确认：

- 登录、注册、当前用户、记住账号、刷新、退出和 401。
- Redirect 返回原站内页面并拒绝外部双斜杠地址。
- 商品、内容拆解、脚本分镜、视频任务、知识库 CRUD。
- 系统设置读取、保存和取消恢复。
- 关联下拉框、筛选、分页、日期和删除确认。
- 错误消息只显示一次。

不得在生产数据库执行冒烟写操作。

## 6. Phase 2 隔离 API 测试

后端 pytest 默认使用临时 SQLite 和 FastAPI dependency override，每项测试重建 schema。若显式提供 `TEST_DATABASE_URL`，数据库名必须包含 `test`、`testing` 或 `ci`；测试绝不回退 `DATABASE_URL`。

```powershell
cd ai-video-commerce-api
.\.venv\Scripts\python.exe -m pytest -q
```

SQLite 覆盖应用契约、RBAC、事务 rollback、完整业务链和迁移往返，但不代表 MySQL 外键、锁、字符集或隔离级别已验证。

## 7. 健康检查

- `GET /health/live`：仅进程存活。
- `GET /health/ready`：轻量数据库探测，失败返回 503。
- `GET /api/health`：保留前端兼容路径并执行真实探测。

## 8. 迁移与管理员

迁移操作见 `docs/DATABASE_MIGRATIONS.md`，权限与显式管理员 CLI 见 `docs/PERMISSIONS.md`。开发和测试不得对当前真实数据库执行 Alembic 或管理员 CLI。