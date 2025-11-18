from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_mail import Mail
from werkzeug.security import check_password_hash
from werkzeug.exceptions import RequestEntityTooLarge
import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import config
from database.models import db, init_db, Staff, User, Project, Message, Permission

def create_app(config_name=None):
    """创建Flask应用"""
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # 加载配置
    config_name = config_name or os.getenv('FLASK_CONFIG') or 'default'
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    init_db(app)
    
    # 配置邮件
    mail = Mail(app)
    
    # 配置登录管理
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录以访问此页面。'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """根据会话中的角色精确加载用户，避免误判导致权限不足。"""
        role = session.get('user_type')

        # 优先根据会话中的角色加载
        if role == 'staff':
            staff = Staff.query.get(int(user_id))
            if staff:
                staff.user_type = 'staff'
                return staff
        elif role == 'user':
            user = User.query.get(int(user_id))
            if user:
                user.user_type = 'user'
                return user

        # 回退策略：先按用户，再按员工，避免普通用户被误识别为员工
        user = User.query.get(int(user_id))
        if user:
            user.user_type = 'user'
            return user

        staff = Staff.query.get(int(user_id))
        if staff:
            staff.user_type = 'staff'
            return staff

        return None
    
    # 注册蓝图
    from web_app.views.auth import auth_bp
    from web_app.views.main import main_bp
    from web_app.views.user import user_bp
    from web_app.views.staff import staff_bp
    from web_app.views.api import api_bp
    from web_app.views.paper import paper_bp
    from web_app.views.patent import patent_bp
    from web_app.views.api_paper import api_paper_bp
    from web_app.views.api_patent import api_patent_bp
    from web_app.views.reports import reports_bp
    from web_app.views.api_auth import api_auth_bp
    from web_app.views.api_desktop import api_desktop_bp
    from web_app.views.api_query import api_query_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(staff_bp, url_prefix='/staff')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(api_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_desktop_bp, url_prefix='/api/desktop')
    app.register_blueprint(api_query_bp)
    app.register_blueprint(paper_bp)
    app.register_blueprint(patent_bp)
    app.register_blueprint(api_paper_bp, url_prefix='/api')
    app.register_blueprint(api_patent_bp, url_prefix='/api')
    app.register_blueprint(reports_bp)
    
    # 全局模板变量
    @app.context_processor
    def inject_globals():
        return {
            'current_user': current_user,
            'enumerate': enumerate
        }
    
    # 错误处理器：处理文件上传大小超限
    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(e):
        """处理文件上传大小超限错误"""
        try:
            # 尝试获取请求路径
            path = getattr(request, 'path', '')
            # 判断是否为API请求
            is_api_request = (path.startswith('/api/') or 
                            path.startswith('/user/') or 
                            path.startswith('/staff/') or
                            path.startswith('/paper/') or
                            path.startswith('/patent/'))
            
            if is_api_request:
                return jsonify({
                    'success': False,
                    'message': '文件大小超过限制，单个文件不能超过16MB'
                }), 413
            else:
                flash('文件大小超过限制，单个文件不能超过16MB', 'danger')
                referrer = getattr(request, 'referrer', None)
                return redirect(referrer or url_for('main.index')), 413
        except Exception:
            # 如果无法获取请求信息，返回JSON格式错误
            return jsonify({
                'success': False,
                'message': '文件大小超过限制，单个文件不能超过16MB'
            }), 413
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
