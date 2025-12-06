# Windows IPv6配置检查脚本
# 在PowerShell中运行: .\check_ipv6_windows.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Windows IPv6配置检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. 检查系统IPv6支持
Write-Host "1. 检查系统IPv6支持..." -ForegroundColor Yellow
try {
    $ipv6Enabled = Get-NetAdapterBinding -ComponentID ms_tcpip6 -ErrorAction SilentlyContinue | Where-Object { $_.Enabled -eq $true }
    if ($ipv6Enabled) {
        Write-Host "   ✅ IPv6已启用" -ForegroundColor Green
        $ipv6Enabled | ForEach-Object {
            Write-Host "      - 适配器: $($_.Name)" -ForegroundColor Gray
        }
    } else {
        Write-Host "   ❌ IPv6未启用" -ForegroundColor Red
        Write-Host "   提示: 在'网络和共享中心' -> '更改适配器设置' -> 右键网络适配器 -> '属性' -> 勾选'Internet协议版本6(TCP/IPv6)'" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  无法检查IPv6状态: $_" -ForegroundColor Yellow
}

# 2. 检查IPv6地址
Write-Host ""
Write-Host "2. 检查IPv6地址..." -ForegroundColor Yellow
try {
    $ipv6Addresses = Get-NetIPAddress -AddressFamily IPv6 -ErrorAction SilentlyContinue | Where-Object { 
        $_.AddressState -eq 'Preferred' -and 
        $_.IPAddress -notlike 'fe80::*' -and 
        $_.IPAddress -notlike '::1' 
    }
    
    if ($ipv6Addresses) {
        Write-Host "   ✅ 发现IPv6地址:" -ForegroundColor Green
        $ipv6Addresses | ForEach-Object {
            Write-Host "      - $($_.IPAddress) (接口: $($_.InterfaceAlias))" -ForegroundColor Gray
        }
    } else {
        Write-Host "   ❌ 未发现全局IPv6地址" -ForegroundColor Red
        Write-Host "   提示: 可能需要配置IPv6地址或联系网络管理员" -ForegroundColor Yellow
    }
    
    # 检查本地回环
    $loopback = Get-NetIPAddress -AddressFamily IPv6 -IPAddress '::1' -ErrorAction SilentlyContinue
    if ($loopback) {
        Write-Host "   ✅ IPv6本地回环 (::1) 可用" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  无法检查IPv6地址: $_" -ForegroundColor Yellow
}

# 3. 检查IPv6路由
Write-Host ""
Write-Host "3. 检查IPv6路由..." -ForegroundColor Yellow
try {
    $ipv6Routes = Get-NetRoute -AddressFamily IPv6 -ErrorAction SilentlyContinue | Where-Object { 
        $_.DestinationPrefix -notlike 'fe80::*' -and 
        $_.DestinationPrefix -ne '::/0' 
    }
    if ($ipv6Routes) {
        Write-Host "   ✅ IPv6路由配置正常" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  未发现IPv6路由" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  无法检查IPv6路由: $_" -ForegroundColor Yellow
}

# 4. 检查应用配置
Write-Host ""
Write-Host "4. 检查应用配置..." -ForegroundColor Yellow

# 检查 run_web.py
if (Test-Path "run_web.py") {
    $runWebContent = Get-Content "run_web.py" -Raw
    if ($runWebContent -match "host\s*=\s*['\`"]::['\`"]") {
        Write-Host "   ✅ run_web.py 已配置IPv6 (host='::')" -ForegroundColor Green
    } elseif ($runWebContent -match "host\s*=\s*['\`"]0\.0\.0\.0['\`"]") {
        Write-Host "   ⚠️  run_web.py 仅配置IPv4 (host='0.0.0.0')" -ForegroundColor Yellow
        Write-Host "   提示: 修改为 host='::' 以支持IPv6" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️  run_web.py 配置未知" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️  未找到 run_web.py" -ForegroundColor Yellow
}

# 检查 start_production_server.py
if (Test-Path "start_production_server.py") {
    $prodServerContent = Get-Content "start_production_server.py" -Raw
    if ($prodServerContent -match "host\s*=\s*['\`"]::['\`"]") {
        Write-Host "   ✅ start_production_server.py 已配置IPv6" -ForegroundColor Green
    } elseif ($prodServerContent -match "host\s*=\s*['\`"]0\.0\.0\.0['\`"]") {
        Write-Host "   ❌ start_production_server.py 仅配置IPv4 (host='0.0.0.0')" -ForegroundColor Red
        Write-Host "   提示: 修改为 host='::' 以支持IPv6" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️  start_production_server.py 配置未知" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️  未找到 start_production_server.py" -ForegroundColor Yellow
}

# 检查 windows_service.py
if (Test-Path "windows_service.py") {
    $serviceContent = Get-Content "windows_service.py" -Raw
    if ($serviceContent -match "host\s*=\s*['\`"]::['\`"]") {
        Write-Host "   ✅ windows_service.py 已配置IPv6" -ForegroundColor Green
    } elseif ($serviceContent -match "host\s*=\s*['\`"]127\.0\.0\.1['\`"]") {
        Write-Host "   ❌ windows_service.py 仅配置IPv4本地 (host='127.0.0.1')" -ForegroundColor Red
        Write-Host "   提示: 修改为 host='::' 以支持IPv6" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️  windows_service.py 配置未知" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️  未找到 windows_service.py" -ForegroundColor Yellow
}

# 5. 检查端口监听
Write-Host ""
Write-Host "5. 检查端口监听状态..." -ForegroundColor Yellow
try {
    $listeningPorts = Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { 
        $_.LocalPort -in @(80, 443, 5000, 8000) 
    }
    
    if ($listeningPorts) {
        Write-Host "   IPv4端口监听:" -ForegroundColor Cyan
        $listeningPorts | Where-Object { $_.LocalAddress -notlike '*::*' } | ForEach-Object {
            $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
            $processName = if ($process) { $process.ProcessName } else { "Unknown" }
            Write-Host "      $($_.LocalAddress):$($_.LocalPort) - $processName" -ForegroundColor Gray
        }
        
        Write-Host ""
        Write-Host "   IPv6端口监听:" -ForegroundColor Cyan
        $ipv6Listening = $listeningPorts | Where-Object { $_.LocalAddress -like '*::*' -or $_.LocalAddress -eq '::' }
        if ($ipv6Listening) {
            $ipv6Listening | ForEach-Object {
                $process = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
                $processName = if ($process) { $process.ProcessName } else { "Unknown" }
                Write-Host "      $($_.LocalAddress):$($_.LocalPort) - $processName" -ForegroundColor Gray
            }
        } else {
            Write-Host "      ❌ 未发现IPv6端口监听" -ForegroundColor Red
        }
    } else {
        Write-Host "   ⚠️  未发现相关端口监听" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  无法检查端口监听: $_" -ForegroundColor Yellow
}

# 6. 检查Windows防火墙
Write-Host ""
Write-Host "6. 检查Windows防火墙..." -ForegroundColor Yellow
try {
    $firewallStatus = Get-NetFirewallProfile -ErrorAction SilentlyContinue
    $firewallStatus | ForEach-Object {
        $status = if ($_.Enabled) { "启用" } else { "禁用" }
        Write-Host "   $($_.Name): $status" -ForegroundColor $(if ($_.Enabled) { "Green" } else { "Yellow" })
    }
    
    # 检查IPv6防火墙规则
    $ipv6Rules = Get-NetFirewallRule -ErrorAction SilentlyContinue | Where-Object { 
        $_.DisplayName -like '*IPv6*' -or $_.DisplayName -like '*80*' -or $_.DisplayName -like '*443*' -or $_.DisplayName -like '*5000*' 
    }
    if ($ipv6Rules) {
        Write-Host "   发现相关防火墙规则" -ForegroundColor Green
    }
} catch {
    Write-Host "   ⚠️  无法检查防火墙: $_" -ForegroundColor Yellow
}

# 7. 测试IPv6连接
Write-Host ""
Write-Host "7. 测试IPv6连接..." -ForegroundColor Yellow
try {
    # 测试本地IPv6
    $testResult = Test-NetConnection -ComputerName "::1" -Port 5000 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($testResult.TcpTestSucceeded) {
        Write-Host "   ✅ IPv6本地连接成功 (::1:5000)" -ForegroundColor Green
    } else {
        Write-Host "   ❌ IPv6本地连接失败 (::1:5000)" -ForegroundColor Red
        Write-Host "   提示: 应用可能未启动或未监听IPv6" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  无法测试IPv6连接: $_" -ForegroundColor Yellow
    Write-Host "   提示: 可以手动测试: curl http://[::1]:5000" -ForegroundColor Gray
}

# 8. 检查IIS配置（如果使用IIS）
Write-Host ""
Write-Host "8. 检查IIS配置（如果使用）..." -ForegroundColor Yellow
try {
    $iisFeature = Get-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole -ErrorAction SilentlyContinue
    if ($iisFeature -and $iisFeature.State -eq 'Enabled') {
        Write-Host "   ✅ IIS已安装" -ForegroundColor Green
        Write-Host "   提示: IIS默认支持IPv6，需要在网站绑定中配置" -ForegroundColor Gray
    } else {
        Write-Host "   ℹ️  IIS未安装或未启用" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  无法检查IIS: $_" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "检查完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "详细配置指南请参考: mdfiles\IPV6_CONFIGURATION_GUIDE_WINDOWS.md" -ForegroundColor Yellow

