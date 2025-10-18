#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查待审核员工数据
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, Staff

def check_pending_staff():
    """检查待审核员工数据"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查所有员工账号
            all_staff = Staff.query.filter_by(is_staff_account=True).all()
            print(f"所有员工账号数量: {len(all_staff)}")
            
            for staff in all_staff:
                print(f"- {staff.name} ({staff.email}) - {staff.approval_status}")
            
            # 检查待审核员工
            pending_staff = Staff.query.filter_by(is_staff_account=True, approval_status='pending').all()
            print(f"\n待审核员工数量: {len(pending_staff)}")
            
            for staff in pending_staff:
                print(f"- {staff.name} ({staff.email}) - {staff.approval_status}")
                print(f"  申请理由: {staff.application_reason}")
                print(f"  申请时间: {staff.register_date}")
            
            return len(pending_staff) > 0
            
        except Exception as e:
            print(f"检查失败: {e}")
            return False

if __name__ == '__main__':
    check_pending_staff()
