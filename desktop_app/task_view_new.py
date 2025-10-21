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
import psutil
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import LOCAL_CONFIG
from desktop_app.dialogs import IDCardDialog, USCCCDialog, ContractDialog
from desktop_app.server_client import ServerClient
from desktop_app.serial_fetcher_simple import fetch_serial_for_project
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
        self.use_playwright_browser = tk.BooleanVar()
        self.controls_frame = tk.Frame(self.right_frame, bg='white', height=25)
        self.controls_frame.pack(fill='x', pady=(0, 10))
        self.controls_frame.pack_propagate(False)
        
        # 按钮
        tk.Button(self.controls_frame, text="创建项目", 
                 font=('Microsoft YaHei', 9), bg='#38a169', fg='white',
                 command=self.create_project_folder).pack(side='left', padx=5)
        
        tk.Button(self.controls_frame, text="执行", 
                 font=('Microsoft YaHei', 9), bg='#3182ce', fg='white',
                 command=self.mark_as_executing).pack(side='left', padx=5)
        
        tk.Button(self.controls_frame, text="完成", 
                 font=('Microsoft YaHei', 9), bg='#d69e2e', fg='white',
                 command=self.mark_as_completed).pack(side='left', padx=5)

        tk.Button(self.controls_frame, text="收费", 
                 font=('Microsoft YaHei', 9), bg='#d69e2e', fg='white',
                 command=self.mark_as_charged).pack(side='left', padx=5)

        tk.Button(self.controls_frame, text="归档", 
                 font=('Microsoft YaHei', 9), bg='#d69e2e', fg='white',
                 command=self.mark_as_archived).pack(side='left', padx=5)

        tk.Button(self.controls_frame, text="获取流水号", 
                 font=('Microsoft YaHei', 9), bg='#805ad5', fg='white',
                 command=self.fetch_serial_number).pack(side='left', padx=5)
        tk.Checkbutton(self.controls_frame,text="使用pwEXPLOER",variable=self.use_playwright_browser).pack(side='left', padx=5)
        self.use_playwright_browser.set(True)
    
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
        """创建右侧项目详细信息 - 支持动态滚动框架"""
        # 项目信息标题
        tk.Label(self.detail_right_frame, text="项目详细信息", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 5))
        
        # 创建动态滚动框架容器
        self.info_container = tk.Frame(self.detail_right_frame, bg='white')
        self.info_container.pack(fill='both', expand=True)
        
        # 初始化滚动框架相关变量
        self.info_canvas = None
        self.info_scrollbar = None
        self.info_scrollable_frame = None
        self.scroll_frame_active = False
        
        # 项目信息字段
        self.info_labels = {}
        self.info_entries = {}
        
        # 创建项目信息内容
        self._create_info_content()
        
        # 绑定窗口大小变化事件
        self._bind_resize_events()
        
        # 初始检查是否需要滚动框架
        self._check_and_update_scroll_frame()
    
    def _create_info_content(self):
        """创建项目信息内容"""
        # 第一行：姓名、流水号、著作权人（带检索功能）
        first_row = tk.Frame(self.info_scrollable_frame if self.scroll_frame_active else self.info_container, bg='white')
        first_row.pack(fill='x', pady=5)
        
        # 申请人
        tk.Label(first_row, text="申请人:", font=('Microsoft YaHei', 9), bg='white').grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.info_entries['software_applicant_name'] = tk.Entry(first_row, font=('Microsoft YaHei', 9), width=15)
        self.info_entries['software_applicant_name'].grid(row=0, column=1, padx=(0, 10))
        
        # 流水号
        tk.Label(first_row, text="流水号:", font=('Microsoft YaHei', 9), bg='white').grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.info_entries['serial_number'] = tk.Entry(first_row, font=('Microsoft YaHei', 9), width=15)
        self.info_entries['serial_number'].grid(row=0, column=3, padx=(0, 10))
        
        # 检索按钮
        tk.Button(first_row, text="检索项目", font=('Microsoft YaHei', 8), 
                 command=self.search_project).grid(row=0, column=4, padx=(5, 0))
        
        # 其他项目信息字段
        info_fields = [
            ('项目名称', 'project_name', 20),
            ('项目类型', 'project_type', 15),
            ('申请人类型', 'applicant_type', 15),
            ('著作权人', 'copyright_owner', 20),
            ('优先级', 'priority', 10),
            ('状态', 'status', 10),
            ('执行者', 'executor_name', 15),
            ('备注', 'remarks', 30)
        ]
        
        for i, (label_text, field_name, width) in enumerate(info_fields):
            row_frame = tk.Frame(self.info_scrollable_frame if self.scroll_frame_active else self.info_container, bg='white')
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
    
    def _bind_resize_events(self):
        """绑定窗口大小变化事件"""
        # 绑定主窗口大小变化事件
        self.parent.bind('<Configure>', self._on_window_resize)
        self.detail_right_frame.bind('<Configure>', self._on_frame_resize)
        
        # 绑定主框架大小变化事件
        self.main_frame.bind('<Configure>', self._on_main_frame_resize)
        
        # 绑定详情框架大小变化事件
        self.detail_frame.bind('<Configure>', self._on_detail_frame_resize)
    
    def _on_window_resize(self, event):
        """窗口大小变化事件处理"""
        # 只有当事件来源是主窗口时才处理
        if event.widget == self.parent:
            # 延迟检查，避免频繁更新
            self.parent.after(100, self._check_and_update_scroll_frame)
    
    def _on_frame_resize(self, event):
        """框架大小变化事件处理"""
        # 只有当事件来源是详情右侧框架时才处理
        if event.widget == self.detail_right_frame:
            # 延迟检查，避免频繁更新
            self.parent.after(100, self._check_and_update_scroll_frame)
    
    def _on_main_frame_resize(self, event):
        """主框架大小变化事件处理"""
        # 只有当事件来源是主框架时才处理
        if event.widget == self.main_frame:
            # 延迟检查，避免频繁更新
            self.parent.after(150, self._check_and_update_scroll_frame)
    
    def _on_detail_frame_resize(self, event):
        """详情框架大小变化事件处理"""
        # 只有当事件来源是详情框架时才处理
        if event.widget == self.detail_frame:
            # 延迟检查，避免频繁更新
            self.parent.after(120, self._check_and_update_scroll_frame)
    
    def _check_and_update_scroll_frame(self):
        """检查并更新滚动框架状态"""
        try:
            # 获取当前框架尺寸
            frame_width = self.detail_right_frame.winfo_width()
            frame_height = self.detail_right_frame.winfo_height()
            
            # 如果框架还没有初始化，跳过
            if frame_width <= 1 or frame_height <= 1:
                return
            
            # 估算内容所需的高度
            estimated_content_height = self._estimate_content_height()
            
            # 判断是否需要滚动框架
            needs_scroll = estimated_content_height > frame_height - 50  # 预留50像素的边距
            
            print(f"[DEBUG] 框架尺寸: {frame_width}x{frame_height}, 估算内容高度: {estimated_content_height}, 需要滚动: {needs_scroll}")
            
            # 如果滚动状态需要改变
            if needs_scroll != self.scroll_frame_active:
                self._toggle_scroll_frame(needs_scroll)
                
        except Exception as e:
            print(f"[DEBUG] 检查滚动框架状态失败: {e}")
    
    def _estimate_content_height(self):
        """估算内容所需的高度"""
        try:
            # 基础高度：标题 + 边距
            base_height = 35
            
            # 第一行高度（申请人、流水号、检索按钮）
            first_row_height = 35
            
            # 其他字段高度（每个字段约35像素，包括标签和输入框）
            field_count = 7  # 项目名称、项目类型、申请人类型、著作权人、优先级、状态、执行者
            fields_height = field_count * 35
            
            # 备注字段额外高度（多行文本框，3行）
            remarks_height = 80
            
            # 额外边距和间距
            spacing_height = 20
            
            # 总高度
            total_height = base_height + first_row_height + fields_height + remarks_height + spacing_height
            
            #print(f"[DEBUG] 内容高度估算: 基础={base_height}, 第一行={first_row_height}, 字段={fields_height}, 备注={remarks_height}, 间距={spacing_height}, 总计={total_height}")
            
            return total_height
            
        except Exception as e:
            print(f"[DEBUG] 估算内容高度失败: {e}")
            return 400  # 默认高度
    
    def _toggle_scroll_frame(self, enable_scroll):
        """切换滚动框架状态"""
        try:
            print(f"[DEBUG] 切换滚动框架状态: {enable_scroll}")
            
            if enable_scroll and not self.scroll_frame_active:
                # 启用滚动框架
                self._enable_scroll_frame()
            elif not enable_scroll and self.scroll_frame_active:
                # 禁用滚动框架
                self._disable_scroll_frame()
                
        except Exception as e:
            print(f"[DEBUG] 切换滚动框架失败: {e}")
    
    def _enable_scroll_frame(self):
        """启用滚动框架"""
        try:
            print("[DEBUG] 启用滚动框架")
            
            # 清空容器
            for widget in self.info_container.winfo_children():
                widget.destroy()
            
            # 创建滚动框架
            self.info_canvas = tk.Canvas(self.info_container, bg='white')
            self.info_scrollbar = ttk.Scrollbar(self.info_container, orient='vertical', 
                                             command=self.info_canvas.yview)
            self.info_scrollable_frame = tk.Frame(self.info_canvas, bg='white')
            
            self.info_canvas.configure(yscrollcommand=self.info_scrollbar.set)
            self.info_canvas.pack(side='left', fill='both', expand=True)
            self.info_scrollbar.pack(side='right', fill='y')
            
            # 在画布中创建窗口
            self.info_canvas.create_window((0, 0), window=self.info_scrollable_frame, anchor='nw')
            
            # 绑定滚动事件
            def on_mousewheel(event):
                self.info_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
            self.info_canvas.bind("<MouseWheel>", on_mousewheel)
            self.info_scrollable_frame.bind("<MouseWheel>", on_mousewheel)
            
            # 更新状态
            self.scroll_frame_active = True
            
            # 重新创建内容
            self._create_info_content()
            
            # 更新滚动区域
            self._update_scroll_region()
            
            print("[DEBUG] 滚动框架已启用")
            
        except Exception as e:
            print(f"[DEBUG] 启用滚动框架失败: {e}")
    
    def _disable_scroll_frame(self):
        """禁用滚动框架"""
        try:
            print("[DEBUG] 禁用滚动框架")
            
            # 清空容器
            for widget in self.info_container.winfo_children():
                widget.destroy()
            
            # 销毁滚动框架组件
            if self.info_canvas:
                self.info_canvas.destroy()
                self.info_canvas = None
            if self.info_scrollbar:
                self.info_scrollbar.destroy()
                self.info_scrollbar = None
            if self.info_scrollable_frame:
                self.info_scrollable_frame.destroy()
                self.info_scrollable_frame = None
            
            # 更新状态
            self.scroll_frame_active = False
            
            # 重新创建内容（直接放在容器中）
            self._create_info_content()
            
            print("[DEBUG] 滚动框架已禁用")
            
        except Exception as e:
            print(f"[DEBUG] 禁用滚动框架失败: {e}")
    
    def _update_scroll_region(self):
        """更新滚动区域"""
        try:
            if self.info_canvas and self.info_scrollable_frame:
                # 等待框架更新
                self.info_container.update_idletasks()
                
                # 更新滚动区域
                self.info_canvas.configure(scrollregion=self.info_canvas.bbox("all"))
                
        except Exception as e:
            print(f"[DEBUG] 更新滚动区域失败: {e}")
    
    def refresh_scroll_frame(self):
        """手动刷新滚动框架状态（供外部调用）"""
        try:
            print("[DEBUG] 手动刷新滚动框架状态")
            self._check_and_update_scroll_frame()
        except Exception as e:
            print(f"[DEBUG] 手动刷新滚动框架失败: {e}")
    
    def get_scroll_frame_status(self):
        """获取当前滚动框架状态"""
        return {
            'active': self.scroll_frame_active,
            'has_canvas': self.info_canvas is not None,
            'has_scrollbar': self.info_scrollbar is not None,
            'has_scrollable_frame': self.info_scrollable_frame is not None
        }
    
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
                'software_applicant_name': project.get('software_applicant_name', ''),
                'serial_number': project.get('serial_number', ''),
                'copyright_owner': project.get('copyright_owner', ''),
                'project_name': project.get('project_name', ''),
                'project_type': project.get('project_type', ''),
                'applicant_type': project.get('applicant_type', ''),
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
            'copyright_owner': 'copyright_owner' 
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
    
    def _is_window_valid(self):
        """检查窗口是否仍然有效"""
        try:
            # 尝试访问窗口属性来检查是否仍然有效
            self.parent.winfo_exists()
            return True
        except tk.TclError:
            return False
    
    def _safe_messagebox(self, title, message, msg_type="info"):
        """安全的消息框显示，检查窗口有效性"""
        if not self._is_window_valid():
            print(f"[DEBUG] 窗口已销毁，跳过消息框: {title} - {message}")
            return
        
        try:
            if msg_type == "info":
                messagebox.showinfo(title, message)
            elif msg_type == "warning":
                messagebox.showwarning(title, message)
            elif msg_type == "error":
                messagebox.showerror(title, message)
            elif msg_type == "askyesno":
                return messagebox.askyesno(title, message)
        except tk.TclError:
            print(f"[DEBUG] 消息框显示失败，窗口可能已销毁: {title}")
            return None
    
    def _is_file_in_use(self, file_path):
        """检查文件是否正在被使用"""
        try:
            if not os.path.exists(file_path):
                return False
            
            # 检查文件是否被其他进程打开
            for proc in psutil.process_iter(['pid', 'name', 'open_files']):
                try:
                    if proc.info['open_files']:
                        for open_file in proc.info['open_files']:
                            if open_file.path == file_path:
                                return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            return False
        except Exception as e:
            print(f"[DEBUG] 检查文件使用状态失败: {e}")
            return False
    
    def _move_project_folder_to_archive(self, project_id, project_name):
        """将项目文件夹移动到归档目录"""
        try:
            # 获取项目文件夹路径
            base_path = self.default_path.get_path('project_path') or LOCAL_CONFIG.get('PROJECT_FILE_DIR', 'D:/SoftwareCopyrightMS/ProjectFile')
            source_folder = os.path.join(base_path, f"{project_id}_{project_name}")
            
            # 检查源文件夹是否存在
            if not os.path.exists(source_folder):
                print(f"[DEBUG] 项目文件夹不存在: {source_folder}")
                return True, "项目文件夹不存在，无需移动"
            
            # 检查文件夹中的文件是否被占用
            for root, dirs, files in os.walk(source_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    if self._is_file_in_use(file_path):
                        return False, f"文件正在使用中，无法移动: {file}"
            
            # 创建归档目录
            archive_base = os.path.join(os.path.dirname(base_path), "Archives")
            archive_folder = os.path.join(archive_base, f"{project_id}_{project_name}")
            
            # 确保归档目录存在
            os.makedirs(archive_base, exist_ok=True)
            
            # 如果目标文件夹已存在，添加时间戳
            if os.path.exists(archive_folder):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archive_folder = os.path.join(archive_base, f"{project_id}_{project_name}_{timestamp}")
            
            # 移动文件夹
            shutil.move(source_folder, archive_folder)
            print(f"[DEBUG] 项目文件夹已移动到归档目录: {archive_folder}")
            return True, f"项目文件夹已移动到归档目录"
            
        except Exception as e:
            print(f"[DEBUG] 移动项目文件夹失败: {e}")
            return False, f"移动项目文件夹失败: {str(e)}"
    
    def _clean_local_archived_folders(self):
        """清理本地项目文件夹中的已归档项目"""
        try:
            if not self.server_client or self.current_user.get('user_type') != 'staff':
                return
            
            # 获取服务器中的已归档项目
            ok, msg, archived_projects = self.server_client.get_archived_projects()
            if not ok:
                print(f"[DEBUG] 获取已归档项目失败: {msg}")
                return
            
            # 获取本地项目文件夹路径
            base_path = self.default_path.get_path('project_path') or LOCAL_CONFIG.get('PROJECT_FILE_DIR', 'D:/SoftwareCopyrightMS/ProjectFile')
            if not os.path.exists(base_path):
                return
            
            # 获取已归档项目的ID列表
            archived_ids = {p.get('id') for p in archived_projects}
            
            # 遍历本地项目文件夹
            moved_count = 0
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if not os.path.isdir(item_path):
                    continue
                
                # 解析文件夹名称获取项目ID
                try:
                    if '_' in item:
                        project_id = int(item.split('_')[0])
                        if project_id in archived_ids:
                            # 找到对应的项目信息
                            project_info = next((p for p in archived_projects if p.get('id') == project_id), None)
                            if project_info:
                                project_name = project_info.get('project_name', '')
                                success, message = self._move_project_folder_to_archive(project_id, project_name)
                                if success:
                                    moved_count += 1
                                    print(f"[DEBUG] 自动清理归档项目文件夹: {item}")
                                else:
                                    print(f"[DEBUG] 清理失败: {message}")
                except (ValueError, IndexError):
                    continue
            
            if moved_count > 0:
                print(f"[DEBUG] 自动清理完成，移动了 {moved_count} 个项目文件夹到归档目录")
                
        except Exception as e:
            print(f"[DEBUG] 自动清理归档文件夹失败: {e}")
            import traceback
            traceback.print_exc()
    

    def open_copyright_center(self):
        """打开国家版权保护中心网站"""
        try:
            # 检测是否安装了Playwright
            from desktop_app.serial_fetcher_simple import is_playwright_available
            
            if is_playwright_available() and self.use_playwright_browser.get():
                # 使用Playwright打开版权中心
                self._open_copyright_center_with_playwright()
            else:
                # 使用默认浏览器打开
                import webbrowser
                url = "https://register.ccopyright.com.cn/login.html"
                webbrowser.open(url)
                
        except Exception as e:
            self._safe_messagebox("错误", f"打开版权保护中心失败: {str(e)}", "error")
    
    def _open_copyright_center_with_playwright(self):
        """使用Playwright打开版权保护中心"""
        try:
            print("[DEBUG] 开始_open_copyright_center_with_playwright方法")
            
            from playwright.sync_api import sync_playwright
            from desktop_app.serial_fetcher_simple import get_valid_global_browser, set_global_browser, is_browser_instance_valid
            
            # 检查是否已有有效的浏览器实例
            print("[DEBUG] 检查有效的全局浏览器实例")
            context, page, instance, playwright_instance = get_valid_global_browser()
            print(f"[DEBUG] 浏览器实例检查结果: context={bool(context)}, page={bool(page)}, instance={bool(instance)}")
            
            if context and page and instance:
                # 复用现有浏览器实例
                print("[DEBUG] 复用现有浏览器实例打开版权中心")
                try:
                    # 检查浏览器实例是否仍然有效
                    if not is_browser_instance_valid(context, page, instance):
                        print("[DEBUG] 浏览器实例已失效，清除并重新创建")
                        from desktop_app.serial_fetcher_simple import clear_global_browser
                        clear_global_browser()
                        # 递归调用创建新实例
                        print("[DEBUG] 递归调用_open_copyright_center_with_playwright")
                        self._open_copyright_center_with_playwright()
                        return
                    
                    # 尝试导航到目标页面
                    print("[DEBUG] 导航到版权保护中心")
                    page.goto("https://register.ccopyright.com.cn/login.html", wait_until='domcontentloaded', timeout=60000)
                    page.wait_for_load_state('networkidle', timeout=10000)
                    print("[DEBUG] 页面网络空闲")
                    
                    # 立即自动填充账号密码（如果已保存）
                    try:
                        print("[DEBUG] 检查是否有保存的账号密码")
                        from desktop_app.credential_manager import load_credentials, has_credentials
                        
                        if has_credentials():
                            print("[DEBUG] 发现保存的账号密码，立即开始自动填充")
                            username, password = load_credentials()
                            
                            # 等待0.5秒后立即填充
                            page.wait_for_timeout(500)
                            
                            # 尝试多种可能的用户名输入框选择器
                            username_selectors = [
                                'input[placeholder*="请输入用户名/手机号/邮箱"]'
                            ]
                            
                            username_filled = False
                            for selector in username_selectors:
                                try:
                                    page.wait_for_selector(selector, timeout=1000)
                                    page.fill(selector, username)
                                    print(f"[DEBUG] 用户名已填充到: {selector}")
                                    username_filled = True
                                    break
                                except Exception:
                                    continue
                            
                            if not username_filled:
                                print("[DEBUG] 未找到用户名输入框")
                            
                            # 尝试多种可能的密码输入框选择器
                            password_selectors = [
                                'input[placeholder*="请输入密码"]'
                            ]
                            
                            password_filled = False
                            for selector in password_selectors:
                                try:
                                    page.wait_for_selector(selector, timeout=1000)
                                    page.fill(selector, password)
                                    print(f"[DEBUG] 密码已填充到: {selector}")
                                    password_filled = True
                                    break
                                except Exception:
                                    continue
                            
                            if not password_filled:
                                print("[DEBUG] 未找到密码输入框")
                            
                            if username_filled and password_filled:
                                print("[DEBUG] 账号密码自动填充完成")
                            else:
                                print("[DEBUG] 自动填充部分失败，请手动输入")
                                
                        else:
                            print("[DEBUG] 没有保存的账号密码，请手动输入")
                            
                    except Exception as e:
                        print(f"[DEBUG] 自动填充功能出错: {e}")
                        print("[DEBUG] 请手动输入账号密码")
                    
                    self._safe_messagebox("提示", "已在现有浏览器中打开版权保护中心", "info")
                except Exception as e:
                    print(f"[DEBUG] 复用浏览器实例失败: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # 检查是否是浏览器被关闭的错误
                    if "Target page, context or browser has been closed" in str(e):
                        print("[DEBUG] 检测到浏览器被关闭，清除实例并重新创建")
                        from desktop_app.serial_fetcher_simple import clear_global_browser
                        clear_global_browser()
                        # 递归调用创建新实例
                        print("[DEBUG] 递归调用_open_copyright_center_with_playwright")
                        self._open_copyright_center_with_playwright()
                        return
                    else:
                        # 其他错误，回退到默认浏览器
                        print("[DEBUG] 其他错误，回退到默认浏览器")
                        import webbrowser
                        url = "https://register.ccopyright.com.cn/login.html"
                        webbrowser.open(url)
                        self._safe_messagebox("提示", f"Playwright打开失败，已使用默认浏览器打开\n\n错误: {str(e)}", "warning")
                        return
            else:
                print("[DEBUG] 没有保存的浏览器实例")
                # 创建新的浏览器实例 - 不使用with语句避免自动关闭
                print("[DEBUG] 创建新浏览器实例打开版权中心")
                
                # 手动启动Playwright实例，不使用with语句
                print("[DEBUG] 启动Playwright实例")
                p = sync_playwright().start()
                print("[DEBUG] Playwright实例启动完成")
                
                # 获取屏幕尺寸
                import tkinter as tk
                try:
                    print("[DEBUG] 创建临时Tkinter根窗口以获取屏幕尺寸")
                    root = tk.Tk()
                    screen_width = root.winfo_screenwidth()
                    screen_height = root.winfo_screenheight()
                    print(f"[DEBUG] 屏幕尺寸: {screen_width}x{screen_height}")
                    root.destroy()
                    print("[DEBUG] 临时Tkinter根窗口已销毁")
                except Exception as e:
                    print(f"[DEBUG] 获取屏幕尺寸失败: {e}")
                    screen_width = 1920
                    screen_height = 1080
                
                # 启动浏览器（不使用持久化上下文）
                print("[DEBUG] 启动Chromium浏览器")
                
                browser = p.chromium.launch(
                    headless=False,
                    args=[
                        '--start-maximized',
                        '--no-sandbox',
                        '--disable-web-security',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-first-run',
                    ]
                )
                print("[DEBUG] Chromium浏览器启动完成")
                
                # 创建新的上下文
                print("[DEBUG] 创建浏览器上下文")
                context = browser.new_context(
                    viewport={'width': screen_width, 'height': screen_height},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='zh-CN',
                    timezone_id='Asia/Shanghai',
                )
                print("[DEBUG] 浏览器上下文创建完成")
                
                # 创建新页面
                print("[DEBUG] 创建新页面")
                page = context.new_page()
                print("[DEBUG] 新页面创建完成")
                
                # 设置页面视口为全屏
                print("[DEBUG] 设置页面视口")
                page.set_viewport_size({'width': screen_width, 'height': screen_height})
                print("[DEBUG] 页面视口设置完成")
                
                # 添加增强的反检测脚本
                print("[DEBUG] 注入反检测脚本")
                try:
                    page.evaluate("""
                        (function() {
                            // 1. 隐藏webdriver特征
                            Object.defineProperty(navigator, 'webdriver', {
                                get: () => undefined,
                            });
                            
                            // 2. 隐藏自动化控制特征
                            delete window.chrome;
                            window.chrome = {
                                runtime: {},
                                loadTimes: function() {},
                                csi: function() {},
                                app: {}
                            };
                            
                            // 3. 模拟真实的插件
                            Object.defineProperty(navigator, 'plugins', {
                                get: () => {
                                    return [
                                        {
                                            0: {type: "application/x-google-chrome-pdf", suffixes: "pdf", description: "Portable Document Format", enabledPlugin: Plugin},
                                            description: "Portable Document Format",
                                            filename: "internal-pdf-viewer",
                                            length: 1,
                                            name: "Chrome PDF Plugin"
                                        },
                                        {
                                            0: {type: "application/pdf", suffixes: "pdf", description: "", enabledPlugin: Plugin},
                                            description: "",
                                            filename: "mhjfbmdgcfjbbpaeojofohoefgiehjai",
                                            length: 1,
                                            name: "Chrome PDF Viewer"
                                        },
                                        {
                                            0: {type: "application/x-nacl", suffixes: "", description: "Native Client Executable", enabledPlugin: Plugin},
                                            1: {type: "application/x-pnacl", suffixes: "", description: "Portable Native Client Executable", enabledPlugin: Plugin},
                                            description: "",
                                            filename: "internal-nacl-plugin",
                                            length: 2,
                                            name: "Native Client"
                                        }
                                    ];
                                },
                            });
                            
                            // 4. 模拟真实的语言设置
                            Object.defineProperty(navigator, 'languages', {
                                get: () => ['zh-CN', 'zh', 'en'],
                            });
                            
                            // 5. 隐藏自动化相关属性
                            Object.defineProperty(navigator, 'permissions', {
                                get: () => ({
                                    query: () => Promise.resolve({ state: 'granted' })
                                }),
                            });
                            
                            // 6. 模拟真实的屏幕信息
                            Object.defineProperty(screen, 'availHeight', {
                                get: () => 1040,
                            });
                            Object.defineProperty(screen, 'availWidth', {
                                get: () => 1920,
                            });
                            Object.defineProperty(screen, 'colorDepth', {
                                get: () => 24,
                            });
                            Object.defineProperty(screen, 'height', {
                                get: () => 1080,
                            });
                            Object.defineProperty(screen, 'width', {
                                get: () => 1920,
                            });
                            
                            // 7. 隐藏自动化痕迹
                            Object.defineProperty(navigator, 'platform', {
                                get: () => 'Win32',
                            });
                            
                            // 8. 模拟真实的连接信息
                            Object.defineProperty(navigator, 'connection', {
                                get: () => ({
                                    effectiveType: '4g',
                                    rtt: 50,
                                    downlink: 10,
                                    saveData: false
                                }),
                            });
                            
                            // 9. 隐藏自动化相关的window属性
                            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
                            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
                            delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
                            
                            // 10. 模拟真实的硬件并发数
                            Object.defineProperty(navigator, 'hardwareConcurrency', {
                                get: () => 8,
                            });
                            
                            // 11. 模拟真实的设备内存
                            Object.defineProperty(navigator, 'deviceMemory', {
                                get: () => 8,
                            });
                            
                            // 12. 隐藏自动化相关的document属性
                            Object.defineProperty(document, 'hidden', {
                                get: () => false,
                            });
                            
                            // 13. 模拟真实的时区
                            Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
                                value: function() {
                                    return {
                                        locale: 'zh-CN',
                                        timeZone: 'Asia/Shanghai',
                                        calendar: 'gregory',
                                        numberingSystem: 'latn'
                                    };
                                }
                            });
                            
                            // 14. 隐藏自动化相关的CSS媒体查询
                            const originalMatchMedia = window.matchMedia;
                            window.matchMedia = function(query) {
                                if (query.includes('prefers-reduced-motion')) {
                                    return { matches: false, media: query };
                                }
                                return originalMatchMedia.call(this, query);
                            };
                            
                            // 15. 模拟真实的触摸支持
                            Object.defineProperty(navigator, 'maxTouchPoints', {
                                get: () => 0,
                            });
                            
                            // 16. 隐藏自动化相关的错误处理
                            const originalConsoleError = console.error;
                            console.error = function(...args) {
                                const message = args.join(' ');
                                if (message.includes('webdriver') || 
                                    message.includes('automation') || 
                                    message.includes('selenium')) {
                                    return;
                                }
                                originalConsoleError.apply(console, args);
                            };
                            
                            // 17. 模拟真实的Canvas指纹
                            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
                            HTMLCanvasElement.prototype.toDataURL = function() {
                                const context = this.getContext('2d');
                                if (context) {
                                    context.fillStyle = 'rgba(255, 255, 255, 0.1)';
                                    context.fillRect(0, 0, 1, 1);
                                }
                                return originalToDataURL.apply(this, arguments);
                            };
                            
                            // 18. 隐藏自动化相关的WebGL指纹
                            const originalGetParameter = WebGLRenderingContext.prototype.getParameter;
                            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                                if (parameter === 37445) { // UNMASKED_VENDOR_WEBGL
                                    return 'Intel Inc.';
                                }
                                if (parameter === 37446) { // UNMASKED_RENDERER_WEBGL
                                    return 'Intel(R) HD Graphics 620';
                                }
                                return originalGetParameter.apply(this, arguments);
                            };
                            
                            // 19. 模拟真实的电池API
                            if ('getBattery' in navigator) {
                                navigator.getBattery = function() {
                                    return Promise.resolve({
                                        charging: true,
                                        chargingTime: 0,
                                        dischargingTime: Infinity,
                                        level: 0.8
                                    });
                                };
                            }
                            
                            // 20. 隐藏自动化相关的Notification API
                            if ('Notification' in window) {
                                Object.defineProperty(Notification, 'permission', {
                                    get: () => 'default',
                                });
                            }
                            
                            console.log('[DEBUG] 增强反检测脚本已注入');
                        })();
                    """)
                    print("[DEBUG] 增强反检测脚本注入成功")
                except Exception as e:
                    print(f"[DEBUG] 反检测脚本注入失败: {e}")
                    import traceback
                    traceback.print_exc()
                
                # 页面加载完成后，检查是否需要自动填充
                print("[DEBUG] 页面加载完成，检查自动填充")
                try:
                    page.evaluate("""
                        (function() {
                            console.log('[FONT-FIX] 开始增强字体修复（处理个人配置冲突）');
                            
                            // 1. 强制重置字体设置
                            function resetFontSettings() {
                                try {
                                    // 重置所有元素的字体设置
                                    const allElements = document.querySelectorAll('*');
                                    allElements.forEach(function(element) {
                                        element.style.fontFamily = '';
                                        element.style.fontSize = '';
                                        element.style.fontWeight = '';
                                        element.style.fontStyle = '';
                                    });
                                    
                                    // 重置body和html
                                    if (document.body) {
                                        document.body.style.fontFamily = '';
                                        document.body.style.fontSize = '';
                                    }
                                    if (document.documentElement) {
                                        document.documentElement.style.fontFamily = '';
                                    }
                                    
                                    console.log('[FONT-FIX] 字体设置已重置');
                                } catch (e) {
                                    console.log('[FONT-FIX] 重置字体设置失败:', e);
                                }
                            }
                            
                            // 2. 强制应用中文字体
                            function forceChineseFont() {
                                try {
                                    // 创建强力的CSS样式
                                    const style = document.createElement('style');
                                    style.id = 'enhanced-font-fix-style';
                                    style.textContent = `
                                        * {
                                            font-family: "Microsoft YaHei", "SimSun", "SimHei", "Arial", sans-serif !important;
                                            font-size: inherit !important;
                                        }
                                        body {
                                            font-family: "Microsoft YaHei", "SimSun", "SimHei", "Arial", sans-serif !important;
                                            font-size: 14px !important;
                                        }
                                        html {
                                            font-family: "Microsoft YaHei", "SimSun", "SimHei", "Arial", sans-serif !important;
                                        }
                                        div, span, p, a, li, td, th, h1, h2, h3, h4, h5, h6, label, input, button, textarea, select {
                                            font-family: "Microsoft YaHei", "SimSun", "SimHei", "Arial", sans-serif !important;
                                        }
                                    `;
                                    
                                    // 移除旧的样式
                                    const oldStyle = document.getElementById('enhanced-font-fix-style');
                                    if (oldStyle) {
                                        oldStyle.remove();
                                    }
                                    
                                    document.head.appendChild(style);
                                    
                                    // 强制设置所有元素的字体
                                    const allElements = document.querySelectorAll('*');
                                    allElements.forEach(function(element) {
                                        element.style.fontFamily = '"Microsoft YaHei", "SimSun", "SimHei", "Arial", sans-serif';
                                        element.style.fontSize = element.style.fontSize || '14px';
                                    });
                                    
                                    console.log('[FONT-FIX] 中文字体已强制应用');
                                } catch (e) {
                                    console.log('[FONT-FIX] 应用中文字体失败:', e);
                                }
                            }
                            
                            // 3. 设置页面编码
                            function setPageEncoding() {
                                try {
                                    if (!document.querySelector('meta[charset]')) {
                                        const meta = document.createElement('meta');
                                        meta.setAttribute('charset', 'UTF-8');
                                        document.head.appendChild(meta);
                                    }
                                    console.log('[FONT-FIX] 页面编码已设置');
                                } catch (e) {
                                    console.log('[FONT-FIX] 设置页面编码失败:', e);
                                }
                            }
                            
                            // 4. 执行修复流程
                            function executeFontFix() {
                                console.log('[FONT-FIX] 开始执行修复流程');
                                
                                // 步骤1：重置字体设置
                                resetFontSettings();
                                
                                // 步骤2：设置页面编码
                                setPageEncoding();
                                
                                // 步骤3：强制应用中文字体
                                setTimeout(function() {
                                    forceChineseFont();
                                }, 100);
                                
                                console.log('[FONT-FIX] 修复流程执行完成');
                            }
                            
                            // 5. 立即执行修复
                            executeFontFix();
                            
                            // 6. 页面加载后再次修复
                            if (document.readyState === 'complete') {
                                setTimeout(executeFontFix, 1000);
                            } else {
                                window.addEventListener('load', function() {
                                    setTimeout(executeFontFix, 1000);
                                });
                            }
                            
                            console.log('[FONT-FIX] 增强字体修复脚本注入成功');
                        })();
                    """)
                    print("[DEBUG] 增强字体修复脚本注入成功")
                        
                except Exception as e:
                    print(f"[DEBUG] 增强字体修复脚本注入失败: {e}")
                
                # 导航到版权中心（增加人类行为模拟）
                print("[DEBUG] 开始导航到版权中心")
                import random
                try:
                    # 增加随机延迟，模拟人类行为
                    delay = random.uniform(1, 1.5)
                    print(f"[DEBUG] 等待 {delay:.1f} 秒后导航...")
                    page.wait_for_timeout(int(delay * 1000))
                    
                    print("[DEBUG] 执行页面导航")
                    page.goto("https://register.ccopyright.com.cn/login.html", wait_until='domcontentloaded', timeout=60000)
                    print("[DEBUG] 页面加载完成")

                    page.wait_for_load_state('networkidle', timeout=10000)
                    print("[DEBUG] 页面网络空闲")
                    
                    # 立即自动填充账号密码（如果已保存）
                    try:
                        print("[DEBUG] 检查是否有保存的账号密码")
                        from desktop_app.credential_manager import load_credentials, has_credentials
                        
                        if has_credentials():
                            print("[DEBUG] 发现保存的账号密码，立即开始自动填充")
                            username, password = load_credentials()
                            
                            # 等待0.5秒后立即填充
                            page.wait_for_timeout(500)
                            
                            # 尝试多种可能的用户名输入框选择器
                            username_selectors = [
                                'input[placeholder*="请输入用户名/手机号/邮箱"]'
                            ]
                            
                            username_filled = False
                            for selector in username_selectors:
                                try:
                                    page.wait_for_selector(selector, timeout=1000)
                                    page.fill(selector, username)
                                    print(f"[DEBUG] 用户名已填充到: {selector}")
                                    username_filled = True
                                    break
                                except Exception:
                                    continue
                            
                            if not username_filled:
                                print("[DEBUG] 未找到用户名输入框")
                            
                            # 尝试多种可能的密码输入框选择器
                            password_selectors = [
                                'input[placeholder*="请输入密码"]',
                                'input[name="password"]',
                                'input[name="pwd"]',
                                'input[type="password"]',
                                'input[placeholder*="密码"]'
                            ]
                            
                            password_filled = False
                            for selector in password_selectors:
                                try:
                                    page.wait_for_selector(selector, timeout=1000)
                                    page.fill(selector, password)
                                    print(f"[DEBUG] 密码已填充到: {selector}")
                                    password_filled = True
                                    break
                                except Exception:
                                    continue
                            
                            if not password_filled:
                                print("[DEBUG] 未找到密码输入框")
                            
                            if username_filled and password_filled:
                                print("[DEBUG] 账号密码自动填充完成")
                                print("[DEBUG] 请手动点击登录按钮")
                            else:
                                print("[DEBUG] 自动填充部分失败，请手动输入")
                                
                        else:
                            print("[DEBUG] 没有保存的账号密码，请手动输入")
                            
                    except Exception as e:
                        print(f"[DEBUG] 自动填充功能出错: {e}")
                        print("[DEBUG] 请手动输入账号密码")
                    
                    # 页面加载完成后增强字体修复
                    print("[DEBUG] 页面加载完成后增强字体修复")
                    try:
                        page.evaluate("""
                            (function() {
                                console.log('[FONT-FIX] 页面加载后开始增强字体修复');
                                
                                // 强制重置字体设置
                                function resetFontSettings() {
                                    try {
                                        const allElements = document.querySelectorAll('*');
                                        allElements.forEach(function(element) {
                                            element.style.fontFamily = '';
                                            element.style.fontSize = '';
                                            element.style.fontWeight = '';
                                            element.style.fontStyle = '';
                                        });
                                        
                                        if (document.body) {
                                            document.body.style.fontFamily = '';
                                            document.body.style.fontSize = '';
                                        }
                                        if (document.documentElement) {
                                            document.documentElement.style.fontFamily = '';
                                        }
                                        
                                        console.log('[FONT-FIX] 页面加载后字体设置已重置');
                                    } catch (e) {
                                        console.log('[FONT-FIX] 页面加载后重置字体设置失败:', e);
                                    }
                                }
                                
                                // 强制应用中文字体
                                function forceChineseFont() {
                                    try {
                                        const style = document.createElement('style');
                                        style.id = 'enhanced-font-fix-style-post-load';
                                        style.textContent = `
                                            * {
                                                font-family: "Microsoft YaHei", "SimSun", "SimHei", "Arial", sans-serif !important;
                                            }
                                            body {
                                                font-family: "Microsoft YaHei", "SimSun", "SimHei", "Arial", sans-serif !important;
                                            }
                                            html {
                                                font-family: "Microsoft YaHei", "SimSun", "SimHei", "Arial", sans-serif !important;
                                            }
                                        `;
                                        
                                        document.head.appendChild(style);
                                        
                                        const allElements = document.querySelectorAll('*');
                                        allElements.forEach(function(element) {
                                            element.style.fontFamily = '"Microsoft YaHei", "SimSun", "SimHei", "Arial", sans-serif';
                                            element.style.fontSize = element.style.fontSize || '14px';
                                        });
                                        
                                        console.log('[FONT-FIX] 页面加载后中文字体已强制应用');
                                    } catch (e) {
                                        console.log('[FONT-FIX] 页面加载后应用中文字体失败:', e);
                                    }
                                }
                                
                                // 执行修复流程
                                resetFontSettings();
                                setTimeout(forceChineseFont, 100);
                                setTimeout(forceChineseFont, 500);
                                
                                console.log('[FONT-FIX] 页面加载后增强字体修复完成');
                            })();
                        """)
                        print("[DEBUG] 页面加载后增强字体修复成功")
                    except Exception as e:
                        print(f"[DEBUG] 页面加载后增强字体修复失败: {e}")
                    
                    
                except Exception as e:
                    print(f"[DEBUG] 导航失败: {e}")
                    import traceback
                    traceback.print_exc()
                    
                    # 检查是否是浏览器被关闭的错误
                    if "Target page, context or browser has been closed" in str(e):
                        print("[DEBUG] 检测到浏览器被关闭，清理实例")
                        try:
                            browser.close()
                        except:
                            pass
                        try:
                            p.stop()
                        except:
                            pass
                        # 回退到默认浏览器
                        import webbrowser
                        url = "https://register.ccopyright.com.cn/login.html"
                        webbrowser.open(url)
                        self._safe_messagebox("提示", f"浏览器被意外关闭，已使用默认浏览器打开\n\n错误: {str(e)}", "warning")
                        return
                    else:
                        # 其他错误，继续抛出
                        raise e
                
                # 保存浏览器实例和Playwright实例
                print("[DEBUG] 保存全局浏览器实例")
                set_global_browser(browser, page, browser, p)
                print("[DEBUG] 全局浏览器实例保存完成")
                
            print("[DEBUG] _open_copyright_center_with_playwright方法执行完成")
                    
        except Exception as e:
            print(f"[DEBUG] 使用Playwright打开版权中心失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 检查是否是浏览器被关闭的错误
            if "Target page, context or browser has been closed" in str(e):
                print("[DEBUG] 检测到浏览器被关闭错误，清理全局实例")
                try:
                    from desktop_app.serial_fetcher_simple import clear_global_browser
                    clear_global_browser()
                except:
                    pass
                # 回退到默认浏览器
                import webbrowser
                url = "https://register.ccopyright.com.cn/login.html"
                webbrowser.open(url)
                self._safe_messagebox("提示", f"浏览器被意外关闭，已使用默认浏览器打开\n\n错误: {str(e)}", "warning")
            else:
                # 其他错误，回退到默认浏览器
                import webbrowser
                url = "https://register.ccopyright.com.cn/login.html"
                webbrowser.open(url)
                self._safe_messagebox("提示", f"Playwright打开失败，已使用默认浏览器打开\n\n错误: {str(e)}", "warning")
    
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
                
                # 自动清理本地项目文件夹中的已归档项目
                self._clean_local_archived_folders()
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
            self._safe_messagebox("警告", "请先选择一个项目", "warning")
            return
        
        try:
            project_id = self.selected_project.get('id')
            
            # 更新本地数据库
            self.local_project.update_project_status(project_id, '执行中')
            
            # 更新服务器数据库
            server_updated = False
            if self.server_client and hasattr(self.server_client, 'update_project_status'):
                try:
                    ok, msg = self.server_client.update_project_status(project_id, '执行中')
                    server_updated = bool(ok)
                    if not ok:
                        print(f"[DEBUG] 服务器状态更新失败: {msg}")
                except Exception as e:
                    print(f"[DEBUG] 服务器状态更新异常: {e}")
                    server_updated = False
            
            # 更新UI显示
            self.refresh_projects()
            
            # 显示结果
            if server_updated:
                self._safe_messagebox("成功", "项目状态已更新为执行中（已同步到服务器）", "info")
            else:
                self._safe_messagebox("成功", "项目状态已更新为执行中（本地更新成功，服务器同步失败）", "info")
                
        except Exception as e:
            print(f"[DEBUG] 标记执行中失败: {e}")
            import traceback
            traceback.print_exc()
            self._safe_messagebox("错误", f"更新项目状态失败: {str(e)}", "error")
    
    def mark_as_charged(self):
        """标记为收费"""
        if not self.selected_project:
            self._safe_messagebox("警告", "请先选择一个项目", "warning")
            return
        
        try:
            project_id = self.selected_project.get('id')
            
            # 更新服务器数据库（收费标记）
            server_updated = False
            if self.server_client and hasattr(self.server_client, 'settle_project'):
                try:
                    ok, msg = self.server_client.settle_project(project_id)
                    server_updated = bool(ok)
                    if not ok:
                        print(f"[DEBUG] 服务器收费标记失败: {msg}")
                        self._safe_messagebox("错误", f"收费标记失败: {msg}", "error")
                        return
                except Exception as e:
                    print(f"[DEBUG] 服务器收费标记异常: {e}")
                    self._safe_messagebox("错误", f"收费标记失败: {str(e)}", "error")
                    return
            
            # 更新本地数据库
            try:
                # 更新本地项目的收费状态
                self.local_project.update_project_settled(project_id, True)
            except Exception as e:
                print(f"[DEBUG] 本地收费状态更新失败: {e}")
            
            # 更新UI显示
            self.refresh_projects()
            
            # 显示结果
            if server_updated:
                self._safe_messagebox("成功", "项目已标记为收费（已同步到服务器）", "info")
            else:
                self._safe_messagebox("成功", "项目已标记为收费（本地更新成功，服务器同步失败）", "info")
                
        except Exception as e:
            print(f"[DEBUG] 标记收费失败: {e}")
            import traceback
            traceback.print_exc()
            self._safe_messagebox("错误", f"更新项目收费状态失败: {str(e)}", "error")
    
    def mark_as_archived(self):
        """标记为归档"""
        if not self.selected_project:
            self._safe_messagebox("警告", "请先选择一个项目", "warning")
            return
        
        try:
            project_id = self.selected_project.get('id')
            
            # 检查项目是否已收费
            project_data = self.local_project.get_project_by_id(project_id)
            if project_data and not project_data.get('is_settled', False):
                self._safe_messagebox("警告", "项目尚未收费，无法归档\n\n请先标记为收费", "warning")
                return
            
            # 确认归档操作
            result = self._safe_messagebox(
                "确认归档", 
                f"确定要归档项目：{self.selected_project.get('project_name', '未知项目')}？\n\n"
                f"归档后项目将从活动列表移动到归档列表，此操作不可撤销。",
                "askyesno"
            )
            
            if not result:
                return
            
            # 更新服务器数据库（归档操作）
            server_updated = False
            if self.server_client and hasattr(self.server_client, 'archive_project'):
                try:
                    ok, msg = self.server_client.archive_project(project_id)
                    server_updated = bool(ok)
                    if not ok:
                        print(f"[DEBUG] 服务器归档失败: {msg}")
                        self._safe_messagebox("错误", f"归档失败: {msg}", "error")
                        return
                except Exception as e:
                    print(f"[DEBUG] 服务器归档异常: {e}")
                    self._safe_messagebox("错误", f"归档失败: {str(e)}", "error")
                    return
            
            # 移动项目文件夹到归档目录
            if server_updated:
                project_name = self.selected_project.get('project_name', '')
                success, message = self._move_project_folder_to_archive(project_id, project_name)
                if not success:
                    print(f"[DEBUG] 文件移动失败: {message}")
                    self._safe_messagebox("警告", f"服务器归档成功，但文件移动失败: {message}", "warning")
            
            # 更新本地数据库
            try:
                # 从本地数据库中删除项目（因为已归档）
                self.local_project.delete_project(project_id)
            except Exception as e:
                print(f"[DEBUG] 本地项目删除失败: {e}")
            
            # 清空选中项目
            self.selected_project = None
            
            # 更新UI显示
            self.refresh_projects()
            
            # 显示结果
            if server_updated:
                self._safe_messagebox("成功", "项目已归档（已同步到服务器）", "info")
            else:
                self._safe_messagebox("成功", "项目已归档（本地更新成功，服务器同步失败）", "info")
                
        except Exception as e:
            print(f"[DEBUG] 归档失败: {e}")
            import traceback
            traceback.print_exc()
            self._safe_messagebox("错误", f"归档项目失败: {str(e)}", "error")
    
    def mark_as_completed(self):
        """标记为已完成"""
        if not self.selected_project:
            self._safe_messagebox("警告", "请先选择一个项目", "warning")
            return
        
        try:
            project_id = self.selected_project.get('id')
            
            # 更新本地数据库
            self.local_project.update_project_status(project_id, '已完成')
            
            # 更新服务器数据库
            server_updated = False
            if self.server_client and hasattr(self.server_client, 'update_project_status'):
                try:
                    ok, msg = self.server_client.update_project_status(project_id, '已完成')
                    server_updated = bool(ok)
                    if not ok:
                        print(f"[DEBUG] 服务器状态更新失败: {msg}")
                except Exception as e:
                    print(f"[DEBUG] 服务器状态更新异常: {e}")
                    server_updated = False
            
            # 更新UI显示
            self.refresh_projects()
            
            # 显示结果
            if server_updated:
                self._safe_messagebox("成功", "项目状态已更新为已完成（已同步到服务器）", "info")
            else:
                self._safe_messagebox("成功", "项目状态已更新为已完成（本地更新成功，服务器同步失败）", "info")
                
        except Exception as e:
            print(f"[DEBUG] 标记已完成失败: {e}")
            import traceback
            traceback.print_exc()
            self._safe_messagebox("错误", f"更新项目状态失败: {str(e)}", "error")
    
    def fetch_serial_number(self):
        """获取流水号 - 支持浏览器实例检测和复用"""
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
            
            # 2) 检测是否已有浏览器实例
            from desktop_app.serial_fetcher_simple import get_valid_global_browser, is_playwright_available
            
            if not is_playwright_available():
                self._safe_messagebox("错误", "系统未安装Playwright，无法自动获取流水号\n\n请先安装Playwright：\npip install playwright\nplaywright install", "error")
                return
            
            context, page, instance, playwright_instance = get_valid_global_browser()
            
            if context and page and instance:
                # 已有浏览器实例，检查是否已登录版权中心
                print("[DEBUG] 检测到现有浏览器实例")
                
                # 检查当前页面是否在版权中心
                try:
                    current_url = page.url
                    if 'ccopyright.com.cn' in current_url:
                        # 已在版权中心，检查登录状态
                        from desktop_app.serial_fetcher_simple import _check_login_status
                        is_logged_in = _check_login_status(page)
                        
                        if is_logged_in:
                            # 已登录，直接获取流水号
                            print("[DEBUG] 检测到已登录版权中心，直接获取流水号")
                            serial = fetch_serial_for_project(project_name, applicant_name, reuse_browser=True, use_temp_profile=True)
                        else:
                            # 未登录，提示用户登录
                            print("[DEBUG] 检测到未登录版权中心")
                            result = self._safe_messagebox(
                                "登录确认", 
                                f"检测到浏览器已打开版权中心但未登录\n\n"
                                f"请完成以下步骤：\n"
                                f"1. 在浏览器中登录版权中心\n"
                                f"2. 进入软件登记页面\n"
                                f"3. 点击'是'开始搜索项目：{project_name}\n"
                                f"4. 点击'否'取消操作",
                                "askyesno"
                            )
                            if result:
                                serial = fetch_serial_for_project(project_name, applicant_name, reuse_browser=True, use_temp_profile=True)
                            else:
                                return
                    else:
                        # 不在版权中心，导航到版权中心
                        print("[DEBUG] 浏览器不在版权中心，导航到版权中心")
                        result = self._safe_messagebox(
                            "导航确认", 
                            f"检测到浏览器已打开但不在版权中心\n\n"
                            f"是否导航到版权中心并登录？\n\n"
                            f"点击'是'：导航到版权中心\n"
                            f"点击'否'：取消操作",
                            "askyesno"
                        )
                        if result:
                            # 导航到版权中心
                            page.goto("https://register.ccopyright.com.cn/login.html", wait_until='domcontentloaded', timeout=60000)
                            page.wait_for_load_state('networkidle', timeout=30000)
                            
                            # 提示用户登录
                            self._safe_messagebox(
                                "登录提示", 
                                f"已导航到版权中心\n\n"
                                f"请完成以下步骤：\n"
                                f"1. 在浏览器中登录版权中心\n"
                                f"2. 进入软件登记页面\n"
                                f"3. 然后再次点击'获取流水号'按钮",
                                "info"
                            )
                            return
                        else:
                            return
                except Exception as e:
                    print(f"[DEBUG] 使用现有浏览器实例失败: {e}")
                    # 清除失效的实例并创建新的
                    from desktop_app.serial_fetcher_simple import clear_global_browser
                    clear_global_browser()
                    # 创建新实例并获取流水号
                    serial = fetch_serial_for_project(project_name, applicant_name, reuse_browser=False, use_temp_profile=True)
                    if not serial:
                        self._safe_messagebox(
                            "获取流水号",
                            f"未找到项目'{project_name}'的流水号\n\n请确认：\n1. 项目名称是否正确\n2. 项目是否已在版权中心登记\n3. 是否在正确的页面（软件登记）",
                            "warning"
                        )
                        return
                    
                    # 更新UI和数据库
                    if 'serial_number' in self.info_entries:
                        try:
                            self.info_entries['serial_number'].delete(0, tk.END)
                            self.info_entries['serial_number'].insert(0, str(serial))
                        except Exception:
                            pass
                    
                    try:
                        self.selected_project['serial_number'] = serial
                    except Exception:
                        pass
                    
                    server_updated = False
                    if self.server_client and hasattr(self.server_client, 'update_project_serial'):
                        try:
                            ok, msg = self.server_client.update_project_serial(project_id, serial)
                            server_updated = bool(ok)
                        except Exception:
                            traceback.print_exc()
                            server_updated = False
                    
                    if server_updated:
                        self._safe_messagebox("获取流水号", f"流水号已获取并同步：{serial}", "info")
                    else:
                        self._safe_messagebox(
                            "获取流水号",
                            f"流水号已获取并回填：{serial}。服务器同步未完成或接口不可用，可稍后再试。",
                            "info"
                        )
                    return
            else:
                # 没有浏览器实例，创建新的
                print("[DEBUG] 没有现有浏览器实例，创建新的")
                serial = fetch_serial_for_project(project_name, applicant_name, reuse_browser=False, use_temp_profile=True)
            
            # 3) 处理获取结果
            if not serial:
                self._safe_messagebox(
                    "获取流水号",
                    f"未找到项目'{project_name}'的流水号\n\n请确认：\n1. 项目名称是否正确\n2. 项目是否已在版权中心登记\n3. 是否在正确的页面（软件登记）",
                    "warning"
                )
                return

            # 4) 回填到界面
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
            
            # 5) 更新到服务器（如可用）
            server_updated = False
            if self.server_client and hasattr(self.server_client, 'update_project_serial'):
                try:
                    ok, msg = self.server_client.update_project_serial(project_id, serial)
                    server_updated = bool(ok)
                except Exception:
                    traceback.print_exc()
                    server_updated = False
            
            # 6) 结果提示
            if server_updated:
                self._safe_messagebox("获取流水号", f"流水号已获取并同步：{serial}", "info")
            else:
                self._safe_messagebox(
                    "获取流水号",
                    f"流水号已获取并回填：{serial}。服务器同步未完成或接口不可用，可稍后再试。",
                    "info"
                )
        except Exception as e:
            traceback.print_exc()
            self._safe_messagebox("错误", f"获取流水号失败: {str(e)}", "error")
