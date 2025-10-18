#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
软件著作权业务流程测试
测试完整的软件著作权申请流程：待确认 → 已确认 → 已立项 → 执行中 → 已完成 → 已上传 → 已获取流水号 → 证书完成 → 已结清 → 已归档
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

class SoftwareWorkflowTest(unittest.TestCase):
    """软件著作权业务流程测试类"""
    
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
            name='测试用户',
            email='testuser@example.com',
            phone='13800138000',
            user_category='软件著作权',
            organization='测试机构',
            research_field='医疗软件'
        )
        test_user.set_password('password123')
        
        # 创建测试员工
        test_staff = Staff(
            name='测试业务员',
            email='teststaff@example.com',
            phone='13800138001',
            position_id=1  # 普通业务员
        )
        test_staff.set_password('staff123')
        
        # 创建测试执行者
        test_executor = Staff(
            name='测试执行者',
            email='testexecutor@example.com',
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
        self.test_project_data = {
            'project_name': '医疗管理系统V1.0',
            'project_type': '软件登记业务',
            'applicant_type': '个人',
            'copyright_owner': '测试用户',
            'software_applicant_name': '测试用户',
            'priority': '普通',
            'price': 2000.00,
            'remarks': '测试项目备注'
        }
        
    def test_user_submit_application(self):
        """测试用户提交申请"""
        print("\n测试用户提交申请...")
        
        # 用户登录
        login_data = {
            'email': self.test_user.email,
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 提交项目申请
        response = self.client.post('/user/apply', 
                                  data=self.test_project_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证项目已创建
        project = Project.query.filter_by(project_name=self.test_project_data['project_name']).first()
        self.assertIsNotNone(project)
        self.assertEqual(project.status, '待确认')
        self.assertEqual(project.applicant_id, self.test_user.id)
        
        print("✓ 用户提交申请功能正常")
        
    def test_staff_confirm_application(self):
        """测试业务员确认申请"""
        print("\n测试业务员确认申请...")
        
        # 先创建待确认的项目
        project = Project(
            project_name='待确认项目',
            project_type='软件设计与登记业务',
            applicant_type='事业单位',
            copyright_owner='测试医院',
            software_applicant_name='测试医院',
            priority='加急',
            price=5000.00,
            status='待确认',
            applicant_id=self.test_user.id
        )
        db.session.add(project)
        db.session.commit()
        
        # 业务员登录
        login_data = {
            'email': self.test_staff.email,
            'password': 'staff123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 确认申请
        confirm_data = {
            'status': '已确认',
            'remarks': '申请已确认，准备立项'
        }
        
        response = self.client.post(f'/staff/project/{project.id}/update_status', 
                                  data=confirm_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.status, '已确认')
        self.assertIsNotNone(updated_project.confirm_time)
        
        print("✓ 业务员确认申请功能正常")
        
    def test_staff_approve_project(self):
        """测试业务员立项审批"""
        print("\n测试业务员立项审批...")
        
        # 先创建已确认的项目
        project = Project(
            project_name='已确认项目',
            project_type='软件部署与登记业务',
            applicant_type='事业单位联合个人',
            copyright_owner='测试医院,测试用户',
            software_applicant_name='测试医院',
            priority='快速',
            price=8000.00,
            status='已确认',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            confirm_time=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # 业务员登录
        login_data = {
            'email': self.test_staff.email,
            'password': 'staff123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 立项审批
        approve_data = {
            'status': '已立项',
            'executor_id': self.test_executor.id,
            'remarks': '项目已立项，分配给执行者'
        }
        
        response = self.client.post(f'/staff/project/{project.id}/approve', 
                                  data=approve_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.status, '已立项')
        self.assertEqual(updated_project.executor_id, self.test_executor.id)
        
        print("✓ 业务员立项审批功能正常")
        
    def test_executor_accept_project(self):
        """测试执行者接收项目"""
        print("\n测试执行者接收项目...")
        
        # 先创建已立项的项目
        project = Project(
            project_name='已立项项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='测试用户',
            software_applicant_name='测试用户',
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
        
        # 执行者登录
        login_data = {
            'email': self.test_executor.email,
            'password': 'executor123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 接收项目
        accept_data = {
            'status': '执行中',
            'remarks': '开始执行项目'
        }
        
        response = self.client.post(f'/staff/project/{project.id}/accept', 
                                  data=accept_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.status, '执行中')
        self.assertIsNotNone(updated_project.execute_time)
        
        print("✓ 执行者接收项目功能正常")
        
    def test_executor_complete_project(self):
        """测试执行者完成项目"""
        print("\n测试执行者完成项目...")
        
        # 先创建执行中的项目
        project = Project(
            project_name='执行中项目',
            project_type='软件设计与登记业务',
            applicant_type='事业单位',
            copyright_owner='测试医院',
            software_applicant_name='测试医院',
            priority='加急',
            price=5000.00,
            status='执行中',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            execute_time=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # 执行者登录
        login_data = {
            'email': self.test_executor.email,
            'password': 'executor123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 完成项目
        complete_data = {
            'status': '已完成',
            'remarks': '项目执行完成'
        }
        
        response = self.client.post(f'/staff/project/{project.id}/complete', 
                                  data=complete_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.status, '已完成')
        self.assertIsNotNone(updated_project.complete_time)
        
        print("✓ 执行者完成项目功能正常")
        
    def test_upload_to_copyright_center(self):
        """测试上传到版权中心"""
        print("\n测试上传到版权中心...")
        
        # 先创建已完成的项目
        project = Project(
            project_name='已完成项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='测试用户',
            software_applicant_name='测试用户',
            priority='普通',
            price=2000.00,
            status='已完成',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            execute_time=datetime.utcnow(),
            complete_time=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # 执行者登录
        login_data = {
            'email': self.test_executor.email,
            'password': 'executor123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 标记已上传
        upload_data = {
            'status': '已上传',
            'remarks': '已上传到版权中心'
        }
        
        response = self.client.post(f'/staff/project/{project.id}/upload', 
                                  data=upload_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.status, '已上传')
        self.assertIsNotNone(updated_project.submit_time)
        
        print("✓ 上传到版权中心功能正常")
        
    def test_update_serial_number(self):
        """测试更新流水号"""
        print("\n测试更新流水号...")
        
        # 先创建已上传的项目
        project = Project(
            project_name='已上传项目',
            project_type='软件设计与登记业务',
            applicant_type='事业单位',
            copyright_owner='测试医院',
            software_applicant_name='测试医院',
            priority='加急',
            price=5000.00,
            status='已上传',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            execute_time=datetime.utcnow(),
            complete_time=datetime.utcnow(),
            submit_time=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # 执行者登录
        login_data = {
            'email': self.test_executor.email,
            'password': 'executor123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 更新流水号
        serial_number = '2024SR001234'
        update_data = {
            'serial_number': serial_number,
            'status': '已获取流水号',
            'remarks': f'流水号已更新: {serial_number}'
        }
        
        response = self.client.post(f'/staff/project/{project.id}/update_serial', 
                                  data=update_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证流水号已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.serial_number, serial_number)
        self.assertEqual(updated_project.status, '已获取流水号')
        
        print("✓ 更新流水号功能正常")
        
    def test_certificate_completion(self):
        """测试证书完成"""
        print("\n测试证书完成...")
        
        # 先创建已获取流水号的项目
        project = Project(
            project_name='已获取流水号项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='测试用户',
            software_applicant_name='测试用户',
            priority='普通',
            price=2000.00,
            serial_number='2024SR001235',
            status='已获取流水号',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            execute_time=datetime.utcnow(),
            complete_time=datetime.utcnow(),
            submit_time=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # 执行者登录
        login_data = {
            'email': self.test_executor.email,
            'password': 'executor123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 标记证书完成
        certificate_data = {
            'status': '证书完成',
            'remarks': '证书已下发'
        }
        
        response = self.client.post(f'/staff/project/{project.id}/certificate', 
                                  data=certificate_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_project = Project.query.get(project.id)
        self.assertEqual(updated_project.status, '证书完成')
        self.assertIsNotNone(updated_project.certificate_time)
        
        print("✓ 证书完成功能正常")
        
    def test_project_settlement(self):
        """测试项目结清"""
        print("\n测试项目结清...")
        
        # 先创建证书完成的项目
        project = Project(
            project_name='证书完成项目',
            project_type='软件设计与登记业务',
            applicant_type='事业单位',
            copyright_owner='测试医院',
            software_applicant_name='测试医院',
            priority='加急',
            price=5000.00,
            serial_number='2024SR001236',
            status='证书完成',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            execute_time=datetime.utcnow(),
            complete_time=datetime.utcnow(),
            submit_time=datetime.utcnow(),
            certificate_time=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # 业务员登录
        login_data = {
            'email': self.test_staff.email,
            'password': 'staff123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 标记项目结清
        settlement_data = {
            'is_settled': True,
            'remarks': '项目款项已结清'
        }
        
        response = self.client.post(f'/staff/project/{project.id}/settle', 
                                  data=settlement_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证结清状态已更新
        updated_project = Project.query.get(project.id)
        self.assertTrue(updated_project.is_settled)
        self.assertIsNotNone(updated_project.settle_time)
        
        print("✓ 项目结清功能正常")
        
    def test_project_archiving(self):
        """测试项目归档"""
        print("\n测试项目归档...")
        
        # 先创建已结清的项目
        project = Project(
            project_name='已结清项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='测试用户',
            software_applicant_name='测试用户',
            priority='普通',
            price=2000.00,
            serial_number='2024SR001237',
            status='证书完成',
            is_settled=True,
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            execute_time=datetime.utcnow(),
            complete_time=datetime.utcnow(),
            submit_time=datetime.utcnow(),
            certificate_time=datetime.utcnow(),
            settle_time=datetime.utcnow()
        )
        db.session.add(project)
        db.session.commit()
        
        # 业务员登录
        login_data = {
            'email': self.test_staff.email,
            'password': 'staff123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 归档项目
        archive_data = {
            'is_archived': True,
            'remarks': '项目已归档'
        }
        
        response = self.client.post(f'/staff/project/{project.id}/archive', 
                                  data=archive_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证归档状态已更新
        updated_project = Project.query.get(project.id)
        self.assertTrue(updated_project.is_archived)
        
        print("✓ 项目归档功能正常")
        
    def test_complete_workflow(self):
        """测试完整业务流程"""
        print("\n测试完整业务流程...")
        
        # 创建新项目
        project = Project(
            project_name='完整流程测试项目',
            project_type='软件部署与登记业务',
            applicant_type='事业单位联合个人',
            copyright_owner='测试医院,测试用户',
            software_applicant_name='测试医院',
            priority='快速',
            price=8000.00,
            status='待确认',
            applicant_id=self.test_user.id
        )
        db.session.add(project)
        db.session.commit()
        
        # 1. 业务员确认
        project.status = '已确认'
        project.confirmer_id = self.test_staff.id
        project.confirm_time = datetime.utcnow()
        
        # 2. 业务员立项
        project.status = '已立项'
        project.executor_id = self.test_executor.id
        
        # 3. 执行者接收
        project.status = '执行中'
        project.execute_time = datetime.utcnow()
        
        # 4. 执行者完成
        project.status = '已完成'
        project.complete_time = datetime.utcnow()
        
        # 5. 上传版权中心
        project.status = '已上传'
        project.submit_time = datetime.utcnow()
        
        # 6. 获取流水号
        project.status = '已获取流水号'
        project.serial_number = '2024SR001238'
        
        # 7. 证书完成
        project.status = '证书完成'
        project.certificate_time = datetime.utcnow()
        
        # 8. 项目结清
        project.is_settled = True
        project.settle_time = datetime.utcnow()
        
        # 9. 项目归档
        project.is_archived = True
        
        db.session.commit()
        
        # 验证完整流程
        final_project = Project.query.get(project.id)
        self.assertEqual(final_project.status, '证书完成')
        self.assertTrue(final_project.is_settled)
        self.assertTrue(final_project.is_archived)
        self.assertEqual(final_project.serial_number, '2024SR001238')
        
        print("✓ 完整业务流程测试通过")
        
    def test_process_logging(self):
        """测试流程日志记录"""
        print("\n测试流程日志记录...")
        
        # 创建项目
        project = Project(
            project_name='日志测试项目',
            project_type='软件登记业务',
            applicant_type='个人',
            copyright_owner='测试用户',
            software_applicant_name='测试用户',
            priority='普通',
            price=2000.00,
            status='待确认',
            applicant_id=self.test_user.id
        )
        db.session.add(project)
        db.session.commit()
        
        # 记录流程日志
        log = ProcessLog(
            project_id=project.id,
            project_type='软件登记业务',
            action='项目创建',
            operator_id=self.test_user.id,
            operator_name=self.test_user.name,
            remarks='用户提交项目申请'
        )
        db.session.add(log)
        db.session.commit()
        
        # 验证日志已记录
        logs = ProcessLog.query.filter_by(project_id=project.id).all()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].action, '项目创建')
        
        print("✓ 流程日志记录功能正常")

def run_software_workflow_tests():
    """运行软件著作权业务流程测试"""
    print("=" * 60)
    print("开始软件著作权业务流程测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(SoftwareWorkflowTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("软件著作权业务流程测试完成")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_software_workflow_tests()
