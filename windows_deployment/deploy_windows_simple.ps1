# 软著管理系统 - Windows Server 简化部署脚本
# 避免复杂语法，确保兼容性

param(
    [string]$ServerIP = "",
    [string]$DbPassword = "SoftwareCopyright2024!"
)

Write-Host "==========================================" -ForegroundColor Green
Write-Host "软著管理系统 - Windows Server 部署" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# 检查管理员权限
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-NOT $isAdmin) {
    Write-Error "请以管理员身份运行此脚本！"
    exit 1
}

# 自动获取服务器IP
if ($ServerIP -eq "") {
    $ipAddresses = Get-NetIPAddress -AddressFamily IPv4
    foreach ($ip in $ipAddresses) {
        if ($ip.IPAddress -notlike "127.*" -and $ip.IPAddress -notlike "169.254.*") {
            $ServerIP = $ip.IPAddress
            break
        }
    }
    Write-Host "自动检测到服务器IP: $ServerIP" -ForegroundColor Yellow
}

# 1. 创建部署目录
Write-Host "`n[1/8] 创建部署目录..." -ForegroundColor Yellow
$DeployPath = "C:\inetpub\wwwroot\software_copyright"
$LogPath = "C:\inetpub\logs"

if (!(Test-Path $DeployPath)) {
    New-Item -ItemType Directory -Path $DeployPath -Force
    Write-Host "创建部署目录: $DeployPath" -ForegroundColor Green
}

if (!(Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath -Force
    Write-Host "创建日志目录: $LogPath" -ForegroundColor Green
}

# 2. 复制项目文件
Write-Host "`n[2/8] 复制项目文件..." -ForegroundColor Yellow
$SourcePath = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $SourcePath

# 简单的文件复制
$ExcludeDirs = @("__pycache__", ".git", "tests", "instance", "browser_data", "test_output")
Get-ChildItem -Path $ProjectRoot -Recurse | ForEach-Object {
    $item = $_
    $shouldExclude = $false
    
    foreach ($dir in $ExcludeDirs) {
        if ($item.FullName -like "*\$dir\*" -or $item.Name -eq $dir) {
            $shouldExclude = $true
            break
        }
    }
    
    if (-NOT $shouldExclude) {
        $destPath = $item.FullName.Replace($ProjectRoot, $DeployPath)
        $destDir = Split-Path -Parent $destPath
        if (!(Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force
        }
        Copy-Item -Path $item.FullName -Destination $destPath -Force
    }
}

Write-Host "项目文件复制完成" -ForegroundColor Green

# 3. 创建Python虚拟环境
Write-Host "`n[3/8] 创建Python虚拟环境..." -ForegroundColor Yellow
$VenvPath = "$DeployPath\venv"
if (!(Test-Path $VenvPath)) {
    python -m venv $VenvPath
    Write-Host "虚拟环境创建完成: $VenvPath" -ForegroundColor Green
}

# 激活虚拟环境并安装依赖
$ActivateScript = "$VenvPath\Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
    pip install --upgrade pip
    pip install -r "$DeployPath\requirements.txt"
    pip install wfastcgi
    Write-Host "依赖包安装完成" -ForegroundColor Green
}

# 4. 配置wfastcgi
Write-Host "`n[4/8] 配置wfastcgi..." -ForegroundColor Yellow
& "$VenvPath\Scripts\wfastcgi-enable.exe"
Write-Host "wfastcgi配置完成" -ForegroundColor Green

# 5. 初始化数据库
Write-Host "`n[5/8] 初始化数据库..." -ForegroundColor Yellow
if ($DbPassword -ne "") {
    $env:DB_PASSWORD = $DbPassword
    $env:FLASK_CONFIG = "production"
    
    & "$VenvPath\Scripts\python.exe" "$DeployPath\init_mysql.py"
    Write-Host "数据库初始化完成" -ForegroundColor Green
}

# 6. 配置IIS站点
Write-Host "`n[6/8] 配置IIS站点..." -ForegroundColor Yellow

# 启用IIS功能
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole, IIS-WebServer, IIS-CommonHttpFeatures, IIS-HttpErrors, IIS-HttpLogging, IIS-RequestFiltering, IIS-StaticContent, IIS-DefaultDocument, IIS-DirectoryBrowsing, IIS-ASPNET45, IIS-NetFxExtensibility45, IIS-ISAPIExtensions, IIS-ISAPIFilter, IIS-CGI

# 导入IIS模块
Import-Module WebAdministration

# 创建应用程序池
$AppPoolName = "SoftwareCopyrightAppPool"
$existingPool = Get-IISAppPool -Name $AppPoolName -ErrorAction SilentlyContinue
if (-NOT $existingPool) {
    New-WebAppPool -Name $AppPoolName
    Set-ItemProperty -Path "IIS:\AppPools\$AppPoolName" -Name processModel.identityType -Value ApplicationPoolIdentity
    Set-ItemProperty -Path "IIS:\AppPools\$AppPoolName" -Name managedRuntimeVersion -Value ""
    Write-Host "应用程序池创建完成: $AppPoolName" -ForegroundColor Green
}

# 创建网站
$SiteName = "SoftwareCopyright"
$existingSite = Get-Website -Name $SiteName -ErrorAction SilentlyContinue
if (-NOT $existingSite) {
    New-Website -Name $SiteName -Port 80 -PhysicalPath $DeployPath -ApplicationPool $AppPoolName
    Write-Host "网站创建完成: $SiteName" -ForegroundColor Green
}

# 7. 设置文件权限
Write-Host "`n[7/8] 设置文件权限..." -ForegroundColor Yellow
$IISUser = "IIS_IUSRS"
$AppPoolUser = "IIS AppPool\$AppPoolName"

icacls $DeployPath /grant "${IISUser}:(OI)(CI)F" /T
icacls $LogPath /grant "${IISUser}:(OI)(CI)F" /T
icacls $DeployPath /grant "${AppPoolUser}:(OI)(CI)F" /T
icacls $LogPath /grant "${AppPoolUser}:(OI)(CI)F" /T

Write-Host "文件权限设置完成" -ForegroundColor Green

# 8. 配置防火墙规则
Write-Host "`n[8/8] 配置防火墙规则..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "Software Copyright HTTP" -Direction Inbound -Protocol TCP -LocalPort 80 -Action Allow -ErrorAction SilentlyContinue
Write-Host "防火墙规则配置完成" -ForegroundColor Green

# 设置环境变量
Write-Host "`n设置环境变量..." -ForegroundColor Yellow
[Environment]::SetEnvironmentVariable("DB_PASSWORD", $DbPassword, "Machine")
[Environment]::SetEnvironmentVariable("FLASK_CONFIG", "production", "Machine")
$AppURL = "http://$ServerIP"
[Environment]::SetEnvironmentVariable("APP_URL", $AppURL, "Machine")
Write-Host "环境变量设置完成" -ForegroundColor Green

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "部署完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "访问地址: $AppURL" -ForegroundColor Cyan
Write-Host "管理地址: $AppURL/staff/login" -ForegroundColor Cyan
Write-Host "默认管理员: admin@yiqichuang.com / admin123" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Green

# 启动IIS服务
Write-Host "`n启动IIS服务..." -ForegroundColor Yellow
Start-Service W3SVC
Write-Host "IIS服务已启动" -ForegroundColor Green

Write-Host "`n注意：当前使用HTTP协议" -ForegroundColor Yellow
Write-Host "如需HTTPS，请联系管理员配置SSL证书" -ForegroundColor Yellow





