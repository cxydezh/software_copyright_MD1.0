# 项目归档功能使用指南

## 功能概述

根据需求文档更新，系统新增了项目归档功能，包括：

1. **归档项目表**：软著、论文、专利的归档项目表
2. **数据迁移**：项目归档时自动从活动表迁移到归档表
3. **Web查询**：普通业务员可以查询和检索所有项目（包括未归档和已归档）

## 数据库表结构

### 1. 软著归档项目表 (archived_software_projects)

当软著项目归档时，记录从 `projects` 表迁移到此表。

**主要字段：**
- `id`: 项目ID（保留原ID）
- `project_name`: 项目名称
- `project_type`: 项目类型
- `copyright_owner`: 著作权人
- `serial_number`: 流水号
- `archive_time`: 归档日期
- `is_settled`: 是否已结清
- 其他时间、财务、外键字段

### 2. 论文归档项目表 (archived_paper_projects)

当论文项目归档时，记录从 `paper_projects` 表迁移到此表。

**主要字段：**
- `id`: 项目ID
- `project_name`: 项目名称
- `paper_title`: 论文标题
- `target_journal`: 目标期刊
- `archive_time`: 归档日期
- 其他论文相关字段

### 3. 专利归档项目表 (archived_patent_projects)

当专利项目归档时，记录从 `patent_projects` 表迁移到此表。

**主要字段：**
- `id`: 项目ID
- `project_name`: 项目名称
- `invention_title`: 发明名称
- `patent_number`: 专利号
- `archive_time`: 归档日期
- 其他专利相关字段

## 归档流程

### 归档条件

项目归档需要满足以下条件：
1. **必须已结算**：`is_settled = True`
2. **未归档**：`is_archived = False`

### 归档过程

1. **检查条件**：验证项目是否已结算
2. **创建归档记录**：在对应的归档表中创建记录
3. **记录流程日志**：在 `process_logs` 表中记录归档操作
4. **删除原记录**：从活动项目表中删除
5. **提交事务**：确保数据一致性

## API接口

### 1. 获取所有项目（未归档）

```http
GET /api/query/projects?type={type}&status={status}&page={page}&per_page={per_page}
```

**参数：**
- `type`: 项目类型 (all, software, paper, patent)
- `status`: 项目状态 (all, 待确认, 已确认, 等)
- `page`: 页码（默认1）
- `per_page`: 每页数量（默认20）

**响应：**
```json
{
  "success": true,
  "data": {
    "software": [...],
    "paper": [...],
    "patent": [...]
  },
  "message": "获取项目列表成功"
}
```

### 2. 获取归档项目

```http
GET /api/query/archived?type={type}&page={page}&per_page={per_page}
```

**参数：**
- `type`: 项目类型 (all, software, paper, patent)
- `page`: 页码
- `per_page`: 每页数量

**响应：**
```json
{
  "success": true,
  "data": {
    "software": [...],
    "paper": [...],
    "patent": [...]
  },
  "message": "获取归档项目成功"
}
```

### 3. 搜索项目

```http
GET /api/query/search?keyword={keyword}&type={type}&include_archived={true/false}
```

**参数：**
- `keyword`: 搜索关键词
- `type`: 项目类型
- `include_archived`: 是否包含归档项目

**响应：**
```json
{
  "success": true,
  "data": {
    "active": {
      "software": [...],
      "paper": [...],
      "patent": [...]
    },
    "archived": {
      "software": [...],
      "paper": [...],
      "patent": [...]
    }
  },
  "message": "搜索完成"
}
```

### 4. 归档项目

```http
POST /api/query/archive/{project_type}/{project_id}
```

**参数：**
- `project_type`: 项目类型 (software, paper, patent)
- `project_id`: 项目ID

**响应：**
```json
{
  "success": true,
  "message": "软著项目归档成功"
}
```

## Web界面

### 访问路径

普通业务员和项目执行者登录后，可以访问：

```
http://your-server:5000/staff/project_query
```

### 功能说明

1. **搜索栏**：
   - 输入关键词搜索
   - 选择项目类型过滤
   - 可选择是否包含归档项目

2. **未归档项目Tab**：
   - 显示所有活动项目
   - 按项目类型分组展示
   - 可按状态筛选
   - 已结算项目可直接归档

3. **已归档项目Tab**：
   - 显示所有归档项目
   - 按项目类型分组展示
   - 只读查看

## 安装步骤

### 1. 创建归档表

```bash
python create_archive_tables.py
```

### 2. 测试功能

```bash
# 启动Web服务器
python run_web.py

# 在另一个终端运行测试
python test_archive_functions.py
```

## 使用示例

### Python代码示例

```python
from web_app.services.archive_service import ArchiveService

# 归档软著项目
success, message = ArchiveService.archive_software_project(project_id=123)
if success:
    print(message)
else:
    print(f"归档失败: {message}")

# 获取归档项目
archived_data = ArchiveService.get_archived_projects('software')
print(f"软著归档项目数量: {len(archived_data['software'])}")

# 搜索归档项目
results = ArchiveService.search_archived_projects("关键词", 'all')
```

### JavaScript示例

```javascript
// 归档项目
function archiveProject(type, id) {
    fetch(`/api/query/archive/${type}/${id}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            // 刷新列表
            loadProjects();
        } else {
            alert('归档失败: ' + data.message);
        }
    });
}

// 搜索项目
function searchProjects(keyword) {
    fetch(`/api/query/search?keyword=${keyword}&type=all&include_archived=true`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displaySearchResults(data.data);
        }
    });
}
```

## 注意事项

1. **数据备份**：归档操作会删除原表记录，建议定期备份数据库

2. **权限控制**：只有登录的员工才能执行归档操作

3. **归档条件**：必须确保项目已结算后才能归档

4. **事务安全**：归档过程使用数据库事务，确保数据一致性

5. **日志记录**：所有归档操作都会在 `process_logs` 表中记录

## 故障排查

### 问题1：归档失败 - "项目尚未结算"

**解决方案**：
```python
# 先标记项目为已结算
project.is_settled = True
project.settle_time = datetime.utcnow()
db.session.commit()
```

### 问题2：无法访问查询页面

**解决方案**：
- 确认已登录
- 确认用户类型为 staff
- 检查路由是否正确注册

### 问题3：搜索结果为空

**解决方案**：
- 检查关键词是否正确
- 确认数据库中有匹配的记录
- 查看API响应日志

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    Web Interface                        │
│              (staff/project_query.html)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    API Layer                            │
│              (api_query.py blueprint)                   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 Service Layer                           │
│             (ArchiveService class)                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 Database Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   projects   │  │paper_projects│  │patent_projects│  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬────────┘  │
│         │                 │                  │           │
│         ▼                 ▼                  ▼           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │archived_soft │  │archived_paper│  │archived_patent│  │
│  │ware_projects │  │  _projects   │  │  _projects    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 更新日志

### v2.0 - 2024年（当前版本）

- ✅ 创建归档项目表（软著、论文、专利）
- ✅ 实现项目归档服务
- ✅ 实现Web查询API
- ✅ 创建查询界面
- ✅ 添加搜索功能

## 相关文件

- `database/models.py` - 数据库模型定义
- `web_app/services/archive_service.py` - 归档服务
- `web_app/views/api_query.py` - 查询API
- `web_app/views/staff.py` - 员工视图
- `templates/staff/project_query.html` - 查询页面
- `create_archive_tables.py` - 创建归档表脚本
- `test_archive_functions.py` - 测试脚本

