#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地数据库迁移脚本
用于在不删除数据的情况下更新表结构
"""

import sqlite3
import os
import shutil
from datetime import datetime
from config.config import LOCAL_CONFIG


def backup_database(db_path):
    """备份数据库"""
    if os.path.exists(db_path):
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_path, backup_path)
        print(f"[OK] 数据库已备份到: {backup_path}")
        return backup_path
    return None


def check_column_exists(cursor, table_name, column_name):
    """检查列是否存在"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    return column_name in columns


def add_column_if_not_exists(cursor, table_name, column_name, column_type, default_value=None):
    """如果列不存在则添加"""
    if not check_column_exists(cursor, table_name, column_name):
        default_clause = f" DEFAULT {default_value}" if default_value else ""
        sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}{default_clause}"
        cursor.execute(sql)
        print(f"  [+] 添加列: {table_name}.{column_name}")
        return True
    else:
        print(f"  [-] 列已存在: {table_name}.{column_name}")
        return False


def migrate_database(db_path):
    """迁移数据库"""
    print(f"\n开始迁移数据库: {db_path}\n")
    
    if not os.path.exists(db_path):
        print("[X] 数据库文件不存在，无需迁移")
        return False
    
    # 备份数据库
    backup_path = backup_database(db_path)
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 1. 更新 default_paths 表
        print("\n[1] 检查 default_paths 表...")
        add_column_if_not_exists(cursor, 'default_paths', 'recurrent_copy_time', 'TEXT')
        
        # 2. 更新 id_card_files 表
        print("\n[2] 检查 id_card_files 表...")
        add_column_if_not_exists(cursor, 'id_card_files', 'recurrent_copy_time', 'TEXT')
        
        # 3. 更新 usccc_files 表
        print("\n[3] 检查 usccc_files 表...")
        add_column_if_not_exists(cursor, 'usccc_files', 'recurrent_copy_time', 'TEXT')
        
        # 4. 更新 contract_files 表
        print("\n[4] 检查 contract_files 表...")
        add_column_if_not_exists(cursor, 'contract_files', 'recurrent_copy_time', 'TEXT')
        
        # 5. 更新 template_folders 表
        print("\n[5] 检查 template_folders 表...")
        add_column_if_not_exists(cursor, 'template_folders', 'recurrent_copy_time', 'TEXT')
        
        # 6. 更新 project_files 表
        print("\n[6] 检查 project_files 表...")
        add_column_if_not_exists(cursor, 'project_files', 'file_size', 'INTEGER', '0')
        add_column_if_not_exists(cursor, 'project_files', 'recurrent_copy_time', 'TEXT')
        
        # 7. 更新 local_projects 表
        print("\n[7] 检查 local_projects 表...")
        add_column_if_not_exists(cursor, 'local_projects', 'recurrent_copy_time', 'TEXT')
        
        conn.commit()
        print("\n[OK] 数据库迁移完成！\n")
        return True
        
    except Exception as e:
        print(f"\n[X] 迁移失败: {e}")
        if backup_path and os.path.exists(backup_path):
            print(f"正在恢复备份...")
            shutil.copy2(backup_path, db_path)
            print(f"[OK] 已从备份恢复数据库")
        return False
        
    finally:
        conn.close()


def recreate_database(db_path):
    """重新创建数据库（会删除所有数据）"""
    print(f"\n警告：将删除现有数据库并重新创建！")
    print(f"数据库路径: {db_path}\n")
    
    response = input("确认要继续吗？(输入 yes 确认): ")
    if response.lower() != 'yes':
        print("操作已取消")
        return False
    
    # 备份现有数据库
    backup_path = backup_database(db_path)
    
    # 删除现有数据库
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"[OK] 已删除旧数据库")
    
    # 导入并重新初始化数据库
    from desktop_app.local_models import LocalDatabase
    db = LocalDatabase(db_path)
    print(f"[OK] 已重新创建数据库\n")
    
    return True


if __name__ == '__main__':
    import sys
    
    db_path = LOCAL_CONFIG['LOCAL_DB_PATH']
    
    print("=" * 60)
    print("本地数据库迁移工具")
    print("=" * 60)
    print(f"\n数据库路径: {db_path}")
    print("\n请选择操作:")
    print("  1. 迁移数据库（保留数据，仅更新表结构）")
    print("  2. 重新创建数据库（删除所有数据）")
    print("  0. 退出")
    
    choice = input("\n请输入选项 (0/1/2): ").strip()
    
    if choice == '1':
        migrate_database(db_path)
    elif choice == '2':
        recreate_database(db_path)
    elif choice == '0':
        print("已退出")
    else:
        print("无效的选项")

