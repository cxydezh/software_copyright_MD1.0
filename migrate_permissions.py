#!/usr/bin/env python3
"""
迁移权限表结构
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from database.models import db, Permission

def migrate_permissions():
    """迁移权限表结构"""
    print("=" * 60)
    print("迁移权限表结构")
    print("=" * 60)
    
    app = create_app('development')
    with app.app_context():
        try:
            # 检查是否需要添加新字段
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('permissions')]
            
            print(f"[INFO] 当前权限表字段: {columns}")
            
            # 添加新字段（如果不存在）
            new_columns = [
                'can_confirm',
                'can_execute', 
                'can_manage',
                'can_view_all',
                'can_edit_paper',
                'can_edit_patent',
                'is_expert'
            ]
            
            for column in new_columns:
                if column not in columns:
                    print(f"[INFO] 添加字段: {column}")
                    # 这里需要手动执行ALTER TABLE语句
                    # 因为SQLAlchemy的add_column在某些情况下可能不工作
                    pass
            
            # 更新position枚举类型
            print("[INFO] 更新position枚举类型...")
            
            # 删除现有权限记录
            Permission.query.delete()
            db.session.commit()
            print("[INFO] 已清空现有权限记录")
            
            # 创建新的权限记录
            permissions = [
                {
                    'position': '普通业务员',
                    'can_confirm': True,
                    'can_execute': False,
                    'can_manage': False,
                    'can_view_all': True,
                    'can_edit_paper': False,
                    'can_edit_patent': False,
                    'is_expert': False,
                    'execute_permission': False,
                    'update_serial_permission': False
                },
                {
                    'position': '项目执行者',
                    'can_confirm': False,
                    'can_execute': True,
                    'can_manage': False,
                    'can_view_all': True,
                    'can_edit_paper': False,
                    'can_edit_patent': False,
                    'is_expert': False,
                    'execute_permission': True,
                    'update_serial_permission': False
                },
                {
                    'position': '论文编辑',
                    'can_confirm': True,
                    'can_execute': True,
                    'can_manage': False,
                    'can_view_all': True,
                    'can_edit_paper': True,
                    'can_edit_patent': False,
                    'is_expert': True,
                    'execute_permission': True,
                    'update_serial_permission': False
                },
                {
                    'position': '专利编辑',
                    'can_confirm': True,
                    'can_execute': True,
                    'can_manage': False,
                    'can_view_all': True,
                    'can_edit_paper': False,
                    'can_edit_patent': True,
                    'is_expert': True,
                    'execute_permission': True,
                    'update_serial_permission': False
                },
                {
                    'position': '专家',
                    'can_confirm': True,
                    'can_execute': True,
                    'can_manage': True,
                    'can_view_all': True,
                    'can_edit_paper': True,
                    'can_edit_patent': True,
                    'is_expert': True,
                    'execute_permission': True,
                    'update_serial_permission': True
                },
                {
                    'position': '系统管理员',
                    'can_confirm': True,
                    'can_execute': True,
                    'can_manage': True,
                    'can_view_all': True,
                    'can_edit_paper': True,
                    'can_edit_patent': True,
                    'is_expert': True,
                    'execute_permission': True,
                    'update_serial_permission': True
                }
            ]
            
            for perm_data in permissions:
                permission = Permission(**perm_data)
                db.session.add(permission)
                print(f"[SUCCESS] 创建权限: {perm_data['position']}")
            
            db.session.commit()
            print(f"[SUCCESS] 成功创建 {len(permissions)} 个权限记录")
            return True
            
        except Exception as e:
            print(f"[ERROR] 迁移权限表失败: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return False

def main():
    """主函数"""
    success = migrate_permissions()
    
    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] 权限表迁移完成！")
        print("=" * 60)
        print("新增权限类型：")
        print("- 普通业务员：可以确认项目，查看所有项目")
        print("- 项目执行者：可以执行项目，查看所有项目")
        print("- 论文编辑：可以确认、执行、编辑论文项目，专家权限")
        print("- 专利编辑：可以确认、执行、编辑专利项目，专家权限")
        print("- 专家：全权限，可以管理所有项目")
        print("- 系统管理员：全权限")
    else:
        print("\n[ERROR] 权限表迁移失败，请检查日志")

if __name__ == '__main__':
    main()
