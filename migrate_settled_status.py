"""
数据库迁移脚本：将"已结清"从status状态转换为独立的is_settled字段

执行说明：
1. 备份数据库
2. 运行此脚本：python migrate_settled_status.py
"""

from web_app.app import create_app
from database.models import db, Project, PaperProject, PatentProject
from sqlalchemy import text

def migrate_settled_status():
    """迁移结清状态"""
    app = create_app()
    with app.app_context():
        print("开始迁移结清状态...")
        
        # 1. 检查是否需要添加is_settled列
        try:
            # 尝试添加is_settled列
            with db.engine.connect() as conn:
                # 添加is_settled列
                try:
                    conn.execute(text('ALTER TABLE projects ADD COLUMN is_settled BOOLEAN DEFAULT FALSE'))
                    conn.commit()
                    print("✓ 成功添加is_settled字段")
                except Exception as e:
                    if "Duplicate column name" in str(e) or "duplicate column name" in str(e).lower():
                        print("✓ is_settled字段已存在")
                    else:
                        raise
                
                # 2. 将status为"已结清"的项目设置is_settled=True
                # 注意：需要根据实际情况决定这些项目应该变成什么状态
                projects_to_migrate = Project.query.filter_by(status='已结清').all()
                
                if projects_to_migrate:
                    print(f"\n找到 {len(projects_to_migrate)} 个状态为'已结清'的项目")
                    for project in projects_to_migrate:
                        project.is_settled = True
                        # 将这些项目的状态改为"证书完成"（因为通常结清发生在证书完成之后）
                        project.status = '证书完成'
                        print(f"  - 项目 {project.id}: {project.project_name} -> is_settled=True, status='证书完成'")
                    
                    db.session.commit()
                    print("✓ 成功迁移所有'已结清'状态的项目")
                else:
                    print("✓ 没有需要迁移的项目")
                
                # 3. 修改status字段的枚举类型（移除'已结清'）
                # 注意：不同数据库系统的ALTER ENUM语法不同
                # SQLite不支持ALTER ENUM，需要重建表
                # MySQL/PostgreSQL有不同的语法
                
                print("\n注意：需要手动更新status字段的枚举定义")
                print("对于SQLite，需要删除旧数据库并重新init")
                print("对于MySQL，运行以下SQL（需要根据实际情况调整）：")
                print("  ALTER TABLE projects MODIFY COLUMN status ENUM('待确认', '已确认', '已立项', '执行中', '已完成', '已上传', '已获取流水号', '证书完成', '已归档') DEFAULT '待确认';")
                
                # 4. 为论文项目表添加字段
                try:
                    conn.execute(text('ALTER TABLE paper_projects ADD COLUMN is_settled BOOLEAN DEFAULT FALSE'))
                    conn.execute(text('ALTER TABLE paper_projects ADD COLUMN settle_time DATETIME'))
                    conn.commit()
                    print("\n✓ 成功为论文项目表添加is_settled和settle_time字段")
                except Exception as e:
                    if "Duplicate column name" in str(e) or "duplicate column name" in str(e).lower():
                        print("\n✓ 论文项目表字段已存在")
                    else:
                        raise
                
                # 5. 为专利项目表添加字段
                try:
                    conn.execute(text('ALTER TABLE patent_projects ADD COLUMN is_settled BOOLEAN DEFAULT FALSE'))
                    conn.execute(text('ALTER TABLE patent_projects ADD COLUMN settle_time DATETIME'))
                    conn.commit()
                    print("✓ 成功为专利项目表添加is_settled和settle_time字段")
                except Exception as e:
                    if "Duplicate column name" in str(e) or "duplicate column name" in str(e).lower():
                        print("✓ 专利项目表字段已存在")
                    else:
                        raise
                
        except Exception as e:
            print(f"✗ 迁移失败: {str(e)}")
            db.session.rollback()
            raise
        
        print("\n✓ 迁移完成！")
        print("\n后续步骤：")
        print("1. 检查所有项目的状态是否正确")
        print("2. 测试结清功能")
        print("3. 测试归档功能（归档前必须已结清）")

if __name__ == '__main__':
    migrate_settled_status()

