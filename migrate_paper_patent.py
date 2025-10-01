#!/usr/bin/env python3
"""
论文指导和专利申请功能数据库迁移脚本
"""

import os
import sys
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from database.models import db, User, Staff, PaperProject, PatentProject, ProjectFile
from sqlalchemy import text

def create_paper_tables():
    """创建论文相关表"""
    print("创建论文项目表...")
    try:
        with db.engine.connect() as conn:
            trans = conn.begin()
            try:
                # 创建论文项目表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS paper_projects (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        project_name VARCHAR(200) NOT NULL COMMENT '项目名称',
                        project_type ENUM('论文指导', '论文发表', '学术咨询') NOT NULL COMMENT '项目类型',
                        service_level ENUM('基础服务', '标准服务', '高级服务') NOT NULL COMMENT '服务等级',
                        applicant_type ENUM('个人学者', '医疗机构', '企业研发', '联合申请') NOT NULL COMMENT '申请人类型',
                        
                        paper_title VARCHAR(500) COMMENT '论文标题',
                        research_field VARCHAR(100) COMMENT '研究领域',
                        target_journal VARCHAR(200) COMMENT '目标期刊',
                        paper_status ENUM('初稿', '修改中', '已投稿', '审稿中', '已录用', '已发表', '被拒稿') DEFAULT '初稿' COMMENT '论文状态',
                        
                        apply_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间',
                        confirm_time DATETIME COMMENT '确认时间',
                        start_time DATETIME COMMENT '开始时间',
                        submit_time DATETIME COMMENT '投稿时间',
                        accept_time DATETIME COMMENT '录用时间',
                        publish_time DATETIME COMMENT '发表时间',
                        
                        price DECIMAL(10,2) COMMENT '项目价格',
                        discount DECIMAL(5,2) DEFAULT 0 COMMENT '优惠折扣',
                        
                        status ENUM('待确认', '已确认', '进行中', '已投稿', '审稿中', '已录用', '已发表', '已完成', '已归档') DEFAULT '待确认' COMMENT '项目状态',
                        is_archived BOOLEAN DEFAULT FALSE COMMENT '是否归档',
                        
                        applicant_id INT NOT NULL COMMENT '申请者ID',
                        confirmer_id INT COMMENT '确认者ID',
                        executor_id INT COMMENT '执行者ID',
                        
                        remarks TEXT COMMENT '项目备注',
                        
                        FOREIGN KEY (applicant_id) REFERENCES users(id),
                        FOREIGN KEY (confirmer_id) REFERENCES staff(id),
                        FOREIGN KEY (executor_id) REFERENCES staff(id)
                    )
                """))
                trans.commit()
                print("论文项目表创建成功")
            except Exception as e:
                trans.rollback()
                raise e
    except Exception as e:
        print(f"创建论文项目表失败: {e}")
        return False
    return True

def create_patent_tables():
    """创建专利相关表"""
    print("创建专利项目表...")
    try:
        with db.engine.connect() as conn:
            trans = conn.begin()
            try:
                # 创建专利项目表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS patent_projects (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        project_name VARCHAR(200) NOT NULL COMMENT '项目名称',
                        project_type ENUM('发明专利申请', '实用新型申请', '外观设计申请', '国际申请', '专利保护', '专利管理') NOT NULL COMMENT '项目类型',
                        applicant_type ENUM('个人发明者', '企业申请', '科研院所', '联合申请') NOT NULL COMMENT '申请人类型',
                        application_field ENUM('医疗设备', '生物医药', '数字医疗', '其他领域') NOT NULL COMMENT '申请领域',
                        
                        invention_title VARCHAR(500) COMMENT '发明名称',
                        technical_field VARCHAR(100) COMMENT '技术领域',
                        application_number VARCHAR(50) COMMENT '申请号',
                        publication_number VARCHAR(50) COMMENT '公开号',
                        patent_number VARCHAR(50) COMMENT '专利号',
                        patent_status ENUM('申请中', '公开', '实审', '授权', '维持', '终止', '无效') DEFAULT '申请中' COMMENT '专利状态',
                        
                        apply_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '申请时间',
                        confirm_time DATETIME COMMENT '确认时间',
                        file_time DATETIME COMMENT '递交时间',
                        publish_time DATETIME COMMENT '公开时间',
                        grant_time DATETIME COMMENT '授权时间',
                        
                        price DECIMAL(10,2) COMMENT '项目价格',
                        discount DECIMAL(5,2) DEFAULT 0 COMMENT '优惠折扣',
                        annual_fee DECIMAL(10,2) COMMENT '年费',
                        
                        status ENUM('待确认', '已确认', '准备中', '已递交', '审查中', '已授权', '维持中', '已完成', '已归档') DEFAULT '待确认' COMMENT '项目状态',
                        is_archived BOOLEAN DEFAULT FALSE COMMENT '是否归档',
                        
                        applicant_id INT NOT NULL COMMENT '申请者ID',
                        confirmer_id INT COMMENT '确认者ID',
                        executor_id INT COMMENT '执行者ID',
                        
                        remarks TEXT COMMENT '项目备注',
                        
                        FOREIGN KEY (applicant_id) REFERENCES users(id),
                        FOREIGN KEY (confirmer_id) REFERENCES staff(id),
                        FOREIGN KEY (executor_id) REFERENCES staff(id)
                    )
                """))
                trans.commit()
                print("专利项目表创建成功")
            except Exception as e:
                trans.rollback()
                raise e
    except Exception as e:
        print(f"创建专利项目表失败: {e}")
        return False
    return True

def create_file_management_table():
    """创建文件管理表"""
    print("创建项目文件表...")
    try:
        with db.engine.connect() as conn:
            trans = conn.begin()
            try:
                # 创建项目文件表
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS project_files (
                        id INT PRIMARY KEY AUTO_INCREMENT,
                        project_id INT NOT NULL COMMENT '项目ID',
                        project_type ENUM('software', 'paper', 'patent') NOT NULL COMMENT '项目类型',
                        file_name VARCHAR(255) NOT NULL COMMENT '文件名',
                        file_path VARCHAR(500) NOT NULL COMMENT '文件路径',
                        file_type VARCHAR(50) NOT NULL COMMENT '文件类型',
                        file_size BIGINT COMMENT '文件大小',
                        upload_time DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
                        uploader_id INT NOT NULL COMMENT '上传者ID',
                        file_category ENUM('申请材料', '技术文档', '证书文件', '其他文件') NOT NULL COMMENT '文件分类',
                        
                        FOREIGN KEY (uploader_id) REFERENCES users(id)
                    )
                """))
                trans.commit()
                print("项目文件表创建成功")
            except Exception as e:
                trans.rollback()
                raise e
    except Exception as e:
        print(f"创建项目文件表失败: {e}")
        return False
    return True

def extend_existing_tables():
    """扩展现有表"""
    print("扩展现有表结构...")
    
    # 扩展用户表
    print("扩展用户表...")
    try:
        with db.engine.connect() as conn:
            trans = conn.begin()
            try:
                # 检查并添加用户表扩展字段
                result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'user_category'"))
                if not result.fetchone():
                    conn.execute(text("ALTER TABLE users ADD COLUMN user_category ENUM('软件著作权', '论文指导', '专利申请', '综合服务') DEFAULT '软件著作权' COMMENT '用户类别'"))
                    print("   添加字段: user_category")
                else:
                    print("   字段已存在: user_category")
                
                result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'organization'"))
                if not result.fetchone():
                    conn.execute(text("ALTER TABLE users ADD COLUMN organization VARCHAR(200) COMMENT '所属机构'"))
                    print("   添加字段: organization")
                else:
                    print("   字段已存在: organization")
                
                result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'research_field'"))
                if not result.fetchone():
                    conn.execute(text("ALTER TABLE users ADD COLUMN research_field VARCHAR(100) COMMENT '研究领域'"))
                    print("   添加字段: research_field")
                else:
                    print("   字段已存在: research_field")
                
                trans.commit()
                print("用户表扩展完成")
            except Exception as e:
                trans.rollback()
                raise e
    except Exception as e:
        print(f"扩展用户表失败: {e}")
        return False
    
    # 扩展员工表
    print("扩展员工表...")
    try:
        with db.engine.connect() as conn:
            trans = conn.begin()
            try:
                # 检查并添加员工表扩展字段
                result = conn.execute(text("SHOW COLUMNS FROM staff LIKE 'expertise_area'"))
                if not result.fetchone():
                    conn.execute(text("ALTER TABLE staff ADD COLUMN expertise_area VARCHAR(200) COMMENT '专业领域'"))
                    print("   添加字段: expertise_area")
                else:
                    print("   字段已存在: expertise_area")
                
                result = conn.execute(text("SHOW COLUMNS FROM staff LIKE 'service_types'"))
                if not result.fetchone():
                    conn.execute(text("ALTER TABLE staff ADD COLUMN service_types VARCHAR(200) COMMENT '服务类型'"))
                    print("   添加字段: service_types")
                else:
                    print("   字段已存在: service_types")
                
                trans.commit()
                print("员工表扩展完成")
            except Exception as e:
                trans.rollback()
                raise e
    except Exception as e:
        print(f"扩展员工表失败: {e}")
        return False
    
    return True

def test_new_models():
    """测试新模型"""
    print("测试新模型...")
    try:
        # 测试PaperProject模型
        paper_count = PaperProject.query.count()
        print(f"论文项目表记录数: {paper_count}")
        
        # 测试PatentProject模型
        patent_count = PatentProject.query.count()
        print(f"专利项目表记录数: {patent_count}")
        
        # 测试ProjectFile模型
        file_count = ProjectFile.query.count()
        print(f"项目文件表记录数: {file_count}")
        
        print("模型测试完成")
        return True
    except Exception as e:
        print(f"模型测试失败: {e}")
        return False

def main():
    """主函数"""
    print("开始论文指导和专利申请功能数据库迁移...")
    print("=" * 50)
    
    # 创建应用上下文
    app = create_app()
    with app.app_context():
        try:
            # 创建新表
            if not create_paper_tables():
                print("论文表创建失败，退出")
                return False
            
            if not create_patent_tables():
                print("专利表创建失败，退出")
                return False
            
            if not create_file_management_table():
                print("文件管理表创建失败，退出")
                return False
            
            # 扩展现有表
            if not extend_existing_tables():
                print("表扩展失败，退出")
                return False
            
            # 测试新模型
            if not test_new_models():
                print("模型测试失败，退出")
                return False
            
            print("=" * 50)
            print("数据库迁移完成！")
            print("新增功能:")
            print("- 论文指导和发表管理")
            print("- 专利申请和保护管理")
            print("- 统一文件管理系统")
            print("- 多业务类型用户支持")
            
        except Exception as e:
            print(f"迁移过程中发生错误: {e}")
            return False
    
    return True

if __name__ == '__main__':
    success = main()
    if success:
        print("\n迁移成功完成！")
    else:
        print("\n迁移失败，请检查错误信息。")
        sys.exit(1)
