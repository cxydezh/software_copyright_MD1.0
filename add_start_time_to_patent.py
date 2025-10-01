#!/usr/bin/env python3
"""
为PatentProject表添加start_time字段
"""

import os
import sys
import pymysql

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def add_start_time_field():
    """为PatentProject表添加start_time字段"""
    print("=" * 60)
    print("为PatentProject表添加start_time字段")
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
        
        # 检查字段是否已存在
        cursor.execute("DESCRIBE patent_projects")
        columns = [row[0] for row in cursor.fetchall()]
        print(f"[INFO] 当前patent_projects表字段: {columns}")
        
        if 'start_time' in columns:
            print("[INFO] start_time字段已存在，跳过添加")
        else:
            # 添加start_time字段
            cursor.execute("ALTER TABLE patent_projects ADD COLUMN start_time DATETIME COMMENT '开始时间'")
            print("[SUCCESS] 添加start_time字段")
        
        connection.commit()
        print("[SUCCESS] 数据库更新完成")
        return True
        
    except Exception as e:
        print(f"[ERROR] 添加字段失败: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()

def main():
    """主函数"""
    success = add_start_time_field()
    
    if success:
        print("\n" + "=" * 60)
        print("[SUCCESS] PatentProject表start_time字段添加完成！")
        print("=" * 60)
    else:
        print("\n[ERROR] 添加字段失败，请检查日志")

if __name__ == '__main__':
    main()
