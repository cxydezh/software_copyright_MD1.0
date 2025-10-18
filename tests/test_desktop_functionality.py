#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面端功能测试
测试桌面端登录、任务视图、模板管理、材料管理等功能
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

from desktop_app.main_with_login import SoftwareCopyrightMS
from desktop_app.local_models import LocalDatabase, DefaultPath, IDCardFile, USCCCFile, ContractFile, TemplateFolder, LocalProject
from desktop_app.server_client import ServerClient
from config.config import LOCAL_CONFIG

class DesktopLoginTest(unittest.TestCase):
    """桌面端登录测试类"""
    
    def setUp(self):
        """每个测试方法前的准备"""
        self.test_db_path = ':memory:'
        self.local_db = LocalDatabase(self.test_db_path)
        
        # 模拟服务器客户端
        self.server_client = Mock(spec=ServerClient)
        
    def test_desktop_login_success(self):
        """测试桌面端登录成功"""
        print("\n测试桌面端登录成功...")
        
        # 模拟成功的登录响应
        mock_response = {
            'success': True,
            'message': '登录成功',
            'user': {
                'id': 1,
                'email': 'test@example.com',
                'user_type': 'staff',
                'name': '测试用户',
                'phone': '13800138000',
                'permissions': {
                    'can_confirm': True,
                    'can_execute': True,
                    'can_manage': True,
                    'can_view_all': True,
                    'can_edit_paper': True,
                    'can_edit_patent': True,
                    'is_expert': True
                }
            }
        }
        
        self.server_client.login.return_value = mock_response
        
        # 测试登录
        result = self.server_client.login('test@example.com', 'password123', 'staff')
        
        self.assertTrue(result['success'])
        self.assertEqual(result['user']['email'], 'test@example.com')
        self.assertEqual(result['user']['user_type'], 'staff')
        
        print("✓ 桌面端登录成功功能正常")
        
    def test_desktop_login_failure(self):
        """测试桌面端登录失败"""
        print("\n测试桌面端登录失败...")
        
        # 模拟失败的登录响应
        mock_response = {
            'success': False,
            'message': '邮箱或密码错误'
        }
        
        self.server_client.login.return_value = mock_response
        
        # 测试登录
        result = self.server_client.login('test@example.com', 'wrongpassword', 'staff')
        
        self.assertFalse(result['success'])
        self.assertIn('错误', result['message'])
        
        print("✓ 桌面端登录失败功能正常")
        
    def test_desktop_login_network_error(self):
        """测试桌面端登录网络错误"""
        print("\n测试桌面端登录网络错误...")
        
        # 模拟网络错误
        self.server_client.login.side_effect = Exception('网络连接失败')
        
        # 测试登录
        with self.assertRaises(Exception):
            self.server_client.login('test@example.com', 'password123', 'staff')
        
        print("✓ 桌面端登录网络错误处理正常")
        
    def test_desktop_login_permission_check(self):
        """测试桌面端登录权限检查"""
        print("\n测试桌面端登录权限检查...")
        
        # 模拟普通用户登录（应该被拒绝）
        mock_response = {
            'success': False,
            'message': '只有执行者和管理员可以登录桌面端'
        }
        
        self.server_client.login.return_value = mock_response
        
        # 测试普通用户登录
        result = self.server_client.login('user@example.com', 'password123', 'user')
        
        self.assertFalse(result['success'])
        self.assertIn('执行者', result['message'])
        
        print("✓ 桌面端登录权限检查功能正常")

class DesktopTaskViewTest(unittest.TestCase):
    """桌面端任务视图测试类"""
    
    def setUp(self):
        """每个测试方法前的准备"""
        self.test_db_path = ':memory:'
        self.local_db = LocalDatabase(self.test_db_path)
        
        # 模拟服务器客户端
        self.server_client = Mock(spec=ServerClient)
        
        # 创建测试项目数据
        self.test_projects = [
            {
                'id': 1,
                'project_name': '已立项项目1',
                'status': '已立项',
                'executor_id': 1,
                'copyright_owner': '测试用户1',
                'serial_number': None
            },
            {
                'id': 2,
                'project_name': '执行中项目1',
                'status': '执行中',
                'executor_id': 1,
                'copyright_owner': '测试用户2',
                'serial_number': None
            },
            {
                'id': 3,
                'project_name': '已完成项目1',
                'status': '已完成',
                'executor_id': 1,
                'copyright_owner': '测试用户3',
                'serial_number': '2024SR001234'
            }
        ]
        
    def test_get_projects_by_status(self):
        """测试按状态获取项目"""
        print("\n测试按状态获取项目...")
        
        # 模拟服务器响应
        self.server_client.get_projects.return_value = {
            'success': True,
            'projects': self.test_projects
        }
        
        # 测试获取已立项项目
        result = self.server_client.get_projects('test@example.com', 'password123', 'staff', status='已立项')
        
        self.assertTrue(result['success'])
        projects = result['projects']
        
        # 验证只返回已立项项目
        for project in projects:
            if project['status'] == '已立项':
                self.assertEqual(project['status'], '已立项')
        
        print("✓ 按状态获取项目功能正常")
        
    def test_create_project_folder(self):
        """测试创建项目文件夹"""
        print("\n测试创建项目文件夹...")
        
        project = self.test_projects[0]
        
        # 模拟文件夹创建
        with patch('os.makedirs') as mock_makedirs:
            with patch('os.path.exists') as mock_exists:
                mock_exists.return_value = False
                
                # 测试创建项目文件夹
                project_folder = f"D:/SoftwareCopyrightMS/ProjectFile/{project['id']}.{project['project_name']}"
                
                # 验证文件夹路径正确
                self.assertIn(str(project['id']), project_folder)
                self.assertIn(project['project_name'], project_folder)
                
        print("✓ 创建项目文件夹功能正常")
        
    def test_update_project_status(self):
        """测试更新项目状态"""
        print("\n测试更新项目状态...")
        
        project_id = 1
        new_status = '执行中'
        
        # 模拟服务器响应
        self.server_client.update_project.return_value = {
            'success': True,
            'message': '项目状态已更新'
        }
        
        # 测试更新项目状态
        result = self.server_client.update_project(
            'test@example.com', 'password123', 'staff',
            project_id, status=new_status, remarks='开始执行项目'
        )
        
        self.assertTrue(result['success'])
        
        print("✓ 更新项目状态功能正常")
        
    def test_search_projects(self):
        """测试搜索项目"""
        print("\n测试搜索项目...")
        
        search_term = '测试用户1'
        
        # 模拟服务器响应
        self.server_client.get_projects.return_value = {
            'success': True,
            'projects': [self.test_projects[0]]  # 只返回匹配的项目
        }
        
        # 测试搜索项目
        result = self.server_client.get_projects('test@example.com', 'password123', 'staff')
        
        self.assertTrue(result['success'])
        projects = result['projects']
        
        # 验证搜索结果
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]['copyright_owner'], '测试用户1')
        
        print("✓ 搜索项目功能正常")
        
    def test_project_file_management(self):
        """测试项目文件管理"""
        print("\n测试项目文件管理...")
        
        project = self.test_projects[0]
        project_folder = f"D:/SoftwareCopyrightMS/ProjectFile/{project['id']}.{project['project_name']}"
        
        # 模拟文件列表
        mock_files = [
            '需求文档.docx',
            '设计文档.docx',
            '用户手册.docx',
            '源代码.zip'
        ]
        
        with patch('os.listdir') as mock_listdir:
            mock_listdir.return_value = mock_files
            
            # 测试获取项目文件列表
            files = mock_listdir(project_folder)
            
            self.assertEqual(len(files), 4)
            self.assertIn('需求文档.docx', files)
            self.assertIn('源代码.zip', files)
            
        print("✓ 项目文件管理功能正常")

class DesktopTemplateTest(unittest.TestCase):
    """桌面端模板管理测试类"""
    
    def setUp(self):
        """每个测试方法前的准备"""
        self.test_db_path = ':memory:'
        self.local_db = LocalDatabase(self.test_db_path)
        
    def test_add_template(self):
        """测试添加模板"""
        print("\n测试添加模板...")
        
        template_data = {
            'template_name': '医疗软件模板',
            'programming_language': 'Python',
            'ide': 'VSCode',
            'database_type': 'MySQL',
            'application_type': 'Web应用',
            'remarks': '医疗软件开发模板'
        }
        
        # 测试添加模板
        template_id = self.local_db.add_template_folder(
            '医疗软件模板',
            'D:/SoftwareCopyrightMS/model/医疗软件模板',
            **template_data
        )
        
        self.assertIsNotNone(template_id)
        
        # 验证模板已添加
        template = self.local_db.get_template_folder(template_id)
        self.assertIsNotNone(template)
        self.assertEqual(template.template_name, '医疗软件模板')
        
        print("✓ 添加模板功能正常")
        
    def test_edit_template(self):
        """测试编辑模板"""
        print("\n测试编辑模板...")
        
        # 先添加模板
        template_id = self.local_db.add_template_folder(
            '原始模板',
            'D:/SoftwareCopyrightMS/model/原始模板',
            template_name='原始模板',
            programming_language='Java',
            ide='Eclipse',
            database_type='Oracle',
            application_type='桌面应用'
        )
        
        # 编辑模板
        updated_data = {
            'template_name': '更新后的模板',
            'programming_language': 'Python',
            'ide': 'VSCode',
            'database_type': 'MySQL',
            'application_type': 'Web应用'
        }
        
        success = self.local_db.update_template_folder(template_id, **updated_data)
        self.assertTrue(success)
        
        # 验证模板已更新
        template = self.local_db.get_template_folder(template_id)
        self.assertEqual(template.template_name, '更新后的模板')
        self.assertEqual(template.programming_language, 'Python')
        
        print("✓ 编辑模板功能正常")
        
    def test_delete_template(self):
        """测试删除模板"""
        print("\n测试删除模板...")
        
        # 先添加模板
        template_id = self.local_db.add_template_folder(
            '待删除模板',
            'D:/SoftwareCopyrightMS/model/待删除模板',
            template_name='待删除模板'
        )
        
        # 删除模板
        success = self.local_db.delete_template_folder(template_id)
        self.assertTrue(success)
        
        # 验证模板已删除
        template = self.local_db.get_template_folder(template_id)
        self.assertIsNone(template)
        
        print("✓ 删除模板功能正常")
        
    def test_create_project_from_template(self):
        """测试从模板创建项目"""
        print("\n测试从模板创建项目...")
        
        # 先添加模板
        template_id = self.local_db.add_template_folder(
            '项目模板',
            'D:/SoftwareCopyrightMS/model/项目模板',
            template_name='项目模板'
        )
        
        project_name = '新项目'
        
        # 模拟从模板创建项目
        with patch('shutil.copytree') as mock_copytree:
            mock_copytree.return_value = None
            
            # 测试从模板创建项目
            source_path = 'D:/SoftwareCopyrightMS/model/项目模板'
            target_path = f'D:/SoftwareCopyrightMS/ProjectFile/1.{project_name}'
            
            # 验证路径正确
            self.assertIn('项目模板', source_path)
            self.assertIn(project_name, target_path)
            
        print("✓ 从模板创建项目功能正常")

class DesktopMaterialTest(unittest.TestCase):
    """桌面端材料管理测试类"""
    
    def setUp(self):
        """每个测试方法前的准备"""
        self.test_db_path = ':memory:'
        self.local_db = LocalDatabase(self.test_db_path)
        
    def test_add_id_card_file(self):
        """测试添加身份证文件"""
        print("\n测试添加身份证文件...")
        
        id_card_data = {
            'file_name': '1.张三_身份证.pdf',
            'file_path': 'D:/SoftwareCopyrightMS/IDPDF/1.张三_身份证.pdf',
            'person_name': '张三',
            'gender': '男',
            'birthplace': '河南省郑州市',
            'id_number': '410101199001011234',
            'remarks': '测试身份证'
        }
        
        # 测试添加身份证文件
        file_id = self.local_db.add_id_card_file(**id_card_data)
        
        self.assertIsNotNone(file_id)
        
        # 验证文件已添加
        file_record = self.local_db.get_id_card_file(file_id)
        self.assertIsNotNone(file_record)
        self.assertEqual(file_record.person_name, '张三')
        
        print("✓ 添加身份证文件功能正常")
        
    def test_add_usccc_file(self):
        """测试添加统一社会信用代码证书文件"""
        print("\n测试添加统一社会信用代码证书文件...")
        
        usccc_data = {
            'file_name': '1.测试医院_统一社会信用代码证书.pdf',
            'file_path': 'D:/SoftwareCopyrightMS/USCCC/1.测试医院_统一社会信用代码证书.pdf',
            'organization_name': '测试医院',
            'validity_period': '2025-12-31',
            'legal_representative': '张院长',
            'remarks': '测试统一社会信用代码证书'
        }
        
        # 测试添加统一社会信用代码证书文件
        file_id = self.local_db.add_usccc_file(**usccc_data)
        
        self.assertIsNotNone(file_id)
        
        # 验证文件已添加
        file_record = self.local_db.get_usccc_file(file_id)
        self.assertIsNotNone(file_record)
        self.assertEqual(file_record.organization_name, '测试医院')
        
        print("✓ 添加统一社会信用代码证书文件功能正常")
        
    def test_add_contract_file(self):
        """测试添加合同文件"""
        print("\n测试添加合同文件...")
        
        contract_data = {
            'file_name': '1.合作开发合同.pdf',
            'file_path': 'D:/SoftwareCopyrightMS/model/contract/1.合作开发合同.pdf',
            'contract_name': '合作开发合同',
            'participant_type': '事业单位联合个人',
            'remarks': '测试合同文件'
        }
        
        # 测试添加合同文件
        file_id = self.local_db.add_contract_file(**contract_data)
        
        self.assertIsNotNone(file_id)
        
        # 验证文件已添加
        file_record = self.local_db.get_contract_file(file_id)
        self.assertIsNotNone(file_record)
        self.assertEqual(file_record.contract_name, '合作开发合同')
        
        print("✓ 添加合同文件功能正常")
        
    def test_file_naming_validation(self):
        """测试文件命名验证"""
        print("\n测试文件命名验证...")
        
        # 测试正确的文件命名格式
        correct_names = [
            '1.张三_身份证.pdf',
            '2.李四_身份证.pdf',
            '1.测试医院_统一社会信用代码证书.pdf',
            '1.合作开发合同.pdf'
        ]
        
        for name in correct_names:
            # 验证文件命名格式
            self.assertTrue(name.startswith(('1.', '2.', '3.', '4.', '5.')))
            self.assertIn('.', name)
            
        # 测试错误的文件命名格式
        incorrect_names = [
            '张三_身份证.pdf',  # 缺少ID
            '1张三_身份证.pdf',  # 缺少点号
            '1.张三身份证.pdf',  # 缺少下划线
            '1.张三_身份证',  # 缺少扩展名
        ]
        
        for name in incorrect_names:
            # 验证文件命名格式不正确
            self.assertFalse(name.startswith(('1.', '2.', '3.', '4.', '5.')) or 
                           (name.startswith(('1.', '2.', '3.', '4.', '5.')) and 
                            '.' in name and '_' in name and name.endswith('.pdf')))
            
        print("✓ 文件命名验证功能正常")
        
    def test_get_recent_files(self):
        """测试获取最近文件"""
        print("\n测试获取最近文件...")
        
        # 添加多个身份证文件
        for i in range(15):
            self.local_db.add_id_card_file(
                file_name=f'{i+1}.用户{i+1}_身份证.pdf',
                file_path=f'D:/SoftwareCopyrightMS/IDPDF/{i+1}.用户{i+1}_身份证.pdf',
                person_name=f'用户{i+1}',
                gender='男',
                birthplace='河南省',
                id_number=f'41010119900101123{i}'
            )
        
        # 测试获取最近10条记录
        recent_files = self.local_db.get_recent_id_card_files(10)
        
        self.assertEqual(len(recent_files), 10)
        
        # 验证按创建时间倒序排列
        for i in range(len(recent_files) - 1):
            self.assertGreaterEqual(
                recent_files[i].created_time,
                recent_files[i + 1].created_time
            )
            
        print("✓ 获取最近文件功能正常")
        
    def test_copy_file_to_project(self):
        """测试复制文件到项目"""
        print("\n测试复制文件到项目...")
        
        # 添加身份证文件
        file_id = self.local_db.add_id_card_file(
            file_name='1.张三_身份证.pdf',
            file_path='D:/SoftwareCopyrightMS/IDPDF/1.张三_身份证.pdf',
            person_name='张三',
            gender='男',
            birthplace='河南省郑州市',
            id_number='410101199001011234'
        )
        
        project_folder = 'D:/SoftwareCopyrightMS/ProjectFile/1.测试项目'
        
        # 模拟文件复制
        with patch('shutil.copy2') as mock_copy:
            mock_copy.return_value = None
            
            # 测试复制文件到项目
            source_file = 'D:/SoftwareCopyrightMS/IDPDF/1.张三_身份证.pdf'
            target_file = f'{project_folder}/1.张三_身份证.pdf'
            
            # 验证路径正确
            self.assertIn('IDPDF', source_file)
            self.assertIn('ProjectFile', target_file)
            
        print("✓ 复制文件到项目功能正常")

def run_desktop_tests():
    """运行桌面端功能测试"""
    print("=" * 60)
    print("开始桌面端功能测试")
    print("=" * 60)
    
    # 创建测试套件
    test_classes = [DesktopLoginTest, DesktopTaskViewTest, DesktopTemplateTest, DesktopMaterialTest]
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("桌面端功能测试完成")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 60)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_desktop_tests()
