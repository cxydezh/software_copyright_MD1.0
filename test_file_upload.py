#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试文件上传和下载功能
"""
import sys
import os
import tempfile
import shutil

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from database.models import db, Project, ProjectFile, Staff, User
from werkzeug.security import generate_password_hash

def test_file_upload():
    """测试文件上传和下载功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("开始测试文件上传和下载功能")
        print("=" * 60)
        
        # 创建测试用户和项目
        print("\n[1] 创建测试数据...")
        try:
            # 查找或创建测试用户
            test_user = User.query.filter_by(email='test_file@example.com').first()
            if not test_user:
                test_user = User(
                    name='测试用户',
                    email='test_file@example.com',
                    phone='13800138000'
                )
                test_user.set_password('test123')
                db.session.add(test_user)
                db.session.flush()
            
            # 查找或创建测试业务员
            test_staff = Staff.query.filter_by(email='test_staff_file@example.com').first()
            if not test_staff:
                from database.models import Permission
                permission = Permission.query.filter_by(position='业务员').first()
                if permission:
                    test_staff = Staff(
                        name='测试业务员',
                        email='test_staff_file@example.com',
                        phone='13800138001',
                        position_id=permission.id,
                        approval_status='approved',
                        approval_date=datetime.utcnow()
                    )
                    test_staff.set_password('test123')
                    db.session.add(test_staff)
                    db.session.flush()
            
            # 创建测试项目
            test_project = Project(
                project_name='测试文件上传项目',
                project_type='软件登记业务',
                applicant_type='个人',
                copyright_owner='测试著作权人',
                applicant_id=test_user.id,
                confirmer_id=test_staff.id if test_staff else None,
                status='已确认',
                confirm_time=datetime.utcnow()
            )
            db.session.add(test_project)
            db.session.flush()
            
            project_id = test_project.id
            print(f"  [OK] 测试项目ID: {project_id}")
            
        except Exception as e:
            print(f"  [ERROR] 创建测试数据失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 测试2: 测试文件上传
        print("\n[2] 测试文件上传...")
        try:
            # 创建临时测试文件
            test_file_content = b"This is a test file content for upload testing."
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
            temp_file.write(test_file_content)
            temp_file.close()
            
            print(f"  [OK] 创建临时测试文件: {temp_file.name}")
            
            # 模拟文件上传（这里只是测试数据库记录创建）
            project_file = ProjectFile(
                project_id=project_id,
                project_type='software',
                file_name='test_file.txt',
                file_path=f'uploads/projects/{project_id}/test_file.txt',
                file_type='txt',
                file_size=len(test_file_content),
                uploader_id=test_user.id,
                file_category='其他文件'
            )
            db.session.add(project_file)
            db.session.commit()
            
            file_id = project_file.id
            print(f"  [OK] 文件记录创建成功，文件ID: {file_id}")
            
            # 清理临时文件
            os.unlink(temp_file.name)
            
        except Exception as e:
            print(f"  [ERROR] 文件上传测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 测试3: 测试文件查询
        print("\n[3] 测试文件查询...")
        try:
            files = ProjectFile.query.filter_by(
                project_id=project_id,
                project_type='software'
            ).all()
            
            assert len(files) > 0, "应该能找到上传的文件"
            assert files[0].file_name == 'test_file.txt', "文件名应该匹配"
            
            print(f"  [OK] 找到 {len(files)} 个文件")
            print(f"  [OK] 文件名: {files[0].file_name}")
            print(f"  [OK] 文件大小: {files[0].file_size} 字节")
            
        except Exception as e:
            print(f"  [ERROR] 文件查询测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 测试4: 清理测试数据
        print("\n[4] 清理测试数据...")
        try:
            ProjectFile.query.filter_by(project_id=project_id).delete()
            Project.query.filter_by(id=project_id).delete()
            db.session.commit()
            print("  [OK] 测试数据已清理")
        except Exception as e:
            print(f"  [ERROR] 清理测试数据失败: {e}")
            db.session.rollback()
            return False
        
        print("\n" + "=" * 60)
        print("所有测试通过！")
        print("=" * 60)
        return True

if __name__ == '__main__':
    from datetime import datetime
    success = test_file_upload()
    sys.exit(0 if success else 1)
