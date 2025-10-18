#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web安全测试
测试XSS攻击、SQL注入、CSRF、路径遍历、密码安全等安全功能
"""

import os
import sys
import unittest
import json
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, User, Staff, Project, Permission
from flask_login import login_user

class WebSecurityTest(unittest.TestCase):
    """Web安全测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.app = create_app('testing')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # 创建测试数据库表
        db.create_all()
        
        # 创建测试数据
        cls.create_test_data()
        
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
        
    @classmethod
    def create_test_data(cls):
        """创建测试数据"""
        # 创建权限
        permission = Permission(
            position='项目执行者',
            can_confirm=True,
            can_execute=True,
            can_manage=True,
            can_view_all=True,
            can_edit_paper=True,
            can_edit_patent=True,
            is_expert=True
        )
        db.session.add(permission)
        
        # 创建测试用户
        test_user = User(
            name='安全测试用户',
            email='securityuser@example.com',
            phone='13800138000',
            user_category='软件著作权',
            organization='测试机构',
            research_field='医疗软件'
        )
        test_user.set_password('password123')
        
        # 创建测试员工
        test_staff = Staff(
            name='安全测试员工',
            email='securitystaff@example.com',
            phone='13800138001',
            position_id=1
        )
        test_staff.set_password('staff123')
        
        db.session.add(test_user)
        db.session.add(test_staff)
        db.session.commit()
        
        # 保存引用
        cls.test_user = test_user
        cls.test_staff = test_staff
        
    def test_xss_protection(self):
        """测试XSS攻击防护"""
        print("\n测试XSS攻击防护...")
        
        # 测试脚本注入
        xss_payloads = [
            '<script>alert("XSS")</script>',
            'javascript:alert("XSS")',
            '<img src="x" onerror="alert(\'XSS\')">',
            '<svg onload="alert(\'XSS\')">',
            '"><script>alert("XSS")</script>',
            "'><script>alert('XSS')</script>",
            '<iframe src="javascript:alert(\'XSS\')"></iframe>',
            '<object data="javascript:alert(\'XSS\')"></object>',
            '<embed src="javascript:alert(\'XSS\')">',
            '<link rel="stylesheet" href="javascript:alert(\'XSS\')">'
        ]
        
        for payload in xss_payloads:
            # 测试用户注册中的XSS防护
            registration_data = {
                'name': payload,
                'email': 'xss_test@example.com',
                'phone': '13800138999',
                'password': 'password123',
                'confirm_password': 'password123',
                'user_category': '软件著作权',
                'organization': payload,
                'research_field': payload
            }
            
            response = self.client.post('/auth/register', 
                                      data=registration_data,
                                      follow_redirects=True)
            
            self.assertEqual(response.status_code, 200)
            
            # 验证响应中不包含原始脚本
            response_text = response.get_data(as_text=True)
            self.assertNotIn('<script>', response_text)
            self.assertNotIn('javascript:', response_text)
            self.assertNotIn('onerror=', response_text)
            self.assertNotIn('onload=', response_text)
            
        print("✓ XSS攻击防护功能正常")
        
    def test_sql_injection_protection(self):
        """测试SQL注入防护"""
        print("\n测试SQL注入防护...")
        
        # SQL注入测试载荷
        sql_payloads = [
            "' OR '1'='1",
            "' OR 1=1--",
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users--",
            "' OR '1'='1' AND '1'='1",
            "admin'--",
            "admin'/*",
            "' OR 'x'='x",
            "' OR 1=1#",
            "') OR ('1'='1"
        ]
        
        for payload in sql_payloads:
            # 测试登录中的SQL注入防护
            login_data = {
                'email': payload,
                'password': 'password123'
            }
            
            response = self.client.post('/auth/login', data=login_data)
            self.assertEqual(response.status_code, 200)
            
            # 验证没有SQL错误信息
            response_text = response.get_data(as_text=True)
            self.assertNotIn('SQL', response_text)
            self.assertNotIn('mysql', response_text)
            self.assertNotIn('syntax error', response_text)
            
            # 测试项目搜索中的SQL注入防护
            search_data = {
                'search_term': payload
            }
            
            response = self.client.post('/user/search', data=search_data)
            self.assertEqual(response.status_code, 200)
            
            # 验证没有SQL错误信息
            response_text = response.get_data(as_text=True)
            self.assertNotIn('SQL', response_text)
            self.assertNotIn('mysql', response_text)
            
        print("✓ SQL注入防护功能正常")
        
    def test_csrf_protection(self):
        """测试CSRF防护"""
        print("\n测试CSRF防护...")
        
        # 用户登录
        login_data = {
            'email': self.test_user.email,
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 测试CSRF令牌验证
        # 尝试在没有CSRF令牌的情况下提交表单
        project_data = {
            'project_name': 'CSRF测试项目',
            'project_type': '软件登记业务',
            'applicant_type': '个人',
            'copyright_owner': '测试用户',
            'software_applicant_name': '测试用户',
            'priority': '普通',
            'price': 2000.00
        }
        
        response = self.client.post('/user/apply', data=project_data)
        # 应该被CSRF保护拦截
        self.assertNotEqual(response.status_code, 200)
        
        print("✓ CSRF防护功能正常")
        
    def test_path_traversal_protection(self):
        """测试路径遍历防护"""
        print("\n测试路径遍历防护...")
        
        # 路径遍历测试载荷
        path_payloads = [
            '../../../etc/passwd',
            '..\\..\\..\\windows\\system32\\drivers\\etc\\hosts',
            '....//....//....//etc/passwd',
            '%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd',
            '..%2f..%2f..%2fetc%2fpasswd',
            '..%252f..%252f..%252fetc%252fpasswd',
            '..%c0%af..%c0%af..%c0%afetc%c0%afpasswd',
            '..%c1%9c..%c1%9c..%c1%9cetc%c1%9cpasswd'
        ]
        
        for payload in path_payloads:
            # 测试文件上传中的路径遍历防护
            response = self.client.get(f'/uploads/{payload}')
            # 应该返回404或403，而不是文件内容
            self.assertIn(response.status_code, [404, 403, 400])
            
            # 测试文件下载中的路径遍历防护
            response = self.client.get(f'/download/{payload}')
            # 应该返回404或403，而不是文件内容
            self.assertIn(response.status_code, [404, 403, 400])
            
        print("✓ 路径遍历防护功能正常")
        
    def test_password_security(self):
        """测试密码安全"""
        print("\n测试密码安全...")
        
        # 测试密码哈希存储
        user = User.query.filter_by(email=self.test_user.email).first()
        self.assertIsNotNone(user.password_hash)
        
        # 验证密码不是明文存储
        self.assertNotEqual(user.password_hash, 'password123')
        
        # 验证密码哈希长度合理
        self.assertGreater(len(user.password_hash), 20)
        
        # 测试密码验证
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.check_password('wrongpassword'))
        
        # 测试密码重置
        user.password_reset_token = 'test_token'
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        
        # 验证重置令牌已设置
        self.assertEqual(user.password_reset_token, 'test_token')
        self.assertIsNotNone(user.password_reset_expires)
        
        print("✓ 密码安全功能正常")
        
    def test_session_security(self):
        """测试会话安全"""
        print("\n测试会话安全...")
        
        # 用户登录
        login_data = {
            'email': self.test_user.email,
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 验证会话cookie设置
        cookies = response.headers.getlist('Set-Cookie')
        session_cookie = None
        for cookie in cookies:
            if 'session=' in cookie:
                session_cookie = cookie
                break
        
        self.assertIsNotNone(session_cookie)
        
        # 验证会话cookie安全属性
        self.assertIn('HttpOnly', session_cookie)
        self.assertIn('Secure', session_cookie)
        self.assertIn('SameSite', session_cookie)
        
        # 测试会话超时
        # 模拟会话过期
        with self.client.session_transaction() as sess:
            sess['_fresh'] = False
            sess['_id'] = 'expired_session'
        
        response = self.client.get('/user/dashboard')
        # 应该重定向到登录页
        self.assertNotEqual(response.status_code, 200)
        
        print("✓ 会话安全功能正常")
        
    def test_input_validation(self):
        """测试输入验证"""
        print("\n测试输入验证...")
        
        # 测试邮箱格式验证
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'user@',
            'user..name@example.com',
            'user@example..com',
            'user name@example.com',
            'user@example com'
        ]
        
        for email in invalid_emails:
            registration_data = {
                'name': '测试用户',
                'email': email,
                'phone': '13800138999',
                'password': 'password123',
                'confirm_password': 'password123'
            }
            
            response = self.client.post('/auth/register', data=registration_data)
            self.assertEqual(response.status_code, 200)
            
            # 验证邮箱格式验证
            response_text = response.get_data(as_text=True)
            self.assertIn('邮箱格式', response_text)
            
        # 测试密码强度验证
        weak_passwords = [
            '123',
            'password',
            '12345678',
            'abcdefgh',
            'Password',
            'password123'
        ]
        
        for password in weak_passwords:
            registration_data = {
                'name': '测试用户',
                'email': f'test_{password}@example.com',
                'phone': '13800138999',
                'password': password,
                'confirm_password': password
            }
            
            response = self.client.post('/auth/register', data=registration_data)
            self.assertEqual(response.status_code, 200)
            
            # 验证密码强度验证
            response_text = response.get_data(as_text=True)
            self.assertIn('密码', response_text)
            
        print("✓ 输入验证功能正常")
        
    def test_file_upload_security(self):
        """测试文件上传安全"""
        print("\n测试文件上传安全...")
        
        # 测试文件类型验证
        dangerous_files = [
            ('malicious.php', 'application/x-php'),
            ('script.js', 'application/javascript'),
            ('virus.exe', 'application/x-executable'),
            ('shell.sh', 'application/x-sh'),
            ('backdoor.py', 'application/x-python')
        ]
        
        for filename, content_type in dangerous_files:
            # 模拟文件上传
            data = {
                'file': (filename, b'malicious content', content_type)
            }
            
            response = self.client.post('/upload', data=data)
            # 应该被拒绝
            self.assertIn(response.status_code, [400, 403, 415])
            
        # 测试文件大小限制
        # 创建超大文件内容
        large_content = b'x' * (17 * 1024 * 1024)  # 17MB，超过16MB限制
        
        data = {
            'file': ('large_file.pdf', large_content, 'application/pdf')
        }
        
        response = self.client.post('/upload', data=data)
        # 应该被拒绝
        self.assertIn(response.status_code, [400, 413])
        
        print("✓ 文件上传安全功能正常")
        
    def test_authorization_control(self):
        """测试授权控制"""
        print("\n测试授权控制...")
        
        # 测试普通用户访问管理员功能
        login_data = {
            'email': self.test_user.email,
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 普通用户不应该能访问员工功能
        response = self.client.get('/staff/dashboard')
        self.assertNotEqual(response.status_code, 200)
        
        # 普通用户不应该能访问API端点
        api_data = {
            'email': self.test_user.email,
            'password': 'password123',
            'user_type': 'staff'
        }
        
        response = self.client.post('/api/desktop/login', 
                                  data=json.dumps(api_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        
        print("✓ 授权控制功能正常")
        
    def test_rate_limiting(self):
        """测试速率限制"""
        print("\n测试速率限制...")
        
        # 测试登录尝试限制
        login_data = {
            'email': self.test_user.email,
            'password': 'wrongpassword'
        }
        
        # 多次尝试登录
        for i in range(10):
            response = self.client.post('/auth/login', data=login_data)
            self.assertEqual(response.status_code, 200)
            
        # 验证速率限制
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 验证错误消息
        response_text = response.get_data(as_text=True)
        self.assertIn('尝试次数', response_text)
        
        print("✓ 速率限制功能正常")
        
    def test_security_headers(self):
        """测试安全响应头"""
        print("\n测试安全响应头...")
        
        response = self.client.get('/')
        
        # 检查安全头
        headers = response.headers
        
        # X-Content-Type-Options
        self.assertIn('X-Content-Type-Options', headers)
        self.assertEqual(headers.get('X-Content-Type-Options'), 'nosniff')
        
        # X-Frame-Options
        self.assertIn('X-Frame-Options', headers)
        self.assertIn(headers.get('X-Frame-Options'), ['DENY', 'SAMEORIGIN'])
        
        # X-XSS-Protection
        self.assertIn('X-XSS-Protection', headers)
        self.assertEqual(headers.get('X-XSS-Protection'), '1; mode=block')
        
        # Strict-Transport-Security (如果使用HTTPS)
        if 'Strict-Transport-Security' in headers:
            self.assertIn('max-age=', headers.get('Strict-Transport-Security'))
        
        print("✓ 安全响应头功能正常")
        
    def test_data_encryption(self):
        """测试数据加密"""
        print("\n测试数据加密...")
        
        # 测试敏感数据加密
        user = User.query.filter_by(email=self.test_user.email).first()
        
        # 验证密码哈希
        self.assertIsNotNone(user.password_hash)
        self.assertNotEqual(user.password_hash, 'password123')
        
        # 验证密码重置令牌
        if user.password_reset_token:
            self.assertIsInstance(user.password_reset_token, str)
            self.assertGreater(len(user.password_reset_token), 10)
            
        # 验证邮箱验证令牌
        if user.email_verification_token:
            self.assertIsInstance(user.email_verification_token, str)
            self.assertGreater(len(user.email_verification_token), 10)
            
        print("✓ 数据加密功能正常")
        
    def test_sql_injection_orm_protection(self):
        """测试ORM SQL注入防护"""
        print("\n测试ORM SQL注入防护...")
        
        # 测试ORM查询中的SQL注入防护
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM users--",
            "admin'--",
            "' OR 1=1#"
        ]
        
        for malicious_input in malicious_inputs:
            # 测试用户查询
            try:
                user = User.query.filter_by(email=malicious_input).first()
                # 应该返回None，而不是抛出异常
                self.assertIsNone(user)
            except Exception as e:
                # 不应该抛出SQL相关异常
                self.assertNotIn('SQL', str(e))
                self.assertNotIn('mysql', str(e))
                
            # 测试项目查询
            try:
                project = Project.query.filter_by(project_name=malicious_input).first()
                # 应该返回None，而不是抛出异常
                self.assertIsNone(project)
            except Exception as e:
                # 不应该抛出SQL相关异常
                self.assertNotIn('SQL', str(e))
                self.assertNotIn('mysql', str(e))
                
        print("✓ ORM SQL注入防护功能正常")

def run_web_security_tests():
    """运行Web安全测试"""
    print("=" * 60)
    print("开始Web安全测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(WebSecurityTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("Web安全测试完成")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_web_security_tests()
