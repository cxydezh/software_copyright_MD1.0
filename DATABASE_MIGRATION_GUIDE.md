# 本地数据库迁移指南

## 问题说明

当你修改了 `desktop_app/local_models.py` 中的表结构代码后，重新运行程序时数据库不会自动更新。

**原因：** SQLite 使用 `CREATE TABLE IF NOT EXISTS` 语句创建表，如果表已经存在，即使你修改了代码，也不会重新创建或修改现有的表结构。

## 解决方案

### 方法1：使用迁移脚本（推荐，保留数据）

运行迁移脚本来更新表结构，同时保留现有数据：

```bash
python quick_migrate_local_db.py
```

这个脚本会：
- 自动备份现有数据库（备份文件名包含时间戳）
- 检查并添加缺失的列
- 保留所有现有数据
- 如果失败会自动恢复备份

### 方法2：手动删除数据库文件（会丢失数据）

如果你不需要保留现有数据，可以直接删除数据库文件：

1. 找到数据库文件位置：`D:/SoftwareCopyrightMS/Database/local.db`
2. 删除该文件
3. 重新运行桌面程序，会自动创建新的数据库

### 方法3：使用交互式迁移工具

运行交互式迁移工具，选择迁移方式：

```bash
python desktop_app/migrate_local_db.py
```

然后按提示选择：
- `1` - 迁移数据库（保留数据，仅更新表结构）
- `2` - 重新创建数据库（删除所有数据）
- `0` - 退出

## 迁移记录

### 2025-10-08 更新

已添加以下列到各表：

- `default_paths` 表：添加 `recurrent_copy_time` 列
- `id_card_files` 表：添加 `recurrent_copy_time` 列
- `usccc_files` 表：添加 `recurrent_copy_time` 列
- `contract_files` 表：添加 `recurrent_copy_time` 列
- `template_folders` 表：添加 `recurrent_copy_time` 列
- `project_files` 表：添加 `file_size` 和 `recurrent_copy_time` 列
- `local_projects` 表：添加 `recurrent_copy_time` 列

数据库备份位置：`D:/SoftwareCopyrightMS/Database/local.db.backup_[timestamp]`

## 注意事项

1. **迁移前会自动备份**：所有迁移操作都会先创建数据库备份
2. **备份文件命名**：`local.db.backup_YYYYMMDD_HHMMSS`
3. **失败自动恢复**：如果迁移失败，会自动从备份恢复
4. **定期清理备份**：建议定期清理旧的备份文件以节省空间

## 开发建议

当你需要修改数据库表结构时：

1. **先备份**：运行迁移脚本会自动备份
2. **使用 ALTER TABLE**：在迁移脚本中添加相应的 ALTER TABLE 语句
3. **测试迁移**：先在测试环境验证迁移脚本
4. **记录变更**：在本文档中记录所有数据库变更

