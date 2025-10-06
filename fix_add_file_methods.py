#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复add_file方法，使其返回插入的ID
"""

import re

def fix_add_file_methods():
    """修复local_models.py中的add_file方法"""
    
    file_path = 'desktop_app/local_models.py'
    
    # 读取文件内容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复IDCardFile的add_file方法
    pattern1 = r'(def add_file\(self, file_name, file_path, person_name=None, gender=None,\s+birthplace=None, id_number=None, remarks=None\):\s+"""添加身份证文件"""\s+self\.db\.execute_update\(\s+"""INSERT INTO id_card_files\s+\(file_name, file_path, person_name, gender, birthplace, id_number, remarks\)\s+VALUES \(\?, \?, \?, \?, \?, \?, \?\)""",\s+\(file_name, file_path, person_name, gender, birthplace, id_number, remarks\)\s+\)\s+)'
    
    replacement1 = r'\1cursor = self.db.execute_update(\n            """INSERT INTO id_card_files \n               (file_name, file_path, person_name, gender, birthplace, id_number, remarks)\n               VALUES (?, ?, ?, ?, ?, ?, ?)""",\n            (file_name, file_path, person_name, gender, birthplace, id_number, remarks)\n        )\n        return cursor.lastrowid'
    
    content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE | re.DOTALL)
    
    # 修复USCCCFile的add_file方法
    pattern2 = r'(def add_file\(self, file_name, file_path, organization_name=None,\s+validity_period=None, legal_representative=None, remarks=None\):\s+"""添加证书文件"""\s+self\.db\.execute_update\(\s+"""INSERT INTO usccc_files\s+\(file_name, file_path, organization_name, validity_period, legal_representative, remarks\)\s+VALUES \(\?, \?, \?, \?, \?, \?\)""",\s+\(file_name, file_path, organization_name, validity_period, legal_representative, remarks\)\s+\)\s+)'
    
    replacement2 = r'\1cursor = self.db.execute_update(\n            """INSERT INTO usccc_files \n               (file_name, file_path, organization_name, validity_period, legal_representative, remarks)\n               VALUES (?, ?, ?, ?, ?, ?)""",\n            (file_name, file_path, organization_name, validity_period, legal_representative, remarks)\n        )\n        return cursor.lastrowid'
    
    content = re.sub(pattern2, replacement2, content, flags=re.MULTILINE | re.DOTALL)
    
    # 修复ContractFile的add_file方法
    pattern3 = r'(def add_file\(self, file_name, file_path, contract_name=None,\s+participant_type=None, remarks=None\):\s+"""添加合同文件"""\s+self\.db\.execute_update\(\s+"""INSERT INTO contract_files\s+\(file_name, file_path, contract_name, participant_type, remarks\)\s+VALUES \(\?, \?, \?, \?, \?\)""",\s+\(file_name, file_path, contract_name, participant_type, remarks\)\s+\)\s+)'
    
    replacement3 = r'\1cursor = self.db.execute_update(\n            """INSERT INTO contract_files \n               (file_name, file_path, contract_name, participant_type, remarks)\n               VALUES (?, ?, ?, ?, ?)""",\n            (file_name, file_path, contract_name, participant_type, remarks)\n        )\n        return cursor.lastrowid'
    
    content = re.sub(pattern3, replacement3, content, flags=re.MULTILINE | re.DOTALL)
    
    # 修复TemplateFolder的add_file方法
    pattern4 = r'(def add_file\(self, file_name, file_path, programming_language=None,\s+ide_type=None, database_type=None, remarks=None\):\s+"""添加模板文件"""\s+self\.db\.execute_update\(\s+"""INSERT INTO template_files\s+\(file_name, file_path, programming_language, ide_type, database_type, remarks\)\s+VALUES \(\?, \?, \?, \?, \?, \?\)""",\s+\(file_name, file_path, programming_language, ide_type, database_type, remarks\)\s+\)\s+)'
    
    replacement4 = r'\1cursor = self.db.execute_update(\n            """INSERT INTO template_files \n               (file_name, file_path, programming_language, ide_type, database_type, remarks)\n               VALUES (?, ?, ?, ?, ?, ?)""",\n            (file_name, file_path, programming_language, ide_type, database_type, remarks)\n        )\n        return cursor.lastrowid'
    
    content = re.sub(pattern4, replacement4, content, flags=re.MULTILINE | re.DOTALL)
    
    # 修复ProjectFile的add_file方法
    pattern5 = r'(def add_file\(self, file_name, file_path, project_id=None,\s+file_type=None, remarks=None\):\s+"""添加项目文件"""\s+self\.db\.execute_update\(\s+"""INSERT INTO project_files\s+\(file_name, file_path, project_id, file_type, remarks\)\s+VALUES \(\?, \?, \?, \?, \?\)""",\s+\(file_name, file_path, project_id, file_type, remarks\)\s+\)\s+)'
    
    replacement5 = r'\1cursor = self.db.execute_update(\n            """INSERT INTO project_files \n               (file_name, file_path, project_id, file_type, remarks)\n               VALUES (?, ?, ?, ?, ?)""",\n            (file_name, file_path, project_id, file_type, remarks)\n        )\n        return cursor.lastrowid'
    
    content = re.sub(pattern5, replacement5, content, flags=re.MULTILINE | re.DOTALL)
    
    # 修复LocalProject的add_project方法
    pattern6 = r'(def add_project\(self, project_name, project_type, applicant_type,\s+copyright_owner, software_applicant_name, serial_number, priority, status,\s+executor_id, remarks\):\s+"""添加项目"""\s+self\.db\.execute_update\(\s+"""INSERT INTO local_projects\s+\(project_name, project_type, applicant_type, copyright_owner, software_applicant_name, serial_number, priority, status, executor_id, remarks\)\s+VALUES \(\?, \?, \?, \?, \?, \?, \?, \?, \?, \?\)""",\s+\(project_name, project_type, applicant_type, copyright_owner, software_applicant_name, serial_number, priority, status, executor_id, remarks\)\s+\)\s+)'
    
    replacement6 = r'\1cursor = self.db.execute_update(\n            """INSERT INTO local_projects \n               (project_name, project_type, applicant_type, copyright_owner, software_applicant_name, serial_number, priority, status, executor_id, remarks)\n               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",\n            (project_name, project_type, applicant_type, copyright_owner, software_applicant_name, serial_number, priority, status, executor_id, remarks)\n        )\n        return cursor.lastrowid'
    
    content = re.sub(pattern6, replacement6, content, flags=re.MULTILINE | re.DOTALL)
    
    # 写回文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("修复完成！")

if __name__ == '__main__':
    fix_add_file_methods()
