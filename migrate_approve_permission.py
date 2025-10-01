"""
数据库迁移脚本：添加立项权限字段 can_approve

执行说明：
1. 备份数据库
2. 运行此脚本：python migrate_approve_permission.py
"""

from web_app.app import create_app
from database.models import db, Permission
from sqlalchemy import text

def migrate_approve_permission():
    """迁移立项权限"""
    app = create_app()
    with app.app_context():
        print("开始迁移立项权限...")
        
        try:
            # 1. 添加 can_approve 列
            with db.engine.connect() as conn:
                try:
                    conn.execute(text('ALTER TABLE permissions ADD COLUMN can_approve BOOLEAN DEFAULT FALSE'))
                    conn.commit()
                    print("✓ 成功添加 can_approve 字段")
                except Exception as e:
                    if "Duplicate column name" in str(e) or "duplicate column name" in str(e).lower():
                        print("✓ can_approve 字段已存在")
                    else:
                        raise
                
                # 2. 根据职位设置默认权限
                print("\n设置默认权限...")
                
                # 系统管理员：拥有所有权限，包括立项
                admin_perms = Permission.query.filter_by(position='系统管理员').all()
                for perm in admin_perms:
                    perm.can_approve = True
                    print(f"  - 系统管理员: 已授予立项权限")
                
                # 普通业务员：可以确认项目，但不能立项
                business_perms = Permission.query.filter_by(position='普通业务员').all()
                for perm in business_perms:
                    perm.can_approve = False  # 普通业务员没有立项权限
                    print(f"  - 普通业务员: 无立项权限（仅能确认项目）")
                
                # 项目执行者：通常不需要立项权限（除非身兼多职）
                executor_perms = Permission.query.filter_by(position='项目执行者').all()
                for perm in executor_perms:
                    perm.can_approve = False  # 默认不给立项权限
                    print(f"  - 项目执行者: 无立项权限（专注执行）")
                
                # 论文编辑、专利编辑：默认不给立项权限
                paper_perms = Permission.query.filter_by(position='论文编辑').all()
                for perm in paper_perms:
                    perm.can_approve = False
                    print(f"  - 论文编辑: 无立项权限")
                
                patent_perms = Permission.query.filter_by(position='专利编辑').all()
                for perm in patent_perms:
                    perm.can_approve = False
                    print(f"  - 专利编辑: 无立项权限")
                
                # 专家：默认不给立项权限
                expert_perms = Permission.query.filter_by(position='专家').all()
                for perm in expert_perms:
                    perm.can_approve = False
                    print(f"  - 专家: 无立项权限")
                
                db.session.commit()
                print("\n✓ 默认权限设置完成")
                
        except Exception as e:
            print(f"✗ 迁移失败: {str(e)}")
            db.session.rollback()
            raise
        
        print("\n✓ 迁移完成！")
        print("\n权限说明：")
        print("=" * 60)
        print("立项权限 (can_approve):")
        print("  ✓ 系统管理员 - 拥有立项权限")
        print("  ✗ 普通业务员 - 无立项权限（仅能确认项目）")
        print("  ✗ 项目执行者 - 无立项权限（专注执行）")
        print("  ✗ 其他角色 - 默认无立项权限")
        print("=" * 60)
        print("\n业务流程：")
        print("1. 用户申请项目 → 待确认")
        print("2. 业务员确认申请 → 已确认")
        print("3. 有立项权限的人员立项 → 已立项（等待执行者接受）")
        print("4. 执行者接受项目 → 执行中")
        print("=" * 60)
        print("\n后续操作：")
        print("1. 如需为某个业务员授予立项权限，请在数据库中手动设置")
        print("   UPDATE permissions SET can_approve = TRUE WHERE position = '普通业务员' AND id = <权限ID>;")
        print("2. 或创建新的职位类型（如'业务主管'）并授予立项权限")
        print("3. 重新登录以使权限生效")

if __name__ == '__main__':
    migrate_approve_permission()

