#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理功能验证脚本
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, Staff, User, Permission

def verify_user_management_data():
    """验证用户管理页面的数据"""
    app = create_app()
    
    with app.app_context():
        print("=== 验证用户管理页面数据 ===")
        
        try:
            # 获取待审核的员工账号
            pending_staff = Staff.query.filter_by(is_staff_account=True, approval_status='pending').order_by(Staff.register_date.desc()).all()
            print(f"[OK] 待审核员工账号数量: {len(pending_staff)}")
            
            for staff in pending_staff:
                print(f"  - {staff.name} ({staff.email}) - {staff.approval_status}")
                print(f"    申请理由: {staff.application_reason}")
                print(f"    申请时间: {staff.register_date}")
            
            # 获取所有员工账号
            all_staff = Staff.query.filter_by(is_staff_account=True).order_by(Staff.register_date.desc()).all()
            print(f"\n[OK] 所有员工账号数量: {len(all_staff)}")
            
            for staff in all_staff:
                status_badge = "待审核" if staff.approval_status == 'pending' else "已通过" if staff.approval_status == 'approved' else "已驳回"
                position = staff.position.position if staff.position else "未分配"
                print(f"  - {staff.name} ({staff.email}) - {status_badge} - {position}")
            
            # 获取所有普通用户
            all_users = User.query.order_by(User.register_time.desc()).all()
            print(f"\n[OK] 所有普通用户数量: {len(all_users)}")
            
            for user in all_users:
                verified = "已验证" if user.email_verified else "未验证"
                print(f"  - {user.name} ({user.email}) - {user.user_category} - {verified}")
            
            # 检查权限数据
            permissions = Permission.query.all()
            print(f"\n[OK] 可用权限数量: {len(permissions)}")
            
            for perm in permissions:
                print(f"  - {perm.position} (ID: {perm.id})")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 验证失败: {e}")
            return False

def test_approval_operations():
    """测试审核操作"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 测试审核操作 ===")
        
        try:
            # 获取待审核的员工
            pending_staff = Staff.query.filter_by(approval_status='pending').first()
            if not pending_staff:
                print("[INFO] 没有待审核的员工账号")
                return True
            
            # 获取系统管理员
            admin = Staff.query.filter_by(email='admin@yiqichuang.com').first()
            if not admin:
                print("[ERROR] 找不到系统管理员")
                return False
            
            print(f"[OK] 找到待审核员工: {pending_staff.name}")
            print(f"[OK] 找到系统管理员: {admin.name}")
            
            # 模拟审核通过
            original_status = pending_staff.approval_status
            pending_staff.approval_status = 'approved'
            pending_staff.approval_date = datetime.utcnow()
            pending_staff.approver_id = admin.id
            
            # 分配默认权限
            default_permission = Permission.query.filter_by(position='普通业务员').first()
            if default_permission:
                pending_staff.position_id = default_permission.id
                print(f"[OK] 分配权限: {default_permission.position}")
            
            db.session.commit()
            print(f"[OK] 审核通过操作成功: {pending_staff.name}")
            
            # 恢复状态用于测试
            pending_staff.approval_status = original_status
            pending_staff.approval_date = None
            pending_staff.approver_id = None
            pending_staff.position_id = None
            db.session.commit()
            print(f"[OK] 恢复原始状态: {pending_staff.name}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 审核操作测试失败: {e}")
            db.session.rollback()
            return False

def test_rejection_operations():
    """测试驳回操作"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 测试驳回操作 ===")
        
        try:
            # 获取待审核的员工
            pending_staff = Staff.query.filter_by(approval_status='pending').first()
            if not pending_staff:
                print("[INFO] 没有待审核的员工账号")
                return True
            
            # 获取系统管理员
            admin = Staff.query.filter_by(email='admin@yiqichuang.com').first()
            if not admin:
                print("[ERROR] 找不到系统管理员")
                return False
            
            print(f"[OK] 找到待审核员工: {pending_staff.name}")
            
            # 模拟驳回
            original_status = pending_staff.approval_status
            pending_staff.approval_status = 'rejected'
            pending_staff.approval_date = datetime.utcnow()
            pending_staff.approver_id = admin.id
            pending_staff.approval_remarks = '测试驳回原因'
            
            db.session.commit()
            print(f"[OK] 驳回操作成功: {pending_staff.name}")
            
            # 恢复状态用于测试
            pending_staff.approval_status = original_status
            pending_staff.approval_date = None
            pending_staff.approver_id = None
            pending_staff.approval_remarks = None
            db.session.commit()
            print(f"[OK] 恢复原始状态: {pending_staff.name}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 驳回操作测试失败: {e}")
            db.session.rollback()
            return False

def main():
    """主验证函数"""
    print("开始验证用户管理功能...")
    
    # 验证数据
    if not verify_user_management_data():
        print("数据验证失败")
        return
    
    # 测试审核操作
    if not test_approval_operations():
        print("审核操作测试失败")
        return
    
    # 测试驳回操作
    if not test_rejection_operations():
        print("驳回操作测试失败")
        return
    
    print("\n=== 验证完成 ===")
    print("所有用户管理功能验证通过！")
    print("\n访问地址: http://127.0.0.1:5000/staff/user_management")
    print("管理员账号: admin@yiqichuang.com")
    print("管理员密码: admin123")

if __name__ == '__main__':
    main()
