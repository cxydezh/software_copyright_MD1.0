#!/usr/bin/env python3
"""
定时任务调度器
处理项目提醒、状态检查等定时任务
"""

import os
import sys
import schedule
import time
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from web_app.app import create_app
from web_app.utils.notifications import ReminderService

def run_reminder_tasks():
    """运行提醒任务"""
    app = create_app()
    
    with app.app_context():
        print(f"[{datetime.now()}] 开始运行提醒任务...")
        
        try:
            # 检查项目截止日期
            print("检查项目截止日期...")
            ReminderService.check_project_deadlines()
            
            # 检查长时间待处理的项目
            print("检查长时间待处理的项目...")
            ReminderService.check_long_pending_projects()
            
            print(f"[{datetime.now()}] 提醒任务完成")
            
        except Exception as e:
            print(f"[{datetime.now()}] 提醒任务执行失败: {str(e)}")

def main():
    """主函数"""
    print("启动定时任务调度器...")
    
    # 设置定时任务
    # 每天上午9点运行提醒任务
    schedule.every().day.at("09:00").do(run_reminder_tasks)
    
    # 每4小时运行一次提醒任务
    schedule.every(4).hours.do(run_reminder_tasks)
    
    print("定时任务已设置:")
    print("- 每天上午9点运行提醒任务")
    print("- 每4小时运行一次提醒任务")
    print("调度器已启动，按 Ctrl+C 停止...")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        print("\n调度器已停止")

if __name__ == '__main__':
    main()
