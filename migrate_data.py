#!/usr/bin/env python3
"""
数据迁移脚本：从SQLite迁移到MySQL
"""

import os
import sys
import sqlite3
from datetime import datetime
from sqlalchemy import create_engine, text

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from database.models import db, Staff, User, Project, Message, Permission

def connect_sqlite():
    """连接SQLite数据库"""
    sqlite_path = 'software_copyright.db'
    if not os.path.exists(sqlite_path):
        print(f"[ERROR] SQLite数据库文件不存在: {sqlite_path}")
        return None
    
    try:
        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row  # 使结果可以按列名访问
        print(f"[SUCCESS] 成功连接SQLite数据库: {sqlite_path}")
        return conn
    except Exception as e:
        print(f"[ERROR] 连接SQLite数据库失败: {e}")
        return None

def migrate_staff_data(sqlite_conn):
    """迁移员工数据"""
    try:
        print("👥 迁移员工数据...")
        
        # 从SQLite读取数据
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM staff")
        staff_rows = cursor.fetchall()
        
        app = create_app('development')
        with app.app_context():
            migrated_count = 0
            for row in staff_rows:
                # 检查是否已存在
                existing = Staff.query.filter_by(username=row['username']).first()
                if existing:
                    print(f"[WARNING] 员工 {row['username']} 已存在，跳过")
                    continue
                
                # 创建新员工记录
                staff = Staff(
                    username=row['username'],
                    password_hash=row['password_hash'],
                    name=row['name'],
                    email=row['email'],
                    phone=row['phone'],
                    department=row['department'],
                    position_id=row['position_id'],
                    is_active=bool(row['is_active']),
                    create_time=datetime.fromisoformat(row['create_time']) if row['create_time'] else datetime.utcnow()
                )
                
                db.session.add(staff)
                migrated_count += 1
            
            db.session.commit()
            print(f"[SUCCESS] 成功迁移 {migrated_count} 个员工记录")
            return True
            
    except Exception as e:
        print(f"[ERROR] 迁移员工数据失败: {e}")
        db.session.rollback()
        return False

def migrate_user_data(sqlite_conn):
    """迁移用户数据"""
    try:
        print("👤 迁移用户数据...")
        
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM user")
        user_rows = cursor.fetchall()
        
        app = create_app('development')
        with app.app_context():
            migrated_count = 0
            for row in user_rows:
                existing = User.query.filter_by(username=row['username']).first()
                if existing:
                    print(f"[WARNING] 用户 {row['username']} 已存在，跳过")
                    continue
                
                user = User(
                    username=row['username'],
                    password_hash=row['password_hash'],
                    name=row['name'],
                    email=row['email'],
                    phone=row['phone'],
                    company=row['company'],
                    address=row['address'],
                    is_active=bool(row['is_active']),
                    create_time=datetime.fromisoformat(row['create_time']) if row['create_time'] else datetime.utcnow()
                )
                
                db.session.add(user)
                migrated_count += 1
            
            db.session.commit()
            print(f"[SUCCESS] 成功迁移 {migrated_count} 个用户记录")
            return True
            
    except Exception as e:
        print(f"[ERROR] 迁移用户数据失败: {e}")
        db.session.rollback()
        return False

def migrate_project_data(sqlite_conn):
    """迁移项目数据"""
    try:
        print("📋 迁移项目数据...")
        
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM project")
        project_rows = cursor.fetchall()
        
        app = create_app('development')
        with app.app_context():
            migrated_count = 0
            for row in project_rows:
                existing = Project.query.filter_by(id=row['id']).first()
                if existing:
                    print(f"[WARNING] 项目 {row['id']} 已存在，跳过")
                    continue
                
                project = Project(
                    id=row['id'],
                    project_name=row['project_name'],
                    project_type=row['project_type'],
                    applicant_type=row['applicant_type'],
                    copyright_owner=row['copyright_owner'],
                    software_applicant_name=row['software_applicant_name'],
                    priority=row['priority'],
                    applicant_id=row['applicant_id'],
                    confirmer_id=row['confirmer_id'],
                    executor_id=row['executor_id'],
                    price=row['price'],
                    discount=row['discount'],
                    status=row['status'],
                    remarks=row['remarks'],
                    create_time=datetime.fromisoformat(row['create_time']) if row['create_time'] else datetime.utcnow(),
                    confirm_time=datetime.fromisoformat(row['confirm_time']) if row['confirm_time'] else None,
                    execute_time=datetime.fromisoformat(row['execute_time']) if row['execute_time'] else None,
                    complete_time=datetime.fromisoformat(row['complete_time']) if row['complete_time'] else None
                )
                
                db.session.add(project)
                migrated_count += 1
            
            db.session.commit()
            print(f"[SUCCESS] 成功迁移 {migrated_count} 个项目记录")
            return True
            
    except Exception as e:
        print(f"[ERROR] 迁移项目数据失败: {e}")
        db.session.rollback()
        return False

def migrate_message_data(sqlite_conn):
    """迁移消息数据"""
    try:
        print("💬 迁移消息数据...")
        
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM message")
        message_rows = cursor.fetchall()
        
        app = create_app('development')
        with app.app_context():
            migrated_count = 0
            for row in message_rows:
                message = Message(
                    id=row['id'],
                    project_id=row['project_id'],
                    sender_id=row['sender_id'],
                    receiver_id=row['receiver_id'],
                    content=row['content'],
                    message_type=row['message_type'],
                    is_read=bool(row['is_read']),
                    create_time=datetime.fromisoformat(row['create_time']) if row['create_time'] else datetime.utcnow()
                )
                
                db.session.add(message)
                migrated_count += 1
            
            db.session.commit()
            print(f"[SUCCESS] 成功迁移 {migrated_count} 个消息记录")
            return True
            
    except Exception as e:
        print(f"[ERROR] 迁移消息数据失败: {e}")
        db.session.rollback()
        return False

def migrate_permissions_data(sqlite_conn):
    """迁移权限数据"""
    try:
        print("🔐 迁移权限数据...")
        
        cursor = sqlite_conn.cursor()
        cursor.execute("SELECT * FROM permissions")
        permission_rows = cursor.fetchall()
        
        app = create_app('development')
        with app.app_context():
            migrated_count = 0
            for row in permission_rows:
                existing = Permission.query.filter_by(position=row['position']).first()
                if existing:
                    print(f"[WARNING] 权限 {row['position']} 已存在，跳过")
                    continue
                
                permission = Permission(
                    position=row['position'],
                    can_confirm=bool(row['can_confirm']),
                    can_execute=bool(row['can_execute']),
                    can_manage=bool(row['can_manage']),
                    can_view_all=bool(row['can_view_all'])
                )
                
                db.session.add(permission)
                migrated_count += 1
            
            db.session.commit()
            print(f"[SUCCESS] 成功迁移 {migrated_count} 个权限记录")
            return True
            
    except Exception as e:
        print(f"[ERROR] 迁移权限数据失败: {e}")
        db.session.rollback()
        return False

def main():
    print("=" * 60)
    print("Data Migration: SQLite to MySQL")
    print("=" * 60)
    
    # 检查环境变量
    if not os.environ.get('DB_PASSWORD'):
        print("[ERROR] 错误：请设置环境变量 DB_PASSWORD")
        print("Windows: set DB_PASSWORD=your_password")
        print("Linux/Mac: export DB_PASSWORD=your_password")
        return
    
    # 连接SQLite数据库
    sqlite_conn = connect_sqlite()
    if not sqlite_conn:
        return
    
    try:
        # 迁移数据
        success = True
        success &= migrate_permissions_data(sqlite_conn)
        success &= migrate_staff_data(sqlite_conn)
        success &= migrate_user_data(sqlite_conn)
        success &= migrate_project_data(sqlite_conn)
        success &= migrate_message_data(sqlite_conn)
        
        if success:
            print("\n" + "=" * 60)
            print("[SUCCESS] 数据迁移完成！")
            print("=" * 60)
            print("所有数据已成功从SQLite迁移到MySQL")
            print("下一步：运行 python run_web.py 启动Web应用")
        else:
            print("\n[ERROR] 数据迁移过程中出现错误，请检查日志")
            
    finally:
        sqlite_conn.close()

if __name__ == '__main__':
    main()
