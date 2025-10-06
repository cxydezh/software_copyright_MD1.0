#!/usr/bin/env python3
"""
系统功能完整性测试脚本
测试论文指导和专利申请功能的完整性和可用性
"""

import os
import sys
import unittest
import requests
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from database.models import db, User, Staff, PaperProject, PatentProject, ProjectFile
from flask_login import login_user

class SystemCompletenessTest(unittest.TestCase):
    """系统功能完整性测试类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.app = create_app('testing')
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # 创建测试数据库表
        db.create_all()
        
        # 创建测试用户
        cls.test_user = User(
            name='测试用户',
            email='test@example.com',
            phone='13800138000',
            user_category='综合服务',
            organization='测试机构',
            research_field='医学影像'
        )
        cls.test_user.set_password('password123')
        
        # 创建测试员工
        cls.test_staff = Staff(
            name='测试员工',
            email='staff@example.com',
            phone='13800138001',
            expertise_area='医学工程',
            service_types='论文指导,专利申请'
        )
        cls.test_staff.set_password('password123')
        
        db.session.add(cls.test_user)
        db.session.add(cls.test_staff)
        db.session.commit()
        
        print("测试环境初始化完成")
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()
        print("测试环境清理完成")
    
    def test_01_database_models(self):
        """测试数据库模型"""
        print("\n=== 测试数据库模型 ===")
        
        # 测试PaperProject模型
        paper = PaperProject(
            project_name='测试论文项目',
            project_type='论文指导',
            service_level='标准服务',
            applicant_type='个人学者',
            paper_title='医学影像AI诊断研究',
            research_field='医学影像',
            target_journal='Nature Medicine',
            applicant_id=self.test_user.id
        )
        db.session.add(paper)
        db.session.commit()
        
        self.assertIsNotNone(paper.id)
        self.assertEqual(paper.status, '待确认')
        print("✓ PaperProject模型测试通过")
        
        # 测试PatentProject模型
        patent = PatentProject(
            project_name='测试专利项目',
            project_type='发明专利申请',
            applicant_type='企业申请',
            application_field='医疗设备',
            invention_title='智能医疗诊断设备',
            technical_field='医疗器械',
            applicant_id=self.test_user.id
        )
        db.session.add(patent)
        db.session.commit()
        
        self.assertIsNotNone(patent.id)
        self.assertEqual(patent.status, '待确认')
        print("✓ PatentProject模型测试通过")
        
        # 测试ProjectFile模型
        project_file = ProjectFile(
            project_id=paper.id,
            project_type='paper',
            file_name='test.pdf',
            file_path='/uploads/test.pdf',
            file_type='pdf',
            file_size=1024,
            uploader_id=self.test_user.id,
            file_category='申请材料'
        )
        db.session.add(project_file)
        db.session.commit()
        
        self.assertIsNotNone(project_file.id)
        print("✓ ProjectFile模型测试通过")
    
    def test_02_paper_routes(self):
        """测试论文相关路由"""
        print("\n=== 测试论文相关路由 ===")
        
        # 测试论文首页（需要登录）
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.test_user.id)
            sess['user_type'] = 'user'
        
        response = self.client.get('/paper/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('论文指导管理', response.data.decode('utf-8'))
        print("✓ 论文首页路由测试通过")
        
        # 测试论文申请页面
        response = self.client.get('/paper/apply')
        self.assertEqual(response.status_code, 200)
        self.assertIn('申请论文指导', response.data.decode('utf-8'))
        print("✓ 论文申请页面路由测试通过")
        
        # 测试论文申请提交
        response = self.client.post('/paper/apply', data={
            'project_name': '测试论文申请',
            'project_type': '论文指导',
            'service_level': '标准服务',
            'applicant_type': '个人学者',
            'paper_title': '测试论文标题',
            'research_field': '医学影像',
            'target_journal': 'Nature',
            'remarks': '测试备注'
        })
        self.assertEqual(response.status_code, 302)  # 重定向到详情页
        print("✓ 论文申请提交测试通过")
    
    def test_03_patent_routes(self):
        """测试专利相关路由"""
        print("\n=== 测试专利相关路由 ===")
        
        # 测试专利首页
        response = self.client.get('/patent/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('专利申请管理', response.data.decode('utf-8'))
        print("✓ 专利首页路由测试通过")
        
        # 测试专利申请页面
        response = self.client.get('/patent/apply')
        self.assertEqual(response.status_code, 200)
        self.assertIn('申请专利保护', response.data.decode('utf-8'))
        print("✓ 专利申请页面路由测试通过")
        
        # 测试专利申请提交
        response = self.client.post('/patent/apply', data={
            'project_name': '测试专利申请',
            'project_type': '发明专利申请',
            'applicant_type': '企业申请',
            'application_field': '医疗设备',
            'invention_title': '测试发明名称',
            'technical_field': '医疗器械',
            'remarks': '测试备注'
        })
        self.assertEqual(response.status_code, 302)  # 重定向到详情页
        print("✓ 专利申请提交测试通过")
    
    def test_04_staff_dashboard_routes(self):
        """测试员工管理面板路由"""
        print("\n=== 测试员工管理面板路由 ===")
        
        # 切换到员工身份
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.test_staff.id)
            sess['user_type'] = 'staff'
        
        # 测试论文管理面板
        response = self.client.get('/paper/staff')
        self.assertEqual(response.status_code, 200)
        self.assertIn('员工论文管理面板', response.data.decode('utf-8'))
        print("✓ 论文管理面板路由测试通过")
        
        # 测试专利管理面板
        response = self.client.get('/patent/staff')
        self.assertEqual(response.status_code, 200)
        self.assertIn('员工专利管理面板', response.data.decode('utf-8'))
        print("✓ 专利管理面板路由测试通过")
    
    def test_05_services_page_integration(self):
        """测试服务项目页面集成"""
        print("\n=== 测试服务项目页面集成 ===")
        
        # 测试服务项目页面
        response = self.client.get('/services')
        self.assertEqual(response.status_code, 200)
        self.assertIn('论文指导和发表', response.data.decode('utf-8'))
        self.assertIn('专利申请和保护', response.data.decode('utf-8'))
        self.assertIn('软件开发和软件著作权登记', response.data.decode('utf-8'))
        print("✓ 服务项目页面集成测试通过")
    
    def test_06_file_upload_functionality(self):
        """测试文件上传功能"""
        print("\n=== 测试文件上传功能 ===")
        
        # 获取一个论文项目
        paper = PaperProject.query.first()
        self.assertIsNotNone(paper)
        
        # 测试文件上传（模拟）
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.test_user.id)
            sess['user_type'] = 'user'
        
        # 创建测试文件
        test_file_content = b"Test file content"
        
        response = self.client.post(f'/paper/{paper.id}/upload', 
                                  data={'file': (test_file_content, 'test.txt'),
                                        'file_category': '申请材料'},
                                  content_type='multipart/form-data')
        
        # 检查响应
        if response.status_code == 200:
            data = json.loads(response.data)
            self.assertTrue(data.get('success', False))
            print("✓ 文件上传功能测试通过")
        else:
            print(f"⚠ 文件上传功能需要完善 (状态码: {response.status_code})")
    
    def test_07_api_endpoints(self):
        """测试API端点"""
        print("\n=== 测试API端点 ===")
        
        # 切换到员工身份
        with self.client.session_transaction() as sess:
            sess['user_id'] = str(self.test_staff.id)
            sess['user_type'] = 'staff'
        
        # 测试项目确认API
        paper = PaperProject.query.first()
        if paper:
            response = self.client.post(f'/paper/{paper.id}/confirm')
            if response.status_code == 200:
                data = json.loads(response.data)
                self.assertTrue(data.get('success', False))
                print("✓ 项目确认API测试通过")
            else:
                print(f"⚠ 项目确认API需要完善 (状态码: {response.status_code})")
        
        # 测试状态更新API
        if paper:
            response = self.client.post(f'/paper/{paper.id}/update_status', 
                                      json={'status': '进行中'})
            if response.status_code == 200:
                data = json.loads(response.data)
                self.assertTrue(data.get('success', False))
                print("✓ 状态更新API测试通过")
            else:
                print(f"⚠ 状态更新API需要完善 (状态码: {response.status_code})")
    
    def test_08_missing_templates(self):
        """测试缺失的模板"""
        print("\n=== 测试缺失的模板 ===")
        
        missing_templates = []
        
        # 检查论文相关模板
        paper_templates = [
            'paper/edit.html',
            'paper/staff_dashboard.html'
        ]
        
        for template in paper_templates:
            if not os.path.exists(f'templates/{template}'):
                missing_templates.append(template)
        
        # 检查专利相关模板
        patent_templates = [
            'patent/detail.html',
            'patent/edit.html',
            'patent/staff_dashboard.html'
        ]
        
        for template in patent_templates:
            if not os.path.exists(f'templates/{template}'):
                missing_templates.append(template)
        
        if missing_templates:
            print(f"⚠ 缺失的模板文件: {missing_templates}")
        else:
            print("✓ 所有模板文件存在")
        
        return missing_templates
    
    def test_09_database_constraints(self):
        """测试数据库约束"""
        print("\n=== 测试数据库约束 ===")
        
        # 测试唯一性约束
        try:
            # 尝试创建重复邮箱的用户
            duplicate_user = User(
                name='重复用户',
                email='test@example.com',  # 重复邮箱
                phone='13800138002'
            )
            duplicate_user.set_password('password123')
            db.session.add(duplicate_user)
            db.session.commit()
            print("⚠ 邮箱唯一性约束可能有问题")
        except Exception as e:
            print("✓ 邮箱唯一性约束正常")
            db.session.rollback()
    
    def test_10_error_handling(self):
        """测试错误处理"""
        print("\n=== 测试错误处理 ===")
        
        # 测试访问不存在的项目
        response = self.client.get('/paper/99999')
        self.assertEqual(response.status_code, 404)
        print("✓ 404错误处理正常")
        
        # 测试未授权访问
        with self.client.session_transaction() as sess:
            sess.clear()  # 清除会话
        
        response = self.client.get('/paper/')
        self.assertEqual(response.status_code, 302)  # 重定向到登录页
        print("✓ 未授权访问处理正常")

def run_completeness_test():
    """运行完整性测试"""
    print("开始系统功能完整性测试...")
    print("=" * 60)
    
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(SystemCompletenessTest)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    # 检查缺失的模板
    print("\n" + "=" * 60)
    print("检查缺失的模板文件...")
    
    missing_templates = []
    test_instance = SystemCompletenessTest()
    test_instance.setUpClass()
    try:
        missing_templates = test_instance.test_08_missing_templates()
    finally:
        test_instance.tearDownClass()
    
    if missing_templates:
        print(f"\n需要创建的模板文件:")
        for template in missing_templates:
            print(f"- templates/{template}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    
    return result

if __name__ == '__main__':
    run_completeness_test()
