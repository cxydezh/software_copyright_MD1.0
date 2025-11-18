#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试系统设置功能
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from database.models import db, SystemSettings, Staff, Permission, User, Project
from werkzeug.security import generate_password_hash

def test_system_settings():
    """测试系统设置功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("开始测试系统设置功能")
        print("=" * 60)
        
        # 清理测试数据
        print("\n[1] 清理测试数据...")
        try:
            SystemSettings.query.filter_by(setting_key='apply_business_customer_phone_required').delete()
            SystemSettings.query.filter_by(setting_key='apply_business_customer_email_required').delete()
            db.session.commit()
            print("  [OK] 测试数据已清理")
        except Exception as e:
            print(f"  [ERROR] 清理测试数据失败: {e}")
            db.session.rollback()
        
        # 测试1: 创建和读取设置
        print("\n[2] 测试创建和读取设置...")
        try:
            # 创建设置
            SystemSettings.set_setting('apply_business_customer_phone_required', 'true', '测试：客户电话是否必填', None)
            SystemSettings.set_setting('apply_business_customer_email_required', 'false', '测试：客户邮箱是否必填', None)
            
            # 读取设置
            phone_required = SystemSettings.get_setting('apply_business_customer_phone_required', 'false')
            email_required = SystemSettings.get_setting('apply_business_customer_email_required', 'true')
            
            assert phone_required == 'true', "客户电话必填设置应该为true"
            assert email_required == 'false', "客户邮箱必填设置应该为false"
            
            print(f"  [OK] 客户电话必填: {phone_required}")
            print(f"  [OK] 客户邮箱必填: {email_required}")
        except Exception as e:
            print(f"  [ERROR] 测试失败: {e}")
            return False
        
        # 测试2: 更新设置
        print("\n[3] 测试更新设置...")
        try:
            SystemSettings.set_setting('apply_business_customer_phone_required', 'false', '测试：客户电话是否必填', None)
            phone_required = SystemSettings.get_setting('apply_business_customer_phone_required', 'true')
            assert phone_required == 'false', "客户电话必填设置应该更新为false"
            print(f"  [OK] 设置已更新: {phone_required}")
        except Exception as e:
            print(f"  [ERROR] 测试失败: {e}")
            return False
        
        # 测试3: 测试系统管理员访问权限
        print("\n[4] 测试系统管理员访问权限...")
        try:
            # 获取系统管理员
            admin_permission = Permission.query.filter_by(position='系统管理员').first()
            if not admin_permission:
                print("  [SKIP] 未找到系统管理员权限，跳过权限测试")
            else:
                admin_staff = Staff.query.filter_by(position_id=admin_permission.id).first()
                if admin_staff:
                    print(f"  [OK] 找到系统管理员: {admin_staff.name}")
                else:
                    print("  [SKIP] 未找到系统管理员账户")
        except Exception as e:
            print(f"  [ERROR] 测试失败: {e}")
            return False
        
        # 测试4: 测试apply_business验证逻辑
        print("\n[5] 测试apply_business验证逻辑...")
        try:
            # 设置客户电话为非必填，客户邮箱为必填
            SystemSettings.set_setting('apply_business_customer_phone_required', 'false', '测试', None)
            SystemSettings.set_setting('apply_business_customer_email_required', 'true', '测试', None)
            
            phone_required = SystemSettings.get_setting('apply_business_customer_phone_required', 'true').lower() == 'true'
            email_required = SystemSettings.get_setting('apply_business_customer_email_required', 'true').lower() == 'true'
            
            assert phone_required == False, "客户电话应该为非必填"
            assert email_required == True, "客户邮箱应该为必填"
            
            print(f"  [OK] 客户电话必填: {phone_required}")
            print(f"  [OK] 客户邮箱必填: {email_required}")
            
            # 测试验证逻辑
            # 模拟表单数据：缺少邮箱（必填）
            customer_name = "测试客户"
            customer_email = ""  # 必填但为空
            customer_phone = ""  # 非必填，可以为空
            project_name = "测试项目"
            project_type = "软件登记业务"
            applicant_type = "个人"
            copyright_owner = "测试著作权人"
            
            # 验证必填字段
            required_fields = [customer_name, project_name, project_type, applicant_type, copyright_owner]
            if email_required:
                required_fields.append(customer_email)
            if phone_required:
                required_fields.append(customer_phone)
            
            # 应该验证失败（缺少邮箱）
            assert not all(required_fields), "验证应该失败（缺少必填的邮箱）"
            print("  [OK] 验证逻辑正确：缺少必填邮箱时验证失败")
            
            # 测试：填写邮箱，不填写电话（应该通过）
            customer_email = "test@example.com"
            required_fields = [customer_name, project_name, project_type, applicant_type, copyright_owner]
            if email_required:
                required_fields.append(customer_email)
            if phone_required:
                required_fields.append(customer_phone)
            
            assert all(required_fields), "验证应该通过（填写了必填的邮箱，电话非必填）"
            print("  [OK] 验证逻辑正确：填写必填邮箱，电话非必填时验证通过")
            
        except Exception as e:
            print(f"  [ERROR] 测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 测试5: 恢复默认设置
        print("\n[6] 恢复默认设置...")
        try:
            SystemSettings.set_setting('apply_business_customer_phone_required', 'true', '代客申请时客户电话是否必填', None)
            SystemSettings.set_setting('apply_business_customer_email_required', 'true', '代客申请时客户邮箱是否必填', None)
            print("  [OK] 默认设置已恢复")
        except Exception as e:
            print(f"  [ERROR] 恢复设置失败: {e}")
            return False
        
        print("\n" + "=" * 60)
        print("所有测试通过！")
        print("=" * 60)
        return True

if __name__ == '__main__':
    success = test_system_settings()
    sys.exit(0 if success else 1)
