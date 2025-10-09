#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
材料管理模块
根据需求分析文档设计：软著申请材料管理
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from datetime import datetime
from config.config import LOCAL_CONFIG


class MaterialManageModule:
    """材料管理模块"""
    
    def __init__(self, parent, db, id_card_file, usccc_file, contract_file, default_path):
        self.parent = parent
        self.db = db
        self.id_card_file = id_card_file
        self.usccc_file = usccc_file
        self.contract_file = contract_file
        self.default_path = default_path
        
        # 当前选中的材料
        self.selected_material = None
        self.current_material_type = '身份证复印件'
        
        # 创建界面
        self.create_interface()
        
        # 加载材料数据
        self.refresh_materials()
    
    def create_interface(self):
        """创建材料管理界面"""
        # 创建主框架
        self.main_frame = tk.Frame(self.parent, bg='white')
        self.parent.add(self.main_frame, text="材料管理")
        
        # 创建左右分栏
        self.create_left_panel()
        self.create_right_panel()
    
    def create_left_panel(self):
        """创建左侧材料列表面板"""
        # 左侧框架
        self.left_frame = tk.Frame(self.main_frame, bg='white', width=300)
        self.left_frame.pack(side='left', fill='y', padx=(10, 5), pady=10)
        self.left_frame.pack_propagate(False)
        
        # 材料类型选择
        self.create_material_type_selector()
        
        # 材料列表
        self.create_material_list()
        
        # 操作按钮
        self.create_left_buttons()
    
    def create_material_type_selector(self):
        """创建材料类型选择器"""
        # 顶部框架
        top_frame = tk.Frame(self.left_frame, bg='white', height=25)
        top_frame.pack(fill='x', pady=(0, 10))
        top_frame.pack_propagate(False)
        
        # 标签
        tk.Label(top_frame, text="材料类型:", 
                font=('Microsoft YaHei', 10), bg='white').pack(side='left')
        
        # 下拉框
        self.material_type_var = tk.StringVar(value='身份证复印件')
        self.material_type_combo = ttk.Combobox(
            top_frame, textvariable=self.material_type_var,
            values=['身份证复印件', '统一社会信用代码证书', '合同模板'],
            state='readonly', font=('Microsoft YaHei', 9)
        )
        self.material_type_combo.pack(side='left', padx=(10, 0))
        self.material_type_combo.bind('<<ComboboxSelected>>', self.on_material_type_change)
    
    def create_material_list(self):
        """创建材料列表"""
        # 材料树
        tree_frame = tk.Frame(self.left_frame, bg='white')
        tree_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.material_tree = ttk.Treeview(tree_frame, columns=('文件名',), show='tree headings')
        self.material_tree.heading('#0', text='ID')
        self.material_tree.heading('文件名', text='文件名')
        
        self.material_tree.column('#0', width=50)
        self.material_tree.column('文件名', width=200)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.material_tree.yview)
        self.material_tree.configure(yscrollcommand=scrollbar.set)
        
        self.material_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 绑定选择事件
        self.material_tree.bind('<<TreeviewSelect>>', self.on_material_select)
    
    def create_left_buttons(self):
        """创建左侧操作按钮"""
        button_frame = tk.Frame(self.left_frame, bg='white')
        button_frame.pack(fill='x')
        
        tk.Button(button_frame, text="添加材料", 
                 font=('Microsoft YaHei', 9), bg='#38a169', fg='white',
                 command=self.add_material).pack(side='left', padx=(0, 5))
        
        tk.Button(button_frame, text="删除材料", 
                 font=('Microsoft YaHei', 9), bg='#e53e3e', fg='white',
                 command=self.delete_material).pack(side='left')
    
    def create_right_panel(self):
        """创建右侧材料详情面板"""
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
        tk.Label(self.right_frame, text="材料详情", 
                font=('Microsoft YaHei', 12, 'bold'), bg='white', fg='#2c5282').pack(anchor='w')
        
        # 详情表单
        self.detail_frame = tk.Frame(self.right_frame, bg='white')
        self.detail_frame.pack(fill='both', expand=True, pady=(10, 0))
        
        # 创建动态表单
        self.create_dynamic_form()
    
    def create_dynamic_form(self):
        """创建动态表单"""
        # 清空现有控件
        for widget in self.detail_frame.winfo_children():
            widget.destroy()
        
        # 根据材料类型创建不同的表单
        material_type = self.material_type_var.get()
        
        if material_type == '身份证复印件':
            self.create_id_card_form()
        elif material_type == '统一社会信用代码证书':
            self.create_usccc_form()
        elif material_type == '合同模板':
            self.create_contract_form()
    
    def create_id_card_form(self):
        """创建身份证复印件表单"""
        fields = [
            ('文件路径', 'file_path'),
            ('姓名', 'person_name'),
            ('性别', 'gender'),
            ('籍贯', 'birthplace'),
            ('身份证号', 'id_number'),
            ('备注', 'remarks')
        ]
        
        self.form_vars = {}
        for i, (label, field) in enumerate(fields):
            # 标签
            tk.Label(self.detail_frame, text=f"{label}:", 
                    font=('Microsoft YaHei', 10), bg='white').grid(
                row=i, column=0, sticky='w', padx=(0, 10), pady=5)
            
            # 输入框
            if field == 'gender':
                # 性别使用下拉框
                var = tk.StringVar()
                combo = ttk.Combobox(self.detail_frame, textvariable=var,
                                   values=['男', '女'], state='readonly',
                                   font=('Microsoft YaHei', 9), width=37)
                self.form_vars[field] = (var, combo)
                combo.grid(row=i, column=1, sticky='ew', pady=5)
            elif field == 'remarks':
                # 备注使用多行文本框
                var = tk.StringVar()
                entry = tk.Text(self.detail_frame, width=40, height=3, 
                               font=('Microsoft YaHei', 9), wrap='word')
                self.form_vars[field] = (var, entry)
            else:
                var = tk.StringVar()
                entry = tk.Entry(self.detail_frame, textvariable=var, 
                                font=('Microsoft YaHei', 9), width=40)
                self.form_vars[field] = (var, entry)
                entry.grid(row=i, column=1, sticky='ew', pady=5)
        
        # 配置列权重
        self.detail_frame.columnconfigure(1, weight=1)
    
    def create_usccc_form(self):
        """创建统一社会信用代码证书表单"""
        fields = [
            ('文件路径', 'file_path'),
            ('事业单位名称', 'organization_name'),
            ('证件有效期', 'validity_period'),
            ('法人代表', 'legal_representative'),
            ('备注', 'remarks')
        ]
        
        self.form_vars = {}
        for i, (label, field) in enumerate(fields):
            # 标签
            tk.Label(self.detail_frame, text=f"{label}:", 
                    font=('Microsoft YaHei', 10), bg='white').grid(
                row=i, column=0, sticky='w', padx=(0, 10), pady=5)
            
            # 输入框
            if field == 'remarks':
                # 备注使用多行文本框
                var = tk.StringVar()
                entry = tk.Text(self.detail_frame, width=40, height=3, 
                               font=('Microsoft YaHei', 9), wrap='word')
                self.form_vars[field] = (var, entry)
            else:
                var = tk.StringVar()
                entry = tk.Entry(self.detail_frame, textvariable=var, 
                                font=('Microsoft YaHei', 9), width=40)
                self.form_vars[field] = (var, entry)
                entry.grid(row=i, column=1, sticky='ew', pady=5)
        
        # 配置列权重
        self.detail_frame.columnconfigure(1, weight=1)
    
    def create_contract_form(self):
        """创建合同模板表单"""
        fields = [
            ('文件路径', 'file_path'),
            ('合同名称', 'contract_name'),
            ('合同参与人类型', 'participant_type'),
            ('备注', 'remarks')
        ]
        
        self.form_vars = {}
        for i, (label, field) in enumerate(fields):
            # 标签
            tk.Label(self.detail_frame, text=f"{label}:", 
                    font=('Microsoft YaHei', 10), bg='white').grid(
                row=i, column=0, sticky='w', padx=(0, 10), pady=5)
            
            # 输入框
            if field == 'participant_type':
                # 参与人类型使用下拉框
                var = tk.StringVar()
                combo = ttk.Combobox(self.detail_frame, textvariable=var,
                                   values=['个人', '事业单位', '企业', '联合申请'], 
                                   state='readonly', font=('Microsoft YaHei', 9), width=37)
                self.form_vars[field] = (var, combo)
                combo.grid(row=i, column=1, sticky='ew', pady=5)
            elif field == 'remarks':
                # 备注使用多行文本框
                var = tk.StringVar()
                entry = tk.Text(self.detail_frame, width=40, height=3, 
                               font=('Microsoft YaHei', 9), wrap='word')
                self.form_vars[field] = (var, entry)
            else:
                var = tk.StringVar()
                entry = tk.Entry(self.detail_frame, textvariable=var, 
                                font=('Microsoft YaHei', 9), width=40)
                self.form_vars[field] = (var, entry)
                entry.grid(row=i, column=1, sticky='ew', pady=5)
        
        # 配置列权重
        self.detail_frame.columnconfigure(1, weight=1)
    
    def create_action_panel(self):
        """创建操作按钮面板"""
        action_frame = tk.Frame(self.right_frame, bg='white', height=40)
        action_frame.pack(fill='x', pady=(10, 0))
        action_frame.pack_propagate(False)
        
        # 按钮
        tk.Button(action_frame, text="保存", 
                 font=('Microsoft YaHei', 10), bg='#3182ce', fg='white',
                 command=self.save_material).pack(side='left', padx=(0, 10))
        
        tk.Button(action_frame, text="重置", 
                 font=('Microsoft YaHei', 10), bg='#d69e2e', fg='white',
                 command=self.reset_form).pack(side='left', padx=(0, 10))
        
        tk.Button(action_frame, text="打开材料文件夹", 
                 font=('Microsoft YaHei', 10), bg='#38a169', fg='white',
                 command=self.open_material_folder).pack(side='left')
    
    def on_material_type_change(self, event):
        """材料类型改变事件"""
        self.current_material_type = self.material_type_var.get()
        self.create_dynamic_form()
        self.refresh_materials()
        self.reset_form()
    
    def refresh_materials(self):
        """刷新材料列表"""
        # 清空树
        for item in self.material_tree.get_children():
            self.material_tree.delete(item)
        
        # 根据材料类型获取数据
        material_type = self.material_type_var.get()
        
        if material_type == '身份证复印件':
            materials = self.id_card_file.get_all_files()
        elif material_type == '统一社会信用代码证书':
            materials = self.usccc_file.get_all_files()
        elif material_type == '合同模板':
            materials = self.contract_file.get_all_files()
        else:
            materials = []
        
        # 添加到树控件
        for material in materials:
            self.material_tree.insert('', 'end', text=material[0], values=(material[1],))
    
    def on_material_select(self, event):
        """材料选择事件"""
        selection = self.material_tree.selection()
        if not selection:
            return
        
        item = self.material_tree.item(selection[0])
        material_id = item['text']
        
        # 获取材料详情
        material_type = self.material_type_var.get()
        
        if material_type == '身份证复印件':
            material = self.id_card_file.get_file_by_id(material_id)
        elif material_type == '统一社会信用代码证书':
            material = self.usccc_file.get_file_by_id(material_id)
        elif material_type == '合同模板':
            material = self.contract_file.get_file_by_id(material_id)
        else:
            material = None
        
        if material:
            self.selected_material = material
            self.load_material_details(material)
    
    def load_material_details(self, material):
        """加载材料详情"""
        # 清空表单
        self.reset_form()
        
        # 根据材料类型填充数据
        material_type = self.material_type_var.get()
        
        if material_type == '身份证复印件':
            fields = ['file_path','person_name', 'gender', 'birthplace', 'id_number', 'remarks']
            for i, field in enumerate(fields):
                if i < len(material) - 2:  # 跳过ID和文件名
                    var, entry = self.form_vars[field]
                    value = material[i + 2] or ''
                    
                    if field == 'remarks':
                        entry.delete(1.0, tk.END)
                        entry.insert(1.0, value)
                    else:
                        var.set(value)
        
        elif material_type == '统一社会信用代码证书':
            fields = ['file_path','organization_name', 'validity_period', 'legal_representative', 'remarks']
            for i, field in enumerate(fields):
                if i < len(material) - 2:  # 跳过ID和文件名
                    var, entry = self.form_vars[field]
                    value = material[i + 2] or ''
                    
                    if field == 'remarks':
                        entry.delete(1.0, tk.END)
                        entry.insert(1.0, value)
                    else:
                        var.set(value)
        
        elif material_type == '合同模板':
            fields = ['file_path','contract_name', 'participant_type', 'remarks']
            for i, field in enumerate(fields):
                if i < len(material) - 2:  # 跳过ID和文件名
                    var, entry = self.form_vars[field]
                    value = material[i + 2] or ''
                    
                    if field == 'remarks':
                        entry.delete(1.0, tk.END)
                        entry.insert(1.0, value)
                    else:
                        var.set(value)
    
    def add_material(self):
        """添加材料"""
        # 选择文件
        material_type = self.material_type_var.get()
        
        if material_type == '身份证复印件':
            filetypes = [("PDF files", "*.pdf"), ("All files", "*.*")]
            initialdir = self.default_path.get_path('id_card_path')
        elif material_type == '统一社会信用代码证书':
            filetypes = [("PDF files", "*.pdf"), ("All files", "*.*")]
            initialdir = self.default_path.get_path('usccc_path')
        elif material_type == '合同模板':
            filetypes = [("Word files", "*.doc;*.docx"), ("All files", "*.*")]
            initialdir = self.default_path.get_path('contract_path')
        else:
            filetypes = [("All files", "*.*")]
            initialdir = None
        
        file_path = filedialog.askopenfilename(
            title=f"选择{material_type}文件",
            filetypes=filetypes,
            initialdir=initialdir
        )
        
        if not file_path:
            return
        
        try:
            # 获取目标文件夹
            if material_type == '身份证复印件':
                target_dir = self.default_path.get_path('id_card_path')
            elif material_type == '统一社会信用代码证书':
                target_dir = self.default_path.get_path('usccc_path')
            elif material_type == '合同模板':
                target_dir = self.default_path.get_path('contract_path')
            else:
                target_dir = LOCAL_CONFIG['BASE_DIR']
            
            if not target_dir or not os.path.exists(target_dir):
                messagebox.showerror("错误", f"{material_type}文件夹不存在")
                return
            
            # 复制文件
            file_name = os.path.basename(file_path)
            target_path = os.path.join(target_dir, file_name)
            shutil.copy2(file_path, target_path)
            
            # 添加到数据库
            if material_type == '身份证复印件':
                self.id_card_file.add_file(file_name, target_path)
            elif material_type == '统一社会信用代码证书':
                self.usccc_file.add_file(file_name, target_path)
            elif material_type == '合同模板':
                self.contract_file.add_file(file_name, target_path)
            
            # 刷新列表
            self.refresh_materials()
            messagebox.showinfo("成功", f"{material_type}文件添加成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"添加文件失败: {str(e)}")
    
    def delete_material(self):
        """删除材料"""
        if not self.selected_material:
            messagebox.showwarning("警告", "请先选择一个材料")
            return
        
        material_type = self.material_type_var.get()
        file_name = self.selected_material[1]
        
        if messagebox.askyesno("确认删除", f"确定要删除{material_type} '{file_name}' 吗？\n这将删除文件和数据记录。"):
            try:
                # 删除文件
                file_path = self.selected_material[2]
                if os.path.exists(file_path):
                    os.remove(file_path)
                
                # 删除数据库记录
                material_id = self.selected_material[0]
                if material_type == '身份证复印件':
                    self.id_card_file.delete_file(material_id)
                elif material_type == '统一社会信用代码证书':
                    self.db.execute_update("DELETE FROM usccc_files WHERE id = ?", (material_id,))
                elif material_type == '合同模板':
                    self.db.execute_update("DELETE FROM contract_files WHERE id = ?", (material_id,))
                
                # 刷新列表
                self.refresh_materials()
                self.reset_form()
                self.selected_material = None
                
                messagebox.showinfo("成功", f"{material_type} '{file_name}' 删除成功")
                
            except Exception as e:
                messagebox.showerror("错误", f"删除文件失败: {str(e)}")
    
    def save_material(self):
        """保存材料"""
        if not self.selected_material:
            messagebox.showwarning("警告", "请先选择一个材料")
            return
        
        try:
            material_type = self.material_type_var.get()
            material_id = self.selected_material[0]
            
            # 获取表单数据
            if material_type == '身份证复印件':
                file_path = self.form_vars['file_path'][0].get()
                person_name = self.form_vars['person_name'][0].get()
                gender = self.form_vars['gender'][0].get()
                birthplace = self.form_vars['birthplace'][0].get()
                id_number = self.form_vars['id_number'][0].get()
                remarks = self.form_vars['remarks'][1].get(1.0, tk.END).strip()
                
                # 更新数据库
                self.id_card_file.update_file(
                    material_id, file_path=file_path, person_name=person_name, gender=gender,
                    birthplace=birthplace, id_number=id_number, remarks=remarks
                )
            
            elif material_type == '统一社会信用代码证书':
                file_path = self.form_vars['file_path'][0].get()
                organization_name = self.form_vars['organization_name'][0].get()
                validity_period = self.form_vars['validity_period'][0].get()
                legal_representative = self.form_vars['legal_representative'][0].get()
                remarks = self.form_vars['remarks'][1].get(1.0, tk.END).strip()
                
                # 更新数据库
                self.db.execute_update(
                    """UPDATE usccc_files SET 
                       file_path = ?, organization_name = ?, validity_period = ?, legal_representative = ?, 
                       remarks = ?, updated_time = ? WHERE id = ?""",
                    (file_path, organization_name, validity_period, legal_representative, 
                     remarks, datetime.now(), material_id)
                )
            
            elif material_type == '合同模板':
                file_path = self.form_vars['file_path'][0].get()
                contract_name = self.form_vars['contract_name'][0].get()
                participant_type = self.form_vars['participant_type'][0].get()
                remarks = self.form_vars['remarks'][1].get(1.0, tk.END).strip()
                
                # 更新数据库
                self.db.execute_update(
                    """UPDATE contract_files SET 
                       file_path = ?, contract_name = ?, participant_type = ?, remarks = ?, updated_time = ?
                       WHERE id = ?""",
                    (file_path, contract_name, participant_type, remarks, datetime.now(), material_id)
                )
            
            # 刷新列表
            self.refresh_materials()
            messagebox.showinfo("成功", f"{material_type}信息保存成功")
            
        except Exception as e:
            messagebox.showerror("错误", f"保存材料失败: {str(e)}")
    
    def reset_form(self):
        """重置表单"""
        if hasattr(self, 'form_vars'):
            for field, (var, entry) in self.form_vars.items():
                if field == 'remarks':
                    entry.delete(1.0, tk.END)
                else:
                    var.set('')
    
    def open_material_folder(self):
        """打开材料文件夹"""
        material_type = self.material_type_var.get()
        
        if material_type == '身份证复印件':
            folder_path = self.default_path.get_path('id_card_path')
        elif material_type == '统一社会信用代码证书':
            folder_path = self.default_path.get_path('usccc_path')
        elif material_type == '合同模板':
            folder_path = self.default_path.get_path('contract_path')
        else:
            folder_path = self.default_path.get_base_dir()  # 替代LOCAL_CONFIG['BASE_DIR']
        
        if folder_path and os.path.exists(folder_path):
            os.startfile(folder_path)
        else:
            messagebox.showerror("错误", f"{material_type}文件夹不存在")
