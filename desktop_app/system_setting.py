#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统设置模块
根据需求分析文档设计：路径配置管理
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
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
        
        # 创建设置表单
        self.create_settings_form()
    
    def create_settings_form(self):
        """创建设置表单"""
        # 标题
        title_frame = tk.Frame(self.main_frame, bg='white')
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(title_frame, text="系统设置", 
                font=('Microsoft YaHei', 16, 'bold'), bg='white', fg='#2c5282').pack()
        
        # 设置表单框架
        form_frame = tk.Frame(self.main_frame, bg='white')
        form_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
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
        
        # 按钮框架
        self.create_button_frame()
    
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
    
    def create_button_frame(self):
        """创建按钮框架"""
        button_frame = tk.Frame(self.main_frame, bg='white')
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
