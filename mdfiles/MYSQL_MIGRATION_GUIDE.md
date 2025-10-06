# MySQL数据库迁移完整指南

## 📋 迁移概述

本指南将帮助您将软件版权管理系统从SQLite数据库迁移到MySQL数据库。

### 🔧 系统要求
- MySQL 5.7+ 或 MySQL 8.0+
- Python 3.8+
- 已安装的依赖包（PyMySQL等）

### 📊 迁移步骤概览
1. ✅ 修改配置文件支持MySQL
2. ✅ 创建环境变量配置
3. ✅ 创建MySQL数据库和用户
4. ✅ 初始化数据库表结构
5. ✅ 迁移SQLite数据到MySQL
6. ✅ 测试MySQL连接和功能

## 🚀 快速开始

### 步骤1：设置环境变量

**Windows系统：**
```cmd
set DB_PASSWORD=your_mysql_password_here
```

**Linux/Mac系统：**
```bash
export DB_PASSWORD=your_mysql_password_here
```

### 步骤2：创建MySQL数据库和用户

```bash
python setup_mysql.py
```

这个脚本会：
- 创建 `software_copyright` 数据库
- 创建 `webuser` 用户
- 设置适当的权限

### 步骤3：初始化MySQL数据库

```bash
python init_mysql.py
```

这个脚本会：
- 创建所有必要的数据库表
- 创建示例数据（管理员、业务员、执行者账户）

### 步骤4：迁移SQLite数据（可选）

如果您有现有的SQLite数据需要迁移：

```bash
python migrate_data.py
```

### 步骤5：测试MySQL连接

```bash
python test_mysql.py
```

### 步骤6：启动Web应用

```bash
python run_web.py
```

## 📁 文件说明

### 配置文件
- `config/config.py` - 数据库连接配置
- `env_example.txt` - 环境变量示例

### 脚本文件
- `setup_mysql.py` - MySQL数据库和用户创建
- `init_mysql.py` - 数据库表结构初始化
- `migrate_data.py` - SQLite到MySQL数据迁移
- `test_mysql.py` - MySQL连接和功能测试

## 🔧 详细配置

### 数据库连接字符串

**开发环境：**
```python
mysql+pymysql://webuser:password@127.0.0.1:3306/software_copyright
```

**生产环境：**
```python
mysql+pymysql://webuser:password@127.0.0.1:3306/software_copyright
```

### 环境变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `DB_PASSWORD` | MySQL用户密码 | `your_password_here` |
| `DEV_DATABASE_URL` | 开发环境数据库URL | `mysql+pymysql://webuser:password@127.0.0.1:3306/software_copyright` |
| `SECRET_KEY` | Flask密钥 | `your-secret-key-here` |

## 🗄️ 数据库结构

### 表结构
- `staff` - 员工表
- `user` - 用户表
- `project` - 项目表
- `message` - 消息表
- `permissions` - 权限表

### 字符集
- 数据库：`utf8mb4`
- 排序规则：`utf8mb4_unicode_ci`

## 🔐 安全配置

### 用户权限
- 用户名：`webuser`
- 主机：`localhost` 和 `%`
- 权限：`ALL PRIVILEGES` on `software_copyright.*`

### 密码安全
- 使用环境变量存储密码
- 不在代码中硬编码密码
- 定期更换密码

## 🧪 测试验证

### 连接测试
```python
# 测试数据库连接
python -c "from web_app.app import create_app; app = create_app('development'); print('连接成功')"
```

### 功能测试
```python
# 运行完整测试套件
python test_mysql.py
```

### Web应用测试
```bash
# 启动应用并访问
python run_web.py
# 访问 http://localhost:5000
```

## 🚨 故障排除

### 常见问题

#### 1. 连接被拒绝
```
OperationalError: (2003, "Can't connect to MySQL server")
```
**解决方案：**
- 确认MySQL服务正在运行
- 检查端口3306是否开放
- 验证主机地址是否正确

#### 2. 访问被拒绝
```
OperationalError: (1045, "Access denied for user 'webuser'@'localhost'")
```
**解决方案：**
- 确认用户名和密码正确
- 检查用户权限设置
- 重新运行 `setup_mysql.py`

#### 3. 数据库不存在
```
OperationalError: (1049, "Unknown database 'software_copyright'")
```
**解决方案：**
- 运行 `setup_mysql.py` 创建数据库
- 检查数据库名称拼写

#### 4. 表不存在
```
OperationalError: (1146, "Table 'software_copyright.staff' doesn't exist")
```
**解决方案：**
- 运行 `init_mysql.py` 创建表结构
- 检查表名是否正确

### 调试技巧

#### 1. 检查MySQL服务状态
```bash
# Windows
net start mysql

# Linux/Mac
sudo systemctl status mysql
```

#### 2. 检查数据库连接
```bash
mysql -u webuser -p -h 127.0.0.1 -P 3306 software_copyright
```

#### 3. 查看错误日志
```bash
# MySQL错误日志
tail -f /var/log/mysql/error.log

# 应用日志
python run_web.py 2>&1 | tee app.log
```

## 📈 性能优化

### 数据库优化
- 添加适当的索引
- 定期优化表
- 监控查询性能

### 连接池配置
```python
# 在config.py中添加
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 120,
    'pool_pre_ping': True
}
```

## 🔄 回滚方案

如果需要回滚到SQLite：

1. 修改 `config/config.py`：
```python
SQLALCHEMY_DATABASE_URI = 'sqlite:///software_copyright.db'
```

2. 重新初始化SQLite数据库：
```bash
python init_sqlite.py
```

3. 重启Web应用：
```bash
python run_web.py
```

## 📞 技术支持

如果遇到问题：
- 邮箱：admin@yiqichuang.com
- 电话：188 3826 9405
- 在线留言：系统内置留言功能

---

**注意：** 在生产环境中部署前，请确保：
1. 使用强密码
2. 配置防火墙规则
3. 定期备份数据库
4. 监控系统性能
