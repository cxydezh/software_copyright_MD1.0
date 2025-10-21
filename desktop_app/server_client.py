#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
服务器客户端模块
处理与Web服务器的API通信
"""

import requests
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from desktop_app.logger import get_logger


class ServerClient:
    """服务器API客户端"""
    
    def __init__(self, server_host: str = 'http://192.168.31.56', server_port: int = 5000):
        """
        初始化服务器客户端
        
        Args:
            server_host: 服务器地址
            server_port: 服务器端口
        """
        # 确保有 http(s) 协议前缀
        if not server_host.startswith('http://') and not server_host.startswith('https://'):
            server_host = f"http://{server_host}"
        self.server_host = server_host.rstrip('/')
        self.server_port = server_port
        self.api_base = f"{self.server_host}:{server_port}/api"
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'SoftwareCopyrightMS-Desktop/2.0'
        })
        self.current_user = None
        self.user_password = None  # 存储用户密码用于API调用
        self.logger = get_logger('desktop_app.server_client')
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            data: 请求数据
            params: URL参数
            
        Returns:
            (success, response_data)
        """
        try:
            url = f"{self.api_base}{endpoint}"
            self.logger.debug("HTTP %s %s params=%s", method.upper(), url, params or data)
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=10)
            else:
                return False, {'message': f'不支持的HTTP方法: {method}'}
            
            # 检查响应状态
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    self.logger.debug("Response 200: %s", response_data)
                    return True, response_data
                except json.JSONDecodeError:
                    self.logger.error("JSON decode error, text=%s", response.text[:500])
                    return False, {'message': '服务器响应格式错误'}
            else:
                try:
                    error_data = response.json()
                    self.logger.warning("Response %s: %s", response.status_code, error_data)
                    return False, error_data
                except json.JSONDecodeError:
                    self.logger.error("Non-JSON error response %s, text=%s", response.status_code, response.text[:500])
                    return False, {'message': f'服务器错误: {response.status_code}'}
                    
        except requests.exceptions.ConnectionError:
            self.logger.exception("Connection error")
            return False, {'message': '无法连接到服务器，请检查网络连接和服务器地址'}
        except requests.exceptions.Timeout:
            self.logger.exception("Request timeout")
            return False, {'message': '请求超时，请检查网络连接'}
        except Exception as e:
            self.logger.exception("Request failed: %s", e)
            return False, {'message': f'请求失败: {str(e)}'}
    
    def login(self, email: str, password: str, user_type: str = 'user') -> Tuple[bool, str, Optional[Dict]]:
        """
        用户登录
        
        Args:
            email: 邮箱
            password: 密码
            user_type: 用户类型 ('user' 或 'staff')
            
        Returns:
            (success, message, user_data)
        """
        data = {
            'email': email,
            'password': password,
            'user_type': user_type
        }
        
        success, response = self._make_request('POST', '/desktop/login', data)
        
        if success and response.get('success'):
            self.current_user = response.get('user')
            self.user_password = password  # 存储密码用于后续API调用
            self.logger.info("Login success for %s (%s)", self.current_user.get('email'), user_type)
            return True, response.get('message', '登录成功'), self.current_user
        else:
            self.logger.warning("Login failed for %s: %s", email, response.get('message'))
            return False, response.get('message', '登录失败'), None
    
    def verify_user(self, user_id: int, user_type: str = 'user') -> Tuple[bool, str, Optional[Dict]]:
        """
        验证用户身份
        
        Args:
            user_id: 用户ID
            user_type: 用户类型
            
        Returns:
            (success, message, user_data)
        """
        data = {
            'user_id': user_id,
            'user_type': user_type
        }
        
        success, response = self._make_request('POST', '/auth/verify', data)
        
        if success and response.get('success'):
            return True, response.get('message', '验证成功'), response.get('user')
        else:
            return False, response.get('message', '验证失败'), None
    
    def get_projects(self, status: Optional[str] = None, executor_id: Optional[int] = None) -> Tuple[bool, str, List[Dict]]:
        """
        获取项目列表
        
        Args:
            status: 项目状态筛选
            executor_id: 执行者ID筛选
            
        Returns:
            (success, message, projects_list)
        """
        # 检查是否已登录
        if not self.current_user:
            return False, '请先登录', []
        
        params = {}
        if status:
            params['status'] = status
        if executor_id:
            params['executor_id'] = executor_id
        
        success, response = self._make_request('GET', '/projects', params=params)
        
        if success and response.get('success'):
            return True, response.get('message', '获取成功'), response.get('projects', [])
        else:
            return False, response.get('message', '获取项目失败'), []
    
    def get_all_projects_for_sync(self) -> Tuple[bool, str, List[Dict]]:
        """
        获取所有需要同步的项目（已确认、已立项、执行中、已完成等状态）
        
        Returns:
            (success, message, projects_list)
        """
        # 检查是否已登录
        if not self.current_user:
            return False, '请先登录', []
        
        # 使用桌面专用API获取所有项目
        data = {
            'email': self.current_user.get('email'),
            'password': self.user_password,
            'user_type': self.current_user.get('user_type')
        }
        
        success, response = self._make_request('POST', '/desktop/sync_projects', data)
        
        if success and response.get('success'):
            projects = response.get('projects', [])
            self.logger.info("Sync projects success: %d items", len(projects))
            return True, response.get('message', '获取成功'), projects
        else:
            self.logger.warning("Sync projects failed: %s", response.get('message'))
            return False, response.get('message', '获取项目失败'), []

    def get_projects_by_status(self, status: str) -> Tuple[bool, str, List[Dict]]:
        """按状态获取项目（桌面专用接口）。"""
        if not self.current_user:
            return False, '请先登录', []

        data = {
            'email': self.current_user.get('email'),
            'password': self.user_password,
            'user_type': self.current_user.get('user_type', 'staff'),
            'status': status
        }

        success, response = self._make_request('POST', '/desktop/projects', data)
        if success and response.get('success'):
            projects = response.get('projects', [])
            self.logger.debug("Fetched %d projects for status=%s", len(projects), status)
            return True, 'OK', projects
        else:
            msg = response.get('message', '获取项目失败') if isinstance(response, dict) else '获取项目失败'
            self.logger.warning("Get projects by status failed: %s", msg)
            return False, msg, []
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        测试服务器连接
        
        Returns:
            (success, message)
        """
        try:
            # 尝试访问服务器根路径
            url = f"{self.server_host}:{self.server_port}"
            self.logger.debug("Health check GET %s", url)
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                return True, f"服务器连接正常 (状态码: {response.status_code})"
            else:
                return False, f"服务器响应异常 (状态码: {response.status_code})"
        except requests.exceptions.ConnectionError:
            self.logger.exception("Health check connection error")
            return False, "无法连接到服务器，请检查服务器地址和端口"
        except requests.exceptions.Timeout:
            self.logger.exception("Health check timeout")
            return False, "连接超时，请检查网络连接"
        except Exception as e:
            self.logger.exception("Health check failed: %s", e)
            return False, f"连接测试失败: {str(e)}"
    
    def update_project_fields(self, project_id: int, fields: Dict) -> Tuple[bool, str]:
        """
        更新项目字段
        
        Args:
            project_id: 项目ID
            fields: 要更新的字段字典
            
        Returns:
            (success, message)
        """
        # 检查是否已登录
        if not self.current_user:
            return False, '请先登录'
        
        # 准备请求数据
        data = {
            'email': self.current_user.get('email'),
            'password': self.user_password,
            'user_type': self.current_user.get('user_type'),
            'project_id': project_id,
            'fields': fields
        }
        
        success, response = self._make_request('POST', '/desktop/update_project', data)
        
        if success and response.get('success'):
            self.logger.info("Update project %d fields success", project_id)
            return True, response.get('message', '更新成功')
        else:
            msg = response.get('message', '更新项目失败') if isinstance(response, dict) else '更新项目失败'
            self.logger.warning("Update project fields failed: %s", msg)
            return False, msg
    
    def update_project_status(self, project_id: int, status: str) -> Tuple[bool, str]:
        """
        更新项目状态
        
        Args:
            project_id: 项目ID
            status: 新状态
            
        Returns:
            (success, message)
        """
        if not self.current_user:
            return False, '请先登录'
        
        data = {
            'email': self.current_user.get('email'),
            'password': self.user_password,
            'user_type': self.current_user.get('user_type'),
            'project_id': project_id,
            'status': status
        }
        
        success, response = self._make_request('POST', '/desktop/update_project_status', data)
        
        if success and response.get('success'):
            self.logger.info("Update project %d status to %s success", project_id, status)
            return True, response.get('message', '状态更新成功')
        else:
            msg = response.get('message', '状态更新失败') if isinstance(response, dict) else '状态更新失败'
            self.logger.warning("Update project status failed: %s", msg)
            return False, msg
    
    def settle_project(self, project_id: int) -> Tuple[bool, str]:
        """
        标记项目为已收费
        
        Args:
            project_id: 项目ID
            
        Returns:
            (success, message)
        """
        if not self.current_user:
            return False, '请先登录'
        
        data = {
            'email': self.current_user.get('email'),
            'password': self.user_password,
            'user_type': self.current_user.get('user_type'),
            'project_id': project_id
        }
        
        success, response = self._make_request('POST', '/desktop/settle_project', data)
        
        if success and response.get('success'):
            self.logger.info("Settle project %d success", project_id)
            return True, response.get('message', '项目已标记为收费')
        else:
            msg = response.get('message', '收费标记失败') if isinstance(response, dict) else '收费标记失败'
            self.logger.warning("Settle project failed: %s", msg)
            return False, msg
    
    def archive_project(self, project_id: int) -> Tuple[bool, str]:
        """
        归档项目
        
        Args:
            project_id: 项目ID
            
        Returns:
            (success, message)
        """
        if not self.current_user:
            return False, '请先登录'
        
        data = {
            'email': self.current_user.get('email'),
            'password': self.user_password,
            'user_type': self.current_user.get('user_type'),
            'project_id': project_id
        }
        
        success, response = self._make_request('POST', '/desktop/archive_project', data)
        
        if success and response.get('success'):
            self.logger.info("Archive project %d success", project_id)
            return True, response.get('message', '项目已归档')
        else:
            msg = response.get('message', '归档失败') if isinstance(response, dict) else '归档失败'
            self.logger.warning("Archive project failed: %s", msg)
            return False, msg

    def update_project_serial(self, project_id: int, serial_number: str) -> Tuple[bool, str]:
        """
        更新项目流水号
        
        Args:
            project_id: 项目ID
            serial_number: 流水号
            
        Returns:
            (success, message)
        """
        return self.update_project_fields(project_id, {'serial_number': serial_number})
    
    def get_archived_projects(self) -> Tuple[bool, str, List[Dict]]:
        """
        获取已归档项目列表
        
        Returns:
            (success, message, projects_list)
        """
        if not self.current_user:
            return False, '请先登录', []
        
        data = {
            'email': self.current_user.get('email'),
            'password': self.user_password,
            'user_type': self.current_user.get('user_type'),
            'project_type': 'software'
        }
        
        success, response = self._make_request('POST', '/desktop/archived_projects', data)
        
        if success and response.get('success'):
            archived_data = response.get('data', {})
            software_projects = archived_data.get('software', [])
            self.logger.info("Get archived projects success, count: %d", len(software_projects))
            return True, '获取已归档项目成功', software_projects
        else:
            msg = response.get('message', '获取已归档项目失败') if isinstance(response, dict) else '获取已归档项目失败'
            self.logger.warning("Get archived projects failed: %s", msg)
            return False, msg, []
    
    def get_server_info(self) -> Dict:
        """
        获取服务器信息
        
        Returns:
            服务器信息字典
        """
        return {
            'server_host': self.server_host,
            'server_port': self.server_port,
            'api_base': self.api_base,
            'current_user': self.current_user
        }
