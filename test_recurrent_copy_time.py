#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 recurrent_copy_time 字段更新功能
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import LOCAL_CONFIG
from desktop_app.local_models import (LocalDatabase, TemplateFolder, IDCardFile,
                                      USCCCFile, ContractFile)


def test_template_update():
    """测试模板文件夹的recurrent_copy_time更新"""
    print("\n=== 测试模板文件夹 recurrent_copy_time 更新 ===")
    
    db_path = LOCAL_CONFIG['LOCAL_DB_PATH']
    db = LocalDatabase(db_path)
    template_folder = TemplateFolder(db)
    
    # 获取所有模板
    templates = template_folder.get_all_folders()
    
    if not templates:
        print("[X] 没有找到模板记录")
        return False
    
    # 选择第一个模板
    template = templates[0]
    template_id = template[0]
    template_name = template[1]
    old_time = template[10] if len(template) > 10 else None
    
    print(f"[*] 模板ID: {template_id}")
    print(f"[*] 模板名称: {template_name}")
    print(f"[*] 更新前 recurrent_copy_time: {old_time}")
    
    # 更新 recurrent_copy_time
    new_time = datetime.now().isoformat()
    print(f"[*] 更新为: {new_time}")
    
    template_folder.update_folder(template_id, recurrent_copy_time=new_time)
    
    # 验证更新
    updated_template = template_folder.get_folder_by_id(template_id)
    updated_time = updated_template[10] if len(updated_template) > 10 else None
    
    print(f"[*] 更新后 recurrent_copy_time: {updated_time}")
    
    if updated_time == new_time:
        print("[OK] 模板 recurrent_copy_time 更新成功！\n")
        return True
    else:
        print(f"[X] 模板 recurrent_copy_time 更新失败！期望: {new_time}, 实际: {updated_time}\n")
        return False


def test_idcard_update():
    """测试身份证文件的recurrent_copy_time更新"""
    print("=== 测试身份证文件 recurrent_copy_time 更新 ===")
    
    db_path = LOCAL_CONFIG['LOCAL_DB_PATH']
    db = LocalDatabase(db_path)
    id_card_file = IDCardFile(db)
    
    files = id_card_file.get_all_files()
    
    if not files:
        print("[X] 没有找到身份证文件记录")
        return False
    
    file = files[0]
    file_id = file[0]
    file_name = file[1]
    old_time = file[10] if len(file) > 10 else None
    
    print(f"[*] 文件ID: {file_id}")
    print(f"[*] 文件名称: {file_name}")
    print(f"[*] 更新前 recurrent_copy_time: {old_time}")
    
    new_time = datetime.now().isoformat()
    print(f"[*] 更新为: {new_time}")
    
    id_card_file.update_file(file_id, recurrent_copy_time=new_time)
    
    updated_file = id_card_file.get_file_by_id(file_id)
    updated_time = updated_file[10] if len(updated_file) > 10 else None
    
    print(f"[*] 更新后 recurrent_copy_time: {updated_time}")
    
    if updated_time == new_time:
        print("[OK] 身份证文件 recurrent_copy_time 更新成功！\n")
        return True
    else:
        print(f"[X] 身份证文件 recurrent_copy_time 更新失败！期望: {new_time}, 实际: {updated_time}\n")
        return False


def test_usccc_update():
    """测试统一社会信用代码证书的recurrent_copy_time更新"""
    print("=== 测试统一社会信用代码证书 recurrent_copy_time 更新 ===")
    
    db_path = LOCAL_CONFIG['LOCAL_DB_PATH']
    db = LocalDatabase(db_path)
    usccc_file = USCCCFile(db)
    
    files = usccc_file.get_all_files()
    
    if not files:
        print("[X] 没有找到证书文件记录")
        return False
    
    file = files[0]
    file_id = file[0]
    file_name = file[1]
    old_time = file[9] if len(file) > 9 else None
    
    print(f"[*] 文件ID: {file_id}")
    print(f"[*] 文件名称: {file_name}")
    print(f"[*] 更新前 recurrent_copy_time: {old_time}")
    
    new_time = datetime.now().isoformat()
    print(f"[*] 更新为: {new_time}")
    
    usccc_file.update_file(file_id, recurrent_copy_time=new_time)
    
    updated_file = usccc_file.get_file_by_id(file_id)
    updated_time = updated_file[9] if len(updated_file) > 9 else None
    
    print(f"[*] 更新后 recurrent_copy_time: {updated_time}")
    
    if updated_time == new_time:
        print("[OK] 证书文件 recurrent_copy_time 更新成功！\n")
        return True
    else:
        print(f"[X] 证书文件 recurrent_copy_time 更新失败！期望: {new_time}, 实际: {updated_time}\n")
        return False


def test_contract_update():
    """测试合同文件的recurrent_copy_time更新"""
    print("=== 测试合同文件 recurrent_copy_time 更新 ===")
    
    db_path = LOCAL_CONFIG['LOCAL_DB_PATH']
    db = LocalDatabase(db_path)
    contract_file = ContractFile(db)
    
    files = contract_file.get_all_files()
    
    if not files:
        print("[X] 没有找到合同文件记录")
        return False
    
    file = files[0]
    file_id = file[0]
    file_name = file[1]
    old_time = file[8] if len(file) > 8 else None
    
    print(f"[*] 文件ID: {file_id}")
    print(f"[*] 文件名称: {file_name}")
    print(f"[*] 更新前 recurrent_copy_time: {old_time}")
    
    new_time = datetime.now().isoformat()
    print(f"[*] 更新为: {new_time}")
    
    contract_file.update_file(file_id, recurrent_copy_time=new_time)
    
    updated_file = contract_file.get_file_by_id(file_id)
    updated_time = updated_file[8] if len(updated_file) > 8 else None
    
    print(f"[*] 更新后 recurrent_copy_time: {updated_time}")
    
    if updated_time == new_time:
        print("[OK] 合同文件 recurrent_copy_time 更新成功！\n")
        return True
    else:
        print(f"[X] 合同文件 recurrent_copy_time 更新失败！期望: {new_time}, 实际: {updated_time}\n")
        return False


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("recurrent_copy_time 字段更新测试")
    print("=" * 60)
    
    results = []
    
    # 测试所有类型
    results.append(("模板文件夹", test_template_update()))
    results.append(("身份证文件", test_idcard_update()))
    results.append(("证书文件", test_usccc_update()))
    results.append(("合同文件", test_contract_update()))
    
    # 总结
    print("=" * 60)
    print("测试总结:")
    print("=" * 60)
    
    for name, result in results:
        status = "[OK] 通过" if result else "[X] 失败"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print("\n[OK] 所有测试通过！")
        sys.exit(0)
    else:
        print("\n[X] 部分测试失败！")
        sys.exit(1)


