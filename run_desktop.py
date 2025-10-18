#!/usr/bin/env python3
"""
郑州医企创医疗科技有限公司 - 软著管理系统
桌面应用启动脚本
"""

import os
import sys
import warnings
import tkinter as tk
from tkinter import messagebox

# 抑制libpng警告
warnings.filterwarnings("ignore", ".*iCCP.*")
os.environ['PYTHONWARNINGS'] = 'ignore::UserWarning'

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
    
    app = None
    try:
        # 导入并启动应用
        from desktop_app.main_with_login import SoftwareCopyrightMS
        
        print("正在初始化桌面应用...")
        app = SoftwareCopyrightMS()
        
        print("桌面应用已启动")
        print("=" * 60)
        
        app.run()
        
    except ImportError as e:
        print(f"[ERROR] 导入错误: {e}")
        try:
            messagebox.showerror("导入错误", f"无法导入应用模块: {e}")
        except:
            pass
    except KeyboardInterrupt:
        print("\n[DEBUG] 用户中断程序")
    except Exception as e:
        print(f"[ERROR] 启动错误: {e}")
        try:
            messagebox.showerror("启动错误", f"应用启动失败: {e}")
        except:
            pass
    finally:
        # 确保清理资源
        if app:
            try:
                print("[DEBUG] 程序退出，清理资源...")
                app._cleanup_on_exit()
            except Exception as e:
                print(f"[DEBUG] 清理资源时出错: {e}")
        
        print("[DEBUG] 程序已退出")

if __name__ == '__main__':
    main()
