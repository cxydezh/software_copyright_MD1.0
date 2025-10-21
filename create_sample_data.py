#!/usr/bin/env python3
"""
创建示例数据和账号
"""

import os
import sys
from datetime import datetime, timedelta
import random

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import db, User, Staff, Project, Message, ProcessLog, PaperProject, PatentProject
from config.config import config
from flask import Flask
from werkzeug.security import generate_password_hash

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    app.config.from_object(config['development'])
    db.init_app(app)
    return app

def create_sample_data():
    """创建示例数据"""
    app = create_app()
    
    with app.app_context():
        # 创建示例用户
        users = [
            {
                'name': '张三',
                'email': 'zhangsan@example.com',
                'phone': '13800138001',
                'password': '123456'
            },
            {
                'name': '李四',
                'email': 'lisi@example.com',
                'phone': '13800138002',
                'password': '123456'
            },
            {
                'name': '王五',
                'email': 'wangwu@example.com',
                'phone': '13800138003',
                'password': '123456'
            }
        ]
        
        created_users = []
        for user_data in users:
            # 检查用户是否已存在
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if existing_user:
                print(f"用户 {user_data['email']} 已存在，跳过创建")
                created_users.append(existing_user)
                continue
                
            user = User(
                name=user_data['name'],
                email=user_data['email'],
                phone=user_data['phone'],
                password_hash=generate_password_hash(user_data['password'])
            )
            db.session.add(user)
            created_users.append(user)
        
        # 创建示例员工
        staff_members = [
            {
                'name': '业务员小王',
                'email': 'staff1@yiqichuang.com',
                'phone': '13800138010',
                'password': '123456',
                'position_name': '普通业务员'
            },
            {
                'name': '执行者小李',
                'email': 'staff2@yiqichuang.com',
                'phone': '13800138011',
                'password': '123456',
                'position_name': '项目执行者'
            },
            {
                'name': '管理员小张',
                'email': 'admin@yiqichuang.com',
                'phone': '13800138012',
                'password': '123456',
                'position_name': '系统管理员'
            }
        ]
        
        created_staff = []
        for staff_data in staff_members:
            # 检查员工是否已存在
            existing_staff = Staff.query.filter_by(email=staff_data['email']).first()
            if existing_staff:
                print(f"员工 {staff_data['email']} 已存在，跳过创建")
                created_staff.append(existing_staff)
                continue
                
            staff = Staff(
                name=staff_data['name'],
                email=staff_data['email'],
                phone=staff_data['phone'],
                password_hash=generate_password_hash(staff_data['password']),
                approval_status='approved'
            )
            db.session.add(staff)
            created_staff.append(staff)
        
        db.session.commit()
        
        # 创建示例项目
        project_types = ['软件登记业务', '软件设计与登记业务', '软件部署与登记业务']
        applicant_types = ['个人', '事业单位', '事业单位联合个人', '自然人联合']
        priorities = ['普通', '加急', '快速']
        statuses = ['待确认', '已确认', '已立项', '执行中', '已完成', '已上传', '已获取流水号', '证书完成']
        
        projects = []
        for i in range(10):
            project = Project(
                project_name=f'示例软件项目{i+1}',
                project_type=random.choice(project_types),
                applicant_type=random.choice(applicant_types),
                copyright_owner=f'著作权人{i+1}',
                software_applicant_name=f'申请人{i+1}',
                priority=random.choice(priorities),
                status=random.choice(statuses),
                price=random.randint(1000, 10000),
                discount=random.randint(0, 20),
                applicant_id=random.choice(created_users).id,
                confirmer_id=created_staff[0].id if random.random() > 0.3 else None,
                executor_id=created_staff[1].id if random.random() > 0.5 else None,
                remarks=f'这是示例项目{i+1}的备注信息'
            )
            db.session.add(project)
            projects.append(project)
        
        db.session.commit()
        
        # 创建示例论文项目
        paper_types = ['论文指导', '论文发表', '学术咨询']
        service_levels = ['基础服务', '标准服务', '高级服务']
        paper_statuses = ['初稿', '修改中', '已投稿', '审稿中', '已录用', '已发表']
        
        for i in range(5):
            paper = PaperProject(
                project_name=f'示例论文项目{i+1}',
                project_type=random.choice(paper_types),
                service_level=random.choice(service_levels),
                applicant_type='个人学者',
                research_field='医疗技术',
                target_journal='医学期刊',
                paper_status=random.choice(paper_statuses),
                price=random.randint(2000, 8000),
                discount=random.randint(0, 15),
                applicant_id=random.choice(created_users).id,
                confirmer_id=created_staff[0].id if random.random() > 0.3 else None,
                executor_id=created_staff[1].id if random.random() > 0.5 else None,
                remarks=f'这是示例论文项目{i+1}的备注信息'
            )
            db.session.add(paper)
        
        # 创建示例专利项目
        patent_types = ['发明专利申请', '实用新型申请', '外观设计申请']
        application_fields = ['医疗设备', '生物医药', '数字医疗']
        patent_statuses = ['申请中', '公开', '实审', '授权', '维持']
        
        for i in range(5):
            patent = PatentProject(
                project_name=f'示例专利项目{i+1}',
                project_type=random.choice(patent_types),
                applicant_type='企业申请',
                application_field=random.choice(application_fields),
                invention_title=f'医疗设备发明{i+1}',
                technical_field='医疗器械',
                patent_status=random.choice(patent_statuses),
                price=random.randint(3000, 12000),
                discount=random.randint(0, 25),
                applicant_id=random.choice(created_users).id,
                confirmer_id=created_staff[0].id if random.random() > 0.3 else None,
                executor_id=created_staff[1].id if random.random() > 0.5 else None,
                remarks=f'这是示例专利项目{i+1}的备注信息'
            )
            db.session.add(patent)
        
        db.session.commit()
        
        # 创建示例留言
        for i in range(8):
            message = Message(
                content=f'这是示例留言{i+1}，用户询问关于软件著作权登记的相关问题。',
                user_id=random.choice(created_users).id,
                create_time=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            db.session.add(message)
        
        db.session.commit()
        
        print("示例数据创建完成！")
        print("\n创建的示例账号：")
        print("普通用户：")
        for user in created_users:
            print(f"  邮箱: {user.email}, 密码: 123456")
        
        print("\n员工账号：")
        for staff in created_staff:
            print(f"  邮箱: {staff.email}, 密码: 123456, 职位: {staff.position}")
        
        print(f"\n创建了 {len(projects)} 个软件项目")
        print(f"创建了 5 个论文项目")
        print(f"创建了 5 个专利项目")
        print(f"创建了 8 条留言记录")

if __name__ == '__main__':
    create_sample_data()
