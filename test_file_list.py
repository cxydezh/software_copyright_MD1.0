#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件列表加载功能
"""

import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import LOCAL_CONFIG


def test_file_list():
    """测试文件列表功能"""
    
    print("\n" + "=" * 60)
    print("测试项目文件列表加载功能")
    print("=" * 60)
    
    # 获取项目基础路径
    base_path = LOCAL_CONFIG.get('PROJECT_FILE_DIR', 'D:/SoftwareCopyrightMS/Projects')
    print(f"\n项目基础路径: {base_path}")
    
    # 测试项目文件夹
    project_id = 1
    project_name = "测试项目"
    project_folder = os.path.join(base_path, f"{project_id}.{project_name}")
    
    print(f"测试项目文件夹: {project_folder}")
    
    if not os.path.exists(project_folder):
        print(f"\n[X] 项目文件夹不存在")
        print(f"请先运行: python create_test_project_files.py")
        return False
    
    print(f"[OK] 项目文件夹存在")
    
    # 遍历文件
    print(f"\n文件列表:")
    print("-" * 60)
    
    file_count = 0
    for root, dirs, files in os.walk(project_folder):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            
            # 获取文件信息
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_name)[1].lower()
            
            # 获取修改时间
            mtime = os.path.getmtime(file_path)
            time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            # 计算相对路径
            rel_path = os.path.relpath(file_path, project_folder)
            
            # 格式化文件大小
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size / 1024:.1f} KB"
            else:
                size_str = f"{file_size / (1024 * 1024):.1f} MB"
            
            print(f"{file_count+1}. {rel_path}")
            print(f"   类型: {file_ext or '无扩展名'}")
            print(f"   大小: {size_str}")
            print(f"   时间: {time_str}")
            print()
            
            file_count += 1
    
    print("-" * 60)
    print(f"\n总计: {file_count} 个文件")
    
    if file_count > 0:
        print("\n[OK] 文件列表功能测试通过！")
        return True
    else:
        print("\n[X] 未找到任何文件")
        return False


if __name__ == '__main__':
    try:
        success = test_file_list()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[X] 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


