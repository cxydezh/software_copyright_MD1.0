#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地数据库模型 - 修复版
根据需求分析文档设计：本地SQLite数据库表结构
"""

import sqlite3
import os
from datetime import datetime


class LocalDatabase:
    """本地数据库管理"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建默认路径表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS default_paths (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path_type TEXT UNIQUE NOT NULL,
                path_value TEXT NOT NULL,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_time TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建身份证复印件表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS id_card_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                person_name TEXT,
                gender TEXT,
                birthplace TEXT,
                id_number TEXT,
                remarks TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_time TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建统一社会信用代码证书文件表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usccc_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                organization_name TEXT,
                validity_period TEXT,
                legal_representative TEXT,
                remarks TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_time TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建合同文件表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contract_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                contract_name TEXT,
                participant_type TEXT,
                remarks TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_time TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建项目模板表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS template_folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_name TEXT NOT NULL,
                folder_path TEXT NOT NULL,
                programming_language TEXT,
                ide_type TEXT,
                database_type TEXT,
                programming_type TEXT,
                remarks TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_time TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建项目文件表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                project_id INTEGER,
                file_type TEXT,
                file_size INTEGER DEFAULT 0,
                remarks TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_time TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建本地项目表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_name TEXT NOT NULL,
                project_type TEXT NOT NULL,
                applicant_type TEXT NOT NULL,
                copyright_owner TEXT,
                software_applicant_name TEXT,
                serial_number TEXT,
                priority TEXT,
                status TEXT,
                executor_id INTEGER,
                remarks TEXT,
                created_time TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_time TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query, params=None):
        """执行查询"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = cursor.fetchall()
        conn.close()
        return result
    
    def execute_update(self, query, params=None):
        """执行更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        conn.close()
        return cursor


class DefaultPath:
    """默认路径管理"""
    
    def __init__(self, db):
        self.db = db
    
    def set_path(self, path_type, path_value):
        """设置路径"""
        self.db.execute_update(
            """INSERT OR REPLACE INTO default_paths (path_type, path_value, updated_time)
               VALUES (?, ?, ?)""",
            (path_type, path_value, datetime.now().isoformat())
        )
    
    def get_path(self, path_type):
        """获取路径"""
        result = self.db.execute_query(
            "SELECT path_value FROM default_paths WHERE path_type = ?",
            (path_type,)
        )
        return result[0][0] if result else None
    
    def get_all_paths(self):
        """获取所有路径"""
        return self.db.execute_query("SELECT * FROM default_paths")


class IDCardFile:
    """身份证复印件管理"""
    
    def __init__(self, db):
        self.db = db
    
    def add_file(self, file_name, file_path, person_name=None, gender=None, 
                 birthplace=None, id_number=None, remarks=None):
        """添加身份证文件"""
        cursor = self.db.execute_update(
            """INSERT INTO id_card_files 
               (file_name, file_path, person_name, gender, birthplace, id_number, remarks)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (file_name, file_path, person_name, gender, birthplace, id_number, remarks)
        )
        return cursor.lastrowid
    
    def get_all_files(self):
        """获取所有身份证文件"""
        return self.db.execute_query("SELECT * FROM id_card_files ORDER BY created_time DESC")
    
    def get_recent_files(self, limit=10):
        """获取最近添加的文件"""
        return self.db.execute_query(
            "SELECT * FROM id_card_files ORDER BY created_time DESC LIMIT ?", 
            (limit,)
        )
    
    def get_file_by_id(self, file_id):
        """根据ID获取文件信息"""
        result = self.db.execute_query(
            "SELECT * FROM id_card_files WHERE id = ?", 
            (file_id,)
        )
        return result[0] if result else None
    
    def update_file(self, file_id, **kwargs):
        """更新文件信息"""
        if not kwargs:
            return
        
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [datetime.now().isoformat(), file_id]
        self.db.execute_update(
            f"UPDATE id_card_files SET {set_clause}, updated_time = ? WHERE id = ?",
            values
        )
    
    def delete_file(self, file_id):
        """删除文件记录"""
        self.db.execute_update("DELETE FROM id_card_files WHERE id = ?", (file_id,))


class USCCCFile:
    """统一社会信用代码证书文件管理"""
    
    def __init__(self, db):
        self.db = db
    
    def add_file(self, file_name, file_path, organization_name=None, 
                 validity_period=None, legal_representative=None, remarks=None):
        """添加证书文件"""
        cursor = self.db.execute_update(
            """INSERT INTO usccc_files 
               (file_name, file_path, organization_name, validity_period, legal_representative, remarks)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (file_name, file_path, organization_name, validity_period, legal_representative, remarks)
        )
        return cursor.lastrowid
    
    def get_all_files(self):
        """获取所有证书文件"""
        return self.db.execute_query("SELECT * FROM usccc_files ORDER BY created_time DESC")
    
    def get_recent_files(self, limit=10):
        """获取最近添加的文件"""
        return self.db.execute_query(
            "SELECT * FROM usccc_files ORDER BY created_time DESC LIMIT ?", 
            (limit,)
        )
    
    def get_file_by_id(self, file_id):
        """根据ID获取文件信息"""
        result = self.db.execute_query(
            "SELECT * FROM usccc_files WHERE id = ?", 
            (file_id,)
        )
        return result[0] if result else None
    
    def update_file(self, file_id, **kwargs):
        """更新文件信息"""
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [file_id]
        self.db.execute_update(
            f"UPDATE usccc_files SET {set_clause}, updated_time = ? WHERE id = ?",
            values + [datetime.now().isoformat()]
        )
    
    def delete_file(self, file_id):
        """删除文件记录"""
        self.db.execute_update("DELETE FROM usccc_files WHERE id = ?", (file_id,))


class ContractFile:
    """合同文件管理"""
    
    def __init__(self, db):
        self.db = db
    
    def add_file(self, file_name, file_path, contract_name=None,
                 participant_type=None, remarks=None):
        """添加合同文件"""
        cursor = self.db.execute_update(
            """INSERT INTO contract_files 
               (file_name, file_path, contract_name, participant_type, remarks)
               VALUES (?, ?, ?, ?, ?)""",
            (file_name, file_path, contract_name, participant_type, remarks)
        )
        return cursor.lastrowid
    
    def get_all_files(self):
        """获取所有合同文件"""
        return self.db.execute_query("SELECT * FROM contract_files ORDER BY created_time DESC")
    
    def get_recent_files(self, limit=10):
        """获取最近添加的文件"""
        return self.db.execute_query(
            "SELECT * FROM contract_files ORDER BY created_time DESC LIMIT ?", 
            (limit,)
        )
    
    def get_file_by_id(self, file_id):
        """根据ID获取文件信息"""
        result = self.db.execute_query(
            "SELECT * FROM contract_files WHERE id = ?", 
            (file_id,)
        )
        return result[0] if result else None
    
    def update_file(self, file_id, **kwargs):
        """更新文件信息"""
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [file_id]
        self.db.execute_update(
            f"UPDATE contract_files SET {set_clause}, updated_time = ? WHERE id = ?",
            values + [datetime.now().isoformat()]
        )
    
    def delete_file(self, file_id):
        """删除文件记录"""
        self.db.execute_update("DELETE FROM contract_files WHERE id = ?", (file_id,))


class TemplateFolder:
    """项目模板文件夹管理"""
    
    def __init__(self, db):
        self.db = db
    
    def add_folder(self, folder_name, folder_path, programming_language=None,
                 ide_type=None, database_type=None, programming_type=None, remarks=None):
        """添加模板文件夹"""
        cursor = self.db.execute_update(
            """INSERT INTO template_folders 
               (folder_name, folder_path, programming_language, ide_type, database_type, programming_type, remarks)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (folder_name, folder_path, programming_language, ide_type, database_type, programming_type, remarks)
        )
        return cursor.lastrowid
    
    def get_all_folders(self):
        """获取所有模板文件夹"""
        return self.db.execute_query("SELECT * FROM template_folders ORDER BY created_time DESC")

    # 兼容旧接口：get_all_templates → get_all_files
    def get_all_templates(self):
        """兼容旧代码，返回所有模板（等同于 get_all_folders）"""
        return self.get_all_folders()
    
    def get_recent_folders(self, limit=10):
        """获取最近添加的文件夹"""
        return self.db.execute_query(
            "SELECT * FROM template_folders ORDER BY created_time DESC LIMIT ?", 
            (limit,)
        )
    
    def get_folder_by_id(self, folder_id):
        """根据ID获取文件夹信息"""
        result = self.db.execute_query(
            "SELECT * FROM template_folders WHERE id = ?", 
            (folder_id,)
        )
        return result[0] if result else None

    # 兼容旧接口：get_template_by_id → get_file_by_id
    def get_template_by_id(self, template_id):
        """兼容旧代码，根据ID获取模板（等同于 get_file_by_id）"""
        return self.get_folder_by_id(template_id)
    
    def update_folder(self, folder_id, **kwargs):
        """更新文件信息"""
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [folder_id]
        self.db.execute_update(
            f"UPDATE template_folders SET {set_clause}, updated_time = ? WHERE id = ?",
            values + [datetime.now().isoformat()]
        )
    
    def delete_folder(self, folder_id):
        """删除文件夹记录"""
        self.db.execute_update("DELETE FROM template_folders WHERE id = ?", (folder_id,))


class ProjectFile:
    """项目文件管理"""
    
    def __init__(self, db):
        self.db = db
    
    def add_file(self, file_name, file_path, project_id=None,
                 file_type=None, file_size=0, remarks=None):
        """添加项目文件"""
        cursor = self.db.execute_update(
            """INSERT INTO project_files 
               (file_name, file_path, project_id, file_type, file_size, remarks)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (file_name, file_path, project_id, file_type, file_size, remarks)
        )
        return cursor.lastrowid
    
    def get_all_files(self):
        """获取所有项目文件"""
        return self.db.execute_query("SELECT * FROM project_files ORDER BY created_time DESC")
    
    def get_files_by_project(self, project_id):
        """根据项目ID获取文件"""
        return self.db.execute_query(
            "SELECT * FROM project_files WHERE project_id = ? ORDER BY created_time DESC",
            (project_id,)
        )
    
    def get_file_by_id(self, file_id):
        """根据ID获取文件信息"""
        result = self.db.execute_query(
            "SELECT * FROM project_files WHERE id = ?", 
            (file_id,)
        )
        return result[0] if result else None
    
    def update_file(self, file_id, **kwargs):
        """更新文件信息"""
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [file_id]
        self.db.execute_update(
            f"UPDATE project_files SET {set_clause}, updated_time = ? WHERE id = ?",
            values + [datetime.now().isoformat()]
        )
    
    def delete_file(self, file_id):
        """删除文件记录"""
        self.db.execute_update("DELETE FROM project_files WHERE id = ?", (file_id,))


class LocalProject:
    """本地项目管理"""
    
    def __init__(self, db):
        self.db = db
    
    def add_project(self, project_name, project_type, applicant_type,
                    copyright_owner, software_applicant_name, serial_number, priority, status,
                    executor_id, remarks):
        """添加项目"""
        cursor = self.db.execute_update(
            """INSERT INTO local_projects 
               (project_name, project_type, applicant_type, copyright_owner, software_applicant_name, serial_number, priority, status, executor_id, remarks)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (project_name, project_type, applicant_type, copyright_owner, software_applicant_name, serial_number, priority, status, executor_id, remarks)
        )
        return cursor.lastrowid
    
    def get_all_projects(self):
        """获取所有项目"""
        try:
            return self.db.execute_query("SELECT * FROM local_projects ORDER BY created_time DESC")
        except Exception:
            # 兼容旧版本数据库无 created_time 列的情况
            return self.db.execute_query("SELECT * FROM local_projects ORDER BY id DESC")
    
    def get_project_by_id(self, project_id):
        """根据ID获取项目"""
        result = self.db.execute_query(
            "SELECT * FROM local_projects WHERE id = ?", 
            (project_id,)
        )
        if result:
            columns = ['id', 'project_name', 'project_type', 'applicant_type', 
                      'copyright_owner', 'software_applicant_name', 'serial_number', 
                      'priority', 'status', 'executor_id', 'remarks', 'created_time', 'updated_time']
            return dict(zip(columns, result[0]))
        return None
    
    def update_project(self, project_id, **kwargs):
        """更新项目信息"""
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [project_id]
        self.db.execute_update(
            f"UPDATE local_projects SET {set_clause}, updated_time = ? WHERE id = ?",
            values + [datetime.now().isoformat()]
        )
    
    def update_project_status(self, project_id, status):
        """更新项目状态"""
        self.db.execute_update(
            "UPDATE local_projects SET status = ?, updated_time = ? WHERE id = ?",
            (status, datetime.now().isoformat(), project_id)
        )
    
    def delete_project(self, project_id):
        """删除项目"""
        self.db.execute_update("DELETE FROM local_projects WHERE id = ?", (project_id,))
    
    def sync_projects(self, projects_data):
        """同步项目数据"""
        for project_data in projects_data:
            # 检查项目是否已存在
            existing = self.db.execute_query(
                "SELECT id FROM local_projects WHERE id = ?", 
                (project_data['id'],)
            )
            
            if existing:
                # 更新现有项目
                self.db.execute_update(
                    """UPDATE local_projects SET 
                       project_name = ?, project_type = ?, applicant_type = ?, 
                       copyright_owner = ?, software_applicant_name = ?, 
                       serial_number = ?, priority = ?, status = ?, 
                       executor_id = ?, remarks = ?, updated_time = ?
                       WHERE id = ?""",
                    (project_data['project_name'], project_data['project_type'], 
                     project_data['applicant_type'], project_data['copyright_owner'],
                     project_data['software_applicant_name'], project_data['serial_number'],
                     project_data['priority'], project_data['status'], 
                     project_data['executor_id'], project_data['remarks'],
                     datetime.now().isoformat(), project_data['id'])
                )
            else:
                # 插入新项目
                self.db.execute_update(
                    """INSERT INTO local_projects 
                       (id, project_name, project_type, applicant_type, copyright_owner, 
                        software_applicant_name, serial_number, priority, status, 
                        executor_id, remarks)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (project_data['id'], project_data['project_name'], 
                     project_data['project_type'], project_data['applicant_type'],
                     project_data['copyright_owner'], project_data['software_applicant_name'],
                     project_data['serial_number'], project_data['priority'], 
                     project_data['status'], project_data['executor_id'], 
                     project_data['remarks'])
                )
