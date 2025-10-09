# 项目归档功能说明

## 功能概述

根据需求文档更新，系统已完成以下功能：

### 1. 归档项目表
- ✅ **archived_software_projects** - 软著归档项目表
- ✅ **archived_paper_projects** - 论文归档项目表
- ✅ **archived_patent_projects** - 专利归档项目表

### 2. 归档逻辑
- ✅ 项目归档时自动从原表迁移到归档表
- ✅ 保留完整项目信息和归档时间
- ✅ 记录归档操作流程日志

### 3. Web查询功能
- ✅ 普通业务员可查询未归档项目
- ✅ 普通业务员可查询已归档项目
- ✅ 支持关键词搜索（项目名称、著作权人、流水号等）
- ✅ 支持按项目类型和状态筛选

## 快速开始

### 访问查询页面

员工登录后访问：
```
http://your-server:5000/staff/project_query
```

### API端点

1. **获取未归档项目**
   ```
   GET /api/query/projects?type=all&status=all
   ```

2. **获取归档项目**
   ```
   GET /api/query/archived?type=all
   ```

3. **搜索项目**
   ```
   GET /api/query/search?keyword=关键词&type=all&include_archived=true
   ```

4. **归档项目**
   ```
   POST /api/query/archive/{project_type}/{project_id}
   ```

## 归档条件

项目必须满足以下条件才能归档：
1. 已结算（is_settled = True）
2. 未归档（is_archived = False）

## 数据迁移流程

1. 验证归档条件
2. 在归档表创建记录
3. 记录流程日志
4. 删除原表记录
5. 提交事务

## 测试结果

归档功能已测试通过：
- ✅ 创建归档表成功
- ✅ 数据迁移成功
- ✅ 原表记录正确删除
- ✅ 搜索功能正常
- ✅ 查询API正常

## 相关文件

- `database/models.py` - 归档表模型
- `web_app/services/archive_service.py` - 归档服务
- `web_app/views/api_query.py` - 查询API
- `web_app/views/staff.py` - 员工视图
- `templates/staff/project_query.html` - 查询界面

## 技术栈

- Flask 2.x
- SQLAlchemy 2.x
- MySQL 8.0
- Bootstrap 5
- JavaScript (ES6+)

## 注意事项

1. 归档操作不可逆，请确保数据已备份
2. 归档前必须完成项目结算
3. 归档后原项目记录将被删除
4. 所有操作都有流程日志记录

