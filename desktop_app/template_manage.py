#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板管理模块
根据需求分析文档设计：软著申请文档模板管理
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from datetime import datetime


class TemplateManageModule:
    """模板管理模块"""
    
    def __init__(self, parent, db, template_file, default_path):
        self.parent = parent
        self.db = db
        self.template_folder = template_file
        self.default_path = default_path
        
        # 当前选中的模板
        self.selected_template = None
        
        # 创建界面
        self.create_interface()
        
        # 加载模板数据
        self.refresh_templates()
    
    def create_interface(self):
        """创建模板管理界面"""
        # 创建主框架
        self.main_frame = tk.Frame(self.parent, bg='white')
        self.parent.add(self.main_frame, text="模板管理")
        
        # 创建左右分栏
        self.create_left_panel()
        self.create_right_panel()
    
    def create_left_panel(self):
        """创建左侧模板列表面板"""
        # 左侧框架
        self.left_frame = tk.Frame(self.main_frame, bg='white', width=300)
        self.left_frame.pack(side='left', fill='y', padx=(10, 5), pady=10)
        self.left_frame.pack_propagate(False)
        
        # 标题
        tk.Label(self.left_frame, text="模板列表", 
                font=('Microsoft YaHei', 12, 'bold'), bg='white', fg='#2c5282').pack(anchor='w')
        
        # 模板树
        tree_frame = tk.Frame(self.left_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        self.template_tree = ttk.Treeview(tree_frame, columns=('模板名称',), show='tree headings')
        self.template_tree.heading('#0', text='ID')
        self.template_tree.heading('模板名称', text='模板名称')
        
        self.template_tree.column('#0', width=50)
        self.template_tree.column('模板名称', width=200)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.template_tree.yview)
        self.template_tree.configure(yscrollcommand=scrollbar.set)
        
        self.template_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 绑定选择事件
        self.template_tree.bind('<<TreeviewSelect>>', self.on_template_select)
        
        # 操作按钮
        button_frame = tk.Frame(self.left_frame, bg='white')
        button_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(button_frame, text="添加模板", 
                 font=('Microsoft YaHei', 9), bg='#38a169', fg='white',
                 command=self.add_template).pack(side='left', padx=(0, 5))
        
        tk.Button(button_frame, text="删除模板", 
                 font=('Microsoft YaHei', 9), bg='#e53e3e', fg='white',
                 command=self.delete_template).pack(side='left')
    
    def create_right_panel(self):
        """创建右侧模板详情面板"""
        # 右侧框架
        self.right_frame = tk.Frame(self.main_frame, bg='white')
        self.right_frame.pack(side='right', fill='both', expand=True, padx=(5, 10), pady=10)
        
        # 详情框架
        self.create_detail_panel()
        
        # 操作按钮框架
        self.create_action_panel()
    
    def create_detail_panel(self):
        """创建详情面板"""
        # 标题
        tk.Label(self.right_frame, text="模板详情", 
                font=('Microsoft YaHei', 12, 'bold'), bg='white', fg='#2c5282').pack(anchor='w')
        
        # 详情表单
        detail_frame = tk.Frame(self.right_frame, bg='white')
        detail_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # 表单字段
        fields = [
            ('模板名称', 'template_name'),
            ('模板路径', 'folder_path'),
            ('编程语言', 'programming_language'),
            ('编程IDE', 'programming_ide'),
            ('数据库类型', 'database_type'),
            ('应用类型', 'programming_type'),
            ('备注', 'remarks')
        ]
        
        self.form_vars = {}
        for i, (label, field) in enumerate(fields):
            # 标签
            tk.Label(detail_frame, text=f"{label}:", 
                    font=('Microsoft YaHei', 10), bg='white').grid(
                row=i, column=0, sticky='w', padx=(0, 10), pady=5)
            
            # 输入框
            if field == 'remarks':
                # 备注使用多行文本框
                var = tk.StringVar()
                entry = tk.Text(detail_frame, width=40, height=4, 
                               font=('Microsoft YaHei', 9), wrap='word')
                self.form_vars[field] = (var, entry)
            else:
                var = tk.StringVar()
                entry = tk.Entry(detail_frame, textvariable=var, 
                                font=('Microsoft YaHei', 9), width=40)
                self.form_vars[field] = (var, entry)
            
            entry.grid(row=i, column=1, sticky='ew', pady=5)
        
        # 配置列权重
        detail_frame.columnconfigure(1, weight=1)
    
    def create_action_panel(self):
        """创建操作按钮面板"""
        action_frame = tk.Frame(self.right_frame, bg='white', height=40)
        action_frame.pack(fill='x', pady=(10, 0))
        action_frame.pack_propagate(False)
        
        # 按钮
        tk.Button(action_frame, text="保存", 
                 font=('Microsoft YaHei', 10), bg='#3182ce', fg='white',
                 command=self.save_template).pack(side='left', padx=(0, 10))
        
        tk.Button(action_frame, text="重置", 
                 font=('Microsoft YaHei', 10), bg='#d69e2e', fg='white',
                 command=self.reset_form).pack(side='left', padx=(0, 10))
        
        tk.Button(action_frame, text="打开模板文件夹", 
                 font=('Microsoft YaHei', 10), bg='#38a169', fg='white',
                 command=self.open_template_folder).pack(side='left', padx=(0, 10))
        
        tk.Button(action_frame, text="通过模板创建项目", 
                 font=('Microsoft YaHei', 10), bg='#e53e3e', fg='white',
                 command=self.create_project_from_template).pack(side='left')
    
    def refresh_templates(self):
        """刷新模板列表"""
        # 清空树
        for item in self.template_tree.get_children():
            self.template_tree.delete(item)
        
        # 获取模板数据
        templates = self.template_folder.get_all_templates()
        
        # 添加到树控件
        for template in templates:
            self.template_tree.insert('', 'end', text=template[0], values=(template[1],))
    
    def on_template_select(self, event):
        """模板选择事件"""
        selection = self.template_tree.selection()
        if not selection:
            return
        
        item = self.template_tree.item(selection[0])
        template_id = item['text']
        
        # 获取模板详情
        template = self.template_folder.get_template_by_id(template_id)
        if template:
            self.selected_template = template
            self.load_template_details(template)
    
    def load_template_details(self, template):
        """加载模板详情"""
        # 清空表单
        self.reset_form()
        
        # 填充数据
        fields = ['template_name','folder_path', 'programming_language', 'programming_ide', 
                 'database_type', 'programming_type', 'remarks']
        
        for i, field in enumerate(fields):
            var, entry = self.form_vars[field]
            value = template[i + 1] if i + 1 < len(template) else ''  # 跳过ID字段
            
            if field == 'remarks':
                entry.delete(1.0, tk.END)
                entry.insert(1.0, value or '')
            else:
                var.set(value or '')
    
    def add_template(self):
        """添加模板"""
        # 选择模板文件夹
        template_folder = filedialog.askdirectory(
            title="选择模板文件夹",
            initialdir=self.default_path.get_path('template_path')
        )
        
        if not template_folder:
            return
        
        # 输入模板名称
        from tkinter import simpledialog
        template_name = simpledialog.askstring("添加模板", "请输入模板名称:")
        if not template_name:
            return
        
        try:
            # 获取模板路径
            template_path = self.default_path.get_path('template_path')
            if not template_path:
                messagebox.showerror("错误", "模板路径未设置")
                return
            
            # 创建目标文件夹
            target_folder = os.path.join(template_path, template_name)
            if os.path.exists(target_folder):
                messagebox.showerror("错误", "模板名称已存在")
                return
            
            # 复制模板文件夹
            shutil.copytree(template_folder, target_folder)
            
            # 添加到数据库
            self.template_folder.add_folder(
                folder_name=template_name,
                folder_path=target_folder,
                programming_language='',
                ide_type='',
                database_type='',
                programming_type='',
                remarks=''
            )
            
            # 刷新列表
            self.refresh_templates()
            messagebox.showinfo("成功", f"模板 '{template_name}' 添加成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"添加模板失败: {str(e)}")
    
    def delete_template(self):
        """删除模板"""
        if not self.selected_template:
            messagebox.showwarning("警告", "请先选择一个模板")
            return
        
        template_name = self.selected_template[1]
        
        if messagebox.askyesno("确认删除", f"确定要删除模板 '{template_name}' 吗？\n这将删除模板文件夹和数据库记录。"):
            try:
                # 删除模板文件夹
                template_path = self.selected_template[2]
                if os.path.exists(template_path):
                    shutil.rmtree(template_path)
                
                # 删除数据库记录
                self.db.execute_update(
                    "DELETE FROM template_files WHERE id = ?", 
                    (self.selected_template[0],)
                )
                
                # 刷新列表
                self.refresh_templates()
                self.reset_form()
                self.selected_template = None
                
                messagebox.showinfo("成功", f"模板 '{template_name}' 删除成功")
                
            except Exception as e:
                messagebox.showerror("错误", f"删除模板失败: {str(e)}")
    
    def save_template(self):
        """保存模板"""
        if not self.selected_template:
            messagebox.showwarning("警告", "请先选择一个模板")
            return
        
        try:
            # 获取表单数据
            template_id = self.selected_template[0]
            template_name = self.form_vars['template_name'][0].get()
            folder_path = self.form_vars['folder_path'][0].get()
            programming_language = self.form_vars['programming_language'][0].get()
            programming_ide = self.form_vars['programming_ide'][0].get()
            database_type = self.form_vars['database_type'][0].get()
            programming_type = self.form_vars['programming_type'][0].get()
            remarks = self.form_vars['remarks'][1].get(1.0, tk.END).strip()
            
            if not template_name:
                messagebox.showerror("错误", "模板名称不能为空")
                return
            
            # 更新数据库
            self.template_folder.update_folder(
                template_id,
                folder_name=template_name,
                folder_path=folder_path,
                programming_language=programming_language,
                ide_type=programming_ide,  # 将programming_ide映射到ide_type
                database_type=database_type,
                programming_type=programming_type,  # 将programming_type映射到programming_type
                remarks=remarks
            )
            
            # 刷新列表
            self.refresh_templates()
            messagebox.showinfo("成功", "模板信息保存成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存模板失败: {str(e)}")
    
    def reset_form(self):
        """重置表单"""
        for field, (var, entry) in self.form_vars.items():
            if field == 'remarks':
                entry.delete(1.0, tk.END)
            else:
                var.set('')
    
    def open_template_folder(self):
        """打开模板文件夹"""
        template_path = self.default_path.get_path('template_path')
        if template_path and os.path.exists(template_path):
            os.startfile(template_path)
        else:
            messagebox.showerror("错误", "模板文件夹不存在")
    
    def create_project_from_template(self):
        """通过模板创建项目"""
        if not self.selected_template:
            messagebox.showwarning("警告", "请先选择一个模板")
            return
        
        # 选择目标项目文件夹
        project_folder = filedialog.askdirectory(
            title="选择目标项目文件夹",
            initialdir=self.default_path.get_path('project_path')
        )
        
        if not project_folder:
            return
        
        try:
            template_path = self.selected_template[2]
            template_name = self.selected_template[1]
            
            # 创建项目文件夹
            project_name = f"项目_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            target_folder = os.path.join(project_folder, project_name)
            
            if os.path.exists(target_folder):
                messagebox.showerror("错误", "项目文件夹已存在")
                return
            
            # 复制模板到项目文件夹
            shutil.copytree(template_path, target_folder)
            
            messagebox.showinfo("成功", f"项目已创建: {target_folder}")
            os.startfile(target_folder)
            
        except Exception as e:
            messagebox.showerror("错误", f"创建项目失败: {str(e)}")
