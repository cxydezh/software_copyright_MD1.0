from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, Project, User, Staff, Message

api_bp = Blueprint('api', __name__)

@api_bp.route('/projects')
@login_required
def get_projects():
    """获取项目列表API"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 获取查询参数
    status = request.args.get('status')
    executor_id = request.args.get('executor_id')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 构建查询
    query = Project.query
    
    if status:
        query = query.filter_by(status=status)
    
    if executor_id:
        query = query.filter_by(executor_id=executor_id)
    
    # 分页
    projects = query.order_by(Project.apply_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # 序列化项目数据
    project_list = []
    for project in projects.items:
        applicant = User.query.get(project.applicant_id)
        project_data = {
            'id': project.id,
            'project_name': project.project_name,
            'project_type': project.project_type,
            'applicant_type': project.applicant_type,
            'status': project.status,
            'priority': project.priority,
            'apply_time': project.apply_time.strftime('%Y-%m-%d %H:%M:%S') if project.apply_time else None,
            'applicant_name': applicant.name if applicant else None,
            'serial_number': project.serial_number
        }
        project_list.append(project_data)
    
    return jsonify({
        'success': True,
        'projects': project_list,
        'pagination': {
            'page': projects.page,
            'pages': projects.pages,
            'per_page': projects.per_page,
            'total': projects.total
        }
    })

@api_bp.route('/project/<int:project_id>')
@login_required
def get_project_detail(project_id):
    """获取项目详情API"""
    project = Project.query.get_or_404(project_id)
    
    # 检查权限
    if hasattr(current_user, 'user_type'):
        if current_user.user_type == 'user' and project.applicant_id != current_user.id:
            return jsonify({'success': False, 'message': '权限不足'})
        elif current_user.user_type == 'staff' and project.confirmer_id != current_user.id and project.executor_id != current_user.id:
            return jsonify({'success': False, 'message': '权限不足'})
    
    # 获取申请人信息
    applicant = User.query.get(project.applicant_id)
    
    # 获取确认者和执行者信息
    confirmer = Staff.query.get(project.confirmer_id) if project.confirmer_id else None
    executor = Staff.query.get(project.executor_id) if project.executor_id else None
    
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
        'price': float(project.price) if project.price else None,
        'discount': float(project.discount) if project.discount else None,
        'remarks': project.remarks,
        'apply_time': project.apply_time.strftime('%Y-%m-%d %H:%M:%S') if project.apply_time else None,
        'confirm_time': project.confirm_time.strftime('%Y-%m-%d %H:%M:%S') if project.confirm_time else None,
        'execute_time': project.execute_time.strftime('%Y-%m-%d %H:%M:%S') if project.execute_time else None,
        'complete_time': project.complete_time.strftime('%Y-%m-%d %H:%M:%S') if project.complete_time else None,
        'settle_time': project.settle_time.strftime('%Y-%m-%d %H:%M:%S') if project.settle_time else None,
        'submit_time': project.submit_time.strftime('%Y-%m-%d %H:%M:%S') if project.submit_time else None,
        'certificate_time': project.certificate_time.strftime('%Y-%m-%d %H:%M:%S') if project.certificate_time else None,
        'applicant': {
            'id': applicant.id,
            'name': applicant.name,
            'email': applicant.email,
            'phone': applicant.phone
        } if applicant else None,
        'confirmer': {
            'id': confirmer.id,
            'name': confirmer.name
        } if confirmer else None,
        'executor': {
            'id': executor.id,
            'name': executor.name
        } if executor else None
    }
    
    return jsonify({'success': True, 'project': project_data})

@api_bp.route('/messages')
@login_required
def get_messages():
    """获取消息列表API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # 根据用户类型获取消息
    if hasattr(current_user, 'user_type'):
        if current_user.user_type == 'user':
            messages = Message.query.filter_by(user_id=current_user.id)
        elif current_user.user_type == 'staff':
            messages = Message.query.filter_by(staff_id=current_user.id)
        else:
            return jsonify({'success': False, 'message': '无效的用户类型'})
    else:
        return jsonify({'success': False, 'message': '用户类型未知'})
    
    messages = messages.order_by(Message.create_time.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    message_list = []
    for message in messages.items:
        message_data = {
            'id': message.id,
            'content': message.content,
            'create_time': message.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'is_read': message.is_read,
            'project_id': message.project_id
        }
        message_list.append(message_data)
    
    return jsonify({
        'success': True,
        'messages': message_list,
        'pagination': {
            'page': messages.page,
            'pages': messages.pages,
            'per_page': messages.per_page,
            'total': messages.total
        }
    })

@api_bp.route('/statistics')
@login_required
def get_statistics():
    """获取统计信息API"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 项目状态统计
    status_stats = {}
    statuses = ['待确认', '已确认', '已立项', '执行中', '已完成', '已上传', '已获取流水号', '证书完成', '已归档']
    
    for status in statuses:
        count = Project.query.filter_by(status=status).count()
        status_stats[status] = count
    
    # 结清状态统计（独立统计）
    status_stats['已结清'] = Project.query.filter_by(is_settled=True).count()
    status_stats['未结清'] = Project.query.filter_by(is_settled=False).count()
    
    # 项目类型统计
    type_stats = {}
    types = ['软件登记业务', '软件设计与登记业务', '软件部署与登记业务']
    
    for project_type in types:
        count = Project.query.filter_by(project_type=project_type).count()
        type_stats[project_type] = count
    
    # 申请人类型统计
    applicant_type_stats = {}
    applicant_types = ['个人', '事业单位', '事业单位联合个人', '自然人联合']
    
    for applicant_type in applicant_types:
        count = Project.query.filter_by(applicant_type=applicant_type).count()
        applicant_type_stats[applicant_type] = count
    
    # 优先级统计
    priority_stats = {}
    priorities = ['普通', '加急', '快速']
    
    for priority in priorities:
        count = Project.query.filter_by(priority=priority).count()
        priority_stats[priority] = count
    
    # 总体统计
    total_projects = Project.query.count()
    total_users = User.query.count()
    total_staff = Staff.query.count()
    total_messages = Message.query.count()
    
    return jsonify({
        'success': True,
        'statistics': {
            'total_projects': total_projects,
            'total_users': total_users,
            'total_staff': total_staff,
            'total_messages': total_messages,
            'status_stats': status_stats,
            'type_stats': type_stats,
            'applicant_type_stats': applicant_type_stats,
            'priority_stats': priority_stats
        }
    })

@api_bp.route('/sync_projects')
def sync_projects():
    """同步项目到本地客户端API"""
    # 检查是否已登录
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'message': '请先登录'})
    
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 检查是否为项目执行者
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.position == '项目执行者'):
        return jsonify({'success': False, 'message': '只有项目执行者可以同步项目'})
    
    # 获取已确认的项目
    projects = Project.query.filter(
        Project.status.in_(['已确认', '已立项', '执行中', '已完成', '已上传', '已获取流水号'])
    ).all()
    
    project_list = []
    for project in projects:
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
            'remarks': project.remarks
        }
        project_list.append(project_data)
    
    return jsonify({
        'success': True,
        'projects': project_list
    })
