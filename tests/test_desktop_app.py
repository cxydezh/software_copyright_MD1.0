#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面应用单元测试
测试desktop_app的各个功能模块
"""

import unittest
import os
import sys
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from desktop_app.local_models import (
    LocalDatabase, DefaultPath, IDCardFile, USCCCFile, 
    ContractFile, TemplateFolder, ProjectFile, LocalProject
)
from desktop_app.task_view_new import TaskViewModule
from desktop_app.template_manage import TemplateManageModule
from desktop_app.material_manage import MaterialManageModule
from desktop_app.system_setting import SystemSettingModule


class TestLocalDatabase(unittest.TestCase):
    """测试本地数据库"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = LocalDatabase(self.db_path)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_database_creation(self):
        """测试数据库创建"""
        self.assertTrue(os.path.exists(self.db_path))
    
    def test_tables_creation(self):
        """测试表创建"""
        # 检查所有表是否创建成功
        tables = [
            'default_paths', 'id_card_files', 'usccc_files', 
            'contract_files', 'template_files', 'project_files', 'local_projects'
        ]
        
        for table in tables:
            result = self.db.execute_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            self.assertTrue(len(result) > 0, f"表 {table} 未创建")


class TestDefaultPath(unittest.TestCase):
    """测试默认路径管理"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = LocalDatabase(self.db_path)
        self.default_path = DefaultPath(self.db)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_set_and_get_path(self):
        """测试设置和获取路径"""
        test_path = "/test/path"
        self.default_path.set_path('test_path', test_path)
        result = self.default_path.get_path('test_path')
        self.assertEqual(result, test_path)
    
    def test_get_nonexistent_path(self):
        """测试获取不存在的路径"""
        result = self.default_path.get_path('nonexistent')
        self.assertIsNone(result)


class TestIDCardFile(unittest.TestCase):
    """测试身份证文件管理"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = LocalDatabase(self.db_path)
        self.id_card_file = IDCardFile(self.db)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_add_file(self):
        """测试添加文件"""
        file_id = self.id_card_file.add_file(
            'test_id.pdf', '/test/path/test_id.pdf', 
            '测试用户', '男', '河南省', '410123199001011234', '测试备注'
        )
        self.assertIsNotNone(file_id)
        
        # 验证文件是否添加成功
        files = self.id_card_file.get_all_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0][1], 'test_id.pdf')
    
    def test_get_file_by_id(self):
        """测试根据ID获取文件"""
        file_id = self.id_card_file.add_file(
            'test_id.pdf', '/test/path/test_id.pdf', 
            '测试用户', '男', '河南省', '410123199001011234', '测试备注'
        )
        result = self.id_card_file.get_file_by_id(file_id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result[1], 'test_id.pdf')
    
    def test_update_file(self):
        """测试更新文件"""
        file_data = {
            'file_name': 'test_id.pdf',
            'file_path': '/test/path/test_id.pdf',
            'person_name': '测试用户',
            'gender': '男',
            'birthplace': '河南省',
            'id_number': '410123199001011234',
            'remarks': '测试备注'
        }
        
        file_id = self.id_card_file.add_file(file_data)
        
        # 更新文件
        update_data = {'person_name': '更新用户', 'remarks': '更新备注'}
        self.id_card_file.update_file(file_id, update_data)
        
        # 验证更新
        result = self.id_card_file.get_file_by_id(file_id)
        self.assertEqual(result[2], '更新用户')
        self.assertEqual(result[6], '更新备注')
    
    def test_delete_file(self):
        """测试删除文件"""
        file_data = {
            'file_name': 'test_id.pdf',
            'file_path': '/test/path/test_id.pdf',
            'person_name': '测试用户',
            'gender': '男',
            'birthplace': '河南省',
            'id_number': '410123199001011234',
            'remarks': '测试备注'
        }
        
        file_id = self.id_card_file.add_file(file_data)
        self.id_card_file.delete_file(file_id)
        
        # 验证删除
        files = self.id_card_file.get_all_files()
        self.assertEqual(len(files), 0)


class TestUSCCCFile(unittest.TestCase):
    """测试统一社会信用代码证书文件管理"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = LocalDatabase(self.db_path)
        self.usccc_file = USCCCFile(self.db)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_add_file(self):
        """测试添加证书文件"""
        file_data = {
            'file_name': 'test_usccc.pdf',
            'file_path': '/test/path/test_usccc.pdf',
            'organization_name': '测试机构',
            'validity_period': '2024-12-31',
            'legal_representative': '张三',
            'remarks': '测试备注'
        }
        
        file_id = self.usccc_file.add_file(file_data)
        self.assertIsNotNone(file_id)
        
        # 验证文件是否添加成功
        files = self.usccc_file.get_all_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0][1], 'test_usccc.pdf')


class TestContractFile(unittest.TestCase):
    """测试合同文件管理"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = LocalDatabase(self.db_path)
        self.contract_file = ContractFile(self.db)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_add_file(self):
        """测试添加合同文件"""
        file_data = {
            'file_name': 'test_contract.pdf',
            'file_path': '/test/path/test_contract.pdf',
            'contract_name': '测试合同',
            'participant_type': '个人',
            'remarks': '测试备注'
        }
        
        file_id = self.contract_file.add_file(file_data)
        self.assertIsNotNone(file_id)
        
        # 验证文件是否添加成功
        files = self.contract_file.get_all_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0][1], 'test_contract.pdf')


class TestTemplateFolder(unittest.TestCase):
    """测试模板文件管理"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = LocalDatabase(self.db_path)
        self.template_file = TemplateFolder(self.db)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_add_file(self):
        """测试添加模板文件"""
        file_data = {
            'file_name': 'test_template.docx',
            'file_path': '/test/path/test_template.docx',
            'programming_language': 'Python',
            'ide_type': 'PyCharm',
            'database_type': 'MySQL',
            'remarks': '测试备注'
        }
        
        file_id = self.template_file.add_file(file_data)
        self.assertIsNotNone(file_id)
        
        # 验证文件是否添加成功
        files = self.template_file.get_all_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0][1], 'test_template.docx')


class TestLocalProject(unittest.TestCase):
    """测试本地项目管理"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = LocalDatabase(self.db_path)
        self.local_project = LocalProject(self.db)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_add_project(self):
        """测试添加项目"""
        project_data = {
            'project_name': '测试项目',
            'project_type': '软件登记业务',
            'applicant_type': '个人',
            'copyright_owner': '测试著作权人',
            'software_applicant_name': '测试申请人',
            'serial_number': None,
            'priority': '普通',
            'status': '已立项',
            'executor_id': 1,
            'remarks': '测试项目'
        }
        
        project_id = self.local_project.add_project(project_data)
        self.assertIsNotNone(project_id)
        
        # 验证项目是否添加成功
        projects = self.local_project.get_all_projects()
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0][1], '测试项目')
    
    def test_update_project_status(self):
        """测试更新项目状态"""
        project_data = {
            'project_name': '测试项目',
            'project_type': '软件登记业务',
            'applicant_type': '个人',
            'copyright_owner': '测试著作权人',
            'software_applicant_name': '测试申请人',
            'serial_number': None,
            'priority': '普通',
            'status': '已立项',
            'executor_id': 1,
            'remarks': '测试项目'
        }
        
        project_id = self.local_project.add_project(project_data)
        self.local_project.update_project_status(project_id, '执行中')
        
        # 验证状态更新
        project = self.local_project.get_project_by_id(project_id)
        self.assertEqual(project['status'], '执行中')


class TestTaskViewModule(unittest.TestCase):
    """测试任务视图模块"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = LocalDatabase(self.db_path)
        
        # 创建模拟的父组件
        self.mock_parent = Mock()
        self.mock_notebook = Mock()
        self.mock_parent.add = Mock()
        
        # 初始化各个管理模块
        self.default_path = DefaultPath(self.db)
        self.id_card_file = IDCardFile(self.db)
        self.usccc_file = USCCCFile(self.db)
        self.contract_file = ContractFile(self.db)
        self.template_file = TemplateFolder(self.db)
        self.project_file = ProjectFile(self.db)
        self.local_project = LocalProject(self.db)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    @patch('tkinter.Frame')
    @patch('tkinter.ttk.Notebook')
    @patch('tkinter.ttk.Treeview')
    def test_task_view_creation(self, mock_treeview, mock_notebook, mock_frame):
        """测试任务视图创建"""
        # 模拟tkinter组件
        mock_frame.return_value = Mock()
        mock_notebook.return_value = Mock()
        mock_treeview.return_value = Mock()
        
        # 创建任务视图模块
        task_view = TaskViewModule(
            self.mock_parent, self.db, self.local_project, self.project_file,
            self.id_card_file, self.usccc_file, self.contract_file
        )
        
        # 验证模块创建成功
        self.assertIsNotNone(task_view)
        self.assertEqual(task_view.db, self.db)
        self.assertEqual(task_view.local_project, self.local_project)


class TestTemplateManageModule(unittest.TestCase):
    """测试模板管理模块"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = LocalDatabase(self.db_path)
        
        # 创建模拟的父组件
        self.mock_parent = Mock()
        self.mock_notebook = Mock()
        self.mock_parent.add = Mock()
        
        # 初始化管理模块
        self.template_file = TemplateFolder(self.db)
        self.default_path = DefaultPath(self.db)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    @patch('tkinter.Frame')
    @patch('tkinter.ttk.Treeview')
    def test_template_manage_creation(self, mock_treeview, mock_frame):
        """测试模板管理模块创建"""
        # 模拟tkinter组件
        mock_frame.return_value = Mock()
        mock_treeview.return_value = Mock()
        
        # 创建模板管理模块
        template_manage = TemplateManageModule(
            self.mock_parent, self.db, self.template_file, self.default_path
        )
        
        # 验证模块创建成功
        self.assertIsNotNone(template_manage)
        self.assertEqual(template_manage.db, self.db)
        self.assertEqual(template_manage.template_folder, self.template_file)


class TestMaterialManageModule(unittest.TestCase):
    """测试材料管理模块"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = LocalDatabase(self.db_path)
        
        # 创建模拟的父组件
        self.mock_parent = Mock()
        self.mock_notebook = Mock()
        self.mock_parent.add = Mock()
        
        # 初始化管理模块
        self.id_card_file = IDCardFile(self.db)
        self.usccc_file = USCCCFile(self.db)
        self.contract_file = ContractFile(self.db)
        self.default_path = DefaultPath(self.db)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    @patch('tkinter.Frame')
    @patch('tkinter.ttk.Treeview')
    def test_material_manage_creation(self, mock_treeview, mock_frame):
        """测试材料管理模块创建"""
        # 模拟tkinter组件
        mock_frame.return_value = Mock()
        mock_treeview.return_value = Mock()
        
        # 创建材料管理模块
        material_manage = MaterialManageModule(
            self.mock_parent, self.db, self.id_card_file, self.usccc_file,
            self.contract_file, self.default_path
        )
        
        # 验证模块创建成功
        self.assertIsNotNone(material_manage)
        self.assertEqual(material_manage.db, self.db)
        self.assertEqual(material_manage.id_card_file, self.id_card_file)


class TestSystemSettingModule(unittest.TestCase):
    """测试系统设置模块"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = LocalDatabase(self.db_path)
        
        # 创建模拟的父组件
        self.mock_parent = Mock()
        self.mock_notebook = Mock()
        self.mock_parent.add = Mock()
        
        # 初始化管理模块
        self.default_path = DefaultPath(self.db)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    @patch('tkinter.Frame')
    @patch('tkinter.ttk.Entry')
    def test_system_setting_creation(self, mock_entry, mock_frame):
        """测试系统设置模块创建"""
        # 模拟tkinter组件
        mock_frame.return_value = Mock()
        mock_entry.return_value = Mock()
        
        # 创建系统设置模块
        system_setting = SystemSettingModule(
            self.mock_parent, self.db, self.default_path
        )
        
        # 验证模块创建成功
        self.assertIsNotNone(system_setting)
        self.assertEqual(system_setting.db, self.db)
        self.assertEqual(system_setting.default_path, self.default_path)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = LocalDatabase(self.db_path)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.temp_dir)
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        # 1. 添加项目
        local_project = LocalProject(self.db)
        project_data = {
            'project_name': '集成测试项目',
            'project_type': '软件登记业务',
            'applicant_type': '个人',
            'copyright_owner': '测试著作权人',
            'software_applicant_name': '测试申请人',
            'serial_number': None,
            'priority': '普通',
            'status': '已立项',
            'executor_id': 1,
            'remarks': '集成测试项目'
        }
        
        project_id = local_project.add_project(project_data)
        self.assertIsNotNone(project_id)
        
        # 2. 添加身份证文件
        id_card_file = IDCardFile(self.db)
        id_data = {
            'file_name': 'test_id.pdf',
            'file_path': '/test/path/test_id.pdf',
            'person_name': '测试用户',
            'gender': '男',
            'birthplace': '河南省',
            'id_number': '410123199001011234',
            'remarks': '测试备注'
        }
        
        id_file_id = id_card_file.add_file(id_data)
        self.assertIsNotNone(id_file_id)
        
        # 3. 添加模板文件
        template_file = TemplateFolder(self.db)
        template_data = {
            'file_name': 'test_template.docx',
            'file_path': '/test/path/test_template.docx',
            'programming_language': 'Python',
            'ide_type': 'PyCharm',
            'database_type': 'MySQL',
            'remarks': '测试模板'
        }
        
        template_id = template_file.add_file(template_data)
        self.assertIsNotNone(template_id)
        
        # 4. 更新项目状态
        local_project.update_project_status(project_id, '执行中')
        
        # 5. 验证数据一致性
        project = local_project.get_project_by_id(project_id)
        self.assertEqual(project['status'], '执行中')
        
        id_files = id_card_file.get_all_files()
        self.assertEqual(len(id_files), 1)
        
        templates = template_file.get_all_files()
        self.assertEqual(len(templates), 1)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestLocalDatabase,
        TestDefaultPath,
        TestIDCardFile,
        TestUSCCCFile,
        TestContractFile,
        TestTemplateFolder,
        TestLocalProject,
        TestTaskViewModule,
        TestTemplateManageModule,
        TestMaterialManageModule,
        TestSystemSettingModule,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果
    print(f"\n{'='*60}")
    print(f"测试结果统计:")
    print(f"运行测试: {result.testsRun}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("开始运行桌面应用单元测试...")
    print("="*60)
    
    success = run_tests()
    
    if success:
        print("\n所有测试通过！")
        sys.exit(0)
    else:
        print("\n部分测试失败！")
        sys.exit(1)
