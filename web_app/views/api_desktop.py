#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
桌面客户端专用API端点
提供无需会话认证的API接口
"""

from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, Staff, User, Project, ProcessLog

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

@api_desktop_bp.route('/update_project_status', methods=['POST'])
def desktop_update_project_status():
    """桌面客户端更新项目状态API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'})
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        user_type = data.get('user_type', 'staff').strip()
        project_id = data.get('project_id')
        status = data.get('status', '').strip()
        
        if not project_id:
            return jsonify({'success': False, 'message': '项目ID不能为空'})
        
        if not status:
            return jsonify({'success': False, 'message': '状态不能为空'})
        
        # 验证用户身份
        user = None
        if user_type == 'staff':
            user = Staff.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'message': '身份验证失败'})
        
        # 检查权限（只有员工可以更新项目状态）
        if user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        # 查找项目
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'success': False, 'message': '项目不存在'})
        
        # 检查权限（业务员和执行者都可以更新状态）
        if project.confirmer_id != user.id and project.executor_id != user.id:
            return jsonify({'success': False, 'message': '您没有权限操作此项目'})
        
        # 验证状态转换
        valid_statuses = ['执行中', '已完成', '已上传', '已获取流水号', '证书完成', '已归档']
        if status not in valid_statuses:
            return jsonify({'success': False, 'message': '无效的状态'})
        
        # 如果要归档，必须先结清
        if status == '已归档' and not project.is_settled:
            return jsonify({'success': False, 'message': '项目必须先结清才能归档'})
        
        try:
            prev_status = project.status
            project.status = status
            
            # 更新相应的时间字段
            if status == '执行中':
                project.execute_time = datetime.utcnow()
            elif status == '已完成':
                project.complete_time = datetime.utcnow()
            elif status == '已上传':
                project.submit_time = datetime.utcnow()
            elif status == '证书完成':
                project.certificate_time = datetime.utcnow()
            elif status == '已归档':
                project.is_archived = True
            
            # 记录流程日志
            db.session.add(ProcessLog(
                project_type='software', 
                project_id=project.id,
                action='update_status', 
                actor_id=user.id, 
                actor_role='staff',
                from_status=prev_status, 
                to_status=project.status, 
                note=f'更新状态为{status}'
            ))
            
            db.session.commit()
            return jsonify({'success': True, 'message': '状态更新成功'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'状态更新失败: {str(e)}'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'更新项目状态失败: {str(e)}'})

@api_desktop_bp.route('/settle_project', methods=['POST'])
def desktop_settle_project():
    """桌面客户端标记项目为已收费API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'})
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        user_type = data.get('user_type', 'staff').strip()
        project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({'success': False, 'message': '项目ID不能为空'})
        
        # 验证用户身份
        user = None
        if user_type == 'staff':
            user = Staff.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'message': '身份验证失败'})
        
        # 检查权限（只有员工可以标记收费）
        if user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        # 查找项目
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'success': False, 'message': '项目不存在'})
        
        # 检查权限（业务员和执行者都可以标记收费）
        if project.confirmer_id != user.id and project.executor_id != user.id:
            return jsonify({'success': False, 'message': '您没有权限操作此项目'})
        
        try:
            project.is_settled = True
            project.settle_time = datetime.utcnow()
            
            # 记录流程日志
            db.session.add(ProcessLog(
                project_type='software', 
                project_id=project.id,
                action='settle', 
                actor_id=user.id, 
                actor_role='staff',
                from_status=None, 
                to_status=project.status, 
                note='标记为已收费'
            ))
            
            db.session.commit()
            return jsonify({'success': True, 'message': '项目已标记为收费'})
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'收费标记失败: {str(e)}'})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'标记收费失败: {str(e)}'})

@api_desktop_bp.route('/archive_project', methods=['POST'])
def desktop_archive_project():
    """桌面客户端归档项目API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'})
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        user_type = data.get('user_type', 'staff').strip()
        project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({'success': False, 'message': '项目ID不能为空'})
        
        # 验证用户身份
        user = None
        if user_type == 'staff':
            user = Staff.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'message': '身份验证失败'})
        
        # 检查权限（只有员工可以归档项目）
        if user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        # 查找项目
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'success': False, 'message': '项目不存在'})
        
        # 检查权限（业务员和执行者都可以归档项目）
        if project.confirmer_id != user.id and project.executor_id != user.id:
            return jsonify({'success': False, 'message': '您没有权限操作此项目'})
        
        # 检查是否已结算
        if not project.is_settled:
            return jsonify({'success': False, 'message': '项目尚未结算，无法归档'})
        
        # 检查是否已归档
        if project.is_archived:
            return jsonify({'success': False, 'message': '项目已归档'})
        
        # 使用归档服务
        from web_app.services.archive_service import ArchiveService
        success, message = ArchiveService.archive_software_project(project_id)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'message': message})
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'归档项目失败: {str(e)}'})

@api_desktop_bp.route('/archived_projects', methods=['POST'])
def desktop_get_archived_projects():
    """桌面客户端获取已归档项目API"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': '请求数据格式错误'})
        
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        user_type = data.get('user_type', 'staff').strip()
        project_type = data.get('project_type', 'software').strip()
        
        # 验证用户身份
        user = None
        if user_type == 'staff':
            user = Staff.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({'success': False, 'message': '身份验证失败'})
        
        # 检查权限（只有员工可以获取归档项目）
        if user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        # 获取归档项目
        from web_app.services.archive_service import ArchiveService
        archived_data = ArchiveService.get_archived_projects(project_type)
        
        if archived_data is None:
            return jsonify({'success': False, 'message': '获取归档项目失败'})
        
        # 格式化返回数据
        results = {
            'software': [{
                'id': p.id,
                'project_name': p.project_name,
                'project_type': p.project_type,
                'copyright_owner': p.copyright_owner,
                'serial_number': p.serial_number,
                'archive_time': p.archive_time.strftime('%Y-%m-%d %H:%M:%S') if p.archive_time else None,
                'price': float(p.price) if p.price else 0
            } for p in archived_data['software']],
            'paper': [{
                'id': p.id,
                'project_name': p.project_name,
                'paper_title': p.paper_title,
                'target_journal': p.target_journal,
                'archive_time': p.archive_time.strftime('%Y-%m-%d %H:%M:%S') if p.archive_time else None,
                'price': float(p.price) if p.price else 0
            } for p in archived_data['paper']],
            'patent': [{
                'id': p.id,
                'project_name': p.project_name,
                'invention_title': p.invention_title,
                'patent_number': p.patent_number,
                'archive_time': p.archive_time.strftime('%Y-%m-%d %H:%M:%S') if p.archive_time else None,
                'price': float(p.price) if p.price else 0
            } for p in archived_data['patent']]
        }
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '获取归档项目成功'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'获取归档项目失败: {str(e)}'})

