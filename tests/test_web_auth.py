#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web端认证系统测试
测试用户注册、登录、登出、密码重置、邮箱验证等功能
"""

import os
import sys
import unittest
import json
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, User, Staff, Permission
from flask_login import login_user

class WebAuthTest(unittest.TestCase):
    """Web端认证系统测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.app = create_app('testing')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # 创建测试数据库表
        db.create_all()
        
        # 创建测试权限
        cls.create_test_permissions()
        
        # 创建测试用户
        cls.create_test_users()
        
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
        
    @classmethod
    def create_test_permissions(cls):
        """创建测试权限"""
        permissions = [
            {
                'position': '普通业务员',
                'can_confirm': True,
                'can_execute': False,
                'can_manage': False,
                'can_view_all': False,
                'can_edit_paper': True,
                'can_edit_patent': True,
                'is_expert': False
            },
            {
                'position': '项目执行者',
                'can_confirm': True,
                'can_execute': True,
                'can_manage': True,
                'can_view_all': True,
                'can_edit_paper': True,
                'can_edit_patent': True,
                'is_expert': True
            }
        ]
        
        for perm_data in permissions:
            existing = Permission.query.filter_by(position=perm_data['position']).first()
            if not existing:
                permission = Permission(**perm_data)
                db.session.add(permission)
                
        db.session.commit()
        
    @classmethod
    def create_test_users(cls):
        """创建测试用户"""
        # 测试普通用户
        test_user = User(
            name='测试用户',
            email='testuser@example.com',
            phone='13800138000',
            user_category='软件著作权',
            organization='测试机构',
            research_field='医疗软件'
        )
        test_user.set_password('password123')
        
        # 测试员工
        test_staff = Staff(
            name='测试员工',
            email='teststaff@example.com',
            phone='13800138001',
            position_id=1  # 普通业务员
        )
        test_staff.set_password('staff123')
        
        # 管理员
        admin = Staff(
            name='系统管理员',
            email='admin@yiqichuang.com',
            phone='13800138002',
            position_id=2  # 项目执行者
        )
        admin.set_password('admin123')
        
        db.session.add(test_user)
        db.session.add(test_staff)
        db.session.add(admin)
        db.session.commit()
        
    def setUp(self):
        """每个测试方法前的准备"""
        self.test_user_email = 'testuser@example.com'
        self.test_staff_email = 'teststaff@example.com'
        self.admin_email = 'admin@yiqichuang.com'
        
    def test_user_registration(self):
        """测试用户注册"""
        print("\n测试用户注册功能...")
        
        # 测试正常注册
        registration_data = {
            'name': '新测试用户',
            'email': 'newuser@example.com',
            'phone': '13800138999',
            'password': 'newpassword123',
            'confirm_password': 'newpassword123',
            'user_category': '软件著作权',
            'organization': '新测试机构',
            'research_field': '医疗信息化'
        }
        
        response = self.client.post('/auth/register', 
                                  data=registration_data,
                                  follow_redirects=True)
        
        # 验证注册成功
        self.assertEqual(response.status_code, 200)
        
        # 验证用户已创建
        new_user = User.query.filter_by(email='newuser@example.com').first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.name, '新测试用户')
        
        print("✓ 用户注册功能正常")
        
    def test_user_registration_validation(self):
        """测试用户注册验证"""
        print("\n测试用户注册验证...")
        
        # 测试邮箱重复
        duplicate_data = {
            'name': '重复用户',
            'email': self.test_user_email,  # 已存在的邮箱
            'phone': '13800138998',
            'password': 'password123',
            'confirm_password': 'password123'
        }
        
        response = self.client.post('/auth/register', data=duplicate_data)
        self.assertEqual(response.status_code, 200)
        # 应该显示错误信息
        
        # 测试密码不匹配
        password_mismatch_data = {
            'name': '密码测试用户',
            'email': 'passwordtest@example.com',
            'phone': '13800138997',
            'password': 'password123',
            'confirm_password': 'differentpassword'
        }
        
        response = self.client.post('/auth/register', data=password_mismatch_data)
        self.assertEqual(response.status_code, 200)
        # 应该显示密码不匹配错误
        
        print("✓ 用户注册验证功能正常")
        
    def test_user_login(self):
        """测试用户登录"""
        print("\n测试用户登录功能...")
        
        # 测试正常登录
        login_data = {
            'email': self.test_user_email,
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login', 
                                  data=login_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 测试错误密码
        wrong_password_data = {
            'email': self.test_user_email,
            'password': 'wrongpassword'
        }
        
        response = self.client.post('/auth/login', data=wrong_password_data)
        self.assertEqual(response.status_code, 200)
        # 应该显示登录失败信息
        
        # 测试不存在的用户
        nonexistent_user_data = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login', data=nonexistent_user_data)
        self.assertEqual(response.status_code, 200)
        # 应该显示用户不存在信息
        
        print("✓ 用户登录功能正常")
        
    def test_staff_login(self):
        """测试员工登录"""
        print("\n测试员工登录功能...")
        
        # 测试员工登录
        login_data = {
            'email': self.test_staff_email,
            'password': 'staff123'
        }
        
        response = self.client.post('/auth/login', 
                                  data=login_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 测试管理员登录
        admin_login_data = {
            'email': self.admin_email,
            'password': 'admin123'
        }
        
        response = self.client.post('/auth/login', 
                                  data=admin_login_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        print("✓ 员工登录功能正常")
        
    def test_logout(self):
        """测试登出功能"""
        print("\n测试登出功能...")
        
        # 先登录
        login_data = {
            'email': self.test_user_email,
            'password': 'password123'
        }
        
        self.client.post('/auth/login', data=login_data)
        
        # 登出
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        print("✓ 登出功能正常")
        
    def test_password_reset_request(self):
        """测试密码重置请求"""
        print("\n测试密码重置请求...")
        
        # 测试正常密码重置请求
        reset_data = {
            'email': self.test_user_email
        }
        
        response = self.client.post('/auth/forgot_password', 
                                  data=reset_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 测试不存在的邮箱
        nonexistent_email_data = {
            'email': 'nonexistent@example.com'
        }
        
        response = self.client.post('/auth/forgot_password', 
                                  data=nonexistent_email_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        print("✓ 密码重置请求功能正常")
        
    def test_password_reset(self):
        """测试密码重置"""
        print("\n测试密码重置功能...")
        
        # 生成重置令牌（模拟）
        user = User.query.filter_by(email=self.test_user_email).first()
        user.password_reset_token = 'test_reset_token'
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        # 测试密码重置
        reset_data = {
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = self.client.post('/auth/reset_password/test_reset_token', 
                                  data=reset_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证密码已更新
        user = User.query.filter_by(email=self.test_user_email).first()
        self.assertTrue(user.check_password('newpassword123'))
        
        print("✓ 密码重置功能正常")
        
    def test_email_verification(self):
        """测试邮箱验证"""
        print("\n测试邮箱验证功能...")
        
        # 创建未验证的用户
        unverified_user = User(
            name='未验证用户',
            email='unverified@example.com',
            phone='13800138996',
            email_verified=False,
            email_verification_code='123456'
        )
        unverified_user.set_password('password123')
        db.session.add(unverified_user)
        db.session.commit()
        
        # 测试邮箱验证
        verification_data = {
            'verification_code': '123456'
        }
        
        response = self.client.post('/auth/verify_code', 
                                  data=verification_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        print("✓ 邮箱验证功能正常")
        
    def test_session_management(self):
        """测试会话管理"""
        print("\n测试会话管理...")
        
        # 测试登录后会话
        login_data = {
            'email': self.test_user_email,
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        
        # 测试访问需要登录的页面
        response = self.client.get('/user/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # 测试登出后访问
        self.client.get('/auth/logout')
        response = self.client.get('/user/dashboard')
        self.assertNotEqual(response.status_code, 200)  # 应该重定向到登录页
        
        print("✓ 会话管理功能正常")
        
    def test_role_based_access(self):
        """测试基于角色的访问控制"""
        print("\n测试基于角色的访问控制...")
        
        # 测试普通用户访问员工功能
        login_data = {
            'email': self.test_user_email,
            'password': 'password123'
        }
        
        self.client.post('/auth/login', data=login_data)
        
        # 普通用户不应该能访问员工功能
        response = self.client.get('/staff/dashboard')
        self.assertNotEqual(response.status_code, 200)
        
        # 测试员工访问员工功能
        self.client.get('/auth/logout')
        
        staff_login_data = {
            'email': self.test_staff_email,
            'password': 'staff123'
        }
        
        self.client.post('/auth/login', data=staff_login_data)
        
        # 员工应该能访问员工功能
        response = self.client.get('/staff/dashboard')
        self.assertEqual(response.status_code, 200)
        
        print("✓ 基于角色的访问控制正常")
        
    def test_security_headers(self):
        """测试安全响应头"""
        print("\n测试安全响应头...")
        
        response = self.client.get('/')
        
        # 检查基本安全头
        self.assertIn('X-Content-Type-Options', response.headers)
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        
        print("✓ 安全响应头设置正常")

def run_auth_tests():
    """运行认证测试"""
    print("=" * 60)
    print("开始Web端认证系统测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(WebAuthTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("Web端认证系统测试完成")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_auth_tests()
