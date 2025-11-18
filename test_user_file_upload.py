#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试用户申请项目时的文件上传功能
"""
import sys
import os
import tempfile

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from database.models import db, Project, ProjectFile, User
from werkzeug.security import generate_password_hash
from datetime import datetime

def test_user_file_upload():
    """测试用户申请项目时的文件上传功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("开始测试用户申请项目文件上传功能")
        print("=" * 60)
        
        # 创建测试用户
        print("\n[1] 创建测试用户...")
        try:
            # 清理测试数据
            test_user = User.query.filter_by(email='test_file_user@example.com').first()
            if test_user:
                # 删除相关项目
                projects = Project.query.filter_by(applicant_id=test_user.id).all()
                for p in projects:
                    ProjectFile.query.filter_by(project_id=p.id).delete()
                    db.session.delete(p)
                db.session.delete(test_user)
                db.session.commit()
            
            # 创建新测试用户
            test_user = User(
                name='测试文件用户',
                email='test_file_user@example.com',
                phone='13800138000'
            )
            test_user.set_password('test123')
            db.session.add(test_user)
            db.session.flush()
            user_id = test_user.id
            print(f"  [OK] 测试用户ID: {user_id}")
            
        except Exception as e:
            print(f"  [ERROR] 创建测试用户失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 测试2: 创建测试项目
        print("\n[2] 创建测试项目...")
        try:
            test_project = Project(
                project_name='测试文件上传项目',
                project_type='软件登记业务',
                applicant_type='个人',
                copyright_owner='测试著作权人',
                applicant_id=user_id,
                status='待确认'
            )
            db.session.add(test_project)
            db.session.flush()
            project_id = test_project.id
            print(f"  [OK] 测试项目ID: {project_id}")
            
        except Exception as e:
            print(f"  [ERROR] 创建测试项目失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 测试3: 测试文件记录创建
        print("\n[3] 测试文件记录创建...")
        try:
            # 创建临时测试文件
            test_file_content = b"This is a test file for user project upload."
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
            temp_file.write(test_file_content)
            temp_file.close()
            
            # 创建文件记录
            project_file = ProjectFile(
                project_id=project_id,
                project_type='software',
                file_name='test_user_file.txt',
                file_path=f'uploads/projects/{project_id}/test_user_file.txt',
                file_type='txt',
                file_size=len(test_file_content),
                uploader_id=user_id,
                file_category='申请材料'
            )
            db.session.add(project_file)
            db.session.commit()
            
            file_id = project_file.id
            print(f"  [OK] 文件记录创建成功，文件ID: {file_id}")
            
            # 清理临时文件
            os.unlink(temp_file.name)
            
        except Exception as e:
            print(f"  [ERROR] 文件记录创建失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 测试4: 测试文件查询
        print("\n[4] 测试文件查询...")
        try:
            files = ProjectFile.query.filter_by(
                project_id=project_id,
                project_type='software'
            ).all()
            
            assert len(files) > 0, "应该能找到上传的文件"
            assert files[0].file_name == 'test_user_file.txt', "文件名应该匹配"
            assert files[0].uploader_id == user_id, "上传者ID应该匹配"
            
            print(f"  [OK] 找到 {len(files)} 个文件")
            print(f"  [OK] 文件名: {files[0].file_name}")
            print(f"  [OK] 上传者ID: {files[0].uploader_id}")
            print(f"  [OK] 文件大小: {files[0].file_size} 字节")
            
        except Exception as e:
            print(f"  [ERROR] 文件查询测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # 测试5: 清理测试数据
        print("\n[5] 清理测试数据...")
        try:
            ProjectFile.query.filter_by(project_id=project_id).delete()
            Project.query.filter_by(id=project_id).delete()
            User.query.filter_by(id=user_id).delete()
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
    success = test_user_file_upload()
    sys.exit(0 if success else 1)
