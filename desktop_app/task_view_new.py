#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
任务视图模块 - 改进版
根据需求分析文档设计：左侧项目列表，右侧项目详情
在左侧面板添加Tab控件，包含项目列表、材料文件、项目模板三个标签页
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import shutil
import traceback
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import LOCAL_CONFIG
from desktop_app.dialogs import IDCardDialog, USCCCDialog, ContractDialog
from desktop_app.server_client import ServerClient
from desktop_app.serial_fetcher import fetch_serial_for_project
from desktop_app.selection_dialogs import (TemplateSelectionDialog, IDCardFileDialog,
                                           USCCCFileDialog, ContractFileDialog)


class TaskViewModule:
    """任务视图模块"""
    
    def __init__(self, parent, db, local_project, project_file, 
                 id_card_file, usccc_file, contract_file, template_file,
                 server_client: ServerClient = None, current_user: dict = None, default_path = None):
        self.parent = parent
        self.db = db
        self.local_project = local_project
        self.project_file = project_file
        self.id_card_file = id_card_file
        self.usccc_file = usccc_file
        self.contract_file = contract_file
        self.template_file = template_file
        self.server_client = server_client
        self.current_user = current_user or {}
        self.default_path = default_path
        self.project_cache = {}
        
        # 当前选中的项目
        self.selected_project = None
        
        # 创建界面
        self.create_interface()
        
        # 加载项目数据
        self.refresh_projects()
    
    def create_interface(self):
        """创建任务视图界面"""
        try:
            # 创建主框架
            self.main_frame = tk.Frame(self.parent, bg='white')
            self.parent.add(self.main_frame, text="任务视图")
            
            # 创建左右分栏
            self.create_left_panel()
            self.create_right_panel()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("错误", f"初始化任务视图失败: {str(e)}")
    
    def create_left_panel(self):
        """创建左侧项目列表面板"""
        # 左侧框架
        self.left_frame = tk.Frame(self.main_frame, bg='white', width=400)
        self.left_frame.pack(side='left', fill='y', padx=(10, 5), pady=10)
        self.left_frame.pack_propagate(False)
        
        # 项目列表标题
        tk.Label(self.left_frame, text="项目管理", 
                font=('Microsoft YaHei', 12, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        try:
            # 在 bottom_frame 中创建分页和三个状态列表
            self.create_bottom_frame()
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("错误", f"初始化左侧面板失败: {str(e)}")
    
    def create_status_trees(self):
        """兼容旧方法，不再使用（保留以避免引用错误）"""
        self.create_bottom_frame()
    
    def create_material_tab(self):
        """创建材料标签页"""
        # 材料标签页（暂时下移到右侧或其它模块，不在左侧）
        material_tab = tk.Frame(self.left_frame, bg='white')
        
        # 材料树形控件
        tree_frame = tk.Frame(material_tab, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        # 创建Treeview
        columns = ('ID', '文件名称', '文件类型', '上传时间')
        self.material_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        for col in columns:
            self.material_tree.heading(col, text=col)
            self.material_tree.column(col, width=80)
        
        # 设置列宽
        self.material_tree.column('ID', width=50)
        self.material_tree.column('文件名称', width=200)
        self.material_tree.column('文件类型', width=100)
        self.material_tree.column('上传时间', width=120)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.material_tree.yview)
        self.material_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.material_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 绑定选择事件
        self.material_tree.bind('<<TreeviewSelect>>', self.on_material_select)
    
    def create_template_tab(self):
        """创建模板标签页"""
        # 模板列表移除出左侧，统一使用模板管理模块展示
        template_tab = tk.Frame(self.left_frame, bg='white')
        
        # 模板树形控件
        tree_frame = tk.Frame(template_tab, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        # 创建Treeview
        columns = ('ID', '模板名称', '编程语言', 'IDE类型')
        self.template_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        for col in columns:
            self.template_tree.heading(col, text=col)
            self.template_tree.column(col, width=80)
        
        # 设置列宽
        self.template_tree.column('ID', width=50)
        self.template_tree.column('模板名称', width=150)
        self.template_tree.column('编程语言', width=100)
        self.template_tree.column('IDE类型', width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=scrollbar.set)
        
        # 布局
        self.template_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 绑定选择事件
        self.template_tree.bind('<<TreeviewSelect>>', self.on_template_select)
    
    def create_bottom_frame(self):
        """创建底部区域：顶部控制按钮 + 分页控件(已立项/执行中/已完成)"""
        bottom_frame = tk.Frame(self.left_frame, bg='white')
        bottom_frame.pack(side='bottom', fill='both', expand=True, pady=(10, 0))

        # 顶部控制按钮条
        btn_bar = tk.Frame(bottom_frame, bg='white')
        btn_bar.pack(fill='x', pady=(0, 6))

        tk.Button(btn_bar, text="刷新项目", 
                 font=('Microsoft YaHei', 9), bg='#3498db', fg='white',
                 command=self.refresh_projects).pack(side='left', padx=(0, 5))

        # 分页控件
        self.left_notebook = ttk.Notebook(bottom_frame)
        self.left_notebook.pack(fill='both', expand=True)

        self.trees = {}
        for title in ("已立项", "执行中", "已完成"):
            tab = ttk.Frame(self.left_notebook)
            self.left_notebook.add(tab, text=title)

            columns = ('ID', '项目名称', '项目类型', '优先级')
            tree = ttk.Treeview(tab, columns=columns, show='headings')
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=80)
            tree.column('ID', width=50)
            tree.column('项目名称', width=160)
            tree.column('项目类型', width=110)
            tree.column('优先级', width=80)

            scrollbar = ttk.Scrollbar(tab, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            tree.bind('<<TreeviewSelect>>', lambda e, s=title: self.on_status_tree_select(e, s))
            self.trees[title] = tree
    
    def create_right_panel(self):
        """创建右侧项目详情面板"""
        # 右侧框架
        self.right_frame = tk.Frame(self.main_frame, bg='white')
        self.right_frame.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)
        
        # 控制按钮框架
        self.create_controls_frame()
        
        # 详情框架
        self.create_detail_frame()
        
        # 操作按钮框架
        self.create_handle_frame()
    
    def create_controls_frame(self):
        """创建控制按钮框架"""
        self.controls_frame = tk.Frame(self.right_frame, bg='white', height=25)
        self.controls_frame.pack(fill='x', pady=(0, 10))
        self.controls_frame.pack_propagate(False)
        
        # 按钮
        tk.Button(self.controls_frame, text="创建项目文件夹", 
                 font=('Microsoft YaHei', 9), bg='#38a169', fg='white',
                 command=self.create_project_folder).pack(side='left', padx=5)
        
        tk.Button(self.controls_frame, text="标记为执行中", 
                 font=('Microsoft YaHei', 9), bg='#3182ce', fg='white',
                 command=self.mark_as_executing).pack(side='left', padx=5)
        
        tk.Button(self.controls_frame, text="标记为已完成", 
                 font=('Microsoft YaHei', 9), bg='#d69e2e', fg='white',
                 command=self.mark_as_completed).pack(side='left', padx=5)

        tk.Button(self.controls_frame, text="获取流水号", 
                 font=('Microsoft YaHei', 9), bg='#805ad5', fg='white',
                 command=self.fetch_serial_number).pack(side='left', padx=5)
    
    def create_detail_frame(self):
        """创建详情框架 - 按照需求文档设计"""
        self.detail_frame = tk.Frame(self.right_frame, bg='white')
        self.detail_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # 分为左右两列：detail_left_frame 和 detail_right_frame
        # detail_left_frame: 显示项目文件列表
        self.detail_left_frame = tk.Frame(self.detail_frame, bg='white')
        self.detail_left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # detail_right_frame: 显示项目详细信息
        self.detail_right_frame = tk.Frame(self.detail_frame, bg='white')
        self.detail_right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # 创建左侧文件列表
        self.create_file_list()
        
        # 创建右侧项目详情
        self.create_project_info()
    
    def create_file_list(self):
        """创建左侧文件列表"""
        # 文件列表标题
        tk.Label(self.detail_left_frame, text="项目文件列表", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        
        # 文件列表Treeview
        file_columns = ('文件名', '类型', '大小', '修改时间')
        self.file_tree = ttk.Treeview(self.detail_left_frame, columns=file_columns, show='headings')
        
        for col in file_columns:
            self.file_tree.heading(col, text=col)
            self.file_tree.column(col, width=100)
        
        # 设置列宽
        self.file_tree.column('文件名', width=200)
        self.file_tree.column('类型', width=80)
        self.file_tree.column('大小', width=80)
        self.file_tree.column('修改时间', width=120)
        
        # 滚动条
        file_scrollbar = ttk.Scrollbar(self.detail_left_frame, orient='vertical', 
                                     command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=file_scrollbar.set)
        
        # 布局
        self.file_tree.pack(side='left', fill='both', expand=True)
        file_scrollbar.pack(side='right', fill='y')
        
        # 绑定右键菜单
        self.file_tree.bind('<Button-3>', self.show_file_context_menu)
        self.file_tree.bind('<Double-1>', self.open_file)
    
    def create_project_info(self):
        """创建右侧项目详细信息"""
        # 项目信息标题
        tk.Label(self.detail_right_frame, text="项目详细信息", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        
        # 创建滚动框架
        info_canvas = tk.Canvas(self.detail_right_frame, bg='white')
        info_scrollbar = ttk.Scrollbar(self.detail_right_frame, orient='vertical', 
                                     command=info_canvas.yview)
        self.info_scrollable_frame = tk.Frame(info_canvas, bg='white')
        
        info_canvas.configure(yscrollcommand=info_scrollbar.set)
        info_canvas.pack(side='left', fill='both', expand=True)
        info_scrollbar.pack(side='right', fill='y')
        
        # 在画布中创建窗口
        info_canvas.create_window((0, 0), window=self.info_scrollable_frame, anchor='nw')
        
        # 项目信息字段
        self.info_labels = {}
        self.info_entries = {}
        
        # 第一行：姓名、流水号、著作权人（带检索功能）
        first_row = tk.Frame(self.info_scrollable_frame, bg='white')
        first_row.pack(fill='x', pady=5)
        
        # 姓名
        tk.Label(first_row, text="姓名:", font=('Microsoft YaHei', 9), bg='white').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.info_entries['applicant_name'] = tk.Entry(first_row, font=('Microsoft YaHei', 9), width=15)
        self.info_entries['applicant_name'].grid(row=0, column=1, padx=(0, 10))
        
        # 流水号
        tk.Label(first_row, text="流水号:", font=('Microsoft YaHei', 9), bg='white').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.info_entries['serial_number'] = tk.Entry(first_row, font=('Microsoft YaHei', 9), width=15)
        self.info_entries['serial_number'].grid(row=0, column=3, padx=(0, 10))
        
        # 著作权人
        tk.Label(first_row, text="著作权人:", font=('Microsoft YaHei', 9), bg='white').grid(row=0, column=4, sticky='w', padx=(0, 5))
        self.info_entries['copyright_owner'] = tk.Entry(first_row, font=('Microsoft YaHei', 9), width=15)
        self.info_entries['copyright_owner'].grid(row=0, column=5, padx=(0, 10))
        
        # 检索按钮
        tk.Button(first_row, text="检索项目", font=('Microsoft YaHei', 8), 
                 command=self.search_project).grid(row=0, column=6, padx=(5, 0))
        
        # 其他项目信息字段
        info_fields = [
            ('项目名称', 'project_name', 20),
            ('项目类型', 'project_type', 15),
            ('申请人类型', 'applicant_type', 15),
            ('软件申请人', 'software_applicant_name', 20),
            ('优先级', 'priority', 10),
            ('状态', 'status', 10),
            ('执行者', 'executor_name', 15),
            ('备注', 'remarks', 30)
        ]
        
        for i, (label_text, field_name, width) in enumerate(info_fields):
            row_frame = tk.Frame(self.info_scrollable_frame, bg='white')
            row_frame.pack(fill='x', pady=2)
            
            tk.Label(row_frame, text=f"{label_text}:", font=('Microsoft YaHei', 9), 
                    bg='white', width=8, anchor='w').pack(side='left', padx=(0, 5))
            
            if field_name == 'remarks':
                # 备注使用多行文本框
                self.info_entries[field_name] = tk.Text(row_frame, font=('Microsoft YaHei', 9), 
                                                      width=width, height=3, wrap='word')
                self.info_entries[field_name].pack(side='left', fill='x', expand=True)
            else:
                self.info_entries[field_name] = tk.Entry(row_frame, font=('Microsoft YaHei', 9), 
                                                       width=width)
                self.info_entries[field_name].pack(side='left', fill='x', expand=True)
        
        # 绑定滚动事件
        def on_mousewheel(event):
            info_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        info_canvas.bind("<MouseWheel>", on_mousewheel)
        self.info_scrollable_frame.bind("<MouseWheel>", on_mousewheel)
    
    def create_handle_frame(self):
        """创建操作按钮框架 - 按照需求文档设计"""
        self.handle_frame = tk.Frame(self.right_frame, bg='white', height=30)
        self.handle_frame.pack(side='bottom', fill='x')
        self.handle_frame.pack_propagate(False)
        
        # 材料选择按钮（按需求文档要求）
        tk.Button(self.handle_frame, text="身份证复印件", 
                 font=('Microsoft YaHei', 9), bg='#e53e3e', fg='white',
                 command=self.show_id_card_dialog).pack(side='left', padx=5)
        
        tk.Button(self.handle_frame, text="统一社会信用代码证书", 
                 font=('Microsoft YaHei', 9), bg='#38a169', fg='white',
                 command=self.show_usccc_dialog).pack(side='left', padx=5)
        
        tk.Button(self.handle_frame, text="合同文件", 
                 font=('Microsoft YaHei', 9), bg='#d69e2e', fg='white',
                 command=self.show_contract_dialog).pack(side='left', padx=5)
        
        # 分隔符
        tk.Frame(self.handle_frame, width=2, height=20, bg='#ccc').pack(side='left', padx=10, fill='y')
        
        # 国家版权保护中心访问按钮
        tk.Button(self.handle_frame, text="版权保护中心", 
                 font=('Microsoft YaHei', 9), bg='#805ad5', fg='white',
                 command=self.open_copyright_center).pack(side='left', padx=5)
        
        # 公司网站访问按钮
        tk.Button(self.handle_frame, text="公司网站", 
                 font=('Microsoft YaHei', 9), bg='#3182ce', fg='white',
                 command=self.open_company_website).pack(side='left', padx=5)
        
        # 保存修改按钮（将右侧表单中的修改提交至服务器）
        tk.Button(self.handle_frame, text="保存修改", 
                 font=('Microsoft YaHei', 9), bg='#2d3748', fg='white',
                 command=self.save_project_changes).pack(side='right', padx=5)
    
    def on_status_tree_select(self, event, status_title: str):
        """任一状态树的选中事件"""
        try:
            tree = self.trees.get(status_title)
            if not tree:
                return
            selection = tree.selection()
            if selection:
                item = tree.item(selection[0])
                project_id = item['values'][0]
                self.load_project_details(project_id)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("错误", f"选择项目失败: {str(e)}")
    
    def on_material_select(self, event):
        """材料选择事件"""
        try:
            selection = self.material_tree.selection()
            if selection:
                item = self.material_tree.item(selection[0])
                material_id = item['values'][0]
                self.load_material_details(material_id)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("错误", f"选择材料失败: {str(e)}")
    
    def on_template_select(self, event):
        """模板选择事件"""
        try:
            selection = self.template_tree.selection()
            if selection:
                item = self.template_tree.item(selection[0])
                template_id = item['values'][0]
                self.load_template_details(template_id)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("错误", f"选择模板失败: {str(e)}")
    
    def load_project_details(self, project_id):
        """加载项目详情"""
        try:
            # 优先从缓存（服务端数据）获取
            project = self.project_cache.get(project_id)
            if not project:
                # 回退到本地数据库
                project = self.local_project.get_project_by_id(project_id)
            if project:
                self.selected_project = project
                self.display_project_details(project)
        except Exception as e:
            messagebox.showerror("错误", f"加载项目详情失败: {str(e)}")
    
    def load_material_details(self, material_id):
        """加载材料详情"""
        try:
            # 这里应该根据材料类型加载不同的详情
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, f"材料ID: {material_id}\n")
            self.detail_text.insert(tk.END, "材料详情加载中...\n")
        except Exception as e:
            messagebox.showerror("错误", f"加载材料详情失败: {str(e)}")
    
    def load_template_details(self, template_id):
        """加载模板详情"""
        try:
            # 这里应该从数据库获取模板详情
            self.detail_text.delete(1.0, tk.END)
            self.detail_text.insert(tk.END, f"模板ID: {template_id}\n")
            self.detail_text.insert(tk.END, "模板详情加载中...\n")
        except Exception as e:
            messagebox.showerror("错误", f"加载模板详情失败: {str(e)}")
    
    def display_project_details(self, project):
        """显示项目详情 - 使用新的界面布局"""
        try:
            # 清空文件列表
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            # 填充项目信息到右侧详情区域
            project_data = {
                'applicant_name': project.get('software_applicant_name', ''),
                'serial_number': project.get('serial_number', ''),
                'copyright_owner': project.get('copyright_owner', ''),
                'project_name': project.get('project_name', ''),
                'project_type': project.get('project_type', ''),
                'applicant_type': project.get('applicant_type', ''),
                'software_applicant_name': project.get('software_applicant_name', ''),
                'priority': project.get('priority', ''),
                'status': project.get('status', ''),
                'executor_name': project.get('executor_name', ''),
                'remarks': project.get('remarks', '')
            }
            
            # 更新信息字段
            for field_name, value in project_data.items():
                if field_name in self.info_entries:
                    if field_name == 'remarks':
                        self.info_entries[field_name].delete(1.0, tk.END)
                        self.info_entries[field_name].insert(1.0, str(value))
                    else:
                        self.info_entries[field_name].delete(0, tk.END)
                        self.info_entries[field_name].insert(0, str(value))
            
            # 加载项目文件列表
            self.load_project_files(project.get('id'))
            
        except Exception as e:
            messagebox.showerror("错误", f"显示项目详情失败: {str(e)}")
    
    def load_project_files(self, project_id):
        """加载项目文件列表 - 从项目文件夹中读取实际文件"""
        try:
            if not project_id:
                return
            
            # 清空文件列表
            for item in self.file_tree.get_children():
                self.file_tree.delete(item)
            
            # 获取项目信息
            project = self.selected_project
            if not project:
                return
            
            project_name = project.get('project_name', '')
            
            # 获取项目文件夹路径
            base_path = self.default_path.get_path('project_path') or LOCAL_CONFIG.get('PROJECT_FILE_DIR', 'D:/SoftwareCopyrightMS/Projects')
            project_folder = os.path.join(base_path, f"{project_id}.{project_name}")
            
            # 检查项目文件夹是否存在
            if not os.path.exists(project_folder):
                print(f"[INFO] 项目文件夹不存在: {project_folder}")
                return
            
            # 遍历项目文件夹中的所有文件
            file_count = 0
            for root, dirs, files in os.walk(project_folder):
                for file_name in files:
                    file_path = os.path.join(root, file_name)
                    
                    # 获取文件信息
                    file_size = os.path.getsize(file_path)
                    file_ext = os.path.splitext(file_name)[1].lower()
                    
                    # 确定文件类型
                    file_type = self.get_file_type(file_ext)
                    
                    # 获取修改时间
                    mtime = os.path.getmtime(file_path)
                    time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 格式化文件大小
                    size_str = self.format_file_size(file_size)
                    
                    # 计算相对路径
                    rel_path = os.path.relpath(file_path, project_folder)
                    
                    # 添加到树形控件
                    self.file_tree.insert('', 'end', values=(
                        rel_path,      # 文件名（相对路径）
                        file_type,     # 文件类型
                        size_str,      # 文件大小
                        time_str       # 修改时间
                    ), tags=(file_path,))  # 完整路径存储在tags中
                    
                    file_count += 1
            
            print(f"[INFO] 加载了 {file_count} 个文件")
                
        except Exception as e:
            print(f"加载项目文件失败: {str(e)}")
            traceback.print_exc()
    
    def get_file_type(self, file_ext):
        """根据文件扩展名确定文件类型"""
        ext_map = {
            '.pdf': 'PDF文档',
            '.doc': 'Word文档',
            '.docx': 'Word文档',
            '.xls': 'Excel表格',
            '.xlsx': 'Excel表格',
            '.txt': '文本文件',
            '.py': 'Python源码',
            '.java': 'Java源码',
            '.cpp': 'C++源码',
            '.c': 'C源码',
            '.h': '头文件',
            '.js': 'JavaScript',
            '.html': 'HTML文件',
            '.css': 'CSS文件',
            '.sql': 'SQL脚本',
            '.zip': '压缩文件',
            '.rar': '压缩文件',
            '.7z': '压缩文件',
            '.png': '图片文件',
            '.jpg': '图片文件',
            '.jpeg': '图片文件',
            '.gif': '图片文件',
            '.bmp': '图片文件',
        }
        return ext_map.get(file_ext, '其他文件')
    
    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def show_file_context_menu(self, event):
        """显示文件右键菜单"""
        try:
            # 选择右键点击的项目
            item = self.file_tree.identify_row(event.y)
            if item:
                self.file_tree.selection_set(item)
                
                # 创建右键菜单
                context_menu = tk.Menu(self.file_tree, tearoff=0)
                context_menu.add_command(label="打开文件", command=self.open_file)
                context_menu.add_command(label="打开文件夹", command=self.open_file_folder)
                context_menu.add_separator()
                context_menu.add_command(label="删除文件", command=self.delete_file)
                
                # 显示菜单
                context_menu.post(event.x_root, event.y_root)
        except Exception as e:
            messagebox.showerror("错误", f"显示右键菜单失败: {str(e)}")
    
    def open_file(self, event=None):
        """打开文件"""
        try:
            selection = self.file_tree.selection()
            if not selection:
                return
            
            item = self.file_tree.item(selection[0])
            tags = item.get('tags', ())
            
            if not tags:
                messagebox.showwarning("警告", "无法获取文件路径")
                return
            
            file_path = tags[0]  # 完整路径存储在第一个tag中
            
            if not os.path.exists(file_path):
                messagebox.showerror("错误", f"文件不存在：{file_path}")
                return
            
            # 使用系统默认程序打开文件
            import subprocess
            if sys.platform == 'win32':
                os.startfile(file_path)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
                
        except Exception as e:
            messagebox.showerror("错误", f"打开文件失败: {str(e)}")
    
    def open_file_folder(self):
        """打开文件所在文件夹"""
        try:
            selection = self.file_tree.selection()
            if not selection:
                return
            
            item = self.file_tree.item(selection[0])
            tags = item.get('tags', ())
            
            if not tags:
                messagebox.showwarning("警告", "无法获取文件路径")
                return
            
            file_path = tags[0]
            
            if not os.path.exists(file_path):
                messagebox.showerror("错误", f"文件不存在：{file_path}")
                return
            
            # 获取文件所在目录
            folder_path = os.path.dirname(file_path)
            
            # 使用系统文件管理器打开文件夹并选中文件
            import subprocess
            if sys.platform == 'win32':
                # 规范化 Windows 路径并正确传递给 explorer
                normalized_path = os.path.normpath(os.path.realpath(file_path))
                # 注意：/select, 与路径需要作为同一个参数传递，且路径需要加引号
                cmd = f'explorer /select,"{normalized_path}"'
                subprocess.run(cmd, shell=True)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', '-R', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', folder_path])
                
        except Exception as e:
            messagebox.showerror("错误", f"打开文件夹失败: {str(e)}")
    
    def delete_file(self):
        """删除文件"""
        try:
            selection = self.file_tree.selection()
            if not selection:
                return
            
            item = self.file_tree.item(selection[0])
            file_name = item['values'][0]
            tags = item.get('tags', ())
            
            if not tags:
                messagebox.showwarning("警告", "无法获取文件路径")
                return
            
            file_path = tags[0]
            
            if not os.path.exists(file_path):
                messagebox.showerror("错误", f"文件不存在：{file_path}")
                return
            
            # 确认删除
            response = messagebox.askyesno(
                "确认删除", 
                f"确定要删除文件吗？\n\n{file_name}\n\n此操作不可恢复！"
            )
            
            if response:
                # 删除文件
                os.remove(file_path)
                
                # 从树形控件中移除
                self.file_tree.delete(selection[0])
                
                messagebox.showinfo("成功", "文件已删除")
                
        except Exception as e:
            messagebox.showerror("错误", f"删除文件失败: {str(e)}")
    
    def search_project(self):
        """检索项目"""
        try:
            # 获取检索条件
            applicant_name = self.info_entries['applicant_name'].get().strip()
            serial_number = self.info_entries['serial_number'].get().strip()
            copyright_owner = self.info_entries['copyright_owner'].get().strip()
            
            if not any([applicant_name, serial_number, copyright_owner]):
                messagebox.showwarning("提示", "请输入至少一个检索条件")
                return
            
            # 这里应该实现项目检索逻辑
            # 检索成功后，在左侧Treeview中跳转到对应项目
            messagebox.showinfo("提示", "项目检索功能待实现")
            
        except Exception as e:
            messagebox.showerror("错误", f"检索项目失败: {str(e)}")
    
    def _collect_project_form_values(self):
        """从右侧表单收集项目字段值，返回dict（仅包含可编辑字段）。"""
        values = {}
        def get_text(name):
            w = self.info_entries.get(name)
            if not w:
                return ''
            try:
                if isinstance(w, tk.Text):
                    return w.get('1.0', tk.END).strip()
                return w.get().strip()
            except Exception:
                return ''
        
        # 映射表单字段到数据库列名
        field_mapping = {
            'project_name': 'project_name',
            'project_type': 'project_type', 
            'applicant_type': 'applicant_type',
            'software_applicant_name': 'software_applicant_name',
            'priority': 'priority',
            'status': 'status',
            'remarks': 'remarks',
            'serial_number': 'serial_number',
            'applicant_name': 'software_applicant_name'  # 表单中的applicant_name对应数据库的software_applicant_name
            # 注意：executor_name 暂时不映射，因为数据库中是 executor_id (INTEGER)，而表单中是文本
        }
        
        for form_field, db_field in field_mapping.items():
            text_value = get_text(form_field)
            if text_value:  # 只添加非空值
                values[db_field] = text_value
        
        return values
    
    def save_project_changes(self):
        """保存当前选中项目的修改到服务器（若可用），并回落更新本地。"""
        try:
            if not self.selected_project:
                messagebox.showwarning("提示", "请先在左侧选择一个项目")
                return
            project_id = self.selected_project.get('id')
            if not project_id:
                messagebox.showwarning("提示", "当前项目缺少ID，无法保存")
                return
            
            payload = self._collect_project_form_values()
            if not payload:
                messagebox.showinfo("提示", "没有需要保存的修改")
                return
            
            # 优先尝试服务器更新
            server_ok = False
            server_msg = ''
            if self.server_client and hasattr(self.server_client, 'update_project_fields'):
                try:
                    # 期望 ServerClient.update_project_fields(project_id, payload: dict) -> (ok, msg)
                    ok, msg = self.server_client.update_project_fields(project_id, payload)
                    server_ok = bool(ok)
                    server_msg = msg or ''
                except Exception as e:
                    traceback.print_exc()
                    server_ok = False
                    server_msg = str(e)
            
            # 回落：更新本地缓存与本地数据库
            if hasattr(self, 'local_project') and self.local_project:
                try:
                    # 仅更新本地表中存在的字段
                    self.local_project.update_project(project_id, **payload)
                except Exception:
                    traceback.print_exc()
            try:
                # 更新内存对象，保持UI与数据同步
                for k, v in payload.items():
                    self.selected_project[k] = v
            except Exception:
                pass
            
            if server_ok:
                messagebox.showinfo("保存修改", "已成功保存到服务器并更新本地")
            else:
                msg = "已保存到本地，服务器未同步\n"
                if server_msg:
                    msg += f"原因：{server_msg}"
                messagebox.showwarning("保存修改", msg)
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("错误", f"保存失败: {str(e)}")
    
    def show_id_card_dialog(self):
        """显示身份证复印件对话框"""
        try:
            # 获取目标文件夹
            target_folder = None
            if self.selected_project:
                project_id = self.selected_project.get('id', '')
                project_name = self.selected_project.get('project_name', '')
                base_path = self.default_path.get_path('project_path') or LOCAL_CONFIG.get('PROJECT_FILE_DIR', 'D:/SoftwareCopyrightMS/Projects')
                target_folder = os.path.join(base_path, f"{project_id}.{project_name}")
                
                # 确保目标文件夹存在
                if not os.path.exists(target_folder):
                    response = messagebox.askyesno("提示", "项目文件夹不存在，是否先创建项目文件夹？")
                    if response:
                        self.create_project_folder()
                        return
                    else:
                        target_folder = None
            
            # 打开身份证复印件选择对话框
            dialog = IDCardFileDialog(
                self.main_frame,
                self.id_card_file,
                target_folder=target_folder
            )
            
            result = dialog.show()
            
            if result:
                messagebox.showinfo("成功", f"文件已添加到项目")
                # 刷新项目文件列表
                if self.selected_project:
                    self.display_project_details(self.selected_project)
            
        except Exception as e:
            messagebox.showerror("错误", f"显示身份证对话框失败: {str(e)}")
    
    def show_usccc_dialog(self):
        """显示统一社会信用代码证书对话框"""
        try:
            # 获取目标文件夹
            target_folder = None
            if self.selected_project:
                project_id = self.selected_project.get('id', '')
                project_name = self.selected_project.get('project_name', '')
                base_path = self.default_path.get_path('project_path') or LOCAL_CONFIG.get('PROJECT_FILE_DIR', 'D:/SoftwareCopyrightMS/Projects')
                target_folder = os.path.join(base_path, f"{project_id}.{project_name}")
                
                # 确保目标文件夹存在
                if not os.path.exists(target_folder):
                    response = messagebox.askyesno("提示", "项目文件夹不存在，是否先创建项目文件夹？")
                    if response:
                        self.create_project_folder()
                        return
                    else:
                        target_folder = None
            
            # 打开统一社会信用代码证书选择对话框
            dialog = USCCCFileDialog(
                self.main_frame,
                self.usccc_file,
                target_folder=target_folder
            )
            
            result = dialog.show()
            
            if result:
                messagebox.showinfo("成功", f"文件已添加到项目")
                # 刷新项目文件列表
                if self.selected_project:
                    self.display_project_details(self.selected_project)
            
        except Exception as e:
            messagebox.showerror("错误", f"显示证书对话框失败: {str(e)}")
    
    def show_contract_dialog(self):
        """显示合同文件对话框"""
        try:
            # 获取目标文件夹
            target_folder = None
            if self.selected_project:
                project_id = self.selected_project.get('id', '')
                project_name = self.selected_project.get('project_name', '')
                base_path = self.default_path.get_path('project_path') or LOCAL_CONFIG.get('PROJECT_FILE_DIR', 'D:/SoftwareCopyrightMS/Projects')
                target_folder = os.path.join(base_path, f"{project_id}.{project_name}")
                
                # 确保目标文件夹存在
                if not os.path.exists(target_folder):
                    response = messagebox.askyesno("提示", "项目文件夹不存在，是否先创建项目文件夹？")
                    if response:
                        self.create_project_folder()
                        return
                    else:
                        target_folder = None
            
            # 打开合同文件选择对话框
            dialog = ContractFileDialog(
                self.main_frame,
                self.contract_file,
                target_folder=target_folder
            )
            
            result = dialog.show()
            
            if result:
                messagebox.showinfo("成功", f"文件已添加到项目")
                # 刷新项目文件列表
                if self.selected_project:
                    self.display_project_details(self.selected_project)
            
        except Exception as e:
            messagebox.showerror("错误", f"显示合同对话框失败: {str(e)}")
    
    def open_copyright_center(self):
        """打开国家版权保护中心网站"""
        try:
            import webbrowser
            url = "https://www.ccopyright.com.cn/"
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("错误", f"打开版权保护中心失败: {str(e)}")
    
    def open_company_website(self):
        """打开公司网站"""
        try:
            import webbrowser
            url = "http://192.168.31.56:5000"
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("错误", f"打开公司网站失败: {str(e)}")
    
    def refresh_projects(self):
        """刷新项目列表"""
        try:
            # 清空现有数据
            for tree in self.trees.values():
                for item in tree.get_children():
                    tree.delete(item)

            # 若已登录且有 server_client，则按状态从服务器取数
            self.project_cache = {}
            if self.server_client and self.current_user.get('user_type') == 'staff':
                for status_title in ("已立项", "执行中", "已完成"):
                    ok, msg, rows = self.server_client.get_projects_by_status(status_title)
                    if not ok:
                        print(f"获取 {status_title} 列表失败: {msg}")
                        continue
                    for p in rows:
                        self.project_cache[p.get('id')] = p
                        self.trees[status_title].insert('', 'end', values=(
                            p.get('id'), p.get('project_name'), p.get('project_type'), p.get('priority')
                        ))
            else:
                # 回退：从本地库按状态字段粗略分组
                projects = self.local_project.get_all_projects()
                for project in projects:
                    pid, name, ptype, status, priority = project[0], project[1], project[2], project[8], project[7]
                    self.project_cache[pid] = {
                        'id': pid,
                        'project_name': name,
                        'project_type': ptype,
                        'priority': priority,
                        'status': status
                    }
                    if status in self.trees:
                        self.trees[status].insert('', 'end', values=(pid, name, ptype, priority))
            
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("错误", f"刷新项目列表失败: {str(e)}")
    
    def refresh_materials(self):
        """刷新材料列表"""
        try:
            # 加载身份证文件
            id_files = self.id_card_file.get_all_files()
            for file in id_files:
                self.material_tree.insert('', 'end', values=(
                    file[0],  # ID
                    file[1],  # 文件名称
                    '身份证',  # 文件类型
                    file[6] if len(file) > 6 else 'N/A'  # 上传时间
                ))
            
            # 加载证书文件
            usccc_files = self.usccc_file.get_all_files()
            for file in usccc_files:
                self.material_tree.insert('', 'end', values=(
                    file[0],  # ID
                    file[1],  # 文件名称
                    '证书',  # 文件类型
                    file[6] if len(file) > 6 else 'N/A'  # 上传时间
                ))
            
            # 加载合同文件
            contract_files = self.contract_file.get_all_files()
            for file in contract_files:
                self.material_tree.insert('', 'end', values=(
                    file[0],  # ID
                    file[1],  # 文件名称
                    '合同',  # 文件类型
                    file[5] if len(file) > 5 else 'N/A'  # 上传时间
                ))
                
        except Exception as e:
            print(f"刷新材料列表失败: {str(e)}")
    
    def refresh_templates(self):
        """刷新模板列表"""
        try:
            # 加载模板数据
            templates = self.template_file.get_all_files()
            for template in templates:
                self.template_tree.insert('', 'end', values=(
                    template[0],  # ID
                    template[1],  # 模板名称
                    template[2],  # 编程语言
                    template[3]   # IDE类型
                ))
                
        except Exception as e:
            traceback.print_exc()
            print(f"刷新模板列表失败: {str(e)}")
    
    def create_project_folder(self):
        """创建项目文件夹 - 使用模板选择对话框"""
        if not self.selected_project:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        try:
            project_name = self.selected_project.get('project_name', 'Unknown')
            project_id = self.selected_project.get('id', 'Unknown')
            
            # 获取项目文件夹基础路径
            base_path = self.default_path.get_path('project_path') or LOCAL_CONFIG.get('PROJECT_FILE_DIR', 'D:/SoftwareCopyrightMS/Projects')
            
            # 确保基础路径存在
            if not os.path.exists(base_path):
                os.makedirs(base_path)
            
            # 打开模板选择对话框
            dialog = TemplateSelectionDialog(
                self.main_frame,
                self.template_file,
                project_id=project_id,
                project_name=project_name,
                target_folder=base_path
            )
            
            result = dialog.show()
            
            if result:
                messagebox.showinfo("成功", f"项目文件夹已创建: {result}")
                # 刷新项目详情显示
                self.display_project_details(self.selected_project)
            
        except Exception as e:
            messagebox.showerror("错误", f"创建项目文件夹失败: {str(e)}")
    
    def mark_as_executing(self):
        """标记为执行中"""
        if not self.selected_project:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        try:
            project_id = self.selected_project.get('id')
            self.local_project.update_project_status(project_id, '执行中')
            messagebox.showinfo("成功", "项目状态已更新为执行中")
            self.refresh_projects()
        except Exception as e:
            messagebox.showerror("错误", f"更新项目状态失败: {str(e)}")
    
    def mark_as_completed(self):
        """标记为已完成"""
        if not self.selected_project:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        try:
            project_id = self.selected_project.get('id')
            self.local_project.update_project_status(project_id, '已完成')
            messagebox.showinfo("成功", "项目状态已更新为已完成")
            self.refresh_projects()
        except Exception as e:
            messagebox.showerror("错误", f"更新项目状态失败: {str(e)}")
    
    def fetch_serial_number(self):
        """获取流水号（占位实现，可扩展为从网页解析或API获取）"""
        if not self.selected_project:
            messagebox.showwarning("警告", "请先选择一个项目")
            return
        
        try:
            # 1) 读取当前项目关键信息
            project_id = self.selected_project.get('id')
            project_name = self.selected_project.get('project_name')
            applicant_name = self.selected_project.get('software_applicant_name')
            
            if not project_name:
                messagebox.showwarning("提示", "当前项目缺少项目名称，无法匹配网页上的项目记录")
                return
            
            # 2) 通过已登录的浏览器页面抓取流水号（用户需事先在版权中心登录并进入用户中心）
            serial = fetch_serial_for_project(project_name, applicant_name)
            
            if not serial:
                messagebox.showwarning(
                    "获取流水号",
                    "未在当前网页中找到匹配的项目，请确认已登录版权保护中心并进入用户中心，且页面包含该项目。"
                )
                return
            
            # 3) 回填到界面
            if 'serial_number' in self.info_entries:
                try:
                    self.info_entries['serial_number'].delete(0, tk.END)
                    self.info_entries['serial_number'].insert(0, str(serial))
                except Exception:
                    pass
            
            # 同步更新到内存选中项目
            try:
                self.selected_project['serial_number'] = serial
            except Exception:
                pass
            
            # 4) 更新到服务器（如可用）
            server_updated = False
            if self.server_client and hasattr(self.server_client, 'update_project_serial'):
                try:
                    ok, msg = self.server_client.update_project_serial(project_id, serial)
                    server_updated = bool(ok)
                except Exception:
                    traceback.print_exc()
                    server_updated = False
            
            # 5) 结果提示
            if server_updated:
                messagebox.showinfo("获取流水号", f"流水号已获取并同步：{serial}")
            else:
                messagebox.showinfo(
                    "获取流水号",
                    f"流水号已获取并回填：{serial}。服务器同步未完成或接口不可用，可稍后再试。"
                )
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("错误", f"获取流水号失败: {str(e)}")
