#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web API接口测试
测试桌面端专用API接口：登录、项目列表、状态更新、流水号更新、数据同步等
"""

import os
import sys
import unittest
import json
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, User, Staff, Project, Permission, ProcessLog
from flask_login import login_user

class WebAPITest(unittest.TestCase):
    """Web API接口测试类"""
    
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
            permission = Permission(**perm_data)
            db.session.add(permission)
            
        # 创建测试用户
        test_user = User(
            name='API测试用户',
            email='apiuser@example.com',
            phone='13800138000',
            user_category='软件著作权',
            organization='测试机构',
            research_field='医疗软件'
        )
        test_user.set_password('password123')
        
        # 创建测试员工
        test_staff = Staff(
            name='API测试业务员',
            email='apistaff@example.com',
            phone='13800138001',
            position_id=1  # 普通业务员
        )
        test_staff.set_password('staff123')
        
        # 创建测试执行者
        test_executor = Staff(
            name='API测试执行者',
            email='apiexecutor@example.com',
            phone='13800138002',
            position_id=2  # 项目执行者
        )
        test_executor.set_password('executor123')
        
        db.session.add(test_user)
        db.session.add(test_staff)
        db.session.add(test_executor)
        db.session.commit()
        
        # 保存引用
        cls.test_user = test_user
        cls.test_staff = test_staff
        cls.test_executor = test_executor
        
    def setUp(self):
        """每个测试方法前的准备"""
        # 创建测试项目
        self.test_project = Project(
            project_name='API测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='API测试用户',
            software_applicant_name='API测试用户',
            priority='普通',
            price=2000.00,
            status='已立项',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow()
        )
        db.session.add(self.test_project)
        db.session.commit()
        
    def test_desktop_login_api(self):
        """测试桌面端登录API"""
        print("\n测试桌面端登录API...")
        
        # 测试正常登录
        login_data = {
            'email': self.test_executor.email,
            'password': 'executor123',
            'user_type': 'staff'
        }
        
        response = self.client.post('/api/desktop/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['user']['email'], self.test_executor.email)
        self.assertEqual(response_data['user']['user_type'], 'staff')
        
        # 测试错误密码
        wrong_password_data = {
            'email': self.test_executor.email,
            'password': 'wrongpassword',
            'user_type': 'staff'
        }
        
        response = self.client.post('/api/desktop/login', 
                                  data=json.dumps(wrong_password_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        
        # 测试不存在的用户
        nonexistent_user_data = {
            'email': 'nonexistent@example.com',
            'password': 'password123',
            'user_type': 'staff'
        }
        
        response = self.client.post('/api/desktop/login', 
                                  data=json.dumps(nonexistent_user_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        
        print("✓ 桌面端登录API功能正常")
        
    def test_desktop_get_projects_api(self):
        """测试桌面端获取项目列表API"""
        print("\n测试桌面端获取项目列表API...")
        
        # 创建更多测试项目
        projects_data = [
            {
                'project_name': '已立项项目1',
                'status': '已立项',
                'executor_id': self.test_executor.id
            },
            {
                'project_name': '执行中项目1',
                'status': '执行中',
                'executor_id': self.test_executor.id
            },
            {
                'project_name': '已完成项目1',
                'status': '已完成',
                'executor_id': self.test_executor.id
            }
        ]
        
        for project_data in projects_data:
            project = Project(
                project_name=project_data['project_name'],
                project_type='软件登记业务',
                applicant_type='个人',
                copyright_owner='测试用户',
                software_applicant_name='测试用户',
                priority='普通',
                price=2000.00,
                status=project_data['status'],
                applicant_id=self.test_user.id,
                confirmer_id=self.test_staff.id,
                executor_id=project_data['executor_id'],
                confirm_time=datetime.utcnow()
            )
            db.session.add(project)
            
        db.session.commit()
        
        # 测试获取项目列表
        request_data = {
            'email': self.test_executor.email,
            'password': 'executor123',
            'user_type': 'staff'
        }
        
        response = self.client.post('/api/desktop/projects', 
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        self.assertIsInstance(response_data['projects'], list)
        
        # 验证项目数据
        projects = response_data['projects']
        self.assertGreater(len(projects), 0)
        
        # 验证项目状态过滤
        status_request_data = {
            'email': self.test_executor.email,
            'password': 'executor123',
            'user_type': 'staff',
            'status': '已立项'
        }
        
        response = self.client.post('/api/desktop/projects', 
                                  data=json.dumps(status_request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        
        # 验证只返回已立项项目
        for project in response_data['projects']:
            self.assertEqual(project['status'], '已立项')
        
        print("✓ 桌面端获取项目列表API功能正常")
        
    def test_desktop_update_project_api(self):
        """测试桌面端更新项目API"""
        print("\n测试桌面端更新项目API...")
        
        # 测试更新项目状态
        update_data = {
            'email': self.test_executor.email,
            'password': 'executor123',
            'user_type': 'staff',
            'project_id': self.test_project.id,
            'status': '执行中',
            'remarks': '开始执行项目'
        }
        
        response = self.client.post('/api/desktop/update_project', 
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        
        # 验证项目状态已更新
        updated_project = Project.query.get(self.test_project.id)
        self.assertEqual(updated_project.status, '执行中')
        
        # 测试更新项目信息
        update_info_data = {
            'email': self.test_executor.email,
            'password': 'executor123',
            'user_type': 'staff',
            'project_id': self.test_project.id,
            'project_name': '更新后的项目名称',
            'remarks': '项目信息已更新'
        }
        
        response = self.client.post('/api/desktop/update_project', 
                                  data=json.dumps(update_info_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        
        # 验证项目信息已更新
        updated_project = Project.query.get(self.test_project.id)
        self.assertEqual(updated_project.project_name, '更新后的项目名称')
        
        print("✓ 桌面端更新项目API功能正常")
        
    def test_desktop_update_serial_number_api(self):
        """测试桌面端更新流水号API"""
        print("\n测试桌面端更新流水号API...")
        
        # 测试更新流水号
        serial_number = '2024SR001234'
        update_data = {
            'email': self.test_executor.email,
            'password': 'executor123',
            'user_type': 'staff',
            'project_id': self.test_project.id,
            'serial_number': serial_number,
            'remarks': f'流水号已更新: {serial_number}'
        }
        
        response = self.client.post('/api/desktop/update_serial_number', 
                                  data=json.dumps(update_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        
        # 验证流水号已更新
        updated_project = Project.query.get(self.test_project.id)
        self.assertEqual(updated_project.serial_number, serial_number)
        
        # 测试更新状态为已获取流水号
        self.assertEqual(updated_project.status, '已获取流水号')
        
        print("✓ 桌面端更新流水号API功能正常")
        
    def test_desktop_sync_data_api(self):
        """测试桌面端数据同步API"""
        print("\n测试桌面端数据同步API...")
        
        # 测试数据同步
        sync_data = {
            'email': self.test_executor.email,
            'password': 'executor123',
            'user_type': 'staff',
            'last_sync_time': '2024-01-01 00:00:00'
        }
        
        response = self.client.post('/api/desktop/sync_data', 
                                  data=json.dumps(sync_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertTrue(response_data['success'])
        
        # 验证同步数据
        self.assertIn('projects', response_data)
        self.assertIn('sync_time', response_data)
        
        print("✓ 桌面端数据同步API功能正常")
        
    def test_desktop_api_authentication(self):
        """测试桌面端API身份验证"""
        print("\n测试桌面端API身份验证...")
        
        # 测试无身份验证的请求
        request_data = {
            'project_id': self.test_project.id,
            'status': '执行中'
        }
        
        response = self.client.post('/api/desktop/update_project', 
                                  data=json.dumps(request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        self.assertIn('身份验证失败', response_data['message'])
        
        # 测试错误密码
        wrong_auth_data = {
            'email': self.test_executor.email,
            'password': 'wrongpassword',
            'user_type': 'staff',
            'project_id': self.test_project.id,
            'status': '执行中'
        }
        
        response = self.client.post('/api/desktop/update_project', 
                                  data=json.dumps(wrong_auth_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        self.assertIn('身份验证失败', response_data['message'])
        
        print("✓ 桌面端API身份验证功能正常")
        
    def test_desktop_api_permissions(self):
        """测试桌面端API权限控制"""
        print("\n测试桌面端API权限控制...")
        
        # 测试普通业务员访问执行者功能
        staff_request_data = {
            'email': self.test_staff.email,
            'password': 'staff123',
            'user_type': 'staff',
            'project_id': self.test_project.id,
            'status': '执行中'
        }
        
        response = self.client.post('/api/desktop/update_project', 
                                  data=json.dumps(staff_request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        # 普通业务员应该不能更新项目状态
        self.assertFalse(response_data['success'])
        
        # 测试执行者访问执行者功能
        executor_request_data = {
            'email': self.test_executor.email,
            'password': 'executor123',
            'user_type': 'staff',
            'project_id': self.test_project.id,
            'status': '执行中'
        }
        
        response = self.client.post('/api/desktop/update_project', 
                                  data=json.dumps(executor_request_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        # 执行者应该能更新项目状态
        self.assertTrue(response_data['success'])
        
        print("✓ 桌面端API权限控制功能正常")
        
    def test_desktop_api_error_handling(self):
        """测试桌面端API错误处理"""
        print("\n测试桌面端API错误处理...")
        
        # 测试无效的JSON数据
        response = self.client.post('/api/desktop/login', 
                                  data='invalid json',
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        
        # 测试缺少必要参数
        incomplete_data = {
            'email': self.test_executor.email
            # 缺少password和user_type
        }
        
        response = self.client.post('/api/desktop/login', 
                                  data=json.dumps(incomplete_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        
        # 测试不存在的项目ID
        nonexistent_project_data = {
            'email': self.test_executor.email,
            'password': 'executor123',
            'user_type': 'staff',
            'project_id': 99999,  # 不存在的项目ID
            'status': '执行中'
        }
        
        response = self.client.post('/api/desktop/update_project', 
                                  data=json.dumps(nonexistent_project_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        self.assertFalse(response_data['success'])
        
        print("✓ 桌面端API错误处理功能正常")
        
    def test_desktop_api_response_format(self):
        """测试桌面端API响应格式"""
        print("\n测试桌面端API响应格式...")
        
        # 测试登录API响应格式
        login_data = {
            'email': self.test_executor.email,
            'password': 'executor123',
            'user_type': 'staff'
        }
        
        response = self.client.post('/api/desktop/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = json.loads(response.data)
        
        # 验证响应格式
        self.assertIn('success', response_data)
        self.assertIn('message', response_data)
        self.assertIn('user', response_data)
        
        # 验证用户信息格式
        user_data = response_data['user']
        self.assertIn('id', user_data)
        self.assertIn('email', user_data)
        self.assertIn('user_type', user_data)
        self.assertIn('name', user_data)
        
        # 验证权限信息格式
        self.assertIn('permissions', user_data)
        permissions = user_data['permissions']
        self.assertIn('can_confirm', permissions)
        self.assertIn('can_execute', permissions)
        self.assertIn('can_manage', permissions)
        
        print("✓ 桌面端API响应格式功能正常")
        
    def test_desktop_api_performance(self):
        """测试桌面端API性能"""
        print("\n测试桌面端API性能...")
        
        import time
        
        # 测试登录API性能
        login_data = {
            'email': self.test_executor.email,
            'password': 'executor123',
            'user_type': 'staff'
        }
        
        start_time = time.time()
        response = self.client.post('/api/desktop/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 1.0)  # 应该在1秒内完成
        
        # 测试获取项目列表API性能
        projects_data = {
            'email': self.test_executor.email,
            'password': 'executor123',
            'user_type': 'staff'
        }
        
        start_time = time.time()
        response = self.client.post('/api/desktop/projects', 
                                  data=json.dumps(projects_data),
                                  content_type='application/json')
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 1.0)  # 应该在1秒内完成
        
        print("✓ 桌面端API性能测试通过")
        
    def test_desktop_api_concurrent_requests(self):
        """测试桌面端API并发请求"""
        print("\n测试桌面端API并发请求...")
        
        import threading
        import time
        
        results = []
        
        def make_request():
            # 在子线程中设置应用上下文
            with self.app.app_context():
                login_data = {
                    'email': self.test_executor.email,
                    'password': 'executor123',
                    'user_type': 'staff'
                }
                
                response = self.client.post('/api/desktop/login', 
                                          data=json.dumps(login_data),
                                          content_type='application/json')
                
                results.append(response.status_code == 200)
        
        # 创建多个线程同时发送请求
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有请求都成功
        self.assertEqual(len(results), 5)
        self.assertTrue(all(results))
        
        print("✓ 桌面端API并发请求测试通过")

def run_web_api_tests():
    """运行Web API接口测试"""
    print("=" * 60)
    print("开始Web API接口测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(WebAPITest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("Web API接口测试完成")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_web_api_tests()
