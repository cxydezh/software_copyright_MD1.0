#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目查询API
为普通业务员提供项目查看和检索功能
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from database.models import (
    db, Project, PaperProject, PatentProject,
    ArchivedSoftwareProject, ArchivedPaperProject, ArchivedPatentProject,
    Staff, Permission
)
from web_app.services.archive_service import ArchiveService

api_query_bp = Blueprint('api_query', __name__, url_prefix='/api/query')


@api_query_bp.route('/projects', methods=['GET'])
@login_required
def get_all_projects():
    """获取所有项目（未归档）"""
    try:
        project_type = request.args.get('type', 'all')  # all, software, paper, patent
        status = request.args.get('status', 'all')  # all, 待确认, 已确认, 等
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        results = {
            'software': [],
            'paper': [],
            'patent': []
        }
        
        # 软著项目
        if project_type in ['all', 'software']:
            query = Project.query
            if status != 'all':
                query = query.filter_by(status=status)
            software_projects = query.order_by(Project.apply_time.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            results['software'] = [{
                'id': p.id,
                'project_name': p.project_name,
                'project_type': p.project_type,
                'applicant_type': p.applicant_type,
                'copyright_owner': p.copyright_owner,
                'serial_number': p.serial_number,
                'status': p.status,
                'apply_time': p.apply_time.strftime('%Y-%m-%d %H:%M:%S') if p.apply_time else None,
                'is_settled': p.is_settled,
                'price': float(p.price) if p.price else 0
            } for p in software_projects.items]
        
        # 论文项目
        if project_type in ['all', 'paper']:
            query = PaperProject.query
            if status != 'all':
                query = query.filter_by(status=status)
            paper_projects = query.order_by(PaperProject.apply_time.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            results['paper'] = [{
                'id': p.id,
                'project_name': p.project_name,
                'project_type': p.project_type,
                'service_level': p.service_level,
                'paper_title': p.paper_title,
                'target_journal': p.target_journal,
                'status': p.status,
                'apply_time': p.apply_time.strftime('%Y-%m-%d %H:%M:%S') if p.apply_time else None,
                'is_settled': p.is_settled,
                'price': float(p.price) if p.price else 0
            } for p in paper_projects.items]
        
        # 专利项目
        if project_type in ['all', 'patent']:
            query = PatentProject.query
            if status != 'all':
                query = query.filter_by(status=status)
            patent_projects = query.order_by(PatentProject.apply_time.desc()).paginate(
                page=page, per_page=per_page, error_out=False
            )
            results['patent'] = [{
                'id': p.id,
                'project_name': p.project_name,
                'project_type': p.project_type,
                'invention_title': p.invention_title,
                'patent_number': p.patent_number,
                'status': p.status,
                'apply_time': p.apply_time.strftime('%Y-%m-%d %H:%M:%S') if p.apply_time else None,
                'is_settled': p.is_settled,
                'price': float(p.price) if p.price else 0
            } for p in patent_projects.items]
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '获取项目列表成功'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取项目列表失败: {str(e)}'
        }), 500


@api_query_bp.route('/archived', methods=['GET'])
@login_required
def get_archived_projects():
    """获取归档项目"""
    try:
        project_type = request.args.get('type', 'all')  # all, software, paper, patent
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        archived_data = ArchiveService.get_archived_projects(project_type, page, per_page)
        
        if archived_data is None:
            return jsonify({
                'success': False,
                'message': '获取归档项目失败'
            }), 500
        
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
        return jsonify({
            'success': False,
            'message': f'获取归档项目失败: {str(e)}'
        }), 500


@api_query_bp.route('/search', methods=['GET'])
@login_required
def search_projects():
    """搜索项目（包括未归档和已归档）"""
    try:
        keyword = request.args.get('keyword', '')
        project_type = request.args.get('type', 'all')
        include_archived = request.args.get('include_archived', 'true').lower() == 'true'
        
        if not keyword:
            return jsonify({
                'success': False,
                'message': '请提供搜索关键词'
            }), 400
        
        results = {
            'active': {
                'software': [],
                'paper': [],
                'patent': []
            },
            'archived': {
                'software': [],
                'paper': [],
                'patent': []
            }
        }
        
        # 搜索活动项目
        if project_type in ['all', 'software']:
            software_projects = Project.query.filter(
                db.or_(
                    Project.project_name.like(f'%{keyword}%'),
                    Project.copyright_owner.like(f'%{keyword}%'),
                    Project.serial_number.like(f'%{keyword}%')
                )
            ).all()
            results['active']['software'] = [{
                'id': p.id,
                'project_name': p.project_name,
                'copyright_owner': p.copyright_owner,
                'serial_number': p.serial_number,
                'status': p.status,
                'apply_time': p.apply_time.strftime('%Y-%m-%d %H:%M:%S') if p.apply_time else None
            } for p in software_projects]
        
        if project_type in ['all', 'paper']:
            paper_projects = PaperProject.query.filter(
                db.or_(
                    PaperProject.project_name.like(f'%{keyword}%'),
                    PaperProject.paper_title.like(f'%{keyword}%'),
                    PaperProject.target_journal.like(f'%{keyword}%')
                )
            ).all()
            results['active']['paper'] = [{
                'id': p.id,
                'project_name': p.project_name,
                'paper_title': p.paper_title,
                'target_journal': p.target_journal,
                'status': p.status,
                'apply_time': p.apply_time.strftime('%Y-%m-%d %H:%M:%S') if p.apply_time else None
            } for p in paper_projects]
        
        if project_type in ['all', 'patent']:
            patent_projects = PatentProject.query.filter(
                db.or_(
                    PatentProject.project_name.like(f'%{keyword}%'),
                    PatentProject.invention_title.like(f'%{keyword}%'),
                    PatentProject.patent_number.like(f'%{keyword}%')
                )
            ).all()
            results['active']['patent'] = [{
                'id': p.id,
                'project_name': p.project_name,
                'invention_title': p.invention_title,
                'patent_number': p.patent_number,
                'status': p.status,
                'apply_time': p.apply_time.strftime('%Y-%m-%d %H:%M:%S') if p.apply_time else None
            } for p in patent_projects]
        
        # 搜索归档项目
        if include_archived:
            archived_results = ArchiveService.search_archived_projects(keyword, project_type)
            if archived_results:
                results['archived']['software'] = [{
                    'id': p.id,
                    'project_name': p.project_name,
                    'copyright_owner': p.copyright_owner,
                    'serial_number': p.serial_number,
                    'archive_time': p.archive_time.strftime('%Y-%m-%d %H:%M:%S') if p.archive_time else None
                } for p in archived_results.get('software', [])]
                
                results['archived']['paper'] = [{
                    'id': p.id,
                    'project_name': p.project_name,
                    'paper_title': p.paper_title,
                    'target_journal': p.target_journal,
                    'archive_time': p.archive_time.strftime('%Y-%m-%d %H:%M:%S') if p.archive_time else None
                } for p in archived_results.get('paper', [])]
                
                results['archived']['patent'] = [{
                    'id': p.id,
                    'project_name': p.project_name,
                    'invention_title': p.invention_title,
                    'patent_number': p.patent_number,
                    'archive_time': p.archive_time.strftime('%Y-%m-%d %H:%M:%S') if p.archive_time else None
                } for p in archived_results.get('patent', [])]
        
        return jsonify({
            'success': True,
            'data': results,
            'message': '搜索完成'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'搜索失败: {str(e)}'
        }), 500


@api_query_bp.route('/archive/<project_type>/<int:project_id>', methods=['POST'])
@login_required
def archive_project(project_type, project_id):
    """归档项目"""
    try:
        # 检查用户权限
        if isinstance(current_user, Staff):
            staff = current_user
        else:
            return jsonify({
                'success': False,
                'message': '只有员工可以归档项目'
            }), 403
        
        # 归档项目
        if project_type == 'software':
            success, message = ArchiveService.archive_software_project(project_id)
        elif project_type == 'paper':
            success, message = ArchiveService.archive_paper_project(project_id)
        elif project_type == 'patent':
            success, message = ArchiveService.archive_patent_project(project_id)
        else:
            return jsonify({
                'success': False,
                'message': '无效的项目类型'
            }), 400
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            })
        else:
            return jsonify({
                'success': False,
                'message': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'归档失败: {str(e)}'
        }), 500

