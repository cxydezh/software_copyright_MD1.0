#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文指导业务流程测试
测试论文指导、论文发表、学术咨询的完整流程
"""

import os
import sys
import unittest
import json
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, User, Staff, PaperProject, Permission, ProcessLog
from flask_login import login_user

class PaperWorkflowTest(unittest.TestCase):
    """论文指导业务流程测试类"""
    
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
            name='论文测试用户',
            email='paperuser@example.com',
            phone='13800138000',
            user_category='论文指导',
            organization='测试医院',
            research_field='医学影像'
        )
        test_user.set_password('password123')
        
        # 创建测试员工
        test_staff = Staff(
            name='论文测试业务员',
            email='paperstaff@example.com',
            phone='13800138001',
            position_id=1  # 普通业务员
        )
        test_staff.set_password('staff123')
        
        # 创建测试执行者
        test_executor = Staff(
            name='论文测试执行者',
            email='paperexecutor@example.com',
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
        self.test_paper_project_data = {
            'project_name': '基于深度学习的医学影像诊断研究',
            'project_type': '论文指导',
            'service_level': '标准服务',
            'applicant_type': '个人学者',
            'paper_title': '基于深度学习的医学影像诊断研究',
            'research_field': '医学影像',
            'target_journal': 'Medical Image Analysis',
            'price': 3000.00,
            'remarks': '需要专业的医学影像分析指导'
        }
        
    def test_user_submit_paper_application(self):
        """测试用户提交论文申请"""
        print("\n测试用户提交论文申请...")
        
        # 用户登录
        login_data = {
            'email': self.test_user.email,
            'password': 'password123'
        }
        
        response = self.client.post('/auth/login', data=login_data)
        self.assertEqual(response.status_code, 200)
        
        # 提交论文申请
        response = self.client.post('/paper/apply', 
                                  data=self.test_paper_project_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证论文项目已创建
        project = PaperProject.query.filter_by(project_name=self.test_paper_project_data['project_name']).first()
        self.assertIsNotNone(project)
        self.assertEqual(project.status, '待确认')
        self.assertEqual(project.applicant_id, self.test_user.id)
        self.assertEqual(project.paper_status, '初稿')
        
        print("✓ 用户提交论文申请功能正常")
        
    def test_paper_guidance_workflow(self):
        """测试论文指导流程"""
        print("\n测试论文指导流程...")
        
        # 创建论文指导项目
        project = PaperProject(
            project_name='论文指导测试项目',
            project_type='论文指导',
            service_level='标准服务',
            applicant_type='个人学者',
            paper_title='医疗AI诊断系统研究',
            research_field='人工智能',
            target_journal='Journal of Medical AI',
            paper_status='初稿',
            price=3000.00,
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
            'remarks': '论文指导申请已确认'
        }
        
        response = self.client.post(f'/staff/paper/{project.id}/confirm', 
                                  data=confirm_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_project = PaperProject.query.get(project.id)
        self.assertEqual(updated_project.status, '已确认')
        self.assertEqual(updated_project.executor_id, self.test_executor.id)
        
        print("✓ 论文指导申请确认功能正常")
        
    def test_paper_status_progression(self):
        """测试论文状态进展"""
        print("\n测试论文状态进展...")
        
        # 创建已确认的论文项目
        project = PaperProject(
            project_name='论文状态测试项目',
            project_type='论文指导',
            service_level='高级服务',
            applicant_type='医疗机构',
            paper_title='智能医疗设备研究',
            research_field='医疗器械',
            target_journal='IEEE Transactions on Biomedical Engineering',
            paper_status='初稿',
            price=5000.00,
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
        
        # 测试论文状态进展：初稿 → 修改中
        status_data = {
            'paper_status': '修改中',
            'status': '执行中',
            'remarks': '开始修改论文初稿'
        }
        
        response = self.client.post(f'/staff/paper/{project.id}/update_status', 
                                  data=status_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证状态已更新
        updated_project = PaperProject.query.get(project.id)
        self.assertEqual(updated_project.paper_status, '修改中')
        self.assertEqual(updated_project.status, '执行中')
        
        # 继续状态进展：修改中 → 已投稿
        status_data = {
            'paper_status': '已投稿',
            'submit_time': datetime.utcnow(),
            'remarks': '论文已投稿到目标期刊'
        }
        
        response = self.client.post(f'/staff/paper/{project.id}/update_status', 
                                  data=status_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证投稿状态
        updated_project = PaperProject.query.get(project.id)
        self.assertEqual(updated_project.paper_status, '已投稿')
        self.assertIsNotNone(updated_project.submit_time)
        
        print("✓ 论文状态进展功能正常")
        
    def test_paper_review_process(self):
        """测试论文审稿流程"""
        print("\n测试论文审稿流程...")
        
        # 创建已投稿的论文项目
        project = PaperProject(
            project_name='论文审稿测试项目',
            project_type='论文发表',
            service_level='标准服务',
            applicant_type='企业研发',
            paper_title='医疗大数据分析研究',
            research_field='大数据',
            target_journal='Journal of Medical Informatics',
            paper_status='已投稿',
            price=4000.00,
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
        
        # 审稿中状态
        review_data = {
            'paper_status': '审稿中',
            'remarks': '论文进入审稿阶段'
        }
        
        response = self.client.post(f'/staff/paper/{project.id}/update_status', 
                                  data=review_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证审稿状态
        updated_project = PaperProject.query.get(project.id)
        self.assertEqual(updated_project.paper_status, '审稿中')
        
        print("✓ 论文审稿流程功能正常")
        
    def test_paper_acceptance(self):
        """测试论文录用"""
        print("\n测试论文录用...")
        
        # 创建审稿中的论文项目
        project = PaperProject(
            project_name='论文录用测试项目',
            project_type='论文发表',
            service_level='高级服务',
            applicant_type='联合申请',
            paper_title='智能诊断系统研究',
            research_field='人工智能',
            target_journal='Nature Medicine',
            paper_status='审稿中',
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
        
        # 论文录用
        acceptance_data = {
            'paper_status': '已录用',
            'accept_time': datetime.utcnow(),
            'remarks': '论文已被期刊录用'
        }
        
        response = self.client.post(f'/staff/paper/{project.id}/update_status', 
                                  data=acceptance_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证录用状态
        updated_project = PaperProject.query.get(project.id)
        self.assertEqual(updated_project.paper_status, '已录用')
        self.assertIsNotNone(updated_project.accept_time)
        
        print("✓ 论文录用功能正常")
        
    def test_paper_publication(self):
        """测试论文发表"""
        print("\n测试论文发表...")
        
        # 创建已录用的论文项目
        project = PaperProject(
            project_name='论文发表测试项目',
            project_type='论文发表',
            service_level='标准服务',
            applicant_type='个人学者',
            paper_title='医疗AI辅助诊断研究',
            research_field='人工智能',
            target_journal='The Lancet Digital Health',
            paper_status='已录用',
            price=4000.00,
            status='执行中',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            submit_time=datetime.utcnow(),
            accept_time=datetime.utcnow()
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
        
        # 论文发表
        publication_data = {
            'paper_status': '已发表',
            'publish_time': datetime.utcnow(),
            'status': '已完成',
            'remarks': '论文已正式发表'
        }
        
        response = self.client.post(f'/staff/paper/{project.id}/update_status', 
                                  data=publication_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证发表状态
        updated_project = PaperProject.query.get(project.id)
        self.assertEqual(updated_project.paper_status, '已发表')
        self.assertEqual(updated_project.status, '已完成')
        self.assertIsNotNone(updated_project.publish_time)
        
        print("✓ 论文发表功能正常")
        
    def test_paper_rejection(self):
        """测试论文被拒稿"""
        print("\n测试论文被拒稿...")
        
        # 创建审稿中的论文项目
        project = PaperProject(
            project_name='论文拒稿测试项目',
            project_type='论文发表',
            service_level='基础服务',
            applicant_type='个人学者',
            paper_title='医疗数据分析研究',
            research_field='数据分析',
            target_journal='Journal of Medical Research',
            paper_status='审稿中',
            price=2000.00,
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
        
        # 论文被拒稿
        rejection_data = {
            'paper_status': '被拒稿',
            'status': '已完成',
            'remarks': '论文被期刊拒稿，需要重新修改'
        }
        
        response = self.client.post(f'/staff/paper/{project.id}/update_status', 
                                  data=rejection_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证拒稿状态
        updated_project = PaperProject.query.get(project.id)
        self.assertEqual(updated_project.paper_status, '被拒稿')
        self.assertEqual(updated_project.status, '已完成')
        
        print("✓ 论文被拒稿功能正常")
        
    def test_academic_consultation(self):
        """测试学术咨询服务"""
        print("\n测试学术咨询服务...")
        
        # 创建学术咨询项目
        project = PaperProject(
            project_name='学术咨询测试项目',
            project_type='学术咨询',
            service_level='高级服务',
            applicant_type='医疗机构',
            paper_title='医疗AI研究方向规划',
            research_field='人工智能',
            target_journal='待定',
            paper_status='初稿',
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
        
        # 确认学术咨询
        confirm_data = {
            'status': '已确认',
            'executor_id': self.test_executor.id,
            'remarks': '学术咨询服务已确认'
        }
        
        response = self.client.post(f'/staff/paper/{project.id}/confirm', 
                                  data=confirm_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证咨询状态
        updated_project = PaperProject.query.get(project.id)
        self.assertEqual(updated_project.status, '已确认')
        self.assertEqual(updated_project.executor_id, self.test_executor.id)
        
        print("✓ 学术咨询服务功能正常")
        
    def test_paper_project_settlement(self):
        """测试论文项目结清"""
        print("\n测试论文项目结清...")
        
        # 创建已完成的论文项目
        project = PaperProject(
            project_name='论文结清测试项目',
            project_type='论文发表',
            service_level='标准服务',
            applicant_type='企业研发',
            paper_title='医疗AI系统研究',
            research_field='人工智能',
            target_journal='IEEE Journal of Biomedical Health Informatics',
            paper_status='已发表',
            price=4000.00,
            status='已完成',
            applicant_id=self.test_user.id,
            confirmer_id=self.test_staff.id,
            executor_id=self.test_executor.id,
            confirm_time=datetime.utcnow(),
            submit_time=datetime.utcnow(),
            accept_time=datetime.utcnow(),
            publish_time=datetime.utcnow()
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
            'remarks': '论文项目款项已结清'
        }
        
        response = self.client.post(f'/staff/paper/{project.id}/settle', 
                                  data=settlement_data,
                                  follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # 验证结清状态
        updated_project = PaperProject.query.get(project.id)
        self.assertIsNotNone(updated_project.settle_time)
        
        print("✓ 论文项目结清功能正常")
        
    def test_paper_service_levels(self):
        """测试不同服务等级"""
        print("\n测试不同服务等级...")
        
        service_levels = [
            {
                'level': '基础服务',
                'description': '论文格式规范、投稿指导',
                'price': 2000.00
            },
            {
                'level': '标准服务',
                'description': '内容修改、期刊推荐、全程跟踪',
                'price': 4000.00
            },
            {
                'level': '高级服务',
                'description': '深度指导、专家审稿、快速发表',
                'price': 6000.00
            }
        ]
        
        for service in service_levels:
            project = PaperProject(
                project_name=f'{service["level"]}测试项目',
                project_type='论文指导',
                service_level=service['level'],
                applicant_type='个人学者',
                paper_title=f'{service["level"]}论文研究',
                research_field='医疗AI',
                target_journal='Test Journal',
                paper_status='初稿',
                price=service['price'],
                status='待确认',
                applicant_id=self.test_user.id
            )
            db.session.add(project)
            
        db.session.commit()
        
        # 验证不同服务等级项目已创建
        for service in service_levels:
            project = PaperProject.query.filter_by(project_name=f'{service["level"]}测试项目').first()
            self.assertIsNotNone(project)
            self.assertEqual(project.service_level, service['level'])
            self.assertEqual(float(project.price), service['price'])
        
        print("✓ 不同服务等级功能正常")
        
    def test_paper_applicant_types(self):
        """测试不同申请人类型"""
        print("\n测试不同申请人类型...")
        
        applicant_types = [
            {
                'type': '个人学者',
                'description': '高校教师、研究人员、博士生'
            },
            {
                'type': '医疗机构',
                'description': '医院、医学研究所、医学院'
            },
            {
                'type': '企业研发',
                'description': '医疗设备公司、制药企业研发部门'
            },
            {
                'type': '联合申请',
                'description': '多机构合作项目'
            }
        ]
        
        for app_type in applicant_types:
            project = PaperProject(
                project_name=f'{app_type["type"]}测试项目',
                project_type='论文指导',
                service_level='标准服务',
                applicant_type=app_type['type'],
                paper_title=f'{app_type["type"]}论文研究',
                research_field='医疗AI',
                target_journal='Test Journal',
                paper_status='初稿',
                price=3000.00,
                status='待确认',
                applicant_id=self.test_user.id
            )
            db.session.add(project)
            
        db.session.commit()
        
        # 验证不同申请人类型项目已创建
        for app_type in applicant_types:
            project = PaperProject.query.filter_by(project_name=f'{app_type["type"]}测试项目').first()
            self.assertIsNotNone(project)
            self.assertEqual(project.applicant_type, app_type['type'])
        
        print("✓ 不同申请人类型功能正常")

def run_paper_workflow_tests():
    """运行论文指导业务流程测试"""
    print("=" * 60)
    print("开始论文指导业务流程测试")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(PaperWorkflowTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("论文指导业务流程测试完成")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_paper_workflow_tests()
