#!/usr/bin/env python3
"""
邮件发送工具模块
"""

from flask import current_app, render_template
from flask_mail import Message
from datetime import datetime, timedelta
import secrets
import string

def generate_token(length=32):
    """生成随机令牌"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_verification_code(length=6):
    """生成6位数字验证码"""
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def send_email_verification(user, token):
    """发送邮箱验证邮件"""
    try:
        msg = Message(
            subject='邮箱验证 - 软件著作权管理系统',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # 生成验证链接
        verification_url = f"{current_app.config['APP_URL']}/auth/verify_email/{token}"
        
        msg.html = render_template('emails/email_verification.html',
                                 user=user,
                                 verification_url=verification_url,
                                 app_name=current_app.config['APP_NAME'])
        
        mail = current_app.extensions['mail']
        mail.send(msg)
        return True
    except Exception as e:
        print(f"发送邮箱验证邮件失败: {e}")
        return False

def send_password_reset(user, token):
    """发送密码重置邮件"""
    try:
        msg = Message(
            subject='密码重置 - 软件著作权管理系统',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # 生成重置链接
        reset_url = f"{current_app.config['APP_URL']}/auth/reset_password/{token}"
        
        msg.html = render_template('emails/password_reset.html',
                                 user=user,
                                 reset_url=reset_url,
                                 app_name=current_app.config['APP_NAME'])
        
        mail = current_app.extensions['mail']
        mail.send(msg)
        return True
    except Exception as e:
        print(f"发送密码重置邮件失败: {e}")
        return False

def send_verification_code(user, code):
    """发送验证码邮件"""
    try:
        msg = Message(
            subject='邮箱验证码 - 软件著作权管理系统',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.html = render_template('emails/verification_code.html',
                                 user=user,
                                 verification_code=code,
                                 app_name=current_app.config['APP_NAME'])
        
        mail = current_app.extensions['mail']
        mail.send(msg)
        return True
    except Exception as e:
        print(f"发送验证码邮件失败: {e}")
        return False

def send_welcome_email(user):
    """发送欢迎邮件"""
    try:
        msg = Message(
            subject='欢迎注册 - 软件著作权管理系统',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.html = render_template('emails/welcome.html',
                                 user=user,
                                 app_name=current_app.config['APP_NAME'],
                                 app_url=current_app.config['APP_URL'])
        
        mail = current_app.extensions['mail']
        mail.send(msg)
        return True
    except Exception as e:
        print(f"发送欢迎邮件失败: {e}")
        return False