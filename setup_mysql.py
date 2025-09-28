#!/usr/bin/env python3
"""
MySQL数据库设置脚本
"""

import os
import sys
import pymysql
from sqlalchemy import create_engine, text
from config.config import DevelopmentConfig

def create_mysql_database():
    """创建MySQL数据库和用户"""
    
    # 获取数据库密码
    db_password = os.environ.get('DB_PASSWORD')
    if not db_password:
        print("❌ 错误：请设置环境变量 DB_PASSWORD")
        print("Windows: set DB_PASSWORD=your_password")
        print("Linux/Mac: export DB_PASSWORD=your_password")
        return False
    
    try:
        # 连接到MySQL服务器（使用root用户）
        print("🔌 连接到MySQL服务器...")
        connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password=input("请输入MySQL root密码: "),
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 创建数据库
            print("📁 创建数据库...")
            cursor.execute("CREATE DATABASE IF NOT EXISTS software_copyright CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            # 创建用户（如果不存在）
            print("👤 创建用户...")
            cursor.execute(f"CREATE USER IF NOT EXISTS 'webuser'@'localhost' IDENTIFIED BY '{db_password}'")
            cursor.execute(f"CREATE USER IF NOT EXISTS 'webuser'@'%' IDENTIFIED BY '{db_password}'")
            
            # 授权
            print("🔑 设置权限...")
            cursor.execute("GRANT ALL PRIVILEGES ON software_copyright.* TO 'webuser'@'localhost'")
            cursor.execute("GRANT ALL PRIVILEGES ON software_copyright.* TO 'webuser'@'%'")
            cursor.execute("FLUSH PRIVILEGES")
            
            print("✅ 数据库和用户创建成功！")
            
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 创建数据库失败: {e}")
        return False

def test_mysql_connection():
    """测试MySQL连接"""
    try:
        print("🧪 测试MySQL连接...")
        
        # 获取数据库密码
        db_password = os.environ.get('DB_PASSWORD')
        if not db_password:
            print("❌ 错误：请设置环境变量 DB_PASSWORD")
            return False
        
        # 创建连接字符串
        database_url = f'mysql+pymysql://webuser:{db_password}@127.0.0.1:3306/software_copyright'
        
        # 测试连接
        engine = create_engine(database_url, echo=True)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.fetchone()[0]
            
        if test_value == 1:
            print("✅ MySQL连接测试成功！")
            return True
        else:
            print("❌ MySQL连接测试失败")
            return False
            
    except Exception as e:
        print(f"❌ MySQL连接测试失败: {e}")
        return False

def main():
    print("=" * 60)
    print("MySQL数据库设置向导")
    print("=" * 60)
    
    # 检查环境变量
    if not os.environ.get('DB_PASSWORD'):
        print("⚠️  请先设置环境变量 DB_PASSWORD")
        print("Windows: set DB_PASSWORD=your_password")
        print("Linux/Mac: export DB_PASSWORD=your_password")
        return
    
    # 步骤1：创建数据库和用户
    if not create_mysql_database():
        return
    
    # 步骤2：测试连接
    if not test_mysql_connection():
        return
    
    print("\n" + "=" * 60)
    print("🎉 MySQL设置完成！")
    print("=" * 60)
    print("下一步：")
    print("1. 运行 python init_mysql.py 初始化数据库表")
    print("2. 运行 python migrate_data.py 迁移SQLite数据")
    print("3. 运行 python run_web.py 启动Web应用")

if __name__ == '__main__':
    main()
