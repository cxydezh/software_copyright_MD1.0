#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
选择对话框测试脚本
测试模板选择、身份证、统一社会信用代码证书、合同文件选择对话框
"""

import sys
import os
import tkinter as tk
from tkinter import ttk

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import LOCAL_CONFIG
from desktop_app.local_models import (LocalDatabase, TemplateFolder, IDCardFile,
                                      USCCCFile, ContractFile)
from desktop_app.selection_dialogs import (TemplateSelectionDialog, IDCardFileDialog,
                                           USCCCFileDialog, ContractFileDialog)


class TestApp:
    """测试应用"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("选择对话框测试")
        self.root.geometry("400x300")
        
        # 初始化数据库
        db_path = LOCAL_CONFIG['LOCAL_DB_PATH']
        self.db = LocalDatabase(db_path)
        
        # 初始化模型
        self.template_folder = TemplateFolder(self.db)
        self.id_card_file = IDCardFile(self.db)
        self.usccc_file = USCCCFile(self.db)
        self.contract_file = ContractFile(self.db)
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建测试界面"""
        # 标题
        ttk.Label(self.root, text="选择对话框测试工具", 
                 font=('Arial', 14, 'bold')).pack(pady=20)
        
        # 按钮框架
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # 测试按钮
        ttk.Button(button_frame, text="测试模板选择对话框", 
                  command=self.test_template_dialog, width=25).pack(pady=5)
        
        ttk.Button(button_frame, text="测试身份证选择对话框", 
                  command=self.test_idcard_dialog, width=25).pack(pady=5)
        
        ttk.Button(button_frame, text="测试证书选择对话框", 
                  command=self.test_usccc_dialog, width=25).pack(pady=5)
        
        ttk.Button(button_frame, text="测试合同选择对话框", 
                  command=self.test_contract_dialog, width=25).pack(pady=5)
        
        ttk.Separator(self.root, orient='horizontal').pack(fill='x', pady=10)
        
        # 结果显示
        ttk.Label(self.root, text="测试结果:").pack()
        self.result_var = tk.StringVar(value="等待测试...")
        ttk.Label(self.root, textvariable=self.result_var, 
                 wraplength=350).pack(pady=10)
    
    def test_template_dialog(self):
        """测试模板选择对话框"""
        try:
            # 创建测试项目信息
            project_id = 999
            project_name = "测试项目"
            target_folder = os.path.join(os.path.dirname(__file__), "test_output")
            
            # 确保目标文件夹存在
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            
            # 打开对话框
            dialog = TemplateSelectionDialog(
                self.root,
                self.template_folder,
                project_id=project_id,
                project_name=project_name,
                target_folder=target_folder
            )
            
            result = dialog.show()
            
            if result:
                self.result_var.set(f"✓ 模板已复制到: {result}")
            else:
                self.result_var.set("✗ 用户取消操作")
        
        except Exception as e:
            self.result_var.set(f"✗ 错误: {str(e)}")
    
    def test_idcard_dialog(self):
        """测试身份证选择对话框"""
        try:
            target_folder = os.path.join(os.path.dirname(__file__), "test_output", "idcards")
            
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            
            dialog = IDCardFileDialog(
                self.root,
                self.id_card_file,
                target_folder=target_folder
            )
            
            result = dialog.show()
            
            if result:
                self.result_var.set(f"✓ 文件已复制到: {result}")
            else:
                self.result_var.set("✗ 用户取消操作")
        
        except Exception as e:
            self.result_var.set(f"✗ 错误: {str(e)}")
    
    def test_usccc_dialog(self):
        """测试统一社会信用代码证书选择对话框"""
        try:
            target_folder = os.path.join(os.path.dirname(__file__), "test_output", "usccc")
            
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            
            dialog = USCCCFileDialog(
                self.root,
                self.usccc_file,
                target_folder=target_folder
            )
            
            result = dialog.show()
            
            if result:
                self.result_var.set(f"✓ 文件已复制到: {result}")
            else:
                self.result_var.set("✗ 用户取消操作")
        
        except Exception as e:
            self.result_var.set(f"✗ 错误: {str(e)}")
    
    def test_contract_dialog(self):
        """测试合同文件选择对话框"""
        try:
            target_folder = os.path.join(os.path.dirname(__file__), "test_output", "contracts")
            
            if not os.path.exists(target_folder):
                os.makedirs(target_folder)
            
            dialog = ContractFileDialog(
                self.root,
                self.contract_file,
                target_folder=target_folder
            )
            
            result = dialog.show()
            
            if result:
                self.result_var.set(f"✓ 文件已复制到: {result}")
            else:
                self.result_var.set("✗ 用户取消操作")
        
        except Exception as e:
            self.result_var.set(f"✗ 错误: {str(e)}")


if __name__ == '__main__':
    root = tk.Tk()
    app = TestApp(root)
    root.mainloop()

