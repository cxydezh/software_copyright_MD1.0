-- 软著管理系统 - Windows Server MySQL数据库初始化脚本
-- 执行前请确保MySQL服务已启动

-- 创建数据库
CREATE DATABASE IF NOT EXISTS software_copyright 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 创建用户（请修改密码）
CREATE USER IF NOT EXISTS 'webuser'@'localhost' IDENTIFIED BY 'SoftwareCopyright2024!';

-- 授权
GRANT ALL PRIVILEGES ON software_copyright.* TO 'webuser'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 使用数据库
USE software_copyright;

-- 显示创建结果
SELECT 'Database and user created successfully!' as Status;

-- 显示数据库信息
SHOW DATABASES LIKE 'software_copyright';

-- 显示用户信息
SELECT User, Host FROM mysql.user WHERE User = 'webuser';



