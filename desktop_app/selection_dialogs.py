#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选择对话框模块
包括模板选择、身份证复印件、统一社会信用代码证书、合同文件的选择对话框
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
from datetime import datetime
import traceback


class TemplateSelectionDialog:
    """模板选择对话框 - 3.2.10"""
    
    def __init__(self, parent, template_folder, project_id=None, project_name=None, target_folder=None):
        """
        初始化模板选择对话框
        
        Args:
            parent: 父窗口
            template_folder: TemplateFolder实例
            project_id: 项目ID
            project_name: 项目名称
            target_folder: 目标文件夹路径
        """
        self.parent = parent
        self.template_folder = template_folder
        self.project_id = project_id
        self.project_name = project_name
        self.target_folder = target_folder
        self.selected_template = None
        self.result = None
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("选择项目模板")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.load_templates()
        
        # 居中显示
        self.center_window()
    
    def center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧框架
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # 右侧框架
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 左侧 - Treeview
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 创建Treeview
        self.tree = ttk.Treeview(tree_frame, selectmode='browse')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        # 绑定选择事件
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # 左侧底部 - 搜索框架
        bottom_frame = ttk.Frame(left_frame)
        bottom_frame.pack(fill=tk.X)
        
        ttk.Label(bottom_frame, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(bottom_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(bottom_frame, text="检索", command=self.search_template).pack(side=tk.LEFT)
        
        # 右侧 - 详细信息
        ttk.Label(right_frame, text="模板详细信息", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        # 信息显示区域
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建显示字段
        fields = [
            ("模板名称:", "folder_name"),
            ("编程语言:", "programming_language"),
            ("编程IDE:", "ide_type"),
            ("数据库类型:", "database_type"),
            ("应用类型:", "programming_type"),
            ("备注:", "remarks"),
            ("创建时间:", "created_time"),
            ("最近使用:", "recurrent_copy_time")
        ]
        
        self.info_vars = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(info_frame, text=label, width=12, anchor='e').grid(
                row=i, column=0, sticky='ne', padx=5, pady=5
            )
            
            if key == "remarks":
                # 备注使用Text控件
                text_widget = tk.Text(info_frame, height=4, width=40, wrap=tk.WORD, state='disabled')
                text_widget.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.info_vars[key] = text_widget
            else:
                var = tk.StringVar()
                entry = ttk.Entry(info_frame, textvariable=var, state='readonly')
                entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.info_vars[key] = var
        
        info_frame.columnconfigure(1, weight=1)
        
        # 底部按钮
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="选择并复制", command=self.confirm_selection).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(
            side=tk.RIGHT
        )
    
    def load_templates(self):
        """加载模板列表"""
        # 清空树
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            # 获取所有模板
            all_templates = self.template_folder.get_all_folders()
            
            if not all_templates:
                return
            
            # 分类：最近使用的和所有的
            recent_templates = []
            other_templates = []
            
            # template_folders表字段: id, folder_name, folder_path, programming_language, ide_type,
            # database_type, programming_type, remarks, created_time, updated_time, recurrent_copy_time
            # 索引: 0=id, 1=folder_name, 2=folder_path, 10=recurrent_copy_time
            for template in all_templates:
                if len(template) > 10 and template[10]:  # recurrent_copy_time在索引10
                    recent_templates.append(template)
                else:
                    other_templates.append(template)
            
            # 按最近使用时间排序
            recent_templates.sort(key=lambda x: x[10] if len(x) > 10 and x[10] else '', reverse=True)
            recent_templates = recent_templates[:10]  # 只取最近10条
            
            # 添加"最近使用"节点
            if recent_templates:
                recent_node = self.tree.insert('', 'end', text='最近使用的模板', open=True)
                for template in recent_templates:
                    self.tree.insert(recent_node, 'end', text=template[1], values=(template[0],))
            
            # 添加"所有模板"节点
            all_node = self.tree.insert('', 'end', text='所有模板', open=True)
            for template in all_templates:
                self.tree.insert(all_node, 'end', text=template[1], values=(template[0],))
            
        except Exception as e:
            print(f"加载模板列表错误: {traceback.format_exc()}")
            messagebox.showerror("错误", f"加载模板列表失败：{str(e)}")
    
    def on_select(self, event):
        """选择事件"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if not values:  # 父节点
            return
        
        template_id = values[0]
        self.show_template_details(template_id)
    
    def show_template_details(self, template_id):
        """显示模板详细信息"""
        try:
            template = self.template_folder.get_folder_by_id(template_id)
            if not template:
                return
            
            self.selected_template = template
            
            # 更新显示
            fields = ["folder_name", "programming_language", "ide_type", 
                     "database_type", "programming_type", "remarks", 
                     "created_time", "recurrent_copy_time"]
            
            for i, field in enumerate(fields):
                value = template[i+1] if i+1 < len(template) else ""
                if value is None:
                    value = ""
                
                if field == "remarks":
                    text_widget = self.info_vars[field]
                    text_widget.config(state='normal')
                    text_widget.delete('1.0', tk.END)
                    text_widget.insert('1.0', value)
                    text_widget.config(state='disabled')
                else:
                    self.info_vars[field].set(value)
        
        except Exception as e:
            messagebox.showerror("错误", f"加载模板详情失败：{str(e)}")
    
    def search_template(self):
        """搜索模板"""
        search_text = self.search_var.get().strip()
        if not search_text:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
        
        # 在树中查找
        for item in self.tree.get_children():
            for child in self.tree.get_children(item):
                text = self.tree.item(child, 'text')
                if search_text.lower() in text.lower():
                    # 选中并显示
                    self.tree.selection_set(child)
                    self.tree.see(child)
                    self.tree.focus(child)
                    return
        
        messagebox.showinfo("提示", "未找到匹配的模板")
    
    def on_double_click(self, event):
        """双击事件 - 直接复制模板"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if not values:  # 父节点
            return
        
        self.confirm_selection()
    
    def confirm_selection(self):
        """确认选择并复制模板"""
        if not self.selected_template:
            messagebox.showwarning("提示", "请先选择一个模板")
            return
        
        if not self.target_folder or not self.project_id or not self.project_name:
            messagebox.showwarning("提示", "缺少必要的项目信息")
            return
        
        try:
            # 源文件夹路径
            source_folder = self.selected_template[2]  # folder_path
            
            if not os.path.exists(source_folder):
                messagebox.showerror("错误", f"模板文件夹不存在：{source_folder}")
                return
            
            # 目标文件夹名称：项目ID + 项目名称
            target_folder_name = f"{self.project_id}.{self.project_name}"
            target_path = os.path.join(self.target_folder, target_folder_name)
            
            # 检查目标是否已存在
            if os.path.exists(target_path):
                response = messagebox.askyesno(
                    "确认", 
                    f"目标文件夹已存在：{target_folder_name}\n是否覆盖？"
                )
                if not response:
                    return
                shutil.rmtree(target_path)
            
            # 复制文件夹
            shutil.copytree(source_folder, target_path)
            
            # 更新recurrent_copy_time
            template_id = self.selected_template[0]
            current_time = datetime.now().isoformat()
            print(f"[DEBUG] 更新模板ID {template_id} 的recurrent_copy_time为 {current_time}")
            self.template_folder.update_folder(
                template_id,
                recurrent_copy_time=current_time
            )
            print(f"[DEBUG] 模板recurrent_copy_time更新完成")
            
            self.result = target_path
            messagebox.showinfo("成功", f"模板已复制到：{target_path}")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"复制模板失败：{str(e)}")
    
    def show(self):
        """显示对话框并等待"""
        self.dialog.wait_window()
        return self.result


class IDCardFileDialog:
    """身份证复印件选择对话框 - 3.2.11"""
    
    def __init__(self, parent, id_card_file, target_folder=None):
        """
        初始化身份证复印件选择对话框
        
        Args:
            parent: 父窗口
            id_card_file: IDCardFile实例
            target_folder: 目标文件夹路径（复制文件的目标位置）
        """
        self.parent = parent
        self.id_card_file = id_card_file
        self.target_folder = target_folder
        self.selected_file = None
        self.result = None
        
        # 创建对话框窗口
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("选择身份证复印件")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.load_files()
        self.center_window()
    
    def center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建界面组件"""
        # 主容器
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧框架
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # 右侧框架
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 左侧 - Treeview
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.tree = ttk.Treeview(tree_frame, selectmode='browse')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # 左侧底部 - 搜索框架
        bottom_frame = ttk.Frame(left_frame)
        bottom_frame.pack(fill=tk.X)
        
        ttk.Label(bottom_frame, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(bottom_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(bottom_frame, text="检索", command=self.search_file).pack(side=tk.LEFT)
        
        # 右侧 - 详细信息
        ttk.Label(right_frame, text="身份证复印件详细信息", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ("文件名:", "file_name"),
            ("姓名:", "person_name"),
            ("性别:", "gender"),
            ("籍贯:", "birthplace"),
            ("身份证号:", "id_number"),
            ("备注:", "remarks"),
            ("创建时间:", "created_time"),
            ("最近使用:", "recurrent_copy_time")
        ]
        
        self.info_vars = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(info_frame, text=label, width=12, anchor='e').grid(
                row=i, column=0, sticky='ne', padx=5, pady=5
            )
            
            if key == "remarks":
                text_widget = tk.Text(info_frame, height=4, width=40, wrap=tk.WORD, state='disabled')
                text_widget.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.info_vars[key] = text_widget
            else:
                var = tk.StringVar()
                entry = ttk.Entry(info_frame, textvariable=var, state='readonly')
                entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.info_vars[key] = var
        
        info_frame.columnconfigure(1, weight=1)
        
        # 底部按钮
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="选择并复制", command=self.confirm_selection).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(
            side=tk.RIGHT
        )
    
    def load_files(self):
        """加载文件列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            all_files = self.id_card_file.get_all_files()
            
            if not all_files:
                return
            
            # 分类
            recent_files = []
            other_files = []
            
            # id_card_files表字段: id, file_name, file_path, person_name, gender, birthplace,
            # id_number, remarks, created_time, updated_time, recurrent_copy_time
            # 索引: 0=id, 1=file_name, 2=file_path, 10=recurrent_copy_time
            for file in all_files:
                if len(file) > 10 and file[10]:  # recurrent_copy_time在索引10
                    recent_files.append(file)
                else:
                    other_files.append(file)
            
            recent_files.sort(key=lambda x: x[10] if len(x) > 10 and x[10] else '', reverse=True)
            recent_files = recent_files[:10]
            
            if recent_files:
                recent_node = self.tree.insert('', 'end', text='最近使用的文件', open=True)
                for file in recent_files:
                    self.tree.insert(recent_node, 'end', text=file[1], values=(file[0],))
            
            all_node = self.tree.insert('', 'end', text='所有文件', open=True)
            for file in all_files:
                self.tree.insert(all_node, 'end', text=file[1], values=(file[0],))
        
        except Exception as e:
            print(f"加载身份证文件列表错误: {traceback.format_exc()}")
            messagebox.showerror("错误", f"加载文件列表失败：{str(e)}")
    
    def on_select(self, event):
        """选择事件"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if not values:
            return
        
        file_id = values[0]
        self.show_file_details(file_id)
    
    def show_file_details(self, file_id):
        """显示文件详细信息"""
        try:
            file_info = self.id_card_file.get_file_by_id(file_id)
            if not file_info:
                return
            
            self.selected_file = file_info
            
            # id_card_files表字段索引:
            # 0=id, 1=file_name, 2=file_path, 3=person_name, 4=gender, 5=birthplace,
            # 6=id_number, 7=remarks, 8=created_time, 9=updated_time, 10=recurrent_copy_time
            field_indices = {
                "file_name": 1,
                "person_name": 3,
                "gender": 4,
                "birthplace": 5,
                "id_number": 6,
                "remarks": 7,
                "created_time": 8,
                "recurrent_copy_time": 10
            }
            
            for field, idx in field_indices.items():
                value = file_info[idx] if idx < len(file_info) else ""
                if value is None:
                    value = ""
                
                if field == "remarks":
                    text_widget = self.info_vars[field]
                    text_widget.config(state='normal')
                    text_widget.delete('1.0', tk.END)
                    text_widget.insert('1.0', value)
                    text_widget.config(state='disabled')
                else:
                    self.info_vars[field].set(value)
        
        except Exception as e:
            print(f"加载身份证文件详情错误: {traceback.format_exc()}")
            messagebox.showerror("错误", f"加载文件详情失败：{str(e)}")
    
    def search_file(self):
        """搜索文件"""
        search_text = self.search_var.get().strip()
        if not search_text:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
        
        for item in self.tree.get_children():
            for child in self.tree.get_children(item):
                text = self.tree.item(child, 'text')
                if search_text.lower() in text.lower():
                    self.tree.selection_set(child)
                    self.tree.see(child)
                    self.tree.focus(child)
                    return
        
        messagebox.showinfo("提示", "未找到匹配的文件")
    
    def on_double_click(self, event):
        """双击事件"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if not values:
            return
        
        self.confirm_selection()
    
    def confirm_selection(self):
        """确认选择并复制文件"""
        if not self.selected_file:
            messagebox.showwarning("提示", "请先选择一个文件")
            return
        
        if not self.target_folder:
            messagebox.showwarning("提示", "未指定目标文件夹")
            return
        
        try:
            source_file = self.selected_file[2]  # file_path
            
            if not os.path.exists(source_file):
                messagebox.showerror("错误", f"源文件不存在：{source_file}")
                return
            
            # 目标文件路径
            file_name = os.path.basename(source_file)
            target_path = os.path.join(self.target_folder, file_name)
            
            # 如果文件已存在，添加后缀
            if os.path.exists(target_path):
                base, ext = os.path.splitext(file_name)
                counter = 1
                while os.path.exists(target_path):
                    new_name = f"{base}_{counter}{ext}"
                    target_path = os.path.join(self.target_folder, new_name)
                    counter += 1
            
            # 复制文件
            shutil.copy2(source_file, target_path)
            
            # 更新recurrent_copy_time
            file_id = self.selected_file[0]
            current_time = datetime.now().isoformat()
            print(f"[DEBUG] 更新身份证文件ID {file_id} 的recurrent_copy_time为 {current_time}")
            self.id_card_file.update_file(
                file_id,
                recurrent_copy_time=current_time
            )
            print(f"[DEBUG] 身份证文件recurrent_copy_time更新完成")
            
            self.result = target_path
            messagebox.showinfo("成功", f"文件已复制到：{target_path}")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"复制文件失败：{str(e)}")
    
    def show(self):
        """显示对话框并等待"""
        self.dialog.wait_window()
        return self.result


class USCCCFileDialog:
    """统一社会信用代码证书选择对话框 - 3.2.12"""
    
    def __init__(self, parent, usccc_file, target_folder=None):
        """初始化统一社会信用代码证书选择对话框"""
        self.parent = parent
        self.usccc_file = usccc_file
        self.target_folder = target_folder
        self.selected_file = None
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("选择统一社会信用代码证书")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.load_files()
        self.center_window()
    
    def center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 左侧Treeview
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.tree = ttk.Treeview(tree_frame, selectmode='browse')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # 搜索框架
        bottom_frame = ttk.Frame(left_frame)
        bottom_frame.pack(fill=tk.X)
        
        ttk.Label(bottom_frame, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(bottom_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(bottom_frame, text="检索", command=self.search_file).pack(side=tk.LEFT)
        
        # 右侧详细信息
        ttk.Label(right_frame, text="统一社会信用代码证书详细信息", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ("文件名:", "file_name"),
            ("事业单位名称:", "organization_name"),
            ("证件有效期:", "validity_period"),
            ("法人代表:", "legal_representative"),
            ("备注:", "remarks"),
            ("创建时间:", "created_time"),
            ("最近使用:", "recurrent_copy_time")
        ]
        
        self.info_vars = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(info_frame, text=label, width=15, anchor='e').grid(
                row=i, column=0, sticky='ne', padx=5, pady=5
            )
            
            if key == "remarks":
                text_widget = tk.Text(info_frame, height=4, width=40, wrap=tk.WORD, state='disabled')
                text_widget.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.info_vars[key] = text_widget
            else:
                var = tk.StringVar()
                entry = ttk.Entry(info_frame, textvariable=var, state='readonly')
                entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.info_vars[key] = var
        
        info_frame.columnconfigure(1, weight=1)
        
        # 底部按钮
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="选择并复制", command=self.confirm_selection).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(
            side=tk.RIGHT
        )
    
    def load_files(self):
        """加载文件列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            all_files = self.usccc_file.get_all_files()
            
            if not all_files:
                return
            
            recent_files = []
            other_files = []
            
            # usccc_files表字段: id, file_name, file_path, organization_name, validity_period,
            # legal_representative, remarks, created_time, updated_time, recurrent_copy_time
            # 索引: 0=id, 1=file_name, 2=file_path, 9=recurrent_copy_time
            for file in all_files:
                if len(file) > 9 and file[9]:  # recurrent_copy_time在索引9
                    recent_files.append(file)
                else:
                    other_files.append(file)
            
            recent_files.sort(key=lambda x: x[9] if len(x) > 9 and x[9] else '', reverse=True)
            recent_files = recent_files[:10]
            
            if recent_files:
                recent_node = self.tree.insert('', 'end', text='最近使用的文件', open=True)
                for file in recent_files:
                    self.tree.insert(recent_node, 'end', text=file[1], values=(file[0],))
            
            all_node = self.tree.insert('', 'end', text='所有文件', open=True)
            for file in all_files:
                self.tree.insert(all_node, 'end', text=file[1], values=(file[0],))
        
        except Exception as e:
            print(f"加载证书文件列表错误: {traceback.format_exc()}")
            messagebox.showerror("错误", f"加载文件列表失败：{str(e)}")
    
    def on_select(self, event):
        """选择事件"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if not values:
            return
        
        file_id = values[0]
        self.show_file_details(file_id)
    
    def show_file_details(self, file_id):
        """显示文件详细信息"""
        try:
            file_info = self.usccc_file.get_file_by_id(file_id)
            if not file_info:
                return
            
            self.selected_file = file_info
            
            # usccc_files表字段索引:
            # 0=id, 1=file_name, 2=file_path, 3=organization_name, 4=validity_period,
            # 5=legal_representative, 6=remarks, 7=created_time, 8=updated_time, 9=recurrent_copy_time
            field_indices = {
                "file_name": 1,
                "organization_name": 3,
                "validity_period": 4,
                "legal_representative": 5,
                "remarks": 6,
                "created_time": 7,
                "recurrent_copy_time": 9
            }
            
            for field, idx in field_indices.items():
                value = file_info[idx] if idx < len(file_info) else ""
                if value is None:
                    value = ""
                
                if field == "remarks":
                    text_widget = self.info_vars[field]
                    text_widget.config(state='normal')
                    text_widget.delete('1.0', tk.END)
                    text_widget.insert('1.0', value)
                    text_widget.config(state='disabled')
                else:
                    self.info_vars[field].set(value)
        
        except Exception as e:
            print(f"加载证书文件详情错误: {traceback.format_exc()}")
            messagebox.showerror("错误", f"加载文件详情失败：{str(e)}")
    
    def search_file(self):
        """搜索文件"""
        search_text = self.search_var.get().strip()
        if not search_text:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
        
        for item in self.tree.get_children():
            for child in self.tree.get_children(item):
                text = self.tree.item(child, 'text')
                if search_text.lower() in text.lower():
                    self.tree.selection_set(child)
                    self.tree.see(child)
                    self.tree.focus(child)
                    return
        
        messagebox.showinfo("提示", "未找到匹配的文件")
    
    def on_double_click(self, event):
        """双击事件"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if not values:
            return
        
        self.confirm_selection()
    
    def confirm_selection(self):
        """确认选择并复制文件"""
        if not self.selected_file:
            messagebox.showwarning("提示", "请先选择一个文件")
            return
        
        if not self.target_folder:
            messagebox.showwarning("提示", "未指定目标文件夹")
            return
        
        try:
            source_file = self.selected_file[2]  # file_path
            
            if not os.path.exists(source_file):
                messagebox.showerror("错误", f"源文件不存在：{source_file}")
                return
            
            file_name = os.path.basename(source_file)
            target_path = os.path.join(self.target_folder, file_name)
            
            if os.path.exists(target_path):
                base, ext = os.path.splitext(file_name)
                counter = 1
                while os.path.exists(target_path):
                    new_name = f"{base}_{counter}{ext}"
                    target_path = os.path.join(self.target_folder, new_name)
                    counter += 1
            
            shutil.copy2(source_file, target_path)
            
            # 更新recurrent_copy_time
            file_id = self.selected_file[0]
            current_time = datetime.now().isoformat()
            print(f"[DEBUG] 更新证书文件ID {file_id} 的recurrent_copy_time为 {current_time}")
            self.usccc_file.update_file(
                file_id,
                recurrent_copy_time=current_time
            )
            print(f"[DEBUG] 证书文件recurrent_copy_time更新完成")
            
            self.result = target_path
            messagebox.showinfo("成功", f"文件已复制到：{target_path}")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"复制文件失败：{str(e)}")
    
    def show(self):
        """显示对话框并等待"""
        self.dialog.wait_window()
        return self.result


class ContractFileDialog:
    """合同文件选择对话框 - 3.2.13"""
    
    def __init__(self, parent, contract_file, target_folder=None):
        """初始化合同文件选择对话框"""
        self.parent = parent
        self.contract_file = contract_file
        self.target_folder = target_folder
        self.selected_file = None
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("选择合同文件")
        self.dialog.geometry("900x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.load_files()
        self.center_window()
    
    def center_window(self):
        """窗口居中"""
        self.dialog.update_idletasks()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        x = (self.dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (height // 2)
        self.dialog.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """创建界面组件"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 左侧Treeview
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.tree = ttk.Treeview(tree_frame, selectmode='browse')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # 搜索框架
        bottom_frame = ttk.Frame(left_frame)
        bottom_frame.pack(fill=tk.X)
        
        ttk.Label(bottom_frame, text="搜索:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(bottom_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(bottom_frame, text="检索", command=self.search_file).pack(side=tk.LEFT)
        
        # 右侧详细信息
        ttk.Label(right_frame, text="合同文件详细信息", 
                 font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        info_frame = ttk.Frame(right_frame)
        info_frame.pack(fill=tk.BOTH, expand=True)
        
        fields = [
            ("文件名:", "file_name"),
            ("合同名称:", "contract_name"),
            ("合同参与人类型:", "participant_type"),
            ("备注:", "remarks"),
            ("创建时间:", "created_time"),
            ("最近使用:", "recurrent_copy_time")
        ]
        
        self.info_vars = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(info_frame, text=label, width=15, anchor='e').grid(
                row=i, column=0, sticky='ne', padx=5, pady=5
            )
            
            if key == "remarks":
                text_widget = tk.Text(info_frame, height=4, width=40, wrap=tk.WORD, state='disabled')
                text_widget.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.info_vars[key] = text_widget
            else:
                var = tk.StringVar()
                entry = ttk.Entry(info_frame, textvariable=var, state='readonly')
                entry.grid(row=i, column=1, sticky='ew', padx=5, pady=5)
                self.info_vars[key] = var
        
        info_frame.columnconfigure(1, weight=1)
        
        # 底部按钮
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="选择并复制", command=self.confirm_selection).pack(
            side=tk.RIGHT, padx=5
        )
        ttk.Button(button_frame, text="取消", command=self.dialog.destroy).pack(
            side=tk.RIGHT
        )
    
    def load_files(self):
        """加载文件列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            all_files = self.contract_file.get_all_files()
            
            if not all_files:
                return
            
            recent_files = []
            other_files = []
            
            # contract_files表字段: id, file_name, file_path, contract_name, participant_type, 
            # remarks, created_time, updated_time, recurrent_copy_time
            # 索引: 0=id, 1=file_name, 2=file_path, 8=recurrent_copy_time
            for file in all_files:
                if len(file) > 8 and file[8]:  # recurrent_copy_time在索引8
                    recent_files.append(file)
                else:
                    other_files.append(file)
            
            recent_files.sort(key=lambda x: x[8] if len(x) > 8 and x[8] else '', reverse=True)
            recent_files = recent_files[:10]
            
            if recent_files:
                recent_node = self.tree.insert('', 'end', text='最近使用的文件', open=True)
                for file in recent_files:
                    self.tree.insert(recent_node, 'end', text=file[1], values=(file[0],))
            
            all_node = self.tree.insert('', 'end', text='所有文件', open=True)
            for file in all_files:
                self.tree.insert(all_node, 'end', text=file[1], values=(file[0],))
        
        except Exception as e:
            print(f"加载合同文件列表错误: {traceback.format_exc()}")
            messagebox.showerror("错误", f"加载文件列表失败：{str(e)}")
    
    def on_select(self, event):
        """选择事件"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if not values:
            return
        
        file_id = values[0]
        self.show_file_details(file_id)
    
    def show_file_details(self, file_id):
        """显示文件详细信息"""
        try:
            file_info = self.contract_file.get_file_by_id(file_id)
            if not file_info:
                return
            
            self.selected_file = file_info
            
            # contract_files表字段索引:
            # 0=id, 1=file_name, 2=file_path, 3=contract_name, 4=participant_type,
            # 5=remarks, 6=created_time, 7=updated_time, 8=recurrent_copy_time
            field_indices = {
                "file_name": 1,
                "contract_name": 3,
                "participant_type": 4,
                "remarks": 5,
                "created_time": 6,
                "recurrent_copy_time": 8
            }
            
            for field, idx in field_indices.items():
                value = file_info[idx] if idx < len(file_info) else ""
                if value is None:
                    value = ""
                
                if field == "remarks":
                    text_widget = self.info_vars[field]
                    text_widget.config(state='normal')
                    text_widget.delete('1.0', tk.END)
                    text_widget.insert('1.0', value)
                    text_widget.config(state='disabled')
                else:
                    self.info_vars[field].set(value)
        
        except Exception as e:
            print(f"加载合同文件详情错误: {traceback.format_exc()}")
            messagebox.showerror("错误", f"加载文件详情失败：{str(e)}")
    
    def search_file(self):
        """搜索文件"""
        search_text = self.search_var.get().strip()
        if not search_text:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return
        
        for item in self.tree.get_children():
            for child in self.tree.get_children(item):
                text = self.tree.item(child, 'text')
                if search_text.lower() in text.lower():
                    self.tree.selection_set(child)
                    self.tree.see(child)
                    self.tree.focus(child)
                    return
        
        messagebox.showinfo("提示", "未找到匹配的文件")
    
    def on_double_click(self, event):
        """双击事件"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.tree.item(item, 'values')
        
        if not values:
            return
        
        self.confirm_selection()
    
    def confirm_selection(self):
        """确认选择并复制文件"""
        if not self.selected_file:
            messagebox.showwarning("提示", "请先选择一个文件")
            return
        
        if not self.target_folder:
            messagebox.showwarning("提示", "未指定目标文件夹")
            return
        
        try:
            source_file = self.selected_file[2]  # file_path
            
            if not os.path.exists(source_file):
                messagebox.showerror("错误", f"源文件不存在：{source_file}")
                return
            
            file_name = os.path.basename(source_file)
            target_path = os.path.join(self.target_folder, file_name)
            
            if os.path.exists(target_path):
                base, ext = os.path.splitext(file_name)
                counter = 1
                while os.path.exists(target_path):
                    new_name = f"{base}_{counter}{ext}"
                    target_path = os.path.join(self.target_folder, new_name)
                    counter += 1
            
            shutil.copy2(source_file, target_path)
            
            # 更新recurrent_copy_time
            file_id = self.selected_file[0]
            current_time = datetime.now().isoformat()
            print(f"[DEBUG] 更新合同文件ID {file_id} 的recurrent_copy_time为 {current_time}")
            self.contract_file.update_file(
                file_id,
                recurrent_copy_time=current_time
            )
            print(f"[DEBUG] 合同文件recurrent_copy_time更新完成")
            
            self.result = target_path
            messagebox.showinfo("成功", f"文件已复制到：{target_path}")
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("错误", f"复制文件失败：{str(e)}")
    
    def show(self):
        """显示对话框并等待"""
        self.dialog.wait_window()
        return self.result

