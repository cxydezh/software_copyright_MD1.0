#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本 - 更新外键级联关系
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_app.app import create_app
from database.models import db

def migrate_foreign_keys():
    """更新外键级联关系"""
    app = create_app()
    
    with app.app_context():
        try:
            print("开始更新外键级联关系...")
            
            with db.engine.connect() as conn:
                # 1. 更新Staff表的approver_id外键
                print("更新Staff表的approver_id外键...")
                try:
                    # 删除旧的外键约束
                    conn.execute(db.text("ALTER TABLE staff DROP FOREIGN KEY staff_ibfk_2"))
                except Exception as e:
                    print(f"删除旧约束时出错（可能不存在）: {e}")
                
                # 添加新的外键约束
                conn.execute(db.text("""
                    ALTER TABLE staff 
                    ADD CONSTRAINT staff_approver_fk 
                    FOREIGN KEY (approver_id) REFERENCES staff(id) 
                    ON DELETE SET NULL
                """))
                print("[OK] Staff表approver_id外键已更新")
                
                # 2. 更新Message表的外键
                print("更新Message表的外键...")
                try:
                    # 删除旧的外键约束
                    conn.execute(db.text("ALTER TABLE messages DROP FOREIGN KEY messages_ibfk_1"))
                    conn.execute(db.text("ALTER TABLE messages DROP FOREIGN KEY messages_ibfk_2"))
                    conn.execute(db.text("ALTER TABLE messages DROP FOREIGN KEY messages_ibfk_3"))
                except Exception as e:
                    print(f"删除旧约束时出错（可能不存在）: {e}")
                
                # 添加新的外键约束
                conn.execute(db.text("""
                    ALTER TABLE messages 
                    ADD CONSTRAINT messages_user_fk 
                    FOREIGN KEY (user_id) REFERENCES users(id) 
                    ON DELETE CASCADE
                """))
                
                conn.execute(db.text("""
                    ALTER TABLE messages 
                    ADD CONSTRAINT messages_staff_fk 
                    FOREIGN KEY (staff_id) REFERENCES staff(id) 
                    ON DELETE CASCADE
                """))
                
                conn.execute(db.text("""
                    ALTER TABLE messages 
                    ADD CONSTRAINT messages_project_fk 
                    FOREIGN KEY (project_id) REFERENCES projects(id) 
                    ON DELETE CASCADE
                """))
                print("[OK] Message表外键已更新")
                
                # 3. 更新Project表的外键
                print("更新Project表的外键...")
                try:
                    # 删除旧的外键约束
                    conn.execute(db.text("ALTER TABLE projects DROP FOREIGN KEY projects_ibfk_1"))
                    conn.execute(db.text("ALTER TABLE projects DROP FOREIGN KEY projects_ibfk_2"))
                    conn.execute(db.text("ALTER TABLE projects DROP FOREIGN KEY projects_ibfk_3"))
                except Exception as e:
                    print(f"删除旧约束时出错（可能不存在）: {e}")
                
                # 添加新的外键约束
                conn.execute(db.text("""
                    ALTER TABLE projects 
                    ADD CONSTRAINT projects_applicant_fk 
                    FOREIGN KEY (applicant_id) REFERENCES users(id) 
                    ON DELETE CASCADE
                """))
                
                conn.execute(db.text("""
                    ALTER TABLE projects 
                    ADD CONSTRAINT projects_confirmer_fk 
                    FOREIGN KEY (confirmer_id) REFERENCES staff(id) 
                    ON DELETE SET NULL
                """))
                
                conn.execute(db.text("""
                    ALTER TABLE projects 
                    ADD CONSTRAINT projects_executor_fk 
                    FOREIGN KEY (executor_id) REFERENCES staff(id) 
                    ON DELETE SET NULL
                """))
                print("[OK] Project表外键已更新")
                
                # 4. 更新PaperProject表的外键
                print("更新PaperProject表的外键...")
                try:
                    # 删除旧的外键约束
                    conn.execute(db.text("ALTER TABLE paper_projects DROP FOREIGN KEY paper_projects_ibfk_1"))
                    conn.execute(db.text("ALTER TABLE paper_projects DROP FOREIGN KEY paper_projects_ibfk_2"))
                    conn.execute(db.text("ALTER TABLE paper_projects DROP FOREIGN KEY paper_projects_ibfk_3"))
                except Exception as e:
                    print(f"删除旧约束时出错（可能不存在）: {e}")
                
                # 添加新的外键约束
                conn.execute(db.text("""
                    ALTER TABLE paper_projects 
                    ADD CONSTRAINT paper_projects_applicant_fk 
                    FOREIGN KEY (applicant_id) REFERENCES users(id) 
                    ON DELETE CASCADE
                """))
                
                conn.execute(db.text("""
                    ALTER TABLE paper_projects 
                    ADD CONSTRAINT paper_projects_confirmer_fk 
                    FOREIGN KEY (confirmer_id) REFERENCES staff(id) 
                    ON DELETE SET NULL
                """))
                
                conn.execute(db.text("""
                    ALTER TABLE paper_projects 
                    ADD CONSTRAINT paper_projects_executor_fk 
                    FOREIGN KEY (executor_id) REFERENCES staff(id) 
                    ON DELETE SET NULL
                """))
                print("[OK] PaperProject表外键已更新")
                
                # 5. 更新PatentProject表的外键
                print("更新PatentProject表的外键...")
                try:
                    # 删除旧的外键约束
                    conn.execute(db.text("ALTER TABLE patent_projects DROP FOREIGN KEY patent_projects_ibfk_1"))
                    conn.execute(db.text("ALTER TABLE patent_projects DROP FOREIGN KEY patent_projects_ibfk_2"))
                    conn.execute(db.text("ALTER TABLE patent_projects DROP FOREIGN KEY patent_projects_ibfk_3"))
                except Exception as e:
                    print(f"删除旧约束时出错（可能不存在）: {e}")
                
                # 添加新的外键约束
                conn.execute(db.text("""
                    ALTER TABLE patent_projects 
                    ADD CONSTRAINT patent_projects_applicant_fk 
                    FOREIGN KEY (applicant_id) REFERENCES users(id) 
                    ON DELETE CASCADE
                """))
                
                conn.execute(db.text("""
                    ALTER TABLE patent_projects 
                    ADD CONSTRAINT patent_projects_confirmer_fk 
                    FOREIGN KEY (confirmer_id) REFERENCES staff(id) 
                    ON DELETE SET NULL
                """))
                
                conn.execute(db.text("""
                    ALTER TABLE patent_projects 
                    ADD CONSTRAINT patent_projects_executor_fk 
                    FOREIGN KEY (executor_id) REFERENCES staff(id) 
                    ON DELETE SET NULL
                """))
                print("[OK] PatentProject表外键已更新")
                
                # 6. 更新ProjectFile表的外键
                print("更新ProjectFile表的外键...")
                try:
                    # 删除旧的外键约束
                    conn.execute(db.text("ALTER TABLE project_files DROP FOREIGN KEY project_files_ibfk_1"))
                except Exception as e:
                    print(f"删除旧约束时出错（可能不存在）: {e}")
                
                # 添加新的外键约束
                conn.execute(db.text("""
                    ALTER TABLE project_files 
                    ADD CONSTRAINT project_files_uploader_fk 
                    FOREIGN KEY (uploader_id) REFERENCES users(id) 
                    ON DELETE CASCADE
                """))
                print("[OK] ProjectFile表外键已更新")
                
                conn.commit()
                print("[OK] 所有外键级联关系更新完成！")
                
        except Exception as e:
            print(f"[ERROR] 外键更新失败: {e}")
            db.session.rollback()
            raise

def check_foreign_keys():
    """检查外键约束"""
    app = create_app()
    
    with app.app_context():
        try:
            print("检查外键约束...")
            
            with db.engine.connect() as conn:
                # 查询所有外键约束
                result = conn.execute(db.text("""
                    SELECT 
                        TABLE_NAME,
                        COLUMN_NAME,
                        CONSTRAINT_NAME,
                        REFERENCED_TABLE_NAME,
                        REFERENCED_COLUMN_NAME,
                        DELETE_RULE
                    FROM information_schema.KEY_COLUMN_USAGE 
                    WHERE REFERENCED_TABLE_NAME IS NOT NULL 
                    AND TABLE_SCHEMA = DATABASE()
                    ORDER BY TABLE_NAME, COLUMN_NAME
                """))
                
                foreign_keys = result.fetchall()
                
                print(f"找到 {len(foreign_keys)} 个外键约束:")
                for fk in foreign_keys:
                    print(f"  {fk[0]}.{fk[1]} -> {fk[3]}.{fk[4]} ({fk[5]})")
                
                return True
                
        except Exception as e:
            print(f"[ERROR] 检查外键失败: {e}")
            return False

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='更新外键级联关系')
    parser.add_argument('--check', action='store_true', help='仅检查外键约束')
    parser.add_argument('--migrate', action='store_true', help='执行迁移')
    
    args = parser.parse_args()
    
    if args.check:
        check_foreign_keys()
    elif args.migrate:
        migrate_foreign_keys()
    else:
        # 默认执行迁移
        migrate_foreign_keys()
        print("\n" + "="*50)
        check_foreign_keys()

