#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
员工账号注册和审核功能测试脚本（简化版）
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, Staff, User, Permission

def test_staff_registration():
    """测试员工账号注册功能"""
    app = create_app()
    
    with app.app_context():
        print("=== 测试员工账号注册功能 ===")
        
        # 测试数据
        test_staff_data = {
            'name': '测试员工',
            'email': 'test_staff@example.com',
            'phone': '13800138001',
            'is_staff_account': True,
            'approval_status': 'pending',
            'application_reason': '申请成为公司员工，参与项目管理'
        }
        
        try:
            # 检查是否已存在
            existing_staff = Staff.query.filter_by(email=test_staff_data['email']).first()
            if existing_staff:
                print(f"删除现有测试员工: {existing_staff.name}")
                db.session.delete(existing_staff)
                db.session.commit()
            
            # 创建测试员工
            test_staff = Staff(**test_staff_data)
            test_staff.set_password('test123')
            
            db.session.add(test_staff)
            db.session.commit()
            
            print(f"[OK] 员工账号注册成功: {test_staff.name}")
            print(f"  - 邮箱: {test_staff.email}")
            print(f"  - 审核状态: {test_staff.approval_status}")
            print(f"  - 申请理由: {test_staff.application_reason}")
            
            return test_staff
            
        except Exception as e:
            print(f"[ERROR] 员工账号注册失败: {e}")
            db.session.rollback()
            return None

def test_admin_approval(staff_id):
    """测试管理员审核功能"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 测试管理员审核功能 ===")
        
        try:
            # 获取测试员工
            test_staff = Staff.query.get(staff_id)
            if not test_staff:
                print("[ERROR] 找不到测试员工")
                return False
            
            # 获取系统管理员
            admin = Staff.query.filter_by(email='admin@yiqichuang.com').first()
            if not admin:
                print("[ERROR] 找不到系统管理员")
                return False
            
            print(f"[OK] 找到系统管理员: {admin.name}")
            
            # 模拟审核通过
            test_staff.approval_status = 'approved'
            test_staff.approval_date = datetime.utcnow()
            test_staff.approver_id = admin.id
            
            # 分配默认权限
            default_permission = Permission.query.filter_by(position='普通业务员').first()
            if default_permission:
                test_staff.position_id = default_permission.id
                print(f"[OK] 分配权限: {default_permission.position}")
            
            db.session.commit()
            
            print(f"[OK] 员工账号审核通过: {test_staff.name}")
            print(f"  - 审核状态: {test_staff.approval_status}")
            print(f"  - 审核时间: {test_staff.approval_date}")
            print(f"  - 审核者: {admin.name}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 审核功能测试失败: {e}")
            db.session.rollback()
            return False

def test_permission_assignment(staff_id):
    """测试权限分配功能"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 测试权限分配功能 ===")
        
        try:
            # 获取测试员工
            test_staff = Staff.query.get(staff_id)
            if not test_staff:
                print("[ERROR] 找不到测试员工")
                return False
            
            # 获取项目执行者权限
            executor_permission = Permission.query.filter_by(position='项目执行者').first()
            if not executor_permission:
                print("[ERROR] 找不到项目执行者权限")
                return False
            
            # 分配权限
            test_staff.position_id = executor_permission.id
            db.session.commit()
            
            print(f"[OK] 权限分配成功: {test_staff.name}")
            print(f"  - 新权限: {executor_permission.position}")
            print(f"  - 权限ID: {executor_permission.id}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 权限分配测试失败: {e}")
            db.session.rollback()
            return False

def test_user_registration():
    """测试普通用户注册功能"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 测试普通用户注册功能 ===")
        
        # 测试数据
        test_user_data = {
            'name': '测试用户',
            'email': 'test_user@example.com',
            'phone': '13800138002',
            'user_category': '软件著作权'
        }
        
        try:
            # 检查是否已存在
            existing_user = User.query.filter_by(email=test_user_data['email']).first()
            if existing_user:
                print(f"删除现有测试用户: {existing_user.name}")
                db.session.delete(existing_user)
                db.session.commit()
            
            # 创建测试用户
            test_user = User(**test_user_data)
            test_user.set_password('test123')
            
            db.session.add(test_user)
            db.session.commit()
            
            print(f"[OK] 普通用户注册成功: {test_user.name}")
            print(f"  - 邮箱: {test_user.email}")
            print(f"  - 用户类别: {test_user.user_category}")
            
            return test_user
            
        except Exception as e:
            print(f"[ERROR] 普通用户注册失败: {e}")
            db.session.rollback()
            return None

def test_login_restrictions():
    """测试登录限制功能"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 测试登录限制功能 ===")
        
        try:
            # 测试待审核员工登录
            pending_staff = Staff.query.filter_by(approval_status='pending').first()
            if pending_staff:
                print(f"[OK] 找到待审核员工: {pending_staff.name}")
                print(f"  - 审核状态: {pending_staff.approval_status}")
                print("  - 该员工在审核通过前无法登录工作台")
            
            # 测试已审核员工登录
            approved_staff = Staff.query.filter_by(approval_status='approved').first()
            if approved_staff:
                print(f"[OK] 找到已审核员工: {approved_staff.name}")
                print(f"  - 审核状态: {approved_staff.approval_status}")
                print("  - 该员工可以正常登录工作台")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 登录限制测试失败: {e}")
            return False

def cleanup_test_data():
    """清理测试数据"""
    app = create_app()
    
    with app.app_context():
        print("\n=== 清理测试数据 ===")
        
        try:
            # 删除测试员工
            test_staff = Staff.query.filter_by(email='test_staff@example.com').first()
            if test_staff:
                db.session.delete(test_staff)
                print(f"[OK] 删除测试员工: {test_staff.name}")
            
            # 删除测试用户
            test_user = User.query.filter_by(email='test_user@example.com').first()
            if test_user:
                db.session.delete(test_user)
                print(f"[OK] 删除测试用户: {test_user.name}")
            
            db.session.commit()
            print("[OK] 测试数据清理完成")
            
        except Exception as e:
            print(f"[ERROR] 测试数据清理失败: {e}")
            db.session.rollback()

def main():
    """主测试函数"""
    print("开始测试员工账号注册和审核功能...")
    
    # 测试员工注册
    test_staff = test_staff_registration()
    if not test_staff:
        print("员工注册测试失败，终止测试")
        return
    
    # 测试管理员审核
    if not test_admin_approval(test_staff.id):
        print("管理员审核测试失败")
    
    # 测试权限分配
    if not test_permission_assignment(test_staff.id):
        print("权限分配测试失败")
    
    # 测试普通用户注册
    test_user = test_user_registration()
    if not test_user:
        print("普通用户注册测试失败")
    
    # 测试登录限制
    if not test_login_restrictions():
        print("登录限制测试失败")
    
    # 清理测试数据
    cleanup_test_data()
    
    print("\n=== 测试完成 ===")
    print("所有功能测试完成！")

if __name__ == '__main__':
    main()
