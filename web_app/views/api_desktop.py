#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面客户端专用API端点
提供无需会话认证的API接口
"""

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, Staff, User, Project

api_desktop_bp = Blueprint('api_desktop', __name__)

@api_desktop_bp.route('/login', methods=['POST'])
def desktop_login():
    """桌面客户端登录API"""
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
            # 返回用户基本信息
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

@api_desktop_bp.route('/projects', methods=['POST'])
def desktop_get_projects():
    """桌面客户端获取项目列表API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'})
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        user_type = data.get('user_type', 'staff').strip()
        status = data.get('status')
        executor_id = data.get('executor_id')
        
        # 验证用户身份
        user = None
        if user_type == 'staff':
            user = Staff.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'message': '身份验证失败'})
        
        # 检查权限（只有员工可以获取项目）
        if user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        # 构建查询
        query = Project.query
        
        if status:
            query = query.filter_by(status=status)
        
        if executor_id:
            query = query.filter_by(executor_id=executor_id)
        
        # 获取项目
        projects = query.order_by(Project.apply_time.desc()).all()
        
        # 序列化项目数据
        project_list = []
        for project in projects:
            applicant = User.query.get(project.applicant_id)
            project_data = {
                'id': project.id,
                'project_name': project.project_name,
                'project_type': project.project_type,
                'applicant_type': project.applicant_type,
                'copyright_owner': project.copyright_owner,
                'software_applicant_name': project.software_applicant_name,
                'serial_number': project.serial_number,
                'priority': project.priority,
                'status': project.status,
                'executor_id': project.executor_id,
                'remarks': project.remarks,
                'apply_time': project.apply_time.strftime('%Y-%m-%d %H:%M:%S') if project.apply_time else None,
                'applicant_name': applicant.name if applicant else None
            }
            project_list.append(project_data)
        
        return jsonify({
            'success': True,
            'message': '获取成功',
            'projects': project_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取项目失败: {str(e)}'})

@api_desktop_bp.route('/sync_projects', methods=['POST'])
def desktop_sync_projects():
    """桌面客户端同步项目API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'})
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        user_type = data.get('user_type', 'staff').strip()
        
        # 验证用户身份
        user = None
        if user_type == 'staff':
            user = Staff.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'message': '身份验证失败'})
        
        # 检查权限（只有员工可以同步项目）
        if user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        # 获取所有需要同步的项目
        projects = Project.query.filter(
            Project.status.in_(['已确认', '已立项', '执行中', '已完成', '已上传', '已获取流水号'])
        ).all()
        
        # 序列化项目数据
        project_list = []
        for project in projects:
            applicant = User.query.get(project.applicant_id)
            project_data = {
                'id': project.id,
                'project_name': project.project_name,
                'project_type': project.project_type,
                'applicant_type': project.applicant_type,
                'copyright_owner': project.copyright_owner,
                'software_applicant_name': project.software_applicant_name,
                'serial_number': project.serial_number,
                'priority': project.priority,
                'status': project.status,
                'executor_id': project.executor_id,
                'remarks': project.remarks,
                'apply_time': project.apply_time.strftime('%Y-%m-%d %H:%M:%S') if project.apply_time else None,
                'applicant_name': applicant.name if applicant else None
            }
            project_list.append(project_data)
        
        return jsonify({
            'success': True,
            'message': f'同步成功，共 {len(project_list)} 个项目',
            'projects': project_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'同步项目失败: {str(e)}'})

@api_desktop_bp.route('/update_project', methods=['POST'])
def desktop_update_project():
    """桌面客户端更新项目字段API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'})
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        user_type = data.get('user_type', 'staff').strip()
        project_id = data.get('project_id')
        fields = data.get('fields', {})
        
        if not project_id:
            return jsonify({'success': False, 'message': '项目ID不能为空'})
        
        if not fields:
            return jsonify({'success': False, 'message': '更新字段不能为空'})
        
        # 验证用户身份
        user = None
        if user_type == 'staff':
            user = Staff.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'message': '身份验证失败'})
        
        # 检查权限（只有员工可以更新项目）
        if user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        # 查找项目
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'success': False, 'message': '项目不存在'})
        
        # 定义允许更新的字段
        allowed_fields = {
            'project_name', 'project_type', 'applicant_type', 'copyright_owner',
            'software_applicant_name', 'serial_number', 'priority', 'status',
            'executor_id', 'remarks'
        }
        
        # 过滤允许更新的字段
        update_fields = {k: v for k, v in fields.items() if k in allowed_fields}
        
        if not update_fields:
            return jsonify({'success': False, 'message': '没有有效的更新字段'})
        
        # 更新项目字段
        for field, value in update_fields.items():
            if hasattr(project, field):
                setattr(project, field, value)
        
        # 保存到数据库
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'项目更新成功，共更新 {len(update_fields)} 个字段',
            'updated_fields': list(update_fields.keys())
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'更新项目失败: {str(e)}'})

