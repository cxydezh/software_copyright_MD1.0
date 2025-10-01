#!/usr/bin/env python3
"""
报表功能模块
"""

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, PaperProject, PatentProject, User, Staff, ProjectFile

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports')
@login_required
def index():
    """报表首页"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return render_template('errors/403.html'), 403
    
    return render_template('reports/index.html')

@reports_bp.route('/reports/project_statistics')
@login_required
def project_statistics():
    """项目统计报表"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    try:
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        project_type = request.args.get('project_type', 'all')
        
        # 构建查询条件
        paper_query = PaperProject.query
        patent_query = PatentProject.query
        
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            paper_query = paper_query.filter(PaperProject.apply_time >= start_dt)
            patent_query = patent_query.filter(PatentProject.apply_time >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            paper_query = paper_query.filter(PaperProject.apply_time < end_dt)
            patent_query = patent_query.filter(PatentProject.apply_time < end_dt)
        
        # 论文项目统计
        paper_stats = {
            'total': paper_query.count(),
            'pending': paper_query.filter(PaperProject.status == '待确认').count(),
            'confirmed': paper_query.filter(PaperProject.status == '已确认').count(),
            'in_progress': paper_query.filter(PaperProject.status.in_(['进行中', '已投稿', '审稿中'])).count(),
            'completed': paper_query.filter(PaperProject.status.in_(['已录用', '已发表', '已完成'])).count(),
            'rejected': paper_query.filter(PaperProject.status == '被拒稿').count()
        }
        
        # 专利项目统计
        patent_stats = {
            'total': patent_query.count(),
            'pending': patent_query.filter(PatentProject.status == '待确认').count(),
            'confirmed': patent_query.filter(PatentProject.status == '已确认').count(),
            'in_progress': patent_query.filter(PatentProject.status.in_(['准备中', '已递交', '审查中'])).count(),
            'completed': patent_query.filter(PatentProject.status.in_(['已授权', '维持中', '已完成'])).count()
        }
        
        # 按月份统计
        monthly_stats = _get_monthly_statistics(start_date, end_date)
        
        # 按状态统计
        status_stats = _get_status_statistics(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': {
                'paper_stats': paper_stats,
                'patent_stats': patent_stats,
                'monthly_stats': monthly_stats,
                'status_stats': status_stats
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取项目统计失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取统计数据失败'})

@reports_bp.route('/reports/revenue_analysis')
@login_required
def revenue_analysis():
    """收入分析报表"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    try:
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # 构建查询条件
        paper_query = PaperProject.query
        patent_query = PatentProject.query
        
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            paper_query = paper_query.filter(PaperProject.apply_time >= start_dt)
            patent_query = patent_query.filter(PatentProject.apply_time >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            paper_query = paper_query.filter(PaperProject.apply_time < end_dt)
            patent_query = patent_query.filter(PatentProject.apply_time < end_dt)
        
        # 论文项目收入统计
        paper_revenue = db.session.query(
            func.sum(PaperProject.price).label('total_revenue'),
            func.avg(PaperProject.price).label('avg_revenue'),
            func.count(PaperProject.id).label('total_count')
        ).filter(PaperProject.price.isnot(None)).first()
        
        # 专利项目收入统计
        patent_revenue = db.session.query(
            func.sum(PatentProject.price).label('total_revenue'),
            func.avg(PatentProject.price).label('avg_revenue'),
            func.count(PatentProject.id).label('total_count')
        ).filter(PatentProject.price.isnot(None)).first()
        
        # 按服务等级统计收入
        paper_level_revenue = db.session.query(
            PaperProject.service_level,
            func.sum(PaperProject.price).label('revenue'),
            func.count(PaperProject.id).label('count')
        ).filter(
            PaperProject.price.isnot(None)
        ).group_by(PaperProject.service_level).all()
        
        # 按项目类型统计收入
        patent_type_revenue = db.session.query(
            PatentProject.project_type,
            func.sum(PatentProject.price).label('revenue'),
            func.count(PatentProject.id).label('count')
        ).filter(
            PatentProject.price.isnot(None)
        ).group_by(PatentProject.project_type).all()
        
        # 月度收入趋势
        monthly_revenue = _get_monthly_revenue(start_date, end_date)
        
        return jsonify({
            'success': True,
            'data': {
                'paper_revenue': {
                    'total': float(paper_revenue.total_revenue or 0),
                    'average': float(paper_revenue.avg_revenue or 0),
                    'count': paper_revenue.total_count or 0
                },
                'patent_revenue': {
                    'total': float(patent_revenue.total_revenue or 0),
                    'average': float(patent_revenue.avg_revenue or 0),
                    'count': patent_revenue.total_count or 0
                },
                'paper_level_revenue': [
                    {
                        'level': item.service_level,
                        'revenue': float(item.revenue or 0),
                        'count': item.count or 0
                    } for item in paper_level_revenue
                ],
                'patent_type_revenue': [
                    {
                        'type': item.project_type,
                        'revenue': float(item.revenue or 0),
                        'count': item.count or 0
                    } for item in patent_type_revenue
                ],
                'monthly_revenue': monthly_revenue
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"获取收入分析失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取收入数据失败'})

@reports_bp.route('/reports/staff_performance')
@login_required
def staff_performance():
    """员工绩效报表"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    try:
        # 获取查询参数
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        staff_id = request.args.get('staff_id')
        
        # 构建查询条件
        paper_query = PaperProject.query
        patent_query = PatentProject.query
        
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            paper_query = paper_query.filter(PaperProject.apply_time >= start_dt)
            patent_query = patent_query.filter(PatentProject.apply_time >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            paper_query = paper_query.filter(PaperProject.apply_time < end_dt)
            patent_query = patent_query.filter(PatentProject.apply_time < end_dt)
        
        if staff_id:
            paper_query = paper_query.filter(or_(
                PaperProject.confirmer_id == staff_id,
                PaperProject.executor_id == staff_id
            ))
            patent_query = patent_query.filter(or_(
                PatentProject.confirmer_id == staff_id,
                PatentProject.executor_id == staff_id
            ))
        
        # 获取所有员工
        staff_list = Staff.query.filter_by(is_active=True).all()
        
        staff_performance = []
        for staff in staff_list:
            # 确认的项目数量
            confirmed_papers = paper_query.filter(PaperProject.confirmer_id == staff.id).count()
            confirmed_patents = patent_query.filter(PatentProject.confirmer_id == staff.id).count()
            
            # 执行的项目数量
            executed_papers = paper_query.filter(PaperProject.executor_id == staff.id).count()
            executed_patents = patent_query.filter(PatentProject.executor_id == staff.id).count()
            
            # 完成的项目数量
            completed_papers = paper_query.filter(
                and_(
                    PaperProject.executor_id == staff.id,
                    PaperProject.status.in_(['已发表', '已完成'])
                )
            ).count()
            completed_patents = patent_query.filter(
                and_(
                    PatentProject.executor_id == staff.id,
                    PatentProject.status.in_(['已授权', '已完成'])
                )
            ).count()
            
            # 计算绩效分数
            performance_score = (confirmed_papers + confirmed_patents) * 1 + \
                              (executed_papers + executed_patents) * 2 + \
                              (completed_papers + completed_patents) * 3
            
            staff_performance.append({
                'staff_id': staff.id,
                'staff_name': staff.name,
                'email': staff.email,
                'expertise_area': staff.expertise_area,
                'confirmed_papers': confirmed_papers,
                'confirmed_patents': confirmed_patents,
                'executed_papers': executed_papers,
                'executed_patents': executed_patents,
                'completed_papers': completed_papers,
                'completed_patents': completed_patents,
                'total_confirmed': confirmed_papers + confirmed_patents,
                'total_executed': executed_papers + executed_patents,
                'total_completed': completed_papers + completed_patents,
                'performance_score': performance_score
            })
        
        # 按绩效分数排序
        staff_performance.sort(key=lambda x: x['performance_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': staff_performance
        })
        
    except Exception as e:
        current_app.logger.error(f"获取员工绩效失败: {str(e)}")
        return jsonify({'success': False, 'message': '获取绩效数据失败'})

def _get_monthly_statistics(start_date, end_date):
    """获取月度统计数据"""
    try:
        # 默认查询最近12个月
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        monthly_data = []
        current = start_dt.replace(day=1)
        
        while current <= end_dt:
            month_start = current
            month_end = (current + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # 论文项目
            paper_count = PaperProject.query.filter(
                PaperProject.apply_time >= month_start,
                PaperProject.apply_time <= month_end
            ).count()
            
            # 专利项目
            patent_count = PatentProject.query.filter(
                PatentProject.apply_time >= month_start,
                PatentProject.apply_time <= month_end
            ).count()
            
            monthly_data.append({
                'month': current.strftime('%Y-%m'),
                'paper_count': paper_count,
                'patent_count': patent_count,
                'total_count': paper_count + patent_count
            })
            
            # 下一个月
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return monthly_data
        
    except Exception as e:
        current_app.logger.error(f"获取月度统计失败: {str(e)}")
        return []

def _get_status_statistics(start_date, end_date):
    """获取状态统计数据"""
    try:
        paper_query = PaperProject.query
        patent_query = PatentProject.query
        
        if start_date:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            paper_query = paper_query.filter(PaperProject.apply_time >= start_dt)
            patent_query = patent_query.filter(PatentProject.apply_time >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            paper_query = paper_query.filter(PaperProject.apply_time < end_dt)
            patent_query = patent_query.filter(PatentProject.apply_time < end_dt)
        
        # 论文项目状态统计
        paper_status = db.session.query(
            PaperProject.status,
            func.count(PaperProject.id).label('count')
        ).group_by(PaperProject.status).all()
        
        # 专利项目状态统计
        patent_status = db.session.query(
            PatentProject.status,
            func.count(PatentProject.id).label('count')
        ).group_by(PatentProject.status).all()
        
        return {
            'paper_status': [{'status': item.status, 'count': item.count} for item in paper_status],
            'patent_status': [{'status': item.status, 'count': item.count} for item in patent_status]
        }
        
    except Exception as e:
        current_app.logger.error(f"获取状态统计失败: {str(e)}")
        return {'paper_status': [], 'patent_status': []}

def _get_monthly_revenue(start_date, end_date):
    """获取月度收入数据"""
    try:
        # 默认查询最近12个月
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        monthly_revenue = []
        current = start_dt.replace(day=1)
        
        while current <= end_dt:
            month_start = current
            month_end = (current + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # 论文项目收入
            paper_revenue = db.session.query(
                func.sum(PaperProject.price).label('revenue')
            ).filter(
                PaperProject.apply_time >= month_start,
                PaperProject.apply_time <= month_end,
                PaperProject.price.isnot(None)
            ).scalar() or 0
            
            # 专利项目收入
            patent_revenue = db.session.query(
                func.sum(PatentProject.price).label('revenue')
            ).filter(
                PatentProject.apply_time >= month_start,
                PatentProject.apply_time <= month_end,
                PatentProject.price.isnot(None)
            ).scalar() or 0
            
            monthly_revenue.append({
                'month': current.strftime('%Y-%m'),
                'paper_revenue': float(paper_revenue),
                'patent_revenue': float(patent_revenue),
                'total_revenue': float(paper_revenue + patent_revenue)
            })
            
            # 下一个月
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return monthly_revenue
        
    except Exception as e:
        current_app.logger.error(f"获取月度收入失败: {str(e)}")
        return []
