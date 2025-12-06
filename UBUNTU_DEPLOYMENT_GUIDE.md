 软著管理系统 - Ubuntu系统部署详细指南

## 目录

1. [项目概述](#项目概述)
2. [系统要求](#系统要求)
3. [准备工作](#准备工作)
4. [系统环境配置](#系统环境配置)
5. [数据库安装与配置](#数据库安装与配置)
6. [项目部署](#项目部署)
7. [Web服务器配置](#web服务器配置)
8. [SSL证书配置](#ssl证书配置)
9. [服务管理](#服务管理)
10. [备份与恢复](#备份与恢复)
11. [故障排查](#故障排查)
12. [安全加固](#安全加固)

---

## 项目概述

### 项目简介

软著管理系统是一个基于Flask框架开发的Web应用系统，用于管理软件著作权相关业务。系统采用前后端分离架构，支持Web端和桌面客户端两种访问方式。

### 技术架构

```
用户浏览器 → Nginx (80/443端口) → Gunicorn (8000端口) → Flask应用 → MySQL数据库
```

**核心技术栈：**
- **后端框架**: Flask 3.0.0
- **数据库**: MySQL 8.0
- **Web服务器**: Nginx
- **WSGI服务器**: Gunicorn
- **Python版本**: 3.8+
- **操作系统**: Ubuntu 20.04 LTS / 22.04 LTS

### 项目结构

```
Software_copyright_MS1.0/
├── web_app/              # Web应用主目录
│   ├── app.py           # Flask应用入口
│   ├── views/           # 视图函数
│   ├── utils/           # 工具函数
│   └── services/        # 业务服务
├── database/            # 数据库模型
│   └── models.py       # 数据模型定义
├── config/             # 配置文件
│   ├── config.py      # 基础配置
│   └── production.py  # 生产环境配置
├── templates/          # HTML模板
├── static/            # 静态资源（CSS/JS/图片）
├── migrate/           # 数据库迁移脚本
├── requirements.txt   # Python依赖包
├── wsgi.py           # WSGI入口文件
├── gunicorn_config.py # Gunicorn配置
├── init_mysql.py     # 数据库初始化脚本
├── deploy_web.sh     # 部署脚本
├── nginx_config/     # Nginx配置
└── systemd/          # 系统服务配置
```

---

## 系统要求

### 最低硬件配置

- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 40GB 可用空间（SSD推荐）
- **网络**: 5Mbps以上带宽
- **操作系统**: Ubuntu 20.04 LTS 或 Ubuntu 22.04 LTS

### 推荐硬件配置

- **CPU**: 4核心
- **内存**: 8GB RAM
- **存储**: 100GB SSD
- **网络**: 10Mbps以上带宽

### 软件要求

- Ubuntu 20.04 LTS / 22.04 LTS
- Python 3.8 或更高版本
- MySQL 8.0,注意进行数据库的配置文件编辑
- Nginx
- Git（用于代码管理）

---

## 准备工作

### 1. 获取服务器访问权限

您需要以下信息：
- **服务器IP地址**: 例如 `192.168.1.100` 或公网IP
- **SSH登录用户名**: 通常是 `root` 或 `ubuntu`
- **SSH登录密码** 或 **SSH密钥**

### 2. 连接服务器

#### Windows系统使用PuTTY或PowerShell

**使用PowerShell（推荐）：**
```powershell
# 打开PowerShell，输入以下命令
ssh root@your-server-ip
# 或
ssh ubuntu@your-server-ip
```

**使用PuTTY：**
1. 下载并安装PuTTY
2. 打开PuTTY，输入服务器IP地址
3. 点击"Open"连接
4. 输入用户名和密码

#### Mac/Linux系统

```bash
ssh root@your-server-ip
# 或
ssh ubuntu@your-server-ip
```

### 3. 准备项目文件

您需要将项目文件上传到服务器。有以下几种方式：

#### 方式一：使用SCP命令（推荐）

在您的本地电脑上（Windows PowerShell或Mac/Linux终端）：

```bash
# 将整个项目目录上传到服务器
scp -r /path/to/Software_copyright_MS1.0 root@your-server-ip:/tmp/
```

#### 方式二：使用Git（如果项目在Git仓库）

```bash
# 在服务器上执行
cd /tmp
git clone your-repository-url
```

#### 方式三：使用FTP工具（如FileZilla）

1. 下载FileZilla客户端
2. 使用SFTP连接到服务器
3. 上传项目文件夹

---

## 系统环境配置

### 步骤1：更新系统软件包

连接到服务器后，首先更新系统：

```bash
# 更新软件包列表
sudo apt update

# 升级已安装的软件包
sudo apt upgrade -y
```

**说明：**
- `sudo`: 以管理员权限执行命令
- `apt update`: 更新软件包列表
- `apt upgrade`: 升级软件包
- `-y`: 自动回答"yes"，无需确认

### 步骤2：安装基础工具

```bash
# 安装常用工具
sudo apt install -y curl wget git vim net-tools
```

**工具说明：**
- `curl`: 用于下载文件
- `wget`: 另一个下载工具
- `git`: 版本控制工具
- `vim`: 文本编辑器
- `net-tools`: 网络工具（包含ifconfig等）

### 步骤3：安装Python 3.8+

```bash
# 检查Python版本（Ubuntu 20.04/22.04通常已预装Python 3.8+）
python3 --version

# 如果没有安装，执行以下命令
sudo apt install -y python3 python3-pip python3-venv

# 验证安装
python3 --version
pip3 --version
```

**说明：**
- `python3`: Python解释器
- `pip3`: Python包管理器
- `python3-venv`: 虚拟环境工具

### 步骤4：安装MySQL数据库

```bash
# 安装MySQL服务器
sudo apt install -y mysql-server

# 启动MySQL服务
sudo systemctl start mysql

# 设置MySQL开机自启
sudo systemctl enable mysql

# 检查MySQL状态
sudo systemctl status mysql
```

**说明：**
- `systemctl start`: 启动服务
- `systemctl enable`: 设置开机自启
- `systemctl status`: 查看服务状态

### 步骤5：安装Nginx

```bash
# 安装Nginx
sudo apt install -y nginx

# 启动Nginx服务
sudo systemctl start nginx

# 设置Nginx开机自启
sudo systemctl enable nginx

# 检查Nginx状态
sudo systemctl status nginx
```

### 步骤6：配置防火墙

```bash
# 安装防火墙工具（如果未安装）
sudo apt install -y ufw

# 允许SSH连接（重要！先允许SSH，避免被锁在外面）
sudo ufw allow 22/tcp

# 允许HTTP和HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 查看防火墙状态
sudo ufw status
```

**重要提示：**
- 必须先允许SSH（22端口），否则可能无法远程连接
- 如果使用云服务器，还需要在云平台控制台配置安全组规则

---

## 数据库安装与配置

### 步骤1：配置MySQL root密码

```bash
# 运行MySQL安全配置脚本
sudo mysql_secure_installation
```

**配置过程说明：**

1. **设置root密码验证插件**
   - 询问：`Would you like to setup VALIDATE PASSWORD plugin?`
   - 建议选择：`Y`（是）
   - 选择密码强度级别：`2`（中等强度）

2. **设置root密码**
   - 输入您要设置的密码（请记住这个密码！）
   - 确认密码

3. **其他安全选项**
   - `Remove anonymous users?` → 输入 `Y`
   - `Disallow root login remotely?` → 输入 `Y`（如果只本地访问）
   - `Remove test database?` → 输入 `Y`
   - `Reload privilege tables now?` → 输入 `Y`

### 步骤2：创建数据库和用户

```bash
# 登录MySQL（使用刚才设置的root密码）
sudo mysql -u root -p
```

进入MySQL命令行后，执行以下SQL命令：

```sql
-- 创建数据库（使用utf8mb4字符集，支持中文和emoji）
CREATE DATABASE software_copyright CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建应用用户（请将 'your_strong_password' 替换为强密码）
CREATE USER 'webuser'@'localhost' IDENTIFIED BY 'your_strong_password';

-- 授予权限
GRANT ALL PRIVILEGES ON software_copyright.* TO 'webuser'@'localhost';

-- 刷新权限
FLUSH PRIVILEGES;

-- 查看用户（验证创建成功）
SELECT user, host FROM mysql.user;

-- 退出MySQL
EXIT;
```

**密码安全建议：**
- 密码长度至少12位
- 包含大小写字母、数字和特殊字符
- 例如：`MyApp@2024#Secure`

**重要提示：**
- 请妥善保存数据库密码，后续配置需要使用
- `webuser` 是应用连接数据库的用户名
- `localhost` 表示只允许本地连接

### 步骤3：测试数据库连接

```bash
# 使用新创建的用户测试连接
mysql -u webuser -p software_copyright
```

输入密码后，如果成功进入MySQL命令行，说明配置正确。输入 `EXIT;` 退出。

---

## 项目部署

### 步骤1：创建应用目录

```bash
# 创建应用主目录
sudo mkdir -p /var/www/software_copyright

# 创建必要的子目录
sudo mkdir -p /var/www/software_copyright/uploads
sudo mkdir -p /var/www/software_copyright/logs
sudo mkdir -p /var/log/software_copyright

# 创建备份目录
sudo mkdir -p /var/backups/software_copyright
```

### 步骤2：复制项目文件

这里使用gitee仓库，将项目文件复制到服务器上，然后下载到Ubuntu系统上。

```bash
# 进入目标目录
cd /var/www/software_copyright

# 使用Git从Gitee仓库下载项目
git clone https://gitee.com/your_username/your_repository.git .
```

**验证文件是否复制成功：**
```bash
# 查看应用目录内容
ls -la /var/www/software_copyright/
```

应该能看到 `web_app`、`database`、`config`、`requirements.txt` 等文件和目录。

### 步骤3：创建Python虚拟环境

```bash
# 进入应用目录
cd /var/www/software_copyright

# 创建虚拟环境
sudo python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级pip
pip install --upgrade pip

# 安装项目依赖
pip install -r requirements.txt

# 安装Gunicorn（生产环境WSGI服务器）
pip install gunicorn
```

**说明：**
- `venv`: 虚拟环境目录，用于隔离项目依赖
- `source venv/bin/activate`: 激活虚拟环境（激活后命令提示符前会显示 `(venv)`）
- 虚拟环境激活后，`pip` 安装的包只会安装到当前虚拟环境中

### 步骤4：配置环境变量

```bash
# 创建环境变量文件
sudo nano /var/www/software_copyright/.env
```

**在nano编辑器中输入以下内容：**

```bash
# 数据库配置
DB_PASSWORD=your_strong_password_here

# Flask配置
FLASK_CONFIG=production
SECRET_KEY=your-secret-key-here-change-this

# 应用URL（请替换为您的域名或IP）
APP_URL=https://your-domain.com

# 邮件配置（可选，用于发送邮件通知）
APPEMAILACCOUNT=your_email@example.com
APPEMAILSMTP=your_smtp_password
```

**关于引号的使用：**
- **通常不需要引号**：大多数情况下，等号后面的值不需要加引号
- **需要引号的情况**：
  - 值中包含空格：`KEY="value with spaces"`
  - 值中包含特殊字符（如 `#`、`$`、`&` 等）：`KEY="value#with$special&chars"`
  - 密码中包含特殊字符时建议加引号：`DB_PASSWORD="My@Pass#2024"`
- **URL和普通字符串**：通常不需要引号，如 `APP_URL=https://your-domain.com`

**重要配置说明：**

1. **DB_PASSWORD**: 替换为步骤2中创建的 `webuser` 用户的密码

2. **SECRET_KEY**: Flask应用的密钥，用于：
   - **加密用户会话（Session）**：保护用户登录状态
   - **生成CSRF令牌**：防止跨站请求伪造攻击
   - **签名Cookie**：确保Cookie不被篡改
   - **加密敏感数据**：保护临时存储的敏感信息
   
   **生成方法（在Ubuntu服务器上执行）：**
   ```bash
   # 方法1：使用openssl（推荐）
   openssl rand -hex 32
   
   # 方法2：使用Python
   python3 -c "import secrets; print(secrets.token_hex(32))"
   
   # 方法3：使用Python的os.urandom
   python3 -c "import os; print(os.urandom(32).hex())"
   ```
   
   **示例输出：**
   ```
   a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
   ```
   
   **重要提示：**
   - SECRET_KEY必须是**随机生成的**，不能使用固定值
   - 长度建议至少32字节（64个十六进制字符）
   - **必须保密**，不要提交到代码仓库
   - 如果泄露，需要立即更换，否则用户会话可能被劫持

3. **APP_URL**: 您的网站访问地址
   - 如果有域名：`https://your-domain.com`
   - 如果只有IP：`http://your-server-ip`

**保存文件：**
- 按 `Ctrl + O` 保存
- 按 `Enter` 确认文件名
- 按 `Ctrl + X` 退出

**或者使用tee命令快速创建：**

```bash
# 生成SECRET_KEY
SECRET_KEY=$(openssl rand -hex 32)

# 创建.env文件（请替换实际值）
# 注意：如果密码包含特殊字符，建议用引号括起来
sudo tee /var/www/software_copyright/.env > /dev/null <<EOF
DB_PASSWORD=your_strong_password_here
FLASK_CONFIG=production
SECRET_KEY=$SECRET_KEY
APP_URL=https://your-domain.com
APPEMAILACCOUNT=your_email@example.com
APPEMAILSMTP=your_smtp_password
EOF
```

**示例：如果密码包含特殊字符**
```bash
# 如果密码是 "My@Pass#2024"，应该这样写：
DB_PASSWORD="My@Pass#2024"

# 或者使用单引号（在bash中，单引号内的变量不会被展开）
DB_PASSWORD='My@Pass#2024'
```

### 步骤5：加载环境变量

修改应用启动脚本以加载环境变量。创建启动脚本：

```bash
# 创建环境变量加载脚本
sudo nano /var/www/software_copyright/load_env.sh
```

输入以下内容：

```bash
#!/bin/bash
# 加载环境变量
if [ -f /var/www/software_copyright/.env ]; then
    export $(cat /var/www/software_copyright/.env | grep -v '^#' | xargs)
fi
```

保存后设置执行权限：

```bash
sudo chmod +x /var/www/software_copyright/load_env.sh
```

### 步骤6：初始化数据库

```bash
# 进入应用目录
cd /var/www/software_copyright

# 激活虚拟环境
source venv/bin/activate

# 加载环境变量
source load_env.sh

# 运行数据库初始化脚本
python init_mysql.py
```

**说明：**
- `init_mysql.py` 会创建所有数据库表
- 如果看到 "✅ 所有数据库表创建成功！" 说明初始化成功

### 步骤7：设置文件权限

```bash
# 设置目录所有者（www-data是Nginx和Web应用运行的用户）
sudo chown -R www-data:www-data /var/www/software_copyright

# 设置目录权限
sudo chmod -R 755 /var/www/software_copyright

# 设置上传目录和日志目录可写
sudo chmod -R 775 /var/www/software_copyright/uploads
sudo chmod -R 775 /var/www/software_copyright/logs
```

**权限说明：**
- `755`: 所有者可读写执行，其他人可读执行
- `775`: 所有者可读写执行，组可读写执行，其他人可读执行
- `www-data`: Ubuntu中Web服务器的默认用户

---

## Web服务器配置

### 步骤1：配置Gunicorn

Gunicorn配置文件已存在于项目中（`gunicorn_config.py`），但需要确保路径正确。

检查配置文件：

```bash
cat /var/www/software_copyright/gunicorn_config.py
```

如果需要修改，编辑配置文件：

```bash
sudo nano /var/www/software_copyright/gunicorn_config.py
```

**关键配置说明：**
- `bind = '127.0.0.1:8000'`: Gunicorn监听地址和端口
- `workers`: Worker进程数（自动根据CPU核心数计算）
- `accesslog` 和 `errorlog`: 日志文件路径

### 步骤2：创建Systemd服务

```bash
# 复制服务配置文件
sudo cp /var/www/software_copyright/systemd/software_copyright.service /etc/systemd/system/

# 编辑服务文件（检查路径是否正确）
sudo nano /etc/systemd/system/software_copyright.service
```

**确保服务文件内容如下：**

```ini
[Unit]
Description=Software Copyright Management System
After=network.target mysql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/software_copyright
Environment="PATH=/var/www/software_copyright/venv/bin"
EnvironmentFile=/var/www/software_copyright/.env
ExecStart=/var/www/software_copyright/venv/bin/gunicorn -c gunicorn_config.py wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**重要配置说明：**
- `EnvironmentFile`: 加载环境变量文件
- `WorkingDirectory`: 应用工作目录
- `User` 和 `Group`: 运行服务的用户
- `Restart=always`: 服务异常退出时自动重启

**重新加载systemd并启动服务：**

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start software_copyright

# 设置开机自启
sudo systemctl enable software_copyright

# 查看服务状态
sudo systemctl status software_copyright
```

**如果服务启动失败，查看日志：**

```bash
# 查看服务日志
sudo journalctl -u software_copyright -f
```

### 步骤3：配置Nginx

```bash
# 复制Nginx配置文件
sudo cp /var/www/software_copyright/nginx_config/software_copyright.conf /etc/nginx/sites-available/

# 编辑配置文件（替换域名）
sudo nano /etc/nginx/sites-available/software_copyright.conf
```

**修改配置文件中的域名：**

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    # 如果没有域名，使用IP地址
    # server_name your-server-ip;
    
    # 重定向到HTTPS（如果已配置SSL）
    # return 301 https://$server_name$request_uri;
    
    # 或者暂时允许HTTP访问（用于测试）
    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://127.0.0.1:8000;
        
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # 静态文件
    location /static {
        alias /var/www/software_copyright/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 文件上传大小限制
    client_max_body_size 20M;
}
```

**启用站点：**

```bash
# 创建符号链接
sudo ln -s /etc/nginx/sites-available/software_copyright.conf /etc/nginx/sites-enabled/

# 删除默认站点（可选）
sudo rm /etc/nginx/sites-enabled/default

# 测试Nginx配置
sudo nginx -t

# 如果测试通过，重启Nginx
sudo systemctl restart nginx
```

**验证Nginx状态：**

```bash
sudo systemctl status nginx
```

### 步骤4：检查IPv6支持（可选）

如果您需要支持IPv6访问，可以运行检查脚本：

```bash
# 在项目目录中
chmod +x check_ipv6.sh
./check_ipv6.sh
```

**快速检查IPv6：**
```bash
# 检查系统IPv6支持
ip -6 addr show

# 检查IPv6端口监听
sudo ss -tlnp6 | grep -E ':(80|443|8000)'
```

**启用IPv6支持：**
- 详细配置请参考：`mdfiles/IPV6_CONFIGURATION_GUIDE.md`
- 简单方法：修改 `gunicorn_config.py` 中的 `bind = '[::]:8000'`
- 在Nginx配置中添加 `listen [::]:80;` 和 `listen [::]:443 ssl http2;`

---

## SSL证书配置

### 使用Let's Encrypt免费SSL证书

Let's Encrypt提供免费的SSL证书，有效期90天，可自动续期。

### 步骤1：安装Certbot

```bash
# 安装Certbot和Nginx插件
sudo apt install -y certbot python3-certbot-nginx
```

### 步骤2：获取SSL证书

**前提条件：**
- 域名已解析到服务器IP（A记录）
- 80端口已开放（Let's Encrypt需要验证域名）

```bash
# 获取SSL证书（替换为您的域名）
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

**配置过程：**
1. 输入邮箱地址（用于证书到期提醒）
2. 同意服务条款：输入 `A`（同意）
3. 是否分享邮箱：输入 `Y` 或 `N`
4. 选择重定向HTTP到HTTPS：输入 `2`（推荐）

**说明：**
- Certbot会自动修改Nginx配置文件
- 证书会自动安装到 `/etc/letsencrypt/live/your-domain.com/`
- 证书有效期90天，会自动续期

### 步骤3：测试自动续期

```bash
# 测试证书续期（不会真正续期，只是测试）
sudo certbot renew --dry-run
```

### 步骤4：配置自动续期

```bash
# 编辑crontab（定时任务）
sudo crontab -e
```

**添加以下行（每天凌晨2点检查并续期）：**
```
0 2 * * * /usr/bin/certbot renew --quiet
```

**保存并退出：**
- 按 `Ctrl + O` 保存
- 按 `Enter` 确认
- 按 `Ctrl + X` 退出

### 步骤5：验证HTTPS访问

在浏览器中访问：
- `https://your-domain.com`
- 应该看到绿色的锁图标，表示SSL证书有效

---

## 服务管理

### 查看服务状态

```bash
# 查看应用服务状态
sudo systemctl status software_copyright

# 查看Nginx状态
sudo systemctl status nginx

# 查看MySQL状态
sudo systemctl status mysql
```

### 启动/停止/重启服务

```bash
# 应用服务
sudo systemctl start software_copyright    # 启动
sudo systemctl stop software_copyright     # 停止
sudo systemctl restart software_copyright  # 重启
sudo systemctl reload software_copyright   # 重新加载配置（不中断服务）

# Nginx服务
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx
sudo systemctl reload nginx

# MySQL服务
sudo systemctl start mysql
sudo systemctl stop mysql
sudo systemctl restart mysql
```

### 查看服务日志

```bash
# 查看应用服务日志（实时）
sudo journalctl -u software_copyright -f

# 查看最近100行日志
sudo journalctl -u software_copyright -n 100

# 查看今天的日志
sudo journalctl -u software_copyright --since today

# 查看Gunicorn错误日志
sudo tail -f /var/log/software_copyright/gunicorn_error.log

# 查看Gunicorn访问日志
sudo tail -f /var/log/software_copyright/gunicorn_access.log

# 查看Nginx错误日志
sudo tail -f /var/log/nginx/software_copyright_error.log

# 查看Nginx访问日志
sudo tail -f /var/log/nginx/software_copyright_access.log
```

### 设置开机自启

```bash
# 确保服务开机自启（通常已设置）
sudo systemctl enable software_copyright
sudo systemctl enable nginx
sudo systemctl enable mysql
```

---

## 备份与恢复

### 自动备份脚本

项目已包含备份脚本 `backup.sh`，需要稍作修改：

```bash
# 编辑备份脚本
sudo nano /var/www/software_copyright/backup.sh
```

**确保脚本内容如下（根据实际情况修改密码）：**

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/software_copyright"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库（需要输入密码，或使用配置文件）
mysqldump -u webuser -p'your_db_password' software_copyright > $BACKUP_DIR/db_$DATE.sql

# 备份上传文件
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/software_copyright/uploads

# 备份应用代码（可选）
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /var/www/software_copyright --exclude=venv --exclude=__pycache__

# 删除30天前的备份
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "备份完成: $DATE"
```

**设置执行权限：**

```bash
sudo chmod +x /var/www/software_copyright/backup.sh
```

### 配置定时备份

```bash
# 编辑crontab
sudo crontab -e
```

**添加以下行（每天凌晨3点执行备份）：**
```
0 3 * * * /var/www/software_copyright/backup.sh >> /var/log/backup.log 2>&1
```

### 手动备份

```bash
# 执行备份脚本
sudo /var/www/software_copyright/backup.sh
```

### 恢复数据库

```bash
# 恢复数据库备份
mysql -u webuser -p software_copyright < /var/backups/software_copyright/db_20240101_120000.sql
```

### 恢复上传文件

```bash
# 解压上传文件备份
sudo tar -xzf /var/backups/software_copyright/uploads_20240101_120000.tar.gz -C /
```

---

## 故障排查

### 问题1：无法访问网站

**检查步骤：**

```bash
# 1. 检查Nginx是否运行
sudo systemctl status nginx

# 2. 检查应用服务是否运行
sudo systemctl status software_copyright

# 3. 检查端口是否监听
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :8000

# 4. 检查防火墙
sudo ufw status

# 5. 查看Nginx错误日志
sudo tail -50 /var/log/nginx/software_copyright_error.log

# 6. 查看应用日志
sudo journalctl -u software_copyright -n 50
```

### 问题2：数据库连接失败

**检查步骤：**

```bash
# 1. 检查MySQL是否运行
sudo systemctl status mysql

# 2. 测试数据库连接
mysql -u webuser -p software_copyright

# 3. 检查环境变量
cat /var/www/software_copyright/.env | grep DB_PASSWORD

# 4. 查看应用日志中的数据库错误
sudo journalctl -u software_copyright | grep -i "database\|mysql\|connection"
```

**常见原因：**
- 数据库密码错误
- MySQL服务未启动
- 环境变量未正确加载

### 问题3：静态文件无法加载

**检查步骤：**

```bash
# 1. 检查静态文件目录是否存在
ls -la /var/www/software_copyright/static

# 2. 检查Nginx配置中的静态文件路径
sudo nginx -T | grep static

# 3. 检查文件权限
sudo ls -la /var/www/software_copyright/static

# 4. 测试静态文件访问
curl -I http://your-domain.com/static/css/style.css
```

### 问题4：文件上传失败

**检查步骤：**

```bash
# 1. 检查上传目录权限
ls -ld /var/www/software_copyright/uploads
# 应该是 drwxrwxr-x www-data www-data

# 2. 检查磁盘空间
df -h

# 3. 检查Nginx配置中的文件大小限制
sudo nginx -T | grep client_max_body_size

# 4. 查看应用日志
sudo journalctl -u software_copyright | grep -i "upload\|file"
```

### 问题5：服务无法启动

**检查步骤：**

```bash
# 1. 查看详细错误信息
sudo journalctl -u software_copyright -n 100 --no-pager

# 2. 检查配置文件语法
cd /var/www/software_copyright
source venv/bin/activate
python -c "from wsgi import app; print('OK')"

# 3. 检查Gunicorn配置
source venv/bin/activate
gunicorn -c gunicorn_config.py wsgi:app --check-config

# 4. 手动测试启动
cd /var/www/software_copyright
source venv/bin/activate
source load_env.sh
gunicorn -c gunicorn_config.py wsgi:app
```

### 问题6：SSL证书问题

**检查步骤：**

```bash
# 1. 检查证书是否过期
sudo certbot certificates

# 2. 手动续期证书
sudo certbot renew

# 3. 检查Nginx SSL配置
sudo nginx -T | grep ssl

# 4. 测试SSL连接
openssl s_client -connect your-domain.com:443
```

### 常用诊断命令

```bash
# 查看系统资源使用
htop
# 或
top

# 查看磁盘使用
df -h
du -sh /var/www/software_copyright/*

# 查看内存使用
free -h

# 查看网络连接
netstat -tlnp
ss -tlnp

# 查看进程
ps aux | grep gunicorn
ps aux | grep nginx
```

---

## 安全加固

### 1. 系统安全更新

```bash
# 定期更新系统
sudo apt update && sudo apt upgrade -y

# 设置自动安全更新（可选）
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 2. 防火墙配置

```bash
# 查看当前防火墙规则
sudo ufw status verbose

# 只允许必要的端口
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS

# 启用防火墙
sudo ufw enable
```

### 3. SSH安全配置

```bash
# 编辑SSH配置
sudo nano /etc/ssh/sshd_config
```

**推荐配置：**
```
PermitRootLogin no              # 禁止root登录
PasswordAuthentication yes      # 允许密码登录（或改为no使用密钥）
PubkeyAuthentication yes         # 允许密钥登录
Port 22                         # SSH端口（可改为其他端口）
```

**重启SSH服务：**
```bash
sudo systemctl restart sshd
```

### 4. MySQL安全配置

```bash
# 运行MySQL安全配置脚本
sudo mysql_secure_installation
```

**推荐设置：**
- 移除匿名用户：`Y`
- 禁止root远程登录：`Y`
- 移除测试数据库：`Y`
- 重新加载权限表：`Y`

### 5. 应用安全配置

**检查敏感信息：**
```bash
# 确保.env文件权限正确
ls -la /var/www/software_copyright/.env
# 应该是 -rw-r--r-- www-data www-data

# 如果权限不对，修正：
sudo chmod 600 /var/www/software_copyright/.env
sudo chown www-data:www-data /var/www/software_copyright/.env
```

**定期更新Python依赖：**
```bash
cd /var/www/software_copyright
source venv/bin/activate
pip list --outdated
pip install --upgrade package_name
```

### 6. 日志监控

```bash
# 安装日志分析工具（可选）
sudo apt install -y logwatch

# 配置fail2ban防止暴力破解
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 7. 定期安全检查清单

- [ ] 系统软件包已更新
- [ ] 防火墙规则已配置
- [ ] SSH安全配置已应用
- [ ] 数据库密码强度足够
- [ ] 应用环境变量文件权限正确
- [ ] SSL证书有效且未过期
- [ ] 备份策略已实施
- [ ] 日志监控已配置

---

## 性能优化

### 1. Nginx优化

编辑Nginx主配置文件：

```bash
sudo nano /etc/nginx/nginx.conf
```

**优化建议：**
```nginx
# 工作进程数（通常等于CPU核心数）
worker_processes auto;

# 每个工作进程的最大连接数
events {
    worker_connections 1024;
    use epoll;
}

# 启用Gzip压缩
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
```

**重启Nginx：**
```bash
sudo systemctl restart nginx
```

### 2. Gunicorn优化

编辑Gunicorn配置：

```bash
sudo nano /var/www/software_copyright/gunicorn_config.py
```

**根据服务器配置调整：**
```python
# Worker进程数（建议：CPU核心数 * 2 + 1）
workers = 4

# Worker类型（异步处理）
worker_class = 'gevent'
worker_connections = 1000

# 超时时间
timeout = 120
keepalive = 5
```

**安装gevent（如果使用异步worker）：**
```bash
cd /var/www/software_copyright
source venv/bin/activate
pip install gevent
```

### 3. MySQL优化

编辑MySQL配置：

```bash
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

**基础优化：**
```ini
[mysqld]
# 最大连接数
max_connections = 200

# 缓冲区大小（根据内存调整）
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M

# 查询缓存
query_cache_type = 1
query_cache_size = 64M
```

**重启MySQL：**
```bash
sudo systemctl restart mysql
```

### 4. 静态文件CDN（可选）

对于生产环境，建议使用CDN加速静态文件：
- 阿里云CDN
- 腾讯云CDN
- Cloudflare

---

## 更新维护

### 更新应用代码

```bash
# 1. 备份当前版本
sudo /var/www/software_copyright/backup.sh

# 2. 停止服务
sudo systemctl stop software_copyright

# 3. 备份当前代码
sudo tar -czf /var/backups/software_copyright/app_backup_$(date +%Y%m%d).tar.gz /var/www/software_copyright --exclude=venv --exclude=__pycache__

# 4. 更新代码（根据您的代码管理方式）
# 方式1：从Git更新
cd /var/www/software_copyright
sudo -u www-data git pull

# 方式2：上传新文件
# 将新文件上传到 /tmp，然后复制
sudo cp -r /tmp/new_version/* /var/www/software_copyright/

# 5. 更新依赖（如果有新依赖）
cd /var/www/software_copyright
source venv/bin/activate
pip install -r requirements.txt

# 6. 运行数据库迁移（如果有）
source venv/bin/activate
source load_env.sh
python migrate/your_migration_script.py

# 7. 设置权限
sudo chown -R www-data:www-data /var/www/software_copyright
sudo chmod -R 755 /var/www/software_copyright
sudo chmod -R 775 /var/www/software_copyright/uploads
sudo chmod -R 775 /var/www/software_copyright/logs

# 8. 重启服务
sudo systemctl start software_copyright

# 9. 检查服务状态
sudo systemctl status software_copyright
```

### 更新系统软件包

```bash
# 更新软件包列表
sudo apt update

# 查看可更新的软件包
sudo apt list --upgradable

# 更新软件包
sudo apt upgrade -y

# 重启系统（如果需要）
sudo reboot
```

---

## 部署检查清单

在完成部署后，请逐项检查：

### 系统环境
- [ ] Ubuntu系统已更新到最新版本
- [ ] Python 3.8+ 已安装
- [ ] MySQL 8.0 已安装并运行
- [ ] Nginx 已安装并运行
- [ ] 防火墙规则已配置

### 数据库配置
- [ ] MySQL数据库已创建
- [ ] 数据库用户已创建并授权
- [ ] 数据库表已初始化
- [ ] 可以正常连接数据库

### 应用部署
- [ ] 项目文件已上传到 `/var/www/software_copyright`
- [ ] Python虚拟环境已创建
- [ ] 所有依赖包已安装
- [ ] 环境变量文件已配置
- [ ] 文件权限已正确设置

### 服务配置
- [ ] Gunicorn服务已配置并运行
- [ ] Nginx已配置并运行
- [ ] 服务已设置开机自启
- [ ] 可以正常访问网站

### SSL证书
- [ ] SSL证书已安装（如果使用HTTPS）
- [ ] 证书自动续期已配置
- [ ] HTTPS可以正常访问

### 备份配置
- [ ] 备份脚本已配置
- [ ] 定时备份已设置
- [ ] 备份目录已创建

### 安全配置
- [ ] 防火墙已启用
- [ ] SSH安全配置已应用
- [ ] 敏感文件权限已设置
- [ ] 数据库密码强度足够

### 功能测试
- [ ] 可以正常登录系统
- [ ] 可以上传文件
- [ ] 可以查看和编辑数据
- [ ] 邮件功能正常（如果配置）

---

## 常见问题FAQ

### Q1: 忘记MySQL root密码怎么办？

```bash
# 1. 停止MySQL服务
sudo systemctl stop mysql

# 2. 以安全模式启动MySQL
sudo mysqld_safe --skip-grant-tables &

# 3. 登录MySQL（无需密码）
mysql -u root

# 4. 重置密码
USE mysql;
UPDATE user SET authentication_string=PASSWORD('new_password') WHERE User='root';
FLUSH PRIVILEGES;
EXIT;

# 5. 重启MySQL
sudo systemctl restart mysql
```

### Q2: 如何查看应用占用的端口？

```bash
sudo netstat -tlnp | grep python
# 或
sudo ss -tlnp | grep python
```

### Q3: 如何查看磁盘使用情况？

```bash
# 查看整体磁盘使用
df -h

# 查看目录大小
du -sh /var/www/software_copyright/*
```

### Q4: 如何重启所有服务？

```bash
sudo systemctl restart mysql
sudo systemctl restart software_copyright
sudo systemctl restart nginx
```

### Q5: 如何查看系统资源使用？

```bash
# 安装htop（更友好的top工具）
sudo apt install -y htop

# 使用htop查看
htop
```

### Q6: 如何添加新的管理员账户？

```bash
cd /var/www/software_copyright
source venv/bin/activate
source load_env.sh
python
```

在Python交互式环境中：
```python
from web_app.app import create_app
from database.models import db, Staff, Permission

app = create_app('production')
with app.app_context():
    # 创建管理员权限
    admin_perm = Permission(
        position='系统管理员',
        can_confirm=True,
        can_approve=True,
        can_execute=True,
        can_manage=True,
        can_view_all=True
    )
    db.session.add(admin_perm)
    db.session.commit()
    
    # 创建管理员账户
    admin = Staff(
        name='新管理员',
        email='admin@example.com',
        phone='13800138000',
        position_id=admin_perm.id
    )
    admin.set_password('your_password')
    db.session.add(admin)
    db.session.commit()
    print("管理员账户创建成功！")
```

---

## 技术支持

### 日志文件位置

- **应用日志**: `/var/log/software_copyright/`
- **Nginx日志**: `/var/log/nginx/`
- **系统日志**: `/var/log/syslog`
- **服务日志**: `sudo journalctl -u software_copyright`

### 重要配置文件位置

- **应用目录**: `/var/www/software_copyright/`
- **环境变量**: `/var/www/software_copyright/.env`
- **Nginx配置**: `/etc/nginx/sites-available/software_copyright.conf`
- **服务配置**: `/etc/systemd/system/software_copyright.service`
- **Gunicorn配置**: `/var/www/software_copyright/gunicorn_config.py`
- **MySQL配置**: `/etc/mysql/mysql.conf.d/mysqld.cnf`

### 获取帮助

如果遇到问题：
1. 查看相关日志文件
2. 检查服务状态
3. 参考故障排查章节
4. 联系技术支持团队

---

## 附录

### A. 常用命令速查

```bash
# 服务管理
sudo systemctl start|stop|restart|status service_name

# 查看日志
sudo journalctl -u service_name -f
sudo tail -f /path/to/logfile

# 文件操作
ls -la          # 列出文件
cat file        # 查看文件
nano file       # 编辑文件
chmod +x file   # 添加执行权限
chown user:group file  # 修改所有者

# 网络
netstat -tlnp   # 查看端口
ping host       # 测试连接
curl url        # 测试HTTP请求

# 系统
df -h           # 磁盘使用
free -h         # 内存使用
top             # 进程监控
```

### B. 环境变量说明

| 变量名 | 说明 | 示例 |
|--------|------|------|
| DB_PASSWORD | MySQL数据库密码 | MyApp@2024#Secure |
| FLASK_CONFIG | Flask配置环境 | production |
| SECRET_KEY | Flask会话密钥 | (32位随机字符串) |
| APP_URL | 应用访问地址 | https://your-domain.com |
| APPEMAILACCOUNT | 邮件账户 | your_email@example.com |
| APPEMAILSMTP | SMTP密码 | your_smtp_password |

**环境变量格式说明：**
- **基本格式**：`KEY=value`（等号前后不要有空格）
- **不需要引号**：普通字符串、URL、数字等
  ```bash
  FLASK_CONFIG=production
  APP_URL=https://your-domain.com
  ```
- **需要引号**：值包含空格或特殊字符时
  ```bash
  DB_PASSWORD="My@Pass#2024"    # 包含特殊字符
  KEY="value with spaces"        # 包含空格
  ```
- **引号类型**：
  - 双引号 `"`：允许变量展开（bash中）
  - 单引号 `'`：不展开变量，原样输出

### C. 端口说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 22 | SSH | 远程管理 |
| 80 | HTTP | Web访问 |
| 443 | HTTPS | 安全Web访问 |
| 3306 | MySQL | 数据库（通常只允许本地） |
| 8000 | Gunicorn | 应用服务器（只允许本地） |

---

**文档版本**: 1.0  
**最后更新**: 2024年  
**适用系统**: Ubuntu 20.04 LTS / 22.04 LTS

---

**祝您部署顺利！如有问题，请参考故障排查章节或联系技术支持。**