"""
安全工具模块
提供各种安全防护功能
"""

import re
import html
import hashlib
import secrets
from functools import wraps
from flask import request, abort, current_app, session
from flask_login import current_user
import bleach

class SecurityUtils:
    """安全工具类"""
    
    # 允许的HTML标签
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                    'ul', 'ol', 'li', 'blockquote', 'a', 'img']
    
    # 允许的HTML属性
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'width', 'height'],
        'blockquote': ['cite']
    }
    
    @staticmethod
    def sanitize_html(content):
        """清理HTML内容，防止XSS攻击"""
        if not content:
            return content
        
        # 使用bleach清理HTML
        cleaned = bleach.clean(
            content,
            tags=SecurityUtils.ALLOWED_TAGS,
            attributes=SecurityUtils.ALLOWED_ATTRIBUTES,
            strip=True
        )
        
        return cleaned
    
    @staticmethod
    def escape_html(content):
        """转义HTML特殊字符"""
        if not content:
            return content
        return html.escape(str(content))
    
    @staticmethod
    def validate_email(email):
        """验证邮箱格式"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """验证手机号格式"""
        if not phone:
            return True  # 手机号可选
        
        pattern = r'^1[3-9]\d{9}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_id_number(id_number):
        """验证身份证号格式"""
        if not id_number:
            return True  # 身份证号可选
        
        pattern = r'^\d{17}[\dXx]$'
        return re.match(pattern, id_number) is not None
    
    @staticmethod
    def check_password_strength(password):
        """检查密码强度"""
        if not password:
            return False, "密码不能为空"
        
        if len(password) < 6:
            return False, "密码长度至少6位"
        
        if len(password) > 128:
            return False, "密码长度不能超过128位"
        
        # 检查是否包含特殊字符（可选）
        # has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)
        # if not has_special:
        #     return False, "密码必须包含特殊字符"
        
        return True, "密码强度合格"
    
    @staticmethod
    def generate_csrf_token():
        """生成CSRF令牌"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def verify_csrf_token(token):
        """验证CSRF令牌"""
        expected_token = session.get('csrf_token')
        return expected_token and secrets.compare_digest(expected_token, token)
    
    @staticmethod
    def hash_file(file_path):
        """计算文件哈希值"""
        hasher = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return None
    
    @staticmethod
    def check_file_type(filename, allowed_extensions):
        """检查文件类型"""
        if not filename:
            return False
        
        extension = filename.rsplit('.', 1)[-1].lower()
        return extension in allowed_extensions
    
    @staticmethod
    def check_file_size(file, max_size_mb):
        """检查文件大小"""
        if not file:
            return False
        
        # 获取文件大小
        file.seek(0, 2)  # 移动到文件末尾
        size = file.tell()
        file.seek(0)  # 重置文件指针
        
        max_size_bytes = max_size_mb * 1024 * 1024
        return size <= max_size_bytes

def require_role(*roles):
    """角色权限装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            user_type = getattr(current_user, 'user_type', None)
            if user_type not in roles:
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_permission(permission):
    """权限检查装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            # 检查用户权限
            if hasattr(current_user, 'position') and current_user.position:
                if permission == 'execute_task' and not current_user.position.execute_permission:
                    abort(403)
                elif permission == 'update_serial' and not current_user.position.update_serial_permission:
                    abort(403)
            else:
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def rate_limit(max_requests=100, per_seconds=3600):
    """简单的速率限制装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 这里可以实现更复杂的速率限制逻辑
            # 目前只是一个示例框架
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_security_event(event_type, description, user_id=None, ip_address=None):
    """记录安全事件"""
    try:
        from datetime import datetime
        import logging
        
        # 配置安全日志
        security_logger = logging.getLogger('security')
        if not security_logger.handlers:
            handler = logging.FileHandler('security.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            security_logger.addHandler(handler)
            security_logger.setLevel(logging.INFO)
        
        # 记录事件
        log_message = f"Event: {event_type} | Description: {description}"
        if user_id:
            log_message += f" | User ID: {user_id}"
        if ip_address:
            log_message += f" | IP: {ip_address}"
        
        security_logger.info(log_message)
        
    except Exception as e:
        # 日志记录失败不应该影响正常业务
        print(f"Security logging failed: {e}")

class InputValidator:
    """输入验证器"""
    
    @staticmethod
    def validate_project_name(name):
        """验证项目名称"""
        if not name or not name.strip():
            return False, "项目名称不能为空"
        
        if len(name.strip()) < 2:
            return False, "项目名称至少2个字符"
        
        if len(name.strip()) > 200:
            return False, "项目名称不能超过200个字符"
        
        # 检查特殊字符
        if re.search(r'[<>"\']', name):
            return False, "项目名称不能包含特殊字符"
        
        return True, "验证通过"
    
    @staticmethod
    def validate_serial_number(serial):
        """验证流水号"""
        if not serial:
            return True, "流水号可以为空"
        
        if len(serial.strip()) > 100:
            return False, "流水号不能超过100个字符"
        
        # 流水号通常是数字和字母的组合
        if not re.match(r'^[A-Za-z0-9-_]+$', serial.strip()):
            return False, "流水号格式不正确"
        
        return True, "验证通过"
    
    @staticmethod
    def validate_message_content(content):
        """验证留言内容"""
        if not content or not content.strip():
            return False, "留言内容不能为空"
        
        if len(content.strip()) > 1000:
            return False, "留言内容不能超过1000个字符"
        
        return True, "验证通过"

def create_security_headers(response):
    """添加安全响应头"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "font-src 'self'"
    )
    return response
