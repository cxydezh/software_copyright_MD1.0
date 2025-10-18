#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试环境准备脚本
初始化测试数据库、创建测试数据、准备测试文件
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime, timedelta
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db, User, Staff, Project, PaperProject, PatentProject, Permission
from config.config import LOCAL_CONFIG

class TestEnvironmentSetup:
    """测试环境准备类"""
    
    def __init__(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # 测试数据目录
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        self.test_files_dir = os.path.join(self.test_data_dir, 'files')
        
    def setup_test_environment(self):
        """设置测试环境"""
        print("=" * 60)
        print("开始准备测试环境...")
        print("=" * 60)
        
        # 1. 创建测试数据目录
        self.create_test_directories()
        
        # 2. 初始化测试数据库
        self.init_test_databases()
        
        # 3. 创建测试用户和员工
        self.create_test_users()
        
        # 4. 创建测试项目数据
        self.create_test_projects()
        
        # 5. 准备测试文件
        self.prepare_test_files()
        
        # 6. 初始化本地SQLite数据库
        self.init_local_test_db()
        
        print("=" * 60)
        print("测试环境准备完成！")
        print("=" * 60)
        
    def create_test_directories(self):
        """创建测试数据目录"""
        print("创建测试数据目录...")
        
        directories = [
            self.test_data_dir,
            self.test_files_dir,
            os.path.join(self.test_files_dir, 'id_cards'),
            os.path.join(self.test_files_dir, 'usccc'),
            os.path.join(self.test_files_dir, 'contracts'),
            os.path.join(self.test_files_dir, 'templates'),
            os.path.join(self.test_files_dir, 'projects')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            
        print(f"测试数据目录创建完成: {self.test_data_dir}")
        
    def init_test_databases(self):
        """初始化测试数据库"""
        print("初始化测试数据库...")
        
        # 创建所有表
        db.create_all()
        
        # 创建默认权限
        self.create_default_permissions()
        
        print("测试数据库初始化完成")
        
    def create_default_permissions(self):
        """创建默认权限"""
        permissions = [
            {
                'position': '普通业务员',
                'can_confirm': True,
                'can_approve': False,
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
                'can_approve': False,
                'can_execute': True,
                'can_manage': True,
                'can_view_all': True,
                'can_edit_paper': True,
                'can_edit_patent': True,
                'is_expert': True
            },
            {
                'position': '系统管理员',
                'can_confirm': True,
                'can_approve': True,
                'can_execute': True,
                'can_manage': True,
                'can_view_all': True,
                'can_edit_paper': True,
                'can_edit_patent': True,
                'is_expert': True
            }
        ]
        
        for perm_data in permissions:
            existing = Permission.query.filter_by(position=perm_data['position']).first()
            if not existing:
                permission = Permission(**perm_data)
                db.session.add(permission)
                
        db.session.commit()
        print("默认权限创建完成")
        
    def create_test_users(self):
        """创建测试用户"""
        print("创建测试用户...")
        
        # 测试用户
        test_users = [
            {
                'name': '测试用户1',
                'email': 'testuser1@example.com',
                'phone': '13800138001',
                'user_category': '软件著作权',
                'organization': '测试机构1',
                'research_field': '医疗软件'
            },
            {
                'name': '测试用户2',
                'email': 'testuser2@example.com',
                'phone': '13800138002',
                'user_category': '论文指导',
                'organization': '测试医院',
                'research_field': '医学影像'
            },
            {
                'name': '测试用户3',
                'email': 'testuser3@example.com',
                'phone': '13800138003',
                'user_category': '专利申请',
                'organization': '测试企业',
                'research_field': '医疗器械'
            }
        ]
        
        for user_data in test_users:
            existing = User.query.filter_by(email=user_data['email']).first()
            if not existing:
                user = User(**user_data)
                user.set_password('password123')
                db.session.add(user)
                
        # 测试员工
        test_staff = [
            {
                'name': '测试业务员',
                'email': 'teststaff@example.com',
                'phone': '13800138004',
                'position_id': 1  # 普通业务员
            },
            {
                'name': '测试执行者',
                'email': 'testexecutor@example.com',
                'phone': '13800138005',
                'position_id': 2  # 项目执行者
            },
            {
                'name': '系统管理员',
                'email': 'admin@yiqichuang.com',
                'phone': '13800138000',
                'position_id': 3  # 系统管理员
            }
        ]
        
        for staff_data in test_staff:
            existing = Staff.query.filter_by(email=staff_data['email']).first()
            if not existing:
                staff = Staff(**staff_data)
                staff.set_password('admin123')
                db.session.add(staff)
                
        db.session.commit()
        print("测试用户创建完成")
        
    def create_test_projects(self):
        """创建测试项目"""
        print("创建测试项目...")
        
        # 获取测试用户和执行者
        test_user = User.query.filter_by(email='testuser1@example.com').first()
        test_executor = Staff.query.filter_by(email='testexecutor@example.com').first()
        
        if not test_user or not test_executor:
            print("警告: 测试用户或执行者不存在，跳过项目创建")
            return
            
        # 软件著作权项目
        software_projects = [
            {
                'project_name': '医疗管理系统V1.0',
                'project_type': '软件登记业务',
                'applicant_type': '个人',
                'copyright_owner': '测试用户1',
                'software_applicant_name': '测试用户1',
                'priority': '普通',
                'price': 2000.00,
                'status': '待确认',
                'applicant_id': test_user.id
            },
            {
                'project_name': '医院信息管理系统V2.0',
                'project_type': '软件设计与登记业务',
                'applicant_type': '事业单位',
                'copyright_owner': '测试医院',
                'software_applicant_name': '测试医院',
                'priority': '加急',
                'price': 5000.00,
                'status': '已立项',
                'applicant_id': test_user.id,
                'executor_id': test_executor.id
            },
            {
                'project_name': '医疗设备监控系统V1.0',
                'project_type': '软件部署与登记业务',
                'applicant_type': '事业单位联合个人',
                'copyright_owner': '测试医院,测试用户1',
                'software_applicant_name': '测试医院',
                'priority': '快速',
                'price': 8000.00,
                'status': '执行中',
                'applicant_id': test_user.id,
                'executor_id': test_executor.id
            }
        ]
        
        for project_data in software_projects:
            existing = Project.query.filter_by(project_name=project_data['project_name']).first()
            if not existing:
                project = Project(**project_data)
                db.session.add(project)
                
        # 论文项目
        paper_projects = [
            {
                'project_name': '基于深度学习的医学影像诊断研究',
                'project_type': '论文指导',
                'service_level': '标准服务',
                'applicant_type': '个人学者',
                'paper_title': '基于深度学习的医学影像诊断研究',
                'research_field': '医学影像',
                'target_journal': 'Medical Image Analysis',
                'paper_status': '初稿',
                'price': 3000.00,
                'status': '待确认',
                'applicant_id': test_user.id
            }
        ]
        
        for project_data in paper_projects:
            existing = PaperProject.query.filter_by(project_name=project_data['project_name']).first()
            if not existing:
                project = PaperProject(**project_data)
                db.session.add(project)
                
        # 专利项目
        patent_projects = [
            {
                'project_name': '智能医疗设备控制系统',
                'project_type': '发明专利',
                'applicant_type': '企业申请',
                'patent_title': '智能医疗设备控制系统',
                'technical_field': '医疗器械',
                'patent_status': '准备材料',
                'price': 10000.00,
                'status': '待确认',
                'applicant_id': test_user.id
            }
        ]
        
        for project_data in patent_projects:
            existing = PatentProject.query.filter_by(project_name=project_data['project_name']).first()
            if not existing:
                project = PatentProject(**project_data)
                db.session.add(project)
                
        db.session.commit()
        print("测试项目创建完成")
        
    def prepare_test_files(self):
        """准备测试文件"""
        print("准备测试文件...")
        
        # 创建测试PDF文件（空文件，仅用于测试）
        test_files = [
            ('id_cards', '1.张三_身份证.pdf'),
            ('id_cards', '2.李四_身份证.pdf'),
            ('usccc', '1.测试医院_统一社会信用代码证书.pdf'),
            ('usccc', '2.测试企业_统一社会信用代码证书.pdf'),
            ('contracts', '1.合作开发合同.pdf'),
            ('contracts', '2.技术转让合同.pdf'),
            ('templates', '医疗软件模板/需求文档.docx'),
            ('templates', '医疗软件模板/设计文档.docx'),
            ('templates', '医疗软件模板/用户手册.docx')
        ]
        
        for folder, filename in test_files:
            folder_path = os.path.join(self.test_files_dir, folder)
            os.makedirs(folder_path, exist_ok=True)
            
            file_path = os.path.join(folder_path, filename)
            if not os.path.exists(file_path):
                # 创建空文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"测试文件: {filename}")
                    
        print("测试文件准备完成")
        
    def init_local_test_db(self):
        """初始化本地SQLite测试数据库"""
        print("初始化本地SQLite测试数据库...")
        
        # 创建本地测试数据库路径
        local_db_path = os.path.join(self.test_data_dir, 'local_test.db')
        
        # 初始化本地数据库
        conn = sqlite3.connect(local_db_path)
        cursor = conn.cursor()
        
        # 创建表结构（简化版）
        tables = [
            '''CREATE TABLE IF NOT EXISTS default_paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path_type TEXT UNIQUE NOT NULL,
                path_value TEXT NOT NULL,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_time TEXT DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS id_card_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                person_name TEXT,
                gender TEXT,
                birthplace TEXT,
                id_number TEXT,
                remarks TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS usccc_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                organization_name TEXT,
                validity_period TEXT,
                legal_representative TEXT,
                remarks TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS contract_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                contract_name TEXT,
                participant_type TEXT,
                remarks TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS template_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_name TEXT NOT NULL,
                folder_path TEXT NOT NULL,
                template_name TEXT,
                programming_language TEXT,
                ide TEXT,
                database_type TEXT,
                application_type TEXT,
                remarks TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS local_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                project_type TEXT NOT NULL,
                applicant_type TEXT NOT NULL,
                copyright_owner TEXT,
                software_applicant_name TEXT,
                serial_number TEXT,
                priority TEXT DEFAULT '普通',
                status TEXT DEFAULT '已确认',
                executor_id INTEGER,
                remarks TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP
            )'''
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
            
        # 插入测试数据
        test_data = [
            ("INSERT INTO default_paths (path_type, path_value) VALUES (?, ?)", 
             [('BASE_DIR', self.test_data_dir), ('IDPDF_DIR', os.path.join(self.test_files_dir, 'id_cards'))]),
            ("INSERT INTO id_card_files (file_name, file_path, person_name, gender, birthplace, id_number) VALUES (?, ?, ?, ?, ?, ?)",
             [('1.张三_身份证.pdf', os.path.join(self.test_files_dir, 'id_cards', '1.张三_身份证.pdf'), '张三', '男', '河南省郑州市', '410101199001011234')]),
            ("INSERT INTO usccc_files (file_name, file_path, organization_name, validity_period, legal_representative) VALUES (?, ?, ?, ?, ?)",
             [('1.测试医院_统一社会信用代码证书.pdf', os.path.join(self.test_files_dir, 'usccc', '1.测试医院_统一社会信用代码证书.pdf'), '测试医院', '2025-12-31', '张院长')]),
            ("INSERT INTO contract_files (file_name, file_path, contract_name, participant_type) VALUES (?, ?, ?, ?)",
             [('1.合作开发合同.pdf', os.path.join(self.test_files_dir, 'contracts', '1.合作开发合同.pdf'), '合作开发合同', '事业单位联合个人')]),
            ("INSERT INTO template_folders (folder_name, folder_path, template_name, programming_language, ide, database_type, application_type) VALUES (?, ?, ?, ?, ?, ?, ?)",
             [('医疗软件模板', os.path.join(self.test_files_dir, 'templates', '医疗软件模板'), '医疗软件模板', 'Python', 'VSCode', 'MySQL', 'Web应用')])
        ]
        
        for sql, data_list in test_data:
            for data in data_list:
                cursor.execute(sql, data)
                
        conn.commit()
        conn.close()
        
        print(f"本地SQLite测试数据库初始化完成: {local_db_path}")
        
    def cleanup_test_environment(self):
        """清理测试环境"""
        print("清理测试环境...")
        
        # 删除测试数据目录
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
            
        print("测试环境清理完成")

def main():
    """主函数"""
    setup = TestEnvironmentSetup()
    
    try:
        setup.setup_test_environment()
        
        print("\n测试环境准备完成！")
        print("可以使用以下测试账户:")
        print("管理员: admin@yiqichuang.com / admin123")
        print("测试用户: testuser1@example.com / password123")
        print("测试执行者: testexecutor@example.com / admin123")
        
    except Exception as e:
        print(f"测试环境准备失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
