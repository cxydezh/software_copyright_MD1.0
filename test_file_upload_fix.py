#!/usr/bin/env python3
"""
测试文件上传修复
"""

import os
import sys
import requests
from io import BytesIO

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_file_upload_fix():
    """测试文件上传修复"""
    print("=" * 60)
    print("测试文件上传修复")
    print("=" * 60)
    
    base_url = "http://localhost:5000"
    
    # 测试不同的文件名情况
    test_cases = [
        {
            'name': 'normal_file.txt',
            'content': b'Normal file content',
            'expected': 'success'
        },
        {
            'name': 'no_extension',
            'content': b'File without extension',
            'expected': 'fail'
        },
        {
            'name': '',
            'content': b'Empty filename',
            'expected': 'fail'
        },
        {
            'name': 'file.with.multiple.dots.txt',
            'content': b'File with multiple dots',
            'expected': 'success'
        },
        {
            'name': '.hidden_file',
            'content': b'Hidden file',
            'expected': 'fail'
        }
    ]
    
    # 登录获取session
    session = requests.Session()
    login_data = {
        'email': 'admin@yiqichuang.com',
        'password': 'admin123',
        'user_type': 'staff'
    }
    
    login_response = session.post(f"{base_url}/auth/login", data=login_data)
    if login_response.status_code != 200:
        print("登录失败")
        return
    
    print("✓ 登录成功")
    
    # 创建测试项目
    paper_data = {
        'project_name': '文件上传测试项目',
        'project_type': '论文指导',
        'service_level': '基础服务',
        'applicant_type': '个人学者',
        'paper_title': '测试论文标题',
        'research_field': '计算机科学',
        'target_journal': '测试期刊',
        'remarks': '这是一个用于测试文件上传修复的项目'
    }
    
    paper_response = session.post(f"{base_url}/paper/apply", data=paper_data)
    if paper_response.status_code == 200:
        print("✓ 论文项目创建成功")
        # 假设项目ID为1，实际应该从响应中获取
        paper_id = 1
    else:
        print("✗ 论文项目创建失败")
        return
    
    # 测试文件上传
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. 测试文件: {test_case['name']}")
        
        files = {
            'file': (test_case['name'], BytesIO(test_case['content']), 'text/plain')
        }
        data = {
            'file_category': '申请材料'
        }
        
        upload_response = session.post(
            f"{base_url}/api/paper/{paper_id}/upload",
            files=files,
            data=data
        )
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            if result.get('success'):
                print(f"✓ 上传成功: {test_case['name']}")
            else:
                print(f"✗ 上传失败: {result.get('message', '未知错误')}")
        else:
            print(f"✗ 上传失败: HTTP {upload_response.status_code}")
    
    print("\n" + "=" * 60)
    print("文件上传修复测试完成")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_file_upload_fix()
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
