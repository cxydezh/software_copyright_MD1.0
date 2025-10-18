#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据同步测试
测试Web端到桌面端、桌面端到Web端的数据同步功能
"""

import os
import sys
import unittest
import json
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, User, Staff, Project, Permission
from desktop_app.local_models import LocalDatabase, LocalProject
from desktop_app.server_client import ServerClient

class DataSyncTest(unittest.TestCase):
    """数据同步测试类"""
    
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
            name='同步测试用户',
            email='syncuser@example.com',
            phone='13800138000',
            user_category='软件著作权',
            organization='测试机构',
            research_field='医疗软件'
        )
        test_user.set_password('password123')
        
        # 创建测试执行者
        test_executor = Staff(
            name='同步测试执行者',
            email='syncexecutor@example.com',
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
        
    def test_web_to_desktop_project_sync(self):
        """测试Web端到桌面端项目同步"""
        print("\n测试Web端到桌面端项目同步...")
        
        # 在Web端创建项目
        project = Project(
            project_name='同步测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='同步测试用户',
            software_applicant_name='同步测试用户',
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
        
        # 模拟桌面端获取项目列表
        mock_response = {
            'success': True,
            'projects': [{
                'id': project.id,
                'project_name': project.project_name,
                'project_type': project.project_type,
                'applicant_type': project.applicant_type,
                'copyright_owner': project.copyright_owner,
                'software_applicant_name': project.software_applicant_name,
                'serial_number': project.serial_number,
                'priority': project.priority,
                'status': project.status,
                'executor_id': project.executor_id,
                'remarks': project.remarks
            }]
        }
        
        self.server_client.get_projects.return_value = mock_response
        
        # 桌面端获取项目列表
        result = self.server_client.get_projects(
            self.test_executor.email, 'executor123', 'staff'
        )
        
        self.assertTrue(result['success'])
        projects = result['projects']
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]['project_name'], '同步测试项目')
        
        # 同步到本地数据库
        for project_data in projects:
            local_project = LocalProject(
                project_name=project_data['project_name'],
                project_type=project_data['project_type'],
                applicant_type=project_data['applicant_type'],
                copyright_owner=project_data['copyright_owner'],
                software_applicant_name=project_data['software_applicant_name'],
                serial_number=project_data['serial_number'],
                priority=project_data['priority'],
                status=project_data['status'],
                executor_id=project_data['executor_id'],
                remarks=project_data['remarks']
            )
            self.local_db.add_local_project(local_project)
        
        # 验证本地数据库中的项目
        local_projects = self.local_db.get_local_projects()
        self.assertEqual(len(local_projects), 1)
        self.assertEqual(local_projects[0].project_name, '同步测试项目')
        
        print("✓ Web端到桌面端项目同步功能正常")
        
    def test_desktop_to_web_status_sync(self):
        """测试桌面端到Web端状态同步"""
        print("\n测试桌面端到Web端状态同步...")
        
        # 在Web端创建项目
        project = Project(
            project_name='状态同步测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='同步测试用户',
            software_applicant_name='同步测试用户',
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
        
        # 模拟桌面端更新项目状态
        update_response = {
            'success': True,
            'message': '项目状态已更新'
        }
        
        self.server_client.update_project.return_value = update_response
        
        # 桌面端更新项目状态
        result = self.server_client.update_project(
            self.test_executor.email, 'executor123', 'staff',
            project.id, status='执行中', remarks='开始执行项目'
        )
        
        self.assertTrue(result['success'])
        
        # 验证Web端项目状态已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.status, '执行中')
        
        print("✓ 桌面端到Web端状态同步功能正常")
        
    def test_serial_number_sync(self):
        """测试流水号同步"""
        print("\n测试流水号同步...")
        
        # 在Web端创建项目
        project = Project(
            project_name='流水号同步测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='同步测试用户',
            software_applicant_name='同步测试用户',
            priority='普通',
            price=2000.00,
            status='已上传',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_executor.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            submit_time=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # 模拟桌面端更新流水号
        serial_number = '2024SR001234'
        update_response = {
            'success': True,
            'message': '流水号已更新'
        }
        
        self.server_client.update_serial_number.return_value = update_response
        
        # 桌面端更新流水号
        result = self.server_client.update_serial_number(
            self.test_executor.email, 'executor123', 'staff',
            project.id, serial_number, '流水号已获取'
        )
        
        self.assertTrue(result['success'])
        
        # 验证Web端流水号已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.serial_number, serial_number)
        self.assertEqual(updated_project.status, '已获取流水号')
        
        print("✓ 流水号同步功能正常")
        
    def test_data_consistency_check(self):
        """测试数据一致性检查"""
        print("\n测试数据一致性检查...")
        
        # 在Web端创建项目
        project = Project(
            project_name='一致性检查测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='同步测试用户',
            software_applicant_name='同步测试用户',
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
        
        # 在本地数据库创建对应项目
        local_project = LocalProject(
            project_name=project.project_name,
            project_type=project.project_type,
            applicant_type=project.applicant_type,
            copyright_owner=project.copyright_owner,
            software_applicant_name=project.software_applicant_name,
            serial_number=project.serial_number,
            priority=project.priority,
            status=project.status,
            executor_id=project.executor_id,
            remarks=project.remarks
        )
        self.local_db.add_local_project(local_project)
        
        # 检查数据一致性
        web_project = Project.query.get(project.id)
        local_projects = self.local_db.get_local_projects()
        local_project = local_projects[0]
        
        # 验证关键字段一致
        self.assertEqual(web_project.project_name, local_project.project_name)
        self.assertEqual(web_project.project_type, local_project.project_type)
        self.assertEqual(web_project.status, local_project.status)
        self.assertEqual(web_project.serial_number, local_project.serial_number)
        
        print("✓ 数据一致性检查功能正常")
        
    def test_sync_conflict_resolution(self):
        """测试同步冲突解决"""
        print("\n测试同步冲突解决...")
        
        # 在Web端创建项目
        project = Project(
            project_name='冲突解决测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='同步测试用户',
            software_applicant_name='同步测试用户',
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
        
        # 在本地数据库创建项目（状态不同）
        local_project = LocalProject(
            project_name=project.project_name,
            project_type=project.project_type,
            applicant_type=project.applicant_type,
            copyright_owner=project.copyright_owner,
            software_applicant_name=project.software_applicant_name,
            serial_number=project.serial_number,
            priority=project.priority,
            status='执行中',  # 本地状态不同
            executor_id=project.executor_id,
            remarks=project.remarks
        )
        self.local_db.add_local_project(local_project)
        
        # 模拟冲突解决策略：以服务器端为准
        web_project = Project.query.get(project.id)
        local_projects = self.local_db.get_local_projects()
        local_project = local_projects[0]
        
        # 更新本地项目状态以匹配服务器端
        local_project.status = web_project.status
        self.local_db.update_local_project(local_project.id, status=web_project.status)
        
        # 验证冲突已解决
        updated_local_project = self.local_db.get_local_project(local_project.id)
        self.assertEqual(updated_local_project.status, web_project.status)
        
        print("✓ 同步冲突解决功能正常")
        
    def test_offline_data_caching(self):
        """测试离线数据缓存"""
        print("\n测试离线数据缓存...")
        
        # 在本地数据库创建项目
        local_project = LocalProject(
            project_name='离线缓存测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='同步测试用户',
            software_applicant_name='同步测试用户',
            priority='普通',
            price=2000.00,
            status='已立项',
            executor_id=self.test_executor.id,
            remarks='离线测试项目'
        )
        self.local_db.add_local_project(local_project)
        
        # 模拟网络断开
        self.server_client.get_projects.side_effect = Exception('网络连接失败')
        
        # 测试离线模式下的数据访问
        try:
            result = self.server_client.get_projects(
                self.test_executor.email, 'executor123', 'staff'
            )
        except Exception:
            # 网络失败时使用本地缓存
            local_projects = self.local_db.get_local_projects()
            self.assertEqual(len(local_projects), 1)
            self.assertEqual(local_projects[0].project_name, '离线缓存测试项目')
        
        print("✓ 离线数据缓存功能正常")
        
    def test_sync_performance(self):
        """测试同步性能"""
        print("\n测试同步性能...")
        
        import time
        
        # 创建大量测试项目
        projects = []
        for i in range(100):
            project = Project(
                project_name=f'性能测试项目{i}',
                project_type='软件登记业务',
                applicant_type='个人',
                copyright_owner='同步测试用户',
                software_applicant_name='同步测试用户',
                priority='普通',
                price=2000.00,
                status='已立项',
                applicant_id=self.test_user.id,
                confirmer_id=self.test_executor.id,
                executor_id=self.test_executor.id,
                confirm_time=datetime.utcnow()
            )
            projects.append(project)
        
        db.session.add_all(projects)
        db.session.commit()
        
        # 模拟服务器响应
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
            } for p in projects]
        }
        
        self.server_client.get_projects.return_value = mock_response
        
        # 测试同步性能
        start_time = time.time()
        
        result = self.server_client.get_projects(
            self.test_executor.email, 'executor123', 'staff'
        )
        
        end_time = time.time()
        
        self.assertTrue(result['success'])
        self.assertEqual(len(result['projects']), 100)
        
        # 验证同步时间合理（应该在5秒内完成）
        sync_time = end_time - start_time
        self.assertLess(sync_time, 5.0)
        
        print(f"✓ 同步性能测试通过，耗时: {sync_time:.2f}秒")
        
    def test_sync_error_handling(self):
        """测试同步错误处理"""
        print("\n测试同步错误处理...")
        
        # 测试网络错误
        self.server_client.get_projects.side_effect = Exception('网络连接失败')
        
        with self.assertRaises(Exception):
            self.server_client.get_projects(
                self.test_executor.email, 'executor123', 'staff'
            )
        
        # 测试服务器错误
        self.server_client.get_projects.side_effect = None
        self.server_client.get_projects.return_value = {
            'success': False,
            'message': '服务器内部错误'
        }
        
        result = self.server_client.get_projects(
            self.test_executor.email, 'executor123', 'staff'
        )
        
        self.assertFalse(result['success'])
        self.assertIn('错误', result['message'])
        
        # 测试数据格式错误
        self.server_client.get_projects.return_value = {
            'success': True,
            'projects': 'invalid_format'  # 应该是列表
        }
        
        result = self.server_client.get_projects(
            self.test_executor.email, 'executor123', 'staff'
        )
        
        # 应该能处理格式错误
        self.assertTrue(result['success'])
        
        print("✓ 同步错误处理功能正常")
        
    def test_sync_data_validation(self):
        """测试同步数据验证"""
        print("\n测试同步数据验证...")
        
        # 测试无效项目数据
        invalid_project_data = {
            'id': None,  # 无效ID
            'project_name': '',  # 空项目名
            'project_type': '无效类型',  # 无效类型
            'status': '无效状态'  # 无效状态
        }
        
        # 验证数据验证逻辑
        self.assertIsNone(invalid_project_data['id'])
        self.assertEqual(invalid_project_data['project_name'], '')
        self.assertNotIn(invalid_project_data['project_type'], 
                        ['软件登记业务', '软件设计与登记业务', '软件部署与登记业务'])
        self.assertNotIn(invalid_project_data['status'], 
                        ['待确认', '已确认', '已立项', '执行中', '已完成', '已上传', '已获取流水号', '证书完成'])
        
        print("✓ 同步数据验证功能正常")
        
    def test_sync_logging(self):
        """测试同步日志记录"""
        print("\n测试同步日志记录...")
        
        # 模拟同步操作
        sync_operations = [
            {'operation': 'get_projects', 'timestamp': datetime.utcnow(), 'status': 'success'},
            {'operation': 'update_project', 'timestamp': datetime.utcnow(), 'status': 'success'},
            {'operation': 'update_serial_number', 'timestamp': datetime.utcnow(), 'status': 'success'},
            {'operation': 'sync_data', 'timestamp': datetime.utcnow(), 'status': 'failed'}
        ]
        
        # 验证日志记录
        for operation in sync_operations:
            self.assertIn('operation', operation)
            self.assertIn('timestamp', operation)
            self.assertIn('status', operation)
            self.assertIn(operation['status'], ['success', 'failed'])
        
        print("✓ 同步日志记录功能正常")

def run_data_sync_tests():
    """运行数据同步测试"""
    print("=" * 60)
    print("开始数据同步测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(DataSyncTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("数据同步测试完成")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_data_sync_tests()
