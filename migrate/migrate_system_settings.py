#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建系统设置表
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, SystemSettings

def migrate_system_settings():
    """创建系统设置表"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("开始创建系统设置表")
        print("=" * 60)
        
        try:
            # 创建表
            print("\n[1] 创建system_settings表...")
            db.create_all()
            print("  [OK] 表创建成功")
            
            # 检查表是否存在
            print("\n[2] 验证表结构...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'system_settings' in tables:
                print("  [OK] system_settings表已存在")
            else:
                print("  [ERROR] system_settings表不存在")
                return False
            
            # 初始化默认设置
            print("\n[3] 初始化默认设置...")
            SystemSettings.set_setting(
                'apply_business_customer_phone_required',
                'true',
                '代客申请时客户电话是否必填',
                None
            )
            SystemSettings.set_setting(
                'apply_business_customer_email_required',
                'true',
                '代客申请时客户邮箱是否必填',
                None
            )
            print("  [OK] 默认设置已初始化")
            
            # 验证设置
            print("\n[4] 验证设置...")
            phone_required = SystemSettings.get_setting('apply_business_customer_phone_required', 'false')
            email_required = SystemSettings.get_setting('apply_business_customer_email_required', 'false')
            
            print(f"  [OK] 客户电话必填: {phone_required}")
            print(f"  [OK] 客户邮箱必填: {email_required}")
            
            print("\n" + "=" * 60)
            print("迁移完成！")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\n[ERROR] 迁移失败: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = migrate_system_settings()
    sys.exit(0 if success else 1)
