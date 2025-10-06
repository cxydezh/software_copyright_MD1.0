#!/usr/bin/env python3
"""
系统功能检查脚本
检查论文指导和专利申请功能的完整性和缺失项
"""

import os
import sys
import requests
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def check_missing_templates():
    """检查缺失的模板文件"""
    print("=== 检查缺失的模板文件 ===")
    
    missing_templates = []
    
    # 检查论文相关模板
    paper_templates = [
        'paper/edit.html',
        'paper/staff_dashboard.html'
    ]
    
    for template in paper_templates:
        if not os.path.exists(f'templates/{template}'):
            missing_templates.append(template)
            print(f"缺失: templates/{template}")
    
    # 检查专利相关模板
    patent_templates = [
        'patent/detail.html',
        'patent/edit.html',
        'patent/staff_dashboard.html'
    ]
    
    for template in patent_templates:
        if not os.path.exists(f'templates/{template}'):
            missing_templates.append(template)
            print(f"缺失: templates/{template}")
    
    if not missing_templates:
        print("所有模板文件都存在")
    
    return missing_templates

def check_missing_views():
    """检查缺失的视图文件"""
    print("\n=== 检查缺失的视图文件 ===")
    
    missing_views = []
    
    # 检查视图文件
    view_files = [
        'web_app/views/paper.py',
        'web_app/views/patent.py'
    ]
    
    for view_file in view_files:
        if not os.path.exists(view_file):
            missing_views.append(view_file)
            print(f"缺失: {view_file}")
    
    if not missing_views:
        print("所有视图文件都存在")
    
    return missing_views

def check_database_models():
    """检查数据库模型"""
    print("\n=== 检查数据库模型 ===")
    
    try:
        from web_app.app import create_app
        from database.models import db, PaperProject, PatentProject, ProjectFile
        
        app = create_app('testing')
        with app.app_context():
            # 检查表是否存在
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['paper_projects', 'patent_projects', 'project_files']
            missing_tables = []
            
            for table in required_tables:
                if table not in tables:
                    missing_tables.append(table)
                    print(f"缺失表: {table}")
            
            if not missing_tables:
                print("所有数据库表都存在")
            
            return missing_tables
            
    except Exception as e:
        print(f"数据库检查失败: {e}")
        return ['database_error']

def check_web_endpoints():
    """检查Web端点"""
    print("\n=== 检查Web端点 ===")
    
    base_url = "http://localhost:5000"
    endpoints_to_check = [
        ('/services', '服务项目页面'),
        ('/paper/', '论文指导首页'),
        ('/paper/apply', '论文申请页面'),
        ('/patent/', '专利申请首页'),
        ('/patent/apply', '专利申请页面'),
        ('/paper/staff', '论文管理面板'),
        ('/patent/staff', '专利管理面板')
    ]
    
    working_endpoints = []
    broken_endpoints = []
    
    for endpoint, description in endpoints_to_check:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                working_endpoints.append((endpoint, description))
                print(f"正常: {endpoint} - {description}")
            elif response.status_code == 302:
                print(f"重定向: {endpoint} - {description} (可能需要登录)")
            else:
                broken_endpoints.append((endpoint, description, response.status_code))
                print(f"错误: {endpoint} - {description} (状态码: {response.status_code})")
        except requests.exceptions.RequestException as e:
            broken_endpoints.append((endpoint, description, str(e)))
            print(f"无法访问: {endpoint} - {description} ({e})")
    
    return working_endpoints, broken_endpoints

def check_file_structure():
    """检查文件结构"""
    print("\n=== 检查文件结构 ===")
    
    required_dirs = [
        'templates/paper',
        'templates/patent',
        'web_app/views',
        'static/uploads'
    ]
    
    missing_dirs = []
    
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
            print(f"缺失目录: {dir_path}")
    
    if not missing_dirs:
        print("所有必需目录都存在")
    
    return missing_dirs

def check_configuration():
    """检查配置"""
    print("\n=== 检查配置 ===")
    
    config_issues = []
    
    # 检查配置文件
    if not os.path.exists('config/config.py'):
        config_issues.append('config/config.py 不存在')
        print("缺失: config/config.py")
    
    # 检查数据库迁移脚本
    if not os.path.exists('migrate_paper_patent.py'):
        config_issues.append('migrate_paper_patent.py 不存在')
        print("缺失: migrate_paper_patent.py")
    
    # 检查requirements.txt
    if not os.path.exists('requirements.txt'):
        config_issues.append('requirements.txt 不存在')
        print("缺失: requirements.txt")
    
    if not config_issues:
        print("配置文件完整")
    
    return config_issues

def generate_report():
    """生成功能检查报告"""
    print("\n" + "="*60)
    print("系统功能完整性检查报告")
    print("="*60)
    
    # 执行各项检查
    missing_templates = check_missing_templates()
    missing_views = check_missing_views()
    missing_tables = check_database_models()
    working_endpoints, broken_endpoints = check_web_endpoints()
    missing_dirs = check_file_structure()
    config_issues = check_configuration()
    
    # 生成报告
    print("\n" + "="*60)
    print("检查结果汇总")
    print("="*60)
    
    total_issues = (len(missing_templates) + len(missing_views) + 
                   len(missing_tables) + len(broken_endpoints) + 
                   len(missing_dirs) + len(config_issues))
    
    if total_issues == 0:
        print("[OK] 系统功能完整，没有发现缺失项")
    else:
        print(f"发现 {total_issues} 个问题需要解决:")
        
        if missing_templates:
            print(f"\n1. 缺失模板文件 ({len(missing_templates)}个):")
            for template in missing_templates:
                print(f"   - {template}")
        
        if missing_views:
            print(f"\n2. 缺失视图文件 ({len(missing_views)}个):")
            for view in missing_views:
                print(f"   - {view}")
        
        if missing_tables:
            print(f"\n3. 数据库问题 ({len(missing_tables)}个):")
            for table in missing_tables:
                print(f"   - {table}")
        
        if broken_endpoints:
            print(f"\n4. Web端点问题 ({len(broken_endpoints)}个):")
            for endpoint, description, error in broken_endpoints:
                print(f"   - {endpoint}: {description} ({error})")
        
        if missing_dirs:
            print(f"\n5. 缺失目录 ({len(missing_dirs)}个):")
            for dir_path in missing_dirs:
                print(f"   - {dir_path}")
        
        if config_issues:
            print(f"\n6. 配置问题 ({len(config_issues)}个):")
            for issue in config_issues:
                print(f"   - {issue}")
    
    print(f"\n正常工作的端点 ({len(working_endpoints)}个):")
    for endpoint, description in working_endpoints:
        print(f"   [OK] {endpoint}: {description}")
    
    return {
        'missing_templates': missing_templates,
        'missing_views': missing_views,
        'missing_tables': missing_tables,
        'broken_endpoints': broken_endpoints,
        'missing_dirs': missing_dirs,
        'config_issues': config_issues,
        'working_endpoints': working_endpoints,
        'total_issues': total_issues
    }

if __name__ == '__main__':
    report = generate_report()
    
    print("\n" + "="*60)
    print("建议的修复步骤:")
    print("="*60)
    
    if report['missing_templates']:
        print("\n1. 创建缺失的模板文件:")
        for template in report['missing_templates']:
            print(f"   - 创建 templates/{template}")
    
    if report['missing_dirs']:
        print("\n2. 创建缺失的目录:")
        for dir_path in report['missing_dirs']:
            print(f"   - 创建 {dir_path}")
    
    if report['missing_tables']:
        print("\n3. 运行数据库迁移:")
        print("   - python migrate_paper_patent.py")
    
    if report['broken_endpoints']:
        print("\n4. 检查Web服务是否运行:")
        print("   - python run_web.py")
    
    print("\n检查完成!")
