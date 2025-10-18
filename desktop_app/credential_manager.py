#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版权中心账号密码管理模块
使用加密方式安全存储和读取账号密码
"""

import os
import base64
import hashlib
import uuid
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def _get_encryption_key() -> bytes:
    """生成基于机器特征的加密密钥"""
    try:
        # 使用MAC地址作为机器特征
        mac = str(uuid.getnode())
        
        # 添加额外的机器特征信息
        import platform
        machine_info = f"{mac}_{platform.node()}_{platform.system()}"
        
        # 生成密钥
        key = hashlib.sha256(machine_info.encode()).digest()
        return base64.urlsafe_b64encode(key)
        
    except Exception as e:
        print(f"[DEBUG] 生成加密密钥失败: {e}")
        # 回退到固定密钥（安全性较低，但保证功能可用）
        fallback_key = hashlib.sha256(b"fallback_key_for_copyright_center").digest()
        return base64.urlsafe_b64encode(fallback_key)


def _get_credentials_file_path() -> str:
    """获取凭证文件路径"""
    try:
        # 确保config目录存在
        config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        credentials_file = os.path.join(config_dir, 'copyright_credentials.enc')
        return credentials_file
        
    except Exception as e:
        print(f"[DEBUG] 获取凭证文件路径失败: {e}")
        # 回退到当前目录
        return 'copyright_credentials.enc'


def save_credentials(username: str, password: str) -> bool:
    """
    保存账号密码到加密文件
    
    Args:
        username: 用户名
        password: 密码
        
    Returns:
        bool: 保存是否成功
    """
    try:
        if not username or not password:
            print("[DEBUG] 用户名或密码为空，无法保存")
            return False
            
        # 生成加密密钥
        key = _get_encryption_key()
        fernet = Fernet(key)
        
        # 组合数据（使用特殊分隔符）
        data = f"{username}|||{password}"
        
        # 加密数据
        encrypted_data = fernet.encrypt(data.encode('utf-8'))
        
        # 保存到文件
        credentials_file = _get_credentials_file_path()
        with open(credentials_file, 'wb') as f:
            f.write(encrypted_data)
            
        print(f"[DEBUG] 账号密码已保存到: {credentials_file}")
        return True
        
    except Exception as e:
        print(f"[DEBUG] 保存账号密码失败: {e}")
        return False


def load_credentials() -> Optional[Tuple[str, str]]:
    """
    从加密文件加载账号密码
    
    Returns:
        Optional[Tuple[str, str]]: (用户名, 密码) 或 None
    """
    try:
        credentials_file = _get_credentials_file_path()
        
        if not os.path.exists(credentials_file):
            print("[DEBUG] 凭证文件不存在")
            return None
            
        # 读取加密数据
        with open(credentials_file, 'rb') as f:
            encrypted_data = f.read()
            
        # 生成解密密钥
        key = _get_encryption_key()
        fernet = Fernet(key)
        
        # 解密数据
        decrypted_data = fernet.decrypt(encrypted_data)
        data_str = decrypted_data.decode('utf-8')
        
        # 分离用户名和密码
        if '|||' in data_str:
            username, password = data_str.split('|||', 1)
            print("[DEBUG] 账号密码加载成功")
            return username, password
        else:
            print("[DEBUG] 凭证文件格式错误")
            return None
            
    except Exception as e:
        print(f"[DEBUG] 加载账号密码失败: {e}")
        return None


def delete_credentials() -> bool:
    """
    删除保存的账号密码
    
    Returns:
        bool: 删除是否成功
    """
    try:
        credentials_file = _get_credentials_file_path()
        
        if os.path.exists(credentials_file):
            os.remove(credentials_file)
            print(f"[DEBUG] 凭证文件已删除: {credentials_file}")
            return True
        else:
            print("[DEBUG] 凭证文件不存在，无需删除")
            return True
            
    except Exception as e:
        print(f"[DEBUG] 删除凭证文件失败: {e}")
        return False


def has_credentials() -> bool:
    """
    检查是否存在保存的账号密码
    
    Returns:
        bool: 是否存在凭证
    """
    try:
        credentials_file = _get_credentials_file_path()
        exists = os.path.exists(credentials_file)
        print(f"[DEBUG] 凭证文件存在状态: {exists}")
        return exists
        
    except Exception as e:
        print(f"[DEBUG] 检查凭证文件失败: {e}")
        return False


def get_username_only() -> Optional[str]:
    """
    仅获取用户名（用于显示，不暴露密码）
    
    Returns:
        Optional[str]: 用户名或None
    """
    try:
        credentials = load_credentials()
        if credentials:
            username, _ = credentials
            return username
        return None
        
    except Exception as e:
        print(f"[DEBUG] 获取用户名失败: {e}")
        return None


def test_credentials() -> bool:
    """
    测试保存的凭证是否有效（仅测试解密，不验证登录）
    
    Returns:
        bool: 凭证是否有效
    """
    try:
        credentials = load_credentials()
        if credentials:
            username, password = credentials
            if username and password:
                print("[DEBUG] 凭证测试通过")
                return True
        print("[DEBUG] 凭证测试失败")
        return False
        
    except Exception as e:
        print(f"[DEBUG] 凭证测试异常: {e}")
        return False


if __name__ == "__main__":
    # 测试功能
    print("=== 版权中心凭证管理器测试 ===")
    
    # 测试保存
    print("\n1. 测试保存凭证...")
    success = save_credentials("test_user", "test_password")
    print(f"保存结果: {success}")
    
    # 测试检查
    print("\n2. 测试检查凭证...")
    has_creds = has_credentials()
    print(f"凭证存在: {has_creds}")
    
    # 测试加载
    print("\n3. 测试加载凭证...")
    creds = load_credentials()
    if creds:
        username, password = creds
        print(f"用户名: {username}")
        print(f"密码: {'*' * len(password)}")
    else:
        print("加载失败")
    
    # 测试仅获取用户名
    print("\n4. 测试获取用户名...")
    username_only = get_username_only()
    print(f"用户名: {username_only}")
    
    # 测试删除
    print("\n5. 测试删除凭证...")
    delete_success = delete_credentials()
    print(f"删除结果: {delete_success}")
    
    # 再次检查
    print("\n6. 再次检查凭证...")
    has_creds_after = has_credentials()
    print(f"凭证存在: {has_creds_after}")
    
    print("\n=== 测试完成 ===")
