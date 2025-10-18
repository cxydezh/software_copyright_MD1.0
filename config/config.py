import os
from datetime import timedelta
from urllib.parse import quote_plus

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    
    # 安全配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # 邮件配置
    MAIL_SERVER = 'smtp.qq.com'  # QQ邮箱SMTP服务器
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('APPEMAILACCOUNT')
    MAIL_PASSWORD = os.environ.get('APPEMAILSMTP')  # 使用SMTP授权码
    MAIL_DEFAULT_SENDER = os.environ.get('APPEMAILACCOUNT')
    
    # 应用配置
    APP_NAME = '软件著作权管理系统'
    APP_URL = 'http://localhost:5000'

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    # 优先使用MySQL，如果连接失败则回退到SQLite
    def get_database_uri():
        db_password = os.environ.get('DB_PASSWORD')
        if db_password:
            # URL编码密码以处理特殊字符
            encoded_password = quote_plus(db_password)
            return f'mysql+pymysql://webuser:{encoded_password}@127.0.0.1:3306/software_copyright'
        else:
            return 'sqlite:///software_copyright.db'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or get_database_uri()

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    def get_database_uri():
        db_password = os.environ.get('DB_PASSWORD')
        if db_password:
            # URL编码密码以处理特殊字符
            encoded_password = quote_plus(db_password)
            return f'mysql+pymysql://webuser:{encoded_password}@127.0.0.1:3306/software_copyright'
        else:
            return 'sqlite:///software_copyright.db'
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or get_database_uri()

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# 本地客户端配置
LOCAL_CONFIG = {
    # 本地数据库路径（SQLite）
    'LOCAL_DB_PATH': os.path.join(os.path.expanduser('~'), 'SoftwareCopyrightMS', 'local.db'),
    
    # 本地文件目录
    'BASE_DIR': os.path.join(os.path.expanduser('~'), 'SoftwareCopyrightMS'),
    'USCCC_DIR': os.path.join(os.path.expanduser('~'), 'SoftwareCopyrightMS', 'USCCC'),
    'IDPDF_DIR': os.path.join(os.path.expanduser('~'), 'SoftwareCopyrightMS', 'IDPDF'),
    'MODEL_DIR': os.path.join(os.path.expanduser('~'), 'SoftwareCopyrightMS', 'templates'),
    'CONTRACT_DIR': os.path.join(os.path.expanduser('~'), 'SoftwareCopyrightMS', 'model', 'contract'),
    'MATERIAL_DIR': os.path.join(os.path.expanduser('~'), 'SoftwareCopyrightMS', 'model', 'material'),
    'PROJECT_FILE_DIR': os.path.join(os.path.expanduser('~'), 'SoftwareCopyrightMS', 'ProjectFile'),
    
    # 云服务器Web API地址（生产环境）
    'WEB_API_HOST': os.environ.get('WEB_API_HOST', 'https://your-domain.com'),
    'WEB_API_PORT': int(os.environ.get('WEB_API_PORT', '443')),
    'API_BASE': os.environ.get('API_BASE', 'https://your-domain.com'),
    
    # 网站链接
    'COMPANY_WEBSITE': os.environ.get('COMPANY_WEBSITE', 'https://your-domain.com'),
    'COPYRIGHT_CENTER_URL': 'https://register.ccopyright.com.cn/login.html',
    
    # 浏览器配置
    'BROWSER_PATH': 'C:/Program Files/Google/Chrome/Application/chrome.exe'
}
