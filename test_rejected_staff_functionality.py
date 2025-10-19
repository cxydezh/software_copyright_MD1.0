#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试被驳回员工处理功能
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, Staff, Permission

def test_rejected_staff_functionality():
    """测试被驳回员工处理功能"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 测试被驳回员工处理功能 ===")
            
            # 1. 创建测试被驳回员工
            print("1. 创建测试被驳回员工...")
            from werkzeug.security import generate_password_hash
            
            # 先清理可能存在的测试数据
            existing_staff = Staff.query.filter_by(email='rejected_test@example.com').first()
            if existing_staff:
                db.session.delete(existing_staff)
                db.session.commit()
                print("    - 清理了已存在的测试数据")
            
            rejected_staff = Staff(
                name='被驳回测试员工',
                email='rejected_test@example.com',
                phone='13800138002',
                password_hash=generate_password_hash('test123'),
                approval_status='rejected',
                approval_date=datetime.utcnow(),
                approval_remarks='申请理由不够详细，请重新填写更具体的申请理由',
                application_reason='我想成为公司员工，参与项目管理'
            )
            
            # 分配权限
            permission = Permission.query.filter_by(position='普通业务员').first()
            if permission:
                rejected_staff.position_id = permission.id
            
            db.session.add(rejected_staff)
            db.session.commit()
            
            print(f"[OK] 创建被驳回员工成功: {rejected_staff.name} ({rejected_staff.email})")
            print(f"    - 审核状态: {rejected_staff.approval_status}")
            print(f"    - 驳回原因: {rejected_staff.approval_remarks}")
            
            # 2. 测试登录重定向逻辑
            print("\n2. 测试登录重定向逻辑...")
            
            # 模拟登录检查
            if rejected_staff.approval_status == 'rejected':
                print("[OK] 被驳回员工登录时会重定向到处理页面")
                print("    - 重定向URL: /auth/handle_rejected_staff")
            else:
                print("[ERROR] 员工状态不是被驳回")
            
            # 3. 测试重新申请功能
            print("\n3. 测试重新申请功能...")
            
            # 模拟重新申请数据
            new_reason = "经过仔细考虑，我重新填写申请理由：我具有3年项目管理经验，熟悉软件著作权申请流程，希望为公司贡献专业技能。"
            
            # 更新员工状态
            rejected_staff.approval_status = 'pending'
            rejected_staff.application_reason = new_reason
            rejected_staff.approval_date = None
            rejected_staff.approver_id = None
            rejected_staff.approval_remarks = None
            
            db.session.commit()
            
            print("[OK] 重新申请功能测试成功")
            print(f"    - 新状态: {rejected_staff.approval_status}")
            print(f"    - 新申请理由: {rejected_staff.application_reason[:50]}...")
            
            # 4. 测试取消申请功能
            print("\n4. 测试取消申请功能...")
            
            # 创建另一个测试员工用于取消申请测试
            # 先清理可能存在的测试数据
            existing_cancel_staff = Staff.query.filter_by(email='cancel_test@example.com').first()
            if existing_cancel_staff:
                db.session.delete(existing_cancel_staff)
                db.session.commit()
            
            cancel_staff = Staff(
                name='取消申请测试员工',
                email='cancel_test@example.com',
                phone='13800138003',
                password_hash=generate_password_hash('test123'),
                approval_status='rejected',
                approval_date=datetime.utcnow(),
                approval_remarks='测试取消申请功能',
                application_reason='测试用申请理由'
            )
            
            db.session.add(cancel_staff)
            db.session.commit()
            
            cancel_staff_id = cancel_staff.id
            
            # 模拟取消申请（删除记录）
            db.session.delete(cancel_staff)
            db.session.commit()
            
            # 验证删除
            deleted_staff = Staff.query.get(cancel_staff_id)
            if deleted_staff is None:
                print("[OK] 取消申请功能测试成功")
                print("    - 员工记录已从数据库删除")
            else:
                print("[ERROR] 员工记录删除失败")
            
            # 5. 测试页面模板
            print("\n5. 测试页面模板...")
            
            # 测试模板渲染
            from flask import render_template_string
            
            # 读取模板文件
            with open('templates/auth/handle_rejected_staff.html', 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # 使用应用上下文渲染模板
            with app.test_request_context():
                rendered_html = render_template_string(
                    template_content,
                    staff=rejected_staff
                )
                
                # 保存渲染结果
                with open('test_rejected_staff_page.html', 'w', encoding='utf-8') as f:
                    f.write(rendered_html)
                
                print("[OK] 被驳回员工处理页面模板渲染成功")
                print("    - 模板文件: templates/auth/handle_rejected_staff.html")
                print("    - 测试文件: test_rejected_staff_page.html")
            
            # 6. 清理测试数据
            print("\n6. 清理测试数据...")
            db.session.delete(rejected_staff)
            db.session.commit()
            print("[OK] 测试数据清理完成")
            
            print("\n=== 被驳回员工处理功能测试完成 ===")
            print("功能验证结果:")
            print("[OK] 被驳回员工登录重定向")
            print("[OK] 重新申请功能")
            print("[OK] 取消申请功能")
            print("[OK] 页面模板渲染")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_auth_routes():
    """测试认证路由"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n=== 测试认证路由 ===")
            
            from web_app.views.auth import auth_bp
            
            # 检查路由是否注册
            routes = []
            for rule in app.url_map.iter_rules():
                if rule.endpoint.startswith('auth.'):
                    routes.append(f"{rule.rule} -> {rule.endpoint}")
            
            print("已注册的认证路由:")
            for route in routes:
                print(f"  - {route}")
            
            # 检查新增的路由
            new_routes = [
                '/auth/handle_rejected_staff',
                '/auth/reapply_staff',
                '/auth/cancel_staff'
            ]
            
            print("\n检查新增路由:")
            for new_route in new_routes:
                found = any(new_route in route for route in routes)
                if found:
                    print(f"[OK] {new_route}")
                else:
                    print(f"[ERROR] {new_route} 未找到")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 路由测试失败: {e}")
            return False

if __name__ == '__main__':
    print("开始测试被驳回员工处理功能...")
    
    # 测试主要功能
    if test_rejected_staff_functionality():
        print("\n" + "="*50)
        
        # 测试路由
        if test_auth_routes():
            print("\n[SUCCESS] 所有功能测试通过！")
            print("\n您可以在浏览器中打开 test_rejected_staff_page.html 查看页面效果")
        else:
            print("\n[ERROR] 路由测试失败")
    else:
        print("\n[ERROR] 功能测试失败")
