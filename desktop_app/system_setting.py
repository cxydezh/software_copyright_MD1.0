#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统设置模块
根据需求分析文档设计：路径配置管理
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import shutil
from config.config import LOCAL_CONFIG


class SystemSettingModule:
    """系统设置模块"""
    
    def __init__(self, parent, db, default_path):
        self.parent = parent
        self.db = db
        self.default_path = default_path
        
        # 创建界面
        self.create_interface()
        
        # 加载当前设置
        self.load_settings()
    
    def create_interface(self):
        """创建系统设置界面"""
        # 创建主框架
        self.main_frame = tk.Frame(self.parent, bg='white')
        self.parent.add(self.main_frame, text="系统设置")
        
        # 创建滚动框架
        self.create_scrollable_form()
    
    def create_scrollable_form(self):
        """创建可滚动的表单"""
        # 创建Canvas和滚动条
        canvas = tk.Canvas(self.main_frame, bg='white')
        scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 布局Canvas和滚动条
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 创建设置表单（使用scrollable_frame作为父容器）
        self.create_settings_form(scrollable_frame)
    
    def create_settings_form(self, parent=None):
        """创建设置表单"""
        if parent is None:
            parent = self.main_frame
            
        # 标题
        title_frame = tk.Frame(parent, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="系统设置", 
                font=('Microsoft YaHei', 16, 'bold'), bg='white', fg='#2c5282').pack()
        
        # 设置表单框架
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill='x', padx=20, pady=20)
        
        # 路径设置
        self.create_path_settings(form_frame)
        
        # 分隔线
        separator = ttk.Separator(form_frame, orient='horizontal')
        separator.pack(fill='x', pady=20)
        
        # 数据库设置
        self.create_database_settings(form_frame)
        
        # 分隔线
        separator2 = ttk.Separator(form_frame, orient='horizontal')
        separator2.pack(fill='x', pady=20)
        
        # 其他设置
        self.create_other_settings(form_frame)
        
        # 分隔线
        separator3 = ttk.Separator(form_frame, orient='horizontal')
        separator3.pack(fill='x', pady=20)
        
        # 版权中心账号设置
        self.create_copyright_account_settings(form_frame)
        
        # 按钮框架
        self.create_button_frame(parent)
    
    def create_path_settings(self, parent):
        """创建路径设置"""
        # 路径设置标题
        path_title_frame = tk.Frame(parent, bg='white')
        path_title_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(path_title_frame, text="路径设置", 
                font=('Microsoft YaHei', 12, 'bold'), bg='white', fg='#2c5282').pack(anchor='w')
        
        # 路径设置表单
        path_frame = tk.Frame(parent, bg='white')
        path_frame.pack(fill='x', pady=(0, 10))
        
        # 路径配置
        self.path_vars = {}
        path_configs = [
            ('项目模板文件夹', 'template_path', '选择项目模板文件夹'),
            ('身份证复印件文件夹', 'id_card_path', '选择身份证复印件文件夹'),
            ('统一社会信用代码证书文件夹', 'usccc_path', '选择统一社会信用代码证书文件夹'),
            ('合同文件夹', 'contract_path', '选择合同文件夹'),
            ('项目文件夹', 'project_path', '选择项目文件夹')
        ]
        
        for i, (label, key, dialog_title) in enumerate(path_configs):
            # 标签
            tk.Label(path_frame, text=f"{label}:", 
                    font=('Microsoft YaHei', 10), bg='white').grid(
                row=i, column=0, sticky='w', padx=(0, 10), pady=8)
            
            # 路径输入框
            var = tk.StringVar()
            entry = tk.Entry(path_frame, textvariable=var, 
                            font=('Microsoft YaHei', 9), width=50)
            entry.grid(row=i, column=1, sticky='ew', padx=(0, 10), pady=8)
            self.path_vars[key] = var
            
            # 浏览按钮
            tk.Button(path_frame, text="浏览", 
                     font=('Microsoft YaHei', 9), bg='#3182ce', fg='white',
                     command=lambda k=key, t=dialog_title: self.browse_folder(k, t)).grid(
                row=i, column=2, pady=8)
        
        # 配置列权重
        path_frame.columnconfigure(1, weight=1)
    
    def create_database_settings(self, parent):
        """创建数据库设置"""
        # 数据库设置标题
        db_title_frame = tk.Frame(parent, bg='white')
        db_title_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(db_title_frame, text="数据库设置", 
                font=('Microsoft YaHei', 12, 'bold'), bg='white', fg='#2c5282').pack(anchor='w')
        
        # 数据库设置表单
        db_frame = tk.Frame(parent, bg='white')
        db_frame.pack(fill='x', pady=(0, 10))
        
        # 本地数据库路径
        tk.Label(db_frame, text="本地数据库路径:", 
                font=('Microsoft YaHei', 10), bg='white').grid(
            row=0, column=0, sticky='w', padx=(0, 10), pady=8)
        
        self.db_path_var = tk.StringVar()
        db_entry = tk.Entry(db_frame, textvariable=self.db_path_var, 
                           font=('Microsoft YaHei', 9), width=50)
        db_entry.grid(row=0, column=1, sticky='ew', padx=(0, 10), pady=8)
        
        tk.Button(db_frame, text="浏览", 
                 font=('Microsoft YaHei', 9), bg='#3182ce', fg='white',
                 command=self.browse_database_file).grid(row=0, column=2, pady=8)
        
        # 配置列权重
        db_frame.columnconfigure(1, weight=1)
    
    def create_other_settings(self, parent):
        """创建其他设置"""
        # 其他设置标题
        other_title_frame = tk.Frame(parent, bg='white')
        other_title_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(other_title_frame, text="其他设置", 
                font=('Microsoft YaHei', 12, 'bold'), bg='white', fg='#2c5282').pack(anchor='w')
        
        # 其他设置表单
        other_frame = tk.Frame(parent, bg='white')
        other_frame.pack(fill='x', pady=(0, 10))
        
        # Web API 地址（HTTP）
        tk.Label(other_frame, text="Web API 地址:", 
                font=('Microsoft YaHei', 10), bg='white').grid(
            row=0, column=0, sticky='w', padx=(0, 10), pady=8)
        self.server_host_var = tk.StringVar()
        server_host_entry = tk.Entry(other_frame, textvariable=self.server_host_var, 
                                font=('Microsoft YaHei', 9), width=50)
        server_host_entry.grid(row=0, column=1, sticky='ew', padx=(0, 10), pady=8)

        # Web API 端口
        tk.Label(other_frame, text="Web API 端口:", 
                font=('Microsoft YaHei', 10), bg='white').grid(
            row=1, column=0, sticky='w', padx=(0, 10), pady=8)
        self.server_port_var = tk.StringVar()
        server_port_entry = tk.Entry(other_frame, textvariable=self.server_port_var, 
                                font=('Microsoft YaHei', 9), width=18)
        server_port_entry.grid(row=1, column=1, sticky='w', padx=(0, 10), pady=8)

        # 公司网站
        tk.Label(other_frame, text="公司网站:", 
                font=('Microsoft YaHei', 10), bg='white').grid(
            row=2, column=0, sticky='w', padx=(0, 10), pady=8)
        
        self.company_website_var = tk.StringVar()
        website_entry = tk.Entry(other_frame, textvariable=self.company_website_var, 
                                font=('Microsoft YaHei', 9), width=50)
        website_entry.grid(row=2, column=1, sticky='ew', padx=(0, 10), pady=8)
        
        # 版权中心网站
        tk.Label(other_frame, text="版权中心网站:", 
                font=('Microsoft YaHei', 10), bg='white').grid(
            row=3, column=0, sticky='w', padx=(0, 10), pady=8)
        
        self.copyright_center_var = tk.StringVar()
        copyright_entry = tk.Entry(other_frame, textvariable=self.copyright_center_var, 
                                  font=('Microsoft YaHei', 9), width=50)
        copyright_entry.grid(row=3, column=1, sticky='ew', padx=(0, 10), pady=8)
        
        # 配置列权重
        other_frame.columnconfigure(1, weight=1)
        
        # 浏览器配置管理（使用pack布局，避免与grid冲突）
        browser_frame = tk.Frame(parent, bg='white')
        browser_frame.pack(fill='x', pady=(20, 0))
        
        tk.Label(browser_frame, text="浏览器配置管理:", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white', fg='#2c5282').pack(anchor='w')
        
        browser_info_frame = tk.Frame(browser_frame, bg='white')
        browser_info_frame.pack(fill='x', pady=(5, 10))
        
        # 浏览器数据目录信息
        browser_data_info = tk.Label(browser_info_frame, 
                                   text="Playwright浏览器数据目录包含登录信息、密码、Cookie等敏感数据。\n"
                                        "如果遇到登录问题或需要清除所有浏览器数据，请使用下面的重置功能。", 
                                   font=('Microsoft YaHei', 9), bg='white', fg='#666666', 
                                   justify='left')
        browser_data_info.pack(anchor='w', pady=(0, 10))
        
        # 浏览器配置按钮框架
        browser_buttons_frame = tk.Frame(browser_info_frame, bg='white')
        browser_buttons_frame.pack(fill='x')
        
        # 查看浏览器数据目录按钮
        tk.Button(browser_buttons_frame, text="查看浏览器数据目录", 
                 font=('Microsoft YaHei', 9), bg='#3182ce', fg='white',
                 command=self.view_browser_data_dir).pack(side='left', padx=(0, 10))
        
        # 重置浏览器配置按钮
        tk.Button(browser_buttons_frame, text="重置浏览器配置", 
                 font=('Microsoft YaHei', 9), bg='#e53e3e', fg='white',
                 command=self.reset_browser_config).pack(side='left', padx=(0, 10))
    
    def create_copyright_account_settings(self, parent):
        """创建版权中心账号设置"""
        # 版权中心账号设置标题
        copyright_title_frame = tk.Frame(parent, bg='white')
        copyright_title_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(copyright_title_frame, text="版权中心账号设置", 
                font=('Microsoft YaHei', 12, 'bold'), bg='white', fg='#2c5282').pack(anchor='w')
        
        # 版权中心账号设置表单
        copyright_frame = tk.Frame(parent, bg='white')
        copyright_frame.pack(fill='x', pady=(0, 10))
        
        # 说明文字
        info_label = tk.Label(copyright_frame, 
                             text="保存版权中心网站的登录账号和密码，系统将自动填充登录表单。\n"
                                  "密码将使用加密方式安全存储。", 
                             font=('Microsoft YaHei', 9), bg='white', fg='#666666', 
                             justify='left')
        info_label.pack(anchor='w', pady=(0, 15))
        
        # 账号输入
        account_frame = tk.Frame(copyright_frame, bg='white')
        account_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(account_frame, text="账号:", 
                font=('Microsoft YaHei', 10), bg='white').grid(
            row=0, column=0, sticky='w', padx=(0, 10), pady=8)
        
        self.copyright_username_var = tk.StringVar()
        username_entry = tk.Entry(account_frame, textvariable=self.copyright_username_var, 
                                font=('Microsoft YaHei', 9), width=30)
        username_entry.grid(row=0, column=1, sticky='w', padx=(0, 10), pady=8)
        
        # 密码输入
        tk.Label(account_frame, text="密码:", 
                font=('Microsoft YaHei', 10), bg='white').grid(
            row=1, column=0, sticky='w', padx=(0, 10), pady=8)
        
        self.copyright_password_var = tk.StringVar()
        password_entry = tk.Entry(account_frame, textvariable=self.copyright_password_var, 
                                font=('Microsoft YaHei', 9), width=30, show='*')
        password_entry.grid(row=1, column=1, sticky='w', padx=(0, 10), pady=8)
        
        # 状态显示
        self.copyright_status_var = tk.StringVar()
        self.copyright_status_label = tk.Label(account_frame, textvariable=self.copyright_status_var,
                                             font=('Microsoft YaHei', 9), bg='white', fg='#666666')
        self.copyright_status_label.grid(row=2, column=0, columnspan=2, sticky='w', pady=(5, 0))
        
        # 按钮框架
        copyright_buttons_frame = tk.Frame(copyright_frame, bg='white')
        copyright_buttons_frame.pack(fill='x', pady=(10, 0))
        
        # 保存账号按钮
        tk.Button(copyright_buttons_frame, text="保存账号", 
                 font=('Microsoft YaHei', 9), bg='#3182ce', fg='white',
                 command=self.save_copyright_credentials).pack(side='left', padx=(0, 10))
        
        # 删除账号按钮
        tk.Button(copyright_buttons_frame, text="删除账号", 
                 font=('Microsoft YaHei', 9), bg='#e53e3e', fg='white',
                 command=self.delete_copyright_credentials).pack(side='left', padx=(0, 10))
        
        # 测试账号按钮
        tk.Button(copyright_buttons_frame, text="测试账号", 
                 font=('Microsoft YaHei', 9), bg='#38a169', fg='white',
                 command=self.test_copyright_credentials).pack(side='left', padx=(0, 10))
        
        # 加载已保存的账号信息
        self.load_copyright_credentials()
    
    def create_button_frame(self, parent=None):
        """创建按钮框架"""
        if parent is None:
            parent = self.main_frame
        button_frame = tk.Frame(parent, bg='white')
        button_frame.pack(fill='x', padx=20, pady=20)
        
        # 按钮
        tk.Button(button_frame, text="保存设置", 
                 font=('Microsoft YaHei', 12), bg='#3182ce', fg='white',
                 command=self.save_settings).pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="重置设置", 
                 font=('Microsoft YaHei', 12), bg='#d69e2e', fg='white',
                 command=self.reset_settings).pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="恢复默认", 
                 font=('Microsoft YaHei', 12), bg='#38a169', fg='white',
                 command=self.restore_defaults).pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="测试连接", 
                 font=('Microsoft YaHei', 12), bg='#e53e3e', fg='white',
                 command=self.test_connection).pack(side='left')
    
    def load_settings(self):
        """加载当前设置"""
        try:
            # 加载路径设置
            for key, var in self.path_vars.items():
                path = self.default_path.get_path(key)
                var.set(path or '')
            
            # 加载数据库路径
            db_path = self.default_path.get_path('db_path')
            self.db_path_var.set(db_path or LOCAL_CONFIG['LOCAL_DB_PATH'])
            
            # 加载其他设置
            server_host = self.default_path.get_path('web_api_host') or LOCAL_CONFIG.get('WEB_API_HOST', 'http://192.168.31.56')
            server_port = self.default_path.get_path('web_api_port') or str(LOCAL_CONFIG.get('WEB_API_PORT', 5000))
            self.server_host_var.set(server_host)
            self.server_port_var.set(server_port)

            self.company_website_var.set(LOCAL_CONFIG.get('COMPANY_WEBSITE', ''))
            self.copyright_center_var.set(LOCAL_CONFIG.get('COPYRIGHT_CENTER_URL', ''))
            
        except Exception as e:
            messagebox.showerror("错误", f"加载设置失败: {str(e)}")
    
    def browse_folder(self, path_key, dialog_title):
        """浏览文件夹"""
        current_path = self.path_vars[path_key].get()
        if not current_path or not os.path.exists(current_path):
            current_path = os.path.expanduser("~")
        
        folder_path = filedialog.askdirectory(
            title=dialog_title,
            initialdir=current_path
        )
        
        if folder_path:
            self.path_vars[path_key].set(folder_path)
    
    def browse_database_file(self):
        """浏览数据库文件"""
        current_path = self.db_path_var.get()
        if not current_path:
            current_path = os.path.dirname(LOCAL_CONFIG['LOCAL_DB_PATH'])
        
        file_path = filedialog.asksaveasfilename(
            title="选择数据库文件",
            defaultextension=".db",
            filetypes=[("SQLite files", "*.db"), ("All files", "*.*")],
            initialdir=os.path.dirname(current_path)
        )
        
        if file_path:
            self.db_path_var.set(file_path)
    
    def save_settings(self):
        """保存设置"""
        try:
            # 保存路径设置
            for key, var in self.path_vars.items():
                path = var.get().strip()
                if path:
                    # 验证路径是否存在
                    if not os.path.exists(path):
                        if messagebox.askyesno("确认", f"路径 '{path}' 不存在，是否创建？"):
                            os.makedirs(path, exist_ok=True)
                        else:
                            continue
                    
                    self.default_path.set_path(key, path)
            
            # 保存数据库路径
            db_path = self.db_path_var.get().strip()
            if db_path:
                self.default_path.set_path('db_path', db_path)
            
            # 保存其他设置（服务器、网站等）
            company_website = self.company_website_var.get().strip()
            copyright_center = self.copyright_center_var.get().strip()
            server_host = self.server_host_var.get().strip() or LOCAL_CONFIG.get('WEB_API_HOST', 'http://192.168.31.56')
            server_port = self.server_port_var.get().strip() or str(LOCAL_CONFIG.get('WEB_API_PORT', 5000))

            if company_website:
                self.default_path.set_path('company_website', company_website)
            if copyright_center:
                self.default_path.set_path('copyright_center', copyright_center)
            if server_host:
                self.default_path.set_path('web_api_host', server_host)
            if server_port:
                self.default_path.set_path('web_api_port', server_port)
            
            messagebox.showinfo("成功", "设置保存成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存设置失败: {str(e)}")
    
    def reset_settings(self):
        """重置设置"""
        if messagebox.askyesno("确认", "确定要重置所有设置吗？"):
            self.load_settings()
            messagebox.showinfo("成功", "设置已重置")
    
    def restore_defaults(self):
        """恢复默认设置"""
        if messagebox.askyesno("确认", "确定要恢复默认设置吗？"):
            try:
                # 恢复默认路径
                default_paths = {
                    'template_path': LOCAL_CONFIG['MODEL_DIR'],
                    'id_card_path': LOCAL_CONFIG['IDPDF_DIR'],
                    'usccc_path': LOCAL_CONFIG['USCCC_DIR'],
                    'contract_path': LOCAL_CONFIG['CONTRACT_DIR'],
                    'project_path': LOCAL_CONFIG['PROJECT_FILE_DIR'],
                    'db_path': LOCAL_CONFIG['LOCAL_DB_PATH']
                }
                
                for key, path in default_paths.items():
                    if key in self.path_vars:
                        self.path_vars[key].set(path)
                    elif key == 'db_path':
                        self.db_path_var.set(path)
                
                # 恢复默认网站
                self.company_website_var.set(LOCAL_CONFIG.get('COMPANY_WEBSITE', ''))
                self.copyright_center_var.set(LOCAL_CONFIG.get('COPYRIGHT_CENTER_URL', ''))
                
                messagebox.showinfo("成功", "默认设置已恢复")
                
            except Exception as e:
                messagebox.showerror("错误", f"恢复默认设置失败: {str(e)}")
    
    def test_connection(self):
        """测试连接"""
        try:
            # 测试数据库连接
            db_path = self.db_path_var.get().strip()
            if not db_path:
                messagebox.showwarning("警告", "请先设置数据库路径")
                return
            
            # 测试数据库
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            
            # 测试网站与服务器连接
            import requests
            company_website = self.company_website_var.get().strip()
            if company_website:
                try:
                    response = requests.get(company_website, timeout=5)
                    website_status = f"网站连接正常 (状态码: {response.status_code})"
                except Exception as e:
                    website_status = f"网站连接失败: {str(e)}"
            else:
                website_status = "未设置网站地址"

            server_host = self.server_host_var.get().strip() or LOCAL_CONFIG.get('WEB_API_HOST', 'http://192.168.31.56')
            server_port = self.server_port_var.get().strip() or str(LOCAL_CONFIG.get('WEB_API_PORT', 5000))
            api_base = f"{server_host.rstrip('/')}:" + server_port if server_host.startswith('http') else f"http://{server_host}:{server_port}"
            try:
                r = requests.get(api_base, timeout=5)
                server_status = f"服务器连接正常 ({api_base}, 状态码: {r.status_code})"
            except Exception as e:
                server_status = f"服务器连接失败: {api_base} 错误: {str(e)}"
            
            # 显示测试结果
            result = f"""连接测试结果:

数据库连接: 正常
{website_status}
{server_status}

所有设置验证通过！"""
            
            messagebox.showinfo("连接测试", result)
            
        except Exception as e:
            messagebox.showerror("连接测试失败", f"测试连接时发生错误: {str(e)}")
    
    def view_browser_data_dir(self):
        """查看浏览器数据目录"""
        try:
            from desktop_app.serial_fetcher_simple import _get_user_data_dir
            
            # 获取浏览器数据目录
            browser_data_dir = _get_user_data_dir()
            
            # 检查目录是否存在
            if os.path.exists(browser_data_dir):
                # 计算目录大小
                total_size = 0
                file_count = 0
                for dirpath, dirnames, filenames in os.walk(browser_data_dir):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        try:
                            total_size += os.path.getsize(filepath)
                            file_count += 1
                        except:
                            pass
                
                # 格式化大小
                if total_size < 1024:
                    size_str = f"{total_size} 字节"
                elif total_size < 1024 * 1024:
                    size_str = f"{total_size / 1024:.1f} KB"
                elif total_size < 1024 * 1024 * 1024:
                    size_str = f"{total_size / (1024 * 1024):.1f} MB"
                else:
                    size_str = f"{total_size / (1024 * 1024 * 1024):.1f} GB"
                
                info_text = f"""浏览器数据目录信息：

目录路径: {browser_data_dir}
目录状态: 存在
文件数量: {file_count} 个文件
占用空间: {size_str}

目录包含以下类型的数据：
• 登录凭据和密码
• Cookie 和会话信息
• 浏览器缓存
• 用户偏好设置
• 扩展程序数据

是否要打开该目录？"""
                
                if messagebox.askyesno("浏览器数据目录", info_text):
                    # 打开文件管理器
                    if os.name == 'nt':  # Windows
                        os.startfile(browser_data_dir)
                    elif os.name == 'posix':  # macOS and Linux
                        os.system(f'open "{browser_data_dir}"' if sys.platform == 'darwin' else f'xdg-open "{browser_data_dir}"')
            else:
                messagebox.showinfo("浏览器数据目录", 
                                  f"浏览器数据目录不存在：\n{browser_data_dir}\n\n"
                                  f"这意味着还没有使用过Playwright浏览器功能。")
                
        except Exception as e:
            messagebox.showerror("错误", f"查看浏览器数据目录失败: {str(e)}")
    
    def reset_browser_config(self):
        """重置浏览器配置"""
        try:
            from desktop_app.serial_fetcher_simple import _get_user_data_dir, clear_global_browser
            
            # 获取浏览器数据目录
            browser_data_dir = _get_user_data_dir()
            
            # 确认对话框
            confirm_text = f"""⚠️ 警告：重置浏览器配置

此操作将删除以下数据：
• 所有保存的登录信息
• 所有保存的密码
• 所有Cookie和会话信息
• 浏览器缓存和临时文件
• 用户偏好设置

目录路径: {browser_data_dir}

⚠️ 此操作不可撤销！

确定要继续吗？"""
            
            if not messagebox.askyesno("确认重置", confirm_text):
                return
            
            # 二次确认
            if not messagebox.askyesno("最终确认", 
                                     "请再次确认：\n\n"
                                     "这将永久删除所有浏览器数据！\n"
                                     "您将需要重新登录所有网站。\n\n"
                                     "确定要继续吗？"):
                return
            
            # 先清理全局浏览器实例
            print("[DEBUG] 清理全局浏览器实例...")
            clear_global_browser()
            
            # 删除浏览器数据目录
            if os.path.exists(browser_data_dir):
                print(f"[DEBUG] 删除浏览器数据目录: {browser_data_dir}")
                
                # 递归删除目录
                import shutil
                shutil.rmtree(browser_data_dir)
                
                print("[DEBUG] 浏览器数据目录已删除")
                
                # 显示成功消息
                messagebox.showinfo("重置成功", 
                                  f"浏览器配置已重置！\n\n"
                                  f"已删除目录: {browser_data_dir}\n\n"
                                  f"下次使用Playwright浏览器时，将创建全新的配置。\n"
                                  f"您需要重新登录所有网站。")
            else:
                messagebox.showinfo("重置完成", 
                                  f"浏览器数据目录不存在：\n{browser_data_dir}\n\n"
                                  f"无需删除任何数据。")
                
        except Exception as e:
            print(f"[DEBUG] 重置浏览器配置失败: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("重置失败", f"重置浏览器配置失败: {str(e)}\n\n"
                                            f"请手动删除目录: {browser_data_dir}")
    
    def load_copyright_credentials(self):
        """加载版权中心账号信息"""
        try:
            from desktop_app.credential_manager import get_username_only, has_credentials
            
            if has_credentials():
                username = get_username_only()
                if username:
                    self.copyright_username_var.set(username)
                    self.copyright_password_var.set("")  # 不显示密码
                    self.copyright_status_var.set(f"已保存账号: {username}")
                else:
                    self.copyright_status_var.set("账号信息加载失败")
            else:
                self.copyright_status_var.set("未保存账号信息")
                
        except Exception as e:
            print(f"[DEBUG] 加载版权中心账号失败: {e}")
            self.copyright_status_var.set("加载账号信息失败")
    
    def save_copyright_credentials(self):
        """保存版权中心账号"""
        try:
            from desktop_app.credential_manager import save_credentials
            
            username = self.copyright_username_var.get().strip()
            password = self.copyright_password_var.get().strip()
            
            if not username:
                messagebox.showwarning("输入错误", "请输入账号")
                return
                
            if not password:
                messagebox.showwarning("输入错误", "请输入密码")
                return
            
            # 保存凭证
            success = save_credentials(username, password)
            
            if success:
                self.copyright_status_var.set(f"账号已保存: {username}")
                messagebox.showinfo("保存成功", f"版权中心账号已保存！\n\n账号: {username}\n\n系统将自动填充登录表单。")
            else:
                messagebox.showerror("保存失败", "保存账号失败，请检查系统权限或重试。")
                
        except Exception as e:
            print(f"[DEBUG] 保存版权中心账号失败: {e}")
            messagebox.showerror("保存失败", f"保存账号时发生错误: {str(e)}")
    
    def delete_copyright_credentials(self):
        """删除版权中心账号"""
        try:
            from desktop_app.credential_manager import delete_credentials, has_credentials
            
            if not has_credentials():
                messagebox.showinfo("提示", "没有保存的账号信息")
                return
            
            # 确认删除
            if not messagebox.askyesno("确认删除", 
                                     "确定要删除保存的版权中心账号吗？\n\n"
                                     "删除后需要重新输入账号密码。\n\n"
                                     "此操作不可撤销！"):
                return
            
            # 删除凭证
            success = delete_credentials()
            
            if success:
                # 清空界面
                self.copyright_username_var.set("")
                self.copyright_password_var.set("")
                self.copyright_status_var.set("账号信息已删除")
                messagebox.showinfo("删除成功", "版权中心账号已删除！")
            else:
                messagebox.showerror("删除失败", "删除账号失败，请重试。")
                
        except Exception as e:
            print(f"[DEBUG] 删除版权中心账号失败: {e}")
            messagebox.showerror("删除失败", f"删除账号时发生错误: {str(e)}")
    
    def test_copyright_credentials(self):
        """测试版权中心账号"""
        try:
            from desktop_app.credential_manager import test_credentials, load_credentials
            
            if not test_credentials():
                messagebox.showwarning("测试失败", "没有保存的账号信息或账号信息无效")
                return
            
            credentials = load_credentials()
            if credentials:
                username, password = credentials
                messagebox.showinfo("测试成功", 
                                  f"账号信息测试通过！\n\n"
                                  f"账号: {username}\n"
                                  f"密码: {'*' * len(password)}\n\n"
                                  f"系统可以正常使用自动填充功能。")
            else:
                messagebox.showerror("测试失败", "无法加载账号信息")
                
        except Exception as e:
            print(f"[DEBUG] 测试版权中心账号失败: {e}")
            messagebox.showerror("测试失败", f"测试账号时发生错误: {str(e)}")
