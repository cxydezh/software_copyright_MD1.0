#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试桌面应用程序登录功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from desktop_app.server_client import ServerClient

def test_login():
    """测试登录功能"""
    print("=" * 60)
    print("测试桌面应用程序登录功能")
    print("=" * 60)
    
    # 创建服务器客户端
    client = ServerClient('http://localhost', 5000)
    
    # 测试登录
    print("正在测试登录...")
    success, message, user_data = client.login(
        email='admin@yiqichuang.com',
        password='admin123',
        user_type='staff'
    )
    
    if success:
        print(f"[SUCCESS] 登录成功: {message}")
        print(f"用户信息: {user_data}")
    else:
        print(f"[ERROR] 登录失败: {message}")
    
    print("=" * 60)

if __name__ == '__main__':
    test_login()
