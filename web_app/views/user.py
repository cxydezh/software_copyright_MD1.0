from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, Project, Message

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """用户仪表板"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'user':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    # 获取用户的项目
    user_projects = Project.query.filter_by(applicant_id=current_user.id).order_by(Project.apply_time.desc()).all()
    
    # 统计信息
    stats = {
        'total_projects': len(user_projects),
        'pending_projects': len([p for p in user_projects if p.status in ['待确认', '已确认', '已立项', '执行中']]),
        'completed_projects': len([p for p in user_projects if p.status in ['已完成', '已上传', '已获取流水号', '证书完成']]),
        'archived_projects': len([p for p in user_projects if p.status == '已归档'])
    }
    
    # 获取最近的消息
    recent_messages = Message.query.filter_by(user_id=current_user.id).order_by(Message.create_time.desc()).limit(5).all()
    
    return render_template('user/dashboard.html', 
                         projects=user_projects, 
                         stats=stats,
                         recent_messages=recent_messages)

@user_bp.route('/apply_project', methods=['GET', 'POST'])
@login_required
def apply_project():
    """申请新项目"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'user':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        project_type = request.form.get('project_type')
        applicant_type = request.form.get('applicant_type')
        copyright_owner = request.form.get('copyright_owner')
        software_applicant_name = request.form.get('software_applicant_name')
        priority = request.form.get('priority', '普通')
        remarks = request.form.get('remarks')
        
        # 验证必填字段
        if not all([project_name, project_type, applicant_type, copyright_owner]):
            flash('请填写所有必填字段', 'danger')
            return render_template('user/apply_project.html')
        
        try:
            new_project = Project(
                project_name=project_name,
                project_type=project_type,
                applicant_type=applicant_type,
                copyright_owner=copyright_owner,
                software_applicant_name=software_applicant_name or current_user.name,
                priority=priority,
                applicant_id=current_user.id,
                remarks=remarks,
                status='待确认'
            )
            
            db.session.add(new_project)
            db.session.commit()
            
            flash('项目申请提交成功', 'success')
            return redirect(url_for('user.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('项目申请提交失败，请重试', 'danger')
    
    # 项目类型选项
    project_types = ['软件登记业务', '软件设计与登记业务', '软件部署与登记业务']
    applicant_types = ['个人', '事业单位', '事业单位联合个人', '自然人联合']
    priorities = ['普通', '加急', '快速']
    
    return render_template('user/apply_project.html',
                         project_types=project_types,
                         applicant_types=applicant_types,
                         priorities=priorities)

@user_bp.route('/project/<int:project_id>')
@login_required
def project_detail(project_id):
    """项目详情"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'user':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    project = Project.query.get_or_404(project_id)
    
    # 检查权限
    if project.applicant_id != current_user.id:
        flash('您没有权限查看此项目', 'danger')
        return redirect(url_for('user.dashboard'))
    
    # 获取项目相关的消息
    project_messages = Message.query.filter_by(project_id=project_id).order_by(Message.create_time.desc()).all()
    
    return render_template('user/project_detail.html', 
                         project=project,
                         messages=project_messages)

@user_bp.route('/project/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """编辑项目"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'user':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    project = Project.query.get_or_404(project_id)
    
    # 检查权限和状态
    if project.applicant_id != current_user.id:
        flash('您没有权限编辑此项目', 'danger')
        return redirect(url_for('user.dashboard'))
    
    if project.status not in ['待确认']:
        flash('项目已进入处理流程，无法编辑', 'warning')
        return redirect(url_for('user.project_detail', project_id=project_id))
    
    if request.method == 'POST':
        project.project_name = request.form.get('project_name')
        project.project_type = request.form.get('project_type')
        project.applicant_type = request.form.get('applicant_type')
        project.copyright_owner = request.form.get('copyright_owner')
        project.software_applicant_name = request.form.get('software_applicant_name')
        project.priority = request.form.get('priority', '普通')
        project.remarks = request.form.get('remarks')
        
        try:
            db.session.commit()
            flash('项目信息更新成功', 'success')
            return redirect(url_for('user.project_detail', project_id=project_id))
        except Exception as e:
            db.session.rollback()
            flash('项目信息更新失败，请重试', 'danger')
    
    # 项目类型选项
    project_types = ['软件登记业务', '软件设计与登记业务', '软件部署与登记业务']
    applicant_types = ['个人', '事业单位', '事业单位联合个人', '自然人联合']
    priorities = ['普通', '加急', '快速']
    
    return render_template('user/edit_project.html',
                         project=project,
                         project_types=project_types,
                         applicant_types=applicant_types,
                         priorities=priorities)

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """用户资料"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'user':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        current_user.name = request.form.get('name')
        current_user.phone = request.form.get('phone')
        current_user.gender = request.form.get('gender')
        current_user.id_number = request.form.get('id_number')
        
        # 如果提供了新密码，则更新密码
        new_password = request.form.get('new_password')
        if new_password:
            current_password = request.form.get('current_password')
            if not current_user.check_password(current_password):
                flash('当前密码错误', 'danger')
                return render_template('user/profile.html')
            
            confirm_password = request.form.get('confirm_password')
            if new_password != confirm_password:
                flash('新密码确认不一致', 'danger')
                return render_template('user/profile.html')
            
            current_user.set_password(new_password)
        
        try:
            db.session.commit()
            flash('资料更新成功', 'success')
        except Exception as e:
            db.session.rollback()
            flash('资料更新失败，请重试', 'danger')
    
    return render_template('user/profile.html')
