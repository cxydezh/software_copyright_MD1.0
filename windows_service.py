#!/usr/bin/env python3
"""
郑州医企创医疗科技有限公司 - 软著管理系统
Windows服务部署脚本
"""

import os
import sys
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

class SoftwareCopyrightService:
    """软著管理系统Windows服务"""
    
    def __init__(self):
        self.app = None
        self.server = None
        
    def start(self):
        """启动服务"""
        try:
            logger.info("正在启动软著管理系统服务...")
            
            # 设置生产环境
            os.environ.setdefault('FLASK_CONFIG', 'production')
            
            # 创建应用
            self.app = create_app('production')
            
            logger.info("应用创建成功")
            logger.info(f"数据库URL: {self.app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
            
            # 启动Waitress服务器
            self.server = serve(
                self.app,
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
            
            logger.info("软著管理系统服务启动成功")
            logger.info("访问地址: http://localhost:5000")
            logger.info("IIS代理: http://localhost/")
            
        except Exception as e:
            logger.error(f"服务启动失败: {e}")
            raise
            
    def stop(self):
        """停止服务"""
        try:
            logger.info("正在停止软著管理系统服务...")
            if self.server:
                self.server.close()
            logger.info("软著管理系统服务已停止")
        except Exception as e:
            logger.error(f"服务停止失败: {e}")

def main():
    """主函数"""
    service = SoftwareCopyrightService()
    
    try:
        service.start()
        # 保持服务运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到停止信号")
    except Exception as e:
        logger.error(f"服务运行错误: {e}")
    finally:
        service.stop()

if __name__ == '__main__':
    main()
