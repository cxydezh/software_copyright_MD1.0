# Windows系统IPv6配置指南

## 当前状态检查

### 快速检查

在PowerShell中运行检查脚本：

```powershell
# 以管理员身份运行PowerShell
.\check_ipv6_windows.ps1
```

### 手动检查

```powershell
# 1. 检查IPv6是否启用
Get-NetAdapterBinding -ComponentID ms_tcpip6 | Where-Object { $_.Enabled -eq $true }

# 2. 检查IPv6地址
Get-NetIPAddress -AddressFamily IPv6 | Where-Object { $_.AddressState -eq 'Preferred' }

# 3. 检查端口监听
Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -in @(80, 443, 5000, 8000) }
```

---

## 当前配置状态

### 开发环境
- ✅ **run_web.py**: 已配置 `host='::'`，支持IPv6
- ⚠️ **web_app/app.py**: 配置 `host='0.0.0.0'`，仅IPv4

### 生产环境
- ❌ **start_production_server.py**: 配置 `host='0.0.0.0'`，仅IPv4
- ❌ **windows_service.py**: 配置 `host='127.0.0.1'`，仅IPv4本地

---

## 启用IPv6访问的完整配置

### 步骤1：启用Windows IPv6支持

#### 方法1：通过图形界面（推荐）

1. 打开"网络和共享中心"
   - 右键点击任务栏网络图标 → "打开网络和 Internet 设置"
   - 或：控制面板 → 网络和 Internet → 网络和共享中心

2. 更改适配器设置
   - 点击"更改适配器设置"

3. 配置网络适配器
   - 右键点击您的网络适配器（如"以太网"或"WLAN"）
   - 选择"属性"
   - 勾选"Internet协议版本6(TCP/IPv6)"
   - 点击"确定"

#### 方法2：通过PowerShell（管理员权限）

```powershell
# 启用IPv6（需要管理员权限）
Enable-NetAdapterBinding -Name "以太网" -ComponentID ms_tcpip6

# 或者对所有适配器启用
Get-NetAdapter | Enable-NetAdapterBinding -ComponentID ms_tcpip6
```

#### 方法3：通过注册表（高级用户）

```powershell
# 警告：修改注册表有风险，请谨慎操作
# 启用IPv6
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters" -Name "DisabledComponents" -Value 0
```

### 步骤2：配置IPv6地址

#### 自动获取（DHCPv6）

如果网络支持DHCPv6，IPv6地址会自动获取：

```powershell
# 检查是否已获取IPv6地址
Get-NetIPAddress -AddressFamily IPv6 | Where-Object { $_.AddressState -eq 'Preferred' }
```

#### 手动配置（静态地址）

```powershell
# 配置静态IPv6地址（需要管理员权限）
New-NetIPAddress -InterfaceAlias "以太网" `
    -AddressFamily IPv6 `
    -IPAddress "2001:db8::1" `
    -PrefixLength 64 `
    -DefaultGateway "2001:db8::1"

# 配置IPv6 DNS
Set-DnsClientServerAddress -InterfaceAlias "以太网" `
    -ServerAddresses "2001:4860:4860::8888","2001:4860:4860::8844"
```

### 步骤3：修改应用配置支持IPv6

#### 修改 start_production_server.py

```python
# 原配置
serve(
    app,
    host='0.0.0.0',  # 仅IPv4
    port=5000,
    ...
)

# 修改为支持IPv6
serve(
    app,
    host='::',  # 监听所有IPv6接口（通常也支持IPv4双栈）
    port=5000,
    ...
)
```

#### 修改 windows_service.py

```python
# 原配置
self.server = serve(
    self.app,
    host='127.0.0.1',  # 仅IPv4本地
    port=5000,
    ...
)

# 修改为支持IPv6
self.server = serve(
    self.app,
    host='::',  # 监听所有接口
    port=5000,
    ...
)
```

#### 修改 web_app/app.py（可选）

```python
# 原配置
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

# 修改为支持IPv6
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='::', port=5000)
```

### 步骤4：配置Windows防火墙

#### 方法1：通过图形界面

1. 打开"Windows Defender 防火墙"
   - 控制面板 → 系统和安全 → Windows Defender 防火墙

2. 高级设置
   - 点击"高级设置"

3. 添加入站规则
   - 点击"入站规则" → "新建规则"
   - 选择"端口" → 下一步
   - 选择"TCP"，输入端口（如5000）→ 下一步
   - 选择"允许连接" → 下一步
   - 勾选所有配置文件 → 下一步
   - 输入规则名称（如"软件著作权系统IPv6"）→ 完成

#### 方法2：通过PowerShell（管理员权限）

```powershell
# 允许IPv6端口5000
New-NetFirewallRule -DisplayName "软件著作权系统IPv6" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 5000 `
    -Action Allow `
    -Enabled True

# 允许IPv6 HTTP和HTTPS（如果使用）
New-NetFirewallRule -DisplayName "HTTP IPv6" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 80 `
    -Action Allow `
    -Enabled True

New-NetFirewallRule -DisplayName "HTTPS IPv6" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 443 `
    -Action Allow `
    -Enabled True
```

### 步骤5：配置IIS支持IPv6（如果使用IIS）

#### 方法1：通过IIS管理器

1. 打开IIS管理器
2. 选择您的网站
3. 点击"绑定"
4. 编辑现有绑定或添加新绑定
5. 在"IP地址"下拉菜单中选择IPv6地址或"全部未分配"
6. 点击"确定"

#### 方法2：通过PowerShell

```powershell
# 获取网站
$site = Get-Website -Name "SoftwareCopyright"

# 添加IPv6绑定
New-WebBinding -Name "SoftwareCopyright" `
    -Protocol http `
    -IPAddress "*" `
    -Port 80

New-WebBinding -Name "SoftwareCopyright" `
    -Protocol https `
    -IPAddress "*" `
    -Port 443
```

### 步骤6：测试IPv6连接

```powershell
# 测试本地IPv6连接
Test-NetConnection -ComputerName "::1" -Port 5000

# 使用curl测试（如果安装了curl）
curl http://[::1]:5000

# 测试IPv6地址（如果有）
curl http://[your-ipv6-address]:5000
```

---

## 快速启用IPv6（最简单方法）

如果您想快速启用IPv6支持，执行以下步骤：

### 1. 启用系统IPv6

```powershell
# 以管理员身份运行PowerShell
Get-NetAdapter | Enable-NetAdapterBinding -ComponentID ms_tcpip6
```

### 2. 修改应用配置

编辑以下文件，将 `host='0.0.0.0'` 或 `host='127.0.0.1'` 改为 `host='::'`：

- `start_production_server.py`
- `windows_service.py`
- `web_app/app.py`（可选）

### 3. 配置防火墙

```powershell
# 以管理员身份运行
New-NetFirewallRule -DisplayName "软件著作权系统IPv6" `
    -Direction Inbound -Protocol TCP -LocalPort 5000 -Action Allow
```

### 4. 重启应用

重启您的应用服务。

### 5. 验证

```powershell
# 检查端口监听
Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -eq 5000 }

# 测试连接
Test-NetConnection -ComputerName "::1" -Port 5000
```

---

## 验证IPv6配置

### 1. 检查端口监听

```powershell
# 检查IPv6端口监听
Get-NetTCPConnection -State Listen | Where-Object { 
    $_.LocalPort -in @(80, 443, 5000, 8000) -and 
    ($_.LocalAddress -like '*::*' -or $_.LocalAddress -eq '::')
}
```

### 2. 测试连接

```powershell
# 测试本地IPv6
Test-NetConnection -ComputerName "::1" -Port 5000

# 使用浏览器测试
# 访问: http://[::1]:5000
```

### 3. 在线IPv6测试工具

访问以下网站测试您的IPv6配置：
- https://ipv6-test.com/
- https://test-ipv6.com/
- https://www.whatismyip.com/ipv6-test/

---

## 常见问题

### Q1: Waitress不支持IPv6？

**Waitress实际上支持IPv6**，使用 `host='::'` 即可。如果遇到问题，可能是：
- 系统IPv6未启用
- 防火墙阻止
- 端口被占用

### Q2: 如何同时支持IPv4和IPv6？

使用 `host='::'` 通常会自动启用双栈模式（同时支持IPv4和IPv6）。

### Q3: IPv6地址格式错误

**正确格式：**
- Python中：`host='::'` 或 `host='[::1]'`
- URL中：`http://[::1]:5000`（IPv6地址必须用方括号）

### Q4: 无法连接到IPv6地址

**检查步骤：**
1. 确认IPv6已启用
2. 检查防火墙规则
3. 确认应用正在监听IPv6
4. 检查网络配置

### Q5: 云服务器没有IPv6地址

**解决方案：**
1. 联系云服务商申请IPv6支持
2. 在云控制台配置IPv6地址
3. 确保安全组规则允许IPv6流量

---

## 推荐配置方案

### 方案1：仅IPv4（当前配置，最简单）

如果不需要IPv6，保持当前配置即可：
- `host='0.0.0.0'` 或 `host='127.0.0.1'`

### 方案2：IPv4 + IPv6双栈（推荐）

同时支持IPv4和IPv6访问：
- `host='::'`（监听所有接口，包括IPv4和IPv6）

### 方案3：仅IPv6（不推荐）

仅支持IPv6访问（会失去IPv4用户）：
- `host='::'` 且禁用IPv4（不推荐）

---

## 总结

**当前状态：**
- ✅ 开发环境（`run_web.py`）已支持IPv6
- ❌ 生产环境（`start_production_server.py`、`windows_service.py`）仅支持IPv4

**启用IPv6需要：**
1. 启用Windows IPv6支持
2. 修改应用配置中的 `host` 参数为 `'::'`
3. 配置防火墙允许IPv6流量
4. 如果使用IIS，配置IPv6绑定
5. 重启应用并验证

**建议：** 如果您的网络环境支持IPv6且需要提供IPv6访问，使用方案2（双栈配置）。如果只有IPv4或不需要IPv6，保持当前配置即可。

---

## 相关文件

- `check_ipv6_windows.ps1` - Windows IPv6检查脚本
- `mdfiles/IPV6_CONFIGURATION_GUIDE.md` - Linux IPv6配置指南









