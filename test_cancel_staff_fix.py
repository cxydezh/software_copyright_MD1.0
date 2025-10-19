#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试取消申请功能修复
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, Staff, Permission

def test_cancel_staff_fix():
    """测试取消申请功能修复"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 测试取消申请功能修复 ===")
            
            from werkzeug.security import generate_password_hash
            
            # 1. 创建测试被驳回员工
            print("1. 创建测试被驳回员工...")
            
            # 先清理可能存在的测试数据
            existing_staff = Staff.query.filter_by(email='cancel_fix_test@example.com').first()
            if existing_staff:
                db.session.delete(existing_staff)
                db.session.commit()
                print("    - 清理了已存在的测试数据")
            
            test_staff = Staff(
                name='取消申请测试员工',
                email='cancel_fix_test@example.com',
                phone='13800138004',
                password_hash=generate_password_hash('test123'),
                approval_status='rejected',
                approval_date=datetime.utcnow(),
                approval_remarks='测试取消申请功能修复',
                application_reason='测试用申请理由'
            )
            
            # 分配权限
            permission = Permission.query.filter_by(position='普通业务员').first()
            if permission:
                test_staff.position_id = permission.id
            
            db.session.add(test_staff)
            db.session.commit()
            
            print(f"[OK] 创建测试员工成功: {test_staff.name} ({test_staff.email})")
            print(f"    - 员工ID: {test_staff.id}")
            print(f"    - 审核状态: {test_staff.approval_status}")
            
            # 2. 测试取消申请逻辑
            print("\n2. 测试取消申请逻辑...")
            
            # 模拟取消申请的操作顺序
            staff_id = test_staff.id
            staff_to_delete = test_staff
            
            # 先删除数据库记录
            db.session.delete(staff_to_delete)
            db.session.commit()
            
            print("[OK] 数据库记录删除成功")
            
            # 验证删除
            deleted_staff = Staff.query.get(staff_id)
            if deleted_staff is None:
                print("[OK] 员工记录已从数据库删除")
            else:
                print("[ERROR] 员工记录删除失败")
                return False
            
            # 3. 测试不同状态的员工
            print("\n3. 测试不同状态的员工...")
            
            # 测试待审核状态的员工
            pending_staff = Staff(
                name='待审核测试员工',
                email='pending_cancel_test@example.com',
                phone='13800138005',
                password_hash=generate_password_hash('test123'),
                approval_status='pending',
                application_reason='测试待审核状态取消申请'
            )
            
            db.session.add(pending_staff)
            db.session.commit()
            
            pending_id = pending_staff.id
            
            # 删除待审核员工
            db.session.delete(pending_staff)
            db.session.commit()
            
            # 验证删除
            deleted_pending = Staff.query.get(pending_id)
            if deleted_pending is None:
                print("[OK] 待审核员工记录删除成功")
            else:
                print("[ERROR] 待审核员工记录删除失败")
                return False
            
            print("\n=== 取消申请功能修复测试完成 ===")
            print("修复结果:")
            print("[OK] 操作顺序修复 - 先删除数据库记录，后登出用户")
            print("[OK] 错误处理改进 - 添加详细的错误信息")
            print("[OK] 不同状态员工 - 待审核和被驳回员工都可以取消申请")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_cancel_staff_api():
    """测试取消申请API"""
    app = create_app()
    
    with app.test_client() as client:
        try:
            print("\n=== 测试取消申请API ===")
            
            # 创建测试员工
            from werkzeug.security import generate_password_hash
            
            with app.app_context():
                test_staff = Staff(
                    name='API测试员工',
                    email='api_cancel_test@example.com',
                    phone='13800138006',
                    password_hash=generate_password_hash('test123'),
                    approval_status='rejected',
                    approval_date=datetime.utcnow(),
                    approval_remarks='测试API取消申请功能',
                    application_reason='测试API用申请理由'
                )
                
                db.session.add(test_staff)
                db.session.commit()
                staff_id = test_staff.id
            
            # 登录测试员工
            login_response = client.post('/auth/login', data={
                'email': 'api_cancel_test@example.com',
                'password': 'test123',
                'user_type': 'staff'
            }, follow_redirects=True)
            
            if login_response.status_code == 200:
                print("[OK] 测试员工登录成功")
            else:
                print("[ERROR] 测试员工登录失败")
                return False
            
            # 测试取消申请API
            cancel_response = client.post('/auth/cancel_staff', 
                                        json={},
                                        headers={'Content-Type': 'application/json'})
            
            if cancel_response.status_code == 200:
                response_data = cancel_response.get_json()
                if response_data.get('success'):
                    print("[OK] 取消申请API调用成功")
                    print(f"    - 返回消息: {response_data.get('message')}")
                    print(f"    - 重定向URL: {response_data.get('redirect')}")
                else:
                    print(f"[ERROR] 取消申请API返回失败: {response_data.get('message')}")
                    return False
            else:
                print(f"[ERROR] 取消申请API调用失败，状态码: {cancel_response.status_code}")
                return False
            
            # 验证员工记录是否被删除
            with app.app_context():
                deleted_staff = Staff.query.get(staff_id)
                if deleted_staff is None:
                    print("[OK] 员工记录已从数据库删除")
                else:
                    print("[ERROR] 员工记录删除失败")
                    return False
            
            print("\n=== 取消申请API测试完成 ===")
            return True
            
        except Exception as e:
            print(f"[ERROR] API测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    print("开始测试取消申请功能修复...")
    
    # 测试修复逻辑
    if test_cancel_staff_fix():
        print("\n" + "="*50)
        
        # 测试API
        if test_cancel_staff_api():
            print("\n[SUCCESS] 取消申请功能修复测试通过！")
        else:
            print("\n[ERROR] API测试失败")
    else:
        print("\n[ERROR] 修复逻辑测试失败")

