#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dialog窗口模块
根据需求分析文档设计：身份证、证书、合同Dialog窗口
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os


class BaseDialog:
    """基础Dialog类"""
    
    def __init__(self, parent, title, width=800, height=600):
        self.parent = parent
        self.selected_file = None
        
        # 创建对话框
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{width}x{height}")
        self.dialog.resizable(True, True)
        
        # 设置模态
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 居中显示
        self.center_window()
        
        # 创建界面
        self.create_interface()
    
    def center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_interface(self):
        """创建界面（子类实现）"""
        pass


class IDCardDialog(BaseDialog):
    """身份证复印件Dialog"""
    
    def __init__(self, parent, id_card_file, selected_project):
        self.id_card_file = id_card_file
        self.selected_project = selected_project
        super().__init__(parent, "身份证复印件管理", 900, 600)
    
    def create_interface(self):
        """创建身份证复印件界面"""
        # 主框架
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建三个分栏
        self.create_left_panel(main_frame)
        self.create_middle_panel(main_frame)
        self.create_right_panel(main_frame)
        
        # 加载数据
        self.load_data()
    
    def create_left_panel(self, parent):
        """创建左侧面板 - 所有身份证文件列表"""
        # 左侧框架
        left_frame = tk.Frame(parent, bg='white', width=300)
        left_frame.pack(side='left', fill='y', padx=(0, 5))
        left_frame.pack_propagate(False)
        
        # 标题
        tk.Label(left_frame, text="所有身份证文件", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        # 文件树
        tree_frame = tk.Frame(left_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        self.all_files_tree = ttk.Treeview(tree_frame, columns=('姓名', '身份证号'), show='tree headings')
        self.all_files_tree.heading('#0', text='ID')
        self.all_files_tree.heading('姓名', text='姓名')
        self.all_files_tree.heading('身份证号', text='身份证号')
        
        self.all_files_tree.column('#0', width=50)
        self.all_files_tree.column('姓名', width=100)
        self.all_files_tree.column('身份证号', width=120)
        
        # 滚动条
        scrollbar1 = ttk.Scrollbar(tree_frame, orient='vertical', command=self.all_files_tree.yview)
        self.all_files_tree.configure(yscrollcommand=scrollbar1.set)
        
        self.all_files_tree.pack(side='left', fill='both', expand=True)
        scrollbar1.pack(side='right', fill='y')
        
        # 绑定选择事件
        self.all_files_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        self.all_files_tree.bind('<Double-1>', self.on_file_double_click)
    
    def create_middle_panel(self, parent):
        """创建中间面板 - 最近添加的10个文件"""
        # 中间框架
        middle_frame = tk.Frame(parent, bg='white', width=300)
        middle_frame.pack(side='left', fill='y', padx=5)
        middle_frame.pack_propagate(False)
        
        # 标题
        tk.Label(middle_frame, text="最近添加的文件", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        # 文件树
        tree_frame = tk.Frame(middle_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        self.recent_files_tree = ttk.Treeview(tree_frame, columns=('姓名', '身份证号'), show='tree headings')
        self.recent_files_tree.heading('#0', text='ID')
        self.recent_files_tree.heading('姓名', text='姓名')
        self.recent_files_tree.heading('身份证号', text='身份证号')
        
        self.recent_files_tree.column('#0', width=50)
        self.recent_files_tree.column('姓名', width=100)
        self.recent_files_tree.column('身份证号', width=120)
        
        # 滚动条
        scrollbar2 = ttk.Scrollbar(tree_frame, orient='vertical', command=self.recent_files_tree.yview)
        self.recent_files_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.recent_files_tree.pack(side='left', fill='both', expand=True)
        scrollbar2.pack(side='right', fill='y')
        
        # 绑定选择事件
        self.recent_files_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        self.recent_files_tree.bind('<Double-1>', self.on_file_double_click)
    
    def create_right_panel(self, parent):
        """创建右侧面板 - 文件详情"""
        # 右侧框架
        right_frame = tk.Frame(parent, bg='white')
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        # 标题
        tk.Label(right_frame, text="文件详情", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        # 详情表单
        self.create_detail_form(right_frame)
        
        # 按钮框架
        button_frame = tk.Frame(right_frame, bg='white')
        button_frame.pack(side='bottom', fill='x', pady=(10, 0))
        
        tk.Button(button_frame, text="确定", 
                 font=('Microsoft YaHei', 10), bg='#3182ce', fg='white',
                 command=self.confirm_selection).pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="取消", 
                 font=('Microsoft YaHei', 10), bg='#d69e2e', fg='white',
                 command=self.cancel_selection).pack(side='left')
    
    def create_detail_form(self, parent):
        """创建详情表单"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill='both', expand=True)
        
        # 表单字段
        fields = [
            ('姓名', 'person_name'),
            ('性别', 'gender'),
            ('籍贯', 'birthplace'),
            ('身份证号', 'id_number'),
            ('备注', 'remarks')
        ]
        
        self.form_vars = {}
        for i, (label, field) in enumerate(fields):
            # 标签
            tk.Label(form_frame, text=f"{label}:", 
                    font=('Microsoft YaHei', 10), bg='white').grid(
                row=i, column=0, sticky='w', padx=(0, 10), pady=8)
            
            # 输入框
            if field == 'gender':
                var = tk.StringVar()
                combo = ttk.Combobox(form_frame, textvariable=var,
                                   values=['男', '女'], state='readonly',
                                   font=('Microsoft YaHei', 9), width=30)
                self.form_vars[field] = (var, combo)
                combo.grid(row=i, column=1, sticky='ew', pady=8)
            elif field == 'remarks':
                var = tk.StringVar()
                entry = tk.Text(form_frame, width=30, height=3, 
                               font=('Microsoft YaHei', 9), wrap='word')
                self.form_vars[field] = (var, entry)
            else:
                var = tk.StringVar()
                entry = tk.Entry(form_frame, textvariable=var, 
                                font=('Microsoft YaHei', 9), width=30)
                self.form_vars[field] = (var, entry)
                entry.grid(row=i, column=1, sticky='ew', pady=8)
        
        # 配置列权重
        form_frame.columnconfigure(1, weight=1)
    
    def load_data(self):
        """加载数据"""
        # 加载所有文件
        all_files = self.id_card_file.get_all_files()
        for file in all_files:
            self.all_files_tree.insert('', 'end', text=file[0], values=(file[2] or '', file[5] or ''))
        
        # 加载最近文件
        recent_files = self.id_card_file.get_recent_files(10)
        for file in recent_files:
            self.recent_files_tree.insert('', 'end', text=file[0], values=(file[2] or '', file[5] or ''))
    
    def on_file_select(self, event):
        """文件选择事件"""
        # 获取选中的文件ID
        file_id = None
        if event.widget == self.all_files_tree:
            selection = self.all_files_tree.selection()
            if selection:
                file_id = self.all_files_tree.item(selection[0])['text']
        elif event.widget == self.recent_files_tree:
            selection = self.recent_files_tree.selection()
            if selection:
                file_id = self.recent_files_tree.item(selection[0])['text']
        
        if file_id:
            # 加载文件详情
            file_data = self.id_card_file.get_file_by_id(file_id)
            if file_data:
                self.load_file_details(file_data)
    
    def load_file_details(self, file_data):
        """加载文件详情"""
        # 填充表单
        fields = ['person_name', 'gender', 'birthplace', 'id_number', 'remarks']
        for i, field in enumerate(fields):
            if i + 2 < len(file_data):  # 跳过ID和文件名
                var, entry = self.form_vars[field]
                value = file_data[i + 2] or ''
                
                if field == 'remarks':
                    entry.delete(1.0, tk.END)
                    entry.insert(1.0, value)
                else:
                    var.set(value)
    
    def on_file_double_click(self, event):
        """文件双击事件"""
        # 获取选中的文件
        file_id = None
        if event.widget == self.all_files_tree:
            selection = self.all_files_tree.selection()
            if selection:
                file_id = self.all_files_tree.item(selection[0])['text']
        elif event.widget == self.recent_files_tree:
            selection = self.recent_files_tree.selection()
            if selection:
                file_id = self.recent_files_tree.item(selection[0])['text']
        
        if file_id:
            file_data = self.id_card_file.get_file_by_id(file_id)
            if file_data:
                self.selected_file = file_data[2]  # file_path
                self.dialog.destroy()
    
    def confirm_selection(self):
        """确认选择"""
        # 获取当前选中的文件
        file_id = None
        for tree in [self.all_files_tree, self.recent_files_tree]:
            selection = tree.selection()
            if selection:
                file_id = tree.item(selection[0])['text']
                break
        
        if file_id:
            file_data = self.id_card_file.get_file_by_id(file_id)
            if file_data:
                self.selected_file = file_data[2]  # file_path
                self.dialog.destroy()
        else:
            messagebox.showwarning("警告", "请先选择一个文件")
    
    def cancel_selection(self):
        """取消选择"""
        self.selected_file = None
        self.dialog.destroy()


class USCCCDialog(BaseDialog):
    """统一社会信用代码证书Dialog"""
    
    def __init__(self, parent, usccc_file, selected_project):
        self.usccc_file = usccc_file
        self.selected_project = selected_project
        super().__init__(parent, "统一社会信用代码证书管理", 900, 600)
    
    def create_interface(self):
        """创建证书界面"""
        # 主框架
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建三个分栏
        self.create_left_panel(main_frame)
        self.create_middle_panel(main_frame)
        self.create_right_panel(main_frame)
        
        # 加载数据
        self.load_data()
    
    def create_left_panel(self, parent):
        """创建左侧面板"""
        left_frame = tk.Frame(parent, bg='white', width=300)
        left_frame.pack(side='left', fill='y', padx=(0, 5))
        left_frame.pack_propagate(False)
        
        tk.Label(left_frame, text="所有证书文件", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        tree_frame = tk.Frame(left_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        self.all_files_tree = ttk.Treeview(tree_frame, columns=('机构名称', '法人代表'), show='tree headings')
        self.all_files_tree.heading('#0', text='ID')
        self.all_files_tree.heading('机构名称', text='机构名称')
        self.all_files_tree.heading('法人代表', text='法人代表')
        
        self.all_files_tree.column('#0', width=50)
        self.all_files_tree.column('机构名称', width=150)
        self.all_files_tree.column('法人代表', width=100)
        
        scrollbar1 = ttk.Scrollbar(tree_frame, orient='vertical', command=self.all_files_tree.yview)
        self.all_files_tree.configure(yscrollcommand=scrollbar1.set)
        
        self.all_files_tree.pack(side='left', fill='both', expand=True)
        scrollbar1.pack(side='right', fill='y')
        
        self.all_files_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        self.all_files_tree.bind('<Double-1>', self.on_file_double_click)
    
    def create_middle_panel(self, parent):
        """创建中间面板"""
        middle_frame = tk.Frame(parent, bg='white', width=300)
        middle_frame.pack(side='left', fill='y', padx=5)
        middle_frame.pack_propagate(False)
        
        tk.Label(middle_frame, text="最近添加的文件", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        tree_frame = tk.Frame(middle_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        self.recent_files_tree = ttk.Treeview(tree_frame, columns=('机构名称', '法人代表'), show='tree headings')
        self.recent_files_tree.heading('#0', text='ID')
        self.recent_files_tree.heading('机构名称', text='机构名称')
        self.recent_files_tree.heading('法人代表', text='法人代表')
        
        self.recent_files_tree.column('#0', width=50)
        self.recent_files_tree.column('机构名称', width=150)
        self.recent_files_tree.column('法人代表', width=100)
        
        scrollbar2 = ttk.Scrollbar(tree_frame, orient='vertical', command=self.recent_files_tree.yview)
        self.recent_files_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.recent_files_tree.pack(side='left', fill='both', expand=True)
        scrollbar2.pack(side='right', fill='y')
        
        self.recent_files_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        self.recent_files_tree.bind('<Double-1>', self.on_file_double_click)
    
    def create_right_panel(self, parent):
        """创建右侧面板"""
        right_frame = tk.Frame(parent, bg='white')
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        tk.Label(right_frame, text="文件详情", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        self.create_detail_form(right_frame)
        
        button_frame = tk.Frame(right_frame, bg='white')
        button_frame.pack(side='bottom', fill='x', pady=(10, 0))
        
        tk.Button(button_frame, text="确定", 
                 font=('Microsoft YaHei', 10), bg='#3182ce', fg='white',
                 command=self.confirm_selection).pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="取消", 
                 font=('Microsoft YaHei', 10), bg='#d69e2e', fg='white',
                 command=self.cancel_selection).pack(side='left')
    
    def create_detail_form(self, parent):
        """创建详情表单"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill='both', expand=True)
        
        fields = [
            ('事业单位名称', 'organization_name'),
            ('证件有效期', 'validity_period'),
            ('法人代表', 'legal_representative'),
            ('备注', 'remarks')
        ]
        
        self.form_vars = {}
        for i, (label, field) in enumerate(fields):
            tk.Label(form_frame, text=f"{label}:", 
                    font=('Microsoft YaHei', 10), bg='white').grid(
                row=i, column=0, sticky='w', padx=(0, 10), pady=8)
            
            if field == 'remarks':
                var = tk.StringVar()
                entry = tk.Text(form_frame, width=30, height=3, 
                               font=('Microsoft YaHei', 9), wrap='word')
                self.form_vars[field] = (var, entry)
            else:
                var = tk.StringVar()
                entry = tk.Entry(form_frame, textvariable=var, 
                                font=('Microsoft YaHei', 9), width=30)
                self.form_vars[field] = (var, entry)
                entry.grid(row=i, column=1, sticky='ew', pady=8)
        
        form_frame.columnconfigure(1, weight=1)
    
    def load_data(self):
        """加载数据"""
        all_files = self.usccc_file.get_all_files()
        for file in all_files:
            self.all_files_tree.insert('', 'end', text=file[0], values=(file[2] or '', file[4] or ''))
        
        recent_files = self.usccc_file.get_recent_files(10)
        for file in recent_files:
            self.recent_files_tree.insert('', 'end', text=file[0], values=(file[2] or '', file[4] or ''))
    
    def on_file_select(self, event):
        """文件选择事件"""
        file_id = None
        if event.widget == self.all_files_tree:
            selection = self.all_files_tree.selection()
            if selection:
                file_id = self.all_files_tree.item(selection[0])['text']
        elif event.widget == self.recent_files_tree:
            selection = self.recent_files_tree.selection()
            if selection:
                file_id = self.recent_files_tree.item(selection[0])['text']
        
        if file_id:
            file_data = self.usccc_file.get_file_by_id(file_id)
            if file_data:
                self.load_file_details(file_data)
    
    def load_file_details(self, file_data):
        """加载文件详情"""
        fields = ['organization_name', 'validity_period', 'legal_representative', 'remarks']
        for i, field in enumerate(fields):
            if i + 2 < len(file_data):
                var, entry = self.form_vars[field]
                value = file_data[i + 2] or ''
                
                if field == 'remarks':
                    entry.delete(1.0, tk.END)
                    entry.insert(1.0, value)
                else:
                    var.set(value)
    
    def on_file_double_click(self, event):
        """文件双击事件"""
        file_id = None
        if event.widget == self.all_files_tree:
            selection = self.all_files_tree.selection()
            if selection:
                file_id = self.all_files_tree.item(selection[0])['text']
        elif event.widget == self.recent_files_tree:
            selection = self.recent_files_tree.selection()
            if selection:
                file_id = self.recent_files_tree.item(selection[0])['text']
        
        if file_id:
            file_data = self.usccc_file.get_file_by_id(file_id)
            if file_data:
                self.selected_file = file_data[2]
                self.dialog.destroy()
    
    def confirm_selection(self):
        """确认选择"""
        file_id = None
        for tree in [self.all_files_tree, self.recent_files_tree]:
            selection = tree.selection()
            if selection:
                file_id = tree.item(selection[0])['text']
                break
        
        if file_id:
            file_data = self.usccc_file.get_file_by_id(file_id)
            if file_data:
                self.selected_file = file_data[2]
                self.dialog.destroy()
        else:
            messagebox.showwarning("警告", "请先选择一个文件")
    
    def cancel_selection(self):
        """取消选择"""
        self.selected_file = None
        self.dialog.destroy()


class ContractDialog(BaseDialog):
    """合同文件Dialog"""
    
    def __init__(self, parent, contract_file, selected_project):
        self.contract_file = contract_file
        self.selected_project = selected_project
        super().__init__(parent, "合同文件管理", 900, 600)
    
    def create_interface(self):
        """创建合同界面"""
        # 主框架
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建三个分栏
        self.create_left_panel(main_frame)
        self.create_middle_panel(main_frame)
        self.create_right_panel(main_frame)
        
        # 加载数据
        self.load_data()
    
    def create_left_panel(self, parent):
        """创建左侧面板"""
        left_frame = tk.Frame(parent, bg='white', width=300)
        left_frame.pack(side='left', fill='y', padx=(0, 5))
        left_frame.pack_propagate(False)
        
        tk.Label(left_frame, text="所有合同文件", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        tree_frame = tk.Frame(left_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        self.all_files_tree = ttk.Treeview(tree_frame, columns=('合同名称', '参与人类型'), show='tree headings')
        self.all_files_tree.heading('#0', text='ID')
        self.all_files_tree.heading('合同名称', text='合同名称')
        self.all_files_tree.heading('参与人类型', text='参与人类型')
        
        self.all_files_tree.column('#0', width=50)
        self.all_files_tree.column('合同名称', width=150)
        self.all_files_tree.column('参与人类型', width=100)
        
        scrollbar1 = ttk.Scrollbar(tree_frame, orient='vertical', command=self.all_files_tree.yview)
        self.all_files_tree.configure(yscrollcommand=scrollbar1.set)
        
        self.all_files_tree.pack(side='left', fill='both', expand=True)
        scrollbar1.pack(side='right', fill='y')
        
        self.all_files_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        self.all_files_tree.bind('<Double-1>', self.on_file_double_click)
    
    def create_middle_panel(self, parent):
        """创建中间面板"""
        middle_frame = tk.Frame(parent, bg='white', width=300)
        middle_frame.pack(side='left', fill='y', padx=5)
        middle_frame.pack_propagate(False)
        
        tk.Label(middle_frame, text="最近添加的文件", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        tree_frame = tk.Frame(middle_frame, bg='white')
        tree_frame.pack(fill='both', expand=True)
        
        self.recent_files_tree = ttk.Treeview(tree_frame, columns=('合同名称', '参与人类型'), show='tree headings')
        self.recent_files_tree.heading('#0', text='ID')
        self.recent_files_tree.heading('合同名称', text='合同名称')
        self.recent_files_tree.heading('参与人类型', text='参与人类型')
        
        self.recent_files_tree.column('#0', width=50)
        self.recent_files_tree.column('合同名称', width=150)
        self.recent_files_tree.column('参与人类型', width=100)
        
        scrollbar2 = ttk.Scrollbar(tree_frame, orient='vertical', command=self.recent_files_tree.yview)
        self.recent_files_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.recent_files_tree.pack(side='left', fill='both', expand=True)
        scrollbar2.pack(side='right', fill='y')
        
        self.recent_files_tree.bind('<<TreeviewSelect>>', self.on_file_select)
        self.recent_files_tree.bind('<Double-1>', self.on_file_double_click)
    
    def create_right_panel(self, parent):
        """创建右侧面板"""
        right_frame = tk.Frame(parent, bg='white')
        right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))
        
        tk.Label(right_frame, text="文件详情", 
                font=('Microsoft YaHei', 10, 'bold'), bg='white').pack(anchor='w', pady=(0, 10))
        
        self.create_detail_form(right_frame)
        
        button_frame = tk.Frame(right_frame, bg='white')
        button_frame.pack(side='bottom', fill='x', pady=(10, 0))
        
        tk.Button(button_frame, text="确定", 
                 font=('Microsoft YaHei', 10), bg='#3182ce', fg='white',
                 command=self.confirm_selection).pack(side='left', padx=(0, 10))
        
        tk.Button(button_frame, text="取消", 
                 font=('Microsoft YaHei', 10), bg='#d69e2e', fg='white',
                 command=self.cancel_selection).pack(side='left')
    
    def create_detail_form(self, parent):
        """创建详情表单"""
        form_frame = tk.Frame(parent, bg='white')
        form_frame.pack(fill='both', expand=True)
        
        fields = [
            ('合同名称', 'contract_name'),
            ('合同参与人类型', 'participant_type'),
            ('备注', 'remarks')
        ]
        
        self.form_vars = {}
        for i, (label, field) in enumerate(fields):
            tk.Label(form_frame, text=f"{label}:", 
                    font=('Microsoft YaHei', 10), bg='white').grid(
                row=i, column=0, sticky='w', padx=(0, 10), pady=8)
            
            if field == 'participant_type':
                var = tk.StringVar()
                combo = ttk.Combobox(form_frame, textvariable=var,
                                   values=['个人', '事业单位', '企业', '联合申请'], 
                                   state='readonly', font=('Microsoft YaHei', 9), width=27)
                self.form_vars[field] = (var, combo)
                combo.grid(row=i, column=1, sticky='ew', pady=8)
            elif field == 'remarks':
                var = tk.StringVar()
                entry = tk.Text(form_frame, width=30, height=3, 
                               font=('Microsoft YaHei', 9), wrap='word')
                self.form_vars[field] = (var, entry)
            else:
                var = tk.StringVar()
                entry = tk.Entry(form_frame, textvariable=var, 
                                font=('Microsoft YaHei', 9), width=30)
                self.form_vars[field] = (var, entry)
                entry.grid(row=i, column=1, sticky='ew', pady=8)
        
        form_frame.columnconfigure(1, weight=1)
    
    def load_data(self):
        """加载数据"""
        all_files = self.contract_file.get_all_files()
        for file in all_files:
            self.all_files_tree.insert('', 'end', text=file[0], values=(file[2] or '', file[3] or ''))
        
        recent_files = self.contract_file.get_recent_files(10)
        for file in recent_files:
            self.recent_files_tree.insert('', 'end', text=file[0], values=(file[2] or '', file[3] or ''))
    
    def on_file_select(self, event):
        """文件选择事件"""
        file_id = None
        if event.widget == self.all_files_tree:
            selection = self.all_files_tree.selection()
            if selection:
                file_id = self.all_files_tree.item(selection[0])['text']
        elif event.widget == self.recent_files_tree:
            selection = self.recent_files_tree.selection()
            if selection:
                file_id = self.recent_files_tree.item(selection[0])['text']
        
        if file_id:
            file_data = self.contract_file.get_file_by_id(file_id)
            if file_data:
                self.load_file_details(file_data)
    
    def load_file_details(self, file_data):
        """加载文件详情"""
        fields = ['contract_name', 'participant_type', 'remarks']
        for i, field in enumerate(fields):
            if i + 2 < len(file_data):
                var, entry = self.form_vars[field]
                value = file_data[i + 2] or ''
                
                if field == 'remarks':
                    entry.delete(1.0, tk.END)
                    entry.insert(1.0, value)
                else:
                    var.set(value)
    
    def on_file_double_click(self, event):
        """文件双击事件"""
        file_id = None
        if event.widget == self.all_files_tree:
            selection = self.all_files_tree.selection()
            if selection:
                file_id = self.all_files_tree.item(selection[0])['text']
        elif event.widget == self.recent_files_tree:
            selection = self.recent_files_tree.selection()
            if selection:
                file_id = self.recent_files_tree.item(selection[0])['text']
        
        if file_id:
            file_data = self.contract_file.get_file_by_id(file_id)
            if file_data:
                self.selected_file = file_data[2]
                self.dialog.destroy()
    
    def confirm_selection(self):
        """确认选择"""
        file_id = None
        for tree in [self.all_files_tree, self.recent_files_tree]:
            selection = tree.selection()
            if selection:
                file_id = tree.item(selection[0])['text']
                break
        
        if file_id:
            file_data = self.contract_file.get_file_by_id(file_id)
            if file_data:
                self.selected_file = file_data[2]
                self.dialog.destroy()
        else:
            messagebox.showwarning("警告", "请先选择一个文件")
    
    def cancel_selection(self):
        """取消选择"""
        self.selected_file = None
        self.dialog.destroy()
