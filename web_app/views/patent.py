#!/usr/bin/env python3
"""
专利申请和保护相关视图
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from database.models import db, PatentProject, User, Staff, ProjectFile
from datetime import datetime
import os
import uuid

patent_bp = Blueprint('patent', __name__, url_prefix='/patent')

# 文件大小限制（16MB）
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def check_file_size(file):
    """检查文件大小是否在限制内"""
    # 获取文件大小（通过读取文件流位置）
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # 重置文件指针
    return file_size <= MAX_FILE_SIZE, file_size

@patent_bp.route('/')
@login_required
def index():
    """专利申请首页"""
    if current_user.is_authenticated and hasattr(current_user, 'id'):
        # 获取用户的专利项目
        user_patents = PatentProject.query.filter_by(applicant_id=current_user.id).order_by(PatentProject.apply_time.desc()).all()
        
        # 统计信息
        total_patents = len(user_patents)
        pending_patents = len([p for p in user_patents if p.status == '待确认'])
        in_progress_patents = len([p for p in user_patents if p.status in ['已确认', '准备中', '已递交', '审查中']])
        completed_patents = len([p for p in user_patents if p.status in ['已授权', '维持中', '已完成']])
        
        return render_template('patent/index.html',
                             patents=user_patents,
                             total_patents=total_patents,
                             pending_patents=pending_patents,
                             in_progress_patents=in_progress_patents,
                             completed_patents=completed_patents)
    else:
        flash('请先登录', 'warning')
        return redirect(url_for('auth.login'))

@patent_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    """专利项目申请"""
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        project_type = request.form.get('project_type')
        applicant_type = request.form.get('applicant_type')
        application_field = request.form.get('application_field')
        invention_title = request.form.get('invention_title')
        technical_field = request.form.get('technical_field')
        remarks = request.form.get('remarks')
        
        # 验证必填字段
        if not all([project_name, project_type, applicant_type, application_field]):
            flash('请填写所有必填字段', 'danger')
            return render_template('patent/apply.html')
        
        try:
            # 创建专利项目
            new_patent = PatentProject(
                project_name=project_name,
                project_type=project_type,
                applicant_type=applicant_type,
                application_field=application_field,
                invention_title=invention_title,
                technical_field=technical_field,
                remarks=remarks,
                applicant_id=current_user.id,
                status='待确认'
            )
            
            db.session.add(new_patent)
            db.session.commit()
            
            flash('专利项目申请提交成功！我们将在1-2个工作日内与您联系。', 'success')
            return redirect(url_for('patent.detail', patent_id=new_patent.id))
            
        except Exception as e:
            db.session.rollback()
            flash('申请提交失败，请重试', 'danger')
            current_app.logger.error(f"专利申请失败: {e}")
    
    return render_template('patent/apply.html')

@patent_bp.route('/<int:patent_id>')
@login_required
def detail(patent_id):
    """专利项目详情"""
    patent = PatentProject.query.get_or_404(patent_id)
    
    # 检查权限
    if patent.applicant_id != current_user.id and not (hasattr(current_user, 'position_id') and current_user.position_id):
        flash('您没有权限查看此项目', 'danger')
        return redirect(url_for('patent.index'))
    
    # 获取项目文件
    files = ProjectFile.query.filter_by(project_id=patent_id, project_type='patent').order_by(ProjectFile.upload_time.desc()).all()
    
    return render_template('patent/detail.html', patent=patent, files=files)

@patent_bp.route('/<int:patent_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(patent_id):
    """编辑专利项目"""
    patent = PatentProject.query.get_or_404(patent_id)
    
    # 检查权限
    if patent.applicant_id != current_user.id:
        flash('您没有权限编辑此项目', 'danger')
        return redirect(url_for('patent.detail', patent_id=patent_id))
    
    # 检查状态
    if patent.status not in ['待确认', '已确认']:
        flash('项目已开始执行，无法编辑', 'warning')
        return redirect(url_for('patent.detail', patent_id=patent_id))
    
    if request.method == 'POST':
        patent.project_name = request.form.get('project_name', patent.project_name)
        patent.invention_title = request.form.get('invention_title', patent.invention_title)
        patent.technical_field = request.form.get('technical_field', patent.technical_field)
        patent.remarks = request.form.get('remarks', patent.remarks)
        
        try:
            db.session.commit()
            flash('项目信息更新成功', 'success')
            return redirect(url_for('patent.detail', patent_id=patent_id))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试', 'danger')
            current_app.logger.error(f"专利项目更新失败: {e}")
    
    return render_template('patent/edit.html', patent=patent)

@patent_bp.route('/<int:patent_id>/upload', methods=['POST'])
@login_required
def upload_file(patent_id):
    """上传项目文件"""
    patent = PatentProject.query.get_or_404(patent_id)
    
    # 检查权限
    if patent.applicant_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限上传文件'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    if file:
        try:
            # 检查文件大小
            is_valid_size, file_size = check_file_size(file)
            if not is_valid_size:
                size_mb = file_size / (1024 * 1024)
                return jsonify({
                    'success': False, 
                    'message': f'文件大小超过限制（{size_mb:.2f}MB），单个文件不能超过16MB'
                })
            
            # 生成唯一文件名
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            
            # 创建上传目录
            upload_dir = os.path.join(current_app.static_folder, 'uploads', 'patents', str(patent_id))
            os.makedirs(upload_dir, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # 保存文件记录
            project_file = ProjectFile(
                project_id=patent_id,
                project_type='patent',
                file_name=file.filename,
                file_path=file_path,
                file_type=file_extension[1:].lower(),
                file_size=os.path.getsize(file_path),
                uploader_id=current_user.id,
                file_category=request.form.get('file_category', '其他文件')
            )
            
            db.session.add(project_file)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': '文件上传成功',
                'file_id': project_file.id,
                'file_name': project_file.file_name
            })
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"文件上传失败: {e}")
            return jsonify({'success': False, 'message': '文件上传失败'})
    
    return jsonify({'success': False, 'message': '文件上传失败'})

@patent_bp.route('/<int:patent_id>/delete_file/<int:file_id>', methods=['POST'])
@login_required
def delete_file(patent_id, file_id):
    """删除项目文件"""
    patent = PatentProject.query.get_or_404(patent_id)
    project_file = ProjectFile.query.get_or_404(file_id)
    
    # 检查权限
    if patent.applicant_id != current_user.id or project_file.project_id != patent_id:
        return jsonify({'success': False, 'message': '您没有权限删除此文件'})
    
    try:
        # 删除物理文件
        if os.path.exists(project_file.file_path):
            os.remove(project_file.file_path)
        
        # 删除数据库记录
        db.session.delete(project_file)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '文件删除成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"文件删除失败: {e}")
        return jsonify({'success': False, 'message': '文件删除失败'})

@patent_bp.route('/staff')
@login_required
def staff_dashboard():
    """员工专利管理面板"""
    # 检查是否为员工
    if not (hasattr(current_user, 'position_id') and current_user.position_id):
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('patent.index'))
    
    # 获取待处理的专利项目
    pending_patents = PatentProject.query.filter_by(status='待确认').order_by(PatentProject.apply_time.desc()).all()
    
    # 获取已确认的专利项目
    confirmed_patents = PatentProject.query.filter_by(status='已确认').order_by(PatentProject.confirm_time.desc()).all()
    
    # 获取进行中的专利项目
    in_progress_patents = PatentProject.query.filter(
        PatentProject.status.in_(['准备中', '已递交', '审查中'])
    ).order_by(PatentProject.start_time.desc()).all()
    
    return render_template('patent/staff_dashboard.html',
                         pending_patents=pending_patents,
                         confirmed_patents=confirmed_patents,
                         in_progress_patents=in_progress_patents)

@patent_bp.route('/<int:patent_id>/confirm', methods=['POST'])
@login_required
def confirm_patent(patent_id):
    """确认专利项目"""
    # 检查是否为员工
    if not (hasattr(current_user, 'position_id') and current_user.position_id):
        return jsonify({'success': False, 'message': '您没有权限执行此操作'})
    
    patent = PatentProject.query.get_or_404(patent_id)
    
    if patent.status != '待确认':
        return jsonify({'success': False, 'message': '项目状态不正确'})
    
    try:
        patent.status = '已确认'
        patent.confirm_time = datetime.utcnow()
        patent.confirmer_id = current_user.id
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '项目确认成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"项目确认失败: {e}")
        return jsonify({'success': False, 'message': '项目确认失败'})

@patent_bp.route('/<int:patent_id>/assign_executor', methods=['POST'])
@login_required
def assign_executor(patent_id):
    """分配执行者"""
    # 检查是否为员工
    if not (hasattr(current_user, 'position_id') and current_user.position_id):
        return jsonify({'success': False, 'message': '您没有权限执行此操作'})
    
    patent = PatentProject.query.get_or_404(patent_id)
    executor_id = request.json.get('executor_id')
    
    if not executor_id:
        return jsonify({'success': False, 'message': '请选择执行者'})
    
    try:
        patent.executor_id = executor_id
        patent.status = '准备中'
        patent.start_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '执行者分配成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"执行者分配失败: {e}")
        return jsonify({'success': False, 'message': '执行者分配失败'})

@patent_bp.route('/<int:patent_id>/update_status', methods=['POST'])
@login_required
def update_status(patent_id):
    """更新项目状态"""
    # 检查是否为员工
    if not (hasattr(current_user, 'position_id') and current_user.position_id):
        return jsonify({'success': False, 'message': '您没有权限执行此操作'})
    
    patent = PatentProject.query.get_or_404(patent_id)
    new_status = request.json.get('status')
    
    if not new_status:
        return jsonify({'success': False, 'message': '请选择新状态'})
    
    try:
        patent.status = new_status
        
        # 根据状态更新时间字段
        if new_status == '已递交':
            patent.file_time = datetime.utcnow()
        elif new_status == '公开':
            patent.publish_time = datetime.utcnow()
        elif new_status == '已授权':
            patent.grant_time = datetime.utcnow()
        elif new_status == '已完成':
            patent.grant_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '状态更新成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"状态更新失败: {e}")
        return jsonify({'success': False, 'message': '状态更新失败'})

@patent_bp.route('/<int:patent_id>/update_patent_info', methods=['POST'])
@login_required
def update_patent_info(patent_id):
    """更新专利信息（申请号、公开号等）"""
    # 检查是否为员工
    if not (hasattr(current_user, 'position_id') and current_user.position_id):
        return jsonify({'success': False, 'message': '您没有权限执行此操作'})
    
    patent = PatentProject.query.get_or_404(patent_id)
    
    try:
        data = request.json
        if 'application_number' in data:
            patent.application_number = data['application_number']
        if 'publication_number' in data:
            patent.publication_number = data['publication_number']
        if 'patent_number' in data:
            patent.patent_number = data['patent_number']
        if 'patent_status' in data:
            patent.patent_status = data['patent_status']
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '专利信息更新成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"专利信息更新失败: {e}")
        return jsonify({'success': False, 'message': '专利信息更新失败'})
