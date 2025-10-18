#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
性能测试
测试系统在高负载下的性能表现，包括并发测试、响应时间测试、数据量测试等
"""

import os
import sys
import unittest
import json
import sqlite3
import threading
import time
import statistics
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor, as_completed

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, User, Staff, Project, PaperProject, PatentProject, Permission
from desktop_app.local_models import LocalDatabase, LocalProject
from desktop_app.server_client import ServerClient

class PerformanceTest(unittest.TestCase):
    """性能测试类"""
    
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
            name='性能测试用户',
            email='perfuser@example.com',
            phone='13800138000',
            user_category='软件著作权',
            organization='测试机构',
            research_field='医疗软件'
        )
        test_user.set_password('password123')
        
        # 创建测试执行者
        test_executor = Staff(
            name='性能测试执行者',
            email='perfexecutor@example.com',
            phone='13800138001',
            position_id=1
        )
        test_executor.set_password('executor123')
        
        db.session.add(test_user)
        db.session.add(test_executor)
        db.session.commit()
        
        # 保存引用
        cls.test_user = test_user
        cls.test_executor = test_executor
        
    def setUp(self):
        """每个测试方法前的准备"""
        # 创建本地测试数据库
        self.local_db_path = ':memory:'
        self.local_db = LocalDatabase(self.local_db_path)
        
        # 模拟服务器客户端
        self.server_client = Mock(spec=ServerClient)
        
    def test_concurrent_login_performance(self):
        """测试并发登录性能"""
        print("\n测试并发登录性能...")
        
        def login_request():
            """单个登录请求"""
            start_time = time.time()
            
            login_data = {
                'email': self.test_user.email,
                'password': 'password123'
            }
            
            response = self.client.post('/auth/login', data=login_data)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'status_code': response.status_code,
                'response_time': response_time,
                'success': response.status_code == 200
            }
        
        # 并发登录测试
        concurrent_users = 20
        results = []
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = [executor.submit(login_request) for _ in range(concurrent_users)]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        # 分析结果
        response_times = [r['response_time'] for r in results]
        success_count = sum(1 for r in results if r['success'])
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        min_response_time = min(response_times)
        
        # 验证性能指标
        self.assertGreater(success_count, concurrent_users * 0.9)  # 90%成功率
        self.assertLess(avg_response_time, 1.0)  # 平均响应时间小于1秒
        self.assertLess(max_response_time, 2.0)  # 最大响应时间小于2秒
        
        print(f"并发登录测试结果:")
        print(f"  并发用户数: {concurrent_users}")
        print(f"  成功率: {success_count/concurrent_users*100:.1f}%")
        print(f"  平均响应时间: {avg_response_time:.3f}秒")
        print(f"  最大响应时间: {max_response_time:.3f}秒")
        print(f"  最小响应时间: {min_response_time:.3f}秒")
        
    def test_concurrent_project_creation(self):
        """测试并发项目创建性能"""
        print("\n测试并发项目创建性能...")
        
        def create_project(project_id):
            """创建单个项目"""
            start_time = time.time()
            
            project = Project(
                project_name=f'性能测试项目{project_id}',
                project_type='软件登记业务',
                applicant_type='个人',
                copyright_owner='性能测试用户',
                software_applicant_name='性能测试用户',
                priority='普通',
                price=2000.00,
                status='待确认',
                applicant_id=self.test_user.id
            )
            
            db.session.add(project)
            db.session.commit()
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'project_id': project.id,
                'response_time': response_time,
                'success': True
            }
        
        # 并发创建项目测试
        concurrent_projects = 50
        results = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_project, i) for i in range(concurrent_projects)]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        # 分析结果
        response_times = [r['response_time'] for r in results]
        success_count = sum(1 for r in results if r['success'])
        
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        # 验证性能指标
        self.assertEqual(success_count, concurrent_projects)  # 100%成功率
        self.assertLess(avg_response_time, 0.5)  # 平均响应时间小于0.5秒
        
        print(f"并发项目创建测试结果:")
        print(f"  并发项目数: {concurrent_projects}")
        print(f"  成功率: {success_count/concurrent_projects*100:.1f}%")
        print(f"  平均响应时间: {avg_response_time:.3f}秒")
        print(f"  最大响应时间: {max_response_time:.3f}秒")
        
    def test_large_dataset_performance(self):
        """测试大数据集性能"""
        print("\n测试大数据集性能...")
        
        # 创建大量项目
        large_dataset_size = 1000
        projects = []
        
        start_time = time.time()
        
        for i in range(large_dataset_size):
            project = Project(
                project_name=f'大数据集测试项目{i}',
                project_type='软件登记业务',
                applicant_type='个人',
                copyright_owner='性能测试用户',
                software_applicant_name='性能测试用户',
                priority='普通',
                price=2000.00,
                status='待确认',
                applicant_id=self.test_user.id
            )
            projects.append(project)
        
        # 批量插入
        db.session.add_all(projects)
        db.session.commit()
        
        end_time = time.time()
        creation_time = end_time - start_time
        
        # 测试查询性能
        start_time = time.time()
        
        # 查询所有项目
        all_projects = Project.query.all()
        
        # 按状态查询
        pending_projects = Project.query.filter_by(status='待确认').all()
        
        # 按用户查询
        user_projects = Project.query.filter_by(applicant_id=self.test_user.id).all()
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # 验证结果
        self.assertEqual(len(all_projects), large_dataset_size)
        self.assertEqual(len(pending_projects), large_dataset_size)
        self.assertEqual(len(user_projects), large_dataset_size)
        
        # 验证性能指标
        self.assertLess(creation_time, 10.0)  # 创建时间小于10秒
        self.assertLess(query_time, 1.0)  # 查询时间小于1秒
        
        print(f"大数据集性能测试结果:")
        print(f"  数据集大小: {large_dataset_size}")
        print(f"  创建时间: {creation_time:.3f}秒")
        print(f"  查询时间: {query_time:.3f}秒")
        print(f"  创建速度: {large_dataset_size/creation_time:.0f} 项目/秒")
        print(f"  查询速度: {large_dataset_size/query_time:.0f} 项目/秒")
        
    def test_api_response_time(self):
        """测试API响应时间"""
        print("\n测试API响应时间...")
        
        # 创建测试项目
        project = Project(
            project_name='API响应时间测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='性能测试用户',
            software_applicant_name='性能测试用户',
            priority='普通',
            price=2000.00,
            status='已立项',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_executor.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # 测试API响应时间
        api_tests = [
            {
                'name': '登录API',
                'url': '/api/desktop/login',
                'data': {
                    'email': self.test_executor.email,
                    'password': 'executor123',
                    'user_type': 'staff'
                }
            },
            {
                'name': '获取项目列表API',
                'url': '/api/desktop/projects',
                'data': {
                    'email': self.test_executor.email,
                    'password': 'executor123',
                    'user_type': 'staff'
                }
            },
            {
                'name': '更新项目API',
                'url': '/api/desktop/update_project',
                'data': {
                    'email': self.test_executor.email,
                    'password': 'executor123',
                    'user_type': 'staff',
                    'project_id': project.id,
                    'status': '执行中'
                }
            }
        ]
        
        results = []
        
        for test in api_tests:
            response_times = []
            
            # 每个API测试10次
            for _ in range(10):
                start_time = time.time()
                
                response = self.client.post(test['url'],
                                          data=json.dumps(test['data']),
                                          content_type='application/json')
                
                end_time = time.time()
                response_time = end_time - start_time
                response_times.append(response_time)
            
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            results.append({
                'name': test['name'],
                'avg_time': avg_response_time,
                'max_time': max_response_time,
                'min_time': min_response_time
            })
            
            # 验证性能指标
            self.assertLess(avg_response_time, 0.5)  # 平均响应时间小于0.5秒
            self.assertLess(max_response_time, 1.0)  # 最大响应时间小于1秒
        
        # 输出结果
        print("API响应时间测试结果:")
        for result in results:
            print(f"  {result['name']}:")
            print(f"    平均响应时间: {result['avg_time']:.3f}秒")
            print(f"    最大响应时间: {result['max_time']:.3f}秒")
            print(f"    最小响应时间: {result['min_time']:.3f}秒")
        
    def test_database_connection_pool(self):
        """测试数据库连接池性能"""
        print("\n测试数据库连接池性能...")
        
        def database_operation(operation_id):
            """数据库操作"""
            start_time = time.time()
            
            # 执行数据库操作
            project = Project(
                project_name=f'连接池测试项目{operation_id}',
                project_type='软件登记业务',
                applicant_type='个人',
                copyright_owner='性能测试用户',
                software_applicant_name='性能测试用户',
                priority='普通',
                price=2000.00,
                status='待确认',
                applicant_id=self.test_user.id
            )
            
            db.session.add(project)
            db.session.commit()
            
            # 查询操作
            projects = Project.query.filter_by(applicant_id=self.test_user.id).all()
            
            db.session.close()
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                'operation_id': operation_id,
                'response_time': response_time,
                'project_count': len(projects)
            }
        
        # 并发数据库操作测试
        concurrent_operations = 30
        results = []
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(database_operation, i) for i in range(concurrent_operations)]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        # 分析结果
        response_times = [r['response_time'] for r in results]
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        # 验证性能指标
        self.assertLess(avg_response_time, 1.0)  # 平均响应时间小于1秒
        self.assertLess(max_response_time, 2.0)  # 最大响应时间小于2秒
        
        print(f"数据库连接池性能测试结果:")
        print(f"  并发操作数: {concurrent_operations}")
        print(f"  平均响应时间: {avg_response_time:.3f}秒")
        print(f"  最大响应时间: {max_response_time:.3f}秒")
        
    def test_memory_usage(self):
        """测试内存使用情况"""
        print("\n测试内存使用情况...")
        
        import psutil
        import gc
        
        # 获取初始内存使用
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量对象
        projects = []
        for i in range(1000):
            project = Project(
                project_name=f'内存测试项目{i}',
                project_type='软件登记业务',
                applicant_type='个人',
                copyright_owner='性能测试用户',
                software_applicant_name='性能测试用户',
                priority='普通',
                price=2000.00,
                status='待确认',
                applicant_id=self.test_user.id
            )
            projects.append(project)
        
        # 获取创建后的内存使用
        after_creation_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 清理对象
        del projects
        gc.collect()
        
        # 获取清理后的内存使用
        after_cleanup_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 计算内存使用
        memory_increase = after_creation_memory - initial_memory
        memory_cleanup = after_creation_memory - after_cleanup_memory
        
        print(f"内存使用测试结果:")
        print(f"  初始内存: {initial_memory:.1f} MB")
        print(f"  创建后内存: {after_creation_memory:.1f} MB")
        print(f"  清理后内存: {after_cleanup_memory:.1f} MB")
        print(f"  内存增长: {memory_increase:.1f} MB")
        print(f"  内存清理: {memory_cleanup:.1f} MB")
        
        # 验证内存使用合理
        self.assertLess(memory_increase, 100)  # 内存增长小于100MB
        
    def test_file_upload_performance(self):
        """测试文件上传性能"""
        print("\n测试文件上传性能...")
        
        # 创建不同大小的测试文件
        file_sizes = [1024, 10240, 102400, 1024000]  # 1KB, 10KB, 100KB, 1MB
        results = []
        
        for size in file_sizes:
            # 创建测试文件内容
            file_content = b'x' * size
            
            start_time = time.time()
            
            # 模拟文件上传
            data = {
                'file': ('test_file.pdf', file_content, 'application/pdf')
            }
            
            response = self.client.post('/upload', data=data)
            
            end_time = time.time()
            upload_time = end_time - start_time
            
            results.append({
                'file_size': size,
                'upload_time': upload_time,
                'throughput': size / upload_time if upload_time > 0 else 0
            })
            
            # 验证上传时间合理
            self.assertLess(upload_time, 5.0)  # 上传时间小于5秒
        
        # 输出结果
        print("文件上传性能测试结果:")
        for result in results:
            print(f"  文件大小: {result['file_size']/1024:.1f} KB")
            print(f"  上传时间: {result['upload_time']:.3f}秒")
            print(f"  吞吐量: {result['throughput']/1024:.1f} KB/s")
        
    def test_desktop_sync_performance(self):
        """测试桌面端同步性能"""
        print("\n测试桌面端同步性能...")
        
        # 创建大量项目用于同步测试
        sync_projects = []
        for i in range(100):
            project = Project(
                project_name=f'同步性能测试项目{i}',
                project_type='软件登记业务',
                applicant_type='个人',
                copyright_owner='性能测试用户',
                software_applicant_name='性能测试用户',
                priority='普通',
                price=2000.00,
                status='已立项',
                applicant_id=self.test_user.id,
                confirmer_id=self.test_executor.id,
                executor_id=self.test_executor.id,
                confirm_time=datetime.utcnow()
            )
            sync_projects.append(project)
        
        db.session.add_all(sync_projects)
        db.session.commit()
        
        # 模拟桌面端同步
        mock_response = {
            'success': True,
            'projects': [{
                'id': p.id,
                'project_name': p.project_name,
                'project_type': p.project_type,
                'applicant_type': p.applicant_type,
                'copyright_owner': p.copyright_owner,
                'software_applicant_name': p.software_applicant_name,
                'serial_number': p.serial_number,
                'priority': p.priority,
                'status': p.status,
                'executor_id': p.executor_id,
                'remarks': p.remarks
            } for p in sync_projects]
        }
        
        self.server_client.get_projects.return_value = mock_response
        
        # 测试同步性能
        start_time = time.time()
        
        result = self.server_client.get_projects(
            self.test_executor.email, 'executor123', 'staff'
        )
        
        end_time = time.time()
        sync_time = end_time - start_time
        
        # 验证同步结果
        self.assertTrue(result['success'])
        self.assertEqual(len(result['projects']), 100)
        
        # 验证同步性能
        self.assertLess(sync_time, 2.0)  # 同步时间小于2秒
        
        print(f"桌面端同步性能测试结果:")
        print(f"  同步项目数: {len(result['projects'])}")
        print(f"  同步时间: {sync_time:.3f}秒")
        print(f"  同步速度: {len(result['projects'])/sync_time:.0f} 项目/秒")
        
    def test_system_throughput(self):
        """测试系统吞吐量"""
        print("\n测试系统吞吐量...")
        
        def system_operation(operation_id):
            """系统操作"""
            start_time = time.time()
            
            # 执行系统操作
            project = Project(
                project_name=f'吞吐量测试项目{operation_id}',
                project_type='软件登记业务',
                applicant_type='个人',
                copyright_owner='性能测试用户',
                software_applicant_name='性能测试用户',
                priority='普通',
                price=2000.00,
                status='待确认',
                applicant_id=self.test_user.id
            )
            
            db.session.add(project)
            db.session.commit()
            
            # 查询操作
            projects = Project.query.filter_by(applicant_id=self.test_user.id).all()
            
            end_time = time.time()
            operation_time = end_time - start_time
            
            return {
                'operation_id': operation_id,
                'operation_time': operation_time,
                'success': True
            }
        
        # 测试系统吞吐量
        total_operations = 200
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(system_operation, i) for i in range(total_operations)]
            
            results = []
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # 计算吞吐量
        throughput = total_operations / total_time
        
        # 验证吞吐量
        self.assertGreater(throughput, 50)  # 吞吐量大于50操作/秒
        
        print(f"系统吞吐量测试结果:")
        print(f"  总操作数: {total_operations}")
        print(f"  总时间: {total_time:.3f}秒")
        print(f"  吞吐量: {throughput:.1f} 操作/秒")

def run_performance_tests():
    """运行性能测试"""
    print("=" * 60)
    print("开始性能测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(PerformanceTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("性能测试完成")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_performance_tests()
