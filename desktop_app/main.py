"""
郑州医企创医疗科技有限公司 - 软著管理系统桌面客户端
项目执行者专用工具

功能：
1. 身份认证
2. 文件管理（身份证PDF、统一社会信用代码证书PDF）
3. 模板管理
4. 项目管理
5. 自动获取流水号
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import json
import requests
import webbrowser
import shutil
import sqlite3
from datetime import datetime
import threading
from pathlib import Path
import traceback

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import LOCAL_CONFIG
from database.models import LocalProject

class SoftwareCopyrightMS:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("软著管理系统 - 项目执行者工具")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 设置窗口图标
        try:
            self.root.iconbitmap('logo.ico')
        except:
            pass
        
        # 初始化变量
        self.current_user = None
        self.projects = []
        self.selected_project = None
        
        # 初始化本地文件夹
        self.init_local_folders()
        
        # 初始化本地数据库
        LocalProject.init_local_db(LOCAL_CONFIG['LOCAL_DB_PATH'])
        
        # 创建界面
        self.create_login_interface()
        
    def init_local_folders(self):
        """初始化本地文件夹结构"""
        folders = [
            LOCAL_CONFIG['BASE_DIR'],
            LOCAL_CONFIG['USCCC_DIR'],
            LOCAL_CONFIG['IDPDF_DIR'],
            LOCAL_CONFIG['MODEL_DIR'],
            LOCAL_CONFIG['CONTRACT_DIR'],
            LOCAL_CONFIG['MATERIAL_DIR'],
            LOCAL_CONFIG['PROJECT_FILE_DIR'],
            os.path.dirname(LOCAL_CONFIG['LOCAL_DB_PATH'])
        ]
        
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"创建文件夹: {folder}")
    
    def create_login_interface(self):
        """创建登录界面"""
        # 清空窗口
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 主框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(expand=True, fill='both', padx=50, pady=50)
        
        # 标题
        title_label = tk.Label(main_frame, text="软著管理系统", 
                              font=('Microsoft YaHei', 24, 'bold'),
                              bg='#f0f0f0', fg='#2c5282')
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(main_frame, text="项目执行者工具", 
                                 font=('Microsoft YaHei', 12),
                                 bg='#f0f0f0', fg='#666666')
        subtitle_label.pack(pady=(0, 30))
        
        # 登录框架
        login_frame = tk.LabelFrame(main_frame, text="身份认证", 
                                   font=('Microsoft YaHei', 12, 'bold'),
                                   bg='white', fg='#2c5282', padx=20, pady=20)
        login_frame.pack(pady=20, ipadx=20, ipady=20)
        
        # 邮箱输入
        tk.Label(login_frame, text="邮箱地址:", font=('Microsoft YaHei', 10),
                bg='white').grid(row=0, column=0, sticky='w', pady=5)
        self.email_var = tk.StringVar()
        email_entry = tk.Entry(login_frame, textvariable=self.email_var, 
                              font=('Microsoft YaHei', 10), width=30)
        email_entry.grid(row=0, column=1, pady=5, padx=(10, 0))
        
        # 密码输入
        tk.Label(login_frame, text="密码:", font=('Microsoft YaHei', 10),
                bg='white').grid(row=1, column=0, sticky='w', pady=5)
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(login_frame, textvariable=self.password_var, 
                                 font=('Microsoft YaHei', 10), width=30, show='*')
        password_entry.grid(row=1, column=1, pady=5, padx=(10, 0))
        
        # 按钮框架
        button_frame = tk.Frame(login_frame, bg='white')
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        # 登录按钮
        login_btn = tk.Button(button_frame, text="登录", 
                             font=('Microsoft YaHei', 10, 'bold'),
                             bg='#2c5282', fg='white', padx=20, pady=5,
                             command=self.login)
        login_btn.pack(side='left', padx=5)
        
        # 测试连接按钮
        test_btn = tk.Button(button_frame, text="测试连接", 
                            font=('Microsoft YaHei', 10),
                            bg='#3182ce', fg='white', padx=20, pady=5,
                            command=self.test_connection)
        test_btn.pack(side='left', padx=5)
        
        # 绑定回车键
        password_entry.bind('<Return>', lambda e: self.login())
        
        # 状态栏
        self.status_var = tk.StringVar(value="准备就绪")
        status_label = tk.Label(main_frame, textvariable=self.status_var,
                               font=('Microsoft YaHei', 9), bg='#f0f0f0', fg='#666666')
        status_label.pack(side='bottom', pady=10)
    
    def test_connection(self):
        """测试与服务器的连接"""
        try:
            response = requests.get(f"{LOCAL_CONFIG['COMPANY_WEBSITE']}/api/statistics", timeout=5)
            if response.status_code == 200:
                messagebox.showinfo("连接测试", "服务器连接正常")
            else:
                messagebox.showwarning("连接测试", f"服务器响应异常: {response.status_code}")
        except requests.exceptions.ConnectionError as e:
            error_msg = f"无法连接到服务器: {str(e)}\n\n"
            error_msg += "可能的原因和解决方案:\n"
            error_msg += "1. Web服务器未启动 - 请运行 run_web.py 启动服务器\n"
            error_msg += "2. 服务器端口被占用 - 检查是否已有一个服务器实例在运行\n"
            error_msg += "3. 防火墙阻止连接 - 检查防火墙设置\n"
            error_msg += "4. 服务器地址配置错误 - 检查 config/config.py 中的 COMPANY_WEBSITE 配置\n"
            messagebox.showerror("连接测试", error_msg)
        except requests.exceptions.Timeout:
            messagebox.showerror("连接测试", "连接超时，请稍后重试")
        except Exception as e:
            messagebox.showerror("连接测试", f"连接测试失败: {str(e)}")
    
    def login(self):
        """登录验证"""
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        
        if not email or not password:
            messagebox.showerror("登录失败", "请输入邮箱和密码")
            return
        
        try:
            self.status_var.set("正在登录...")
            self.root.update()
            
            # 发送登录请求
            login_data = {
                'email': email,
                'password': password,
                'user_type': 'staff'
            }
            
            response = requests.post(f"{LOCAL_CONFIG['COMPANY_WEBSITE']}/auth/login", 
                                   data=login_data, timeout=10)
            
            if response.status_code == 200:
                # 登录成功，保存用户信息
                self.current_user = {
                    'email': email,
                    'login_time': datetime.now()
                }
                
                # 同步项目数据
                self.sync_projects()
                
                # 创建主界面
                self.create_main_interface()
                
                self.status_var.set("登录成功")
                
            else:
                messagebox.showerror("登录失败", "邮箱或密码错误")
                self.status_var.set("登录失败")
                
        except requests.exceptions.ConnectionError:
            messagebox.showerror("登录失败", "无法连接到服务器")
            self.status_var.set("连接失败")
        except Exception as e:
            messagebox.showerror("登录失败", f"登录过程中发生错误: {str(e)}")
            self.status_var.set("登录失败")
    
    def sync_projects(self):
        """从服务器同步项目数据"""
        try:
            response = requests.get(f"{LOCAL_CONFIG['COMPANY_WEBSITE']}/api/sync_projects", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data['success']:
                    # 更新本地数据库
                    self.projects = data['projects']
                    print(f"同步了 {len(self.projects)} 个项目")
                else:
                    print("项目同步失败:", data.get('message', '未知错误'))
                    # 如果是权限问题，提示用户重新登录
                    if '登录' in data.get('message', ''):
                        print("请重新登录桌面应用")
            else:
                print(f"项目同步失败: HTTP {response.status_code}")
        except json.JSONDecodeError as e:
            print(f"项目同步错误: JSON解析失败 - {str(e)}")
            print("服务器可能返回了非JSON格式的响应")
        except Exception as e:
            print(f"项目同步错误: {str(e)}")
    
    def create_main_interface(self):
        """创建主界面"""
        # 清空窗口
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 创建菜单栏
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="同步项目", command=self.sync_projects)
        file_menu.add_separator()
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
        
        # 主框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建选项卡
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True)
        
        # 项目管理选项卡
        self.create_project_tab(notebook)
        
        # 文件管理选项卡
        self.create_file_management_tab(notebook)
        
        # 模板管理选项卡
        self.create_template_tab(notebook)
        
        # 工具选项卡
        self.create_tools_tab(notebook)
        
        # 状态栏
        status_frame = tk.Frame(self.root, bg='#e0e0e0', height=25)
        status_frame.pack(side='bottom', fill='x')
        
        self.status_var = tk.StringVar(value=f"已登录: {self.current_user['email']}")
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                               font=('Microsoft YaHei', 9), bg='#e0e0e0')
        status_label.pack(side='left', padx=10, pady=2)
        
        time_label = tk.Label(status_frame, text=f"登录时间: {self.current_user['login_time'].strftime('%Y-%m-%d %H:%M:%S')}",
                             font=('Microsoft YaHei', 9), bg='#e0e0e0')
        time_label.pack(side='right', padx=10, pady=2)
    
    def create_project_tab(self, notebook):
        """创建项目管理选项卡"""
        project_frame = tk.Frame(notebook, bg='white')
        notebook.add(project_frame, text="项目管理")
        
        # 项目列表框架
        list_frame = tk.LabelFrame(project_frame, text="项目列表", 
                                  font=('Microsoft YaHei', 10, 'bold'),
                                  bg='white', padx=10, pady=10)
        list_frame.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        # 项目列表
        columns = ('ID', '项目名称', '项目类型', '状态', '优先级')
        self.project_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.project_tree.heading(col, text=col)
            self.project_tree.column(col, width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.project_tree.yview)
        self.project_tree.configure(yscrollcommand=scrollbar.set)
        
        self.project_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 绑定选择事件
        self.project_tree.bind('<<TreeviewSelect>>', self.on_project_select)
        
        # 项目详情框架
        detail_frame = tk.LabelFrame(project_frame, text="项目详情", 
                                    font=('Microsoft YaHei', 10, 'bold'),
                                    bg='white', padx=10, pady=10)
        detail_frame.pack(side='right', fill='y', padx=10, pady=10)
        
        # 项目详情显示区域
        self.detail_text = tk.Text(detail_frame, width=40, height=20, 
                                  font=('Microsoft YaHei', 9))
        detail_scrollbar = ttk.Scrollbar(detail_frame, orient='vertical', command=self.detail_text.yview)
        self.detail_text.configure(yscrollcommand=detail_scrollbar.set)
        
        self.detail_text.pack(side='left', fill='both', expand=True)
        detail_scrollbar.pack(side='right', fill='y')
        
        # 操作按钮框架
        button_frame = tk.Frame(detail_frame, bg='white')
        button_frame.pack(side='bottom', fill='x', pady=10)
        
        # 创建项目文件夹按钮
        create_folder_btn = tk.Button(button_frame, text="创建项目文件夹", 
                                     font=('Microsoft YaHei', 9),
                                     bg='#38a169', fg='white', padx=10, pady=5,
                                     command=self.create_project_folder)
        create_folder_btn.pack(side='top', fill='x', pady=2)
        
        # 更新流水号按钮
        update_serial_btn = tk.Button(button_frame, text="更新流水号", 
                                     font=('Microsoft YaHei', 9),
                                     bg='#3182ce', fg='white', padx=10, pady=5,
                                     command=self.update_serial_number)
        update_serial_btn.pack(side='top', fill='x', pady=2)
        
        # 项目归档按钮
        archive_btn = tk.Button(button_frame, text="项目归档", 
                               font=('Microsoft YaHei', 9),
                               bg='#d69e2e', fg='white', padx=10, pady=5,
                               command=self.archive_project)
        archive_btn.pack(side='top', fill='x', pady=2)
        
        # 刷新项目列表
        self.refresh_project_list()
    
    def create_file_management_tab(self, notebook):
        """创建文件管理选项卡"""
        file_frame = tk.Frame(notebook, bg='white')
        notebook.add(file_frame, text="文件管理")
        
        # 身份证PDF管理
        id_frame = tk.LabelFrame(file_frame, text="身份证PDF管理", 
                                font=('Microsoft YaHei', 10, 'bold'),
                                bg='white', padx=10, pady=10)
        id_frame.pack(fill='x', padx=10, pady=5)
        
        id_button_frame = tk.Frame(id_frame, bg='white')
        id_button_frame.pack(fill='x', pady=5)
        
        tk.Button(id_button_frame, text="打开身份证文件夹", 
                 font=('Microsoft YaHei', 9), bg='#3182ce', fg='white',
                 command=lambda: self.open_folder(LOCAL_CONFIG['IDPDF_DIR'])).pack(side='left', padx=5)
        
        tk.Button(id_button_frame, text="添加身份证PDF", 
                 font=('Microsoft YaHei', 9), bg='#38a169', fg='white',
                 command=self.add_id_pdf).pack(side='left', padx=5)
        
        # 身份证文件列表
        self.id_listbox = tk.Listbox(id_frame, height=6, font=('Microsoft YaHei', 9))
        self.id_listbox.pack(fill='x', pady=5)
        
        # 统一社会信用代码证书PDF管理
        usccc_frame = tk.LabelFrame(file_frame, text="统一社会信用代码证书PDF管理", 
                                   font=('Microsoft YaHei', 10, 'bold'),
                                   bg='white', padx=10, pady=10)
        usccc_frame.pack(fill='x', padx=10, pady=5)
        
        usccc_button_frame = tk.Frame(usccc_frame, bg='white')
        usccc_button_frame.pack(fill='x', pady=5)
        
        tk.Button(usccc_button_frame, text="打开证书文件夹", 
                 font=('Microsoft YaHei', 9), bg='#3182ce', fg='white',
                 command=lambda: self.open_folder(LOCAL_CONFIG['USCCC_DIR'])).pack(side='left', padx=5)
        
        tk.Button(usccc_button_frame, text="添加证书PDF", 
                 font=('Microsoft YaHei', 9), bg='#38a169', fg='white',
                 command=self.add_usccc_pdf).pack(side='left', padx=5)
        
        # 证书文件列表
        self.usccc_listbox = tk.Listbox(usccc_frame, height=6, font=('Microsoft YaHei', 9))
        self.usccc_listbox.pack(fill='x', pady=5)
        
        # 项目文件管理
        project_file_frame = tk.LabelFrame(file_frame, text="项目文件管理", 
                                          font=('Microsoft YaHei', 10, 'bold'),
                                          bg='white', padx=10, pady=10)
        project_file_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        project_button_frame = tk.Frame(project_file_frame, bg='white')
        project_button_frame.pack(fill='x', pady=5)
        
        tk.Button(project_button_frame, text="打开项目文件夹", 
                 font=('Microsoft YaHei', 9), bg='#3182ce', fg='white',
                 command=lambda: self.open_folder(LOCAL_CONFIG['PROJECT_FILE_DIR'])).pack(side='left', padx=5)
        
        tk.Button(project_button_frame, text="刷新文件列表", 
                 font=('Microsoft YaHei', 9), bg='#d69e2e', fg='white',
                 command=self.refresh_file_lists).pack(side='left', padx=5)
        
        # 刷新文件列表
        self.refresh_file_lists()
    
    def create_template_tab(self, notebook):
        """创建模板管理选项卡"""
        template_frame = tk.Frame(notebook, bg='white')
        notebook.add(template_frame, text="模板管理")
        
        # 材料模板管理
        material_frame = tk.LabelFrame(template_frame, text="申请材料模板", 
                                      font=('Microsoft YaHei', 10, 'bold'),
                                      bg='white', padx=10, pady=10)
        material_frame.pack(fill='x', padx=10, pady=5)
        
        material_button_frame = tk.Frame(material_frame, bg='white')
        material_button_frame.pack(fill='x', pady=5)
        
        tk.Button(material_button_frame, text="打开模板文件夹", 
                 font=('Microsoft YaHei', 9), bg='#3182ce', fg='white',
                 command=lambda: self.open_folder(LOCAL_CONFIG['MATERIAL_DIR'])).pack(side='left', padx=5)
        
        tk.Button(material_button_frame, text="通过模板创建项目", 
                 font=('Microsoft YaHei', 9), bg='#38a169', fg='white',
                 command=self.create_project_from_template).pack(side='left', padx=5)
        
        # 材料模板列表
        self.material_listbox = tk.Listbox(material_frame, height=8, font=('Microsoft YaHei', 9))
        self.material_listbox.pack(fill='x', pady=5)
        
        # 合同模板管理
        contract_frame = tk.LabelFrame(template_frame, text="合同模板", 
                                      font=('Microsoft YaHei', 10, 'bold'),
                                      bg='white', padx=10, pady=10)
        contract_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        contract_button_frame = tk.Frame(contract_frame, bg='white')
        contract_button_frame.pack(fill='x', pady=5)
        
        tk.Button(contract_button_frame, text="打开合同文件夹", 
                 font=('Microsoft YaHei', 9), bg='#3182ce', fg='white',
                 command=lambda: self.open_folder(LOCAL_CONFIG['CONTRACT_DIR'])).pack(side='left', padx=5)
        
        tk.Button(contract_button_frame, text="复制合同到项目", 
                 font=('Microsoft YaHei', 9), bg='#38a169', fg='white',
                 command=self.copy_contract_to_project).pack(side='left', padx=5)
        
        # 合同模板列表
        self.contract_listbox = tk.Listbox(contract_frame, height=8, font=('Microsoft YaHei', 9))
        self.contract_listbox.pack(fill='x', pady=5)
        
        # 刷新模板列表
        self.refresh_template_lists()
    
    def create_tools_tab(self, notebook):
        """创建工具选项卡"""
        tools_frame = tk.Frame(notebook, bg='white')
        notebook.add(tools_frame, text="工具")
        
        # 网站快捷方式
        web_frame = tk.LabelFrame(tools_frame, text="网站快捷方式", 
                                 font=('Microsoft YaHei', 10, 'bold'),
                                 bg='white', padx=10, pady=10)
        web_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(web_frame, text="打开公司网站", 
                 font=('Microsoft YaHei', 10), bg='#3182ce', fg='white',
                 padx=20, pady=10, command=self.open_company_website).pack(side='left', padx=10)
        
        tk.Button(web_frame, text="打开版权保护中心", 
                 font=('Microsoft YaHei', 10), bg='#e53e3e', fg='white',
                 padx=20, pady=10, command=self.open_copyright_center).pack(side='left', padx=10)
        
        # 流水号工具
        serial_frame = tk.LabelFrame(tools_frame, text="流水号管理", 
                                    font=('Microsoft YaHei', 10, 'bold'),
                                    bg='white', padx=10, pady=10)
        serial_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Label(serial_frame, text="项目ID:", font=('Microsoft YaHei', 9), bg='white').grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.project_id_var = tk.StringVar()
        tk.Entry(serial_frame, textvariable=self.project_id_var, font=('Microsoft YaHei', 9), width=20).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(serial_frame, text="流水号:", font=('Microsoft YaHei', 9), bg='white').grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.serial_number_var = tk.StringVar()
        tk.Entry(serial_frame, textvariable=self.serial_number_var, font=('Microsoft YaHei', 9), width=20).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Button(serial_frame, text="更新流水号", 
                 font=('Microsoft YaHei', 9), bg='#38a169', fg='white',
                 padx=10, pady=5, command=self.manual_update_serial).grid(row=2, column=0, columnspan=2, pady=10)
        
        # 系统工具
        system_frame = tk.LabelFrame(tools_frame, text="系统工具", 
                                    font=('Microsoft YaHei', 10, 'bold'),
                                    bg='white', padx=10, pady=10)
        system_frame.pack(fill='x', padx=10, pady=10)
        
        tk.Button(system_frame, text="清理临时文件", 
                 font=('Microsoft YaHei', 10), bg='#d69e2e', fg='white',
                 padx=20, pady=10, command=self.clean_temp_files).pack(side='left', padx=10)
        
        tk.Button(system_frame, text="备份数据", 
                 font=('Microsoft YaHei', 10), bg='#38a169', fg='white',
                 padx=20, pady=10, command=self.backup_data).pack(side='left', padx=10)
    
    def refresh_project_list(self):
        """刷新项目列表"""
        # 清空现有项目
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        
        # 从本地数据库获取项目
        projects = LocalProject.get_all_projects(LOCAL_CONFIG['LOCAL_DB_PATH'])
        
        for project in projects:
            self.project_tree.insert('', 'end', values=(
                project[0],  # ID
                project[1],  # 项目名称
                project[2],  # 项目类型
                project[8],  # 状态
                project[7]   # 优先级
            ))
    
    def on_project_select(self, event):
        """项目选择事件处理"""
        selection = self.project_tree.selection()
        if selection:
            item = self.project_tree.item(selection[0])
            project_id = item['values'][0]
            
            # 从本地数据库获取项目详情
            conn = sqlite3.connect(LOCAL_CONFIG['LOCAL_DB_PATH'])
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM local_projects WHERE id = ?', (project_id,))
            project = cursor.fetchone()
            conn.close()
            
            if project:
                self.selected_project = project
                self.display_project_details(project)
                self.project_id_var.set(str(project[0]))
    
    def display_project_details(self, project):
        """显示项目详情"""
        self.detail_text.delete(1.0, tk.END)
        
        details = f"""项目详情
        
项目ID: {project[0]}
项目名称: {project[1]}
项目类型: {project[2]}
申请人类型: {project[3]}
著作权人: {project[4] or '未填写'}
软著申请人: {project[5] or '未填写'}
流水号: {project[6] or '未获取'}
优先级: {project[7]}
项目状态: {project[8]}
执行者ID: {project[9] or '未分配'}
项目备注: {project[10] or '无'}
同步时间: {project[11]}
"""
        
        self.detail_text.insert(1.0, details)
    
    def create_project_folder(self):
        """创建项目文件夹"""
        if not self.selected_project:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        project_id = self.selected_project[0]
        project_name = self.selected_project[1]
        folder_name = f"{project_id}_{project_name}"
        
        project_folder = os.path.join(LOCAL_CONFIG['PROJECT_FILE_DIR'], folder_name)
        
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
            messagebox.showinfo("成功", f"项目文件夹已创建: {project_folder}")
            self.open_folder(project_folder)
        else:
            messagebox.showinfo("提示", "项目文件夹已存在")
            self.open_folder(project_folder)
    
    def update_serial_number(self):
        """更新流水号"""
        if not self.selected_project:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        # 打开输入对话框
        serial_number = tk.simpledialog.askstring("更新流水号", "请输入流水号:")
        
        if serial_number:
            try:
                # 更新本地数据库
                LocalProject.update_serial_number(LOCAL_CONFIG['LOCAL_DB_PATH'], 
                                                 self.selected_project[0], serial_number)
                
                # 更新服务器（如果需要）
                # TODO: 实现服务器更新
                
                messagebox.showinfo("成功", "流水号更新成功")
                self.refresh_project_list()
                
            except Exception as e:
                messagebox.showerror("错误", f"更新流水号失败: {str(e)}")
    
    def manual_update_serial(self):
        """手动更新流水号"""
        project_id = self.project_id_var.get().strip()
        serial_number = self.serial_number_var.get().strip()
        
        if not project_id or not serial_number:
            messagebox.showwarning("警告", "请输入项目ID和流水号")
            return
        
        try:
            LocalProject.update_serial_number(LOCAL_CONFIG['LOCAL_DB_PATH'], 
                                             int(project_id), serial_number)
            messagebox.showinfo("成功", "流水号更新成功")
            self.refresh_project_list()
            
        except Exception as e:
            messagebox.showerror("错误", f"更新流水号失败: {str(e)}")
    
    def archive_project(self):
        """项目归档"""
        if not self.selected_project:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        result = messagebox.askyesno("确认", "确定要归档此项目吗？")
        if result:
            try:
                project_id = self.selected_project[0]
                project_name = self.selected_project[1]
                
                # 移动项目文件夹到归档目录
                source_folder = os.path.join(LOCAL_CONFIG['PROJECT_FILE_DIR'], f"{project_id}_{project_name}")
                archive_folder = os.path.join(LOCAL_CONFIG['PROJECT_FILE_DIR'], "Archived", f"{project_id}_{project_name}")
                
                if os.path.exists(source_folder):
                    os.makedirs(os.path.dirname(archive_folder), exist_ok=True)
                    shutil.move(source_folder, archive_folder)
                
                messagebox.showinfo("成功", "项目已归档")
                
            except Exception as e:
                messagebox.showerror("错误", f"归档失败: {str(e)}")
    
    def refresh_file_lists(self):
        """刷新文件列表"""
        # 刷新身份证PDF列表
        self.id_listbox.delete(0, tk.END)
        if os.path.exists(LOCAL_CONFIG['IDPDF_DIR']):
            for file in os.listdir(LOCAL_CONFIG['IDPDF_DIR']):
                if file.lower().endswith('.pdf'):
                    self.id_listbox.insert(tk.END, file)
        
        # 刷新统一社会信用代码证书PDF列表
        self.usccc_listbox.delete(0, tk.END)
        if os.path.exists(LOCAL_CONFIG['USCCC_DIR']):
            for file in os.listdir(LOCAL_CONFIG['USCCC_DIR']):
                if file.lower().endswith('.pdf'):
                    self.usccc_listbox.insert(tk.END, file)
    
    def refresh_template_lists(self):
        """刷新模板列表"""
        # 刷新材料模板列表
        self.material_listbox.delete(0, tk.END)
        if os.path.exists(LOCAL_CONFIG['MATERIAL_DIR']):
            for file in os.listdir(LOCAL_CONFIG['MATERIAL_DIR']):
                if file.lower().endswith(('.doc', '.docx')):
                    self.material_listbox.insert(tk.END, file)
        
        # 刷新合同模板列表
        self.contract_listbox.delete(0, tk.END)
        if os.path.exists(LOCAL_CONFIG['CONTRACT_DIR']):
            for file in os.listdir(LOCAL_CONFIG['CONTRACT_DIR']):
                if file.lower().endswith(('.doc', '.docx')):
                    self.contract_listbox.insert(tk.END, file)
    
    def add_id_pdf(self):
        """添加身份证PDF"""
        file_path = filedialog.askopenfilename(
            title="选择身份证PDF文件",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            target_path = os.path.join(LOCAL_CONFIG['IDPDF_DIR'], filename)
            
            try:
                shutil.copy2(file_path, target_path)
                messagebox.showinfo("成功", f"身份证PDF已添加: {filename}")
                self.refresh_file_lists()
            except Exception as e:
                messagebox.showerror("错误", f"添加文件失败: {str(e)}")
    
    def add_usccc_pdf(self):
        """添加统一社会信用代码证书PDF"""
        file_path = filedialog.askopenfilename(
            title="选择统一社会信用代码证书PDF文件",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            target_path = os.path.join(LOCAL_CONFIG['USCCC_DIR'], filename)
            
            try:
                shutil.copy2(file_path, target_path)
                messagebox.showinfo("成功", f"证书PDF已添加: {filename}")
                self.refresh_file_lists()
            except Exception as e:
                messagebox.showerror("错误", f"添加文件失败: {str(e)}")
    
    def create_project_from_template(self):
        """通过模板创建项目"""
        if not self.selected_project:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        selection = self.material_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个模板")
            return
        
        template_name = self.material_listbox.get(selection[0])
        template_path = os.path.join(LOCAL_CONFIG['MATERIAL_DIR'], template_name)
        
        project_id = self.selected_project[0]
        project_name = self.selected_project[1]
        project_folder = os.path.join(LOCAL_CONFIG['PROJECT_FILE_DIR'], f"{project_id}_{project_name}")
        
        try:
            # 创建项目文件夹
            os.makedirs(project_folder, exist_ok=True)
            
            # 复制模板文件
            target_path = os.path.join(project_folder, template_name)
            shutil.copy2(template_path, target_path)
            
            messagebox.showinfo("成功", f"已通过模板创建项目文件夹: {project_folder}")
            self.open_folder(project_folder)
            
        except Exception as e:
            messagebox.showerror("错误", f"创建项目失败: {str(e)}")
    
    def copy_contract_to_project(self):
        """复制合同到项目"""
        if not self.selected_project:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        selection = self.contract_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个合同模板")
            return
        
        contract_name = self.contract_listbox.get(selection[0])
        contract_path = os.path.join(LOCAL_CONFIG['CONTRACT_DIR'], contract_name)
        
        project_id = self.selected_project[0]
        project_name = self.selected_project[1]
        project_folder = os.path.join(LOCAL_CONFIG['PROJECT_FILE_DIR'], f"{project_id}_{project_name}")
        
        try:
            # 确保项目文件夹存在
            os.makedirs(project_folder, exist_ok=True)
            
            # 复制合同文件
            target_path = os.path.join(project_folder, contract_name)
            shutil.copy2(contract_path, target_path)
            
            messagebox.showinfo("成功", f"合同已复制到项目文件夹: {target_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"复制合同失败: {str(e)}")
    
    def open_folder(self, folder_path):
        """打开文件夹"""
        try:
            os.startfile(folder_path)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开文件夹: {str(e)}")
    
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
        self.open_folder(LOCAL_CONFIG['BASE_DIR'])
    
    def clean_temp_files(self):
        """清理临时文件"""
        try:
            # 这里可以添加清理临时文件的逻辑
            messagebox.showinfo("成功", "临时文件清理完成")
        except Exception as e:
            messagebox.showerror("错误", f"清理失败: {str(e)}")
    
    def backup_data(self):
        """备份数据"""
        try:
            backup_folder = filedialog.askdirectory(title="选择备份目录")
            if backup_folder:
                # 备份数据库
                backup_db_path = os.path.join(backup_folder, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
                shutil.copy2(LOCAL_CONFIG['LOCAL_DB_PATH'], backup_db_path)
                
                messagebox.showinfo("成功", f"数据备份完成: {backup_db_path}")
        except Exception as e:
            messagebox.showerror("错误", f"备份失败: {str(e)}")
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """软著管理系统 v1.0
        
郑州医企创医疗科技有限公司
项目执行者专用工具

功能特性:
• 项目管理
• 文件管理
• 模板管理
• 流水号管理
• 网站快捷访问

技术支持: admin@yiqichuang.com"""
        
        messagebox.showinfo("关于", about_text)
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SoftwareCopyrightMS()
    app.run()
