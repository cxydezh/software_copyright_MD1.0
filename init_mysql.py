#!/usr/bin/env python3
"""
MySQL数据库设置脚本
"""
import os
import sys
import pymysql
from sqlalchemy import create_engine, text
from datetime import datetime
from config.config import DevelopmentConfig

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from database.models import db, Staff, User, Project, Message, Permission

def init_mysql_database():
    """初始化MySQL数据库表结构"""
    try:
        print("🔌 连接到MySQL数据库...")
        
        # 获取数据库密码
        db_password = os.environ.get('DB_PASSWORD')
        if not db_password:
            print("❌ 错误：请设置环境变量 DB_PASSWORD")
            return False
        
        # 创建Flask应用
        app = create_app('development')
        
        with app.app_context():
            # 创建所有表
            print("📋 创建数据库表...")
            db.create_all()
            
            # 检查表是否创建成功
            print("🔍 验证表结构...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            expected_tables = ['staff', 'users', 'projects', 'messages', 'permissions']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ 表 {table} 创建成功")
                else:
                    print(f"❌ 表 {table} 创建失败")
                    return False
            
            print("✅ 所有数据库表创建成功！")
            return True
            
    except Exception as e:
        print(f"❌ 初始化数据库失败: {e}")
        return False

def create_sample_data():
    """创建示例数据"""
    try:
        print("📝 创建示例数据...")
        
        app = create_app('development')
        with app.app_context():
            # 检查是否已有数据
            if Staff.query.first() or User.query.first():
                print("⚠️  数据库中已有数据，跳过示例数据创建")
                return True
            
            # 创建权限
            admin_permission = Permission(
                position='系统管理员',
                can_confirm=True,
                can_approve=True,
                can_execute=True,
                can_manage=True,
                can_view_all=True
            )
            
            business_permission = Permission(
                position='普通业务员',
                can_confirm=True,
                can_approve=False,
                can_execute=False,
                can_manage=False,
                can_view_all=False
            )
            
            executor_permission = Permission(
                position='项目执行者',
                can_confirm=False,
                can_approve=False,
                can_execute=True,
                can_manage=False,
                can_view_all=False
            )
            
            # 创建管理员账户
            admin_staff = Staff(
                name='系统管理员',
                email='admin@yiqichuang.com',
                phone='195 5553 8037',
                position_id=1,
                password_hash='$pbkdf2-sha256$29000$N2YqzZ8GK3bDFu4vP3P3Og$rZ3P1N4.3T1hJ5V8x9Q2O0Y7Z6W1E4R3T2Y1U0I9O8P'  # admin123
            )
            admin_staff.set_password('admin123')
            
            # 创建业务员
            business_staff = Staff(
                name='张业务',
                email='business@yiqichuang.com',
                phone='0371-12345679',
                position_id=2,
                password_hash='$pbkdf2-sha256$29000$N2YqzZ8GK3bDFu4vP3P3Og$rZ3P1N4.3T1hJ5V8x9Q2O0Y7Z6W1E4R3T2Y1U0I9O8P'  # business123
            )
            business_staff.set_password('business123')
            
            # 创建执行者
            executor_staff = Staff(
                name='李执行',
                email='executor@yiqichuang.com',
                phone='0371-12345680',
                position_id=3,
                password_hash='$pbkdf2-sha256$29000$N2YqzZ8GK3bDFu4vP3P3Og$rZ3P1N4.3T1hJ5V8x9Q2O0Y7Z6W1E4R3T2Y1U0I9O8P'  # executor123
            )
            executor_staff.set_password('executor123')
            
            # 创建测试用户
            test_user = User(
                name='测试用户',
                email='test@example.com',
                phone='13800138000',
                password_hash='$pbkdf2-sha256$29000$N2YqzZ8GK3bDFu4vP3P3Og$rZ3P1N4.3T1hJ5V8x9Q2O0Y7Z6W1E4R3T2Y1U0I9O8P'  # test123
            )
            test_user.set_password('test123')
            
            # 保存到数据库
            db.session.add(admin_permission)
            db.session.add(business_permission)
            db.session.add(executor_permission)
            db.session.add(admin_staff)
            db.session.add(business_staff)
            db.session.add(executor_staff)
            db.session.add(test_user)
            
            db.session.commit()
            
            print("✅ 示例数据创建成功！")
            print("管理员账户: admin@yiqichuang.com / admin123")
            print("业务员账户: business@yiqichuang.com / business123")
            print("执行者账户: executor@yiqichuang.com / executor123")
            print("测试用户: test@example.com / test123")
            
            return True
            
    except Exception as e:
        print(f"❌ 创建示例数据失败: {e}")
        db.session.rollback()
        return False

def main():
    print("=" * 60)
    print("MySQL数据库初始化")
    print("=" * 60)
    
    # 检查环境变量
    if not os.environ.get('DB_PASSWORD'):
        print("❌ 错误：请设置环境变量 DB_PASSWORD")
        print("Windows: set DB_PASSWORD=your_password")
        print("Linux/Mac: export DB_PASSWORD=your_password")
        return
    
    # 步骤1：初始化数据库表
    if not init_mysql_database():
        return
    
    # 步骤2：创建示例数据
    if not create_sample_data():
        return
    
    print("\n" + "=" * 60)
    print("🎉 MySQL数据库初始化完成！")
    print("=" * 60)
    print("下一步：")
    print("1. 运行 python migrate_data.py 迁移SQLite数据（可选）")
    print("2. 运行 python run_web.py 启动Web应用")

if __name__ == '__main__':
    main()