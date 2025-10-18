#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加员工账号审核功能（安全版本）
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db

def migrate_database():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            print("开始数据库迁移...")
            
            # 使用原始SQL添加字段
            with db.engine.connect() as conn:
                # 检查字段是否存在，如果不存在则添加
                result = conn.execute(db.text("SHOW COLUMNS FROM staff LIKE 'is_staff_account'"))
                if not result.fetchone():
                    print("添加 is_staff_account 字段...")
                    conn.execute(db.text("ALTER TABLE staff ADD COLUMN is_staff_account BOOLEAN DEFAULT 0"))
                    conn.commit()
                
                result = conn.execute(db.text("SHOW COLUMNS FROM staff LIKE 'approval_status'"))
                if not result.fetchone():
                    print("添加 approval_status 字段...")
                    conn.execute(db.text("ALTER TABLE staff ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending'"))
                    conn.commit()
                
                result = conn.execute(db.text("SHOW COLUMNS FROM staff LIKE 'approval_date'"))
                if not result.fetchone():
                    print("添加 approval_date 字段...")
                    conn.execute(db.text("ALTER TABLE staff ADD COLUMN approval_date DATETIME"))
                    conn.commit()
                
                result = conn.execute(db.text("SHOW COLUMNS FROM staff LIKE 'approver_id'"))
                if not result.fetchone():
                    print("添加 approver_id 字段...")
                    conn.execute(db.text("ALTER TABLE staff ADD COLUMN approver_id INTEGER"))
                    conn.commit()
                
                result = conn.execute(db.text("SHOW COLUMNS FROM staff LIKE 'approval_remarks'"))
                if not result.fetchone():
                    print("添加 approval_remarks 字段...")
                    conn.execute(db.text("ALTER TABLE staff ADD COLUMN approval_remarks TEXT"))
                    conn.commit()
                
                result = conn.execute(db.text("SHOW COLUMNS FROM staff LIKE 'application_reason'"))
                if not result.fetchone():
                    print("添加 application_reason 字段...")
                    conn.execute(db.text("ALTER TABLE staff ADD COLUMN application_reason TEXT"))
                    conn.commit()
            
            print("字段添加完成，现在更新现有记录...")
            
            # 现在可以安全地使用ORM更新记录
            from database.models import Staff
            
            # 更新现有员工记录
            existing_staff = Staff.query.all()
            updated_count = 0
            
            for staff in existing_staff:
                if staff.is_staff_account is None:
                    staff.is_staff_account = True  # 现有员工默认为员工账号
                    updated_count += 1
                
                if staff.approval_status is None:
                    staff.approval_status = 'approved'  # 现有员工默认为已审核通过
                    updated_count += 1
                
                if staff.approval_date is None:
                    staff.approval_date = datetime.utcnow()
                    updated_count += 1
            
            if updated_count > 0:
                db.session.commit()
                print(f"更新了 {updated_count} 个员工记录")
            
            # 确保默认管理员账户有正确的状态
            admin_staff = Staff.query.filter_by(email='admin@yiqichuang.com').first()
            if admin_staff:
                admin_staff.is_staff_account = True
                admin_staff.approval_status = 'approved'
                admin_staff.approval_date = datetime.utcnow()
                db.session.commit()
                print("更新默认管理员账户状态...")
            
            print("数据库迁移完成！")
            
        except Exception as e:
            print(f"数据库迁移失败: {e}")
            db.session.rollback()
            raise

def check_migration_status():
    """检查迁移状态"""
    app = create_app()
    
    with app.app_context():
        try:
            print("检查数据库迁移状态...")
            
            # 检查新字段是否存在
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SHOW COLUMNS FROM staff"))
                columns = [row[0] for row in result.fetchall()]
            
            required_fields = [
                'is_staff_account',
                'approval_status', 
                'approval_date',
                'approver_id',
                'approval_remarks',
                'application_reason'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in columns:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"缺少字段: {', '.join(missing_fields)}")
                return False
            else:
                print("所有必需字段已存在")
                
                # 检查现有员工记录状态
                from database.models import Staff
                staff_count = Staff.query.count()
                approved_count = Staff.query.filter_by(approval_status='approved').count()
                pending_count = Staff.query.filter_by(approval_status='pending').count()
                
                print(f"员工总数: {staff_count}")
                print(f"已审核通过: {approved_count}")
                print(f"待审核: {pending_count}")
                
                return True
                
        except Exception as e:
            print(f"检查失败: {e}")
            return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='员工账号功能数据库迁移')
    parser.add_argument('--check', action='store_true', help='仅检查迁移状态')
    parser.add_argument('--migrate', action='store_true', help='执行迁移')
    
    args = parser.parse_args()
    
    if args.check:
        check_migration_status()
    elif args.migrate:
        migrate_database()
    else:
        # 默认执行迁移
        migrate_database()
        print("\n" + "="*50)
        check_migration_status()
