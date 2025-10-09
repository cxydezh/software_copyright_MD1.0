#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速验证 recurrent_copy_time 修复
"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import LOCAL_CONFIG
from desktop_app.local_models import LocalDatabase, ContractFile


def quick_verify():
    """快速验证合同文件的更新"""
    print("\n快速验证 recurrent_copy_time 字段更新...")
    
    db_path = LOCAL_CONFIG['LOCAL_DB_PATH']
    db = LocalDatabase(db_path)
    contract_file = ContractFile(db)
    
    # 获取所有文件
    files = contract_file.get_all_files()
    
    if not files:
        print("[!] 数据库中没有合同文件记录，无法测试")
        return
    
    # 选择第一个文件
    file = files[0]
    file_id = file[0]
    file_name = file[1]
    
    print(f"\n测试文件: ID={file_id}, 名称={file_name}")
    print(f"表字段数: {len(file)}")
    print(f"字段内容: {file}")
    
    # 更新前的值
    old_time = file[8] if len(file) > 8 else None
    print(f"\n更新前 recurrent_copy_time (索引8): {old_time}")
    
    # 执行更新
    new_time = datetime.now().isoformat()
    print(f"准备更新为: {new_time}")
    
    contract_file.update_file(file_id, recurrent_copy_time=new_time)
    
    # 读取更新后的值
    updated_file = contract_file.get_file_by_id(file_id)
    print(f"\n更新后字段数: {len(updated_file)}")
    print(f"更新后字段内容: {updated_file}")
    
    updated_time = updated_file[8] if len(updated_file) > 8 else None
    print(f"更新后 recurrent_copy_time (索引8): {updated_time}")
    
    # 验证
    if updated_time == new_time:
        print("\n[OK] 更新成功！")
        return True
    else:
        print(f"\n[X] 更新失败！")
        print(f"    期望: {new_time}")
        print(f"    实际: {updated_time}")
        return False


if __name__ == '__main__':
    try:
        success = quick_verify()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[X] 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

