@echo off
REM 郑州医企创医疗科技有限公司 - 软著管理系统
REM 生产环境启动脚本

echo ============================================================
echo 郑州医企创医疗科技有限公司 - 软著管理系统
echo 生产环境启动脚本
echo ============================================================

cd /d C:\inetpub\wwwroot\Software_copyright_MS1.0

REM 激活虚拟环境
call .venv\Scripts\activate.bat

echo 启动生产环境WSGI服务器...
python start_production_server.py

pause
