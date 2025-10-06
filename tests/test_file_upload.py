#!/usr/bin/env python3
"""
文件上传功能测试脚本
"""

import os
import sys
import requests
import tempfile
from io import BytesIO

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_file_upload():
    """测试文件上传功能"""
    print("=" * 60)
    print("文件上传功能测试")
    print("=" * 60)
    
    # 测试配置
    base_url = "http://localhost:5000"
    test_files = [
        {
            'name': 'test_document.pdf',
            'content': b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n174\n%%EOF',
            'type': 'application/pdf'
        },
        {
            'name': 'test_image.jpg',
            'content': b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9',
            'type': 'image/jpeg'
        },
        {
            'name': 'test_document.txt',
            'content': b'This is a test document for file upload testing.\nIt contains multiple lines of text.\nTesting file upload functionality.',
            'type': 'text/plain'
        }
    ]
    
    # 测试登录
    print("\n1. 测试用户登录...")
    login_data = {
        'email': 'test@example.com',
        'password': 'test123',
        'user_type': 'user'
    }
    
    session = requests.Session()
    login_response = session.post(f"{base_url}/auth/login", data=login_data)
    
    if login_response.status_code == 200:
        print("✓ 用户登录成功")
    else:
        print("✗ 用户登录失败，尝试注册测试用户...")
        # 注册测试用户
        register_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'test123',
            'confirm_password': 'test123',
            'phone': '13800138000',
            'address': 'Test Address'
        }
        register_response = session.post(f"{base_url}/auth/register", data=register_data)
        if register_response.status_code == 200:
            print("✓ 测试用户注册成功")
        else:
            print("✗ 测试用户注册失败")
            return
    
    # 测试创建论文项目
    print("\n2. 测试创建论文项目...")
    paper_data = {
        'project_name': '文件上传测试项目',
        'project_type': '论文指导',
        'service_level': '基础服务',
        'applicant_type': '个人学者',
        'paper_title': '测试论文标题',
        'research_field': '计算机科学',
        'target_journal': '测试期刊',
        'remarks': '这是一个用于测试文件上传功能的项目'
    }
    
    paper_response = session.post(f"{base_url}/paper/apply", data=paper_data)
    if paper_response.status_code == 200:
        print("✓ 论文项目创建成功")
        # 从响应中提取项目ID（这里需要根据实际实现调整）
        paper_id = 1  # 假设项目ID为1
    else:
        print("✗ 论文项目创建失败")
        return
    
    # 测试文件上传
    print("\n3. 测试文件上传...")
    for i, test_file in enumerate(test_files, 1):
        print(f"\n3.{i} 测试上传 {test_file['name']}...")
        
        files = {
            'file': (test_file['name'], BytesIO(test_file['content']), test_file['type'])
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
                print(f"✓ {test_file['name']} 上传成功")
                print(f"  文件ID: {result['file']['id']}")
                print(f"  文件大小: {result['file']['size']} bytes")
            else:
                print(f"✗ {test_file['name']} 上传失败: {result.get('message', '未知错误')}")
        else:
            print(f"✗ {test_file['name']} 上传失败: HTTP {upload_response.status_code}")
    
    # 测试文件下载
    print("\n4. 测试文件下载...")
    download_response = session.get(f"{base_url}/api/paper/{paper_id}/file/1/download")
    if download_response.status_code == 200:
        print("✓ 文件下载成功")
        print(f"  下载文件大小: {len(download_response.content)} bytes")
    else:
        print("✗ 文件下载失败")
    
    # 测试文件预览
    print("\n5. 测试文件预览...")
    preview_response = session.get(f"{base_url}/api/paper/{paper_id}/file/1/preview")
    if preview_response.status_code == 200:
        print("✓ 文件预览成功")
    else:
        print("✗ 文件预览失败")
    
    # 测试文件删除
    print("\n6. 测试文件删除...")
    delete_response = session.post(f"{base_url}/api/paper/{paper_id}/file/1/delete")
    if delete_response.status_code == 200:
        result = delete_response.json()
        if result.get('success'):
            print("✓ 文件删除成功")
        else:
            print(f"✗ 文件删除失败: {result.get('message', '未知错误')}")
    else:
        print("✗ 文件删除失败")
    
    print("\n" + "=" * 60)
    print("文件上传功能测试完成")
    print("=" * 60)

def test_patent_file_upload():
    """测试专利项目文件上传功能"""
    print("\n" + "=" * 60)
    print("专利项目文件上传功能测试")
    print("=" * 60)
    
    # 类似的测试逻辑，但针对专利项目
    # 这里可以添加专利项目的文件上传测试
    print("专利项目文件上传测试功能待实现...")

if __name__ == '__main__':
    try:
        test_file_upload()
        test_patent_file_upload()
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
