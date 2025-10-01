@echo off
REM 启动UTF-8编码的终端

echo 正在启动UTF-8编码的终端...

REM 设置代码页为UTF-8
chcp 65001 >nul

REM 设置Python环境变量
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM 设置控制台代码页
reg add "HKEY_CURRENT_USER\Console" /v "CodePage" /t REG_DWORD /d 65001 /f >nul 2>&1

echo UTF-8终端已启动！
echo.
echo 当前设置：
echo - 代码页: 65001 (UTF-8)
echo - Python编码: UTF-8
echo.
echo 现在可以正常显示中文字符了
echo.

REM 启动PowerShell或CMD
powershell -NoExit -Command "Write-Host 'UTF-8终端已就绪' -ForegroundColor Green; Write-Host '公司名称：郑州医企创医疗科技有限公司' -ForegroundColor Cyan"

