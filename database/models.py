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
    
    # 邮箱验证相关字段
    email_verified = db.Column(db.Boolean, default=False, comment='邮箱是否已验证')
    email_verification_token = db.Column(db.String(100), comment='邮箱验证令牌')
    email_verification_expires = db.Column(db.DateTime, comment='邮箱验证令牌过期时间')
    email_verification_code = db.Column(db.String(6), comment='邮箱验证码')
    email_verification_code_expires = db.Column(db.DateTime, comment='验证码过期时间')
    email_verification_tries = db.Column(db.Integer, default=0, comment='验证尝试次数')
    last_email_sent_at = db.Column(db.DateTime, comment='最后邮件发送时间')
    email_send_count = db.Column(db.Integer, default=0, comment='邮件发送计数')
    
    # 密码重置相关字段
    password_reset_token = db.Column(db.String(100), comment='密码重置令牌')
    password_reset_expires = db.Column(db.DateTime, comment='密码重置令牌过期时间')
    
    # 扩展字段 - 支持多业务类型
    expertise_area = db.Column(db.String(200), comment='专业领域')
    service_types = db.Column(db.String(200), comment='服务类型')
    
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
    
    # 邮箱验证相关字段
    email_verified = db.Column(db.Boolean, default=False, comment='邮箱是否已验证')
    email_verification_token = db.Column(db.String(100), comment='邮箱验证令牌')
    email_verification_expires = db.Column(db.DateTime, comment='邮箱验证令牌过期时间')
    email_verification_code = db.Column(db.String(6), comment='邮箱验证码')
    email_verification_code_expires = db.Column(db.DateTime, comment='验证码过期时间')
    email_verification_tries = db.Column(db.Integer, default=0, comment='验证尝试次数')
    last_email_sent_at = db.Column(db.DateTime, comment='最后邮件发送时间')
    email_send_count = db.Column(db.Integer, default=0, comment='邮件发送计数')
    
    # 密码重置相关字段
    password_reset_token = db.Column(db.String(100), comment='密码重置令牌')
    password_reset_expires = db.Column(db.DateTime, comment='密码重置令牌过期时间')
    
    # 扩展字段 - 支持多业务类型
    user_category = db.Column(db.Enum('软件著作权', '论文指导', '专利申请', '综合服务'), 
                            default='软件著作权', comment='用户类别')
    organization = db.Column(db.String(200), comment='所属机构')
    research_field = db.Column(db.String(100), comment='研究领域')
    
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
    position = db.Column(db.Enum('普通业务员', '项目执行者', '论文编辑', '专利编辑', '专家', '系统管理员'), 
                        nullable=False, comment='职务')
    
    # 基础权限
    can_confirm = db.Column(db.Boolean, default=False, comment='确认项目权限')
    can_approve = db.Column(db.Boolean, default=False, comment='立项权限（项目立项，指定执行者）')
    can_execute = db.Column(db.Boolean, default=False, comment='执行任务权限')
    can_manage = db.Column(db.Boolean, default=False, comment='管理权限')
    can_view_all = db.Column(db.Boolean, default=False, comment='查看所有项目权限')
    
    # 专业权限
    can_edit_paper = db.Column(db.Boolean, default=False, comment='编辑论文项目权限')
    can_edit_patent = db.Column(db.Boolean, default=False, comment='编辑专利项目权限')
    is_expert = db.Column(db.Boolean, default=False, comment='专家权限')
    
    # 兼容旧字段
    execute_permission = db.Column(db.Boolean, default=False, comment='执行任务权限（兼容）')
    update_serial_permission = db.Column(db.Boolean, default=False, comment='更新流水号权限（兼容）')
    
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
    is_settled = db.Column(db.Boolean, default=False, comment='是否已结清（可与其他状态共存）')
    status = db.Column(db.Enum('待确认', '已确认', '已立项', '执行中', '已完成', '已上传', 
                              '已获取流水号', '证书完成', '已归档'), 
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

class ProcessLog(db.Model):
    """统一的项目流程日志，记录所有项目类型的操作轨迹"""
    __tablename__ = 'process_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_type = db.Column(db.Enum('software', 'paper', 'patent'), nullable=False, comment='项目类型')
    project_id = db.Column(db.Integer, nullable=False, comment='项目ID')
    action = db.Column(db.String(100), nullable=False, comment='动作，如confirm/approve/take/reject/...')
    actor_id = db.Column(db.Integer, comment='操作者ID')
    actor_role = db.Column(db.Enum('user', 'staff'), comment='操作者角色')
    from_status = db.Column(db.String(50), comment='变更前状态')
    to_status = db.Column(db.String(50), comment='变更后状态')
    note = db.Column(db.Text, comment='备注/意见/说明')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')

    def __repr__(self):
        return f'<ProcessLog {self.project_type}:{self.project_id} {self.action}>'

class PaperProject(db.Model):
    """论文项目表"""
    __tablename__ = 'paper_projects'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(200), nullable=False, comment='项目名称')
    project_type = db.Column(db.Enum('论文指导', '论文发表', '学术咨询'), 
                           nullable=False, comment='项目类型')
    service_level = db.Column(db.Enum('基础服务', '标准服务', '高级服务'), 
                            nullable=False, comment='服务等级')
    applicant_type = db.Column(db.Enum('个人学者', '医疗机构', '企业研发', '联合申请'), 
                             nullable=False, comment='申请人类型')
    
    # 论文信息
    paper_title = db.Column(db.String(500), comment='论文标题')
    research_field = db.Column(db.String(100), comment='研究领域')
    target_journal = db.Column(db.String(200), comment='目标期刊')
    paper_status = db.Column(db.Enum('初稿', '修改中', '已投稿', '审稿中', '已录用', '已发表', '被拒稿'), 
                           default='初稿', comment='论文状态')
    
    # 时间管理
    apply_time = db.Column(db.DateTime, default=datetime.utcnow, comment='申请时间')
    confirm_time = db.Column(db.DateTime, comment='确认时间')
    start_time = db.Column(db.DateTime, comment='开始时间')
    submit_time = db.Column(db.DateTime, comment='投稿时间')
    accept_time = db.Column(db.DateTime, comment='录用时间')
    publish_time = db.Column(db.DateTime, comment='发表时间')
    
    # 财务信息
    price = db.Column(db.Numeric(10, 2), comment='项目价格')
    discount = db.Column(db.Numeric(5, 2), default=0, comment='优惠折扣')
    settle_time = db.Column(db.DateTime, comment='结清时间')
    
    # 状态管理
    status = db.Column(db.Enum('待确认', '已确认', '进行中', '已投稿', '审稿中', '已录用', '已发表', '已完成', '已归档'), 
                      default='待确认', comment='项目状态')
    is_archived = db.Column(db.Boolean, default=False, comment='是否归档')
    is_settled = db.Column(db.Boolean, default=False, comment='是否已结清（可与其他状态共存）')
    
    # 外键关联
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='申请者ID')
    confirmer_id = db.Column(db.Integer, db.ForeignKey('staff.id'), comment='确认者ID')
    executor_id = db.Column(db.Integer, db.ForeignKey('staff.id'), comment='执行者ID')
    
    remarks = db.Column(db.Text, comment='项目备注')
    
    # 关系
    applicant = db.relationship('User', backref='paper_projects')
    confirmer = db.relationship('Staff', foreign_keys=[confirmer_id], backref='confirmed_paper_projects')
    executor = db.relationship('Staff', foreign_keys=[executor_id], backref='executed_paper_projects')
    
    def __repr__(self):
        return f'<PaperProject {self.project_name}>'

class PatentProject(db.Model):
    """专利项目表"""
    __tablename__ = 'patent_projects'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_name = db.Column(db.String(200), nullable=False, comment='项目名称')
    project_type = db.Column(db.Enum('发明专利申请', '实用新型申请', '外观设计申请', '国际申请', '专利保护', '专利管理'), 
                           nullable=False, comment='项目类型')
    applicant_type = db.Column(db.Enum('个人发明者', '企业申请', '科研院所', '联合申请'), 
                             nullable=False, comment='申请人类型')
    application_field = db.Column(db.Enum('医疗设备', '生物医药', '数字医疗', '其他领域'), 
                                nullable=False, comment='申请领域')
    
    # 专利信息
    invention_title = db.Column(db.String(500), comment='发明名称')
    technical_field = db.Column(db.String(100), comment='技术领域')
    application_number = db.Column(db.String(50), comment='申请号')
    publication_number = db.Column(db.String(50), comment='公开号')
    patent_number = db.Column(db.String(50), comment='专利号')
    patent_status = db.Column(db.Enum('申请中', '公开', '实审', '授权', '维持', '终止', '无效'), 
                            default='申请中', comment='专利状态')
    
    # 时间管理
    apply_time = db.Column(db.DateTime, default=datetime.utcnow, comment='申请时间')
    confirm_time = db.Column(db.DateTime, comment='确认时间')
    start_time = db.Column(db.DateTime, comment='开始时间')
    file_time = db.Column(db.DateTime, comment='递交时间')
    publish_time = db.Column(db.DateTime, comment='公开时间')
    grant_time = db.Column(db.DateTime, comment='授权时间')
    
    # 财务信息
    price = db.Column(db.Numeric(10, 2), comment='项目价格')
    discount = db.Column(db.Numeric(5, 2), default=0, comment='优惠折扣')
    annual_fee = db.Column(db.Numeric(10, 2), comment='年费')
    settle_time = db.Column(db.DateTime, comment='结清时间')
    
    # 状态管理
    status = db.Column(db.Enum('待确认', '已确认', '准备中', '已递交', '审查中', '已授权', '维持中', '已完成', '已归档'), 
                      default='待确认', comment='项目状态')
    is_archived = db.Column(db.Boolean, default=False, comment='是否归档')
    is_settled = db.Column(db.Boolean, default=False, comment='是否已结清（可与其他状态共存）')
    
    # 外键关联
    applicant_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='申请者ID')
    confirmer_id = db.Column(db.Integer, db.ForeignKey('staff.id'), comment='确认者ID')
    executor_id = db.Column(db.Integer, db.ForeignKey('staff.id'), comment='执行者ID')
    
    remarks = db.Column(db.Text, comment='项目备注')
    
    # 关系
    applicant = db.relationship('User', backref='patent_projects')
    confirmer = db.relationship('Staff', foreign_keys=[confirmer_id], backref='confirmed_patent_projects')
    executor = db.relationship('Staff', foreign_keys=[executor_id], backref='executed_patent_projects')
    
    def __repr__(self):
        return f'<PatentProject {self.project_name}>'

class ProjectFile(db.Model):
    """项目文件表"""
    __tablename__ = 'project_files'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    project_id = db.Column(db.Integer, nullable=False, comment='项目ID')
    project_type = db.Column(db.Enum('software', 'paper', 'patent'), 
                           nullable=False, comment='项目类型')
    file_name = db.Column(db.String(255), nullable=False, comment='文件名')
    file_path = db.Column(db.String(500), nullable=False, comment='文件路径')
    file_type = db.Column(db.String(50), nullable=False, comment='文件类型')
    file_size = db.Column(db.BigInteger, comment='文件大小')
    upload_time = db.Column(db.DateTime, default=datetime.utcnow, comment='上传时间')
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='上传者ID')
    file_category = db.Column(db.Enum('申请材料', '技术文档', '证书文件', '其他文件'), 
                            nullable=False, comment='文件分类')
    
    # 关系
    uploader = db.relationship('User', backref='uploaded_files')
    
    def __repr__(self):
        return f'<ProjectFile {self.file_name}>'

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
