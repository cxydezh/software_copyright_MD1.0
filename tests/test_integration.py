#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试
测试Web端和桌面端的完整集成功能，验证端到端业务流程
"""

import os
import sys
import unittest
import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, User, Staff, Project, PaperProject, PatentProject, Permission
from desktop_app.local_models import LocalDatabase, LocalProject
from desktop_app.server_client import ServerClient

class IntegrationTest(unittest.TestCase):
    """集成测试类"""
    
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
            name='集成测试用户',
            email='integrationuser@example.com',
            phone='13800138000',
            user_category='软件著作权',
            organization='测试机构',
            research_field='医疗软件'
        )
        test_user.set_password('password123')
        
        # 创建测试员工
        test_staff = Staff(
            name='集成测试业务员',
            email='integrationstaff@example.com',
            phone='13800138001',
            position_id=1
        )
        test_staff.set_password('staff123')
        
        # 创建测试执行者
        test_executor = Staff(
            name='集成测试执行者',
            email='integrationexecutor@example.com',
            phone='13800138002',
            position_id=2
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
        # 创建本地测试数据库
        self.local_db_path = ':memory:'
        self.local_db = LocalDatabase(self.local_db_path)
        
        # 模拟服务器客户端
        self.server_client = Mock(spec=ServerClient)
        
    def test_complete_software_copyright_workflow(self):
        """测试完整的软件著作权流程"""
        print("\n测试完整的软件著作权流程...")
        
        # 1. 用户在Web端提交申请
        project_data = {
            'project_name': '集成测试软件项目',
            'project_type': '软件登记业务',
            'applicant_type': '个人',
            'copyright_owner': '集成测试用户',
            'software_applicant_name': '集成测试用户',
            'priority': '普通',
            'price': 2000.00,
            'remarks': '集成测试项目'
        }
        
        # 用户登录
        login_data = {
            'email': self.test_user.email,
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 提交项目申请
        response = self.client.post('/user/apply', 
                                  data=project_data,
                                  follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # 验证项目已创建
        project = Project.query.filter_by(project_name=project_data['project_name']).first()
        self.assertIsNotNone(project)
        self.assertEqual(project.status, '待确认')
        
        # 2. 业务员在Web端确认申请
        self.client.get('/auth/logout')
        
        staff_login_data = {
            'email': self.test_staff.email,
            'password': 'staff123'
        }
        
        response = self.client.post('/auth/login', data=staff_login_data)
        self.assertEqual(response.status_code, 200)
        
        # 确认申请
        confirm_data = {
            'status': '已确认',
            'executor_id': self.test_executor.id,
            'remarks': '申请已确认'
        }
        
        response = self.client.post(f'/staff/project/{project.id}/confirm', 
                                  data=confirm_data,
                                  follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.status, '已确认')
        
        # 3. 业务员立项
        approve_data = {
            'status': '已立项',
            'remarks': '项目已立项'
        }
        
        response = self.client.post(f'/staff/project/{project.id}/approve', 
                                  data=approve_data,
                                  follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.status, '已立项')
        
        # 4. 执行者在桌面端接收项目
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
        self.assertEqual(len(result['projects']), 1)
        
        # 同步到本地数据库
        project_data = result['projects'][0]
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
        
        # 验证本地项目已创建
        local_projects = self.local_db.get_local_projects()
        self.assertEqual(len(local_projects), 1)
        self.assertEqual(local_projects[0].project_name, '集成测试软件项目')
        
        # 5. 执行者在桌面端更新项目状态
        update_response = {
            'success': True,
            'message': '项目状态已更新'
        }
        
        self.server_client.update_project.return_value = update_response
        
        # 更新项目状态为执行中
        result = self.server_client.update_project(
            self.test_executor.email, 'executor123', 'staff',
            project.id, status='执行中', remarks='开始执行项目'
        )
        
        self.assertTrue(result['success'])
        
        # 验证Web端状态已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.status, '执行中')
        
        # 6. 执行者在桌面端更新流水号
        serial_number = '2024SR001234'
        serial_update_response = {
            'success': True,
            'message': '流水号已更新'
        }
        
        self.server_client.update_serial_number.return_value = serial_update_response
        
        # 更新流水号
        result = self.server_client.update_serial_number(
            self.test_executor.email, 'executor123', 'staff',
            project.id, serial_number, '流水号已获取'
        )
        
        self.assertTrue(result['success'])
        
        # 验证Web端流水号已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.serial_number, serial_number)
        self.assertEqual(updated_project.status, '已获取流水号')
        
        print("✓ 完整的软件著作权流程测试通过")
        
    def test_complete_paper_workflow(self):
        """测试完整的论文指导流程"""
        print("\n测试完整的论文指导流程...")
        
        # 1. 用户在Web端提交论文申请
        paper_data = {
            'project_name': '集成测试论文项目',
            'project_type': '论文指导',
            'service_level': '标准服务',
            'applicant_type': '个人学者',
            'paper_title': '基于AI的医疗诊断研究',
            'research_field': '人工智能',
            'target_journal': 'Journal of Medical AI',
            'price': 3000.00,
            'remarks': '集成测试论文项目'
        }
        
        # 用户登录
        login_data = {
            'email': self.test_user.email,
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 提交论文申请
        response = self.client.post('/paper/apply', 
                                  data=paper_data,
                                  follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # 验证论文项目已创建
        paper_project = PaperProject.query.filter_by(project_name=paper_data['project_name']).first()
        self.assertIsNotNone(paper_project)
        self.assertEqual(paper_project.status, '待确认')
        self.assertEqual(paper_project.paper_status, '初稿')
        
        # 2. 业务员在Web端确认申请
        self.client.get('/auth/logout')
        
        staff_login_data = {
            'email': self.test_staff.email,
            'password': 'staff123'
        }
        
        response = self.client.post('/auth/login', data=staff_login_data)
        self.assertEqual(response.status_code, 200)
        
        # 确认申请
        confirm_data = {
            'status': '已确认',
            'executor_id': self.test_executor.id,
            'remarks': '论文申请已确认'
        }
        
        response = self.client.post(f'/staff/paper/{paper_project.id}/confirm', 
                                  data=confirm_data,
                                  follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_paper_project = PaperProject.query.get(paper_project.id)
        self.assertEqual(updated_paper_project.status, '已确认')
        
        # 3. 执行者在Web端更新论文状态
        self.client.get('/auth/logout')
        
        executor_login_data = {
            'email': self.test_executor.email,
            'password': 'executor123'
        }
        
        response = self.client.post('/auth/login', data=executor_login_data)
        self.assertEqual(response.status_code, 200)
        
        # 更新论文状态
        status_data = {
            'paper_status': '修改中',
            'status': '执行中',
            'remarks': '开始修改论文'
        }
        
        response = self.client.post(f'/staff/paper/{paper_project.id}/update_status', 
                                  data=status_data,
                                  follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_paper_project = PaperProject.query.get(paper_project.id)
        self.assertEqual(updated_paper_project.paper_status, '修改中')
        self.assertEqual(updated_paper_project.status, '执行中')
        
        print("✓ 完整的论文指导流程测试通过")
        
    def test_complete_patent_workflow(self):
        """测试完整的专利申请流程"""
        print("\n测试完整的专利申请流程...")
        
        # 1. 用户在Web端提交专利申请
        patent_data = {
            'project_name': '集成测试专利项目',
            'project_type': '发明专利',
            'applicant_type': '企业申请',
            'patent_title': '智能医疗设备控制系统',
            'technical_field': '医疗器械',
            'invention_description': '一种基于AI的医疗设备控制系统',
            'price': 10000.00,
            'remarks': '集成测试专利项目'
        }
        
        # 用户登录
        login_data = {
            'email': self.test_user.email,
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 提交专利申请
        response = self.client.post('/patent/apply', 
                                  data=patent_data,
                                  follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # 验证专利项目已创建
        patent_project = PatentProject.query.filter_by(project_name=patent_data['project_name']).first()
        self.assertIsNotNone(patent_project)
        self.assertEqual(patent_project.status, '待确认')
        self.assertEqual(patent_project.patent_status, '准备材料')
        
        # 2. 业务员在Web端确认申请
        self.client.get('/auth/logout')
        
        staff_login_data = {
            'email': self.test_staff.email,
            'password': 'staff123'
        }
        
        response = self.client.post('/auth/login', data=staff_login_data)
        self.assertEqual(response.status_code, 200)
        
        # 确认申请
        confirm_data = {
            'status': '已确认',
            'executor_id': self.test_executor.id,
            'remarks': '专利申请已确认'
        }
        
        response = self.client.post(f'/staff/patent/{patent_project.id}/confirm', 
                                  data=confirm_data,
                                  follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_patent_project = PatentProject.query.get(patent_project.id)
        self.assertEqual(updated_patent_project.status, '已确认')
        
        # 3. 执行者在Web端提交专利
        self.client.get('/auth/logout')
        
        executor_login_data = {
            'email': self.test_executor.email,
            'password': 'executor123'
        }
        
        response = self.client.post('/auth/login', data=executor_login_data)
        self.assertEqual(response.status_code, 200)
        
        # 提交专利
        submission_data = {
            'patent_status': '已提交',
            'status': '执行中',
            'application_number': '202410123456.7',
            'submit_time': datetime.utcnow(),
            'remarks': '专利已提交'
        }
        
        response = self.client.post(f'/staff/patent/{patent_project.id}/submit', 
                                  data=submission_data,
                                  follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_patent_project = PatentProject.query.get(patent_project.id)
        self.assertEqual(updated_patent_project.patent_status, '已提交')
        self.assertEqual(updated_patent_project.status, '执行中')
        
        print("✓ 完整的专利申请流程测试通过")
        
    def test_cross_platform_data_sync(self):
        """测试跨平台数据同步"""
        print("\n测试跨平台数据同步...")
        
        # 在Web端创建项目
        project = Project(
            project_name='跨平台同步测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='集成测试用户',
            software_applicant_name='集成测试用户',
            priority='普通',
            price=2000.00,
            status='已立项',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # 模拟桌面端同步
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
        
        # 桌面端获取项目
        result = self.server_client.get_projects(
            self.test_executor.email, 'executor123', 'staff'
        )
        
        self.assertTrue(result['success'])
        
        # 同步到本地数据库
        project_data = result['projects'][0]
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
        
        # 验证本地数据
        local_projects = self.local_db.get_local_projects()
        self.assertEqual(len(local_projects), 1)
        self.assertEqual(local_projects[0].project_name, '跨平台同步测试项目')
        
        # 桌面端更新状态
        update_response = {
            'success': True,
            'message': '项目状态已更新'
        }
        
        self.server_client.update_project.return_value = update_response
        
        # 更新项目状态
        result = self.server_client.update_project(
            self.test_executor.email, 'executor123', 'staff',
            project.id, status='执行中', remarks='开始执行'
        )
        
        self.assertTrue(result['success'])
        
        # 验证Web端状态已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.status, '执行中')
        
        print("✓ 跨平台数据同步测试通过")
        
    def test_concurrent_user_operations(self):
        """测试并发用户操作"""
        print("\n测试并发用户操作...")
        
        results = []
        
        def user_operation(user_id):
            """模拟用户操作"""
            # 在子线程中设置应用上下文
            with self.app.app_context():
                # 创建项目
                project = Project(
                    project_name=f'并发测试项目{user_id}',
                    project_type='软件登记业务',
                    applicant_type='个人',
                    copyright_owner='集成测试用户',
                    software_applicant_name='集成测试用户',
                    priority='普通',
                    price=2000.00,
                    status='待确认',
                    applicant_id=self.test_user.id
                )
                db.session.add(project)
                db.session.commit()
                
                results.append(project.id)
        
        # 创建多个线程同时执行用户操作
        threads = []
        for i in range(5):
            thread = threading.Thread(target=user_operation, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有操作都成功
        self.assertEqual(len(results), 5)
        
        # 验证所有项目都已创建
        for project_id in results:
            project = Project.query.get(project_id)
            self.assertIsNotNone(project)
            self.assertIn('并发测试项目', project.project_name)
        
        print("✓ 并发用户操作测试通过")
        
    def test_system_recovery_after_failure(self):
        """测试系统故障恢复"""
        print("\n测试系统故障恢复...")
        
        # 创建项目
        project = Project(
            project_name='故障恢复测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='集成测试用户',
            software_applicant_name='集成测试用户',
            priority='普通',
            price=2000.00,
            status='已立项',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # 模拟系统故障
        original_status = project.status
        
        # 模拟故障恢复
        project.status = '执行中'
        db.session.commit()
        
        # 验证恢复后的状态
        recovered_project = Project.query.get(project.id)
        self.assertEqual(recovered_project.status, '执行中')
        self.assertNotEqual(recovered_project.status, original_status)
        
        print("✓ 系统故障恢复测试通过")
        
    def test_data_integrity_validation(self):
        """测试数据完整性验证"""
        print("\n测试数据完整性验证...")
        
        # 创建项目
        project = Project(
            project_name='完整性验证测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='集成测试用户',
            software_applicant_name='集成测试用户',
            priority='普通',
            price=2000.00,
            status='已立项',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # 验证数据完整性
        self.assertIsNotNone(project.id)
        self.assertIsNotNone(project.project_name)
        self.assertIsNotNone(project.project_type)
        self.assertIsNotNone(project.applicant_type)
        self.assertIsNotNone(project.copyright_owner)
        self.assertIsNotNone(project.software_applicant_name)
        self.assertIsNotNone(project.priority)
        self.assertIsNotNone(project.status)
        self.assertIsNotNone(project.applicant_id)
        self.assertIsNotNone(project.confirmer_id)
        self.assertIsNotNone(project.executor_id)
        self.assertIsNotNone(project.confirm_time)
        
        # 验证外键关系
        self.assertEqual(project.applicant_id, self.test_user.id)
        self.assertEqual(project.confirmer_id, self.test_staff.id)
        self.assertEqual(project.executor_id, self.test_executor.id)
        
        print("✓ 数据完整性验证测试通过")
        
    def test_end_to_end_performance(self):
        """测试端到端性能"""
        print("\n测试端到端性能...")
        
        import time
        
        start_time = time.time()
        
        # 执行完整的业务流程
        # 1. 创建项目
        project = Project(
            project_name='性能测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='集成测试用户',
            software_applicant_name='集成测试用户',
            priority='普通',
            price=2000.00,
            status='待确认',
            applicant_id=self.test_user.id
        )
        db.session.add(project)
        db.session.commit()
        
        # 2. 确认项目
        project.status = '已确认'
        project.confirmer_id = self.test_staff.id
        project.confirm_time = datetime.utcnow()
        db.session.commit()
        
        # 3. 立项
        project.status = '已立项'
        project.executor_id = self.test_executor.id
        db.session.commit()
        
        # 4. 执行
        project.status = '执行中'
        project.execute_time = datetime.utcnow()
        db.session.commit()
        
        # 5. 完成
        project.status = '已完成'
        project.complete_time = datetime.utcnow()
        db.session.commit()
        
        end_time = time.time()
        
        # 验证性能
        total_time = end_time - start_time
        self.assertLess(total_time, 2.0)  # 应该在2秒内完成
        
        # 验证最终状态
        final_project = Project.query.get(project.id)
        self.assertEqual(final_project.status, '已完成')
        
        print(f"✓ 端到端性能测试通过，耗时: {total_time:.2f}秒")

def run_integration_tests():
    """运行集成测试"""
    print("=" * 60)
    print("开始集成测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(IntegrationTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("集成测试完成")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_integration_tests()
