#!/usr/bin/env python3
"""
扩展权限系统和添加测试用户
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from database.models import db, Staff, User, Permission
from werkzeug.security import generate_password_hash

def check_permissions():
    """检查权限系统"""
    print("=" * 60)
    print("检查权限系统")
    print("=" * 60)
    
    app = create_app('development')
    with app.app_context():
        try:
            from database.models import Permission
            permissions = Permission.query.all()
            print(f"[INFO] 当前权限记录数量: {len(permissions)}")
            for perm in permissions:
                print(f"  - {perm.position}: 确认={perm.can_confirm}, 执行={perm.can_execute}, 管理={perm.can_manage}")
            return True
            
        except Exception as e:
            print(f"[ERROR] 检查权限系统失败: {e}")
            return False

def create_test_users():
    """创建测试用户"""
    print("\n" + "=" * 60)
    print("创建测试用户")
    print("=" * 60)
    
    app = create_app('development')
    with app.app_context():
        try:
            # 测试员工用户
            test_staff = [
                {
                    'name': '论文编辑员',
                    'email': 'paper_editor@yiqichuang.com',
                    'password': 'paper123',
                    'position': '论文编辑',
                    'expertise_area': '医学论文写作与发表',
                    'service_types': '论文指导,论文发表,学术咨询'
                },
                {
                    'name': '专利编辑员',
                    'email': 'patent_editor@yiqichuang.com',
                    'password': 'patent123',
                    'position': '专利编辑',
                    'expertise_area': '医疗器械专利撰写与申请',
                    'service_types': '发明专利申请,实用新型申请,专利保护'
                },
                {
                    'name': '专家用户',
                    'email': 'expert@yiqichuang.com',
                    'password': 'expert123',
                    'position': '专家',
                    'expertise_area': '医疗知识产权综合服务',
                    'service_types': '论文指导,专利申请,软件著作权,综合服务'
                },
                {
                    'name': '业务经理',
                    'email': 'manager@yiqichuang.com',
                    'password': 'manager123',
                    'position': '普通业务员',
                    'expertise_area': '业务管理与客户服务',
                    'service_types': '客户服务,项目管理'
                },
                {
                    'name': '项目执行者',
                    'email': 'executor@yiqichuang.com',
                    'password': 'executor123',
                    'position': '项目执行者',
                    'expertise_area': '软件开发与实施',
                    'service_types': '软件开发,系统实施'
                }
            ]
            
            # 测试普通用户
            test_users = [
                {
                    'name': '测试用户1',
                    'email': 'user1@example.com',
                    'password': 'user123',
                    'user_category': '论文指导',
                    'organization': '郑州大学第一附属医院',
                    'research_field': '心血管医学'
                },
                {
                    'name': '测试用户2',
                    'email': 'user2@example.com',
                    'password': 'user123',
                    'user_category': '专利申请',
                    'organization': '河南省人民医院',
                    'research_field': '医疗器械研发'
                },
                {
                    'name': '测试用户3',
                    'email': 'user3@example.com',
                    'password': 'user123',
                    'user_category': '综合服务',
                    'organization': '郑州大学',
                    'research_field': '生物医学工程'
                }
            ]
            
            # 创建员工用户
            for staff_data in test_staff:
                # 检查是否已存在
                existing = Staff.query.filter_by(email=staff_data['email']).first()
                if existing:
                    print(f"[WARNING] 员工 {staff_data['email']} 已存在，跳过")
                    continue
                
                # 获取权限ID
                from database.models import Permission
                permission = Permission.query.filter_by(position=staff_data['position']).first()
                if not permission:
                    print(f"[ERROR] 权限 {staff_data['position']} 不存在，跳过员工 {staff_data['name']}")
                    continue
                
                staff = Staff(
                    name=staff_data['name'],
                    email=staff_data['email'],
                    password_hash=generate_password_hash(staff_data['password']),
                    position_id=permission.id,
                    expertise_area=staff_data['expertise_area'],
                    service_types=staff_data['service_types'],
                    email_verified=True
                )
                db.session.add(staff)
                print(f"[SUCCESS] 创建员工: {staff_data['name']} ({staff_data['position']})")
            
            # 创建普通用户
            for user_data in test_users:
                # 检查是否已存在
                existing = User.query.filter_by(email=user_data['email']).first()
                if existing:
                    print(f"[WARNING] 用户 {user_data['email']} 已存在，跳过")
                    continue
                
                user = User(
                    name=user_data['name'],
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    user_category=user_data['user_category'],
                    organization=user_data['organization'],
                    research_field=user_data['research_field'],
                    email_verified=True
                )
                db.session.add(user)
                print(f"[SUCCESS] 创建用户: {user_data['name']} ({user_data['user_category']})")
            
            db.session.commit()
            print(f"[SUCCESS] 成功创建测试用户")
            return True
            
        except Exception as e:
            print(f"[ERROR] 创建测试用户失败: {e}")
            db.session.rollback()
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("检查权限系统和创建测试用户")
    print("=" * 60)
    
    # 检查权限系统
    success1 = check_permissions()
    
    # 创建测试用户
    success2 = create_test_users()
    
    if success1 and success2:
        print("\n" + "=" * 60)
        print("[SUCCESS] 所有操作完成！")
        print("=" * 60)
        print("权限类型：")
        print("- 普通业务员：可以确认项目，查看所有项目")
        print("- 项目执行者：可以执行项目，查看所有项目")
        print("- 论文编辑：可以确认、执行、编辑论文项目，专家权限")
        print("- 专利编辑：可以确认、执行、编辑专利项目，专家权限")
        print("- 专家：全权限，可以管理所有项目")
        print("- 系统管理员：全权限")
        print("\n新增测试用户：")
        print("员工用户：paper_editor, patent_editor, expert_user, business_manager, executor_user")
        print("普通用户：test_user1, test_user2, test_user3")
        print("\n下一步：运行 python run_web.py 启动Web应用进行测试")
    else:
        print("\n[ERROR] 操作过程中出现错误，请检查日志")

if __name__ == '__main__':
    main()
