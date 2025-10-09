# 快速参考卡片

## 🚀 快速开始

```bash
# 1. 数据库迁移（首次必须）
python quick_migrate_local_db.py

# 2. 启动应用
python run_desktop.py
```

## 📋 新功能一览

### 选择对话框（4个）

| 功能 | 触发按钮 | 对话框 |
|------|---------|--------|
| 选择模板 | 创建项目文件夹 | `TemplateSelectionDialog` |
| 选择身份证 | 身份证复印件 | `IDCardFileDialog` |
| 选择证书 | 统一社会信用代码证书 | `USCCCFileDialog` |
| 选择合同 | 合同 | `ContractFileDialog` |

### 项目文件列表

| 操作 | 方式 | 功能 |
|------|------|------|
| 查看文件 | 选择项目 | 自动显示文件列表 |
| 打开文件 | 双击 / 右键 | 系统默认程序打开 |
| 定位文件 | 右键→打开文件夹 | 文件管理器中定位 |
| 删除文件 | 右键→删除文件 | 从磁盘删除 |

## 🔧 常用命令

```bash
# 测试
python test_selection_dialogs.py      # 测试对话框
python test_file_list.py               # 测试文件列表
python test_recurrent_copy_time.py     # 测试字段更新

# 验证
python verify_fix.py                   # 快速验证修复

# 创建测试数据
python create_test_project_files.py    # 创建测试项目文件
```

## 📁 关键文件路径

| 用途 | 路径 |
|------|------|
| 本地数据库 | `D:/SoftwareCopyrightMS/Database/local.db` |
| 项目文件夹 | `D:/SoftwareCopyrightMS/ProjectFile/` |
| 模板文件夹 | `D:/SoftwareCopyrightMS/模板/` |
| 身份证文件 | `D:/SoftwareCopyrightMS/身份证复印件/` |
| 证书文件 | `D:/SoftwareCopyrightMS/统一社会信用代码证书/` |
| 合同文件 | `D:/SoftwareCopyrightMS/合同/` |

## 🎯 主要改进

1. ✅ 4个选择对话框全部实现
2. ✅ 文件列表从文件系统实时读取
3. ✅ 完整的文件操作功能
4. ✅ recurrent_copy_time字段正确更新
5. ✅ 跨平台兼容（Win/Mac/Linux）

## 📚 文档快速导航

- **快速入门**: `README_SELECTION_DIALOGS.md`
- **使用指南**: `TASK_VIEW_FILE_LIST_GUIDE.md`
- **完整总结**: `COMPLETE_IMPLEMENTATION_SUMMARY.md`
- **修复报告**: `RECURRENT_COPY_TIME_FIX.md`

## ⚠️ 注意事项

1. **首次使用必须迁移数据库**
2. **删除文件操作不可恢复**
3. **确保项目文件夹路径正确配置**
4. **建议定期备份项目文件**

## 🆘 故障排除

| 问题 | 解决方法 |
|------|---------|
| 数据库字段不存在 | `python quick_migrate_local_db.py` |
| 文件列表为空 | 检查项目文件夹是否存在 |
| 文件打不开 | 检查文件是否存在、安装相应程序 |
| 路由错误 | 已修复，重启Web服务器 |

---

**快速访问**: 保存此文件到收藏夹，随时查阅！


