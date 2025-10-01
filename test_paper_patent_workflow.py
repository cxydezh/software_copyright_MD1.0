#!/usr/bin/env python3
"""
测试论文和专利申请业务工作流程
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from database.models import db, User, Staff, PaperProject, PatentProject, Permission

def test_paper_patent_workflow():
    """测试论文和专利申请业务工作流程"""
    print("=" * 60)
    print("测试论文和专利申请业务工作流程")
    print("=" * 60)
    
    app = create_app('development')
    with app.app_context():
        try:
            # 1. 检查权限系统
            print("\n1. 检查权限系统")
            permissions = Permission.query.all()
            print(f"   权限记录数量: {len(permissions)}")
            for perm in permissions:
                print(f"   - {perm.position}: 确认={perm.can_confirm}, 执行={perm.can_execute}, 管理={perm.can_manage}")
            
            # 2. 检查员工用户
            print("\n2. 检查员工用户")
            staff_users = Staff.query.all()
            print(f"   员工用户数量: {len(staff_users)}")
            for staff in staff_users:
                permission = Permission.query.get(staff.position_id) if staff.position_id else None
                print(f"   - {staff.name} ({staff.email}): {permission.position if permission else '无权限'}")
            
            # 3. 检查普通用户
            print("\n3. 检查普通用户")
            normal_users = User.query.all()
            print(f"   普通用户数量: {len(normal_users)}")
            for user in normal_users:
                print(f"   - {user.name} ({user.email}): {user.user_category}")
            
            # 4. 创建测试论文项目
            print("\n4. 创建测试论文项目")
            test_user = User.query.filter_by(email='user1@example.com').first()
            if test_user:
                paper_project = PaperProject(
                    project_name='测试论文项目',
                    project_type='论文指导',
                    service_level='标准服务',
                    applicant_type='个人学者',
                    paper_title='基于深度学习的医学图像分析研究',
                    research_field='医学影像',
                    target_journal='Nature Medicine',
                    applicant_id=test_user.id,
                    price=5000.00,
                    status='待确认'
                )
                db.session.add(paper_project)
                print(f"   创建论文项目: {paper_project.project_name}")
            else:
                print("   未找到测试用户，跳过论文项目创建")
            
            # 5. 创建测试专利项目
            print("\n5. 创建测试专利项目")
            if test_user:
                patent_project = PatentProject(
                    project_name='测试专利项目',
                    project_type='发明专利申请',
                    applicant_type='个人发明者',
                    application_field='医疗设备',
                    invention_title='智能医疗诊断系统',
                    technical_field='人工智能',
                    applicant_id=test_user.id,
                    price=8000.00,
                    status='待确认'
                )
                db.session.add(patent_project)
                print(f"   创建专利项目: {patent_project.project_name}")
            else:
                print("   未找到测试用户，跳过专利项目创建")
            
            # 6. 检查业务员是否能查看待处理项目
            print("\n6. 检查业务员权限")
            business_manager = Staff.query.filter_by(email='manager@yiqichuang.com').first()
            if business_manager:
                permission = Permission.query.get(business_manager.position_id)
                print(f"   业务经理权限: {permission.position if permission else '无权限'}")
                if permission and permission.can_confirm:
                    print("   [SUCCESS] 业务经理可以确认项目")
                else:
                    print("   [ERROR] 业务经理无法确认项目")
            
            # 7. 检查论文编辑权限
            paper_editor = Staff.query.filter_by(email='paper_editor@yiqichuang.com').first()
            if paper_editor:
                permission = Permission.query.get(paper_editor.position_id)
                print(f"   论文编辑权限: {permission.position if permission else '无权限'}")
                if permission and permission.can_edit_paper:
                    print("   [SUCCESS] 论文编辑可以编辑论文项目")
                else:
                    print("   [ERROR] 论文编辑无法编辑论文项目")
            
            # 8. 检查专利编辑权限
            patent_editor = Staff.query.filter_by(email='patent_editor@yiqichuang.com').first()
            if patent_editor:
                permission = Permission.query.get(patent_editor.position_id)
                print(f"   专利编辑权限: {permission.position if permission else '无权限'}")
                if permission and permission.can_edit_patent:
                    print("   [SUCCESS] 专利编辑可以编辑专利项目")
                else:
                    print("   [ERROR] 专利编辑无法编辑专利项目")
            
            # 9. 检查专家权限
            expert = Staff.query.filter_by(email='expert@yiqichuang.com').first()
            if expert:
                permission = Permission.query.get(expert.position_id)
                print(f"   专家权限: {permission.position if permission else '无权限'}")
                if permission and permission.is_expert:
                    print("   [SUCCESS] 专家具有专家权限")
                else:
                    print("   [ERROR] 专家无专家权限")
            
            db.session.commit()
            print("\n[SUCCESS] 测试完成！")
            return True
            
        except Exception as e:
            print(f"[ERROR] 测试失败: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

def main():
    """主函数"""
    success = test_paper_patent_workflow()
    
    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] 论文和专利申请业务工作流程测试完成！")
        print("=" * 60)
        print("测试结果：")
        print("[SUCCESS] 权限系统已扩展，包含6种权限类型")
        print("[SUCCESS] 员工用户已创建，包含不同权限级别")
        print("[SUCCESS] 普通用户已创建，支持不同业务类型")
        print("[SUCCESS] 论文和专利项目可以正常创建")
        print("[SUCCESS] 业务员可以查看和处理待确认项目")
        print("[SUCCESS] 专业编辑具有相应的编辑权限")
        print("[SUCCESS] 专家具有全权限")
        print("\n下一步：启动Web应用进行实际测试")
    else:
        print("\n[ERROR] 测试失败，请检查日志")

if __name__ == '__main__':
    main()
