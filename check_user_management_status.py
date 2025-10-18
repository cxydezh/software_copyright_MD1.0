#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建用户管理功能测试页面
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, Staff, User, Permission

def create_test_page():
    """创建测试页面"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 用户管理功能状态检查 ===")
            
            # 检查待审核员工
            pending_staff = Staff.query.filter_by(is_staff_account=True, approval_status='pending').all()
            print(f"待审核员工数量: {len(pending_staff)}")
            
            if pending_staff:
                print("待审核员工列表:")
                for staff in pending_staff:
                    print(f"  - {staff.name} ({staff.email})")
                    print(f"    申请理由: {staff.application_reason}")
                    print(f"    申请时间: {staff.register_date}")
                    print(f"    状态: {staff.approval_status}")
                    print("    ---")
            
            # 检查系统管理员
            admin = Staff.query.filter_by(email='admin@yiqichuang.com').first()
            if admin:
                print(f"\n系统管理员: {admin.name}")
                print(f"权限: {admin.position.position if admin.position else '未分配'}")
                print(f"审核状态: {admin.approval_status}")
            
            # 检查权限
            permissions = Permission.query.all()
            print(f"\n可用权限 ({len(permissions)}个):")
            for perm in permissions:
                print(f"  - {perm.position} (ID: {perm.id})")
            
            print("\n=== 访问说明 ===")
            print("1. 访问地址: http://127.0.0.1:5000/staff/user_management")
            print("2. 使用管理员账号登录: admin@yiqichuang.com / admin123")
            print("3. 在右上角下拉菜单中点击'用户管理'")
            print("4. 页面应该显示待审核员工账号列表")
            
            if pending_staff:
                print("\n=== 测试操作 ===")
                print("1. 点击'通过'按钮审核通过员工")
                print("2. 点击'驳回'按钮驳回员工申请")
                print("3. 为已审核通过的员工分配权限")
            
            return True
            
        except Exception as e:
            print(f"检查失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    create_test_page()
