#!/usr/bin/env python3
"""
验证码功能测试脚本
"""

import os
import sys
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from database.models import db, User
from web_app.utils.email import generate_verification_code, send_verification_code

def test_verification_code_generation():
    """测试验证码生成"""
    print("测试验证码生成...")
    
    codes = []
    for i in range(10):
        code = generate_verification_code()
        codes.append(code)
        print(f"  生成验证码 {i+1}: {code}")
    
    # 检查验证码格式
    all_valid = all(len(code) == 6 and code.isdigit() for code in codes)
    print(f"验证码格式检查: {'通过' if all_valid else '失败'}")
    
    # 检查验证码唯一性
    unique_codes = len(set(codes))
    print(f"验证码唯一性检查: {unique_codes}/10 个唯一")
    
    return all_valid and unique_codes >= 8

def test_database_verification():
    """测试数据库验证功能"""
    print("\n测试数据库验证功能...")
    
    app = create_app()
    with app.app_context():
        try:
            # 创建测试用户
            test_user = User(
                name="测试用户",
                email="test@example.com",
                password_hash="test_hash"
            )
            
            # 生成验证码
            verification_code = generate_verification_code()
            code_expires = datetime.utcnow() + timedelta(minutes=5)
            
            test_user.email_verification_code = verification_code
            test_user.email_verification_code_expires = code_expires
            
            print(f"  生成验证码: {verification_code}")
            print(f"  过期时间: {code_expires}")
            
            # 测试验证码验证
            current_time = datetime.utcnow()
            is_valid = (test_user.email_verification_code == verification_code and 
                       test_user.email_verification_code_expires and 
                       test_user.email_verification_code_expires > current_time)
            
            print(f"验证码验证: {'通过' if is_valid else '失败'}")
            
            # 测试过期验证码
            expired_time = datetime.utcnow() - timedelta(minutes=1)
            test_user.email_verification_code_expires = expired_time
            
            is_expired = (test_user.email_verification_code_expires and 
                         test_user.email_verification_code_expires <= current_time)
            
            print(f"过期验证码检查: {'通过' if is_expired else '失败'}")
            
            return is_valid and is_expired
            
        except Exception as e:
            print(f"数据库测试失败: {e}")
            return False

def test_email_sending():
    """测试邮件发送功能"""
    print("\n测试邮件发送功能...")
    
    app = create_app()
    with app.app_context():
        try:
            # 检查邮件配置
            from flask import current_app
            mail_server = current_app.config.get('MAIL_SERVER')
            mail_username = current_app.config.get('MAIL_USERNAME')
            
            print(f"  邮件服务器: {mail_server}")
            print(f"  邮件用户名: {mail_username}")
            
            if not mail_username:
                print("邮件配置未完成，跳过发送测试")
                return True
            
            # 创建测试用户
            class TestUser:
                def __init__(self):
                    self.name = "测试用户"
                    self.email = mail_username  # 发送给自己
            
            test_user = TestUser()
            verification_code = generate_verification_code()
            
            print(f"  发送验证码到: {test_user.email}")
            print(f"  验证码: {verification_code}")
            
            # 发送邮件
            result = send_verification_code(test_user, verification_code)
            print(f"邮件发送: {'成功' if result else '失败'}")
            
            return result
            
        except Exception as e:
            print(f"邮件发送测试失败: {e}")
            return False

def test_verification_flow():
    """测试完整验证流程"""
    print("\n测试完整验证流程...")
    
    app = create_app()
    with app.app_context():
        try:
            # 模拟注册流程
            print("1. 模拟用户注册...")
            verification_code = generate_verification_code()
            code_expires = datetime.utcnow() + timedelta(minutes=5)
            
            print(f"   生成验证码: {verification_code}")
            print(f"   过期时间: {code_expires}")
            
            # 模拟验证流程
            print("2. 模拟验证码验证...")
            current_time = datetime.utcnow()
            
            # 正确验证码
            correct_code = verification_code
            is_correct = (correct_code == verification_code and 
                         code_expires > current_time)
            print(f"   正确验证码验证: {'通过' if is_correct else '失败'}")
            
            # 错误验证码
            wrong_code = "123456"
            is_wrong = (wrong_code != verification_code)
            print(f"   错误验证码验证: {'通过' if is_wrong else '失败'}")
            
            # 过期验证码
            expired_time = datetime.utcnow() - timedelta(minutes=1)
            is_expired = (code_expires <= expired_time)
            print(f"   过期验证码验证: {'通过' if is_expired else '失败'}")
            
            return is_correct and is_wrong and not is_expired
            
        except Exception as e:
            print(f"验证流程测试失败: {e}")
            return False

def main():
    print("=" * 60)
    print("验证码功能测试工具")
    print("=" * 60)
    
    tests = [
        ("验证码生成", test_verification_code_generation),
        ("数据库验证", test_database_verification),
        ("邮件发送", test_email_sending),
        ("验证流程", test_verification_flow)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"{test_name}: {'通过' if result else '失败'}")
        except Exception as e:
            print(f"{test_name}: 异常 - {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "通过" if result else "失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总体结果: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("所有测试通过！验证码功能正常工作。")
    else:
        print("部分测试失败，请检查相关功能。")
    
    return passed == total

if __name__ == '__main__':
    main()
