@echo off
REM 郑州医企创医疗科技有限公司 - 软著管理系统
REM Windows服务安装脚本

echo ============================================================
echo 郑州医企创医疗科技有限公司 - 软著管理系统
echo Windows服务安装脚本
echo ============================================================

cd /d C:\inetpub\wwwroot\Software_copyright_MS1.0

REM 激活虚拟环境
call .venv\Scripts\activate.bat

REM 安装pywin32（如果未安装）
echo 检查pywin32依赖...
python -c "import win32service" 2>nul
if errorlevel 1 (
    echo 安装pywin32...
    pip install pywin32
)

REM 创建服务安装脚本
echo 创建服务安装脚本...
python -c "
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os
import time
import logging
from waitress import serve
from web_app.app import create_app

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('C:\\inetpub\\logs\\software_copyright_service.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SoftwareCopyrightService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'SoftwareCopyrightService'
    _svc_display_name_ = '郑州医企创软著管理系统'
    _svc_description_ = '郑州医企创医疗科技有限公司软著管理系统Web服务'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.server = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        if self.server:
            self.server.close()

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def main(self):
        try:
            logger.info('正在启动软著管理系统服务...')
            
            # 设置生产环境
            os.environ.setdefault('FLASK_CONFIG', 'production')
            
            # 创建应用
            app = create_app('production')
            
            logger.info('应用创建成功')
            
            # 启动Waitress服务器
            self.server = serve(
                app,
                host='127.0.0.1',
                port=5000,
                threads=4,
                connection_limit=1000,
                cleanup_interval=30,
                channel_timeout=120,
                log_socket_errors=True,
                max_request_header_size=262144,
                max_request_body_size=1073741824,
            )
            
            logger.info('软著管理系统服务启动成功')
            
            # 等待停止信号
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            logger.error(f'服务运行错误: {e}')

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(SoftwareCopyrightService)
" > install_service.py

echo 安装Windows服务...
python install_service.py install

echo 启动服务...
python install_service.py start

echo ============================================================
echo 服务安装完成！
echo 服务名称: 郑州医企创软著管理系统
echo 访问地址: http://localhost/
echo ============================================================

pause
