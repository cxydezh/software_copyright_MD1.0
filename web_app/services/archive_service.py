#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
项目归档服务模块
实现项目从活动表迁移到归档表的功能
"""

from database.models import (
    db, Project, PaperProject, PatentProject,
    ArchivedSoftwareProject, ArchivedPaperProject, ArchivedPatentProject,
    ProcessLog
)
from datetime import datetime


class ArchiveService:
    """项目归档服务"""
    
    @staticmethod
    def archive_software_project(project_id):
        """归档软著项目"""
        try:
            # 获取原项目
            project = Project.query.get(project_id)
            if not project:
                return False, "项目不存在"
            
            # 检查是否已结算
            if not project.is_settled:
                return False, "项目尚未结算，无法归档"
            
            # 检查是否已归档
            if project.is_archived:
                return False, "项目已归档"
            
            # 创建归档记录
            archived_project = ArchivedSoftwareProject(
                id=project.id,
                project_name=project.project_name,
                project_type=project.project_type,
                applicant_type=project.applicant_type,
                copyright_owner=project.copyright_owner,
                software_applicant_name=project.software_applicant_name,
                serial_number=project.serial_number,
                priority=project.priority,
                apply_time=project.apply_time,
                confirm_time=project.confirm_time,
                execute_time=project.execute_time,
                complete_time=project.complete_time,
                settle_time=project.settle_time,
                submit_time=project.submit_time,
                certificate_time=project.certificate_time,
                archive_time=datetime.utcnow(),
                price=project.price,
                discount=project.discount,
                is_archived=True,
                is_settled=True,
                applicant_id=project.applicant_id,
                confirmer_id=project.confirmer_id,
                executor_id=project.executor_id,
                remarks=project.remarks
            )
            
            # 添加归档记录
            db.session.add(archived_project)
            
            # 记录流程日志
            log = ProcessLog(
                project_type='software',
                project_id=project.id,
                action='archive',
                from_status=project.status,
                to_status='已归档',
                note='项目已归档到归档表',
                created_at=datetime.utcnow()
            )
            db.session.add(log)
            
            # 删除原项目
            db.session.delete(project)
            
            # 提交事务
            db.session.commit()
            
            return True, "软著项目归档成功"
            
        except Exception as e:
            db.session.rollback()
            return False, f"归档失败: {str(e)}"
    
    @staticmethod
    def archive_paper_project(project_id):
        """归档论文项目"""
        try:
            # 获取原项目
            project = PaperProject.query.get(project_id)
            if not project:
                return False, "项目不存在"
            
            # 检查是否已结算
            if not project.is_settled:
                return False, "项目尚未结算，无法归档"
            
            # 检查是否已归档
            if project.is_archived:
                return False, "项目已归档"
            
            # 创建归档记录
            archived_project = ArchivedPaperProject(
                id=project.id,
                project_name=project.project_name,
                project_type=project.project_type,
                service_level=project.service_level,
                applicant_type=project.applicant_type,
                paper_title=project.paper_title,
                research_field=project.research_field,
                target_journal=project.target_journal,
                paper_status=project.paper_status,
                apply_time=project.apply_time,
                confirm_time=project.confirm_time,
                start_time=project.start_time,
                submit_time=project.submit_time,
                accept_time=project.accept_time,
                publish_time=project.publish_time,
                archive_time=datetime.utcnow(),
                price=project.price,
                discount=project.discount,
                settle_time=project.settle_time,
                status='已归档',
                is_archived=True,
                is_settled=True,
                applicant_id=project.applicant_id,
                confirmer_id=project.confirmer_id,
                executor_id=project.executor_id,
                remarks=project.remarks
            )
            
            # 添加归档记录
            db.session.add(archived_project)
            
            # 记录流程日志
            log = ProcessLog(
                project_type='paper',
                project_id=project.id,
                action='archive',
                from_status=project.status,
                to_status='已归档',
                note='项目已归档到归档表',
                created_at=datetime.utcnow()
            )
            db.session.add(log)
            
            # 删除原项目
            db.session.delete(project)
            
            # 提交事务
            db.session.commit()
            
            return True, "论文项目归档成功"
            
        except Exception as e:
            db.session.rollback()
            return False, f"归档失败: {str(e)}"
    
    @staticmethod
    def archive_patent_project(project_id):
        """归档专利项目"""
        try:
            # 获取原项目
            project = PatentProject.query.get(project_id)
            if not project:
                return False, "项目不存在"
            
            # 检查是否已结算
            if not project.is_settled:
                return False, "项目尚未结算，无法归档"
            
            # 检查是否已归档
            if project.is_archived:
                return False, "项目已归档"
            
            # 创建归档记录
            archived_project = ArchivedPatentProject(
                id=project.id,
                project_name=project.project_name,
                project_type=project.project_type,
                applicant_type=project.applicant_type,
                application_field=project.application_field,
                invention_title=project.invention_title,
                technical_field=project.technical_field,
                application_number=project.application_number,
                publication_number=project.publication_number,
                patent_number=project.patent_number,
                patent_status=project.patent_status,
                apply_time=project.apply_time,
                confirm_time=project.confirm_time,
                start_time=project.start_time,
                file_time=project.file_time,
                publish_time=project.publish_time,
                grant_time=project.grant_time,
                archive_time=datetime.utcnow(),
                price=project.price,
                discount=project.discount,
                annual_fee=project.annual_fee,
                settle_time=project.settle_time,
                status='已归档',
                is_archived=True,
                is_settled=True,
                applicant_id=project.applicant_id,
                confirmer_id=project.confirmer_id,
                executor_id=project.executor_id,
                remarks=project.remarks
            )
            
            # 添加归档记录
            db.session.add(archived_project)
            
            # 记录流程日志
            log = ProcessLog(
                project_type='patent',
                project_id=project.id,
                action='archive',
                from_status=project.status,
                to_status='已归档',
                note='项目已归档到归档表',
                created_at=datetime.utcnow()
            )
            db.session.add(log)
            
            # 删除原项目
            db.session.delete(project)
            
            # 提交事务
            db.session.commit()
            
            return True, "专利项目归档成功"
            
        except Exception as e:
            db.session.rollback()
            return False, f"归档失败: {str(e)}"
    
    @staticmethod
    def get_archived_projects(project_type='all', page=1, per_page=20):
        """获取归档项目列表"""
        try:
            if project_type == 'software' or project_type == 'all':
                software_projects = ArchivedSoftwareProject.query.order_by(
                    ArchivedSoftwareProject.archive_time.desc()
                ).all()
            else:
                software_projects = []
            
            if project_type == 'paper' or project_type == 'all':
                paper_projects = ArchivedPaperProject.query.order_by(
                    ArchivedPaperProject.archive_time.desc()
                ).all()
            else:
                paper_projects = []
            
            if project_type == 'patent' or project_type == 'all':
                patent_projects = ArchivedPatentProject.query.order_by(
                    ArchivedPatentProject.archive_time.desc()
                ).all()
            else:
                patent_projects = []
            
            return {
                'software': software_projects,
                'paper': paper_projects,
                'patent': patent_projects
            }
            
        except Exception as e:
            return None
    
    @staticmethod
    def search_archived_projects(keyword, project_type='all'):
        """搜索归档项目"""
        try:
            results = {
                'software': [],
                'paper': [],
                'patent': []
            }
            
            if project_type in ['software', 'all']:
                results['software'] = ArchivedSoftwareProject.query.filter(
                    db.or_(
                        ArchivedSoftwareProject.project_name.like(f'%{keyword}%'),
                        ArchivedSoftwareProject.copyright_owner.like(f'%{keyword}%'),
                        ArchivedSoftwareProject.serial_number.like(f'%{keyword}%')
                    )
                ).all()
            
            if project_type in ['paper', 'all']:
                results['paper'] = ArchivedPaperProject.query.filter(
                    db.or_(
                        ArchivedPaperProject.project_name.like(f'%{keyword}%'),
                        ArchivedPaperProject.paper_title.like(f'%{keyword}%'),
                        ArchivedPaperProject.target_journal.like(f'%{keyword}%')
                    )
                ).all()
            
            if project_type in ['patent', 'all']:
                results['patent'] = ArchivedPatentProject.query.filter(
                    db.or_(
                        ArchivedPatentProject.project_name.like(f'%{keyword}%'),
                        ArchivedPatentProject.invention_title.like(f'%{keyword}%'),
                        ArchivedPatentProject.patent_number.like(f'%{keyword}%')
                    )
                ).all()
            
            return results
            
        except Exception as e:
            return None

