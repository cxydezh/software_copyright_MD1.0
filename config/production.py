import os
from config.config import Config
from urllib.parse import quote_plus
from datetime import timedelta

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    
    # 从环境变量读取敏感配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'CHANGE-THIS-IN-PRODUCTION'
    
    # 数据库配置
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_USER = os.environ.get('DB_USER', 'webuser')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'software_copyright')
    
    encoded_password = quote_plus(DB_PASSWORD)
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    
    # 安全配置
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 文件上传 - Windows Server路径
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'C:\\inetpub\\wwwroot\\software_copyright\\uploads')
    
    # 应用URL（云服务器公网地址）
    APP_URL = os.environ.get('APP_URL', 'https://your-domain.com')
    
    # Windows Server特定配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'C:\\inetpub\\logs\\software_copyright.log')
    
    # 静态文件配置
    STATIC_FOLDER = os.environ.get('STATIC_FOLDER', 'C:\\inetpub\\wwwroot\\software_copyright\\static')
    
    # 会话配置 - Windows Server优化
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # 邮件配置 - Windows Server
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.qq.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')