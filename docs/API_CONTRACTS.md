# API 契约

## 成功响应

所有现有业务接口继续返回：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {}
}
```

创建接口 HTTP status 与 `code` 为 201。删除接口 `data` 为 `null`。全部列表接口的 `data` 继续是数组，不引入分页对象。前端唯一 Axios 实例在成功时返回业务 `data`，页面不得读取 `response.data` 或 `response.data.data`。

## 路径与 Method

| 资源 | 路径 | Method |
|---|---|---|
| 认证 | `/api/auth/login`、`/register`、`/me` | POST、POST、GET |
| 商品 | `/api/products`、`/{id}` | GET、POST、PUT、DELETE |
| 内容拆解 | `/api/content-analyses`、`/{id}` | GET、POST、PUT、DELETE |
| 脚本/分镜 | `/api/scripts`、`/{id}` | GET、POST、PUT、DELETE |
| 视频任务 | `/api/video-tasks`、`/{id}` | GET、POST、PUT、DELETE |
| 知识库 | `/api/knowledge-items`、`/{id}`、`/{id}/use` | GET、POST、PUT、DELETE |
| 系统设置 | `/api/system-settings` | GET、PUT |
| 健康 | `/api/health`、`/health/live`、`/health/ready` | GET |

现有请求字段保持不变。金额仍为 Float、列表仍为全量返回，服务端分页和 Decimal 不属于 Phase 2。

## 错误语义

领域错误保持 FastAPI 兼容结构：

```json
{"detail": "错误说明"}
```

| HTTP | 语义 |
|---:|---|
| 401 | 缺少/无效 Token、用户不存在或已停用；前端清理会话并跳转登录 |
| 403 | 身份有效但权限不足；前端显示“当前账号无权限执行此操作”，不清理会话 |
| 404 | 资源或关联资源不存在 |
| 409 | 用户名、唯一约束或持久化冲突 |
| 422 | Pydantic 字段错误、非法关联组合或非法状态转换 |
| 500 | 未处理异常，对外仅返回通用信息 |
| 503 | readiness 数据库探测失败，不泄露连接信息 |

## OpenAPI

业务 Router 使用泛型 `ApiResponse[T]` 声明 `response_model`。`ErrorResponse` 声明安全错误形状。Schema 是外部契约，Router 不直接序列化 ORM 细节或返回密码字段。
