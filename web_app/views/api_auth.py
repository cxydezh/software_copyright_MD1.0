#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API认证端点
为桌面客户端提供独立的认证接口
"""

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, Staff, User

api_auth_bp = Blueprint('api_auth', __name__)

@api_auth_bp.route('/login', methods=['POST'])
def api_login():
    """API登录端点"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'})
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        user_type = data.get('user_type', 'user').strip()
        
        if not email or not password:
            return jsonify({'success': False, 'message': '邮箱和密码不能为空'})
        
        # 根据用户类型查找用户
        user = None
        if user_type == 'staff':
            user = Staff.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # 返回用户基本信息（不包含敏感信息）
            user_data = {
                'id': user.id,
                'email': user.email,
                'user_type': user_type,
                'name': getattr(user, 'name', ''),
                'phone': getattr(user, 'phone', ''),
            }
            
            # 如果是员工，添加职位信息
            if user_type == 'staff' and hasattr(user, 'position') and user.position:
                user_data['position'] = user.position.position
                user_data['permissions'] = {
                    'can_confirm': user.position.can_confirm,
                    'can_execute': user.position.can_execute,
                    'can_manage': user.position.can_manage,
                    'can_view_all': user.position.can_view_all,
                    'can_edit_paper': user.position.can_edit_paper,
                    'can_edit_patent': user.position.can_edit_patent,
                    'is_expert': user.position.is_expert
                }
            
            return jsonify({
                'success': True,
                'message': '登录成功',
                'user': user_data
            })
        else:
            return jsonify({'success': False, 'message': '邮箱或密码错误'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'登录失败: {str(e)}'})

@api_auth_bp.route('/verify', methods=['POST'])
def api_verify():
    """API验证端点（用于验证用户身份）"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'})
        
        user_id = data.get('user_id')
        user_type = data.get('user_type', 'user')
        
        if not user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'})
        
        # 根据用户类型查找用户
        user = None
        if user_type == 'staff':
            user = Staff.query.get(user_id)
        else:
            user = User.query.get(user_id)
        
        if user:
            return jsonify({
                'success': True,
                'message': '用户验证成功',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'user_type': user_type,
                    'name': getattr(user, 'name', ''),
                }
            })
        else:
            return jsonify({'success': False, 'message': '用户不存在'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'验证失败: {str(e)}'})
