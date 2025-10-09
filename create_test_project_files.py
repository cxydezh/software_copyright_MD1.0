#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试项目文件
用于测试任务视图中的文件列表显示功能
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import LOCAL_CONFIG


def create_test_project_folder():
    """创建测试项目文件夹和文件"""
    
    # 获取项目基础路径
    base_path = LOCAL_CONFIG.get('PROJECT_FILE_DIR', 'D:/SoftwareCopyrightMS/Projects')
    
    # 创建测试项目文件夹（假设项目ID=1）
    test_project_folder = os.path.join(base_path, "1.测试项目")
    
    print(f"创建测试项目文件夹: {test_project_folder}")
    
    # 创建主文件夹
    os.makedirs(test_project_folder, exist_ok=True)
    
    # 创建子文件夹
    subdirs = ['源代码', '文档', '测试数据']
    for subdir in subdirs:
        subdir_path = os.path.join(test_project_folder, subdir)
        os.makedirs(subdir_path, exist_ok=True)
        print(f"  创建子文件夹: {subdir}")
    
    # 创建测试文件
    test_files = [
        ('README.txt', '这是一个测试项目\n用于验证文件列表功能'),
        ('源代码/main.py', '# 主程序文件\nprint("Hello, World!")'),
        ('源代码/utils.py', '# 工具函数\ndef helper():\n    pass'),
        ('文档/需求文档.txt', '项目需求说明文档'),
        ('文档/设计文档.txt', '项目设计说明文档'),
        ('测试数据/test1.txt', '测试数据1'),
        ('测试数据/test2.txt', '测试数据2'),
    ]
    
    for rel_path, content in test_files:
        file_path = os.path.join(test_project_folder, rel_path)
        
        # 确保父目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  创建文件: {rel_path}")
    
    print(f"\n✓ 测试项目文件夹创建完成！")
    print(f"  路径: {test_project_folder}")
    print(f"  文件数: {len(test_files)}")
    print(f"\n现在可以运行桌面应用，选择项目ID=1的项目查看文件列表")
    
    return test_project_folder


if __name__ == '__main__':
    try:
        folder = create_test_project_folder()
        print(f"\n提示: 在桌面应用中选择 ID=1 的项目，查看中间的文件列表")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()


