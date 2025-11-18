# 软著管理系统 - 分离部署实施指南

## 概述

本指南详细说明了如何将软著管理系统的Web应用和Desktop应用进行分离部署，实现云端Web服务和本地桌面客户端的架构。支持Linux和Windows Server两种部署环境。

## 部署架构

```
互联网用户 → 云服务器(Nginx/IIS:80/443) → Gunicorn/wfastcgi(Flask) → MySQL
                                              ↑
内部员工 → Desktop.exe → HTTP API ────────────┘
                      → 本地SQLite
```

## 部署环境选择

### Linux环境（推荐）
- 操作系统：Ubuntu 20.04 LTS
- Web服务器：Nginx + Gunicorn
- 数据库：MySQL 8.0
- SSL证书：Let's Encrypt

### Windows Server环境
- 操作系统：Windows Server 2019/2022
- Web服务器：IIS + wfastcgi
- 数据库：MySQL 8.0
- SSL证书：Let's Encrypt (win-acme)

---

### 1.1 服务器准备

**推荐配置**:
- CPU: 2核
- 内存: 4GB
- 存储: 40GB SSD
- 带宽: 5Mbps以上
- 操作系统: Ubuntu 20.04 LTS

**基础软件安装**:
```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Python 3.8+
sudo apt install python3 python3-pip python3-venv -y

# 安装MySQL
sudo apt install mysql-server -y

# 安装Nginx
sudo apt install nginx -y

# 安装其他工具
sudo apt install git curl wget openssl -y
```

### 1.2 数据库配置

```bash
# 登录MySQL
sudo mysql -u root -p

# 创建数据库和用户
CREATE DATABASE software_copyright CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'webuser'@'localhost' IDENTIFIED BY 'your_strong_password_here';
GRANT ALL PRIVILEGES ON software_copyright.* TO 'webuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 1.3 部署步骤

1. **上传代码到服务器**:
```bash
scp -r /path/to/project root@your-server-ip:/tmp/
```

2. **执行部署脚本**:
```bash
ssh root@your-server-ip
cd /tmp/project
chmod +x deploy_web.sh
./deploy_web.sh
```

3. **配置Nginx**:
```bash
sudo cp nginx_config/software_copyright.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/software_copyright.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **配置systemd服务**:
```bash
sudo cp systemd/software_copyright.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable software_copyright
sudo systemctl start software_copyright
```

5. **检查服务状态**:
```bash
sudo systemctl status software_copyright
sudo systemctl status nginx
```

### 1.4 SSL证书配置

**使用Let's Encrypt免费证书**:
```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取证书
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 设置自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 二、Windows Server环境Web应用部署

### 2.1 服务器环境准备

**推荐配置**:
- Windows Server 2019/2022
- CPU: 4核心
- 内存: 8GB
- 存储: 100GB SSD
- 公网IP和域名

**安装必需软件**:
1. Python 3.8+ (从python.org下载)
2. MySQL 8.0 (从mysql.com下载)
3. IIS (通过服务器管理器启用)
4. URL Rewrite模块 (从IIS官网下载)
5. wfastcgi (Python的IIS适配器)

### 2.2 自动化部署

**使用PowerShell部署脚本**:
```powershell
# 1. 以管理员身份运行PowerShell
# 2. 执行部署脚本
.\windows_deployment\deploy_windows.ps1 -DomainName "116.62.177.223" -DbPassword "cxy@51885188"
```

**手动部署步骤**:
1. 复制项目文件到 `C:\inetpub\wwwroot\software_copyright`
2. 创建Python虚拟环境
3. 安装依赖包和wfastcgi
4. 配置MySQL数据库
5. 设置IIS应用程序池和网站
6. 配置SSL证书

### 2.3 IIS配置

**web.config配置**:
项目已包含 `windows_deployment/web.config` 文件，包含：
- FastCGI处理器配置
- URL重写规则
- 静态文件处理
- 安全头设置
- 错误页面配置

**应用程序池设置**:
- 名称：SoftwareCopyrightAppPool
- .NET Framework版本：无托管代码
- 进程模型：ApplicationPoolIdentity
- 回收条件：内存限制、时间限制

### 2.4 SSL证书配置

**使用win-acme自动获取Let's Encrypt证书**:
```powershell
# 执行SSL配置脚本
.\windows_deployment\setup_ssl_windows.ps1 -DomainName "your-domain.com" -Email "admin@your-domain.com"
```

**手动配置SSL**:
1. 安装win-acme工具
2. 申请Let's Encrypt证书
3. 在IIS中绑定SSL证书
4. 配置HTTP到HTTPS重定向
5. 设置自动续期任务

### 2.5 环境变量配置

**必需的环境变量**:
```powershell
[Environment]::SetEnvironmentVariable("DB_PASSWORD", "your_password", "Machine")
[Environment]::SetEnvironmentVariable("SECRET_KEY", "your_secret_key", "Machine")
[Environment]::SetEnvironmentVariable("FLASK_CONFIG", "production", "Machine")
[Environment]::SetEnvironmentVariable("APP_URL", "https://your-domain.com", "Machine")
```

### 2.6 数据库初始化

**执行SQL脚本**:
```sql
-- 使用提供的脚本
source windows_deployment/setup_mysql_windows.sql
```

**或手动创建**:
```sql
CREATE DATABASE software_copyright CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'webuser'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON software_copyright.* TO 'webuser'@'localhost';
FLUSH PRIVILEGES;
```

### 2.7 服务管理

**IIS服务管理**:
```powershell
# 启动IIS服务
Start-Service W3SVC

# 重启应用程序池
Restart-WebAppPool -Name "SoftwareCopyrightAppPool"

# 重启网站
Restart-Website -Name "SoftwareCopyright"
```

**日志查看**:
- IIS访问日志：`C:\inetpub\logs\LogFiles\W3SVC1\`
- 应用程序日志：`C:\inetpub\logs\software_copyright.log`
- Windows事件日志：事件查看器 → Windows日志 → 应用程序

## 三、Desktop应用打包

### 3.1 环境准备

**Windows开发环境**:
- Python 3.8+
- PyInstaller
- Inno Setup 6.0+
- 所有依赖包

### 3.2 打包步骤

1. **安装依赖**:
```bash
pip install -r desktop_requirements.txt
pip install pyinstaller
```

2. **执行打包**:
```bash
build_desktop.bat
```

3. **生成安装包**:
- 自动检测Inno Setup安装
- 生成带安装向导的.exe安装程序
- 包含卸载功能

### 3.3 安装包特性

**Inno Setup安装程序特性**:
- 中文界面支持
- 自动创建开始菜单和桌面快捷方式
- 用户数据目录自动创建
- 卸载时保留用户数据
- 安装前版本检查
- 安装后自动启动程序

**分发方式**:
- 上传到公司内部文件服务器
- 通过企业微信/钉钉分发
- 制作U盘安装介质

### 3.4 配置说明

Desktop应用首次运行时会：
- 自动创建本地SQLite数据库
- 在用户目录下创建`SoftwareCopyrightMS`文件夹
- 提供服务器地址配置界面
- 支持离线工作模式

## 四、运维管理

### 4.1 日志管理

**Linux环境日志位置**:
- Nginx访问日志: `/var/log/nginx/software_copyright_access.log`
- Nginx错误日志: `/var/log/nginx/software_copyright_error.log`
- Gunicorn日志: `/var/log/software_copyright/gunicorn_*.log`
- 应用日志: `/var/www/software_copyright/logs/`

**Windows环境日志位置**:
- IIS访问日志: `C:\inetpub\logs\LogFiles\W3SVC1\`
- IIS错误日志: `C:\inetpub\logs\LogFiles\W3SVC1\`
- 应用程序日志: `C:\inetpub\logs\software_copyright.log`
- Windows事件日志: 事件查看器 → Windows日志 → 应用程序

**查看日志**:
```bash
# Linux环境
sudo tail -f /var/log/software_copyright/gunicorn_error.log
sudo tail -f /var/log/nginx/software_copyright_error.log

# Windows环境
Get-Content "C:\inetpub\logs\software_copyright.log" -Tail 50 -Wait
```

### 4.2 备份策略

**Linux环境自动备份**:
```bash
# 复制备份脚本
sudo cp backup.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/backup.sh

# 设置定时备份
sudo crontab -e
# 添加: 0 2 * * * /usr/local/bin/backup.sh
```

**Windows环境自动备份**:
```powershell
# 创建备份任务
$Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\scripts\backup.ps1"
$Trigger = New-ScheduledTaskTrigger -Daily -At 2AM
Register-ScheduledTask -TaskName "SoftwareCopyright-Backup" -Action $Action -Trigger $Trigger
```

### 4.3 监控告警

**Linux环境监控**:
```bash
# 安装htop
sudo apt install htop -y

# 监控系统资源
htop
```

**Windows环境监控**:
```powershell
# 使用Windows性能监视器
perfmon.exe

# 使用PowerShell监控
Get-Counter "\Processor(_Total)\% Processor Time"
Get-Counter "\Memory\Available MBytes"
```

**可选高级监控**:
- Prometheus + Grafana
- 云服务商监控服务
- 自定义监控脚本

## 五、安全加固

### 5.1 Linux服务器安全

```bash
# 1. 配置防火墙
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# 2. 禁用root SSH登录
sudo sed -i 's/PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# 3. 配置fail2ban防暴力破解
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 5.2 Windows服务器安全

```powershell
# 1. 配置Windows防火墙
New-NetFirewallRule -DisplayName "SSH" -Direction Inbound -Protocol TCP -LocalPort 22 -Action Allow
New-NetFirewallRule -DisplayName "HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow
New-NetFirewallRule -DisplayName "HTTPS" -Direction Inbound -Protocol TCP -LocalPort 443 -Action Allow

# 2. 启用Windows Defender
Set-MpPreference -DisableRealtimeMonitoring $false

# 3. 配置用户权限
# 创建专用服务账户，避免使用管理员权限运行应用
```

### 5.3 应用安全

- 定期更新依赖包
- 使用强密码策略
- 启用HTTPS（SSL/TLS）
- 配置CORS策略
- 定期安全审计
- 敏感信息加密存储

## 六、更新维护

### 6.1 Linux环境Web应用更新

```bash
# 1. 备份当前版本
cd /var/www/software_copyright
sudo tar -czf /var/backups/software_copyright/pre_update_$(date +%Y%m%d).tar.gz .

# 2. 上传新版本代码
scp -r /path/to/new/version root@your-server-ip:/tmp/

# 3. 停止服务
sudo systemctl stop software_copyright

# 4. 更新代码
sudo cp -r /tmp/new/version/* /var/www/software_copyright/

# 5. 更新依赖
sudo /var/www/software_copyright/venv/bin/pip install -r requirements.txt

# 6. 数据库迁移（如有）
sudo -u www-data /var/www/software_copyright/venv/bin/python migrate_script.py

# 7. 重启服务
sudo systemctl start software_copyright
sudo systemctl status software_copyright
```

### 6.2 Windows环境Web应用更新

```powershell
# 1. 备份当前版本
$BackupPath = "C:\backups\software_copyright\pre_update_$(Get-Date -Format 'yyyyMMdd')"
Compress-Archive -Path "C:\inetpub\wwwroot\software_copyright\*" -DestinationPath "$BackupPath.zip"

# 2. 停止IIS应用池
Stop-WebAppPool -Name "SoftwareCopyrightAppPool"

# 3. 更新代码
Copy-Item -Path "C:\temp\new_version\*" -Destination "C:\inetpub\wwwroot\software_copyright\" -Recurse -Force

# 4. 更新依赖
& "C:\inetpub\wwwroot\software_copyright\venv\Scripts\pip.exe" install -r requirements.txt

# 5. 数据库迁移（如有）
& "C:\inetpub\wwwroot\software_copyright\venv\Scripts\python.exe" migrate_script.py

# 6. 重启应用池
Start-WebAppPool -Name "SoftwareCopyrightAppPool"
```

### 6.3 Desktop应用更新

1. 重新打包新版本
2. 通知用户下载更新
3. 提供版本更新说明
4. 可选: 实现自动更新功能

## 七、故障排查

### 7.1 常见问题

**Web应用无法访问**:
- Linux: 检查Nginx状态 `sudo systemctl status nginx`
- Windows: 检查IIS状态 `Get-Service W3SVC`
- 检查应用服务状态
- 查看错误日志

**数据库连接失败**:
- Linux: 检查MySQL状态 `sudo systemctl status mysql`
- Windows: 检查MySQL服务 `Get-Service MySQL`
- 验证数据库凭据
- 检查防火墙规则

**Desktop应用无法连接**:
- 验证服务器地址配置
- 检查网络连接
- 查看API日志
- 检查SSL证书

### 7.2 性能优化

**Web应用优化**:
- 启用Gzip压缩
- 配置静态文件缓存
- 优化数据库查询
- 使用CDN加速
- 配置Redis缓存（可选）

**Desktop应用优化**:
- 减少API调用频率
- 实现本地缓存
- 优化文件操作
- 异步处理长时间任务

## 八、部署检查清单

### 8.1 Linux环境部署检查

- [ ] 服务器基础环境安装完成
- [ ] MySQL数据库创建并配置
- [ ] 应用代码上传并部署
- [ ] Nginx配置并启动
- [ ] Gunicorn服务配置并启动
- [ ] SSL证书安装并配置
- [ ] 防火墙规则配置
- [ ] 备份策略设置
- [ ] 监控工具安装
- [ ] 安全加固完成

### 8.2 Windows环境部署检查

- [ ] Windows Server环境准备完成
- [ ] Python和MySQL安装完成
- [ ] IIS和wfastcgi配置完成
- [ ] 应用代码部署完成
- [ ] 数据库初始化完成
- [ ] SSL证书配置完成
- [ ] 环境变量设置完成
- [ ] 防火墙规则配置完成
- [ ] 备份任务设置完成
- [ ] 监控配置完成

### 8.3 Desktop应用部署检查

- [ ] 开发环境准备完成
- [ ] 依赖包安装完成
- [ ] PyInstaller配置正确
- [ ] Inno Setup安装完成
- [ ] 应用打包成功
- [ ] 安装包测试通过
- [ ] 版本信息配置正确
- [ ] 使用说明文档完整
- [ ] 分发渠道准备就绪
- [ ] 用户培训计划制定

## 九、联系信息

**技术支持**:
- 邮箱: support@company.com
- 电话: XXX-XXXX-XXXX

**紧急联系**:
- 24小时技术支持热线
- 在线工单系统
- 远程协助服务

---

**注意**: 请根据实际环境调整配置参数，确保所有敏感信息（如密码、密钥）使用环境变量或安全的配置文件管理。
