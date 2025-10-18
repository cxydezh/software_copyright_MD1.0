#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试员工账号用于验证用户管理功能
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, Staff

def create_test_staff():
    """创建测试员工账号"""
    app = create_app()
    
    with app.app_context():
        try:
            # 检查是否已存在
            existing_staff = Staff.query.filter_by(email='test_pending@example.com').first()
            if existing_staff:
                print(f"删除现有测试员工: {existing_staff.name}")
                db.session.delete(existing_staff)
                db.session.commit()
            
            # 创建待审核的测试员工
            test_staff = Staff(
                name='待审核员工',
                email='test_pending@example.com',
                phone='13800138003',
                is_staff_account=True,
                approval_status='pending',
                application_reason='申请成为公司员工，参与软件著作权项目管理'
            )
            test_staff.set_password('test123')
            
            db.session.add(test_staff)
            db.session.commit()
            
            print(f"[OK] 创建待审核员工账号成功: {test_staff.name}")
            print(f"  - 邮箱: {test_staff.email}")
            print(f"  - 审核状态: {test_staff.approval_status}")
            print(f"  - 申请理由: {test_staff.application_reason}")
            print(f"  - 密码: test123")
            
            return test_staff
            
        except Exception as e:
            print(f"[ERROR] 创建测试员工失败: {e}")
            db.session.rollback()
            return None

if __name__ == '__main__':
    create_test_staff()
