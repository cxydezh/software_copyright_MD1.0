#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试用户管理页面数据传递
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, Staff, User

def debug_user_management():
    """调试用户管理页面数据"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 调试用户管理页面数据 ===")
            
            # 模拟用户管理视图的数据查询
            pending_staff = Staff.query.filter_by(is_staff_account=True, approval_status='pending').order_by(Staff.register_date.desc()).all()
            all_staff = Staff.query.filter_by(is_staff_account=True).order_by(Staff.register_date.desc()).all()
            all_users = User.query.order_by(User.register_time.desc()).all()
            
            print(f"pending_staff 数量: {len(pending_staff)}")
            print(f"all_staff 数量: {len(all_staff)}")
            print(f"all_users 数量: {len(all_users)}")
            
            print("\n=== pending_staff 详细信息 ===")
            for staff in pending_staff:
                print(f"ID: {staff.id}")
                print(f"姓名: {staff.name}")
                print(f"邮箱: {staff.email}")
                print(f"is_staff_account: {staff.is_staff_account}")
                print(f"approval_status: {staff.approval_status}")
                print(f"application_reason: {staff.application_reason}")
                print(f"register_date: {staff.register_date}")
                print("---")
            
            # 检查模板变量
            print("\n=== 模板变量检查 ===")
            print(f"pending_staff 是否为真: {bool(pending_staff)}")
            print(f"pending_staff 长度: {len(pending_staff) if pending_staff else 0}")
            
            # 检查是否有空值
            if pending_staff:
                print("pending_staff 不为空")
                for i, staff in enumerate(pending_staff):
                    print(f"  [{i}] {staff.name} - {staff.approval_status}")
            else:
                print("pending_staff 为空")
            
            return True
            
        except Exception as e:
            print(f"调试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    debug_user_management()
