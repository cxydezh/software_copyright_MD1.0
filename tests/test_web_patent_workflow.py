#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专利申请业务流程测试
测试专利申请、专利管理、专利转化的完整流程
"""

import os
import sys
import unittest
import json
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, User, Staff, PatentProject, Permission, ProcessLog
from flask_login import login_user

class PatentWorkflowTest(unittest.TestCase):
    """专利申请业务流程测试类"""
    
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
            name='专利测试用户',
            email='patentuser@example.com',
            phone='13800138000',
            user_category='专利申请',
            organization='测试企业',
            research_field='医疗器械'
        )
        test_user.set_password('password123')
        
        # 创建测试员工
        test_staff = Staff(
            name='专利测试业务员',
            email='patentstaff@example.com',
            phone='13800138001',
            position_id=1  # 普通业务员
        )
        test_staff.set_password('staff123')
        
        # 创建测试执行者
        test_executor = Staff(
            name='专利测试执行者',
            email='patentexecutor@example.com',
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
        self.test_patent_project_data = {
            'project_name': '智能医疗设备控制系统',
            'project_type': '发明专利',
            'applicant_type': '企业申请',
            'patent_title': '智能医疗设备控制系统',
            'technical_field': '医疗器械',
            'invention_description': '一种基于AI的医疗设备智能控制系统',
            'price': 10000.00,
            'remarks': '需要专业的医疗器械专利申请服务'
        }
        
    def test_user_submit_patent_application(self):
        """测试用户提交专利申请"""
        print("\n测试用户提交专利申请...")
        
        # 用户登录
        login_data = {
            'email': self.test_user.email,
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 提交专利申请
        response = self.client.post('/patent/apply', 
                                  data=self.test_patent_project_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证专利项目已创建
        project = PatentProject.query.filter_by(project_name=self.test_patent_project_data['project_name']).first()
        self.assertIsNotNone(project)
        self.assertEqual(project.status, '待确认')
        self.assertEqual(project.applicant_id, self.test_user.id)
        self.assertEqual(project.patent_status, '准备材料')
        
        print("✓ 用户提交专利申请功能正常")
        
    def test_patent_application_confirmation(self):
        """测试专利申请确认"""
        print("\n测试专利申请确认...")
        
        # 创建专利申请项目
        project = PatentProject(
            project_name='专利确认测试项目',
            project_type='发明专利',
            applicant_type='企业申请',
            patent_title='医疗AI诊断系统',
            technical_field='人工智能',
            invention_description='基于深度学习的医疗诊断系统',
            patent_status='准备材料',
            price=12000.00,
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
            'executor_id': self.test_executor.id,
            'remarks': '专利申请已确认'
        }
        
        response = self.client.post(f'/staff/patent/{project.id}/confirm', 
                                  data=confirm_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_project = PatentProject.query.get(project.id)
        self.assertEqual(updated_project.status, '已确认')
        self.assertEqual(updated_project.executor_id, self.test_executor.id)
        
        print("✓ 专利申请确认功能正常")
        
    def test_patent_submission(self):
        """测试专利提交"""
        print("\n测试专利提交...")
        
        # 创建已确认的专利项目
        project = PatentProject(
            project_name='专利提交测试项目',
            project_type='实用新型专利',
            applicant_type='个人发明者',
            patent_title='便携式医疗检测设备',
            technical_field='医疗器械',
            invention_description='一种便携式医疗检测设备',
            patent_status='准备材料',
            price=8000.00,
            status='已确认',
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
        
        # 提交专利
        submission_data = {
            'patent_status': '已提交',
            'status': '执行中',
            'application_number': '202410123456.7',
            'submit_time': datetime.utcnow(),
            'remarks': '专利已提交到国家知识产权局'
        }
        
        response = self.client.post(f'/staff/patent/{project.id}/submit', 
                                  data=submission_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_project = PatentProject.query.get(project.id)
        self.assertEqual(updated_project.patent_status, '已提交')
        self.assertEqual(updated_project.status, '执行中')
        self.assertEqual(updated_project.application_number, '202410123456.7')
        self.assertIsNotNone(updated_project.submit_time)
        
        print("✓ 专利提交功能正常")
        
    def test_patent_acceptance(self):
        """测试专利受理"""
        print("\n测试专利受理...")
        
        # 创建已提交的专利项目
        project = PatentProject(
            project_name='专利受理测试项目',
            project_type='外观设计专利',
            applicant_type='科研院所',
            patent_title='医疗设备外观设计',
            technical_field='工业设计',
            invention_description='医疗设备的外观设计',
            patent_status='已提交',
            application_number='202410123457.8',
            price=6000.00,
            status='执行中',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
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
        
        # 专利受理
        acceptance_data = {
            'patent_status': '受理中',
            'acceptance_number': '202410123457.8',
            'acceptance_time': datetime.utcnow(),
            'remarks': '专利已被国家知识产权局受理'
        }
        
        response = self.client.post(f'/staff/patent/{project.id}/accept', 
                                  data=acceptance_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证受理状态
        updated_project = PatentProject.query.get(project.id)
        self.assertEqual(updated_project.patent_status, '受理中')
        self.assertEqual(updated_project.acceptance_number, '202410123457.8')
        self.assertIsNotNone(updated_project.acceptance_time)
        
        print("✓ 专利受理功能正常")
        
    def test_patent_examination(self):
        """测试专利审查"""
        print("\n测试专利审查...")
        
        # 创建受理中的专利项目
        project = PatentProject(
            project_name='专利审查测试项目',
            project_type='发明专利',
            applicant_type='企业申请',
            patent_title='智能医疗机器人系统',
            technical_field='机器人技术',
            invention_description='一种智能医疗机器人系统',
            patent_status='受理中',
            application_number='202410123458.9',
            acceptance_number='202410123458.9',
            price=15000.00,
            status='执行中',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            submit_time=datetime.utcnow(),
            acceptance_time=datetime.utcnow()
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
        
        # 专利审查
        examination_data = {
            'patent_status': '审查中',
            'examination_time': datetime.utcnow(),
            'remarks': '专利进入实质审查阶段'
        }
        
        response = self.client.post(f'/staff/patent/{project.id}/examine', 
                                  data=examination_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证审查状态
        updated_project = PatentProject.query.get(project.id)
        self.assertEqual(updated_project.patent_status, '审查中')
        self.assertIsNotNone(updated_project.examination_time)
        
        print("✓ 专利审查功能正常")
        
    def test_patent_authorization(self):
        """测试专利授权"""
        print("\n测试专利授权...")
        
        # 创建审查中的专利项目
        project = PatentProject(
            project_name='专利授权测试项目',
            project_type='发明专利',
            applicant_type='联合申请',
            patent_title='医疗大数据分析系统',
            technical_field='大数据',
            invention_description='一种医疗大数据分析系统',
            patent_status='审查中',
            application_number='202410123459.0',
            acceptance_number='202410123459.0',
            price=18000.00,
            status='执行中',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            submit_time=datetime.utcnow(),
            acceptance_time=datetime.utcnow(),
            examination_time=datetime.utcnow()
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
        
        # 专利授权
        authorization_data = {
            'patent_status': '授权',
            'patent_number': 'ZL202410123459.0',
            'authorization_time': datetime.utcnow(),
            'remarks': '专利已获得授权'
        }
        
        response = self.client.post(f'/staff/patent/{project.id}/authorize', 
                                  data=authorization_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证授权状态
        updated_project = PatentProject.query.get(project.id)
        self.assertEqual(updated_project.patent_status, '授权')
        self.assertEqual(updated_project.patent_number, 'ZL202410123459.0')
        self.assertIsNotNone(updated_project.authorization_time)
        
        print("✓ 专利授权功能正常")
        
    def test_patent_certificate_issuance(self):
        """测试专利证书下发"""
        print("\n测试专利证书下发...")
        
        # 创建已授权的专利项目
        project = PatentProject(
            project_name='专利证书测试项目',
            project_type='实用新型专利',
            applicant_type='企业申请',
            patent_title='智能医疗监护系统',
            technical_field='医疗监护',
            invention_description='一种智能医疗监护系统',
            patent_status='授权',
            application_number='202410123460.1',
            acceptance_number='202410123460.1',
            patent_number='ZL202410123460.1',
            price=10000.00,
            status='执行中',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            submit_time=datetime.utcnow(),
            acceptance_time=datetime.utcnow(),
            examination_time=datetime.utcnow(),
            authorization_time=datetime.utcnow()
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
        
        # 专利证书下发
        certificate_data = {
            'patent_status': '已发证',
            'status': '已完成',
            'certificate_time': datetime.utcnow(),
            'remarks': '专利证书已下发'
        }
        
        response = self.client.post(f'/staff/patent/{project.id}/certificate', 
                                  data=certificate_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证证书状态
        updated_project = PatentProject.query.get(project.id)
        self.assertEqual(updated_project.patent_status, '已发证')
        self.assertEqual(updated_project.status, '已完成')
        self.assertIsNotNone(updated_project.certificate_time)
        
        print("✓ 专利证书下发功能正常")
        
    def test_patent_types(self):
        """测试不同专利类型"""
        print("\n测试不同专利类型...")
        
        patent_types = [
            {
                'type': '发明专利',
                'description': '技术方案的保护',
                'price': 15000.00,
                'duration': '20年'
            },
            {
                'type': '实用新型专利',
                'description': '产品形状、构造的保护',
                'price': 8000.00,
                'duration': '10年'
            },
            {
                'type': '外观设计专利',
                'description': '产品外观的保护',
                'price': 6000.00,
                'duration': '15年'
            },
            {
                'type': 'PCT国际专利',
                'description': '国际专利申请',
                'price': 25000.00,
                'duration': '20年'
            }
        ]
        
        for patent_type in patent_types:
            project = PatentProject(
                project_name=f'{patent_type["type"]}测试项目',
                project_type=patent_type['type'],
                applicant_type='企业申请',
                patent_title=f'{patent_type["type"]}研究',
                technical_field='医疗器械',
                invention_description=f'{patent_type["type"]}技术方案',
                patent_status='准备材料',
                price=patent_type['price'],
                status='待确认',
                applicant_id=self.test_user.id
            )
            db.session.add(project)
            
        db.session.commit()
        
        # 验证不同专利类型项目已创建
        for patent_type in patent_types:
            project = PatentProject.query.filter_by(project_name=f'{patent_type["type"]}测试项目').first()
            self.assertIsNotNone(project)
            self.assertEqual(project.project_type, patent_type['type'])
            self.assertEqual(float(project.price), patent_type['price'])
        
        print("✓ 不同专利类型功能正常")
        
    def test_patent_applicant_types(self):
        """测试不同申请人类型"""
        print("\n测试不同申请人类型...")
        
        applicant_types = [
            {
                'type': '个人发明者',
                'description': '独立发明人'
            },
            {
                'type': '企业申请',
                'description': '公司法人申请'
            },
            {
                'type': '科研院所',
                'description': '高校、研究所'
            },
            {
                'type': '联合申请',
                'description': '多机构合作'
            }
        ]
        
        for app_type in applicant_types:
            project = PatentProject(
                project_name=f'{app_type["type"]}测试项目',
                project_type='发明专利',
                applicant_type=app_type['type'],
                patent_title=f'{app_type["type"]}专利研究',
                technical_field='医疗器械',
                invention_description=f'{app_type["type"]}技术方案',
                patent_status='准备材料',
                price=10000.00,
                status='待确认',
                applicant_id=self.test_user.id
            )
            db.session.add(project)
            
        db.session.commit()
        
        # 验证不同申请人类型项目已创建
        for app_type in applicant_types:
            project = PatentProject.query.filter_by(project_name=f'{app_type["type"]}测试项目').first()
            self.assertIsNotNone(project)
            self.assertEqual(project.applicant_type, app_type['type'])
        
        print("✓ 不同申请人类型功能正常")
        
    def test_patent_management_services(self):
        """测试专利管理服务"""
        print("\n测试专利管理服务...")
        
        # 创建已发证的专利项目
        project = PatentProject(
            project_name='专利管理测试项目',
            project_type='发明专利',
            applicant_type='企业申请',
            patent_title='医疗AI诊断系统',
            technical_field='人工智能',
            invention_description='一种医疗AI诊断系统',
            patent_status='已发证',
            application_number='202410123461.2',
            acceptance_number='202410123461.2',
            patent_number='ZL202410123461.2',
            price=15000.00,
            status='已完成',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            submit_time=datetime.utcnow(),
            acceptance_time=datetime.utcnow(),
            examination_time=datetime.utcnow(),
            authorization_time=datetime.utcnow(),
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
        
        # 专利年费管理
        annual_fee_data = {
            'annual_fee_paid': True,
            'annual_fee_amount': 3000.00,
            'annual_fee_date': datetime.utcnow(),
            'remarks': '专利年费已缴纳'
        }
        
        response = self.client.post(f'/staff/patent/{project.id}/annual_fee', 
                                  data=annual_fee_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证年费管理
        updated_project = PatentProject.query.get(project.id)
        self.assertTrue(updated_project.annual_fee_paid)
        self.assertEqual(float(updated_project.annual_fee_amount), 3000.00)
        
        print("✓ 专利管理服务功能正常")
        
    def test_patent_transformation(self):
        """测试专利转化"""
        print("\n测试专利转化...")
        
        # 创建已发证的专利项目
        project = PatentProject(
            project_name='专利转化测试项目',
            project_type='发明专利',
            applicant_type='企业申请',
            patent_title='智能医疗监护设备',
            technical_field='医疗监护',
            invention_description='一种智能医疗监护设备',
            patent_status='已发证',
            application_number='202410123462.3',
            acceptance_number='202410123462.3',
            patent_number='ZL202410123462.3',
            price=12000.00,
            status='已完成',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            submit_time=datetime.utcnow(),
            acceptance_time=datetime.utcnow(),
            examination_time=datetime.utcnow(),
            authorization_time=datetime.utcnow(),
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
        
        # 专利转化
        transformation_data = {
            'is_transformed': True,
            'transformation_type': '技术转让',
            'transformation_value': 500000.00,
            'transformation_time': datetime.utcnow(),
            'remarks': '专利已成功转化'
        }
        
        response = self.client.post(f'/staff/patent/{project.id}/transform', 
                                  data=transformation_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证转化状态
        updated_project = PatentProject.query.get(project.id)
        self.assertTrue(updated_project.is_transformed)
        self.assertEqual(updated_project.transformation_type, '技术转让')
        self.assertEqual(float(updated_project.transformation_value), 500000.00)
        
        print("✓ 专利转化功能正常")
        
    def test_patent_project_settlement(self):
        """测试专利项目结清"""
        print("\n测试专利项目结清...")
        
        # 创建已完成的专利项目
        project = PatentProject(
            project_name='专利结清测试项目',
            project_type='发明专利',
            applicant_type='企业申请',
            patent_title='医疗机器人控制系统',
            technical_field='机器人技术',
            invention_description='一种医疗机器人控制系统',
            patent_status='已发证',
            application_number='202410123463.4',
            acceptance_number='202410123463.4',
            patent_number='ZL202410123463.4',
            price=18000.00,
            status='已完成',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            submit_time=datetime.utcnow(),
            acceptance_time=datetime.utcnow(),
            examination_time=datetime.utcnow(),
            authorization_time=datetime.utcnow(),
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
        
        # 项目结清
        settlement_data = {
            'settle_time': datetime.utcnow(),
            'remarks': '专利项目款项已结清'
        }
        
        response = self.client.post(f'/staff/patent/{project.id}/settle', 
                                  data=settlement_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证结清状态
        updated_project = PatentProject.query.get(project.id)
        self.assertIsNotNone(updated_project.settle_time)
        
        print("✓ 专利项目结清功能正常")
        
    def test_complete_patent_workflow(self):
        """测试完整专利流程"""
        print("\n测试完整专利流程...")
        
        # 创建新专利项目
        project = PatentProject(
            project_name='完整专利流程测试项目',
            project_type='发明专利',
            applicant_type='企业申请',
            patent_title='智能医疗诊断系统',
            technical_field='人工智能',
            invention_description='一种基于AI的医疗诊断系统',
            patent_status='准备材料',
            price=20000.00,
            status='待确认',
            applicant_id=self.test_user.id
        )
        db.session.add(project)
        db.session.commit()
        
        # 1. 确认申请
        project.status = '已确认'
        project.confirmer_id = self.test_staff.id
        project.confirm_time = datetime.utcnow()
        
        # 2. 提交专利
        project.patent_status = '已提交'
        project.application_number = '202410123464.5'
        project.submit_time = datetime.utcnow()
        
        # 3. 专利受理
        project.patent_status = '受理中'
        project.acceptance_number = '202410123464.5'
        project.acceptance_time = datetime.utcnow()
        
        # 4. 专利审查
        project.patent_status = '审查中'
        project.examination_time = datetime.utcnow()
        
        # 5. 专利授权
        project.patent_status = '授权'
        project.patent_number = 'ZL202410123464.5'
        project.authorization_time = datetime.utcnow()
        
        # 6. 证书下发
        project.patent_status = '已发证'
        project.status = '已完成'
        project.certificate_time = datetime.utcnow()
        
        # 7. 项目结清
        project.settle_time = datetime.utcnow()
        
        db.session.commit()
        
        # 验证完整流程
        final_project = PatentProject.query.get(project.id)
        self.assertEqual(final_project.patent_status, '已发证')
        self.assertEqual(final_project.status, '已完成')
        self.assertEqual(final_project.patent_number, 'ZL202410123464.5')
        self.assertIsNotNone(final_project.settle_time)
        
        print("✓ 完整专利流程测试通过")

def run_patent_workflow_tests():
    """运行专利申请业务流程测试"""
    print("=" * 60)
    print("开始专利申请业务流程测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(PatentWorkflowTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("专利申请业务流程测试完成")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_patent_workflow_tests()
