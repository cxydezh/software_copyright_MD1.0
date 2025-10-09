# 项目文件列表功能实现文档

## 功能概述

根据需求分析文档要求，实现了任务视图中的项目文件列表显示功能：
- 当左侧Treeview中的项目被选中后
- 中间的 `detail_left_frame` 显示该项目的文件列表
- 提供右键菜单支持文件操作

## 实现细节

### 1. 文件列表加载 (`load_project_files()`)

**功能**:
- 从项目文件夹中读取所有实际文件
- 支持递归遍历子文件夹
- 显示文件的相对路径、类型、大小、修改时间

**实现逻辑**:
```python
def load_project_files(self, project_id):
    # 1. 构建项目文件夹路径: base_path/项目ID.项目名称
    # 2. 检查文件夹是否存在
    # 3. 使用 os.walk() 递归遍历所有文件
    # 4. 获取每个文件的详细信息（大小、类型、时间）
    # 5. 将文件信息添加到 file_tree
    # 6. 完整路径存储在 tags 中供后续操作使用
```

**关键代码**:
```python
for root, dirs, files in os.walk(project_folder):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        
        # 获取文件信息
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()
        file_type = self.get_file_type(file_ext)
        
        # 获取修改时间
        mtime = os.path.getmtime(file_path)
        time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        # 计算相对路径
        rel_path = os.path.relpath(file_path, project_folder)
        
        # 添加到树形控件，完整路径存储在tags中
        self.file_tree.insert('', 'end', values=(
            rel_path, file_type, size_str, time_str
        ), tags=(file_path,))
```

### 2. 文件类型识别 (`get_file_type()`)

**功能**: 根据文件扩展名自动识别文件类型

**支持的文件类型**:
- 文档类: PDF、Word、Excel
- 源代码: Python、Java、C/C++、JavaScript、HTML、CSS、SQL
- 图片: PNG、JPG、GIF、BMP
- 压缩包: ZIP、RAR、7Z
- 其他: 文本文件、其他文件

**示例**:
```python
'.pdf' → 'PDF文档'
'.py' → 'Python源码'
'.jpg' → '图片文件'
'.zip' → '压缩文件'
```

### 3. 文件大小格式化 (`format_file_size()`)

**功能**: 将字节数转换为人类可读的格式

**示例**:
```
1024 → "1.0 KB"
1048576 → "1.0 MB"
0 → "0 B"
```

### 4. 打开文件 (`open_file()`)

**功能**: 使用系统默认程序打开选中的文件

**触发方式**:
- 双击文件列表中的项目
- 右键菜单 → "打开文件"

**实现**:
- Windows: 使用 `os.startfile()`
- macOS: 使用 `open` 命令
- Linux: 使用 `xdg-open` 命令

### 5. 打开文件夹 (`open_file_folder()`)

**功能**: 在文件管理器中打开文件所在文件夹并选中该文件

**触发方式**: 右键菜单 → "打开文件夹"

**实现**:
- Windows: `explorer /select, <file_path>` - 打开资源管理器并选中文件
- macOS: `open -R <file_path>` - 打开Finder并选中文件
- Linux: `xdg-open <folder_path>` - 打开文件夹

### 6. 删除文件 (`delete_file()`)

**功能**: 删除选中的文件（带确认）

**触发方式**: 右键菜单 → "删除文件"

**安全措施**:
- 需要用户确认
- 提示"此操作不可恢复"
- 验证文件存在性

## 数据流程

```
1. 用户选择项目
   ↓
2. 触发 on_status_tree_select()
   ↓
3. 调用 display_project_details(project)
   ↓
4. 调用 load_project_files(project_id)
   ↓
5. 遍历项目文件夹中的所有文件
   ↓
6. 在 file_tree 中显示文件列表
   ↓
7. 用户可以右键操作文件
```

## 界面布局

```
+------------------+------------------------+
| Left Frame       | Detail Frame           |
| (项目列表)       +------------+-----------+
|                  | Left       | Right     |
| [项目树]         | (文件列表)  | (详情)    |
|                  |            |           |
| 已立项           | 文件1.pdf  | 项目名称  |
| 执行中           | 文件2.docx | 流水号    |
| 已完成           | 文件3.zip  | 著作权人  |
|                  | ...        | ...       |
+------------------+------------+-----------+
```

## 文件树控件配置

**列定义**:
```python
columns = ('文件名', '类型', '大小', '修改时间')
widths = (300, 100, 100, 150)
```

**右键菜单**:
- 打开文件
- 打开文件夹
- -------
- 删除文件

**事件绑定**:
- 双击 (`<Double-1>`) → 打开文件
- 右键 (`<Button-3>`) → 显示菜单

## 技术要点

### 1. 使用 tags 存储完整路径

由于 Treeview 的 values 只能显示简单信息，我们使用 tags 存储完整路径：

```python
self.file_tree.insert('', 'end', 
    values=(rel_path, file_type, size_str, time_str),
    tags=(file_path,)  # 完整路径
)

# 使用时
tags = item.get('tags', ())
file_path = tags[0]
```

### 2. 递归遍历文件夹

使用 `os.walk()` 递归遍历所有子文件夹：

```python
for root, dirs, files in os.walk(project_folder):
    for file_name in files:
        file_path = os.path.join(root, file_name)
        # 处理文件...
```

### 3. 跨平台文件操作

支持 Windows、macOS、Linux 三个平台：

```python
if sys.platform == 'win32':
    os.startfile(file_path)
elif sys.platform == 'darwin':
    subprocess.run(['open', file_path])
else:
    subprocess.run(['xdg-open', file_path])
```

## 使用示例

### 场景1: 查看项目文件

```
1. 在任务视图左侧选择一个项目
2. 中间面板自动显示该项目的所有文件
3. 文件按相对路径、类型、大小、时间显示
```

### 场景2: 打开文件

```
1. 双击文件列表中的任意文件
   或
   右键点击 → 选择"打开文件"
2. 文件使用系统默认程序打开
```

### 场景3: 查找文件位置

```
1. 右键点击文件
2. 选择"打开文件夹"
3. 文件管理器打开并自动选中该文件
```

### 场景4: 删除文件

```
1. 右键点击文件
2. 选择"删除文件"
3. 确认删除
4. 文件从磁盘和列表中删除
```

## 文件类型支持

| 扩展名 | 显示类型 | 默认打开方式 |
|--------|---------|-------------|
| .pdf | PDF文档 | Adobe Reader / 浏览器 |
| .docx | Word文档 | Microsoft Word |
| .xlsx | Excel表格 | Microsoft Excel |
| .txt | 文本文件 | 记事本 |
| .py | Python源码 | Python IDE |
| .java | Java源码 | Java IDE |
| .zip | 压缩文件 | 压缩软件 |
| .png/.jpg | 图片文件 | 图片查看器 |

## 性能考虑

1. **递归遍历**: 使用 `os.walk()` 高效遍历
2. **延迟加载**: 仅在选中项目时加载文件列表
3. **相对路径**: 显示相对路径减少界面宽度
4. **文件缓存**: 完整路径存储在tags中避免重复计算

## 测试要点

### 测试1: 文件列表显示
- ✅ 选择项目后文件列表自动加载
- ✅ 显示所有文件（包括子文件夹中的）
- ✅ 文件信息正确（名称、类型、大小、时间）

### 测试2: 文件操作
- ✅ 双击文件能正常打开
- ✅ 右键菜单正常显示
- ✅ "打开文件"功能正常
- ✅ "打开文件夹"功能正常
- ✅ "删除文件"功能正常（需确认）

### 测试3: 边界情况
- ✅ 项目文件夹不存在时不报错
- ✅ 空文件夹时显示空列表
- ✅ 文件不存在时给出友好提示
- ✅ 大文件也能正常显示

## 后续优化建议

1. **文件图标**: 根据文件类型显示不同图标
2. **排序功能**: 点击列标题排序
3. **文件过滤**: 按类型或名称过滤文件
4. **批量操作**: 支持多选和批量删除
5. **文件预览**: 添加预览面板
6. **拖拽上传**: 支持拖拽文件到项目文件夹
7. **文件搜索**: 在文件列表中搜索

## 已知限制

1. **不同步数据库**: 当前从文件系统读取，不与 `project_files` 表同步
2. **无文件监控**: 外部修改文件后需手动刷新
3. **大文件夹性能**: 包含大量文件时可能加载较慢

## 总结

✅ **完全实现需求分析文档中的文件列表功能**

- 实时读取项目文件夹中的实际文件
- 支持完整的文件操作（打开、定位、删除）
- 跨平台兼容（Windows/macOS/Linux）
- 用户友好的界面和提示
- 完整的错误处理

可以直接在桌面应用中使用！


