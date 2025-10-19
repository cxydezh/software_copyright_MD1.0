#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 删除is_staff_account字段
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
            
            # 使用原始SQL删除字段
            with db.engine.connect() as conn:
                # 检查字段是否存在，如果存在则删除
                result = conn.execute(db.text("SHOW COLUMNS FROM staff LIKE 'is_staff_account'"))
                if result.fetchone():
                    print("删除 is_staff_account 字段...")
                    conn.execute(db.text("ALTER TABLE staff DROP COLUMN is_staff_account"))
                    conn.commit()
                    print("[OK] is_staff_account 字段已删除")
                else:
                    print("[OK] is_staff_account 字段不存在，无需删除")
            
            print("[OK] 数据库迁移完成！")
            
        except Exception as e:
            print(f"[ERROR] 数据库迁移失败: {e}")
            db.session.rollback()
            raise

def check_migration_status():
    """检查迁移状态"""
    app = create_app()
    
    with app.app_context():
        try:
            print("检查数据库迁移状态...")
            
            # 检查字段是否已删除
            with db.engine.connect() as conn:
                result = conn.execute(db.text("SHOW COLUMNS FROM staff"))
                columns = [row[0] for row in result.fetchall()]
            
            if 'is_staff_account' in columns:
                print("[ERROR] is_staff_account 字段仍然存在")
                return False
            else:
                print("[OK] is_staff_account 字段已成功删除")
                
                # 检查其他必需字段
                required_fields = [
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
                    print(f"[ERROR] 缺少字段: {', '.join(missing_fields)}")
                    return False
                else:
                    print("[OK] 所有必需字段都存在")
                    
                    # 检查现有员工记录状态
                    from database.models import Staff
                    staff_count = Staff.query.count()
                    approved_count = Staff.query.filter_by(approval_status='approved').count()
                    pending_count = Staff.query.filter_by(approval_status='pending').count()
                    rejected_count = Staff.query.filter_by(approval_status='rejected').count()
                    
                    print(f"[OK] 员工总数: {staff_count}")
                    print(f"[OK] 已审核通过: {approved_count}")
                    print(f"[OK] 待审核: {pending_count}")
                    print(f"[OK] 已驳回: {rejected_count}")
                    
                    return True
                
        except Exception as e:
            print(f"[ERROR] 检查失败: {e}")
            return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='删除is_staff_account字段数据库迁移')
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
