#!/usr/bin/env python3
"""
郑州医企创医疗科技有限公司 - 软著管理系统
生产环境WSGI服务器启动脚本
使用Waitress作为生产级WSGI服务器
"""

import os
import sys
from waitress import serve
from web_app.app import create_app

def main():
    """主函数"""
    print("=" * 60)
    print("郑州医企创医疗科技有限公司 - 软著管理系统")
    print("生产环境WSGI服务器启动中...")
    print("=" * 60)

    # 设置生产环境
    os.environ.setdefault('FLASK_CONFIG', 'production')

    # 创建应用
    app = create_app('production')

    # 启动信息
    print(f"应用配置: {os.environ.get('FLASK_CONFIG', 'production')}")
    print(f"调试模式: {app.config.get('DEBUG', False)}")
    print(f"数据库URL: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    print("-" * 60)
    print("生产环境访问地址:")
    print("  本地访问: http://localhost:5000")
    print("  公网访问: http://47.111.186.20:5000")
    print("  IIS代理: http://localhost/")
    print("  IIS公网: http://47.111.186.20/")
    print("-" * 60)
    print("默认管理员账户:")
    print("  邮箱: admin@yiqichuang.com")
    print("  密码: admin123")
    print("=" * 60)

    try:
        # 使用Waitress生产级WSGI服务器
        serve(
            app,
            host='0.0.0.0',  # 监听所有网络接口，支持公共网络访问
            port=5000,
            threads=4,  # 线程数
            connection_limit=1000,  # 连接限制
            cleanup_interval=30,  # 清理间隔
            channel_timeout=120,  # 通道超时
            log_socket_errors=True,  # 记录socket错误
            max_request_header_size=262144,  # 最大请求头大小
            max_request_body_size=1073741824,  # 最大请求体大小(1GB)
        )
    except KeyboardInterrupt:
        print("\n生产服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
