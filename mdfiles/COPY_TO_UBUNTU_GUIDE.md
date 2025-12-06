# 将项目复制到Ubuntu系统的详细指南

## 方法一：使用SCP命令（推荐，适合小到中等项目）

### 在Windows PowerShell中执行

1. **打开PowerShell**（以管理员身份运行，如果需要）

2. **导航到项目目录**
   ```powershell
   cd D:\CursorCode\pyRespository\Software_copyright_MS1.0
   ```

3. **使用SCP命令复制整个项目**
   ```powershell
   # 基本命令格式
   scp -r . ubuntu@your-server-ip:/tmp/software_copyright
   
   # 或者使用root用户
   scp -r . root@your-server-ip:/tmp/software_copyright
   ```

   **参数说明：**
   - `-r`: 递归复制整个目录
   - `.`: 当前目录（项目根目录）
   - `ubuntu@your-server-ip`: Ubuntu系统的用户名和IP地址
   - `/tmp/software_copyright`: 临时目标目录

4. **输入SSH密码**（如果使用密码认证）

5. **等待传输完成**

6. **在Ubuntu服务器上移动文件到目标位置**
   ```bash
   # SSH登录到Ubuntu服务器后执行
   sudo mkdir -p /var/www/software_copyright
   sudo mv /tmp/software_copyright/* /var/www/software_copyright/
   sudo mv /tmp/software_copyright/.* /var/www/software_copyright/ 2>/dev/null || true
   sudo rm -rf /tmp/software_copyright
   ```

### 完整示例

假设您的Ubuntu服务器IP是 `192.168.1.100`，用户名是 `ubuntu`：

```powershell
# 在Windows PowerShell中
cd D:\CursorCode\pyRespository\Software_copyright_MS1.0
scp -r . ubuntu@192.168.1.100:/tmp/software_copyright
```

然后在Ubuntu服务器上：
```bash
ssh ubuntu@192.168.1.100
sudo mkdir -p /var/www/software_copyright
sudo mv /tmp/software_copyright/* /var/www/software_copyright/
sudo chown -R $USER:$USER /var/www/software_copyright
```

---

## 方法二：使用rsync命令（推荐，适合大项目，支持断点续传）

### 在Windows PowerShell中执行

**注意：** Windows 10/11 默认没有 `rsync`，需要先安装。

#### 安装rsync（Windows）

1. **安装WSL（Windows Subsystem for Linux）**（如果未安装）
   ```powershell
   wsl --install
   ```

2. **或者使用Git Bash**（Git for Windows自带rsync）

3. **或者使用Chocolatey安装rsync**
   ```powershell
   choco install rsync
   ```

#### 使用rsync复制

```powershell
# 在PowerShell或Git Bash中
cd D:\CursorCode\pyRespository\Software_copyright_MS1.0

# 使用rsync（排除不必要的文件）
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' --exclude='instance' . ubuntu@your-server-ip:/tmp/software_copyright
```

**参数说明：**
- `-a`: 归档模式（保留权限、时间戳等）
- `-v`: 详细输出
- `-z`: 压缩传输
- `--exclude`: 排除不需要的文件/目录

---

## 方法三：使用SFTP工具（图形界面，最简单）

### 使用FileZilla（推荐）

1. **下载并安装FileZilla**
   - 访问：https://filezilla-project.org/
   - 下载FileZilla Client

2. **连接到Ubuntu服务器**
   - 打开FileZilla
   - 点击"文件" → "站点管理器"
   - 新建站点：
     - 协议：`SFTP - SSH文件传输协议`
     - 主机：`your-server-ip`
     - 端口：`22`
     - 用户名：`ubuntu` 或 `root`
     - 密码：输入SSH密码
     - 点击"连接"

3. **上传文件**
   - 左侧：本地文件（Windows）
   - 右侧：远程文件（Ubuntu）
   - 导航到项目目录：`D:\CursorCode\pyRespository\Software_copyright_MS1.0`
   - 导航到远程目录：`/tmp/software_copyright`（先创建）
   - 选择所有文件和文件夹
   - 右键 → "上传"

4. **在Ubuntu服务器上移动文件**
   ```bash
   sudo mkdir -p /var/www/software_copyright
   sudo mv /tmp/software_copyright/* /var/www/software_copyright/
   sudo chown -R $USER:$USER /var/www/software_copyright
   ```

### 使用WinSCP（另一个选择）

1. 下载WinSCP：https://winscp.net/
2. 连接方式与FileZilla类似

---

## 方法四：使用Git（如果项目在Git仓库中）

### 在Ubuntu服务器上直接克隆

```bash
# SSH登录到Ubuntu服务器
ssh ubuntu@your-server-ip

# 安装Git（如果未安装）
sudo apt update
sudo apt install -y git

# 创建目标目录
sudo mkdir -p /var/www/software_copyright
sudo chown -R $USER:$USER /var/www/software_copyright

# 克隆项目（如果项目在Git仓库中）
cd /var/www/software_copyright
git clone your-repository-url .

# 或者如果已有仓库，直接克隆
git clone your-repository-url /var/www/software_copyright
```

---

## 方法五：使用tar压缩传输（适合大项目）

### 在Windows PowerShell中

```powershell
# 1. 压缩项目（排除不必要的文件）
cd D:\CursorCode\pyRespository
tar -czf software_copyright.tar.gz Software_copyright_MS1.0 --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='.git' --exclude='instance'

# 2. 传输压缩文件
scp software_copyright.tar.gz ubuntu@your-server-ip:/tmp/
```

### 在Ubuntu服务器上

```bash
# 1. 解压文件
cd /tmp
tar -xzf software_copyright.tar.gz

# 2. 移动到目标位置
sudo mkdir -p /var/www/software_copyright
sudo mv Software_copyright_MS1.0/* /var/www/software_copyright/
sudo mv Software_copyright_MS1.0/.* /var/www/software_copyright/ 2>/dev/null || true

# 3. 清理
rm -rf Software_copyright_MS1.0
rm software_copyright.tar.gz
```

---

## 推荐方案（完整步骤）

### 步骤1：在Windows上准备

```powershell
# 打开PowerShell，导航到项目目录
cd D:\CursorCode\pyRespository\Software_copyright_MS1.0

# 检查当前目录内容
dir
```

### 步骤2：使用SCP传输（最简单）

```powershell
# 替换 your-server-ip 为您的Ubuntu服务器IP
# 替换 ubuntu 为您的用户名（可能是 root 或 ubuntu）
scp -r . ubuntu@your-server-ip:/tmp/software_copyright
```

**如果使用SSH密钥：**
```powershell
scp -i C:\path\to\your\private_key -r . ubuntu@your-server-ip:/tmp/software_copyright
```

### 步骤3：在Ubuntu服务器上配置

```bash
# SSH登录到Ubuntu服务器
ssh ubuntu@your-server-ip

# 创建目标目录
sudo mkdir -p /var/www/software_copyright

# 移动文件到目标位置
sudo mv /tmp/software_copyright/* /var/www/software_copyright/

# 移动隐藏文件（.env等）
sudo mv /tmp/software_copyright/.* /var/www/software_copyright/ 2>/dev/null || true

# 设置权限（先设置为当前用户，后续部署时会改为www-data）
sudo chown -R $USER:$USER /var/www/software_copyright

# 验证文件是否复制成功
ls -la /var/www/software_copyright/

# 清理临时文件
sudo rm -rf /tmp/software_copyright
```

---

## 常见问题解决

### 问题1：SCP命令找不到

**解决方案：**
- Windows 10/11 通常内置OpenSSH客户端
- 如果没有，在"设置" → "应用" → "可选功能"中安装OpenSSH客户端
- 或者在PowerShell中运行：`Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0`

### 问题2：权限被拒绝

**解决方案：**
```bash
# 在Ubuntu服务器上检查目录权限
ls -ld /var/www

# 如果/var/www不存在，创建它
sudo mkdir -p /var/www
sudo chown $USER:$USER /var/www
```

### 问题3：传输速度慢

**解决方案：**
- 使用rsync（支持断点续传）
- 先压缩再传输（tar方法）
- 排除不必要的文件（venv、__pycache__等）

### 问题4：SSH连接超时

**解决方案：**
```powershell
# 增加超时时间
scp -o ServerAliveInterval=60 -r . ubuntu@your-server-ip:/tmp/software_copyright
```

---

## 需要排除的文件/目录

传输时建议排除以下内容（减少传输大小和时间）：

- `venv/` - Python虚拟环境（在服务器上重新创建）
- `__pycache__/` - Python缓存文件
- `*.pyc` - Python编译文件
- `.git/` - Git仓库（如果不需要）
- `instance/` - 本地数据库实例
- `*.db` - SQLite数据库文件
- `browser_data/` - 浏览器数据
- `test_output/` - 测试输出

### 使用rsync排除文件示例

```powershell
rsync -avz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  --exclude='instance' \
  --exclude='*.db' \
  --exclude='browser_data' \
  --exclude='test_output' \
  . ubuntu@your-server-ip:/tmp/software_copyright
```

---

## 验证传输结果

在Ubuntu服务器上检查：

```bash
# 检查文件是否完整
cd /var/www/software_copyright
ls -la

# 应该看到以下关键文件和目录：
# - web_app/
# - database/
# - config/
# - templates/
# - static/
# - requirements.txt
# - wsgi.py
# - gunicorn_config.py
# 等等

# 检查文件数量（可选）
find . -type f | wc -l
```

---

## 下一步

文件复制完成后，按照 `UBUNTU_DEPLOYMENT_GUIDE.md` 文档继续部署：

1. 创建Python虚拟环境
2. 安装依赖包
3. 配置环境变量
4. 初始化数据库
5. 配置Nginx和Gunicorn

---

**提示：** 如果传输过程中断，可以重新运行SCP命令，或者使用rsync（支持断点续传）。



