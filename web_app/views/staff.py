from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, Project, Message, User, Staff
from werkzeug.security import generate_password_hash

staff_bp = Blueprint('staff', __name__)

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
        'completed_count': len([p for p in confirmed_projects if p.status in ['已完成', '已上传', '已获取流水号', '证书完成', '已结清', '已归档']])
    }
    
    # 获取最近的消息
    recent_messages = Message.query.filter_by(staff_id=current_user.id).order_by(Message.create_time.desc()).limit(5).all()
    
    return render_template('staff/business_dashboard.html',
                         pending_projects=pending_projects,
                         confirmed_projects=confirmed_projects,
                         stats=stats,
                         recent_messages=recent_messages)

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
    assigned_projects = Project.query.filter_by(executor_id=current_user.id).order_by(Project.execute_time.desc()).all()
    
    # 获取待立项的项目（已确认但未分配执行者）
    available_projects = Project.query.filter_by(status='已立项', executor_id=None).order_by(Project.confirm_time.desc()).all()
    
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
    
    return render_template('staff/project_detail.html',
                         project=project,
                         applicant=applicant,
                         messages=project_messages)

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
        project.status = '已确认'
        project.confirmer_id = current_user.id
        project.confirm_time = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'message': '项目确认成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '确认失败，请重试'})

@staff_bp.route('/project/<int:project_id>/approve', methods=['POST'])
@login_required
def approve_project(project_id):
    """立项申请"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    project = Project.query.get_or_404(project_id)
    
    if project.status != '已确认':
        return jsonify({'success': False, 'message': '项目状态不允许此操作'})
    
    try:
        project.status = '已立项'
        db.session.commit()
        return jsonify({'success': True, 'message': '立项申请成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '立项申请失败，请重试'})

@staff_bp.route('/project/<int:project_id>/take', methods=['POST'])
@login_required
def take_project(project_id):
    """接受项目执行"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 检查是否为项目执行者
    if not (hasattr(current_user, 'position') and current_user.position and current_user.position.position == '项目执行者'):
        return jsonify({'success': False, 'message': '您不是项目执行者'})
    
    project = Project.query.get_or_404(project_id)
    
    if project.status != '已立项' or project.executor_id is not None:
        return jsonify({'success': False, 'message': '项目状态不允许此操作'})
    
    try:
        project.executor_id = current_user.id
        project.execute_time = datetime.utcnow()
        project.status = '执行中'
        
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
        project.status = '已完成'
        project.complete_time = datetime.utcnow()
        
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
    
    # 状态转换逻辑
    valid_statuses = ['已完成', '已上传', '已获取流水号', '证书完成', '已结清', '已归档']
    
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': '无效的状态'})
    
    try:
        project.status = new_status
        
        # 更新相应的时间字段
        if new_status == '已上传':
            project.submit_time = datetime.utcnow()
        elif new_status == '证书完成':
            project.certificate_time = datetime.utcnow()
        elif new_status == '已结清':
            project.settle_time = datetime.utcnow()
        
        db.session.commit()
        return jsonify({'success': True, 'message': '状态更新成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '状态更新失败，请重试'})

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

@staff_bp.route('/apply_business', methods=['GET', 'POST'])
@login_required
def apply_business():
    """代客申请业务"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
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
        
        # 验证必填字段
        if not all([customer_name, customer_email, customer_phone, project_name, project_type, applicant_type, copyright_owner]):
            flash('请填写所有必填字段', 'danger')
            return render_template('staff/apply_business.html')
        
        try:
            # 检查客户是否已存在
            existing_user = User.query.filter_by(email=customer_email).first()
            
            if not existing_user:
                # 创建新用户
                new_user = User(
                    name=customer_name,
                    email=customer_email,
                    phone=customer_phone,
                    id_number=customer_id_number
                )
                # 设置默认密码为手机号后6位
                default_password = customer_phone[-6:] if len(customer_phone) >= 6 else '123456'
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
            db.session.commit()
            
            flash('代客申请提交成功，项目已进入确认状态', 'success')
            return redirect(url_for('staff.business_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('代客申请提交失败，请重试', 'danger')
    
    return render_template('staff/apply_business.html')
