# 架构标准化重构计划（Phase 0）

> 分支：`refactor/architecture-standardization`  
> 基线提交：`60f385715e8858cd768f0edb33eb1a7bccc73907`  
> 审计日期：2026-07-13  
> 本阶段范围：只审计、执行基线检查并制定计划；未修改业务源码、未格式化、未删除文件、未访问或修改数据库。

## 1. Phase 0 结论

当前项目已经从简单原型演进为包含商品、内容拆解、脚本分镜、视频任务、知识库和系统设置的前后端分离应用，但演进过程留下了两套代码风格并存的状态：部分新页面已经使用 `useAsyncList`、`usePagination`、`apiResponse`、`confirm` 和 `date` 等共享能力，部分页面仍在本地实现同类逻辑；后端则仍由 Router 直接承担查询、业务校验、事务和响应组装，没有 services/repositories/dependencies 分层。

最高风险不是代码格式，而是安全与数据演进：应用启动会自动执行 `create_all()` 并创建固定弱口令管理员；全局系统设置和多数业务写接口只校验“已登录”，没有角色授权；大部分数据库写操作没有统一异常回滚；所有列表接口全量返回且前端本地分页。

Phase 0 不实施任何修复。后续应先冻结接口兼容边界和补最小回归测试，再逐层移动职责，避免“大爆炸式”重写。

## 2. 当前架构概览

### 2.1 前端

技术栈：Vue 3、Vue Router、Pinia、Axios、Element Plus、ECharts、Vite。

当前调用方向大致为：

```text
main.js
  -> router/index.js
  -> layouts/MainLayout.vue
  -> views/*.vue
       -> components/*（知识库模块已部分拆分）
       -> composables/*（部分页面使用）
       -> api/*.js
            -> utils/request.js
                 -> Axios
       -> utils/* / constants/*（使用不一致）
```

现状特点：

- Router 已采用路由懒加载。
- `request.js` 在响应拦截器中返回 `response.data`，但页面仍存在兼容完整 Axios Response 的解析代码。
- `ContentAnalysisView`、`ScriptManagementView`、`VideoManagementView` 和知识库已开始复用公共能力。
- `ProductView` 中仍保留两整段注释掉的旧脚本；活动脚本是第三段。
- 大多数路由页面仍是 1000～1700 行的单文件组件，样式、表单、查询和 CRUD 编排耦合。
- 认证数据由 Store、Router、Axios 拦截器、Layout 和个别组件直接操作 `localStorage`。

### 2.2 后端

技术栈：FastAPI、Pydantic v2、SQLAlchemy 2、PyMySQL、JWT、Argon2。

当前调用方向为：

```text
main.py
  -> app/api/*.py Router
       -> security.py / database.py
       -> models/*.py（直接查询和写入）
       -> schemas/*.py（校验与序列化）
```

当前 `app` 下只有 `api`、`models`、`schemas` 三个业务目录；`services`、`repositories`、`dependencies` 均不存在。Router 同时处理 HTTP、业务规则、ORM 查询、事务提交和响应字典组装。

## 3. 严重级别定义

| 级别 | 定义 |
|---|---|
| P0 / Critical | 可能直接造成账号失陷、越权、数据不可控变更或生产事故，进入生产前必须处理 |
| P1 / High | 明显阻碍可靠演进、测试和大数据量运行，应在架构重构前半段处理 |
| P2 / Medium | 主要影响维护成本、一致性、性能或开发体验，应随模块迁移处理 |
| P3 / Low | 清理性或样式一致性问题，可在风险更高的工作完成后处理 |

## 4. 已发现问题及对应文件

### 4.1 P0 / Critical

| 问题 | 证据位置 | 影响 |
|---|---|---|
| 启动时隐式建表并创建固定 `admin/123456` | `app/main.py:13-16`、`app/init_db.py:22-81`、`app/schemas/auth.py:22`、`app/schemas/auth.py:58` | 服务暴露后可能直接失陷；应用启动会修改数据库结构和数据 |
| 只有认证、没有写权限授权 | `app/api/products.py:18`、`content_analysis.py:16`、`scripts.py:24`、`video_tasks.py:23`、`knowledge.py:22`；`system_settings.py:45-96` | 任意已登录普通用户可修改/删除业务数据，且可修改全局系统设置 |
| 缺少数据库迁移机制 | `app/init_db.py:22-25`；仓库无 Alembic 配置 | `create_all()` 无法可靠演进列、索引、约束与数据，部署不可审计、不可回滚 |
| JWT 长期存储在 `localStorage` 且读写散落 | `stores/auth.js:5-203`、`router/index.js:8-25`、`utils/request.js:10-27`、`layouts/MainLayout.vue:129-218` | XSS 可读取令牌；兼容键和清理路径不一致会产生幽灵登录状态 |

### 4.2 P1 / High

| 问题 | 证据位置 | 影响 |
|---|---|---|
| Router 直接访问 ORM、处理业务规则和事务 | 后端全部 `app/api/*.py`；例如 `video_tasks.py:32-283`、`scripts.py:33-323` | HTTP 层过重，业务逻辑难单测、难复用，事务边界不统一 |
| 写事务错误处理不一致 | 仅 `auth.py:149-163`、`scripts.py:207-220,285-297` 显式回滚；其他 Router 直接 `commit()` | IntegrityError 或连接错误后 Session 可能处于失败状态，错误响应不稳定 |
| 所有列表均无服务端分页 | `products.py:26-42`、`content_analysis.py:37-68`、`scripts.py:93-153`、`video_tasks.py:88-161`、`knowledge.py:68-156` | 数据增长后数据库、网络、浏览器内存和渲染成本线性增长 |
| 前端采用全量列表 + 本地分页 | `composables/usePagination.js:42-69`，由商品、内容拆解、脚本、视频、知识库使用 | 前端页码不等于服务端分页；统计值和并发刷新缺少契约 |
| API 响应契约不统一 | `utils/request.js:22-23` 已解包；`utils/apiResponse.js:1-35` 再兼容；`ContentCreationView.vue:140-169`、`SystemSettingsView.vue:232-261` 重复解析 | 页面无法确定收到业务数据还是 Axios Response，兼容分支不断扩散 |
| 错误解析重复 | 公共 `utils/apiResponse.js:45-62`；页面重复于 `ContentCreationView.vue:172`、`SystemSettingsView.vue:265`；`ProductView.vue` 的两段旧脚本也各自包含实现 | 同一后端错误在不同页面提示不一致，Pydantic 错误数组处理不一致 |
| 超大页面和职责混合 | `ProductView.vue` 约 3003 物理行、`ScriptManagementView.vue` 约 1676 行、`VideoManagementView.vue` 约 1516 行、`ContentAnalysisView.vue` 约 1412 行、`SystemSettingsView.vue` 约 1249 行 | API 编排、表单、筛选、分页、展示和样式无法独立测试或复用 |
| `ProductView` 保留两整段注释旧实现 | `ProductView.vue:1-566`、`ProductView.vue:567-1181` | 搜索结果、审查和维护严重受干扰，重复代码掩盖真实活动逻辑 |
| 平台常量重复且公共常量未使用 | `constants/platforms.js:1-20` 无外部引用；重复定义于 `ContentAnalysisView.vue:179`、`ScriptManagementView.vue:211`、`VideoManagementView.vue:232`、`SystemSettingsView.vue:138` | 增删平台需同步多处，前后端允许值容易漂移 |
| 状态常量分散 | 前端各业务页面的 `statusOptions` 和 `STATUS_*_MAP`；后端 `schemas/script.py:12`、`video_task.py:11`、`knowledge.py:12`，但内容拆解仍为自由字符串 | UI、Schema、数据库默认值之间缺少单一事实来源；可写入非法状态 |
| 接口没有声明响应模型 | 后端未发现 `response_model`、`ApiResponse` 或 `PageResponse` | OpenAPI 无法完整表达统一包装结构，前端只能手写兼容解析 |
| 配置硬编码 | `utils/request.js:3-6`、`main.py:58-68`、`vite.config.js:6-16` | API Base URL、CORS 和开发工具无法按环境可靠切换 |

### 4.3 P2 / Medium

| 问题 | 证据位置 | 影响 |
|---|---|---|
| 删除确认标准化只完成一半 | 公共 `utils/confirm.js` 已被多数活动页面使用；`SystemSettingsView.vue:497` 仍直接确认恢复操作；`ProductView.vue:496,1095` 是注释旧代码 | 方向正确，但旧代码污染搜索；非删除确认应有独立通用确认能力 |
| 日期格式化标准化只完成一半 | 公共 `utils/date.js` 已被新页面使用；`ProductView.vue:230,852` 为注释旧实现；`HomeView.vue:20` 仍按旧响应读取 | 活动业务页大体统一，但遗留文件和旧代码继续造成误判 |
| 认证存储兼容键过多 | `stores/auth.js` 同时写 `access_token`、`token`、`token_type`、`user`；Router 只读前两个；Axios 只读 `access_token`；Layout 清理未删除 `token_type` | 退出或迁移时可能残留状态；依赖方向绕过 Pinia |
| API 调用写法不统一 | `api/products.js` 使用 `request({ url, method })` 且省略 `.js`；其余 API 多用 `request.get/post/...` 和 Base URL 常量 | 代码风格、默认参数和可搜索性不一致 |
| API 命名存在兼容别名和疑似死导出 | `api/auth.js:36-42`、`api/system.js:12-16`；多个 `get*DetailApi` 仅定义未调用 | 增加公共 API 面积，隐藏真实依赖 |
| 前后端重复业务校验 | 商品/拆解/脚本/视频的状态、平台、关联 ID 与字段清洗同时散落在 Vue 表单、Pydantic 和 Router | 服务端校验必须保留，但前端规则应从明确契约派生，而非人工复制 |
| 金额使用浮点数 | `models/product.py:32-35`、`schemas/product.py:22-25` | 电商金额可能出现二进制浮点精度误差 |
| 健康检查不真实 | `main.py:44-55` 固定返回数据库 running | 数据库失联时仍会报告就绪 |
| 日期时间无时区约定 | 多个 Model 使用无时区 `DateTime`；前端按浏览器本地时区解析 | 跨时区部署或用户访问时可能显示错误时间 |
| 前端包体仍偏大 | 基线构建中 `echarts` 约 1,118.32 kB、主 index JS 约 790.42 kB | 首次加载和解析成本高，Vite 发出大于 500 kB 警告 |

### 4.4 P3 / Low 与清理项

| 问题 | 证据位置 | 说明 |
|---|---|---|
| Git 跟踪 `.bak` 文件 | `backup/KnowledgeBaseView.vue.bak`、`src/api/contentAnalysis.js.bak`、`src/router/index.js.bak` | 应在后续清理阶段删除并通过 Git 历史保留版本 |
| 疑似死代码 | `stores/counter.js` 无引用；`HomeView.vue` 未注册路由；`ModulePlaceholderView.vue` 只被备份 Router 引用；多个详情 API 无调用 | 删除前仍需用运行时/产品需求确认 |
| 注释旧代码 | `MainLayout.vue:72-109`、`KnowledgeBaseView.vue:9`、备份 Router 大段注释 | 应由 Git 历史替代注释存档 |
| 空文件 | `styles/variables.css`、多个后端 `__init__.py` | 空 `__init__.py` 有包语义可保留；空样式文件需确认用途 |
| Lint 脚本默认修改源码 | `package.json:10-11` 中 Oxlint/ESLint 均带 `--fix` | CI 和审计不应运行会改文件的检查命令，应拆分 `lint` 与 `lint:fix` |

### 4.5 用户指定搜索项结果汇总

| 搜索项 | 结果 |
|---|---|
| Axios 直接导入 | 仅 `src/utils/request.js:1`；业务页面和 API 模块未直接导入 Axios |
| `response.data` | 活动代码见 `request.js:23`、`apiResponse.js:8-14`、`HomeView.vue:20`、`ContentCreationView.vue:153,166`、`SystemSettingsView.vue:241-251`；Product 中命中位于注释旧脚本 |
| `resolveListResponse` | 活动实现位于 `ContentCreationView.vue:140`；Product 命中位于注释旧脚本 |
| `getErrorMessage` | 活动实现位于 `ContentCreationView.vue:172`、`SystemSettingsView.vue:265`；共享实现名为 `getApiErrorMessage` |
| 认证 `localStorage` 操作 | Store、Router、Request、MainLayout、KnowledgeFormDialog 均有直接操作；Login 另操作 remembered account |
| `ElMessageBox.confirm` | 活动公共删除实现 `utils/confirm.js:27`；`SystemSettingsView.vue:497` 用于恢复设置；Product 两个命中均为注释旧脚本 |
| 页面内日期函数 | 活动业务页面已多用 `utils/date.js`；Product 两个本地函数命中均在注释旧脚本 |
| 页面内分页 `slice` / 页码 `watch` | 活动通用实现为 `usePagination.js:63,143`；Product 页面命中位于注释旧脚本；`ContentCreationView.vue:663` 的 `slice(0,3)` 是展示截断，不是分页 |
| 重复平台列表 | 四个活动页面重复定义，同时 `constants/platforms.js` 无引用 |
| 重复状态列表 | 内容拆解、脚本、视频各自页面与后端 Schema/Model 重复；知识库已部分集中 |
| 中文乱码 | 对受跟踪前后端文本执行常见乱码字符扫描，无命中；构建和编译也未报告编码错误 |
| `.bak` | 3 个受 Git 跟踪文件，见 4.4 |
| 大段注释旧代码 | `ProductView.vue:1-1181` 最严重；MainLayout 和 KnowledgeBase 有少量旧注释 |
| 未使用 import | 只读 ESLint 与 Oxlint 均 exit 0、无输出；未发现活动代码的静态未使用 import。死模块/死导出不属于该规则覆盖范围 |
| API 路径/函数命名不统一 | REST 路径总体一致；Products 的调用写法、认证/健康兼容别名和 detail 死导出不一致 |
| 前后端职责重复/越层 | 前端组件 `KnowledgeFormDialog.vue` 直接调用 API；后端所有 Router 直接操作 ORM 和事务；平台/状态/关联校验人工重复 |

## 5. 目标目录结构

### 5.1 前端目标

```text
ai-video-commerce-web/src/
├─ app/
│  ├─ router/
│  └─ bootstrap/
├─ layouts/
├─ views/                         # 只做路由级组合，保持薄层
├─ features/
│  ├─ auth/
│  │  ├─ api/
│  │  ├─ components/
│  │  ├─ composables/
│  │  └─ store/
│  ├─ products/
│  ├─ content-analysis/
│  ├─ scripts/
│  ├─ video-tasks/
│  ├─ knowledge/
│  └─ system-settings/
├─ shared/
│  ├─ api/                        # httpClient、统一响应/错误边界
│  ├─ components/
│  ├─ composables/                # 分页、异步状态等无业务能力
│  ├─ constants/
│  ├─ storage/                    # 唯一认证存储适配器
│  └─ utils/                      # 日期、格式化等纯函数
└─ styles/
```

迁移期不要求一次性物理搬完目录；优先建立依赖边界，再按 feature 移动。

### 5.2 后端目标

```text
ai-video-commerce-api/app/
├─ main.py
├─ core/
│  ├─ config.py
│  ├─ security.py
│  ├─ exceptions.py
│  └─ logging.py
├─ database/
│  ├─ base.py
│  ├─ session.py
│  └─ migrations/                 # Alembic 配置位于项目级亦可
├─ api/
│  ├─ router.py                   # 聚合 Router
│  └─ routers/                    # 仅 HTTP 适配
├─ dependencies/
│  ├─ auth.py
│  └─ database.py
├─ models/
├─ schemas/
│  ├─ common.py                   # ApiResponse、PageResponse、ErrorResponse
│  └─ ...
├─ repositories/                  # 只处理持久化查询
├─ services/                      # 业务规则与事务编排
└─ constants/                     # 角色、平台、状态枚举
```

## 6. 目标依赖方向

### 6.1 前端

```text
app/router -> views -> features -> shared
features/<x>/components -> features/<x>/composables -> features/<x>/api -> shared/api
features -> shared
shared -X-> features
```

约束：

- View 不直接处理 Axios Response，不直接读写认证存储。
- 展示组件不直接调用 API；由 feature composable/controller 编排。
- Feature 之间不通过深层相对路径互相读取内部文件；跨模块只使用公开入口。
- 认证存储只有一个适配器，Store、Router 和 Http Client 通过它访问。
- 状态和平台常量按业务归属定义；真正跨域的 platform 由 shared 提供。

### 6.2 后端

```text
main -> api.router -> api.routers -> services -> repositories -> database/models
api.routers -> schemas + dependencies
services -> schemas/domain constants + repositories
repositories -> models + database
models/core/database -X-> api/services
```

约束：

- Router 不写 SQLAlchemy 查询，不直接 `commit()`。
- Service 不依赖 FastAPI Request/Response/HTTPException；业务异常由全局映射转换为 HTTP。
- Repository 不组装 HTTP 响应，不包含 UI 状态文案。
- Pydantic Schema 是外部契约；ORM Model 不向上依赖 Schema。
- 事务边界由统一 Unit of Work 或 service 层约定管理。

## 7. 分阶段实施计划

### Phase 1：安全护栏、契约冻结和清理准备

目标：先建立可重构的安全网，不改变已有 API 路径和核心页面行为。

预计文件：

- 新增前后端最小测试目录和测试配置。
- 调整 `package.json`，拆分只读 `lint` 与 `lint:fix`。
- 新增 API 契约快照/冒烟测试。
- 新增 `.env.example`、环境校验和开发种子开关设计。
- 清理 `.bak`、`ProductView` 注释脚本、确定死模块清单（单独提交）。

验收：登录、五组 CRUD、系统设置的现有路径/字段/状态码有回归测试；清理提交不改变构建产物行为。

### Phase 2：前端共享基础设施标准化

目标：统一 HTTP、响应、错误、认证存储、日期、确认和分页入口。

预计文件：

- `src/utils/request.js`、`apiResponse.js`、`confirm.js`、`date.js`。
- `src/stores/auth.js`、`src/router/index.js`、`src/layouts/MainLayout.vue`。
- 新增 `src/shared/api/*`、`src/shared/storage/authStorage.js`、公共 composables。
- `src/api/*.js` 统一为同一请求写法和命名约定。

验收：业务页面不再解析多层 `response.data`；认证键只有适配器直接操作；401 只执行一次清理/导航；旧 token 可一次性迁移。

### Phase 3：前端按业务模块拆分

目标：让 View 只负责组合，表格、筛选、表单和 CRUD 编排进入 feature。

建议顺序及预计文件：

1. Products：`ProductView.vue`、`api/products.js`，新增 products components/composable/constants。
2. Content Analysis：`ContentAnalysisView.vue`、`api/contentAnalysis.js`。
3. Scripts：`ScriptManagementView.vue`、`api/scripts.js`。
4. Video Tasks：`VideoManagementView.vue`、`api/videoTasks.js`。
5. Knowledge：迁移现有 knowledge components/composable 到统一 feature 结构。
6. Settings/Auth：`SystemSettingsView.vue`、`LoginView.vue` 和相关 API/Store。

验收：路由页面脚本显著缩小；展示组件无 API import；平台和状态选项来自统一常量；页面无本地错误解析、删除确认和日期实现。

### Phase 4：后端基础设施与分层

目标：先建立公共异常、响应、依赖与事务边界，再逐模块迁移。

预计文件：

- 拆分 `config.py`、`database.py`、`security.py` 到 core/database/dependencies。
- 新增 `schemas/common.py`、全局异常处理器和 API 聚合 Router。
- 新增 `repositories/`、`services/`。
- 逐个精简 `app/api/*.py`。

模块迁移顺序建议：Products -> Content Analysis -> Scripts -> Video Tasks -> Knowledge -> System Settings -> Auth。

验收：Router 不直接导入 ORM Model 或执行 `db.commit()`；异常响应、rollback 和日志行为一致；OpenAPI 声明准确响应模型。

### Phase 5：分页、枚举和数据库演进

目标：在分层稳定后修改数据契约和数据库结构。

预计文件：

- 新增 Alembic 配置和基线迁移。
- `schemas/common.py` 增加分页契约。
- 各列表 Router/Service/Repository 和前端列表 composable。
- 平台、角色、各业务状态枚举及必要 CHECK 约束。
- Product 金额改用 Decimal/Numeric。

验收：所有列表支持服务端分页与总数；非法平台/状态被服务端拒绝；迁移可在空库和现有数据副本上前进/回退；金额序列化有测试。

### Phase 6：生产化与性能

目标：补齐 RBAC、可观测性、真实健康检查、包体优化和完整 CI。

预计文件：

- 角色依赖、权限矩阵、登录限流/审计。
- 存活/就绪端点、结构化日志和请求 ID。
- `vite.config.js`、ECharts 按需加载、Element Plus 引入策略。
- CI workflow、部署和运维文档。

验收：普通用户不能执行管理操作；就绪检查真实验证数据库；构建不再出现非预期大 chunk；CI 全量执行且无写入式检查。

## 8. 兼容策略

1. **路由兼容**：现有浏览器路径和 Router name 在迁移期间不变。
2. **API 路径兼容**：保持 `/api/auth`、`/api/products`、`/api/content-analyses`、`/api/scripts`、`/api/video-tasks`、`/api/knowledge-items`、`/api/system-settings`。
3. **响应兼容**：先在 HTTP 边界固定 `{code,message,data}`；页面不再自行兼容。引入分页时可为新参数返回分页结构，或短期提供显式 v2 端点，禁止静默改变旧调用。
4. **认证兼容**：读取旧 `token` 一次后迁移到标准键，并删除旧键；迁移窗口结束后移除别名。Cookie 方案若实施，应单独设计 CSRF 和灰度。
5. **模块迁移兼容**：旧路径文件可暂时作为 re-export，不在多个位置同时维护实现。
6. **数据库兼容**：Phase 0～4 不改变现有表结构；Phase 5 只通过审核过的迁移变更，并先在数据副本验证。
7. **用户体验兼容**：表单字段、提示文案和默认筛选在结构迁移提交中保持不变，行为变更另起提交。

## 9. 风险点

- 响应拦截器已解包 `data`，移除页面兼容逻辑时容易出现一层或两层 `data` 偏差。
- 清理 `token` 兼容键可能导致旧浏览器会话退出，需要明确一次性迁移。
- 将本地分页改为服务端分页会改变统计数据、筛选时机和刷新后的页码行为。
- 拆分大 Vue 文件时，Element Plus 表单 ref、dialog 生命周期和 scoped CSS 容易失效。
- Script/Video 的关联校验和 ScriptScene 全量替换有事务一致性风险。
- 引入 Alembic 时，现有数据库由 `create_all()` 产生，必须正确 stamp 基线，不能直接假设空库。
- 枚举/CHECK 约束上线前需清洗既有自由字符串数据。
- RBAC 会改变当前“所有登录用户均可写”的行为，需要产品确认角色矩阵。
- ECharts 拆包可能改变图表首屏时序和 ResizeObserver 行为。

## 10. 回滚方案

1. 每个 Phase 和每个 feature 使用独立小提交，禁止把目录移动、行为修改和格式化混在一个提交。
2. 纯移动先用 `git mv` 独立提交，下一提交再修改内容，以保留可审查历史。
3. 前端共享层迁移期间保留旧导出作为薄 re-export；单模块异常时可回退该模块提交。
4. 后端新 Service/Repository 逐 Router 切换；未迁移模块继续使用旧路径，避免全量切换。
5. API 行为改变使用特性开关或版本端点；回滚只切换调用，不回退数据。
6. 每个数据库迁移必须提供 downgrade，生产执行前备份并在恢复演练通过后上线。
7. 安全修复（弱口令、密钥轮换）不应通过代码回滚恢复不安全默认值；需要运维级恢复流程。

## 11. 测试方案

### 11.1 前端

- 单元测试：`apiResponse`、authStorage、日期、分页、状态映射、payload builder。
- 组件测试：筛选栏、表单 Dialog、删除确认、加载/空/错误状态。
- Store 测试：登录、注册、旧 token 迁移、损坏 user JSON、401 清理、退出。
- E2E：登录 -> 商品 -> 内容拆解 -> 脚本 -> 视频 -> 知识库 -> 系统设置；覆盖 CRUD、筛选、分页和权限拒绝。
- 每次提交执行只读 ESLint、Oxlint、单元测试和 `npm run build`。

### 11.2 后端

- Schema 单测：边界长度、枚举、金额、空白清洗、关联 ID。
- Repository 集成测试：筛选、排序、分页、总数和数据库约束。
- Service 单测：关联校验、权限、事务回滚、冲突与级联策略。
- API 测试：401/403/404/409/422/500 契约、分页包装和 OpenAPI。
- 迁移测试：空库 upgrade、现有基线 stamp + upgrade、downgrade、脏状态预检查。
- 使用独立测试数据库；禁止连接开发/生产数据库。

### 11.3 安全与非功能

- 普通用户对所有写端点的权限矩阵。
- 登录爆破限流、过期/伪造 JWT、停用用户、旧 token 迁移。
- 大数据量分页与查询计划。
- 就绪检查在数据库断开时必须失败，存活检查仍可按设计返回。
- 前端 bundle 分析和关键页面首屏性能基线。

## 12. 各阶段验收标准

| 阶段 | 验收标准 |
|---|---|
| Phase 0 | 仅新增本计划；构建/编译/lint 真实结果记录完整；Git 状态只包含计划文档 |
| Phase 1 | 安全护栏和回归测试存在；清理不改变业务行为；无 `.bak` 和整段注释旧实现 |
| Phase 2 | HTTP、响应、错误、认证存储、日期、确认、分页均有唯一公共入口 |
| Phase 3 | View 为薄组合层；组件不越层请求 API；业务常量集中；关键组件有测试 |
| Phase 4 | Router 无 ORM/commit；Service/Repository 依赖单向；统一异常与响应模型 |
| Phase 5 | Alembic 可回退；全列表服务端分页；状态/平台/金额数据契约可靠 |
| Phase 6 | RBAC、限流、审计、就绪检查、CI 和包体目标全部通过 |

## 13. 建议的 Git commit 划分

建议使用 Conventional Commits，并让每个提交可独立构建/测试：

1. `docs(refactor): add phase 0 architecture audit and plan`
2. `test(baseline): add frontend and backend smoke coverage`
3. `chore(lint): split check and fix commands`
4. `chore(cleanup): remove tracked backups and commented legacy blocks`
5. `refactor(web-auth): centralize auth storage and session cleanup`
6. `refactor(web-api): standardize http response and error boundary`
7. `refactor(web-products): move product workflow into feature module`
8. `refactor(web-content): modularize content analysis and shared constants`
9. `refactor(web-scripts): modularize scripts and scenes workflow`
10. `refactor(web-videos): modularize video task workflow`
11. `refactor(web-knowledge): align knowledge feature structure`
12. `refactor(api-core): add common responses exceptions and dependencies`
13. `refactor(api-products): add product service and repository`
14. 后续每个后端业务模块各一个 service/repository 提交。
15. `feat(api-pagination): add shared page contract and server pagination`
16. `feat(db): add alembic baseline enums and decimal money migration`
17. `feat(authz): enforce role based access control`
18. `perf(web): split echarts and optimize vendor chunks`
19. `ci: add non-mutating quality and test gates`

不要在同一个提交中同时做全仓格式化、目录移动、接口行为变化和数据库迁移。

## 14. Phase 0 实际命令与真实结果

### 14.1 Git 与文件扫描

执行：

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
git status --branch --short
git ls-files
Get-ChildItem -Path . -Filter AGENTS.md -Recurse -Force
```

结果：

- 分支：`refactor/architecture-standardization`。
- HEAD：`60f385715e8858cd768f0edb33eb1a7bccc73907`。
- 审计开始时工作区 clean。
- 未发现 `AGENTS.md`。
- 逐文件读取了 package/Vite/Router/Store/API/View/Component/Composable/Utils，以及后端 main/config/database/security/init_db/全部 Router/Model/Schema。
- 后端不存在 services、repositories、dependencies 目录；审计前不存在 docs 目录。

### 14.2 指定模式搜索

使用 `rg -n -S` 对 `ai-video-commerce-web/src`、`backup` 和 `ai-video-commerce-api/app` 执行了以下模式搜索：

```text
axios
response.data
resolveListResponse
getErrorMessage
localStorage.getItem/setItem/removeItem
ElMessageBox.confirm
formatDate / formatDateTime
.slice( / watch(
platformOptions / PLATFORM_OPTIONS
statusOptions / STATUS_OPTIONS
常见中文乱码字符
注释代码块、TODO/FIXME/旧代码
前端 API export/path
后端 Router/path/ORM/commit/rollback/response_model/pagination
```

结果已汇总在第 4.5 节；中文乱码扫描无命中，跟踪到 3 个 `.bak` 文件。

### 14.3 前端构建

执行：

```powershell
cd ai-video-commerce-web
npm run build
```

真实结果：**exit 0，通过**。Vite 8.1.4 转换 2284 个模块。主要产物：

- `echarts-*.js`：1,118.32 kB，gzip 370.94 kB。
- `index-*.js`：790.42 kB，gzip 250.99 kB。
- `index-*.css`：361.87 kB，gzip 49.12 kB。
- Vite 警告部分 chunk 大于 500 kB。

### 14.4 后端编译

首先按要求执行：

```powershell
cd ai-video-commerce-api
python -m compileall app
```

真实结果：**exit 1，失败且无标准输出**。`Get-Command python` 显示系统命令指向 `C:\Users\kongl\AppData\Local\Microsoft\WindowsApps\python.exe`，不是项目虚拟环境解释器。

随后使用仓库已有虚拟环境执行同一检查（没有安装或升级依赖）：

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m compileall app
```

真实结果：**exit 0，通过**；项目虚拟环境 Python 为 3.14.6，输出列出了 `app`、`app\api`、`app\models`、`app\schemas`，未报告语法错误。

### 14.5 Lint 与测试

现有 `npm run lint` 会调用两个带 `--fix` 的脚本，违反 Phase 0“不批量格式化/不修改源码”的约束，因此没有执行该写入式脚本；改为执行等价只读检查：

```powershell
.\node_modules\.bin\eslint.cmd .
.\node_modules\.bin\oxlint.cmd .
```

真实结果：两条命令均 **exit 0、无错误输出**。

仓库未发现 pytest 配置、pytest 依赖、测试目录或测试文件，也未发现后端 lint/type-check 配置，因此没有执行 pytest 或后端 lint。没有声称这些未执行检查通过。

## 15. Phase 0 停止点

本文件是 Phase 0 唯一计划内变更。完成本文件复核和最终 Git 状态记录后停止，不进入 Phase 1。
