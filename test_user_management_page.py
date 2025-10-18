#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户管理页面访问
"""

import requests
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_user_management_page():
    """测试用户管理页面"""
    try:
        # 首先登录获取session
        session = requests.Session()
        
        # 登录
        login_data = {
            'email': 'admin@yiqichuang.com',
            'password': 'admin123',
            'user_type': 'staff'
        }
        
        login_response = session.post('http://127.0.0.1:5000/auth/login', data=login_data)
        print(f"登录响应状态码: {login_response.status_code}")
        
        if login_response.status_code == 200:
            # 访问用户管理页面
            user_mgmt_response = session.get('http://127.0.0.1:5000/staff/user_management')
            print(f"用户管理页面响应状态码: {user_mgmt_response.status_code}")
            
            if user_mgmt_response.status_code == 200:
                content = user_mgmt_response.text
                
                # 检查是否包含待审核员工账号相关内容
                if '待审核员工账号' in content:
                    print("[OK] 页面包含'待审核员工账号'文本")
                else:
                    print("[ERROR] 页面不包含'待审核员工账号'文本")
                
                if 'pending_staff' in content:
                    print("[OK] 页面包含pending_staff变量")
                else:
                    print("[ERROR] 页面不包含pending_staff变量")
                
                if 'test_pending@example.com' in content:
                    print("[OK] 页面包含测试员工邮箱")
                else:
                    print("[ERROR] 页面不包含测试员工邮箱")
                
                # 检查调试信息
                if '调试信息' in content:
                    print("[OK] 页面包含调试信息")
                    # 提取调试信息
                    import re
                    debug_match = re.search(r'调试信息: pending_staff 数量 = (\d+)', content)
                    if debug_match:
                        count = debug_match.group(1)
                        print(f"调试信息显示数量: {count}")
                else:
                    print("[ERROR] 页面不包含调试信息")
                
                # 保存页面内容到文件用于检查
                with open('user_management_page.html', 'w', encoding='utf-8') as f:
                    f.write(content)
                print("页面内容已保存到 user_management_page.html")
                
            else:
                print(f"访问用户管理页面失败: {user_mgmt_response.status_code}")
                print(f"响应内容: {user_mgmt_response.text}")
        else:
            print(f"登录失败: {login_response.status_code}")
            print(f"响应内容: {login_response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_user_management_page()
