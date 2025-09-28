#!/usr/bin/env python3
"""
郑州医企创医疗科技有限公司 - 软著管理系统
桌面应用启动脚本
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox

def check_dependencies():
    """检查依赖项"""
    try:
        import requests
        import sqlite3
        import webbrowser
        import shutil
        return True
    except ImportError as e:
        messagebox.showerror("依赖错误", f"缺少必要的依赖项: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("郑州医企创医疗科技有限公司 - 软著管理系统")
    print("桌面客户端启动中...")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        return
    
    try:
        # 导入并启动应用
        from desktop_app.main import SoftwareCopyrightMS
        
        print("正在初始化桌面应用...")
        app = SoftwareCopyrightMS()
        
        print("桌面应用已启动")
        print("=" * 60)
        
        app.run()
        
    except ImportError as e:
        messagebox.showerror("导入错误", f"无法导入应用模块: {e}")
    except Exception as e:
        messagebox.showerror("启动错误", f"应用启动失败: {e}")
        print(f"错误详情: {e}")

if __name__ == '__main__':
    main()
