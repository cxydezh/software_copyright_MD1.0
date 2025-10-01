#!/usr/bin/env python3
"""
数据验证工具模块
"""

import re
import os
from datetime import datetime, timedelta
from werkzeug.datastructures import FileStorage
from flask import current_app

class ValidationError(Exception):
    """验证错误异常"""
    pass

class FileValidator:
    """文件验证器"""
    
    # 允许的文件类型
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'txt', 'rtf',
        'jpg', 'jpeg', 'png', 'gif', 'bmp',
        'zip', 'rar', '7z'
    }
    
    # 文件大小限制 (字节)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    @classmethod
    def validate_file(cls, file: FileStorage, max_size: int = None) -> dict:
        """
        验证上传文件
        
        Args:
            file: 上传的文件对象
            max_size: 最大文件大小限制
            
        Returns:
            dict: 验证结果
            
        Raises:
            ValidationError: 验证失败时抛出
        """
        if not file or file.filename == '':
            raise ValidationError('请选择要上传的文件')
        
        # 检查文件扩展名
        if '.' not in file.filename:
            raise ValidationError('文件必须包含扩展名')
        
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            allowed_exts = ', '.join(sorted(cls.ALLOWED_EXTENSIONS))
            raise ValidationError(f'不支持的文件类型。允许的类型：{allowed_exts}')
        
        # 检查文件大小
        file.seek(0, 2)  # 移动到文件末尾
        file_size = file.tell()
        file.seek(0)  # 重置到文件开头
        
        max_size = max_size or cls.MAX_FILE_SIZE
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            raise ValidationError(f'文件大小不能超过 {max_size_mb:.1f}MB')
        
        if file_size == 0:
            raise ValidationError('文件不能为空')
        
        return {
            'filename': file.filename,
            'extension': file_ext,
            'size': file_size,
            'valid': True
        }

class PaperValidator:
    """论文项目验证器"""
    
    @staticmethod
    def validate_application(data: dict) -> dict:
        """
        验证论文申请数据
        
        Args:
            data: 申请数据字典
            
        Returns:
            dict: 验证结果
            
        Raises:
            ValidationError: 验证失败时抛出
        """
        errors = {}
        
        # 必填字段验证
        required_fields = ['project_name', 'project_type', 'service_level', 'applicant_type']
        for field in required_fields:
            if not data.get(field) or not data.get(field).strip():
                errors[field] = f'{field} 不能为空'
        
        # 项目名称验证
        project_name = data.get('project_name', '').strip()
        if project_name:
            if len(project_name) < 2:
                errors['project_name'] = '项目名称至少需要2个字符'
            elif len(project_name) > 200:
                errors['project_name'] = '项目名称不能超过200个字符'
        
        # 论文标题验证
        paper_title = data.get('paper_title', '').strip()
        if paper_title and len(paper_title) > 500:
            errors['paper_title'] = '论文标题不能超过500个字符'
        
        # 研究领域验证
        research_field = data.get('research_field', '').strip()
        if research_field and len(research_field) > 100:
            errors['research_field'] = '研究领域不能超过100个字符'
        
        # 目标期刊验证
        target_journal = data.get('target_journal', '').strip()
        if target_journal and len(target_journal) > 200:
            errors['target_journal'] = '目标期刊不能超过200个字符'
        
        # 备注验证
        remarks = data.get('remarks', '').strip()
        if remarks and len(remarks) > 2000:
            errors['remarks'] = '备注不能超过2000个字符'
        
        if errors:
            raise ValidationError('数据验证失败', errors)
        
        return {'valid': True}

class PatentValidator:
    """专利项目验证器"""
    
    @staticmethod
    def validate_application(data: dict) -> dict:
        """
        验证专利申请数据
        
        Args:
            data: 申请数据字典
            
        Returns:
            dict: 验证结果
            
        Raises:
            ValidationError: 验证失败时抛出
        """
        errors = {}
        
        # 必填字段验证
        required_fields = ['project_name', 'project_type', 'applicant_type', 'application_field']
        for field in required_fields:
            if not data.get(field) or not data.get(field).strip():
                errors[field] = f'{field} 不能为空'
        
        # 项目名称验证
        project_name = data.get('project_name', '').strip()
        if project_name:
            if len(project_name) < 2:
                errors['project_name'] = '项目名称至少需要2个字符'
            elif len(project_name) > 200:
                errors['project_name'] = '项目名称不能超过200个字符'
        
        # 发明名称验证
        invention_title = data.get('invention_title', '').strip()
        if invention_title and len(invention_title) > 500:
            errors['invention_title'] = '发明名称不能超过500个字符'
        
        # 技术领域验证
        technical_field = data.get('technical_field', '').strip()
        if technical_field and len(technical_field) > 100:
            errors['technical_field'] = '技术领域不能超过100个字符'
        
        # 申请号验证
        application_number = data.get('application_number', '').strip()
        if application_number:
            if not PatentValidator._validate_application_number(application_number):
                errors['application_number'] = '申请号格式不正确，应为：年份+流水号+校验位'
        
        # 公开号验证
        publication_number = data.get('publication_number', '').strip()
        if publication_number:
            if not PatentValidator._validate_publication_number(publication_number):
                errors['publication_number'] = '公开号格式不正确，应为：CN+流水号+字母'
        
        # 专利号验证
        patent_number = data.get('patent_number', '').strip()
        if patent_number:
            if not PatentValidator._validate_patent_number(patent_number):
                errors['patent_number'] = '专利号格式不正确，应为：ZL+年份+流水号+校验位'
        
        # 年费验证
        annual_fee = data.get('annual_fee')
        if annual_fee is not None:
            try:
                fee = float(annual_fee)
                if fee < 0:
                    errors['annual_fee'] = '年费不能为负数'
                elif fee > 1000000:
                    errors['annual_fee'] = '年费不能超过100万元'
            except (ValueError, TypeError):
                errors['annual_fee'] = '年费必须是有效的数字'
        
        # 备注验证
        remarks = data.get('remarks', '').strip()
        if remarks and len(remarks) > 2000:
            errors['remarks'] = '备注不能超过2000个字符'
        
        if errors:
            raise ValidationError('数据验证失败', errors)
        
        return {'valid': True}
    
    @staticmethod
    def _validate_application_number(number: str) -> bool:
        """验证申请号格式"""
        pattern = r'^\d{4}\d{6}\.\d$'
        return bool(re.match(pattern, number))
    
    @staticmethod
    def _validate_publication_number(number: str) -> bool:
        """验证公开号格式"""
        pattern = r'^CN\d{9}[A-Z]$'
        return bool(re.match(pattern, number))
    
    @staticmethod
    def _validate_patent_number(number: str) -> bool:
        """验证专利号格式"""
        pattern = r'^ZL\d{4}\d{6}\.\d$'
        return bool(re.match(pattern, number))

class BusinessRuleValidator:
    """业务规则验证器"""
    
    @staticmethod
    def validate_project_status_transition(current_status: str, new_status: str, project_type: str) -> bool:
        """
        验证项目状态转换是否符合业务规则
        
        Args:
            current_status: 当前状态
            new_status: 新状态
            project_type: 项目类型 ('paper' 或 'patent')
            
        Returns:
            bool: 是否允许转换
        """
        if project_type == 'paper':
            valid_transitions = {
                '待确认': ['已确认'],
                '已确认': ['进行中'],
                '进行中': ['已投稿', '审稿中', '已完成'],
                '已投稿': ['审稿中', '已录用', '被拒稿'],
                '审稿中': ['已录用', '被拒稿'],
                '已录用': ['已发表'],
                '已发表': ['已完成'],
                '被拒稿': ['进行中']
            }
        elif project_type == 'patent':
            valid_transitions = {
                '待确认': ['已确认'],
                '已确认': ['准备中'],
                '准备中': ['已递交', '已完成'],
                '已递交': ['审查中', '已授权', '已完成'],
                '审查中': ['已授权', '已完成'],
                '已授权': ['维持中', '已完成'],
                '维持中': ['已完成']
            }
        else:
            return False
        
        return new_status in valid_transitions.get(current_status, [])
    
    @staticmethod
    def validate_user_permissions(user, project, action: str) -> bool:
        """
        验证用户权限
        
        Args:
            user: 用户对象
            project: 项目对象
            action: 操作类型 ('view', 'edit', 'delete', 'confirm', 'assign')
            
        Returns:
            bool: 是否有权限
        """
        if not hasattr(user, 'user_type'):
            return False
        
        # 员工权限
        if user.user_type == 'staff':
            if action in ['confirm', 'assign', 'update_status']:
                return True
            elif action in ['view', 'edit']:
                return True
        
        # 用户权限
        elif user.user_type == 'user':
            if hasattr(project, 'applicant_id') and project.applicant_id == user.id:
                if action in ['view', 'edit', 'delete']:
                    return True
        
        return False

class FormValidator:
    """表单验证器"""
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> dict:
        """
        验证必填字段
        
        Args:
            data: 表单数据
            required_fields: 必填字段列表
            
        Returns:
            dict: 验证结果
        """
        errors = {}
        
        for field in required_fields:
            value = data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                errors[field] = f'{field} 是必填字段'
        
        return errors
    
    @staticmethod
    def validate_string_length(data: dict, field: str, min_length: int = 0, max_length: int = None) -> str:
        """
        验证字符串长度
        
        Args:
            data: 表单数据
            field: 字段名
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            str: 错误信息，无错误返回空字符串
        """
        value = data.get(field, '')
        if not isinstance(value, str):
            value = str(value)
        
        value = value.strip()
        
        if len(value) < min_length:
            return f'{field} 至少需要 {min_length} 个字符'
        
        if max_length and len(value) > max_length:
            return f'{field} 不能超过 {max_length} 个字符'
        
        return ''
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱格式"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """验证手机号格式"""
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, phone))
