#!/usr/bin/env python3
"""
通知系统模块
"""

import os
import sys
from datetime import datetime, timedelta
from flask import current_app, render_template
from flask_mail import Message

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import db, Message as MessageModel, User, Staff, PaperProject, PatentProject

class NotificationService:
    """通知服务类"""
    
    @staticmethod
    def send_project_status_notification(project, old_status: str, new_status: str, project_type: str):
        """
        发送项目状态变更通知
        
        Args:
            project: 项目对象
            old_status: 旧状态
            new_status: 新状态
            project_type: 项目类型 ('paper' 或 'patent')
        """
        try:
            # 获取申请人
            applicant = User.query.get(project.applicant_id)
            if not applicant:
                return
            
            # 构建通知内容
            subject = f"项目状态更新通知 - {project.project_name}"
            
            # 根据项目类型和状态变化生成不同的消息
            if project_type == 'paper':
                status_messages = {
                    '已确认': '您的论文指导项目已确认，我们将尽快安排专家为您服务。',
                    '进行中': '您的论文指导项目已开始执行，专家正在为您提供专业指导。',
                    '已投稿': '您的论文已成功投稿，请耐心等待审稿结果。',
                    '审稿中': '您的论文正在审稿中，我们会及时通知您审稿进度。',
                    '已录用': '恭喜！您的论文已被录用，即将发表。',
                    '已发表': '您的论文已成功发表，感谢您选择我们的服务。',
                    '已完成': '您的论文指导项目已完成，感谢您的信任。',
                    '被拒稿': '很遗憾，您的论文被拒稿，我们的专家将协助您改进。'
                }
            else:  # patent
                status_messages = {
                    '已确认': '您的专利申请项目已确认，我们将尽快安排专家为您服务。',
                    '准备中': '您的专利申请项目正在准备中，专家正在为您准备申请材料。',
                    '已递交': '您的专利申请已成功递交，请耐心等待审查结果。',
                    '审查中': '您的专利申请正在审查中，我们会及时通知您审查进度。',
                    '已授权': '恭喜！您的专利申请已获得授权。',
                    '维持中': '您的专利正在维持中，我们会协助您处理相关事务。',
                    '已完成': '您的专利申请项目已完成，感谢您的信任。'
                }
            
            message_content = status_messages.get(new_status, f'您的项目状态已更新为：{new_status}')
            
            # 发送邮件通知
            NotificationService._send_email_notification(
                to_email=applicant.email,
                subject=subject,
                template='emails/project_status_update.html',
                project=project,
                old_status=old_status,
                new_status=new_status,
                message_content=message_content,
                project_type=project_type
            )
            
            # 创建站内消息
            NotificationService._create_internal_message(
                user_id=applicant.id,
                title=f"项目状态更新 - {project.project_name}",
                content=message_content,
                project_id=project.id,
                project_type=project_type
            )
            
        except Exception as e:
            current_app.logger.error(f"发送项目状态通知失败: {str(e)}")
    
    @staticmethod
    def send_executor_assigned_notification(project, executor, project_type: str):
        """
        发送执行者分配通知
        
        Args:
            project: 项目对象
            executor: 执行者对象
            project_type: 项目类型
        """
        try:
            # 获取申请人
            applicant = User.query.get(project.applicant_id)
            if not applicant:
                return
            
            subject = f"项目执行者分配通知 - {project.project_name}"
            message_content = f"您的项目已分配给执行者：{executor.name}，联系方式：{executor.email}"
            
            # 发送邮件通知
            NotificationService._send_email_notification(
                to_email=applicant.email,
                subject=subject,
                template='emails/executor_assigned.html',
                project=project,
                executor=executor,
                message_content=message_content,
                project_type=project_type
            )
            
            # 创建站内消息
            NotificationService._create_internal_message(
                user_id=applicant.id,
                title=f"执行者分配 - {project.project_name}",
                content=message_content,
                project_id=project.id,
                project_type=project_type
            )
            
        except Exception as e:
            current_app.logger.error(f"发送执行者分配通知失败: {str(e)}")
    
    @staticmethod
    def send_project_reminder(project, reminder_type: str, project_type: str):
        """
        发送项目提醒
        
        Args:
            project: 项目对象
            reminder_type: 提醒类型
            project_type: 项目类型
        """
        try:
            # 获取申请人
            applicant = User.query.get(project.applicant_id)
            if not applicant:
                return
            
            # 根据提醒类型生成不同的消息
            reminder_messages = {
                'deadline_approaching': '您的项目截止日期即将到来，请及时关注项目进度。',
                'long_pending': '您的项目已长时间处于待处理状态，我们会尽快处理。',
                'follow_up': '项目需要您的配合，请及时查看项目详情。'
            }
            
            message_content = reminder_messages.get(reminder_type, '项目提醒')
            subject = f"项目提醒 - {project.project_name}"
            
            # 发送邮件通知
            NotificationService._send_email_notification(
                to_email=applicant.email,
                subject=subject,
                template='emails/project_reminder.html',
                project=project,
                reminder_type=reminder_type,
                message_content=message_content,
                project_type=project_type
            )
            
            # 创建站内消息
            NotificationService._create_internal_message(
                user_id=applicant.id,
                title=f"项目提醒 - {project.project_name}",
                content=message_content,
                project_id=project.id,
                project_type=project_type
            )
            
        except Exception as e:
            current_app.logger.error(f"发送项目提醒失败: {str(e)}")
    
    @staticmethod
    def _send_email_notification(to_email: str, subject: str, template: str, **kwargs):
        """发送邮件通知"""
        try:
            if not current_app.extensions.get('mail'):
                current_app.logger.warning("邮件服务未配置，跳过邮件发送")
                return
            
            msg = Message(
                subject=subject,
                recipients=[to_email],
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            # 渲染邮件模板
            msg.html = render_template(template, **kwargs)
            
            # 发送邮件
            current_app.extensions['mail'].send(msg)
            current_app.logger.info(f"邮件发送成功: {to_email}")
            
        except Exception as e:
            current_app.logger.error(f"邮件发送失败: {str(e)}")
    
    @staticmethod
    def _create_internal_message(user_id: int, title: str, content: str, 
                                project_id: int = None, project_type: str = None):
        """创建站内消息"""
        try:
            message = MessageModel(
                user_id=user_id,
                title=title,
                content=content,
                project_id=project_id,
                project_type=project_type,
                create_time=datetime.utcnow()
            )
            
            db.session.add(message)
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"创建站内消息失败: {str(e)}")
    
    @staticmethod
    def get_user_messages(user_id: int, limit: int = 10, unread_only: bool = False):
        """
        获取用户消息
        
        Args:
            user_id: 用户ID
            limit: 限制数量
            unread_only: 是否只获取未读消息
            
        Returns:
            list: 消息列表
        """
        try:
            query = MessageModel.query.filter_by(user_id=user_id)
            
            if unread_only:
                query = query.filter_by(is_read=False)
            
            messages = query.order_by(MessageModel.create_time.desc()).limit(limit).all()
            
            return messages
            
        except Exception as e:
            current_app.logger.error(f"获取用户消息失败: {str(e)}")
            return []
    
    @staticmethod
    def mark_message_as_read(message_id: int, user_id: int):
        """
        标记消息为已读
        
        Args:
            message_id: 消息ID
            user_id: 用户ID
        """
        try:
            message = MessageModel.query.filter_by(id=message_id, user_id=user_id).first()
            if message:
                message.is_read = True
                message.read_time = datetime.utcnow()
                db.session.commit()
                
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"标记消息已读失败: {str(e)}")
    
    @staticmethod
    def get_unread_message_count(user_id: int):
        """
        获取未读消息数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 未读消息数量
        """
        try:
            count = MessageModel.query.filter_by(user_id=user_id, is_read=False).count()
            return count
            
        except Exception as e:
            current_app.logger.error(f"获取未读消息数量失败: {str(e)}")
            return 0

class ReminderService:
    """提醒服务类"""
    
    @staticmethod
    def check_project_deadlines():
        """检查项目截止日期"""
        try:
            # 检查论文项目
            paper_projects = PaperProject.query.filter(
                PaperProject.status.in_(['进行中', '已投稿', '审稿中']),
                PaperProject.deadline.isnot(None),
                PaperProject.deadline <= datetime.utcnow() + timedelta(days=7)
            ).all()
            
            for project in paper_projects:
                NotificationService.send_project_reminder(
                    project, 'deadline_approaching', 'paper'
                )
            
            # 检查专利项目
            patent_projects = PatentProject.query.filter(
                PatentProject.status.in_(['准备中', '已递交', '审查中']),
                PatentProject.deadline.isnot(None),
                PatentProject.deadline <= datetime.utcnow() + timedelta(days=7)
            ).all()
            
            for project in patent_projects:
                NotificationService.send_project_reminder(
                    project, 'deadline_approaching', 'patent'
                )
                
        except Exception as e:
            current_app.logger.error(f"检查项目截止日期失败: {str(e)}")
    
    @staticmethod
    def check_long_pending_projects():
        """检查长时间待处理的项目"""
        try:
            # 检查超过3天未确认的论文项目
            paper_projects = PaperProject.query.filter(
                PaperProject.status == '待确认',
                PaperProject.apply_time <= datetime.utcnow() - timedelta(days=3)
            ).all()
            
            for project in paper_projects:
                NotificationService.send_project_reminder(
                    project, 'long_pending', 'paper'
                )
            
            # 检查超过3天未确认的专利项目
            patent_projects = PatentProject.query.filter(
                PatentProject.status == '待确认',
                PatentProject.apply_time <= datetime.utcnow() - timedelta(days=3)
            ).all()
            
            for project in patent_projects:
                NotificationService.send_project_reminder(
                    project, 'long_pending', 'patent'
                )
                
        except Exception as e:
            current_app.logger.error(f"检查长时间待处理项目失败: {str(e)}")
