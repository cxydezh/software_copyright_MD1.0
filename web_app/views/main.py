from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, Project, Message

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页"""
    return render_template('index.html')

@main_bp.route('/about')
def about():
    """关于我们页面"""
    return render_template('about.html')

@main_bp.route('/services')
def services():
    """服务介绍页面"""
    services_list = [
        {
            'title': '论文指导和发表',
            'description': '提供专业的医疗论文指导和发表服务，帮助医务人员提升学术水平',
            'icon': 'fas fa-file-alt'
        },
        {
            'title': '专利申请和保护',
            'description': '专业的医疗器械专利申请、保护和转化服务',
            'icon': 'fas fa-shield-alt'
        },
        {
            'title': '软件开发和软件著作权登记',
            'description': '提供软件开发、设计、部署及软件著作权登记的全流程服务',
            'icon': 'fas fa-code'
        }
    ]
    
    business_types = [
        {
            'name': '软件登记业务',
            'description': '协助用户进行软件著作权登记，不包括软件设计开发'
        },
        {
            'name': '软件设计与登记业务',
            'description': '包括软件的设计与开发，协助用户获得软件著作权登记证书'
        },
        {
            'name': '软件部署与登记业务',
            'description': '包括软件的开发、设计与部署，同时协助用户获得软件著作权登记证书'
        }
    ]
    
    return render_template('services.html', 
                         services=services_list, 
                         business_types=business_types)

@main_bp.route('/contact')
def contact():
    """联系我们页面"""
    contact_info = {
        'company': '郑州医企创医疗科技有限公司',
        'address': '郑州市高新区科学大道',
        'phone': '0371-12345678',
        'email': 'contact@yiqichuang.com',
        'business_hours': '周一至周五 9:00-18:00'
    }
    return render_template('contact.html', contact=contact_info)

@main_bp.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    """在线留言"""
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            try:
                new_message = Message(
                    content=content,
                    user_id=current_user.id if hasattr(current_user, 'user_type') and current_user.user_type == 'user' else None,
                    staff_id=current_user.id if hasattr(current_user, 'user_type') and current_user.user_type == 'staff' else None
                )
                db.session.add(new_message)
                db.session.commit()
                flash('留言提交成功', 'success')
            except Exception as e:
                db.session.rollback()
                flash('留言提交失败，请重试', 'danger')
        else:
            flash('请输入留言内容', 'warning')
    
    # 获取用户的留言历史
    user_messages = []
    if hasattr(current_user, 'user_type'):
        if current_user.user_type == 'user':
            user_messages = Message.query.filter_by(user_id=current_user.id).order_by(Message.create_time.desc()).all()
        elif current_user.user_type == 'staff':
            user_messages = Message.query.filter_by(staff_id=current_user.id).order_by(Message.create_time.desc()).all()
    
    return render_template('messages.html', messages=user_messages)

@main_bp.route('/project_status/<int:project_id>')
@login_required
def project_status(project_id):
    """项目状态查询"""
    project = Project.query.get_or_404(project_id)
    
    # 检查权限
    if hasattr(current_user, 'user_type') and current_user.user_type == 'user':
        if project.applicant_id != current_user.id:
            flash('您没有权限查看此项目', 'danger')
            return redirect(url_for('user.dashboard'))
    elif hasattr(current_user, 'user_type') and current_user.user_type == 'staff':
        if project.confirmer_id != current_user.id and project.executor_id != current_user.id:
            flash('您没有权限查看此项目', 'danger')
            return redirect(url_for('staff.business_dashboard'))
    
    # 项目状态流程
    status_flow = [
        '待确认', '已确认', '已立项', '执行中', '已完成', 
        '已上传', '已获取流水号', '证书完成', '已结清', '已归档'
    ]
    
    current_step = status_flow.index(project.status) if project.status in status_flow else 0
    
    return render_template('project_status.html', 
                         project=project, 
                         status_flow=status_flow, 
                         current_step=current_step)
