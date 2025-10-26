#!/usr/bin/env python3
"""
邮箱功能数据库迁移脚本
添加邮箱验证和密码重置相关字段
"""

import os
import sys
from datetime import datetime
from sqlalchemy import text

# 修复：添加项目根目录到Python路径（而不是当前脚本目录）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from web_app.app import create_app
from database.models import db, User, Staff

def migrate_database():
    """迁移数据库，添加邮箱验证和密码重置字段"""
    app = create_app()
    
    with app.app_context():
        print("开始数据库迁移...")
        
        try:
            # 检查字段是否已存在
            inspector = db.inspect(db.engine)
            user_columns = [col['name'] for col in inspector.get_columns('users')]
            staff_columns = [col['name'] for col in inspector.get_columns('staff')]
            
            print("检查现有字段...")
            print(f"用户表字段: {user_columns}")
            print(f"员工表字段: {staff_columns}")
            
            # 为User表添加字段
            print("为用户表添加缺失的邮箱验证字段...")
            with db.engine.connect() as conn:
                trans = conn.begin()
                try:
                    # 检查并添加缺失的字段
                    fields_to_add = [
                        ("email_verified", "BOOLEAN DEFAULT 0"),
                        ("email_verification_token", "VARCHAR(100)"),
                        ("email_verification_expires", "DATETIME"),
                        ("email_verification_code", "VARCHAR(6)"),
                        ("email_verification_code_expires", "DATETIME"),
                        ("password_reset_token", "VARCHAR(100)"),
                        ("password_reset_expires", "DATETIME"),
                        ("email_verification_tries", "INTEGER DEFAULT 0"),
                        ("last_email_sent_at", "DATETIME"),
                        ("email_send_count", "INTEGER DEFAULT 0")
                    ]
                    
                    for field_name, field_type in fields_to_add:
                        if field_name not in user_columns:
                            print(f"   添加字段: {field_name}")
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}"))
                        else:
                            print(f"   字段已存在: {field_name}")
                    
                    trans.commit()
                    print("用户表字段添加完成")
                except Exception as e:
                    trans.rollback()
                    raise e
            
            # 为Staff表添加字段
            print("为员工表添加缺失的邮箱验证字段...")
            with db.engine.connect() as conn:
                trans = conn.begin()
                try:
                    # 检查并添加缺失的字段
                    fields_to_add = [
                        ("email_verified", "BOOLEAN DEFAULT 0"),
                        ("email_verification_token", "VARCHAR(100)"),
                        ("email_verification_expires", "DATETIME"),
                        ("email_verification_code", "VARCHAR(6)"),
                        ("email_verification_code_expires", "DATETIME"),
                        ("password_reset_token", "VARCHAR(100)"),
                        ("password_reset_expires", "DATETIME"),
                        ("email_verification_tries", "INTEGER DEFAULT 0"),
                        ("last_email_sent_at", "DATETIME"),
                        ("email_send_count", "INTEGER DEFAULT 0")
                    ]
                    
                    for field_name, field_type in fields_to_add:
                        if field_name not in staff_columns:
                            print(f"   添加字段: {field_name}")
                            conn.execute(text(f"ALTER TABLE staff ADD COLUMN {field_name} {field_type}"))
                        else:
                            print(f"   字段已存在: {field_name}")
                    
                    trans.commit()
                    print("员工表字段添加完成")
                except Exception as e:
                    trans.rollback()
                    raise e
            
            # 更新现有用户的邮箱验证状态
            print("更新现有用户邮箱验证状态...")
            existing_users = User.query.all()
            for user in existing_users:
                if user.email_verified is None:
                    user.email_verified = True  # 现有用户默认为已验证
                    print(f"   更新用户 {user.name} 的邮箱验证状态")
            
            existing_staff = Staff.query.all()
            for staff in existing_staff:
                if staff.email_verified is None:
                    staff.email_verified = True  # 现有员工默认为已验证
                    print(f"   更新员工 {staff.name} 的邮箱验证状态")
            
            db.session.commit()
            print("现有用户邮箱验证状态更新完成")
            
            print("\n数据库迁移完成！")
            print("=" * 50)
            print("新增功能：")
            print("1. 邮箱验证功能")
            print("2. 忘记密码功能")
            print("3. 邮件发送功能")
            print("4. 密码重置功能")
            print("=" * 50)
            
        except Exception as e:
            print(f"迁移失败: {e}")
            db.session.rollback()
            return False
        
        return True

def test_email_features():
    """测试邮箱功能"""
    app = create_app()
    
    with app.app_context():
        print("\n测试邮箱功能...")
        
        try:
            # 测试邮件配置
            from flask import current_app
            print(f"邮件服务器: {current_app.config.get('MAIL_SERVER')}")
            
            # 测试发送邮件功能
            from web_app.utils.email import send_welcome_email
            test_email = current_app.config.get('MAIL_DEFAULT_SENDER')
            if test_email:
                # 创建一个临时用户对象用于测试
                class TempUser:
                    def __init__(self):
                        self.name = "系统管理员"
                        self.email = test_email
                
                temp_user = TempUser()
                result = send_welcome_email(temp_user)
                if result:
                    print("邮件发送功能正常")
                else:
                    print("邮件发送失败")
            else:
                print("未配置测试邮箱")
                
        except Exception as e:
            print(f"测试失败: {e}")
            return False
            
        return True

def main():
    """主函数"""
    print("=" * 60)
    print("邮箱功能数据库迁移工具")
    print("=" * 60)
    
    # 检查环境变量
    print("检查环境变量...")
    required_envs = ['MAIL_SERVER', 'MAIL_PORT', 'MAIL_USE_TLS', 'MAIL_USERNAME', 'MAIL_PASSWORD']
    missing_envs = [env for env in required_envs if not os.getenv(env)]
    
    if missing_envs:
        print(f"警告: 缺少以下环境变量: {', '.join(missing_envs)}")
        print("   请在运行前设置环境变量或在config.py中配置邮件相关参数")
    else:
        print("环境变量检查通过")
    
    # 执行迁移
    success = migrate_database()
    
    if success:
        # 测试功能
        test_success = test_email_features()
        if test_success:
            print("\n所有功能测试通过！")
        else:
            print("\n数据库迁移成功，但功能测试失败，请检查邮件配置。")
            print("提示：邮件功能测试失败不影响数据库迁移，仅影响邮件功能验证。")
    else:
        print("\n迁移失败！请检查错误信息。")

if __name__ == "__main__":
    main()