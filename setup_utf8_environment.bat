@echo off
REM 设置UTF-8环境的完整脚本

echo 正在设置UTF-8环境...

REM 设置代码页为UTF-8
chcp 65001 >nul

REM 设置Python环境变量
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

REM 设置控制台字体（如果可能）
reg add "HKEY_CURRENT_USER\Console" /v "CodePage" /t REG_DWORD /d 65001 /f >nul 2>&1

echo.
echo UTF-8环境设置完成！
echo.
echo 当前设置：
echo - 代码页: 65001 (UTF-8)
echo - Python编码: UTF-8
echo - 控制台编码: UTF-8
echo.
echo 现在可以正常显示中文字符了
echo.

REM 测试显示
echo 测试中文显示：
echo 公司名称：郑州医企创医疗科技有限公司
echo 系统状态：正常运行
echo 编码测试：成功
echo.

pause

