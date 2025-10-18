#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tkinter应用程序基类 - 修复主题变更事件错误
"""

import tkinter as tk
from tkinter import ttk
import threading
import atexit
import signal
import sys
import os

class SafeTkinterApp:
    """安全的Tkinter应用程序基类"""
    
    def __init__(self):
        self.root = None
        self._is_destroyed = False
        self._cleanup_functions = []
        
        # 注册退出处理
        atexit.register(self._safe_cleanup)
        
        # 注册信号处理
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._signal_handler)
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"[DEBUG] 收到信号 {signum}，开始安全退出...")
        self._safe_cleanup()
        sys.exit(0)
    
    def _safe_cleanup(self):
        """安全清理资源"""
        if self._is_destroyed:
            return
        
        self._is_destroyed = True
        
        try:
            print("[DEBUG] 开始安全清理资源...")
            
            # 执行注册的清理函数
            for cleanup_func in self._cleanup_functions:
                try:
                    cleanup_func()
                except Exception as e:
                    print(f"[DEBUG] 清理函数执行失败: {e}")
            
            # 清理Tkinter资源
            if self.root and self.root.winfo_exists():
                try:
                    # 取消所有待处理的事件
                    self.root.after_cancel("all")
                except:
                    pass
                
                try:
                    # 销毁窗口
                    self.root.destroy()
                except Exception as e:
                    print(f"[DEBUG] 销毁窗口失败: {e}")
            
            print("[DEBUG] 安全清理完成")
            
        except Exception as e:
            print(f"[DEBUG] 安全清理过程中出错: {e}")
    
    def add_cleanup_function(self, func):
        """添加清理函数"""
        self._cleanup_functions.append(func)
    
    def create_root(self, **kwargs):
        """创建根窗口"""
        if self.root is None:
            self.root = tk.Tk(**kwargs)
            
            # 设置窗口关闭事件
            self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
            
            # 禁用主题变更事件处理
            self._disable_theme_events()
        
        return self.root
    
    def _disable_theme_events(self):
        """禁用主题变更事件"""
        try:
            # 重写ttk的ThemeChanged函数，避免在窗口销毁后执行
            original_theme_changed = ttk._ThemeChanged
            
            def safe_theme_changed():
                try:
                    if self.root and self.root.winfo_exists():
                        original_theme_changed()
                except Exception:
                    pass  # 忽略主题变更错误
            
            ttk._ThemeChanged = safe_theme_changed
            
        except Exception as e:
            print(f"[DEBUG] 禁用主题事件失败: {e}")
    
    def _on_closing(self):
        """窗口关闭事件处理"""
        print("[DEBUG] 窗口关闭事件触发")
        self._safe_cleanup()
        
        # 强制退出进程
        try:
            os._exit(0)
        except:
            sys.exit(0)
    
    def run(self):
        """运行应用程序"""
        if not self.root:
            raise RuntimeError("根窗口未创建，请先调用create_root()")
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("[DEBUG] 用户中断程序")
        except Exception as e:
            print(f"[DEBUG] 主循环异常: {e}")
        finally:
            self._safe_cleanup()

# 使用示例
if __name__ == "__main__":
    app = SafeTkinterApp()
    
    # 创建根窗口
    root = app.create_root()
    root.title("测试应用")
    root.geometry("400x300")
    
    # 添加一些测试组件
    label = ttk.Label(root, text="这是一个安全的Tkinter应用")
    label.pack(pady=20)
    
    button = ttk.Button(root, text="关闭", command=root.quit)
    button.pack(pady=10)
    
    # 添加清理函数
    def cleanup_test():
        print("[DEBUG] 测试清理函数执行")
    
    app.add_cleanup_function(cleanup_test)
    
    # 运行应用
    app.run()
