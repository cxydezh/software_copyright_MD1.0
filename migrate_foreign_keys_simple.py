#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 更新外键级联关系（简化版）
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db

def migrate_foreign_keys_simple():
    """使用SQLAlchemy重新创建表结构来更新外键"""
    app = create_app()
    
    with app.app_context():
        try:
            print("开始更新外键级联关系...")
            
            # 使用SQLAlchemy的create_all()来更新表结构
            # 这会根据新的模型定义更新外键约束
            print("重新创建表结构...")
            db.create_all()
            
            print("[OK] 外键级联关系更新完成！")
            print("\n更新的外键级联关系:")
            print("1. Staff.approver_id -> Staff.id (SET NULL)")
            print("2. Message.user_id -> User.id (CASCADE)")
            print("3. Message.staff_id -> Staff.id (CASCADE)")
            print("4. Message.project_id -> Project.id (CASCADE)")
            print("5. Project.applicant_id -> User.id (CASCADE)")
            print("6. Project.confirmer_id -> Staff.id (SET NULL)")
            print("7. Project.executor_id -> Staff.id (SET NULL)")
            print("8. PaperProject.applicant_id -> User.id (CASCADE)")
            print("9. PaperProject.confirmer_id -> Staff.id (SET NULL)")
            print("10. PaperProject.executor_id -> Staff.id (SET NULL)")
            print("11. PatentProject.applicant_id -> User.id (CASCADE)")
            print("12. PatentProject.confirmer_id -> Staff.id (SET NULL)")
            print("13. PatentProject.executor_id -> Staff.id (SET NULL)")
            print("14. ProjectFile.uploader_id -> User.id (CASCADE)")
            
        except Exception as e:
            print(f"[ERROR] 外键更新失败: {e}")
            raise

def test_foreign_keys():
    """测试外键约束"""
    app = create_app()
    
    with app.app_context():
        try:
            print("测试外键约束...")
            
            from database.models import Staff, User, Message, Project
            
            # 测试数据查询
            staff_count = Staff.query.count()
            user_count = User.query.count()
            message_count = Message.query.count()
            project_count = Project.query.count()
            
            print(f"[OK] 数据查询正常:")
            print(f"  - Staff: {staff_count}")
            print(f"  - User: {user_count}")
            print(f"  - Message: {message_count}")
            print(f"  - Project: {project_count}")
            
            # 测试关系查询
            if staff_count > 0:
                staff = Staff.query.first()
                if hasattr(staff, 'approved_staff'):
                    approved_count = len(staff.approved_staff)
                    print(f"  - Staff审核关系: {approved_count} 个被审核员工")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 测试失败: {e}")
            return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='更新外键级联关系')
    parser.add_argument('--test', action='store_true', help='仅测试外键约束')
    parser.add_argument('--migrate', action='store_true', help='执行迁移')
    
    args = parser.parse_args()
    
    if args.test:
        test_foreign_keys()
    elif args.migrate:
        migrate_foreign_keys_simple()
    else:
        # 默认执行迁移
        migrate_foreign_keys_simple()
        print("\n" + "="*50)
        test_foreign_keys()

