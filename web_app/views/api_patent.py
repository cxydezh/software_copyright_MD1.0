#!/usr/bin/env python3
"""
专利相关API端点
"""

from flask import Blueprint, request, jsonify, current_app, send_file, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import sys
import os
import mimetypes

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, PatentProject, ProjectFile, Staff

api_patent_bp = Blueprint('api_patent', __name__)

# 允许的文件类型
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'}

def allowed_file(filename):
    """检查文件类型是否允许"""
    if not filename or '.' not in filename:
        return False
    try:
        extension = filename.rsplit('.', 1)[1].lower()
        return extension in ALLOWED_EXTENSIONS
    except IndexError:
        return False

@api_patent_bp.route('/patent/<int:patent_id>/upload', methods=['POST'])
@login_required
def upload_patent_file(patent_id):
    """上传专利项目文件"""
    try:
        # 检查项目是否存在
        patent = PatentProject.query.get_or_404(patent_id)
        
        # 检查权限
        if hasattr(current_user, 'user_type') and current_user.user_type == 'user':
            if patent.applicant_id != current_user.id:
                return jsonify({'success': False, 'message': '权限不足'})
        
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择文件'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': '不支持的文件类型'})
        
        # 生成安全的文件名
        original_filename = file.filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        
        # 调试信息
        current_app.logger.info(f"原始文件名: {original_filename}")
        current_app.logger.info(f"安全文件名: {filename}")
        current_app.logger.info(f"唯一文件名: {unique_filename}")
        
        # 确保上传目录存在
        upload_dir = os.path.join(current_app.static_folder, 'uploads', 'patents', str(patent_id))
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, unique_filename)
        file.save(file_path)
        
        # 获取文件大小
        file_size = os.path.getsize(file_path)
        
        # 获取文件分类
        file_category = request.form.get('file_category', '其他文件')
        
        # 生成相对路径用于数据库存储
        relative_path = os.path.join('uploads', 'patents', str(patent_id), unique_filename)
        
        # 获取文件类型
        try:
            file_type = filename.rsplit('.', 1)[1].lower()
        except IndexError:
            file_type = 'unknown'
        
        # 保存文件记录到数据库
        project_file = ProjectFile(
            project_id=patent_id,
            project_type='patent',
            file_name=original_filename,  # 存储原始文件名
            file_path=relative_path,  # 存储相对路径
            file_type=file_type,
            file_size=file_size,
            uploader_id=current_user.id,
            file_category=file_category
        )
        
        db.session.add(project_file)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '文件上传成功',
            'file': {
                'id': project_file.id,
                'name': filename,
                'size': file_size,
                'type': project_file.file_type,
                'category': file_category
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"文件上传失败: {str(e)}")
        return jsonify({'success': False, 'message': f'文件上传失败: {str(e)}'})

@api_patent_bp.route('/patent/<int:patent_id>/file/<int:file_id>/download')
@login_required
def download_patent_file(patent_id, file_id):
    """下载专利项目文件"""
    try:
        # 检查项目是否存在
        patent = PatentProject.query.get_or_404(patent_id)
        
        # 检查权限
        if hasattr(current_user, 'user_type') and current_user.user_type == 'user':
            if patent.applicant_id != current_user.id:
                return jsonify({'success': False, 'message': '权限不足'})
        
        # 获取文件记录
        project_file = ProjectFile.query.filter_by(
            id=file_id, 
            project_id=patent_id, 
            project_type='patent'
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

@api_patent_bp.route('/patent/<int:patent_id>/file/<int:file_id>/preview')
@login_required
def preview_patent_file(patent_id, file_id):
    """预览专利项目文件"""
    try:
        # 检查项目是否存在
        patent = PatentProject.query.get_or_404(patent_id)
        
        # 检查权限
        if hasattr(current_user, 'user_type') and current_user.user_type == 'user':
            if patent.applicant_id != current_user.id:
                return jsonify({'success': False, 'message': '权限不足'})
        
        # 获取文件记录
        project_file = ProjectFile.query.filter_by(
            id=file_id, 
            project_id=patent_id, 
            project_type='patent'
        ).first_or_404()
        
        # 构建文件完整路径
        file_path = os.path.join(current_app.static_folder, project_file.file_path)
        
        if not os.path.exists(file_path):
            return jsonify({'success': False, 'message': '文件不存在'})
        
        # 检查文件类型是否支持预览
        previewable_types = ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'txt']
        if project_file.file_type not in previewable_types:
            return jsonify({'success': False, 'message': '该文件类型不支持预览'})
        
        # 发送文件
        return send_file(
            file_path,
            as_attachment=False,
            mimetype=mimetypes.guess_type(project_file.file_name)[0] or 'application/octet-stream'
        )
        
    except Exception as e:
        current_app.logger.error(f"文件预览失败: {str(e)}")
        return jsonify({'success': False, 'message': f'文件预览失败: {str(e)}'})

@api_patent_bp.route('/patent/<int:patent_id>/file/<int:file_id>/delete', methods=['POST'])
@login_required
def delete_patent_file(patent_id, file_id):
    """删除专利项目文件"""
    try:
        # 检查项目是否存在
        patent = PatentProject.query.get_or_404(patent_id)
        
        # 检查权限
        if hasattr(current_user, 'user_type') and current_user.user_type == 'user':
            if patent.applicant_id != current_user.id:
                return jsonify({'success': False, 'message': '权限不足'})
        
        # 获取文件记录
        project_file = ProjectFile.query.filter_by(
            id=file_id, 
            project_id=patent_id, 
            project_type='patent'
        ).first_or_404()
        
        # 删除物理文件
        file_path = os.path.join(current_app.static_folder, project_file.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 删除数据库记录
        db.session.delete(project_file)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '文件删除成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"文件删除失败: {str(e)}")
        return jsonify({'success': False, 'message': f'文件删除失败: {str(e)}'})

@api_patent_bp.route('/patent/<int:patent_id>/confirm', methods=['POST'])
@login_required
def confirm_patent_project(patent_id):
    """确认专利项目"""
    try:
        # 检查权限
        if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        patent = PatentProject.query.get_or_404(patent_id)
        
        if patent.status != '待确认':
            return jsonify({'success': False, 'message': '项目状态不正确'})
        
        # 更新项目状态
        patent.status = '已确认'
        patent.confirmer_id = current_user.id
        patent.confirm_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '项目确认成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"项目确认失败: {str(e)}")
        return jsonify({'success': False, 'message': '项目确认失败'})

@api_patent_bp.route('/patent/<int:patent_id>/assign_executor', methods=['POST'])
@login_required
def assign_patent_executor(patent_id):
    """分配执行者"""
    try:
        # 检查权限
        if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        patent = PatentProject.query.get_or_404(patent_id)
        
        if patent.status not in ['已确认', '准备中']:
            return jsonify({'success': False, 'message': '项目状态不正确'})
        
        data = request.get_json()
        executor_id = data.get('executor_id')
        
        if not executor_id:
            return jsonify({'success': False, 'message': '请选择执行者'})
        
        # 检查执行者是否存在
        executor = Staff.query.get(executor_id)
        if not executor:
            return jsonify({'success': False, 'message': '执行者不存在'})
        
        # 更新项目
        patent.executor_id = executor_id
        patent.status = '准备中'
        patent.start_time = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '执行者分配成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"执行者分配失败: {str(e)}")
        return jsonify({'success': False, 'message': '执行者分配失败'})

@api_patent_bp.route('/patent/<int:patent_id>/update_status', methods=['POST'])
@login_required
def update_patent_status(patent_id):
    """更新项目状态"""
    try:
        # 检查权限
        if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        patent = PatentProject.query.get_or_404(patent_id)
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'message': '请选择状态'})
        
        # 验证状态转换
        valid_transitions = {
            '待确认': ['已确认'],
            '已确认': ['准备中'],
            '准备中': ['已递交', '已完成'],
            '已递交': ['审查中', '已授权', '已完成'],
            '审查中': ['已授权', '已完成'],
            '已授权': ['维持中', '已完成'],
            '维持中': ['已完成']
        }
        
        if new_status not in valid_transitions.get(patent.status, []):
            return jsonify({'success': False, 'message': '状态转换不正确'})
        
        # 更新状态
        patent.status = new_status
        
        # 根据状态更新时间字段
        now = datetime.utcnow()
        if new_status == '已递交':
            patent.file_time = now
        elif new_status == '审查中':
            patent.publish_time = now
        elif new_status == '已授权':
            patent.grant_time = now
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': '状态更新成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"状态更新失败: {str(e)}")
        return jsonify({'success': False, 'message': '状态更新失败'})

@api_patent_bp.route('/patent/<int:patent_id>/delete_file/<int:file_id>', methods=['POST'])
@login_required
def delete_patent_file_by_id(patent_id, file_id):
    """删除项目文件"""
    try:
        # 检查项目是否存在
        patent = PatentProject.query.get_or_404(patent_id)
        
        # 检查权限
        if hasattr(current_user, 'user_type') and current_user.user_type == 'user':
            if patent.applicant_id != current_user.id:
                return jsonify({'success': False, 'message': '权限不足'})
        
        # 查找文件
        project_file = ProjectFile.query.filter_by(
            id=file_id, 
            project_id=patent_id, 
            project_type='patent'
        ).first()
        
        if not project_file:
            return jsonify({'success': False, 'message': '文件不存在'})
        
        # 删除物理文件
        if os.path.exists(project_file.file_path):
            os.remove(project_file.file_path)
        
        # 删除数据库记录
        db.session.delete(project_file)
        db.session.commit()
        
        return jsonify({'success': True, 'message': '文件删除成功'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"文件删除失败: {str(e)}")
        return jsonify({'success': False, 'message': '文件删除失败'})

@api_patent_bp.route('/patent/staff_list', methods=['GET'])
@login_required
def get_patent_staff_list():
    """获取有专利编辑权限的员工列表"""
    try:
        # 检查权限
        if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
            return jsonify({'success': False, 'message': '权限不足'})
        
        from database.models import Permission
        
        # 获取有专利编辑权限的员工
        staff_with_patent_permission = Staff.query.join(Permission, Staff.position_id == Permission.id).filter(
            Permission.can_edit_patent == True
        ).all()
        
        staff_data = []
        for staff in staff_with_patent_permission:
            permission = Permission.query.get(staff.position_id)
            staff_data.append({
                'id': staff.id,
                'name': staff.name,
                'email': staff.email,
                'expertise_area': staff.expertise_area or '无专业领域',
                'position': permission.position if permission else '未知职位'
            })
        
        return jsonify({'success': True, 'staff_list': staff_data})
        
    except Exception as e:
        current_app.logger.error(f"获取员工列表失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取员工列表失败'})
