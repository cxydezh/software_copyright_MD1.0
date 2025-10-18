#!/usr/bin/env python3
import os
from web_app.app import create_app

# 设置生产环境
os.environ.setdefault('FLASK_CONFIG', 'production')

# 创建应用实例
application = create_app('production')

# WSGI要求的app变量
app = application

if __name__ == '__main__':
    application.run()