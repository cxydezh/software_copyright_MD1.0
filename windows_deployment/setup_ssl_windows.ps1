# 软著管理系统 - Windows Server SSL证书配置脚本
# 使用 win-acme 工具自动获取和配置 Let's Encrypt SSL证书

param(
    [Parameter(Mandatory=$true)]
    [string]$DomainName,
    
    [string]$Email = "admin@your-domain.com",
    
    [string]$WebRoot = "C:\inetpub\wwwroot\software_copyright",
    
    [switch]$Force = $false
)

Write-Host "==========================================" -ForegroundColor Green
Write-Host "软著管理系统 - SSL证书配置脚本" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# 检查管理员权限
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Error "请以管理员身份运行此脚本！"
    exit 1
}

# 检查域名解析
Write-Host "`n检查域名解析..." -ForegroundColor Yellow
try {
    $DnsResult = Resolve-DnsName -Name $DomainName -ErrorAction Stop
    Write-Host "域名解析正常: $DomainName" -ForegroundColor Green
} catch {
    Write-Error "域名解析失败: $DomainName，请检查DNS配置"
    exit 1
}

# 下载 win-acme 工具
Write-Host "`n下载 win-acme 工具..." -ForegroundColor Yellow
$WinAcmePath = "C:\win-acme"
$WinAcmeExe = "$WinAcmePath\wacs.exe"

if (!(Test-Path $WinAcmeExe) -or $Force) {
    if (!(Test-Path $WinAcmePath)) {
        New-Item -ItemType Directory -Path $WinAcmePath -Force
    }
    
    # 下载最新版本
    $DownloadUrl = "https://github.com/win-acme/win-acme/releases/latest/download/win-acme.v2.2.16.1471.x64.pluggable.zip"
    $ZipFile = "$WinAcmePath\win-acme.zip"
    
    try {
        Invoke-WebRequest -Uri $DownloadUrl -OutFile $ZipFile -UseBasicParsing
        Expand-Archive -Path $ZipFile -DestinationPath $WinAcmePath -Force
        Remove-Item $ZipFile -Force
        Write-Host "win-acme 工具下载完成" -ForegroundColor Green
    } catch {
        Write-Error "下载 win-acme 工具失败: $($_.Exception.Message)"
        exit 1
    }
}

# 配置 win-acme
Write-Host "`n配置 win-acme..." -ForegroundColor Yellow

# 设置默认配置
$ConfigArgs = @(
    "--source", "iis",
    "--siteid", "1",
    "--commonname", $DomainName,
    "--emailaddress", $Email,
    "--accepttos",
    "--installation", "iis",
    "--store", "certificatestore",
    "--validation", "http-01",
    "--validationmode", "http-01",
    "--webroot", $WebRoot,
    "--script", "C:\win-acme\Scripts\Import-Pfx.ps1",
    "--scriptparameters", "`"C:\ProgramData\win-acme\httpsacme-v02.api.letsencrypt.org\$DomainName\$DomainName.pfx`"",
    "--script", "C:\win-acme\Scripts\Update-IIS.ps1",
    "--scriptparameters", "`"$DomainName`""
)

# 执行证书申请
Write-Host "`n申请SSL证书..." -ForegroundColor Yellow
try {
    & $WinAcmeExe @ConfigArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "SSL证书申请成功！" -ForegroundColor Green
    } else {
        Write-Error "SSL证书申请失败"
        exit 1
    }
} catch {
    Write-Error "执行证书申请时出错: $($_.Exception.Message)"
    exit 1
}

# 配置IIS HTTPS绑定
Write-Host "`n配置IIS HTTPS绑定..." -ForegroundColor Yellow
Import-Module WebAdministration

$SiteName = "SoftwareCopyright"
$CertThumbprint = ""

# 获取证书指纹
try {
    $Cert = Get-ChildItem -Path "Cert:\LocalMachine\My" | Where-Object { $_.Subject -like "*$DomainName*" } | Sort-Object NotAfter -Descending | Select-Object -First 1
    if ($Cert) {
        $CertThumbprint = $Cert.Thumbprint
        Write-Host "找到证书: $($Cert.Subject)" -ForegroundColor Green
    } else {
        Write-Error "未找到域名证书"
        exit 1
    }
} catch {
    Write-Error "获取证书信息失败: $($_.Exception.Message)"
    exit 1
}

# 添加HTTPS绑定
try {
    $Binding = Get-WebBinding -Name $SiteName -Protocol "https" -ErrorAction SilentlyContinue
    if ($Binding) {
        Remove-WebBinding -Name $SiteName -Protocol "https" -Port 443
    }
    
    New-WebBinding -Name $SiteName -Protocol "https" -Port 443 -SslFlags 1
    $Binding = Get-WebBinding -Name $SiteName -Protocol "https"
    $Binding.AddSslCertificate($CertThumbprint, "my")
    
    Write-Host "HTTPS绑定配置完成" -ForegroundColor Green
} catch {
    Write-Error "配置HTTPS绑定失败: $($_.Exception.Message)"
    exit 1
}

# 配置HTTP到HTTPS重定向
Write-Host "`n配置HTTP到HTTPS重定向..." -ForegroundColor Yellow
try {
    # 安装URL重写模块（如果未安装）
    $RewriteModule = Get-WindowsFeature -Name IIS-HttpRedirect
    if ($RewriteModule.InstallState -ne "Installed") {
        Enable-WindowsOptionalFeature -Online -FeatureName IIS-HttpRedirect
    }
    
    # 配置重定向规则
    $WebConfigPath = "$WebRoot\web.config"
    if (Test-Path $WebConfigPath) {
        # 备份原配置
        Copy-Item $WebConfigPath "$WebConfigPath.backup" -Force
        
        # 读取并修改web.config
        [xml]$WebConfig = Get-Content $WebConfigPath
        
        # 添加重定向规则
        $RewriteNode = $WebConfig.configuration.'system.webServer'.rewrite
        if ($RewriteNode) {
            $Rule = $WebConfig.CreateElement("rule")
            $Rule.SetAttribute("name", "HTTP to HTTPS redirect")
            $Rule.SetAttribute("stopProcessing", "true")
            
            $Match = $WebConfig.CreateElement("match")
            $Match.SetAttribute("url", "(.*)")
            $Rule.AppendChild($Match)
            
            $Conditions = $WebConfig.CreateElement("conditions")
            $Add = $WebConfig.CreateElement("add")
            $Add.SetAttribute("input", "{HTTPS}")
            $Add.SetAttribute("pattern", "off")
            $Add.SetAttribute("ignoreCase", "true")
            $Conditions.AppendChild($Add)
            $Rule.AppendChild($Conditions)
            
            $Action = $WebConfig.CreateElement("action")
            $Action.SetAttribute("type", "Redirect")
            $Action.SetAttribute("url", "https://{HTTP_HOST}/{R:1}")
            $Action.SetAttribute("redirectType", "Permanent")
            $Rule.AppendChild($Action)
            
            $RewriteNode.rules.AppendChild($Rule)
            
            $WebConfig.Save($WebConfigPath)
            Write-Host "HTTP到HTTPS重定向配置完成" -ForegroundColor Green
        }
    }
} catch {
    Write-Error "配置重定向规则失败: $($_.Exception.Message)"
}

# 设置自动续期
Write-Host "`n设置自动续期..." -ForegroundColor Yellow
try {
    $TaskName = "WinAcme-Renewal"
    $TaskExists = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    
    if (!$TaskExists) {
        $Action = New-ScheduledTaskAction -Execute $WinAcmeExe -Argument "--renew --baseuri https://acme-v02.api.letsencrypt.org/"
        $Trigger = New-ScheduledTaskTrigger -Daily -At 3AM
        $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        $Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        
        Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "自动续期Let's Encrypt SSL证书"
        
        Write-Host "自动续期任务创建完成" -ForegroundColor Green
    } else {
        Write-Host "自动续期任务已存在" -ForegroundColor Yellow
    }
} catch {
    Write-Error "设置自动续期失败: $($_.Exception.Message)"
}

# 测试HTTPS访问
Write-Host "`n测试HTTPS访问..." -ForegroundColor Yellow
try {
    $Response = Invoke-WebRequest -Uri "https://$DomainName" -UseBasicParsing -TimeoutSec 30
    if ($Response.StatusCode -eq 200) {
        Write-Host "HTTPS访问测试成功！" -ForegroundColor Green
    } else {
        Write-Warning "HTTPS访问测试返回状态码: $($Response.StatusCode)"
    }
} catch {
    Write-Warning "HTTPS访问测试失败: $($_.Exception.Message)"
}

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "SSL证书配置完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "HTTPS访问地址: https://$DomainName" -ForegroundColor Cyan
Write-Host "证书有效期: $($Cert.NotAfter.ToString('yyyy-MM-dd'))" -ForegroundColor Cyan
Write-Host "自动续期: 已配置（每日3:00检查）" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Green




