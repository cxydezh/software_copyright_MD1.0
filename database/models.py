from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

db = SQLAlchemy()

class Staff(UserMixin, db.Model):
    """工作人员表"""
    __tablename__ = 'staff'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, comment='姓名')
    gender = db.Column(db.Enum('男', '女'), comment='性别')
    birth_date = db.Column(db.Date, comment='出生日期')
    position_id = db.Column(db.Integer, db.ForeignKey('permissions.id'), comment='职务ID')
    phone = db.Column(db.String(20), comment='电话')
    email = db.Column(db.String(100), unique=True, comment='邮箱')
    register_date = db.Column(db.DateTime, default=datetime.utcnow, comment='注册日期')
    remarks = db.Column(db.Text, comment='备注')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    
    # 关系
    position = db.relationship('Permission', backref='staff_members')
    confirmed_projects = db.relationship('Project', foreign_keys='Project.confirmer_id', backref='confirmer')
    executed_projects = db.relationship('Project', foreign_keys='Project.executor_id', backref='executor')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Staff {self.name}>'

class User(UserMixin, db.Model):
    """用户表"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, comment='姓名')
    gender = db.Column(db.Enum('男', '女'), comment='性别')
    id_number = db.Column(db.String(18), unique=True, comment='身份证号')
    birth_date = db.Column(db.Date, comment='出生日期')
    email = db.Column(db.String(100), unique=True, comment='邮箱')
    phone = db.Column(db.String(20), comment='电话')
    register_time = db.Column(db.DateTime, default=datetime.utcnow, comment='注册时间')
    remarks = db.Column(db.Text, comment='备注')
    password_hash = db.Column(db.String(255), nullable=False, comment='密码哈希')
    
    # 关系
    projects = db.relationship('Project', backref='applicant')
    messages = db.relationship('Message', backref='user')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.name}>'

class Permission(db.Model):
    """权限列表"""
    __tablename__ = 'permissions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    position = db.Column(db.Enum('普通业务员', '项目执行者'), nullable=False, comment='职务')
    execute_permission = db.Column(db.Boolean, default=False, comment='执行任务权限')
    update_serial_permission = db.Column(db.Boolean, default=False, comment='更新流水号权限')
    
    def __repr__(self):
        return f'<Permission {self.position}>'

class Project(db.Model):
    """公司项目表"""
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(200), nullable=False, comment='项目名称')
    project_type = db.Column(db.Enum('软件登记业务', '软件设计与登记业务', '软件部署与登记业务'), 
                           nullable=False, comment='项目类型')
    applicant_type = db.Column(db.Enum('个人', '事业单位', '事业单位联合个人', '自然人联合'), 
                             nullable=False, comment='申请人类型')
    copyright_owner = db.Column(db.Text, comment='著作权人')
    software_applicant_name = db.Column(db.String(200), comment='软著申请人名称')
    serial_number = db.Column(db.String(100), comment='项目流水号')
    priority = db.Column(db.Enum('普通', '加急', '快速'), default='普通', comment='项目优先级')
    
    # 时间字段
    apply_time = db.Column(db.DateTime, default=datetime.utcnow, comment='项目申请时间')
    confirm_time = db.Column(db.DateTime, comment='项目确认时间')
    execute_time = db.Column(db.DateTime, comment='项目执行时间')
    complete_time = db.Column(db.DateTime, comment='项目完成时间')
    settle_time = db.Column(db.DateTime, comment='项目结清时间')
    submit_time = db.Column(db.DateTime, comment='项目上网提交时间')
    certificate_time = db.Column(db.DateTime, comment='项目证书完成时间')
    
    # 财务字段
    price = db.Column(db.Numeric(10, 2), comment='项目价目')
    discount = db.Column(db.Numeric(5, 2), default=0, comment='优惠折扣')
    
    # 状态字段
    is_archived = db.Column(db.Boolean, default=False, comment='是否归档')
    status = db.Column(db.Enum('待确认', '已确认', '已立项', '执行中', '已完成', '已上传', 
                              '已获取流水号', '证书完成', '已结清', '已归档'), 
                      default='待确认', comment='项目状态')
    
    # 外键
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='申请者ID')
    confirmer_id = db.Column(db.Integer, db.ForeignKey('staff.id'), comment='确认者ID')
    executor_id = db.Column(db.Integer, db.ForeignKey('staff.id'), comment='执行者ID')
    
    remarks = db.Column(db.Text, comment='项目备注')
    
    # 关系
    messages = db.relationship('Message', backref='project')
    
    def __repr__(self):
        return f'<Project {self.project_name}>'

class Message(db.Model):
    """留言表"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False, comment='留言内容')
    create_time = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    is_read = db.Column(db.Boolean, default=False, comment='是否已读')
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), comment='用户ID')
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), comment='员工ID')
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), comment='项目ID')
    
    # 关系
    staff = db.relationship('Staff', backref='messages')
    
    def __repr__(self):
        return f'<Message {self.id}>'

class LocalProject:
    """本地项目表（SQLite）"""
    
    @staticmethod
    def init_local_db(db_path):
        """初始化本地数据库"""
        if not os.path.exists(os.path.dirname(db_path)):
            os.makedirs(os.path.dirname(db_path))
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS local_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT NOT NULL,
            project_type TEXT NOT NULL,
            applicant_type TEXT NOT NULL,
            copyright_owner TEXT,
            software_applicant_name TEXT,
            serial_number TEXT,
            priority TEXT DEFAULT '普通',
            status TEXT DEFAULT '已确认',
            executor_id INTEGER,
            remarks TEXT,
            sync_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS local_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER,
            file_name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES local_projects (id)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def sync_from_server(db_path, server_projects):
        """从服务器同步项目数据"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        for project in server_projects:
            cursor.execute('''
            INSERT OR REPLACE INTO local_projects 
            (id, project_name, project_type, applicant_type, copyright_owner, 
             software_applicant_name, serial_number, priority, status, executor_id, remarks)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                project.id, project.project_name, project.project_type,
                project.applicant_type, project.copyright_owner,
                project.software_applicant_name, project.serial_number,
                project.priority, project.status, project.executor_id, project.remarks
            ))
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_all_projects(db_path):
        """获取所有本地项目"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM local_projects ORDER BY sync_time DESC')
        projects = cursor.fetchall()
        
        conn.close()
        return projects
    
    @staticmethod
    def update_serial_number(db_path, project_id, serial_number):
        """更新项目流水号"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        UPDATE local_projects 
        SET serial_number = ?, sync_time = CURRENT_TIMESTAMP 
        WHERE id = ?
        ''', (serial_number, project_id))
        
        conn.commit()
        conn.close()

def init_db(app):
    """初始化数据库"""
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        
        # 创建默认权限
        if not Permission.query.first():
            business_permission = Permission(
                position='普通业务员',
                execute_permission=False,
                update_serial_permission=False
            )
            executor_permission = Permission(
                position='项目执行者',
                execute_permission=True,
                update_serial_permission=True
            )
            
            db.session.add(business_permission)
            db.session.add(executor_permission)
            
            # 创建默认管理员账户
            admin_staff = Staff(
                name='系统管理员',
                email='admin@yiqichuang.com',
                position_id=2,  # 项目执行者
                phone='13800138000'
            )
            admin_staff.set_password('admin123')
            
            db.session.add(admin_staff)
            db.session.commit()
