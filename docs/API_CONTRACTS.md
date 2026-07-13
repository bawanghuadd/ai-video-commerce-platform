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

## 认证响应

登录和注册成功的 `data` 均为：

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "example_user",
    "display_name": "示例用户",
    "role": "viewer",
    "is_active": true
  }
}
```

`GET /api/auth/me` 的 `data` 直接是上述 `user` 对象。新注册用户固定为
`viewer`；注册响应会同时返回 Token，前端可直接建立登录会话。响应不包含密码或密码哈希。

## 错误语义

领域错误保持 FastAPI 兼容结构：

```json
{"detail": "错误说明"}
```

| HTTP | 语义 |
|---:|---|
| 401 | 受保护请求缺少/使用无效 Token，或 Token 对应用户不存在/已停用；前端清理会话并跳转登录 |
| 403 | 身份有效但权限不足；停用账号主动登录也返回 403；前端显示权限错误且不清理已有有效会话 |
| 404 | 资源或关联资源不存在 |
| 409 | 用户名、唯一约束或持久化冲突 |
| 422 | Pydantic 字段错误、非法关联组合或非法状态转换 |
| 500 | 未处理异常，对外仅返回通用信息 |
| 503 | readiness 数据库探测失败，不泄露连接信息 |

## OpenAPI

业务 Router 使用泛型 `ApiResponse[T]` 声明 `response_model`。`ErrorResponse` 声明安全错误形状。Schema 是外部契约，Router 不直接序列化 ORM 细节或返回密码字段。
