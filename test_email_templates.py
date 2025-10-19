#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试员工审核邮件模板
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, Staff, Permission

def test_email_templates():
    """测试邮件模板"""
    app = create_app()
    
    with app.app_context():
        try:
            print("=== 测试员工审核邮件模板 ===")
            
            # 创建测试员工数据
            test_staff = Staff(
                name='测试员工',
                email='test@example.com',
                phone='13800138000',
                approval_status='approved',
                approval_date=datetime.utcnow(),
                application_reason='申请成为公司员工，参与项目管理'
            )
            
            # 分配权限
            permission = Permission.query.filter_by(position='普通业务员').first()
            if permission:
                test_staff.position_id = permission.id
            
            print("1. 测试审核通过邮件模板...")
            
            # 测试审核通过邮件模板渲染
            from flask import render_template_string
            with app.app_context():
                # 读取模板文件
                with open('templates/emails/staff_approval_notification.html', 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # 渲染模板
                rendered_html = render_template_string(
                    template_content,
                    staff=test_staff,
                    app_name='软件著作权管理系统',
                    app_url='http://localhost:5000'
                )
                
                # 保存渲染结果
                with open('test_approval_email.html', 'w', encoding='utf-8') as f:
                    f.write(rendered_html)
                
                print("[OK] 审核通过邮件模板渲染成功")
                print("    - 模板文件: templates/emails/staff_approval_notification.html")
                print("    - 测试文件: test_approval_email.html")
            
            print("\n2. 测试驳回邮件模板...")
            
            # 更新测试员工状态为驳回
            test_staff.approval_status = 'rejected'
            test_staff.approval_remarks = '申请理由不够详细，请重新填写更具体的申请理由'
            
            # 测试驳回邮件模板渲染
            with open('templates/emails/staff_rejection_notification.html', 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            rendered_html = render_template_string(
                template_content,
                staff=test_staff,
                rejection_reason=test_staff.approval_remarks,
                app_name='软件著作权管理系统',
                app_url='http://localhost:5000'
            )
            
            # 保存渲染结果
            with open('test_rejection_email.html', 'w', encoding='utf-8') as f:
                f.write(rendered_html)
            
            print("[OK] 驳回邮件模板渲染成功")
            print("    - 模板文件: templates/emails/staff_rejection_notification.html")
            print("    - 测试文件: test_rejection_email.html")
            
            print("\n=== 邮件模板测试完成 ===")
            print("您可以在浏览器中打开以下文件查看邮件效果：")
            print("1. test_approval_email.html - 审核通过邮件")
            print("2. test_rejection_email.html - 驳回邮件")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 邮件模板测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_email_functions():
    """测试邮件发送函数"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n=== 测试邮件发送函数 ===")
            
            from web_app.utils.email import send_staff_approval_notification, send_staff_rejection_notification
            
            # 创建测试员工
            test_staff = Staff(
                name='邮件测试员工',
                email='test_email@example.com',
                phone='13800138001',
                approval_status='approved',
                approval_date=datetime.utcnow(),
                application_reason='测试邮件发送功能'
            )
            
            print("1. 测试审核通过邮件发送函数...")
            print(f"    - 函数: send_staff_approval_notification")
            print(f"    - 参数: staff={test_staff.name}")
            
            print("2. 测试驳回邮件发送函数...")
            print(f"    - 函数: send_staff_rejection_notification")
            print(f"    - 参数: staff={test_staff.name}, rejection_reason='测试驳回原因'")
            
            print("[OK] 邮件发送函数导入成功")
            print("注意: 实际发送需要配置邮件服务器")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] 邮件发送函数测试失败: {e}")
            return False

if __name__ == '__main__':
    print("开始测试员工审核邮件模板...")
    
    # 测试邮件模板
    if test_email_templates():
        print("\n" + "="*50)
        
        # 测试邮件发送函数
        if test_email_functions():
            print("\n[SUCCESS] 所有邮件模板测试通过！")
        else:
            print("\n[ERROR] 邮件发送函数测试失败")
    else:
        print("\n[ERROR] 邮件模板测试失败")

