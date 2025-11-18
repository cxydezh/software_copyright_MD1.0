#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查看当前应用使用的数据库配置
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from config.config import DevelopmentConfig, ProductionConfig

def show_database_config():
    """显示数据库配置信息"""
    print("=" * 60)
    print("数据库配置信息")
    print("=" * 60)
    
    # 获取当前环境
    config_name = os.getenv('FLASK_CONFIG', 'development')
    print(f"\n当前环境: {config_name}")
    
    # 创建应用以获取配置
    app = create_app(config_name)
    
    with app.app_context():
        # 获取数据库URI
        db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '未配置')
        
        print(f"\n数据库连接字符串: {db_uri}")
        
        # 解析数据库信息
        if db_uri.startswith('mysql'):
            print("\n数据库类型: MySQL")
            # 解析MySQL连接信息
            try:
                # 格式: mysql+pymysql://user:password@host:port/database
                parts = db_uri.replace('mysql+pymysql://', '').split('@')
                if len(parts) == 2:
                    user_pass = parts[0].split(':')
                    host_db = parts[1].split('/')
                    host_port = host_db[0].split(':')
                    
                    print(f"  用户名: {user_pass[0]}")
                    print(f"  密码: {'*' * len(user_pass[1]) if len(user_pass) > 1 else '未设置'}")
                    print(f"  主机: {host_port[0]}")
                    print(f"  端口: {host_port[1] if len(host_port) > 1 else '3306'}")
                    print(f"  数据库名: {host_db[1] if len(host_db) > 1 else '未指定'}")
            except Exception as e:
                print(f"  解析连接字符串时出错: {e}")
        elif db_uri.startswith('sqlite'):
            print("\n数据库类型: SQLite")
            # 解析SQLite路径
            try:
                if 'sqlite:///' in db_uri:
                    db_path = db_uri.replace('sqlite:///', '')
                    if not os.path.isabs(db_path):
                        db_path = os.path.join(os.getcwd(), db_path)
                    print(f"  数据库文件路径: {db_path}")
                    if os.path.exists(db_path):
                        file_size = os.path.getsize(db_path)
                        print(f"  文件大小: {file_size / 1024 / 1024:.2f} MB")
                        print(f"  文件存在: 是")
                    else:
                        print(f"  文件存在: 否（将在首次使用时创建）")
            except Exception as e:
                print(f"  解析路径时出错: {e}")
        else:
            print(f"\n数据库类型: 未知 ({db_uri[:20]}...)")
        
        # 显示环境变量
        print("\n相关环境变量:")
        db_password = os.environ.get('DB_PASSWORD')
        if db_password:
            print(f"  DB_PASSWORD: {'*' * len(db_password)} (已设置)")
        else:
            print(f"  DB_PASSWORD: 未设置（将使用SQLite）")
        
        dev_db_url = os.environ.get('DEV_DATABASE_URL')
        if dev_db_url:
            print(f"  DEV_DATABASE_URL: {dev_db_url[:50]}...")
        else:
            print(f"  DEV_DATABASE_URL: 未设置")
        
        dat_db_url = os.environ.get('DATABASE_URL')
        if dat_db_url:
            print(f"  DATABASE_URL: {dat_db_url[:50]}...")
        else:
            print(f"  DATABASE_URL: 未设置")
        
        # 测试数据库连接
        print("\n测试数据库连接...")
        try:
            from database.models import db
            db.engine.connect()
            print("  [OK] 数据库连接成功")
        except Exception as e:
            print(f"  [ERROR] 数据库连接失败: {e}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    show_database_config()
