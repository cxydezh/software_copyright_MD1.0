#!/usr/bin/env python3
"""
SQLite数据库初始化脚本
"""

import os
import sys

def init_sqlite_database():
    """初始化SQLite数据库"""
    try:
        from web_app.app import create_app
        from database.models import db
        
        print("正在创建SQLite数据库...")
        
        app = create_app('development')
        with app.app_context():
            # 创建所有表
            db.create_all()
            print("✅ 数据库表创建成功")
            
            # 检查数据库文件
            db_path = os.path.join(os.getcwd(), 'software_copyright.db')
            if os.path.exists(db_path):
                print(f"✅ 数据库文件已创建: {db_path}")
            
        return True
        
    except Exception as e:
        print(f"❌ 初始化数据库失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("郑州医企创医疗科技有限公司 - 软著管理系统")
    print("SQLite数据库初始化")
    print("=" * 60)
    
    if init_sqlite_database():
        print("\n" + "=" * 60)
        print("🎉 数据库初始化完成！")
        print("=" * 60)
        print("数据库类型: SQLite")
        print("数据库文件: software_copyright.db")
        print("\n现在可以运行以下命令启动系统:")
        print("python run_web.py")
        print("=" * 60)
    else:
        print("\n❌ 数据库初始化失败")

if __name__ == '__main__':
    main()
