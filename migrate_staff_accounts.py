#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 添加员工账号审核功能
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, Staff, Permission

def migrate_database():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        try:
            print("开始数据库迁移...")
            
            # 检查是否需要添加新字段
            inspector = db.inspect(db.engine)
            staff_columns = [col['name'] for col in inspector.get_columns('staff')]
            
            # 添加新字段（如果不存在）
            if 'is_staff_account' not in staff_columns:
                print("添加 is_staff_account 字段...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE staff ADD COLUMN is_staff_account BOOLEAN DEFAULT 0"))
                    conn.commit()
            
            if 'approval_status' not in staff_columns:
                print("添加 approval_status 字段...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE staff ADD COLUMN approval_status VARCHAR(20) DEFAULT 'pending'"))
                    conn.commit()
            
            if 'approval_date' not in staff_columns:
                print("添加 approval_date 字段...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE staff ADD COLUMN approval_date DATETIME"))
                    conn.commit()
            
            if 'approver_id' not in staff_columns:
                print("添加 approver_id 字段...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE staff ADD COLUMN approver_id INTEGER"))
                    conn.commit()
            
            if 'approval_remarks' not in staff_columns:
                print("添加 approval_remarks 字段...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE staff ADD COLUMN approval_remarks TEXT"))
                    conn.commit()
            
            if 'application_reason' not in staff_columns:
                print("添加 application_reason 字段...")
                with db.engine.connect() as conn:
                    conn.execute(db.text("ALTER TABLE staff ADD COLUMN application_reason TEXT"))
                    conn.commit()
            
            # 更新现有员工记录
            print("更新现有员工记录...")
            existing_staff = Staff.query.all()
            for staff in existing_staff:
                if not hasattr(staff, 'is_staff_account') or staff.is_staff_account is None:
                    staff.is_staff_account = True  # 现有员工默认为员工账号
                    staff.approval_status = 'approved'  # 现有员工默认为已审核通过
                    staff.approval_date = datetime.utcnow()
            
            db.session.commit()
            
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

if __name__ == '__main__':
    migrate_database()
