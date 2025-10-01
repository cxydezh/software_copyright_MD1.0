#!/usr/bin/env python3
"""
更新permissions表结构
"""

import os
import sys
import pymysql

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def update_permissions_table():
    """更新permissions表结构"""
    print("=" * 60)
    print("更新permissions表结构")
    print("=" * 60)
    
    # 获取数据库密码
    db_password = os.environ.get('DB_PASSWORD')
    if not db_password:
        print("[ERROR] 请设置环境变量 DB_PASSWORD")
        return False
    
    try:
        # 连接数据库
        connection = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='webuser',
            password=db_password,
            database='software_copyright',
            charset='utf8mb4'
        )
        
        cursor = connection.cursor()
        print("[SUCCESS] 成功连接数据库")
        
        # 检查表结构
        cursor.execute("DESCRIBE permissions")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"[INFO] 当前permissions表字段: {columns}")
        
        # 添加新字段（如果不存在）
        new_columns = [
            ('can_confirm', 'BOOLEAN DEFAULT FALSE COMMENT "确认项目权限"'),
            ('can_execute', 'BOOLEAN DEFAULT FALSE COMMENT "执行任务权限"'),
            ('can_manage', 'BOOLEAN DEFAULT FALSE COMMENT "管理权限"'),
            ('can_view_all', 'BOOLEAN DEFAULT FALSE COMMENT "查看所有项目权限"'),
            ('can_edit_paper', 'BOOLEAN DEFAULT FALSE COMMENT "编辑论文项目权限"'),
            ('can_edit_patent', 'BOOLEAN DEFAULT FALSE COMMENT "编辑专利项目权限"'),
            ('is_expert', 'BOOLEAN DEFAULT FALSE COMMENT "专家权限"')
        ]
        
        for column_name, column_def in new_columns:
            if column_name not in columns:
                sql = f"ALTER TABLE permissions ADD COLUMN {column_name} {column_def}"
                cursor.execute(sql)
                print(f"[SUCCESS] 添加字段: {column_name}")
            else:
                print(f"[INFO] 字段已存在: {column_name}")
        
        # 更新position枚举类型
        print("[INFO] 更新position枚举类型...")
        cursor.execute("""
            ALTER TABLE permissions MODIFY COLUMN position 
            ENUM('普通业务员', '项目执行者', '论文编辑', '专利编辑', '专家', '系统管理员') 
            NOT NULL COMMENT '职务'
        """)
        print("[SUCCESS] 更新position枚举类型")
        
        # 删除现有权限记录
        cursor.execute("DELETE FROM permissions")
        print("[INFO] 删除现有权限记录")
        
        # 插入新的权限记录
        permissions_data = [
            ('普通业务员', True, False, False, True, False, False, False, False, False),
            ('项目执行者', False, True, False, True, False, False, False, True, False),
            ('论文编辑', True, True, False, True, True, False, True, True, False),
            ('专利编辑', True, True, False, True, False, True, True, True, False),
            ('专家', True, True, True, True, True, True, True, True, True),
            ('系统管理员', True, True, True, True, True, True, True, True, True)
        ]
        
        insert_sql = """
            INSERT INTO permissions 
            (position, can_confirm, can_execute, can_manage, can_view_all, 
             can_edit_paper, can_edit_patent, is_expert, execute_permission, update_serial_permission) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        for perm_data in permissions_data:
            cursor.execute(insert_sql, perm_data)
            print(f"[SUCCESS] 插入权限: {perm_data[0]}")
        
        connection.commit()
        print(f"[SUCCESS] 成功更新permissions表")
        return True
        
    except Exception as e:
        print(f"[ERROR] 更新permissions表失败: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def main():
    """主函数"""
    success = update_permissions_table()
    
    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] permissions表更新完成！")
        print("=" * 60)
        print("新增权限类型：")
        print("- 普通业务员：可以确认项目，查看所有项目")
        print("- 项目执行者：可以执行项目，查看所有项目")
        print("- 论文编辑：可以确认、执行、编辑论文项目，专家权限")
        print("- 专利编辑：可以确认、执行、编辑专利项目，专家权限")
        print("- 专家：全权限，可以管理所有项目")
        print("- 系统管理员：全权限")
    else:
        print("\n[ERROR] permissions表更新失败，请检查日志")

if __name__ == '__main__':
    main()
