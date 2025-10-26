#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
郑州医企创医疗科技有限公司 - 软著管理系统桌面客户端
根据需求分析文档重新设计，包含登录界面

功能模块：
1. 任务视图 (Task_view) - 项目管理、文件创建、流水号获取
2. 模板管理 (models_manage) - 软著申请文档模板管理
3. 材料管理 (material_manage) - 申请材料管理
4. 系统设置 (System_setting) - 路径配置
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import json
import requests
import traceback
import warnings

# 抑制libpng和其他图像相关警告
warnings.filterwarnings("ignore", ".*iCCP.*")
warnings.filterwarnings("ignore", ".*sRGB.*")
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning'
import webbrowser
import shutil
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import LOCAL_CONFIG
from desktop_app.local_models import (
    LocalDatabase, DefaultPath, IDCardFile, USCCCFile, 
    ContractFile, TemplateFolder, ProjectFile, LocalProject
)

# 导入各个功能模块
from desktop_app.task_view_new import TaskViewModule
from desktop_app.template_manage import TemplateManageModule
from desktop_app.material_manage import MaterialManageModule
from desktop_app.system_setting import SystemSettingModule
from desktop_app.dialogs import IDCardDialog, USCCCDialog, ContractDialog
from desktop_app.server_client import ServerClient
from desktop_app.logger import get_logger
from desktop_app.safe_tkinter_app import SafeTkinterApp
from desktop_app.tkinter_event_manager import install_tkinter_event_handler


class SoftwareCopyrightMS(SafeTkinterApp):
    """软著管理系统桌面应用主类"""
    
    def __init__(self):
        super().__init__()
        
        # 创建根窗口
        self.root = self.create_root()
        self.root.title("软著管理系统 - 项目执行者工具")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # 安装全局异常捕获，终端可见
        self._install_exception_hooks()
        
        # 安装Tkinter事件处理器
        install_tkinter_event_handler()
        
        # 设置窗口图标
        try:
            self.root.iconbitmap('logo.ico')
        except:
            pass
        
        # 初始化变量
        self.current_user = None
        self.db = None
        self.modules = {}
        self.is_logged_in = False
        self.server_client = None
        self.logger = get_logger('desktop_app.main')
        
        # 初始化本地数据库
        self.init_local_database()
        
        # 初始化服务器客户端
        self.init_server_client()
        
        # 注册清理函数
        self.add_cleanup_function(self._cleanup_on_exit)
        
        # 创建登录界面
        self.create_login_interface()
        
    def init_local_database(self):
        """初始化本地数据库"""
        db_path = LOCAL_CONFIG['LOCAL_DB_PATH']
        self.db = LocalDatabase(db_path)
        
        # 初始化各个管理模块
        self.default_path = DefaultPath(self.db)
        self.id_card_file = IDCardFile(self.db)
        self.usccc_file = USCCCFile(self.db)
        self.contract_file = ContractFile(self.db)
        self.template_file = TemplateFolder(self.db)
        self.project_file = ProjectFile(self.db)
        self.local_project = LocalProject(self.db)
        
        # 设置默认路径（如果不存在）
        self.setup_default_paths()

    def _install_exception_hooks(self):
        """安装终端可见的异常捕获：sys.excepthook 与 Tkinter 回调异常。"""
        def excepthook(exc_type, exc_value, exc_tb):
            try:
                self.logger.exception("未捕获异常", exc_info=(exc_type, exc_value, exc_tb))
            except Exception:
                pass
            traceback.print_exception(exc_type, exc_value, exc_tb)
        sys.excepthook = excepthook

        def tk_report_callback_exception(exc_type, exc_value, exc_tb):
            try:
                self.logger.exception("Tk 回调异常", exc_info=(exc_type, exc_value, exc_tb))
            except Exception:
                pass
            traceback.print_exception(exc_type, exc_value, exc_tb)
            try:
                messagebox.showerror("运行错误", f"{exc_type.__name__}: {exc_value}")
            except Exception:
                pass
        try:
            self.root.report_callback_exception = tk_report_callback_exception
        except Exception:
            pass
    
    def setup_default_paths(self):
        """设置默认路径"""
        default_paths = {
            'template_path': LOCAL_CONFIG['MODEL_DIR'],
            'id_card_path': LOCAL_CONFIG['IDPDF_DIR'],
            'usccc_path': LOCAL_CONFIG['USCCC_DIR'],
            'contract_path': LOCAL_CONFIG['CONTRACT_DIR'],
            'project_path': LOCAL_CONFIG['PROJECT_FILE_DIR']
        }
        
        for path_type, path_value in default_paths.items():
            if not self.default_path.get_path(path_type):
                self.default_path.set_path(path_type, path_value)
    
    def init_server_client(self):
        """初始化服务器客户端"""
        try:
            # 从本地配置获取 Web API 地址和端口（与数据库地址隔离）
            server_host = self.default_path.get_path('web_api_host') or LOCAL_CONFIG.get('WEB_API_HOST', 'http://192.168.31.56')
            server_port = int(self.default_path.get_path('web_api_port') or LOCAL_CONFIG.get('WEB_API_PORT', 5000))
            
            self.server_client = ServerClient(server_host, server_port)
            self.logger.info("服务器客户端已初始化: %s:%s", server_host, server_port)
        except Exception as e:
            self.logger.exception("服务器客户端初始化失败: %s", e)
            # 使用默认配置
            self.server_client = ServerClient()
    
    def create_login_interface(self):
        """创建登录界面"""
        # 清除现有界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 设置窗口标题
        self.root.title("软著管理系统 - 登录")
        
        # 创建主框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True)
        
        # 创建登录表单
        login_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=2)
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # 标题
        title_label = tk.Label(login_frame, text="软著管理系统", 
                              font=('Microsoft YaHei', 16, 'bold'), 
                              bg='white', fg='#2c3e50')
        title_label.pack(pady=(20, 30))
        
        # 用户类型选择
        tk.Label(login_frame, text="用户类型:", 
                font=('Microsoft YaHei', 10), bg='white').pack(anchor='w', padx=20)
        
        self.user_type_var = tk.StringVar(value="staff")
        user_type_frame = tk.Frame(login_frame, bg='white')
        user_type_frame.pack(pady=(5, 15), padx=20)
        
        tk.Radiobutton(user_type_frame, text="普通用户", variable=self.user_type_var, 
                      value="general", font=('Microsoft YaHei', 9), bg='white').pack(side='left', padx=(0, 20))
        tk.Radiobutton(user_type_frame, text="员工", variable=self.user_type_var, 
                      value="staff", font=('Microsoft YaHei', 9), bg='white').pack(side='left')
        
        # 用户名输入
        tk.Label(login_frame, text="用户名:", 
                font=('Microsoft YaHei', 10), bg='white').pack(anchor='w', padx=20)
        self.username_var = tk.StringVar()
        username_entry = tk.Entry(login_frame, textvariable=self.username_var, 
                                 font=('Microsoft YaHei', 10), width=25)
        username_entry.pack(pady=(5, 15), padx=20)
        
        # 密码输入
        tk.Label(login_frame, text="密码:", 
                font=('Microsoft YaHei', 10), bg='white').pack(anchor='w', padx=20)
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(login_frame, textvariable=self.password_var, 
                                 font=('Microsoft YaHei', 10), width=25, show='*')
        password_entry.pack(pady=(5, 15), padx=20)
        
        # 登录按钮
        login_btn = tk.Button(login_frame, text="登录", 
                             font=('Microsoft YaHei', 10), bg='#3498db', fg='white',
                             command=self.login, width=20)
        login_btn.pack(pady=(10, 20))
        
        # 绑定回车键登录
        username_entry.bind('<Return>', lambda e: self.login())
        password_entry.bind('<Return>', lambda e: self.login())
        
        # 设置默认焦点
        username_entry.focus()
        self.username_var.set('cxyde@sina.cn')
        self.password_var.set('admin123')

    def login(self):
        """处理登录"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        user_type = self.user_type_var.get()
        
        if not username or not password:
            messagebox.showwarning("警告", "请输入用户名和密码")
            return
        
        # 检查服务器连接
        if not self.server_client:
            messagebox.showerror("错误", "服务器客户端未初始化，请检查系统设置")
            return
        
        # 显示登录进度（如果状态栏尚未创建则忽略）
        self._set_status("正在连接服务器...")
        self.logger.info("尝试登录: user_type=%s, username=%s", user_type, username)
        self.root.update()
        
        try:
            # 使用服务器API进行登录验证
            success, message, user_data = self.server_client.login(username, password, user_type)
            
            if success and user_data:
                self.current_user = {
                    'id': user_data.get('id'),
                    'username': user_data.get('name', username),
                    'email': user_data.get('email', username),
                    'user_type': user_type,
                    'login_time': datetime.now(),
                    'position': user_data.get('position', ''),
                    'permissions': user_data.get('permissions', {})
                }
                self.is_logged_in = True
                self._set_status(f"登录成功: {self.current_user['username']}")
                self.logger.info("登录成功: %s (%s)", self.current_user['email'], user_type)
                self.create_main_interface()
            else:
                self._set_status("登录失败")
                self.logger.warning("登录失败: %s", message)
                messagebox.showerror("登录失败", message or "用户名或密码错误")
                
        except Exception as e:
            self._set_status("登录失败")
            self.logger.exception("登录异常: %s", e)
            messagebox.showerror("登录失败", f"连接服务器时发生错误: {str(e)}")
        
    def create_main_interface(self):
        """创建主界面"""
        # 清除登录界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 设置窗口标题
        self.root.title(f"软著管理系统 - 欢迎 {self.current_user['username']}")
        
        # 创建菜单栏
        self.create_menubar()
        
        # 创建主框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建Notebook（选项卡）
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True)
        
        # 创建各个功能模块
        self.create_modules()
        
        # 创建状态栏
        self.create_statusbar()
        
        # 自动同步项目数据（如果用户是员工）
        if self.current_user.get('user_type') == '员工':
            self.sync_projects()
    
    def create_menubar(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="同步项目", command=self.sync_projects)
        file_menu.add_separator()
        file_menu.add_command(label="退出登录", command=self.logout)
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="打开公司网站", command=self.open_company_website)
        tools_menu.add_command(label="打开版权中心", command=self.open_copyright_center)
        tools_menu.add_separator()
        tools_menu.add_command(label="打开文件目录", command=self.open_file_directory)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_modules(self):
        """创建各个功能模块"""
        # 任务视图模块
        self.modules['task_view'] = TaskViewModule(
            self.notebook, self.db, self.local_project, self.project_file,
            self.id_card_file, self.usccc_file, self.contract_file, self.template_file,
            server_client=self.server_client, current_user=self.current_user, default_path=self.default_path
        )
        
        # 模板管理模块
        self.modules['template_manage'] = TemplateManageModule(
            self.notebook, self.db, self.template_file, self.default_path
        )
        
        # 材料管理模块
        self.modules['material_manage'] = MaterialManageModule(
            self.notebook, self.db, self.id_card_file, self.usccc_file, 
            self.contract_file, self.default_path
        )
        
        # 系统设置模块
        self.modules['system_setting'] = SystemSettingModule(
            self.notebook, self.db, self.default_path
        )
        
        # 绑定设置更新事件
        self.bind_setting_update_events()
    
    def bind_setting_update_events(self):
        """绑定设置更新事件"""
        # 当系统设置中的服务器配置发生变化时，重新初始化服务器客户端
        if hasattr(self.modules.get('system_setting'), 'server_host_var'):
            # 监听服务器地址和端口变化
            self.modules['system_setting'].server_host_var.trace('w', self.on_server_config_change)
            self.modules['system_setting'].server_port_var.trace('w', self.on_server_config_change)
    
    def on_server_config_change(self, *args):
        """服务器配置变化时的回调"""
        try:
            # 重新初始化服务器客户端
            server_host = self.modules['system_setting'].server_host_var.get().strip()
            server_port = self.modules['system_setting'].server_port_var.get().strip()
            
            if server_host and server_port:
                self.server_client = ServerClient(server_host, int(server_port))
                print(f"服务器客户端已更新: {server_host}:{server_port}")
        except Exception as e:
            print(f"更新服务器客户端失败: {e}")
    
    def create_statusbar(self):
        """创建状态栏"""
        status_frame = tk.Frame(self.root, bg='#e0e0e0', height=25)
        status_frame.pack(side='bottom', fill='x')
        
        self.status_var = tk.StringVar(value=f"已登录: {self.current_user['username']} ({self.current_user['user_type']})")
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               font=('Microsoft YaHei', 9), bg='#e0e0e0')
        status_label.pack(side='left', padx=10, pady=2)
        
        time_label = tk.Label(status_frame, text=f"登录时间: {self.current_user['login_time'].strftime('%Y-%m-%d %H:%M:%S')}",
                             font=('Microsoft YaHei', 9), bg='#e0e0e0')
        time_label.pack(side='right', padx=10, pady=2)
    
    def logout(self):
        """退出登录"""
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            self.is_logged_in = False
            self.current_user = None
            self.create_login_interface()
    
    def sync_projects(self):
        """同步项目数据"""
        try:
            self._set_status("正在同步项目数据...")
            self.logger.info("开始同步项目数据")
            self.root.update()
            
            # 检查服务器连接
            if not self.server_client:
                messagebox.showerror("错误", "服务器客户端未初始化，请检查系统设置")
                return
            
            # 检查用户权限（只有员工可以同步项目）
            if self.current_user.get('user_type') != 'staff':
                messagebox.showwarning("权限不足", "只有员工用户可以同步项目数据")
                return
            
            # 从服务器获取项目数据
            success, message, projects_data = self.server_client.get_all_projects_for_sync()
            
            if success and projects_data:
                # 同步到本地数据库
                self.local_project.sync_projects(projects_data)
                
                # 刷新任务视图
                if 'task_view' in self.modules:
                    self.modules['task_view'].refresh_projects()
                
                self._set_status(f"已登录: {self.current_user['username']} ({self.current_user['user_type']})")
                self.logger.info("同步完成: %d 个项目", len(projects_data))
                messagebox.showinfo("同步完成", f"成功同步 {len(projects_data)} 个项目")
            else:
                self._set_status(f"已登录: {self.current_user['username']} ({self.current_user['user_type']})")
                self.logger.warning("同步失败: %s", message)
                messagebox.showerror("同步失败", message or "无法从服务器获取项目数据")
            
        except Exception as e:
            self._set_status(f"已登录: {self.current_user['username']} ({self.current_user['user_type']})")
            self.logger.exception("同步异常: %s", e)
            messagebox.showerror("同步失败", f"同步项目数据时发生错误: {str(e)}")
    
    def get_mock_projects(self):
        """获取模拟项目数据"""
        # 这里应该从服务器获取真实数据
        return [
            {
                'id': 1,
                'project_name': '示例软件项目-1',
                'project_type': '软件登记业务',
                'applicant_type': '个人',
                'copyright_owner': '示例著作权人',
                'software_applicant_name': '示例申请人',
                'serial_number': None,
                'priority': '普通',
                'status': '已立项',
                'executor_id': 1,
                'remarks': '示例项目'
            }
        ]
    
    def open_company_website(self):
        """打开公司网站"""
        try:
            webbrowser.open(LOCAL_CONFIG['COMPANY_WEBSITE'])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开网站: {str(e)}")
    
    def open_copyright_center(self):
        """打开版权保护中心网站"""
        try:
            webbrowser.open(LOCAL_CONFIG['COPYRIGHT_CENTER_URL'])
        except Exception as e:
            messagebox.showerror("错误", f"无法打开网站: {str(e)}")
    
    def open_file_directory(self):
        """打开文件目录"""
        try:
            base_dir = self.default_path.get_path('project_path') or LOCAL_CONFIG['BASE_DIR']
            os.startfile(base_dir)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """软著管理系统 v2.0
        
郑州医企创医疗科技有限公司
项目执行者专用工具

功能特性:
• 任务视图 - 项目管理、文件创建、流水号获取
• 模板管理 - 软著申请文档模板管理
• 材料管理 - 申请材料管理
• 系统设置 - 路径配置

技术支持: admin@yiqichuang.com"""
        
        messagebox.showinfo("关于", about_text)
    
    def run(self):
        """运行应用程序"""
        try:
            # 启动主循环
            super().run()
        except Exception as e:
            print(f"[DEBUG] 应用运行异常: {e}")
            self._cleanup_on_exit()
    
    def _cleanup_on_exit(self):
        """程序退出时的清理"""
        try:
            print("[DEBUG] 开始清理资源...")
            
            # 清理Playwright浏览器实例
            try:
                from desktop_app.serial_fetcher_simple import clear_global_browser
                clear_global_browser()
                print("[DEBUG] Playwright浏览器实例已清理")
            except Exception as e:
                print(f"[DEBUG] 清理Playwright实例失败: {e}")
            
            # 清理其他资源
            try:
                if hasattr(self, 'server_client') and self.server_client:
                    # 如果有服务器客户端，可以在这里清理
                    pass
                print("[DEBUG] 其他资源已清理")
            except Exception as e:
                print(f"[DEBUG] 清理其他资源失败: {e}")
            
            print("[DEBUG] 资源清理完成")
        except Exception as e:
            print(f"[DEBUG] 清理过程中出错: {e}")

    # -------- 通用小工具 --------
    def _set_status(self, text: str):
        """安全设置状态栏文本：在状态栏尚未创建时不报错"""
        try:
            if hasattr(self, 'status_var') and isinstance(self.status_var, tk.StringVar):
                self.status_var.set(text)
        except Exception:
            pass


def main():
    """主函数"""
    print("=" * 60)
    print("郑州医企创医疗科技有限公司 - 软著管理系统")
    print("桌面客户端启动中...")
    print("=" * 60)
    
    try:
        app = SoftwareCopyrightMS()
        print("桌面应用已启动")
        print("=" * 60)
        app.run()
        
    except Exception as e:
        messagebox.showerror("启动错误", f"应用启动失败: {str(e)}")
        print(f"错误详情: {e}")


if __name__ == '__main__':
    main()
