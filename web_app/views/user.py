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

from database.models import db, Project, PaperProject, PatentProject, Message, ProcessLog, ProjectFile

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

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """用户仪表板"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'user':
        flash('权限不足', 'danger')
        return redirect(url_for('main.index'))
    
    # 获取用户的所有类型项目
    software_projects = Project.query.filter_by(applicant_id=current_user.id).order_by(Project.apply_time.desc()).all()
    paper_projects = PaperProject.query.filter_by(applicant_id=current_user.id).order_by(PaperProject.apply_time.desc()).all()
    patent_projects = PatentProject.query.filter_by(applicant_id=current_user.id).order_by(PatentProject.apply_time.desc()).all()
    
    # 合并所有项目
    all_projects = []
    
    # 软件登记项目
    for p in software_projects:
        all_projects.append({
            'type': 'software',
            'id': p.id,
            'project_name': p.project_name,
            'project_type': p.project_type,
            'status': p.status,
            'apply_time': p.apply_time,
            'priority': getattr(p, 'priority', None),
            'serial_number': getattr(p, 'serial_number', None)
        })
    
    # 论文项目
    for p in paper_projects:
        all_projects.append({
            'type': 'paper',
            'id': p.id,
            'project_name': p.project_name,
            'project_type': p.project_type,
            'status': p.status,
            'apply_time': p.apply_time,
            'priority': None,
            'serial_number': None
        })
    
    # 专利项目
    for p in patent_projects:
        all_projects.append({
            'type': 'patent',
            'id': p.id,
            'project_name': p.project_name,
            'project_type': p.project_type,
            'status': p.status,
            'apply_time': p.apply_time,
            'priority': None,
            'serial_number': None
        })
    
    # 按申请时间倒序排序
    all_projects.sort(key=lambda x: x['apply_time'] if x['apply_time'] else datetime.min, reverse=True)
    
    # 统计信息
    stats = {
        'total_projects': len(all_projects),
        'pending_projects': len([p for p in all_projects if p['status'] in ['待确认', '已确认', '已立项', '执行中', '进行中', '准备中']]),
        'completed_projects': len([p for p in all_projects if p['status'] in ['已完成', '已上传', '已获取流水号', '证书完成', '已录用', '已发表', '已授权']]),
        'archived_projects': len([p for p in all_projects if p['status'] == '已归档'])
    }
    
    # 获取最近的消息
    recent_messages = Message.query.filter_by(user_id=current_user.id).order_by(Message.create_time.desc()).limit(5).all()
    
    return render_template('user/dashboard.html', 
                         projects=all_projects, 
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
                                uploader_id=current_user.id,
                                file_category=request.form.get(f'file_category_{temp_file_path}', '其他文件')
                            )
                            db.session.add(project_file)
                    except Exception as e:
                        current_app.logger.error(f"处理临时文件失败: {str(e)}")
                        import traceback
                        current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
                        # 继续处理其他文件
            
            db.session.commit()
            
            flash('项目申请提交成功', 'success')
            return redirect(url_for('user.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"项目申请提交失败: {str(e)}")
            import traceback
            current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
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
    
    # 获取项目文件列表
    project_files = ProjectFile.query.filter_by(
        project_id=project_id,
        project_type='software'
    ).order_by(ProjectFile.upload_time.desc()).all()
    
    return render_template('user/project_detail.html', 
                         project=project,
                         messages=project_messages,
                         project_files=project_files)

@user_bp.route('/project/<int:project_id>/resubmit', methods=['POST'])
@login_required
def resubmit_project(project_id):
    """用户完善信息后重新申请（状态回到待确认）"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'user':
        return jsonify({'success': False, 'message': '权限不足'})
    project = Project.query.get_or_404(project_id)
    if project.applicant_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作该项目'})
    try:
        prev_status = project.status
        project.status = '待确认'
        project.confirm_time = None
        db.session.add(ProcessLog(
            project_type='software', project_id=project.id,
            action='user_resubmit', actor_id=current_user.id, actor_role='user',
            from_status=prev_status, to_status=project.status, note='用户重新申请'))
        db.session.commit()
        return jsonify({'success': True, 'message': '已重新提交，等待业务员确认'})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': '提交失败，请重试'})

@user_bp.route('/project/<int:project_id>/cancel', methods=['POST'])
@login_required
def cancel_project(project_id):
    """用户取消申请（保持当前状态，仅记录流程）"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'user':
        return jsonify({'success': False, 'message': '权限不足'})
    project = Project.query.get_or_404(project_id)
    if project.applicant_id != current_user.id:
        return jsonify({'success': False, 'message': '无权操作该项目'})
    try:
        db.session.add(ProcessLog(
            project_type='software', project_id=project.id,
            action='user_cancel', actor_id=current_user.id, actor_role='user',
            from_status=project.status, to_status=project.status, note='用户取消申请'))
        db.session.commit()
        return jsonify({'success': True, 'message': '已取消申请'})
    except Exception:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'})

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

# ==================== 文件上传和下载相关路由 ====================

@user_bp.route('/apply_project/upload', methods=['POST'])
@login_required
def upload_apply_project_file():
    """用户申请项目时上传文件（临时存储，提交申请后关联到项目）"""
    try:
        # 检查权限
        if not hasattr(current_user, 'user_type') or current_user.user_type != 'user':
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
        
        # 临时存储目录（使用用户ID）
        temp_dir = os.path.join(current_app.static_folder, 'uploads', 'temp', str(current_user.id))
        os.makedirs(temp_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(temp_dir, unique_filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 获取文件分类
        file_category = request.form.get('file_category', '其他文件')
        
        # 返回临时文件信息（存储在表单中，提交申请时关联到项目）
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

@user_bp.route('/project/<int:project_id>/file/<int:file_id>/download')
@login_required
def download_project_file(project_id, file_id):
    """下载项目文件"""
    try:
        # 检查项目是否存在
        project = Project.query.get_or_404(project_id)
        
        # 检查权限（只有项目申请人可以下载）
        if not hasattr(current_user, 'user_type') or current_user.user_type != 'user':
            return jsonify({'success': False, 'message': '权限不足'})
        
        if project.applicant_id != current_user.id:
            return jsonify({'success': False, 'message': '您没有权限下载此文件'})
        
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
