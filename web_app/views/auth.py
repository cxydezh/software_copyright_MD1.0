from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from datetime import datetime, timedelta
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, Staff, User
from web_app.utils.email import generate_token, generate_verification_code, send_email_verification, send_verification_code, send_password_reset, send_welcome_email

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
            # 检查员工账号审核状态
            if user_type == 'staff':
                if user.approval_status == 'pending':
                    flash('您的员工账号申请正在审核中，请耐心等待系统管理员审核。', 'warning')
                    return render_template('auth/login.html')
                elif user.approval_status == 'rejected':
                    # 登录被驳回的员工，重定向到处理页面
                    login_user(user, remember=True)
                    user.user_type = user_type
                    session['user_type'] = user_type
                    return redirect(url_for('auth.handle_rejected_staff'))
            
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
        is_staff_account = request.form.get('is_staff_account') == 'on'
        application_reason = request.form.get('application_reason', '').strip()
        
        # 验证输入
        if not all([name, email, password, confirm_password]):
            flash('请填写所有必填字段', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return render_template('auth/register.html')
        
        # 员工账号需要申请理由
        if is_staff_account and not application_reason:
            flash('申请员工账号需要填写申请理由', 'danger')
            return render_template('auth/register.html')
        
        # 检查邮箱是否已存在（检查User和Staff表）
        if User.query.filter_by(email=email).first() or Staff.query.filter_by(email=email).first():
            flash('该邮箱已被注册', 'danger')
            return render_template('auth/register.html')
        
        # 创建新用户
        try:
            if is_staff_account:
                # 创建员工账号
                new_staff = Staff(
                    name=name,
                    email=email,
                    phone=phone,
                    approval_status='pending',
                    application_reason=application_reason
                )
                new_staff.set_password(password)
                
                db.session.add(new_staff)
                db.session.commit()
                
                flash('员工账号注册成功！您的申请已提交，等待系统管理员审核。审核通过后您将收到邮件通知。', 'success')
                return redirect(url_for('auth.login'))
            else:
                # 创建普通用户
                verification_code = generate_verification_code()
                code_expires = datetime.utcnow() + timedelta(minutes=5)
                
                new_user = User(
                    name=name,
                    email=email,
                    phone=phone,
                    email_verification_code=verification_code,
                    email_verification_code_expires=code_expires
                )
                new_user.set_password(password)
                
                db.session.add(new_user)
                db.session.commit()
                
                # 发送验证码邮件
                if send_verification_code(new_user, verification_code):
                    flash('注册成功！验证码已发送到您的邮箱，请查收并完成验证。', 'success')
                    return redirect(url_for('auth.verify_code', user_id=new_user.id))
                else:
                    flash('注册成功，但验证码邮件发送失败。请联系管理员。', 'warning')
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

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    """忘记密码页面"""
    if request.method == 'POST':
        email = request.form.get('email')
        user_type = request.form.get('user_type', 'user')
        
        if not email:
            flash('请输入邮箱地址', 'danger')
            return render_template('auth/forgot_password.html')
        
        # 根据用户类型查找用户
        user = None
        if user_type == 'staff':
            user = Staff.query.filter_by(email=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        
        if user:
            # 生成密码重置令牌
            reset_token = generate_token()
            reset_expires = datetime.utcnow() + timedelta(hours=1)
            
            user.password_reset_token = reset_token
            user.password_reset_expires = reset_expires
            
            db.session.commit()
            
            # 发送密码重置邮件
            if send_password_reset(user, reset_token):
                flash('密码重置邮件已发送，请检查您的邮箱。', 'success')
            else:
                flash('邮件发送失败，请重试或联系管理员。', 'danger')
        else:
            flash('该邮箱地址未注册', 'danger')
    
    return render_template('auth/forgot_password.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """重置密码页面"""
    # 查找有效的重置令牌
    user = User.query.filter_by(password_reset_token=token).first()
    if not user:
        user = Staff.query.filter_by(password_reset_token=token).first()
    
    if not user or user.password_reset_expires < datetime.utcnow():
        flash('密码重置链接无效或已过期', 'danger')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not password or not confirm_password:
            flash('请填写所有字段', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        if password != confirm_password:
            flash('两次输入的密码不一致', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        if len(password) < 6:
            flash('密码长度至少6位', 'danger')
            return render_template('auth/reset_password.html', token=token)
        
        # 更新密码
        user.set_password(password)
        user.password_reset_token = None
        user.password_reset_expires = None
        
        db.session.commit()
        
        flash('密码重置成功，请使用新密码登录', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', token=token)

@auth_bp.route('/verify_email/<token>')
def verify_email(token):
    """邮箱验证"""
    # 查找有效的验证令牌
    user = User.query.filter_by(email_verification_token=token).first()
    if not user:
        user = Staff.query.filter_by(email_verification_token=token).first()
    
    if not user or user.email_verification_expires < datetime.utcnow():
        flash('验证链接无效或已过期', 'danger')
        return redirect(url_for('auth.login'))
    
    # 验证邮箱
    user.email_verified = True
    user.email_verification_token = None
    user.email_verification_expires = None
    
    db.session.commit()
    
    flash('邮箱验证成功！您现在可以正常使用所有功能。', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/resend_verification', methods=['POST'])
def resend_verification():
    """重新发送验证邮件"""
    if not current_user.is_authenticated:
        flash('请先登录', 'danger')
        return redirect(url_for('auth.login'))
    
    if current_user.email_verified:
        flash('您的邮箱已经验证过了', 'info')
        return redirect(url_for('user.dashboard' if current_user.user_type == 'user' else 'staff.business_dashboard'))
    
    # 生成新的验证令牌
    verification_token = generate_token()
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    current_user.email_verification_token = verification_token
    current_user.email_verification_expires = verification_expires
    
    db.session.commit()
    
    # 发送验证邮件
    if send_email_verification(current_user, verification_token):
        flash('验证邮件已重新发送，请检查您的邮箱。', 'success')
    else:
        flash('邮件发送失败，请重试或联系管理员。', 'danger')
    
    return redirect(url_for('user.dashboard' if current_user.user_type == 'user' else 'staff.business_dashboard'))

@auth_bp.route('/verify_code/<int:user_id>', methods=['GET', 'POST'])
def verify_code(user_id):
    """验证码验证页面"""
    user = User.query.get_or_404(user_id)
    
    if user.email_verified:
        flash('您的邮箱已经验证过了', 'info')
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        verification_code = request.form.get('verification_code', '').strip()
        
        if not verification_code:
            flash('请输入验证码', 'danger')
            return render_template('auth/verify_code.html', user=user)
        
        if len(verification_code) != 6 or not verification_code.isdigit():
            flash('验证码格式不正确', 'danger')
            return render_template('auth/verify_code.html', user=user)
        
        # 检查验证码
        if (user.email_verification_code == verification_code and 
            user.email_verification_code_expires and 
            user.email_verification_code_expires > datetime.utcnow()):
            
            # 验证成功
            user.email_verified = True
            user.email_verification_code = None
            user.email_verification_code_expires = None
            
            db.session.commit()
            
            # 发送欢迎邮件
            send_welcome_email(user)
            
            flash('邮箱验证成功！欢迎使用我们的服务。', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('验证码错误或已过期，请重新输入', 'danger')
            return render_template('auth/verify_code.html', user=user)
    
    return render_template('auth/verify_code.html', user=user)

@auth_bp.route('/resend_verification_code', methods=['POST'])
def resend_verification_code():
    """重新发送验证码"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({'success': False, 'message': '邮箱地址不能为空'})
        
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'success': False, 'message': '用户不存在'})
        
        if user.email_verified:
            return jsonify({'success': False, 'message': '邮箱已经验证过了'})
        
        # 生成新的验证码
        verification_code = generate_verification_code()
        code_expires = datetime.utcnow() + timedelta(minutes=5)
        
        user.email_verification_code = verification_code
        user.email_verification_code_expires = code_expires
        
        db.session.commit()
        
        # 发送验证码邮件
        if send_verification_code(user, verification_code):
            return jsonify({'success': True, 'message': '验证码已重新发送'})
        else:
            return jsonify({'success': False, 'message': '邮件发送失败，请重试'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': '系统错误，请重试'})

@auth_bp.route('/handle_rejected_staff', methods=['GET'])
@login_required
def handle_rejected_staff():
    """处理被驳回的员工账号"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return redirect(url_for('auth.login'))
    
    if current_user.approval_status != 'rejected':
        return redirect(url_for('staff.business_dashboard'))
    
    return render_template('auth/handle_rejected_staff.html', staff=current_user)

@auth_bp.route('/reapply_staff', methods=['POST'])
@login_required
def reapply_staff():
    """重新申请员工账号"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    if current_user.approval_status != 'rejected':
        return jsonify({'success': False, 'message': '账号状态不允许此操作'})
    
    data = request.get_json() or {}
    new_reason = data.get('application_reason', '').strip()
    
    if not new_reason:
        return jsonify({'success': False, 'message': '请填写申请理由'})
    
    try:
        current_user.approval_status = 'pending'
        current_user.application_reason = new_reason
        current_user.approval_date = None
        current_user.approver_id = None
        current_user.approval_remarks = None
        
        db.session.commit()
        
        flash('重新申请成功，等待系统管理员审核', 'success')
        return jsonify({'success': True, 'message': '重新申请成功，等待审核'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': '操作失败，请重试'})

@auth_bp.route('/cancel_staff', methods=['POST'])
@login_required
def cancel_staff():
    """取消员工账号申请"""
    if not hasattr(current_user, 'user_type') or current_user.user_type != 'staff':
        return jsonify({'success': False, 'message': '权限不足'})
    
    if current_user.approval_status not in ['pending', 'rejected']:
        return jsonify({'success': False, 'message': '账号状态不允许此操作'})
    
    try:
        staff_id = current_user.id
        staff_to_delete = current_user
        
        # 先删除数据库记录
        db.session.delete(staff_to_delete)
        db.session.commit()
        
        # 然后登出用户
        logout_user()
        
        flash('申请已取消，您的员工账号信息已删除', 'info')
        return jsonify({'success': True, 'message': '申请已取消', 'redirect': url_for('auth.login')})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'})
