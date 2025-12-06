# IPv6配置指南

## 当前状态检查

### 1. 检查系统IPv6支持

在Ubuntu服务器上执行以下命令检查IPv6支持：

```bash
# 检查IPv6是否启用
ip -6 addr show

# 或者使用
ifconfig | grep inet6

# 检查IPv6路由
ip -6 route show

# 检查内核IPv6模块
lsmod | grep ipv6
```

**如果看到IPv6地址（如 `2001:db8::1` 或 `fe80::...`），说明系统支持IPv6。**

### 2. 检查当前应用配置

根据项目代码分析：

- ✅ **开发环境** (`run_web.py`): 已配置 `host='::'`，支持IPv6
- ❌ **生产环境** (`gunicorn_config.py`): 只配置了 `127.0.0.1:8000`，仅支持IPv4
- ❌ **Nginx配置**: 没有IPv6监听配置

---

## 当前配置状态

### 开发环境（run_web.py）
```python
app.run(
    host='::',  # ✅ 已支持IPv6（:: 表示监听所有IPv6接口）
    port=5000,
    debug=True,
    threaded=True
)
```

### 生产环境（gunicorn_config.py）
```python
bind = '127.0.0.1:8000'  # ❌ 仅支持IPv4本地地址
```

### Nginx配置
```nginx
server {
    listen 80;  # ❌ 仅监听IPv4
    listen 443 ssl http2;  # ❌ 仅监听IPv4
    ...
}
```

---

## 启用IPv6访问的完整配置

### 步骤1：确认系统IPv6支持

```bash
# 检查IPv6是否启用
cat /proc/sys/net/ipv6/conf/all/disable_ipv6
# 输出应该是 0（0表示启用，1表示禁用）

# 如果输出是1，启用IPv6
sudo sysctl -w net.ipv6.conf.all.disable_ipv6=0
sudo sysctl -w net.ipv6.conf.default.disable_ipv6=0

# 永久启用（编辑配置文件）
sudo nano /etc/sysctl.conf
# 确保以下行存在且未被注释：
# net.ipv6.conf.all.disable_ipv6 = 0
# net.ipv6.conf.default.disable_ipv6 = 0

# 应用配置
sudo sysctl -p
```

### 步骤2：检查网络接口IPv6地址

```bash
# 查看所有网络接口的IPv6地址
ip -6 addr show

# 查看特定接口（如eth0）
ip -6 addr show eth0

# 如果没有IPv6地址，需要配置
# 方法取决于您的网络环境（静态配置或DHCPv6）
```

### 步骤3：配置Gunicorn支持IPv6

编辑 `gunicorn_config.py`：

```python
import multiprocessing

# 服务器socket - 支持IPv4和IPv6
# 方法1：同时监听IPv4和IPv6（推荐）
bind = ['127.0.0.1:8000', '[::1]:8000']  # 本地IPv4和IPv6

# 方法2：监听所有接口（包括IPv4和IPv6）
# bind = '0.0.0.0:8000'  # 仅IPv4
# bind = '[::]:8000'     # 仅IPv6
# 注意：Gunicorn不支持同时绑定IPv4和IPv6，需要分别配置

# 方法3：使用通配符（如果Gunicorn版本支持）
# bind = '[::]:8000'  # 监听所有IPv6接口，通常也会监听IPv4（双栈模式）

backlog = 2048

# Worker进程
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# 日志
accesslog = '/var/log/software_copyright/gunicorn_access.log'
errorlog = '/var/log/software_copyright/gunicorn_error.log'
loglevel = 'info'

# 进程命名
proc_name = 'software_copyright_web'

# 守护进程
daemon = False

# 环境变量
raw_env = [
    'FLASK_CONFIG=production',
]
```

**注意：** Gunicorn的 `bind` 参数一次只能绑定一个地址。如果需要同时支持IPv4和IPv6，有几种方案：

#### 方案A：使用systemd socket（推荐）

创建systemd socket单元来监听IPv4和IPv6：

```bash
# 创建socket配置文件
sudo nano /etc/systemd/system/software_copyright.socket
```

内容：
```ini
[Unit]
Description=Software Copyright Management System Socket

[Socket]
ListenStream=127.0.0.1:8000
ListenStream=[::1]:8000
# 或者监听所有接口
# ListenStream=0.0.0.0:8000
# ListenStream=[::]:8000

[Install]
WantedBy=sockets.target
```

然后修改service文件：
```ini
[Unit]
Description=Software Copyright Management System
After=network.target mysql.service software_copyright.socket
Requires=software_copyright.socket

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/software_copyright
Environment="PATH=/var/www/software_copyright/venv/bin"
EnvironmentFile=/var/www/software_copyright/.env
ExecStart=/var/www/software_copyright/venv/bin/gunicorn --fd 3 -c gunicorn_config.py wsgi:app
ExecReload=/bin/kill -s HUP $MAINPID
StandardInput=null
StandardOutput=journal
StandardError=journal
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 方案B：修改gunicorn_config.py使用IPv6（简单）

```python
# 监听所有IPv6接口（通常也支持IPv4双栈）
bind = '[::]:8000'
```

### 步骤4：配置Nginx支持IPv6

编辑Nginx配置文件：

```bash
sudo nano /etc/nginx/sites-available/software_copyright.conf
```

更新配置：

```nginx
upstream software_copyright_app {
    server 127.0.0.1:8000 fail_timeout=0;
    # 如果Gunicorn也监听IPv6，可以添加：
    # server [::1]:8000 fail_timeout=0;
}

# HTTP服务器 - IPv4和IPv6
server {
    listen 80;
    listen [::]:80;  # IPv6监听
    server_name your-domain.com www.your-domain.com;
    
    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS服务器 - IPv4和IPv6
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;  # IPv6监听
    server_name your-domain.com www.your-domain.com;
    
    # SSL证书配置
    ssl_certificate /etc/nginx/ssl/your-domain.crt;
    ssl_certificate_key /etc/nginx/ssl/your-domain.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # 日志
    access_log /var/log/nginx/software_copyright_access.log;
    error_log /var/log/nginx/software_copyright_error.log;
    
    # 静态文件
    location /static {
        alias /var/www/software_copyright/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # 上传文件
    location /uploads {
        alias /var/www/software_copyright/uploads;
        internal;
    }
    
    # 应用代理
    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://software_copyright_app;
        
        # 超时设置
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # 文件上传大小限制
    client_max_body_size 20M;
}
```

### 步骤5：配置防火墙支持IPv6

```bash
# 检查UFW IPv6支持
sudo ufw status verbose

# 允许IPv6 HTTP和HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
# UFW默认同时配置IPv4和IPv6

# 如果使用iptables，需要单独配置IPv6
sudo ip6tables -A INPUT -p tcp --dport 80 -j ACCEPT
sudo ip6tables -A INPUT -p tcp --dport 443 -j ACCEPT
```

### 步骤6：测试IPv6连接

```bash
# 测试本地IPv6连接
curl -6 http://[::1]:8000
# 或
curl -6 http://localhost:8000

# 测试公网IPv6（如果有）
curl -6 http://[your-ipv6-address]:8000

# 测试Nginx IPv6
curl -6 http://[your-ipv6-address]
curl -6 https://[your-ipv6-address]
```

### 步骤7：重启服务

```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 重启服务
sudo systemctl restart software_copyright
sudo systemctl restart nginx

# 检查服务状态
sudo systemctl status software_copyright
sudo systemctl status nginx

# 检查端口监听
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp6 | grep :8000  # IPv6端口
sudo ss -tlnp | grep :8000
sudo ss -tlnp6 | grep :8000  # IPv6端口
```

---

## 验证IPv6配置

### 1. 检查端口监听

```bash
# 检查IPv4端口
sudo ss -tlnp | grep :8000
# 应该看到: LISTEN 0 2048 127.0.0.1:8000

# 检查IPv6端口
sudo ss -tlnp6 | grep :8000
# 应该看到: LISTEN 0 2048 [::1]:8000 或 [::]:8000

# 检查Nginx IPv6监听
sudo ss -tlnp6 | grep :80
sudo ss -tlnp6 | grep :443
```

### 2. 测试连接

```bash
# 测试Gunicorn IPv6
curl -v http://[::1]:8000

# 测试Nginx IPv6
curl -v http://[::1]
curl -v https://[::1]
```

### 3. 在线IPv6测试工具

访问以下网站测试您的IPv6配置：
- https://ipv6-test.com/
- https://test-ipv6.com/
- https://www.whatismyip.com/ipv6-test/

---

## 常见问题

### Q1: Gunicorn报错 "Address already in use"

**原因：** 端口已被占用或配置冲突

**解决：**
```bash
# 检查端口占用
sudo lsof -i :8000
sudo ss -tlnp | grep :8000

# 停止冲突的服务
sudo systemctl stop software_copyright
# 或杀死占用端口的进程
sudo kill -9 <PID>
```

### Q2: IPv6地址格式错误

**正确格式：**
- IPv6地址必须用方括号括起来：`[::1]`、`[2001:db8::1]`
- 端口在方括号外：`[::1]:8000`

**错误示例：**
```python
bind = '::1:8000'  # ❌ 错误
bind = '[::1]8000'  # ❌ 错误
```

**正确示例：**
```python
bind = '[::1]:8000'  # ✅ 正确
bind = '[::]:8000'   # ✅ 正确（监听所有IPv6接口）
```

### Q3: Nginx无法启动

**检查配置语法：**
```bash
sudo nginx -t
```

**查看错误日志：**
```bash
sudo tail -f /var/log/nginx/error.log
```

### Q4: 系统不支持IPv6

**检查内核支持：**
```bash
# 检查IPv6模块
lsmod | grep ipv6

# 如果没有，加载模块
sudo modprobe ipv6

# 永久启用
echo "ipv6" | sudo tee -a /etc/modules
```

### Q5: 云服务器没有IPv6地址

**解决方案：**
1. 联系云服务商申请IPv6支持
2. 配置IPv6地址（通常通过控制台或API）
3. 确保安全组/防火墙规则允许IPv6流量

---

## 推荐配置方案

### 方案1：仅IPv4（当前配置，最简单）

如果不需要IPv6，保持当前配置即可：
- Gunicorn: `bind = '127.0.0.1:8000'`
- Nginx: `listen 80;` 和 `listen 443 ssl http2;`

### 方案2：IPv4 + IPv6双栈（推荐）

同时支持IPv4和IPv6访问：
- Gunicorn: `bind = '[::]:8000'`（监听所有接口，包括IPv4和IPv6）
- Nginx: 添加 `listen [::]:80;` 和 `listen [::]:443 ssl http2;`

### 方案3：仅IPv6（不推荐）

仅支持IPv6访问（会失去IPv4用户）：
- Gunicorn: `bind = '[::]:8000'`
- Nginx: 只配置IPv6监听

---

## 快速启用IPv6（最简单方法）

如果您想快速启用IPv6支持，执行以下步骤：

```bash
# 1. 修改Gunicorn配置
cd /var/www/software_copyright
sudo nano gunicorn_config.py
# 将 bind = '127.0.0.1:8000' 改为：
# bind = '[::]:8000'

# 2. 修改Nginx配置
sudo nano /etc/nginx/sites-available/software_copyright.conf
# 在 listen 80; 后添加：listen [::]:80;
# 在 listen 443 ssl http2; 后添加：listen [::]:443 ssl http2;

# 3. 测试Nginx配置
sudo nginx -t

# 4. 重启服务
sudo systemctl restart software_copyright
sudo systemctl restart nginx

# 5. 验证
sudo ss -tlnp6 | grep -E ':(80|443|8000)'
```

---

## 总结

**当前状态：**
- ✅ 开发环境已支持IPv6（`run_web.py` 使用 `host='::'`）
- ❌ 生产环境（Gunicorn）仅支持IPv4
- ❌ Nginx未配置IPv6监听

**启用IPv6需要：**
1. 确认系统支持IPv6
2. 修改 `gunicorn_config.py` 的 `bind` 参数
3. 在Nginx配置中添加IPv6监听
4. 配置防火墙允许IPv6流量
5. 重启服务并验证

**建议：** 如果您的服务器有IPv6地址且需要支持IPv6访问，使用方案2（双栈配置）。如果只有IPv4，保持当前配置即可。



