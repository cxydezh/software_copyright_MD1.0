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
    # 设置环境变量
    os.environ.setdefault('FLASK_CONFIG', 'development')
    
    # 创建应用
    app = create_app()
    
    try:
        # 启动应用
        app.run(
            host='::',
            port=5000,
            debug=True,
            threaded=True
        )
    except KeyboardInterrupt:
        pass
    except Exception as e:
        sys.exit(1)

if __name__ == '__main__':
    main()
