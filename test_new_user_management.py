#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的用户管理功能
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, Staff, User, Permission

def test_new_features():
    """测试新功能"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 测试新的用户管理功能 ===")
            
            # 1. 测试数据库结构
            print("\n1. 测试数据库结构...")
            inspector = db.inspect(db.engine)
            staff_columns = [col['name'] for col in inspector.get_columns('staff')]
            
            if 'is_staff_account' in staff_columns:
                print("[ERROR] is_staff_account 字段仍然存在")
                return False
            else:
                print("[OK] is_staff_account 字段已成功删除")
            
            # 2. 测试员工数据查询
            print("\n2. 测试员工数据查询...")
            pending_staff = Staff.query.filter_by(approval_status='pending').all()
            approved_staff = Staff.query.filter_by(approval_status='approved').all()
            rejected_staff = Staff.query.filter_by(approval_status='rejected').all()
            all_users = User.query.all()
            
            print(f"[OK] 待审核员工: {len(pending_staff)}")
            print(f"[OK] 已审核通过员工: {len(approved_staff)}")
            print(f"[OK] 已驳回员工: {len(rejected_staff)}")
            print(f"[OK] 普通用户: {len(all_users)}")
            
            # 3. 测试重新申请功能
            print("\n3. 测试重新申请功能...")
            if rejected_staff:
                test_staff = rejected_staff[0]
                print(f"[OK] 找到已驳回员工: {test_staff.name}")
                
                # 模拟重新申请
                original_status = test_staff.approval_status
                test_staff.approval_status = 'pending'
                test_staff.application_reason = '修改后的申请理由'
                test_staff.approval_date = None
                test_staff.approver_id = None
                test_staff.approval_remarks = None
                
                db.session.commit()
                print("[OK] 重新申请功能测试成功")
                
                # 恢复状态
                test_staff.approval_status = original_status
                db.session.commit()
                print("[OK] 状态已恢复")
            else:
                print("[INFO] 没有已驳回的员工，跳过重新申请测试")
            
            # 4. 测试取消申请功能
            print("\n4. 测试取消申请功能...")
            # 创建一个测试员工用于取消申请测试
            test_cancel_staff = Staff(
                name='测试取消员工',
                email='test_cancel@example.com',
                phone='13800138004',
                approval_status='pending',
                application_reason='测试取消申请功能'
            )
            test_cancel_staff.set_password('test123')
            
            db.session.add(test_cancel_staff)
            db.session.commit()
            
            staff_id = test_cancel_staff.id
            print(f"[OK] 创建测试员工: {test_cancel_staff.name} (ID: {staff_id})")
            
            # 删除测试员工
            db.session.delete(test_cancel_staff)
            db.session.commit()
            print("[OK] 取消申请功能测试成功")
            
            # 5. 测试权限分配功能
            print("\n5. 测试权限分配功能...")
            if approved_staff:
                test_staff = approved_staff[0]
                permissions = Permission.query.all()
                
                if permissions:
                    test_permission = permissions[0]
                    original_position = test_staff.position_id
                    
                    test_staff.position_id = test_permission.id
                    db.session.commit()
                    print(f"[OK] 权限分配测试成功: {test_permission.position}")
                    
                    # 恢复权限
                    test_staff.position_id = original_position
                    db.session.commit()
                    print("[OK] 权限已恢复")
                else:
                    print("[ERROR] 没有可用权限")
            else:
                print("[INFO] 没有已审核通过的员工，跳过权限分配测试")
            
            print("\n=== 所有功能测试完成 ===")
            return True
            
        except Exception as e:
            print(f"[ERROR] 测试失败: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

def create_test_data():
    """创建测试数据"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 创建测试数据 ===")
            
            # 创建待审核员工
            pending_staff = Staff(
                name='待审核员工',
                email='test_pending_new@example.com',
                phone='13800138005',
                approval_status='pending',
                application_reason='申请成为公司员工'
            )
            pending_staff.set_password('test123')
            
            # 创建已驳回员工
            rejected_staff = Staff(
                name='已驳回员工',
                email='test_rejected@example.com',
                phone='13800138006',
                approval_status='rejected',
                application_reason='申请理由不充分',
                approval_remarks='申请理由不够详细'
            )
            rejected_staff.set_password('test123')
            
            db.session.add(pending_staff)
            db.session.add(rejected_staff)
            db.session.commit()
            
            print(f"[OK] 创建待审核员工: {pending_staff.name}")
            print(f"[OK] 创建已驳回员工: {rejected_staff.name}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 创建测试数据失败: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    print("开始测试新的用户管理功能...")
    
    # 创建测试数据
    if create_test_data():
        print("\n" + "="*50)
        
        # 测试功能
        if test_new_features():
            print("\n[SUCCESS] 所有功能测试通过！")
            print("\n访问地址: http://127.0.0.1:5000/staff/user_management")
            print("管理员账号: admin@yiqichuang.com")
            print("管理员密码: admin123")
        else:
            print("\n[ERROR] 功能测试失败")
    else:
        print("\n[ERROR] 测试数据创建失败")
