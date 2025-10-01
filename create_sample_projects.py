#!/usr/bin/env python3
"""
批量新增示例项目数据脚本

为每一项业务新增至少 N 条项目数据：
- 软件项目（Project）：N 条
- 论文项目（PaperProject）：N 条
- 专利项目（PatentProject）：N 条

使用方法（在项目根目录执行）：
  python create_sample_projects.py --count 20 --env development

注意：脚本具备幂等性，会尽量避免重复插入（基于生成的项目名检查）。
"""

import os
import sys
import random
from datetime import datetime, timedelta
import argparse

# 将项目根路径加入 sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from database.models import db, User, Staff, Project, PaperProject, PatentProject, Permission


def get_or_create_default_user() -> User:
    """获取一个可用的普通用户，若不存在则创建一个。"""
    user = User.query.first()
    if user:
        return user

    user = User(
        name='示例用户',
        email='sample_user@example.com',
        password_hash='',
        email_verified=True,
        user_category='综合服务',
        organization='示例机构',
        research_field='信息技术'
    )
    db.session.add(user)
    db.session.commit()
    return user


def get_or_create_executor(position_name: str = '项目执行者') -> Staff:
    """获取一个可用的执行者员工，若不存在则创建一个。"""
    staff = Staff.query.first()
    if staff:
        return staff

    # 确保存在对应权限
    perm = Permission.query.filter_by(position=position_name).first()
    if not perm:
        perm = Permission(position=position_name, can_execute=True)
        db.session.add(perm)
        db.session.commit()

    staff = Staff(
        name='示例执行者',
        email='executor@example.com',
        password_hash='',
        position_id=perm.id,
        expertise_area='软件工程',
        service_types='软件登记,论文指导,专利申请',
        email_verified=True
    )
    db.session.add(staff)
    db.session.commit()
    return staff


def ensure_history_time(offset_days: int) -> datetime:
    return datetime.utcnow() - timedelta(days=offset_days)


def seed_software_projects(n: int) -> int:
    """新增软件项目（Project） n 条。"""
    applicant = get_or_create_default_user()
    executor = get_or_create_executor()

    project_types = ['软件登记业务', '软件设计与登记业务', '软件部署与登记业务']
    applicant_types = ['个人', '事业单位', '事业单位联合个人', '自然人联合']
    priorities = ['普通', '加急', '快速']
    statuses = ['待确认', '已确认', '已立项', '执行中', '已完成', '已上传', '已获取流水号']

    created = 0
    for i in range(n):
        ptype = random.choice(project_types)
        aname = f"示例软件项目-{ptype}-{i+1:02d}"

        # 幂等：若名称已存在则跳过
        if Project.query.filter_by(project_name=aname).first():
            continue

        project = Project(
            project_name=aname,
            project_type=ptype,
            applicant_type=random.choice(applicant_types),
            copyright_owner='示例著作权人',
            software_applicant_name=applicant.name,
            priority=random.choice(priorities),
            status=random.choice(statuses),
            applicant_id=applicant.id,
            confirmer_id=None,
            executor_id=executor.id,
            remarks='批量新增示例数据'
        )

        # 设置时间轨迹（可选）
        project.apply_time = ensure_history_time(random.randint(5, 60))
        db.session.add(project)
        created += 1

    db.session.commit()
    return created


def seed_paper_projects(n: int) -> int:
    """新增论文项目（PaperProject） n 条。"""
    applicant = get_or_create_default_user()
    executor = get_or_create_executor()

    project_types = ['论文指导', '论文发表', '学术咨询']
    service_levels = ['基础服务', '标准服务', '高级服务']
    applicant_types = ['个人学者', '医疗机构', '企业研发', '联合申请']
    paper_statuses = ['初稿', '修改中', '已投稿', '审稿中', '已录用', '已发表', '被拒稿']
    statuses = ['待确认', '已确认', '进行中', '已投稿', '审稿中', '已录用', '已发表', '已完成']

    created = 0
    for i in range(n):
        ptype = random.choice(project_types)
        slevel = random.choice(service_levels)
        pname = f"示例论文项目-{ptype}-{slevel}-{i+1:02d}"

        if PaperProject.query.filter_by(project_name=pname).first():
            continue

        paper = PaperProject(
            project_name=pname,
            project_type=ptype,
            service_level=slevel,
            applicant_type=random.choice(applicant_types),
            paper_title=f"关于医疗信息化的研究-{i+1:02d}",
            research_field='医疗信息学',
            target_journal='中国医疗期刊',
            paper_status=random.choice(paper_statuses),
            price=random.randint(3000, 12000),
            discount=0,
            status=random.choice(statuses),
            applicant_id=applicant.id,
            confirmer_id=None,
            executor_id=executor.id,
            remarks='批量新增示例数据'
        )
        paper.apply_time = ensure_history_time(random.randint(5, 60))
        db.session.add(paper)
        created += 1

    db.session.commit()
    return created


def seed_patent_projects(n: int) -> int:
    """新增专利项目（PatentProject） n 条。"""
    applicant = get_or_create_default_user()
    executor = get_or_create_executor()

    project_types = ['发明专利申请', '实用新型申请', '外观设计申请', '国际申请', '专利保护', '专利管理']
    applicant_types = ['个人发明者', '企业申请', '科研院所', '联合申请']
    app_fields = ['医疗设备', '生物医药', '数字医疗', '其他领域']
    patent_statuses = ['申请中', '公开', '实审', '授权', '维持', '终止', '无效']
    statuses = ['待确认', '已确认', '准备中', '已递交', '审查中', '已授权', '维持中', '已完成']

    created = 0
    for i in range(n):
        ptype = random.choice(project_types)
        pname = f"示例专利项目-{ptype}-{i+1:02d}"

        if PatentProject.query.filter_by(project_name=pname).first():
            continue

        patent = PatentProject(
            project_name=pname,
            project_type=ptype,
            applicant_type=random.choice(applicant_types),
            application_field=random.choice(app_fields),
            invention_title=f"一种医疗器械创新方案-{i+1:02d}",
            technical_field='医疗器械',
            application_number=None,
            publication_number=None,
            patent_number=None,
            patent_status=random.choice(patent_statuses),
            price=random.randint(5000, 20000),
            discount=0,
            annual_fee=None,
            status=random.choice(statuses),
            applicant_id=applicant.id,
            confirmer_id=None,
            executor_id=executor.id,
            remarks='批量新增示例数据'
        )
        patent.apply_time = ensure_history_time(random.randint(5, 90))
        db.session.add(patent)
        created += 1

    db.session.commit()
    return created


def main():
    parser = argparse.ArgumentParser(description='批量新增示例项目数据脚本')
    parser.add_argument('--count', type=int, default=20, help='每类业务新增的项目数量（默认20）')
    parser.add_argument('--env', type=str, default='development', help='应用配置环境（默认development）')
    args = parser.parse_args()

    app = create_app(args.env)
    with app.app_context():
        # 确保数据库连接正常
        db.session.execute(db.text('SELECT 1'))

        software_added = seed_software_projects(args.count)
        paper_added = seed_paper_projects(args.count)
        patent_added = seed_patent_projects(args.count)

        print('=' * 60)
        print(f'[RESULT] 新增 软件项目: {software_added} 条')
        print(f'[RESULT] 新增 论文项目: {paper_added} 条')
        print(f'[RESULT] 新增 专利项目: {patent_added} 条')
        print('=' * 60)


if __name__ == '__main__':
    main()



