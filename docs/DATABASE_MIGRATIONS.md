# 数据库迁移指南

## 安全边界

应用启动不会自动运行 Alembic。`alembic/env.py` 只接受显式 `ALEMBIC_DATABASE_URL`，不会回退使用应用数据库配置。任何生产迁移都必须先备份、评审迁移脚本、在同版本副本演练并取得变更审批。

Codex Phase 2 仅在临时 SQLite 执行迁移验证，没有连接或修改用户 MySQL。SQLite 结果不能证明 MySQL 外键、锁、字符集或隔离级别行为。

## 新库初始化

在已确认的目标环境显式设置 URL 后执行：

```powershell
$env:ALEMBIC_DATABASE_URL = 'mysql+pymysql://user:password@host/database'
.\.venv\Scripts\alembic.exe upgrade head
Remove-Item Env:ALEMBIC_DATABASE_URL
```

不要把 URL 写入 `alembic.ini`、源码、命令历史、CI 日志或 Git。

## 既有库接入

`20260713_0001` 表达 Phase 1 完整 schema。对于已经由旧版应用创建且结构经核对一致的库：

1. 完整备份并验证恢复。
2. 使用 `alembic current` 确认尚未管理。
3. 对照初始迁移逐表核验列、类型、索引和外键。
4. 仅在结构一致后执行 `alembic stamp 20260713_0001`。
5. 审查 `20260713_0002` 的角色数据影响，再执行 `alembic upgrade head`。

禁止在未核对结构时直接 stamp。Phase 2 角色迁移把既有 `user` 映射为 `editor`，并把新用户数据库默认值设为 `viewer`；未知角色不会提升为管理员。

## Upgrade、Downgrade 与检查

```powershell
.\.venv\Scripts\alembic.exe current
.\.venv\Scripts\alembic.exe history
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\alembic.exe downgrade -1
```

角色 downgrade 会把 `editor` 映射回旧 `user`，无法区分原生 editor 与由旧 user 转换的 editor，因此生产 downgrade 前必须评估数据并优先采用备份恢复。

## 备份与恢复

- 迁移前记录数据库版本、应用 commit、表行数和角色分布。
- 使用数据库原生一致性备份；恢复演练必须在隔离环境完成。
- 失败时先停止写流量，再根据审批选择 Alembic downgrade 或整库恢复。
- 回滚不得恢复固定弱口令管理员、生产自动建表或自动种子。

## 隔离验证

仓库测试 `tests/integration/test_migrations.py` 在 pytest 临时目录创建 SQLite，验证 initial、旧角色数据、upgrade、downgrade 和再次 upgrade。显式 `TEST_DATABASE_URL` 的数据库名必须包含 `test/testing/ci`；测试绝不回退真实数据库。
