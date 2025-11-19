# 配置问题快速修复脚本 (PowerShell版本)

Write-Host "=== 配置问题快速修复脚本 ===" -ForegroundColor Green

# 1. 检查web.config文件
Write-Host "1. 检查web.config文件..." -ForegroundColor Yellow
if (Test-Path "windows_deployment\web.config") {
    Write-Host "✓ web.config文件存在" -ForegroundColor Green
    
    # 检查重复的mimeMap配置
    $content = Get-Content "windows_deployment\web.config" -Raw
    $duplicate_mime = ($content | Select-String "fileExtension.*json").Matches.Count
    
    if ($duplicate_mime -gt 1) {
        Write-Host "⚠ 发现重复的mimeMap配置" -ForegroundColor Red
        Write-Host "正在修复..." -ForegroundColor Yellow
        
        # 备份原文件
        Copy-Item "windows_deployment\web.config" "windows_deployment\web.config.backup"
        
        # 移除重复的mimeMap
        $content = $content -replace '<mimeMap fileExtension="\.json" mimeType="application/json" />', ''
        
        # 添加正确的mimeMap
        $content = $content -replace '(<staticContent>)', '$1`n      <mimeMap fileExtension=".json" mimeType="application/json" />'
        
        Set-Content "windows_deployment\web.config" $content
        
        Write-Host "✓ 修复完成" -ForegroundColor Green
    } else {
        Write-Host "✓ mimeMap配置正常" -ForegroundColor Green
    }
} else {
    Write-Host "✗ web.config文件不存在" -ForegroundColor Red
}

# 2. 检查IIS配置
Write-Host "2. 检查IIS配置..." -ForegroundColor Yellow
try {
    Import-Module WebAdministration -ErrorAction SilentlyContinue
    $appPools = Get-IISAppPool | Where-Object {$_.Name -like "*software_copyright*"}
    if ($appPools) {
        Write-Host "✓ 应用程序池存在" -ForegroundColor Green
    } else {
        Write-Host "✗ 应用程序池不存在" -ForegroundColor Red
    }
    
    $sites = Get-IISSite | Where-Object {$_.Name -like "*software_copyright*"}
    if ($sites) {
        Write-Host "✓ 网站存在" -ForegroundColor Green
    } else {
        Write-Host "✗ 网站不存在" -ForegroundColor Red
    }
} catch {
    Write-Host "⚠ IIS模块不可用" -ForegroundColor Yellow
}

# 3. 检查Python环境
Write-Host "3. 检查Python环境..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\python.exe") {
    Write-Host "✓ Python环境存在" -ForegroundColor Green
    
    # 检查Flask应用
    Write-Host "检查Flask应用..." -ForegroundColor Yellow
    if (Test-Path "app.py") {
        Write-Host "✓ Flask应用文件存在" -ForegroundColor Green
    } else {
        Write-Host "✗ Flask应用文件不存在" -ForegroundColor Red
    }
} else {
    Write-Host "✗ Python环境不存在" -ForegroundColor Red
}

# 4. 检查日志文件
Write-Host "4. 检查日志文件..." -ForegroundColor Yellow
if (Test-Path "logs") {
    Write-Host "✓ 日志目录存在" -ForegroundColor Green
    
    # 检查最新日志
    $latest_log = Get-ChildItem "logs\*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($latest_log) {
        Write-Host "✓ 最新日志: $($latest_log.Name)" -ForegroundColor Green
        
        # 检查错误
        $error_content = Get-Content $latest_log.FullName | Select-String "0x800700b7"
        if ($error_content) {
            Write-Host "⚠ 发现0x800700b7错误" -ForegroundColor Red
            Write-Host "错误详情:" -ForegroundColor Yellow
            $error_content | Select-Object -Last 5 | ForEach-Object { Write-Host $_ -ForegroundColor Red }
        } else {
            Write-Host "✓ 未发现0x800700b7错误" -ForegroundColor Green
        }
    } else {
        Write-Host "⚠ 未找到日志文件" -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ 日志目录不存在" -ForegroundColor Red
}

# 5. 清理临时文件
Write-Host "5. 清理临时文件..." -ForegroundColor Yellow
if (Test-Path "__pycache__") {
    Remove-Item "__pycache__" -Recurse -Force
    Write-Host "✓ 清理Python缓存" -ForegroundColor Green
}

if (Test-Path "venv\__pycache__") {
    Remove-Item "venv\__pycache__" -Recurse -Force
    Write-Host "✓ 清理虚拟环境缓存" -ForegroundColor Green
}

# 6. 验证修复
Write-Host "6. 验证修复..." -ForegroundColor Yellow
if (Test-Path "windows_deployment\web.config") {
    # 检查配置语法
    try {
        [xml]$config = Get-Content "windows_deployment\web.config"
        Write-Host "✓ web.config语法正确" -ForegroundColor Green
    } catch {
        Write-Host "✗ web.config语法错误" -ForegroundColor Red
    }
}

Write-Host "=== 修复完成 ===" -ForegroundColor Green
Write-Host ""
Write-Host "如果问题仍然存在，请检查：" -ForegroundColor Yellow
Write-Host "1. IIS应用程序池状态" -ForegroundColor White
Write-Host "2. Python环境配置" -ForegroundColor White
Write-Host "3. 文件权限设置" -ForegroundColor White
Write-Host "4. 防火墙规则" -ForegroundColor White













