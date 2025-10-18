#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全局Tkinter事件处理器 - 强制防止主题变更事件错误
在程序启动时立即安装，确保所有Tkinter操作都被保护
"""

import tkinter as tk
from tkinter import ttk
import atexit
import signal
import sys
import os
import threading

# 全局标志
_tkinter_protection_installed = False
_protection_lock = threading.Lock()

def force_install_tkinter_protection():
    """强制安装Tkinter保护"""
    global _tkinter_protection_installed
    
    with _protection_lock:
        if _tkinter_protection_installed:
            return True
        
        try:
            print("[DEBUG] 强制安装Tkinter保护...")
            
            # 1. 保护ttk._ThemeChanged
            if hasattr(ttk, '_ThemeChanged'):
                original_theme_changed = ttk._ThemeChanged
                
                def safe_theme_changed():
                    try:
                        # 检查是否有活动的Tkinter窗口
                        if hasattr(tk, '_default_root') and tk._default_root:
                            root = tk._default_root
                            if root.winfo_exists():
                                original_theme_changed()
                            else:
                                print("[DEBUG] 跳过ThemeChanged，根窗口已销毁")
                        else:
                            print("[DEBUG] 跳过ThemeChanged，没有默认根窗口")
                    except Exception as e:
                        print(f"[DEBUG] ThemeChanged异常: {e}")
                
                ttk._ThemeChanged = safe_theme_changed
                print("[DEBUG] ttk._ThemeChanged已保护")
            
            # 2. 保护ttk.Style.theme_use
            original_theme_use = ttk.Style.theme_use
            
            def safe_theme_use(self, themeName=None):
                try:
                    if hasattr(tk, '_default_root') and tk._default_root:
                        root = tk._default_root
                        if root.winfo_exists():
                            return original_theme_use(self, themeName)
                        else:
                            print("[DEBUG] 跳过theme_use，根窗口已销毁")
                            return None
                    else:
                        print("[DEBUG] 跳过theme_use，没有默认根窗口")
                        return None
                except Exception as e:
                    print(f"[DEBUG] theme_use异常: {e}")
                    return None
            
            ttk.Style.theme_use = safe_theme_use
            print("[DEBUG] ttk.Style.theme_use已保护")
            
            # 3. 保护所有可能的主题相关方法
            _protect_all_theme_methods()
            
            # 4. 注册清理函数
            atexit.register(_cleanup_on_exit)
            
            # 5. 注册信号处理器
            try:
                signal.signal(signal.SIGTERM, _signal_handler)
                signal.signal(signal.SIGINT, _signal_handler)
                print("[DEBUG] 信号处理器已注册")
            except Exception as e:
                print(f"[DEBUG] 注册信号处理器失败: {e}")
            
            _tkinter_protection_installed = True
            print("[DEBUG] Tkinter保护安装完成")
            return True
            
        except Exception as e:
            print(f"[DEBUG] 安装Tkinter保护失败: {e}")
            return False

def _protect_all_theme_methods():
    """保护所有可能的主题相关方法"""
    try:
        # 保护ttk.Style的其他方法
        style_methods_to_protect = [
            'theme_names', 'theme_settings', 'lookup', 'map', 'configure',
            'layout', 'element_create', 'element_names', 'element_options'
        ]
        
        for method_name in style_methods_to_protect:
            if hasattr(ttk.Style, method_name):
                original_method = getattr(ttk.Style, method_name)
                
                def create_safe_method(orig_method):
                    def safe_method(self, *args, **kwargs):
                        try:
                            if hasattr(tk, '_default_root') and tk._default_root:
                                root = tk._default_root
                                if root.winfo_exists():
                                    return orig_method(self, *args, **kwargs)
                                else:
                                    print(f"[DEBUG] 跳过{method_name}，根窗口已销毁")
                                    return None
                            else:
                                print(f"[DEBUG] 跳过{method_name}，没有默认根窗口")
                                return None
                        except Exception as e:
                            print(f"[DEBUG] {method_name}异常: {e}")
                            return None
                    return safe_method
                
                setattr(ttk.Style, method_name, create_safe_method(original_method))
        
        print("[DEBUG] 所有主题相关方法已保护")
        
    except Exception as e:
        print(f"[DEBUG] 保护主题方法失败: {e}")

def _cleanup_on_exit():
    """程序退出时的清理"""
    try:
        print("[DEBUG] 开始Tkinter保护清理...")
        
        # 恢复原始函数（如果需要）
        # 这里可以添加恢复逻辑
        
        print("[DEBUG] Tkinter保护清理完成")
        
    except Exception as e:
        print(f"[DEBUG] Tkinter保护清理失败: {e}")

def _signal_handler(signum, frame):
    """信号处理器"""
    print(f"[DEBUG] 收到信号 {signum}，开始Tkinter保护清理...")
    _cleanup_on_exit()
    sys.exit(0)

def ensure_tkinter_protection():
    """确保Tkinter保护已安装"""
    if not _tkinter_protection_installed:
        return force_install_tkinter_protection()
    return True

def is_tkinter_protection_installed():
    """检查Tkinter保护是否已安装"""
    return _tkinter_protection_installed

# 自动安装保护
if __name__ != "__main__":
    # 在模块导入时自动安装保护
    force_install_tkinter_protection()

# 测试代码
if __name__ == "__main__":
    print("测试全局Tkinter保护...")
    
    # 安装保护
    success = force_install_tkinter_protection()
    print(f"保护安装: {'成功' if success else '失败'}")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("Tkinter保护测试")
    root.geometry("400x300")
    
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill='both', expand=True)
    
    label = ttk.Label(frame, text="Tkinter保护测试")
    label.pack(pady=10)
    
    button = ttk.Button(frame, text="测试主题变更", 
                       command=lambda: ttk.Style().theme_use('clam'))
    button.pack(pady=10)
    
    close_button = ttk.Button(frame, text="关闭", command=root.quit)
    close_button.pack(pady=10)
    
    print("测试窗口已创建，请测试主题变更功能")
    
    # 运行主循环
    root.mainloop()
    
    print("测试完成")
