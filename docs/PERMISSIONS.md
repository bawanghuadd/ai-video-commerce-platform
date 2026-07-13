# 权限与管理员操作

## 角色矩阵

| 能力 | admin | editor | viewer |
|---|---:|---:|---:|
| 业务读取 | 是 | 是 | 是 |
| 商品/拆解/脚本/视频/知识库写入 | 是 | 是 | 否 |
| 知识引用计数 | 是 | 是 | 否 |
| 系统设置读取 | 是 | 是 | 是 |
| 系统设置写入 | 是 | 否 | 否 |
| 管理用户/角色 | 是 | 否 | 否 |

服务端 `dependencies/permissions.py` 是权威授权点。JWT 角色 claim 不作为授权依据；每个请求重新查询数据库用户和 `is_active/role`，因此伪造 admin claim 不能把 viewer 提升为管理员。

兼容映射：既有 `user` 按 editor 授权以保持原业务能力；迁移将其更新为 editor。新注册用户是 viewer。未知角色采用最小权限并拒绝访问，不会自动变为 admin。

## 前端

`src/utils/permissions.js` 是唯一权限矩阵，Auth Store 暴露 `canRead/canCreate/canUpdate/canDelete/canManageSettings/canManageUsers`。页面和知识库组件不散落角色字符串。按钮隐藏/禁用只改善体验，不能替代服务端检查。403 不清理认证存储，401 才清理并跳转。

## 创建管理员

管理员操作是显式 CLI，不在应用启动时执行，不包含默认账号或密码：

```powershell
cd ai-video-commerce-api
$env:ADMIN_PASSWORD = '<至少12位的高熵临时密码>'
.\.venv\Scripts\python.exe -m app.cli.admin create secure_admin --display-name '安全管理员'
Remove-Item Env:ADMIN_PASSWORD
```

晋升既有用户：

```powershell
.\.venv\Scripts\python.exe -m app.cli.admin promote existing_username
```

在生产执行前必须确认目标数据库、操作人、审批和审计要求。Codex Phase 2 没有运行这些命令，也没有修改真实用户。
