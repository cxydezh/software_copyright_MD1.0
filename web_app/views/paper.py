#!/usr/bin/env python3
"""
论文指导和发表相关视图
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from database.models import db, PaperProject, User, Staff, ProjectFile
from datetime import datetime
import os
import uuid

paper_bp = Blueprint('paper', __name__, url_prefix='/paper')

@paper_bp.route('/')
@login_required
def index():
    """论文指导首页"""
    if current_user.is_authenticated and hasattr(current_user, 'id'):
        # 获取用户的论文项目
        user_papers = PaperProject.query.filter_by(applicant_id=current_user.id).order_by(PaperProject.apply_time.desc()).all()
        
        # 统计信息
        total_papers = len(user_papers)
        pending_papers = len([p for p in user_papers if p.status == '待确认'])
        in_progress_papers = len([p for p in user_papers if p.status in ['已确认', '进行中', '已投稿', '审稿中']])
        completed_papers = len([p for p in user_papers if p.status in ['已录用', '已发表', '已完成']])
        
        return render_template('paper/index.html',
                             papers=user_papers,
                             total_papers=total_papers,
                             pending_papers=pending_papers,
                             in_progress_papers=in_progress_papers,
                             completed_papers=completed_papers)
    else:
        flash('请先登录', 'warning')
        return redirect(url_for('auth.login'))

@paper_bp.route('/apply', methods=['GET', 'POST'])
@login_required
def apply():
    """论文项目申请"""
    if request.method == 'POST':
        project_name = request.form.get('project_name')
        project_type = request.form.get('project_type')
        service_level = request.form.get('service_level')
        applicant_type = request.form.get('applicant_type')
        paper_title = request.form.get('paper_title')
        research_field = request.form.get('research_field')
        target_journal = request.form.get('target_journal')
        remarks = request.form.get('remarks')
        
        # 验证必填字段
        if not all([project_name, project_type, service_level, applicant_type]):
            flash('请填写所有必填字段', 'danger')
            return render_template('paper/apply.html')
        
        try:
            # 创建论文项目
            new_paper = PaperProject(
                project_name=project_name,
                project_type=project_type,
                service_level=service_level,
                applicant_type=applicant_type,
                paper_title=paper_title,
                research_field=research_field,
                target_journal=target_journal,
                remarks=remarks,
                applicant_id=current_user.id,
                status='待确认'
            )
            
            db.session.add(new_paper)
            db.session.commit()
            
            flash('论文项目申请提交成功！我们将在1-2个工作日内与您联系。', 'success')
            return redirect(url_for('paper.detail', paper_id=new_paper.id))
            
        except Exception as e:
            db.session.rollback()
            flash('申请提交失败，请重试', 'danger')
            current_app.logger.error(f"论文申请失败: {e}")
    
    return render_template('paper/apply.html')

@paper_bp.route('/<int:paper_id>')
@login_required
def detail(paper_id):
    """论文项目详情"""
    paper = PaperProject.query.get_or_404(paper_id)
    
    # 检查权限
    if paper.applicant_id != current_user.id and not (hasattr(current_user, 'position_id') and current_user.position_id):
        flash('您没有权限查看此项目', 'danger')
        return redirect(url_for('paper.index'))
    
    # 获取项目文件
    files = ProjectFile.query.filter_by(project_id=paper_id, project_type='paper').order_by(ProjectFile.upload_time.desc()).all()
    
    return render_template('paper/detail.html', paper=paper, files=files)

@paper_bp.route('/<int:paper_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(paper_id):
    """编辑论文项目"""
    paper = PaperProject.query.get_or_404(paper_id)
    
    # 检查权限
    if paper.applicant_id != current_user.id:
        flash('您没有权限编辑此项目', 'danger')
        return redirect(url_for('paper.detail', paper_id=paper_id))
    
    # 检查状态
    if paper.status not in ['待确认', '已确认']:
        flash('项目已开始执行，无法编辑', 'warning')
        return redirect(url_for('paper.detail', paper_id=paper_id))
    
    if request.method == 'POST':
        paper.project_name = request.form.get('project_name', paper.project_name)
        paper.paper_title = request.form.get('paper_title', paper.paper_title)
        paper.research_field = request.form.get('research_field', paper.research_field)
        paper.target_journal = request.form.get('target_journal', paper.target_journal)
        paper.remarks = request.form.get('remarks', paper.remarks)
        
        try:
            db.session.commit()
            flash('项目信息更新成功', 'success')
            return redirect(url_for('paper.detail', paper_id=paper_id))
        except Exception as e:
            db.session.rollback()
            flash('更新失败，请重试', 'danger')
            current_app.logger.error(f"论文项目更新失败: {e}")
    
    return render_template('paper/edit.html', paper=paper)

@paper_bp.route('/<int:paper_id>/upload', methods=['POST'])
@login_required
def upload_file(paper_id):
    """上传项目文件"""
    paper = PaperProject.query.get_or_404(paper_id)
    
    # 检查权限
    if paper.applicant_id != current_user.id:
        return jsonify({'success': False, 'message': '您没有权限上传文件'})
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'message': '没有选择文件'})
    
    if file:
        try:
            # 生成唯一文件名
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4().hex}{file_extension}"
            
            # 创建上传目录
            upload_dir = os.path.join(current_app.static_folder, 'uploads', 'papers', str(paper_id))
            os.makedirs(upload_dir, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # 保存文件记录
            project_file = ProjectFile(
                project_id=paper_id,
                project_type='paper',
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

@paper_bp.route('/<int:paper_id>/delete_file/<int:file_id>', methods=['POST'])
@login_required
def delete_file(paper_id, file_id):
    """删除项目文件"""
    paper = PaperProject.query.get_or_404(paper_id)
    project_file = ProjectFile.query.get_or_404(file_id)
    
    # 检查权限
    if paper.applicant_id != current_user.id or project_file.project_id != paper_id:
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

@paper_bp.route('/staff')
@login_required
def staff_dashboard():
    """员工论文管理面板"""
    # 检查是否为员工
    if not hasattr(current_user, 'position_id') or not current_user.position_id:
        flash('您没有权限访问此页面', 'danger')
        return redirect(url_for('paper.index'))
    
    # 获取待处理的论文项目
    pending_papers = PaperProject.query.filter_by(status='待确认').order_by(PaperProject.apply_time.desc()).all()
    
    # 获取已确认的论文项目
    confirmed_papers = PaperProject.query.filter_by(status='已确认').order_by(PaperProject.confirm_time.desc()).all()
    
    # 获取进行中的论文项目
    in_progress_papers = PaperProject.query.filter(
        PaperProject.status.in_(['进行中', '已投稿', '审稿中'])
    ).order_by(PaperProject.start_time.desc()).all()
    
    return render_template('paper/staff_dashboard.html',
                         pending_papers=pending_papers,
                         confirmed_papers=confirmed_papers,
                         in_progress_papers=in_progress_papers)

@paper_bp.route('/<int:paper_id>/confirm', methods=['POST'])
@login_required
def confirm_paper(paper_id):
    """确认论文项目"""
    # 检查是否为员工
    if not (hasattr(current_user, 'position_id') and current_user.position_id):
        return jsonify({'success': False, 'message': '您没有权限执行此操作'})
    
    paper = PaperProject.query.get_or_404(paper_id)
    
    if paper.status != '待确认':
        return jsonify({'success': False, 'message': '项目状态不正确'})
    
    try:
        paper.status = '已确认'
        paper.confirm_time = datetime.utcnow()
        paper.confirmer_id = current_user.id
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '项目确认成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"项目确认失败: {e}")
        return jsonify({'success': False, 'message': '项目确认失败'})

@paper_bp.route('/<int:paper_id>/assign_executor', methods=['POST'])
@login_required
def assign_executor(paper_id):
    """分配执行者"""
    # 检查是否为员工
    if not (hasattr(current_user, 'position_id') and current_user.position_id):
        return jsonify({'success': False, 'message': '您没有权限执行此操作'})
    
    paper = PaperProject.query.get_or_404(paper_id)
    executor_id = request.json.get('executor_id')
    
    if not executor_id:
        return jsonify({'success': False, 'message': '请选择执行者'})
    
    try:
        paper.executor_id = executor_id
        paper.status = '进行中'
        paper.start_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '执行者分配成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"执行者分配失败: {e}")
        return jsonify({'success': False, 'message': '执行者分配失败'})

@paper_bp.route('/<int:paper_id>/update_status', methods=['POST'])
@login_required
def update_status(paper_id):
    """更新项目状态"""
    # 检查是否为员工
    if not (hasattr(current_user, 'position_id') and current_user.position_id):
        return jsonify({'success': False, 'message': '您没有权限执行此操作'})
    
    paper = PaperProject.query.get_or_404(paper_id)
    new_status = request.json.get('status')
    
    if not new_status:
        return jsonify({'success': False, 'message': '请选择新状态'})
    
    try:
        paper.status = new_status
        
        # 根据状态更新时间字段
        if new_status == '已投稿':
            paper.submit_time = datetime.utcnow()
        elif new_status == '已录用':
            paper.accept_time = datetime.utcnow()
        elif new_status == '已发表':
            paper.publish_time = datetime.utcnow()
        elif new_status == '已完成':
            paper.publish_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '状态更新成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"状态更新失败: {e}")
        return jsonify({'success': False, 'message': '状态更新失败'})
