#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试取消申请功能
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, Staff, Permission

def create_test_rejected_staff():
    """创建一个被驳回的测试员工"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 创建被驳回测试员工 ===")
            
            from werkzeug.security import generate_password_hash
            
            # 先清理可能存在的测试数据
            existing_staff = Staff.query.filter_by(email='manual_test@example.com').first()
            if existing_staff:
                db.session.delete(existing_staff)
                db.session.commit()
                print("    - 清理了已存在的测试数据")
            
            test_staff = Staff(
                name='手动测试员工',
                email='manual_test@example.com',
                phone='13800138007',
                password_hash=generate_password_hash('test123'),
                approval_status='rejected',
                approval_date=datetime.utcnow(),
                approval_remarks='申请理由不够详细，请重新填写更具体的申请理由',
                application_reason='我想成为公司员工，参与项目管理'
            )
            
            # 分配权限
            permission = Permission.query.filter_by(position='普通业务员').first()
            if permission:
                test_staff.position_id = permission.id
            
            db.session.add(test_staff)
            db.session.commit()
            
            print(f"[OK] 创建被驳回员工成功:")
            print(f"    - 姓名: {test_staff.name}")
            print(f"    - 邮箱: {test_staff.email}")
            print(f"    - 密码: test123")
            print(f"    - 状态: {test_staff.approval_status}")
            print(f"    - 驳回原因: {test_staff.approval_remarks}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 创建测试员工失败: {e}")
            return False

if __name__ == '__main__':
    print("创建测试员工...")
    
    if create_test_rejected_staff():
        print("\n[SUCCESS] 测试员工创建成功！")
        print("\n现在您可以:")
        print("1. 访问 http://127.0.0.1:5000/auth/login")
        print("2. 使用邮箱: manual_test@example.com")
        print("3. 使用密码: test123")
        print("4. 选择用户类型: 员工")
        print("5. 登录后会自动跳转到被驳回员工处理页面")
        print("6. 点击'取消申请'按钮测试修复效果")
    else:
        print("\n[ERROR] 测试员工创建失败")








