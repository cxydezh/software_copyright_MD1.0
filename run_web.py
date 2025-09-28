#!/usr/bin/env python3
"""
郑州医企创医疗科技有限公司 - 软著管理系统
Web应用启动脚本
"""

import os
import sys
from web_app.app import create_app

def main():
    """主函数"""
    print("=" * 60)
    print("郑州医企创医疗科技有限公司 - 软著管理系统")
    print("Web应用服务器启动中...")
    print("=" * 60)
    
    # 设置环境变量
    os.environ.setdefault('FLASK_CONFIG', 'development')
    
    # 创建应用
    app = create_app()
    
    # 启动信息
    print(f"应用配置: {os.environ.get('FLASK_CONFIG', 'development')}")
    print(f"调试模式: {app.config.get('DEBUG', False)}")
    print(f"数据库URL: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')}")
    print("-" * 60)
    print("访问地址:")
    print("  本地访问: http://localhost:5000")
    print("  局域网访问: http://0.0.0.0:5000")
    print("-" * 60)
    print("默认管理员账户:")
    print("  邮箱: admin@yiqichuang.com")
    print("  密码: admin123")
    print("=" * 60)
    
    try:
        # 启动应用
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
