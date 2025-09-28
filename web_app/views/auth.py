from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, Staff, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录页面"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_type = request.form.get('user_type', 'user')
        
        if not email or not password:
            flash('请输入邮箱和密码', 'danger')
            return render_template('auth/login.html')
        
        # 根据用户类型查找用户
        user = None
        if user_type == 'staff':
            user = Staff.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            user.user_type = user_type
            session['user_type'] = user_type
            
            # 根据用户类型重定向
            if user_type == 'staff':
                if hasattr(user, 'position') and user.position:
                    if user.position.position == '项目执行者':
                        return redirect(url_for('staff.executor_dashboard'))
                    else:
                        return redirect(url_for('staff.business_dashboard'))
                return redirect(url_for('staff.business_dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('邮箱或密码错误', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册页面"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证输入
        if not all([name, email, password, confirm_password]):
            flash('请填写所有必填字段', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return render_template('auth/register.html')
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            flash('该邮箱已被注册', 'danger')
            return render_template('auth/register.html')
        
        # 创建新用户
        try:
            new_user = User(
                name=name,
                email=email,
                phone=phone
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('注册成功，请登录', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash('注册失败，请重试', 'danger')
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """退出登录"""
    logout_user()
    session.pop('user_type', None)
    flash('已成功退出登录', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/choose_role')
@login_required
def choose_role():
    """角色选择页面（用于多重身份用户）"""
    # 检查用户是否有多重身份
    user_roles = []
    
    # 检查是否为普通用户
    if User.query.filter_by(email=current_user.email).first():
        user_roles.append(('user', '普通用户'))
    
    # 检查是否为员工
    staff = Staff.query.filter_by(email=current_user.email).first()
    if staff:
        if staff.position:
            user_roles.append(('staff', staff.position.position))
    
    if len(user_roles) <= 1:
        # 只有一个身份，直接重定向
        if user_roles:
            role = user_roles[0][0]
            session['user_type'] = role
            if role == 'staff':
                return redirect(url_for('staff.business_dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('账户异常，请联系管理员', 'danger')
            return redirect(url_for('auth.logout'))
    
    return render_template('auth/choose_role.html', roles=user_roles)

@auth_bp.route('/switch_role/<role>')
@login_required
def switch_role(role):
    """切换用户角色"""
    if role in ['user', 'staff']:
        session['user_type'] = role
        if role == 'staff':
            return redirect(url_for('staff.business_dashboard'))
        else:
            return redirect(url_for('user.dashboard'))
    
    flash('无效的角色选择', 'danger')
    return redirect(url_for('auth.choose_role'))
