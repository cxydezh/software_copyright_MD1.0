from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
from datetime import datetime
from werkzeug.utils import secure_filename
import sys
import os
import uuid
import mimetypes
import shutil

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, Project, Message, User, Staff, ProcessLog, Permission, SystemSettings, ProjectFile
from werkzeug.security import generate_password_hash

# 允许的文件类型
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif', 'zip', 'rar', 'xls', 'xlsx'}

# 文件大小限制（16MB）
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    """检查文件类型是否允许"""
    if not filename or '.' not in filename:
        return False
    try:
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in ALLOWED_EXTENSIONS
    except IndexError:
        return False

def check_file_size(file):
    """检查文件大小是否在限制内"""
    # 获取文件大小（通过读取文件流位置）
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # 重置文件指针
    return file_size <= MAX_FILE_SIZE, file_size

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/login')
def staff_login():
    """员工登录页面重定向"""
    return redirect(url_for('auth.login'))

@staff_bp.route('/business_dashboard')
@login_required
def business_dashboard():
    """普通业务员仪表板"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    # 获取待处理的项目申请
    pending_projects = Project.query.filter_by(status='待确认').order_by(Project.apply_time.desc()).all()
    
    # 获取我确认的项目
    confirmed_projects = Project.query.filter_by(confirmer_id=current_user.id).order_by(Project.confirm_time.desc()).all()
    
    # 统计信息
    stats = {
        'pending_count': len(pending_projects),
        'confirmed_count': len(confirmed_projects),
        'in_progress_count': len([p for p in confirmed_projects if p.status in ['已确认', '已立项', '执行中']]),
        'completed_count': len([p for p in confirmed_projects if p.status in ['已完成', '已上传', '已获取流水号', '证书完成', '已归档']]),
        'settled_count': len([p for p in confirmed_projects if p.is_settled])
    }
    
    # 获取最近的消息
    recent_messages = Message.query.filter_by(staff_id=current_user.id).order_by(Message.create_time.desc()).limit(5).all()
    
    return render_template('staff/business_dashboard.html',
                         pending_projects=pending_projects,
                         confirmed_projects=confirmed_projects,
                         stats=stats,
                         recent_messages=recent_messages)

@staff_bp.route('/project/<int:project_id>/reject', methods=['POST'])
@login_required
def reject_project(project_id):
    """业务员在待确认阶段，驳回给用户并附带修改意见（不改变状态，记录流程）"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    project = Project.query.get_or_404(project_id)
    if project.status != '待确认':
        return jsonify({'success': False, 'message': '当前状态不能驳回，请返回待确认后操作'})
    data = request.get_json() or {}
    reason = (data.get('reject_reason') or '').strip()
    if not reason:
        return jsonify({'success': False, 'message': '请输入驳回原因'})
    try:
        # 记录流程
        db.session.add(ProcessLog(
            project_type='software', project_id=project.id,
            action='reject_to_user', actor_id=current_user.id, actor_role='staff',
            from_status=project.status, to_status=project.status, note=reason))
        # 通知用户
        db.session.add(Message(
            content=f'您的项目【{project.project_name}】被驳回：{reason}',
            user_id=project.applicant_id,
            staff_id=current_user.id,
            project_id=project.id
        ))
        db.session.commit()
        return jsonify({'success': True, 'message': '已驳回并通知用户修改'})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': '驳回失败，请重试'})

@staff_bp.route('/project/<int:project_id>/reject_to_business', methods=['POST'])
@login_required
def reject_to_business(project_id):
    """立项人将已确认项目退回给业务员完善（状态回到待确认）"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    # 权限：确认者且有立项权限，或 项目执行者角色（用于可接受项目的退回）
    is_approver = hasattr(current_user, 'position') and current_user.position and current_user.position.can_approve
    is_executor_role = hasattr(current_user, 'position') and current_user.position and current_user.position.position == '项目执行者'
    project = Project.query.get_or_404(project_id)
    if project.status != '已确认':
        return jsonify({'success': False, 'message': '仅已确认的项目可以退回业务员'})
    # 执行者可在未分配执行者时退回
    if is_executor_role:
        if project.executor_id is not None:
            return jsonify({'success': False, 'message': '该项目已分配执行者，无法退回'})
    else:
        return jsonify({'success': False, 'message': '您没有权限退回该项目'})
    data = request.get_json() or {}
    reason = (data.get('reject_reason') or '').strip()
    if not reason:
        return jsonify({'success': False, 'message': '请输入退回原因'})
    try:
        prev_status = project.status
        project.status = '待确认'
        project.confirm_time = None
        # 流程记录
        db.session.add(ProcessLog(
            project_type='software', project_id=project.id,
            action='return_to_business', actor_id=current_user.id, actor_role='staff',
            from_status=prev_status, to_status=project.status, note=reason))
        # 通知业务员（确认者自己）
        db.session.add(Message(
            content=f'项目【{project.project_name}】被退回至待确认：{reason}',
            user_id=None,
            staff_id=project.confirmer_id,
            project_id=project.id
        ))
        db.session.commit()
        return jsonify({'success': True, 'message': '已退回给业务员完善'})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'})

@staff_bp.route('/executor_dashboard')
@login_required
def executor_dashboard():
    """项目执行者仪表板"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    # 检查是否为项目执行者
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.position == '项目执行者'):
        flash('您不是项目执行者', 'warning')
        return redirect(url_for('staff.business_dashboard'))
    
    # 获取分配给我的项目
    assigned_projects = Project.query.filter_by(executor_id=current_user.id).filter(Project.status != '已归档').order_by(Project.execute_time.desc()).all()
    
    # 获取待立项的项目（已确认但未分配执行者）
    available_projects = Project.query.filter_by(status='已确认', executor_id=None).order_by(Project.confirm_time.desc()).all()
    
    # 获取已立项待执行的项目（已立项且未分配执行者）
    approved_projects = Project.query.filter_by(status='已立项', executor_id=None).order_by(Project.confirm_time.desc()).all()
    
    # 统计信息
    stats = {
        'assigned_count': len(assigned_projects),
        'available_count': len(available_projects),
        'in_progress_count': len([p for p in assigned_projects if p.status in ['已立项', '执行中']]),
        'completed_count': len([p for p in assigned_projects if p.status in ['已完成', '已上传', '已获取流水号', '证书完成']])
    }
    
    return render_template('staff/executor_dashboard.html',
                         assigned_projects=assigned_projects,
                         available_projects=available_projects,
                         approved_projects=approved_projects,
                         stats=stats)

@staff_bp.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    """项目详情"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    project = Project.query.get_or_404(project_id)
    
    # 检查权限
    # 业务员可以查看：1. 待确认的项目 2. 自己确认的项目 3. 自己执行的项目
    can_view = False
    
    # 待确认的项目，所有业务员都可以查看和确认
    if project.status == '待确认':
        can_view = True
    # 已确认的项目，确认者和执行者可以查看
    elif project.confirmer_id == current_user.id or project.executor_id == current_user.id:
        can_view = True
    # 项目执行者可以查看所有已立项但未分配执行者的项目
    elif (project.status == '已立项' and project.executor_id is None and 
          hasattr(current_user, 'position') and current_user.position and 
          current_user.position.position == '项目执行者'):
        can_view = True
    
    if not can_view:
        flash('您没有权限查看此项目', 'danger')
        return redirect(url_for('staff.business_dashboard'))
    
    # 获取项目申请人信息
    applicant = User.query.get(project.applicant_id)
    
    # 获取项目相关的消息
    project_messages = Message.query.filter_by(project_id=project_id).order_by(Message.create_time.desc()).all()
    
    # 获取项目文件列表
    project_files = ProjectFile.query.filter_by(
        project_id=project_id,
        project_type='software'
    ).order_by(ProjectFile.upload_time.desc()).all()
    
    return render_template('staff/project_detail.html',
                         project=project,
                         applicant=applicant,
                         messages=project_messages,
                         project_files=project_files)

@staff_bp.route('/project/<int:project_id>/confirm', methods=['POST'])
@login_required
def confirm_project(project_id):
    """确认项目申请"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    project = Project.query.get_or_404(project_id)
    
    if project.status != '待确认':
        return jsonify({'success': False, 'message': '项目状态不允许此操作'})
    
    try:
        prev_status = project.status
        project.status = '已确认'
        project.confirmer_id = current_user.id
        project.confirm_time = datetime.utcnow()
        # 自动给申请人发送站内信提示（可选）
        db.session.add(Message(
            content=f'您的项目【{project.project_name}】已通过审核，进入已确认状态。',
            user_id=project.applicant_id,
            staff_id=current_user.id,
            project_id=project.id
        ))
        # 记录流程
        db.session.add(ProcessLog(
            project_type='software', project_id=project.id,
            action='confirm', actor_id=current_user.id, actor_role='staff',
            from_status=prev_status, to_status=project.status, note='业务员确认项目'))
        db.session.commit()
        return jsonify({'success': True, 'message': '项目确认成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '确认失败，请重试'})

@staff_bp.route('/project/<int:project_id>/approve', methods=['POST'])
@login_required
def approve_project(project_id):
    """立项（只有有立项权限的人可以操作）"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 检查立项权限
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.can_approve):
        return jsonify({'success': False, 'message': '您没有立项权限，请联系主管'})
    
    project = Project.query.get_or_404(project_id)
    
    
    if project.status != '已确认':
        return jsonify({'success': False, 'message': '项目状态不允许此操作'})
    
    try:
        prev_status = project.status
        project.status = '已立项'
        # 不自动设置执行者，等待执行者自己接受项目
        # project.executor_id 保持为 None
        # 通知执行者团队（此处仅发站内信给确认者自身，后续可扩展）
        db.session.add(Message(
            content=f'项目【{project.project_name}】已立项，等待执行者接受。',
            user_id=None,
            staff_id=current_user.id,
            project_id=project.id
        ))
        db.session.add(ProcessLog(
            project_type='software', project_id=project.id,
            action='approve', actor_id=current_user.id, actor_role='staff',
            from_status=prev_status, to_status=project.status, note='立项'))
        db.session.commit()
        return jsonify({'success': True, 'message': '项目立项成功，等待执行者接受'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '立项失败，请重试'})

@staff_bp.route('/project/<int:project_id>/take', methods=['POST'])
@login_required
def take_project(project_id):
    """接受项目执行"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
        
    project = Project.query.get_or_404(project_id)
    
    if project.status != '已立项' or project.executor_id is not None:
        return jsonify({'success': False, 'message': '项目状态不允许此操作'})
    
    try:
        prev_status = project.status
        project.executor_id = current_user.id
        project.execute_time = datetime.utcnow()
        project.status = '执行中'
        # 通知确认者
        if project.confirmer_id:
            db.session.add(Message(
                content=f'项目【{project.project_name}】已被执行者接受，进入执行中。',
                user_id=None,
                staff_id=project.confirmer_id,
                project_id=project.id
            ))
        db.session.add(ProcessLog(
            project_type='software', project_id=project.id,
            action='take', actor_id=current_user.id, actor_role='staff',
            from_status=prev_status, to_status=project.status, note='执行者接受项目'))
        db.session.commit()
        return jsonify({'success': True, 'message': '项目接受成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '接受项目失败，请重试'})

@staff_bp.route('/project/<int:project_id>/complete', methods=['POST'])
@login_required
def complete_project(project_id):
    """标记项目完成"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    project = Project.query.get_or_404(project_id)
    
    if project.executor_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限操作此项目'})
    
    if project.status != '执行中':
        return jsonify({'success': False, 'message': '项目状态不允许此操作'})
    
    try:
        prev_status = project.status
        project.status = '已完成'
        project.complete_time = datetime.utcnow()
        # 通知确认者和申请人
        if project.confirmer_id:
            db.session.add(Message(
                content=f'项目【{project.project_name}】已完成。',
                user_id=None,
                staff_id=project.confirmer_id,
                project_id=project.id
            ))
        if project.applicant_id:
            db.session.add(Message(
                content=f'您的项目【{project.project_name}】已完成。',
                user_id=project.applicant_id,
                staff_id=current_user.id,
                project_id=project.id
            ))
        db.session.add(ProcessLog(
            project_type='software', project_id=project.id,
            action='complete', actor_id=current_user.id, actor_role='staff',
            from_status=prev_status, to_status=project.status, note='执行者标记完成'))
        db.session.commit()
        return jsonify({'success': True, 'message': '项目标记完成成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'})

@staff_bp.route('/project/<int:project_id>/update_status', methods=['POST'])
@login_required
def update_project_status(project_id):
    """更新项目状态"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    project = Project.query.get_or_404(project_id)
    new_status = request.json.get('status')
    
    # 检查权限
    if project.confirmer_id != current_user.id and project.executor_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限操作此项目'})
    
    # 状态转换逻辑（已结清不在此列表中，它有独立的操作）
    valid_statuses = ['已完成', '已上传', '已获取流水号', '证书完成', '已归档']
    
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': '无效的状态'})
    
    # 如果要归档，必须先结清
    if new_status == '已归档' and not project.is_settled:
        return jsonify({'success': False, 'message': '项目必须先结清才能归档'})
    
    try:
        prev_status = project.status
        
        # 如果状态是"已归档"，调用归档服务进行完整归档
        if new_status == '已归档':
            from web_app.services.archive_service import ArchiveService
            success, message = ArchiveService.archive_software_project(project_id)
            if success:
                return jsonify({'success': True, 'message': '项目已成功归档'})
            else:
                return jsonify({'success': False, 'message': f'归档失败: {message}'})
        
        # 其他状态更新
        project.status = new_status
        
        # 更新相应的时间字段
        if new_status == '已上传':
            project.submit_time = datetime.utcnow()
        elif new_status == '证书完成':
            project.certificate_time = datetime.utcnow()
            
        db.session.add(ProcessLog(
            project_type='software', project_id=project.id,
            action='update_status', actor_id=current_user.id, actor_role='staff',
            from_status=prev_status, to_status=project.status, note=f'更新状态为{new_status}'))
        db.session.commit()
        return jsonify({'success': True, 'message': '状态更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '状态更新失败，请重试'})

@staff_bp.route('/project/<int:project_id>/settle', methods=['POST'])
@login_required
def settle_project(project_id):
    """标记项目为已结清"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    project = Project.query.get_or_404(project_id)
    
    # 检查权限（业务员和执行者都可以标记结清）
    if project.confirmer_id != current_user.id and project.executor_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限操作此项目'})
    
    try:
        project.is_settled = True
        project.settle_time = datetime.utcnow()
        db.session.add(ProcessLog(
            project_type='software', project_id=project.id,
            action='settle', actor_id=current_user.id, actor_role='staff',
            from_status=None, to_status=project.status, note='标记为已结清'))
        db.session.commit()
        return jsonify({'success': True, 'message': '项目已标记为结清'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'})

@staff_bp.route('/project/<int:project_id>/unsettle', methods=['POST'])
@login_required
def unsettle_project(project_id):
    """取消项目结清标记"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    project = Project.query.get_or_404(project_id)
    
    # 检查权限
    if project.confirmer_id != current_user.id and project.executor_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限操作此项目'})
    
    # 如果已归档，不能取消结清
    if project.status == '已归档':
        return jsonify({'success': False, 'message': '已归档的项目不能取消结清'})
    
    try:
        project.is_settled = False
        project.settle_time = None
        db.session.add(ProcessLog(
            project_type='software', project_id=project.id,
            action='unsettle', actor_id=current_user.id, actor_role='staff',
            from_status=None, to_status=project.status, note='取消结清标记'))
        db.session.commit()
        return jsonify({'success': True, 'message': '已取消结清标记'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'})

@staff_bp.route('/project/<int:project_id>/update_serial', methods=['POST'])
@login_required
def update_serial_number(project_id):
    """更新项目流水号"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 检查更新流水号权限
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.update_serial_permission):
        return jsonify({'success': False, 'message': '您没有更新流水号的权限'})
    
    project = Project.query.get_or_404(project_id)
    serial_number = request.json.get('serial_number')
    
    if not serial_number:
        return jsonify({'success': False, 'message': '请提供流水号'})
    
    try:
        project.serial_number = serial_number
        if project.status == '已上传':
            project.status = '已获取流水号'
        
        db.session.commit()
        return jsonify({'success': True, 'message': '流水号更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '流水号更新失败，请重试'})

@staff_bp.route('/send_message', methods=['POST'])
@login_required
def send_message():
    """发送消息给用户"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    content = request.json.get('content')
    user_id = request.json.get('user_id')
    project_id = request.json.get('project_id')
    
    if not content:
        return jsonify({'success': False, 'message': '请输入消息内容'})
    
    try:
        new_message = Message(
            content=content,
            staff_id=current_user.id,
            user_id=user_id,
            project_id=project_id
        )
        
        db.session.add(new_message)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '消息发送成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '消息发送失败，请重试'})

@staff_bp.route('/assigned_projects')
@login_required
def assigned_projects():
    """查看所有分配给我的项目"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    # 检查是否为项目执行者
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.position == '项目执行者'):
        flash('您不是项目执行者', 'warning')
        return redirect(url_for('staff.business_dashboard'))
    
    # 获取分配给我的所有项目
    assigned_projects = Project.query.filter_by(executor_id=current_user.id).order_by(Project.execute_time.desc()).all()
    
    return render_template('staff/assigned_projects.html', assigned_projects=assigned_projects)

@staff_bp.route('/available_projects')
@login_required
def available_projects():
    """查看所有可接受的项目"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    # 检查是否为项目执行者
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.position == '项目执行者'):
        flash('您不是项目执行者', 'warning')
        return redirect(url_for('staff.business_dashboard'))
    
    # 获取待立项的项目（已确认但未分配执行者）
    available_projects = Project.query.filter_by(status='已确认', executor_id=None).order_by(Project.confirm_time.desc()).all()
    
    return render_template('staff/available_projects.html', available_projects=available_projects)

@staff_bp.route('/my_confirmed_projects')
@login_required
def my_confirmed_projects():
    """查看我确认的所有项目"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    # 获取我确认的所有项目（所有状态的）
    confirmed_projects = Project.query.filter_by(confirmer_id=current_user.id).order_by(Project.confirm_time.desc()).all()
    
    return render_template('staff/my_confirmed_projects.html', confirmed_projects=confirmed_projects)

@staff_bp.route('/approved_projects')
@login_required
def approved_projects_page():
    """查看所有已立项待执行的项目（未分配执行者）"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    # 如果是项目执行者，查看未分配的项目
    if hasattr(current_user, 'position') and current_user.position and current_user.position.position == '项目执行者':
        approved_projects = Project.query.filter_by(status='已立项', executor_id=None).order_by(Project.confirm_time.desc()).all()
    else:
        # 如果是业务员，查看自己确认的所有项目（包括已分配和未分配的）
        approved_projects = Project.query.filter_by(confirmer_id=current_user.id, status='已立项').order_by(Project.confirm_time.desc()).all()
    
    return render_template('staff/approved_projects.html', approved_projects=approved_projects)

@staff_bp.route('/apply_business', methods=['GET', 'POST'])
@login_required
def apply_business():
    """代客申请业务"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    # 获取系统设置
    customer_phone_required = SystemSettings.get_setting('apply_business_customer_phone_required', 'true').lower() == 'true'
    customer_email_required = SystemSettings.get_setting('apply_business_customer_email_required', 'true').lower() == 'true'
    
    if request.method == 'POST':
        # 获取客户信息
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        customer_id_number = request.form.get('customer_id_number')
        
        # 获取项目信息
        project_name = request.form.get('project_name')
        project_type = request.form.get('project_type')
        applicant_type = request.form.get('applicant_type')
        copyright_owner = request.form.get('copyright_owner')
        software_applicant_name = request.form.get('software_applicant_name')
        priority = request.form.get('priority', '普通')
        remarks = request.form.get('remarks')
        
        # 验证必填字段（根据系统设置）
        required_fields = [customer_name, project_name, project_type, applicant_type, copyright_owner]
        if customer_email_required:
            required_fields.append(customer_email)
        if customer_phone_required:
            required_fields.append(customer_phone)
        
        if not all(required_fields):
            missing_fields = []
            if not customer_name:
                missing_fields.append('客户姓名')
            if customer_email_required and not customer_email:
                missing_fields.append('客户邮箱')
            if customer_phone_required and not customer_phone:
                missing_fields.append('客户电话')
            if not project_name:
                missing_fields.append('项目名称')
            if not project_type:
                missing_fields.append('项目类型')
            if not applicant_type:
                missing_fields.append('申请人类型')
            if not copyright_owner:
                missing_fields.append('著作权人')
            flash(f'请填写所有必填字段：{", ".join(missing_fields)}', 'danger')
            return render_template('staff/apply_business.html', 
                                 customer_phone_required=customer_phone_required,
                                 customer_email_required=customer_email_required)
        
        try:
            # 检查客户是否已存在
            existing_user = User.query.filter_by(email=customer_email).first() if customer_email else None
            
            if not existing_user:
                # 创建新用户
                new_user = User(
                    name=customer_name,
                    email=customer_email or '',
                    phone=customer_phone or '',
                    id_number=customer_id_number or ''
                )
                # 设置默认密码为手机号后6位（如果有手机号），否则使用默认密码
                if customer_phone and len(customer_phone) >= 6:
                    default_password = customer_phone[-6:]
                else:
                    default_password = '123456'
                new_user.set_password(default_password)
                
                db.session.add(new_user)
                db.session.flush()  # 获取用户ID
                
                customer = new_user
                flash(f'已为客户创建账户，默认密码：{default_password}', 'info')
            else:
                customer = existing_user
                flash('客户账户已存在，使用现有账户', 'info')
            
            # 创建项目申请
            new_project = Project(
                project_name=project_name,
                project_type=project_type,
                applicant_type=applicant_type,
                copyright_owner=copyright_owner,
                software_applicant_name=software_applicant_name or customer_name,
                priority=priority,
                applicant_id=customer.id,
                confirmer_id=current_user.id,  # 直接设置确认者
                remarks=remarks,
                status='已确认',  # 代客申请直接进入已确认状态
                confirm_time=datetime.utcnow()
            )
            
            db.session.add(new_project)
            db.session.flush()  # 获取项目ID
            
            # 处理临时上传的文件
            temp_files = request.form.getlist('temp_files[]')
            if temp_files:
                temp_dir = os.path.join(current_app.static_folder, 'uploads', 'temp', str(current_user.id))
                project_dir = os.path.join(current_app.static_folder, 'uploads', 'projects', str(new_project.id))
                os.makedirs(project_dir, exist_ok=True)
                
                for temp_file_path in temp_files:
                    try:
                        # 构建临时文件完整路径
                        temp_full_path = os.path.join(current_app.static_folder, temp_file_path)
                        if os.path.exists(temp_full_path):
                            # 获取文件名
                            temp_filename = os.path.basename(temp_file_path)
                            # 生成新的唯一文件名
                            file_ext = os.path.splitext(temp_filename)[1]
                            unique_filename = f"{uuid.uuid4()}{file_ext}"
                            
                            # 移动到项目目录
                            new_file_path = os.path.join(project_dir, unique_filename)
                            shutil.move(temp_full_path, new_file_path)
                            
                            # 获取文件信息
                            file_size = os.path.getsize(new_file_path)
                            # 获取原始文件名
                            original_name = request.form.get(f'file_name_{temp_file_path}', temp_filename)
                            
                            # 获取文件类型
                            try:
                                file_type = original_name.rsplit('.', 1)[1].lower() if '.' in original_name else 'unknown'
                            except IndexError:
                                file_type = 'unknown'
                            
                            # 创建文件记录
                            project_file = ProjectFile(
                                project_id=new_project.id,
                                project_type='software',
                                file_name=original_name,
                                file_path=os.path.join('uploads', 'projects', str(new_project.id), unique_filename),
                                file_type=file_type,
                                file_size=file_size,
                                uploader_id=customer.id,
                                file_category=request.form.get(f'file_category_{temp_file_path}', '其他文件')
                            )
                            db.session.add(project_file)
                    except Exception as e:
                        current_app.logger.error(f"处理临时文件失败: {str(e)}")
                        import traceback
                        current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
                        # 继续处理其他文件
            
            db.session.commit()
            
            flash('代客申请提交成功，项目已进入确认状态', 'success')
            return redirect(url_for('staff.business_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('代客申请提交失败，请重试', 'danger')
    
    return render_template('staff/apply_business.html',
                         customer_phone_required=customer_phone_required,
                         customer_email_required=customer_email_required)

@staff_bp.route('/project_query')
@login_required
def project_query():
    """项目查询页面"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('staff/project_query.html')

@staff_bp.route('/user_management')
@login_required
def user_management():
    """系统管理员用户管理页面"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    # 检查是否为系统管理员
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.position == '系统管理员'):
        flash('您不是系统管理员，无权访问此页面', 'danger')
        return redirect(url_for('staff.business_dashboard'))
    
    # 获取待审核的员工账号
    pending_staff = Staff.query.filter_by(approval_status='pending').order_by(Staff.register_date.desc()).all()

    # 获取已审核通过的员工账号
    approved_staff = Staff.query.filter_by(approval_status='approved').order_by(Staff.register_date.desc()).all()
    
    # 获取所有普通用户
    all_users = User.query.order_by(User.register_time.desc()).all()
    
    return render_template('staff/user_management.html',
                         pending_staff=pending_staff,
                         approved_staff=approved_staff,
                         all_users=all_users)

@staff_bp.route('/system_settings', methods=['GET', 'POST'])
@login_required
def system_settings():
    """系统设置页面（仅系统管理员）"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    # 检查是否为系统管理员
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.position == '系统管理员'):
        flash('您不是系统管理员，无权访问此页面', 'danger')
        return redirect(url_for('staff.business_dashboard'))
    
    if request.method == 'POST':
        # 更新设置
        customer_phone_required = request.form.get('customer_phone_required', 'false')
        customer_email_required = request.form.get('customer_email_required', 'false')
        
        try:
            SystemSettings.set_setting(
                'apply_business_customer_phone_required',
                customer_phone_required,
                '代客申请时客户电话是否必填',
                current_user.id
            )
            SystemSettings.set_setting(
                'apply_business_customer_email_required',
                customer_email_required,
                '代客申请时客户邮箱是否必填',
                current_user.id
            )
            flash('设置已保存', 'success')
            return redirect(url_for('staff.system_settings'))
        except Exception as e:
            db.session.rollback()
            flash('保存设置失败，请重试', 'danger')
    
    # 获取当前设置
    customer_phone_required = SystemSettings.get_setting('apply_business_customer_phone_required', 'true').lower() == 'true'
    customer_email_required = SystemSettings.get_setting('apply_business_customer_email_required', 'true').lower() == 'true'
    
    return render_template('staff/system_settings.html',
                         customer_phone_required=customer_phone_required,
                         customer_email_required=customer_email_required)

@staff_bp.route('/approve_staff/<int:staff_id>', methods=['POST'])
@login_required
def approve_staff(staff_id):
    """审核通过员工账号"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 检查是否为系统管理员
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.position == '系统管理员'):
        return jsonify({'success': False, 'message': '您不是系统管理员，无权执行此操作'})
    
    staff = Staff.query.get_or_404(staff_id)
    
    if staff.approval_status != 'pending':
        return jsonify({'success': False, 'message': '该账号状态不允许此操作'})
    
    try:
        staff.approval_status = 'approved'
        staff.approval_date = datetime.utcnow()
        staff.approver_id = current_user.id
        
        # 如果没有分配权限，默认分配普通业务员权限
        if not staff.position_id:
            default_permission = Permission.query.filter_by(position='普通业务员').first()
            if default_permission:
                staff.position_id = default_permission.id
        
        db.session.commit()
        # 发送审核通过通知邮件
        try:
            from web_app.utils.email import send_staff_approval_notification
        except ImportError:
            # 若不能在此导入, 假设send_staff_approval_notification已在其他地方导入
            pass

        try:
            # 调用邮件发送函数，给员工发送审核通过通知
            send_staff_approval_notification(staff)
        except Exception as mail_exc:
            # 邮件发送失败也不影响业务主流程
            pass
        
        return jsonify({'success': True, 'message': '员工账号审核通过'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'})

@staff_bp.route('/reject_staff/<int:staff_id>', methods=['POST'])
@login_required
def reject_staff(staff_id):
    """驳回员工账号"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 检查是否为系统管理员
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.position == '系统管理员'):
        return jsonify({'success': False, 'message': '您不是系统管理员，无权执行此操作'})
    
    staff = Staff.query.get_or_404(staff_id)
    
    if staff.approval_status != 'pending':
        return jsonify({'success': False, 'message': '该账号状态不允许此操作'})
    
    data = request.get_json() or {}
    rejection_reason = data.get('rejection_reason', '').strip()
    
    if not rejection_reason:
        return jsonify({'success': False, 'message': '请输入驳回原因'})
    
    try:
        staff.approval_status = 'rejected'
        staff.approval_date = datetime.utcnow()
        staff.approver_id = current_user.id
        staff.approval_remarks = rejection_reason
        
        db.session.commit()
        try:
            from web_app.utils.email import send_staff_rejection_notification
        except ImportError:
            # 若不能在此导入, 假设send_staff_rejection_notification已在其他地方导入
            pass

        try:
            # 调用邮件发送函数，给员工发送账号驳回通知
            send_staff_rejection_notification(staff, rejection_reason)
        except Exception as mail_exc:
            # 邮件发送失败也不影响业务主流程
            pass
        
        return jsonify({'success': True, 'message': '员工账号已驳回'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'})

@staff_bp.route('/reapply_staff/<int:staff_id>', methods=['POST'])
@login_required
def reapply_staff(staff_id):
    """员工重新申请"""
    staff = Staff.query.get_or_404(staff_id)
    
    if staff.approval_status != 'rejected':
        return jsonify({'success': False, 'message': '该账号状态不允许此操作'})
    
    data = request.get_json() or {}
    new_reason = data.get('application_reason', '').strip()
    
    if not new_reason:
        return jsonify({'success': False, 'message': '请填写申请理由'})
    
    try:
        staff.approval_status = 'pending'
        staff.application_reason = new_reason
        staff.approval_date = None
        staff.approver_id = None
        staff.approval_remarks = None
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '重新申请成功，等待审核'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'})

@staff_bp.route('/cancel_staff/<int:staff_id>', methods=['POST'])
@login_required
def cancel_staff(staff_id):
    """员工取消申请"""
    staff = Staff.query.get_or_404(staff_id)
    
    if staff.approval_status not in ['pending', 'rejected']:
        return jsonify({'success': False, 'message': '该账号状态不允许此操作'})
    
    try:
        db.session.delete(staff)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '申请已取消'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'})

@staff_bp.route('/assign_permission/<int:staff_id>', methods=['POST'])
@login_required
def assign_permission(staff_id):
    """为员工分配权限"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 检查是否为系统管理员
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.position == '系统管理员'):
        return jsonify({'success': False, 'message': '您不是系统管理员，无权执行此操作'})
    
    staff = Staff.query.get_or_404(staff_id)
    
    if staff.approval_status != 'approved':
        return jsonify({'success': False, 'message': '该账号状态不允许此操作'})
    
    data = request.get_json() or {}
    permission_id = data.get('permission_id')
    
    if not permission_id:
        return jsonify({'success': False, 'message': '请选择权限'})
    
    try:
        permission = Permission.query.get_or_404(permission_id)
        staff.position_id = permission_id
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'已分配{permission.position}权限'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'})

@staff_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """删除普通用户"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 检查是否为系统管理员
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.position == '系统管理员'):
        return jsonify({'success': False, 'message': '您不是系统管理员，无权执行此操作'})
    
    user = User.query.get_or_404(user_id)
    
    try:
        # 检查用户是否有相关项目
        project_count = Project.query.filter_by(applicant_id=user_id).count()
        
        if project_count > 0:
            return jsonify({
                'success': False, 
                'message': f'该用户有 {project_count} 个相关项目，无法删除。请先处理相关项目。'
            })
        
        # 删除用户
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '用户删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '删除失败，请重试'})

@staff_bp.route('/delete_staff/<int:staff_id>', methods=['POST'])
@login_required
def delete_staff(staff_id):
    """删除员工账号"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 检查是否为系统管理员
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.position == '系统管理员'):
        return jsonify({'success': False, 'message': '您不是系统管理员，无权执行此操作'})
    
    # 不能删除自己
    if staff_id == current_user.id:
        return jsonify({'success': False, 'message': '不能删除自己的账号'})
    
    staff = Staff.query.get_or_404(staff_id)
    
    try:
        # 检查员工是否有相关项目
        project_count = Project.query.filter(
            db.or_(Project.confirmer_id == staff_id, Project.executor_id == staff_id)
        ).count()
        
        if project_count > 0:
            return jsonify({
                'success': False, 
                'message': f'该员工有 {project_count} 个相关项目，无法删除。请先处理相关项目。'
            })
        
        # 删除员工
        db.session.delete(staff)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '员工删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '删除失败，请重试'})

# ==================== 文件上传和下载相关路由 ====================

@staff_bp.route('/project/<int:project_id>/upload', methods=['POST'])
@login_required
def upload_project_file(project_id):
    """上传项目文件"""
    try:
        # 检查项目是否存在
        project = Project.query.get_or_404(project_id)
        
        # 检查权限（业务员可以上传）
        if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': '不支持的文件类型'})
        
        # 检查文件大小
        is_valid_size, file_size = check_file_size(file)
        if not is_valid_size:
            size_mb = file_size / (1024 * 1024)
            return jsonify({
                'success': False, 
                'message': f'文件大小超过限制（{size_mb:.2f}MB），单个文件不能超过16MB'
            })
        
        # 生成安全的文件名
        original_filename = file.filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # 确保上传目录存在
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'projects', str(project_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 获取文件分类
        file_category = request.form.get('file_category', '其他文件')
        
        # 生成相对路径用于数据库存储
        relative_path = os.path.join('uploads', 'projects', str(project_id), unique_filename)
        
        # 获取文件类型
        try:
            file_type = filename.rsplit('.', 1)[1].lower()
        except IndexError:
            file_type = 'unknown'
        
        # 保存文件记录到数据库
        project_file = ProjectFile(
            project_id=project_id,
            project_type='software',
            file_name=original_filename,  # 存储原始文件名
            file_path=relative_path,  # 存储相对路径
            file_type=file_type,
            file_size=file_size,
            uploader_id=project.applicant_id,  # 使用项目申请人的ID
            file_category=file_category
        )
        
        db.session.add(project_file)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '文件上传成功',
            'file': {
                'id': project_file.id,
                'name': original_filename,
                'size': file_size,
                'type': project_file.file_type,
                'category': file_category,
                'upload_time': project_file.upload_time.strftime('%Y-%m-%d %H:%M:%S')
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"文件上传失败: {str(e)}")
        import traceback
        current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'文件上传失败: {str(e)}'})

@staff_bp.route('/project/<int:project_id>/file/<int:file_id>/download')
@login_required
def download_project_file(project_id, file_id):
    """下载项目文件"""
    try:
        # 检查项目是否存在
        project = Project.query.get_or_404(project_id)
        
        # 检查权限
        if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        # 获取文件记录
        project_file = ProjectFile.query.filter_by(
            id=file_id, 
            project_id=project_id, 
            project_type='software'
        ).first_or_404()
        
        # 构建文件完整路径
        file_path = os.path.join(current_app.static_folder, project_file.file_path)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': '文件不存在'})
        
        # 发送文件
        return send_file(
            file_path,
            as_attachment=True,
            download_name=project_file.file_name,
            mimetype=mimetypes.guess_type(project_file.file_name)[0] or 'application/octet-stream'
        )
        
    except Exception as e:
        current_app.logger.error(f"文件下载失败: {str(e)}")
        return jsonify({'success': False, 'message': f'文件下载失败: {str(e)}'})

@staff_bp.route('/apply_business/upload', methods=['POST'])
@login_required
def upload_apply_business_file():
    """代客申请时上传文件（临时存储，提交申请后关联到项目）"""
    try:
        # 检查权限
        if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': '不支持的文件类型'})
        
        # 检查文件大小
        is_valid_size, file_size = check_file_size(file)
        if not is_valid_size:
            size_mb = file_size / (1024 * 1024)
            return jsonify({
                'success': False, 
                'message': f'文件大小超过限制（{size_mb:.2f}MB），单个文件不能超过16MB'
            })
        
        # 生成安全的文件名
        original_filename = file.filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # 临时存储目录（使用session ID或用户ID）
        temp_dir = os.path.join(current_app.static_folder, 'uploads', 'temp', str(current_user.id))
        os.makedirs(temp_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(temp_dir, unique_filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 获取文件分类
        file_category = request.form.get('file_category', '其他文件')
        
        # 返回临时文件信息（存储在session中，提交申请时关联到项目）
        return jsonify({
            'success': True,
            'message': '文件上传成功',
            'file': {
                'temp_path': os.path.join('uploads', 'temp', str(current_user.id), unique_filename),
                'original_name': original_filename,
                'size': file_size,
                'category': file_category
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"文件上传失败: {str(e)}")
        import traceback
        current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'文件上传失败: {str(e)}'})
