#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tkinter事件处理器 - 防止主题变更事件错误
"""

import tkinter as tk
from tkinter import ttk
import atexit
import signal
import sys
import os
import threading

class TkinterEventManager:
    """Tkinter事件管理器"""
    
    _instance = None
    _initialized = False
    _lock = threading.Lock()  # 添加线程锁
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # 双重检查锁定模式
                if cls._instance is None:
                    cls._instance = super(TkinterEventManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        print(f"[DEBUG] TkinterEventManager.__init__ 调用, initialized={self._initialized}")
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    print("[DEBUG] 初始化TkinterEventManager")
                    self._original_theme_changed = None
                    self._is_cleanup_active = False
                    self._install_event_handlers()
                    TkinterEventManager._initialized = True
                    print("[DEBUG] TkinterEventManager初始化完成")
    
    def _install_event_handlers(self):
        """安装事件处理器"""
        print("[DEBUG] 开始安装事件处理器")
        try:
            # 保存原始的主题变更函数
            if hasattr(ttk, '_ThemeChanged'):
                print("[DEBUG] 保存原始的ttk._ThemeChanged函数")
                self._original_theme_changed = ttk._ThemeChanged
                
                # 替换为安全版本
                print("[DEBUG] 替换ttk._ThemeChanged为安全版本")
                ttk._ThemeChanged = self._safe_theme_changed
                print("[DEBUG] Tkinter主题事件处理器已安装")
            else:
                print("[DEBUG] ttk._ThemeChanged属性不存在")
            
            # 额外保护：重写ttk.Style的theme_use方法
            print("[DEBUG] 修补ttk.Style的theme_use方法")
            self._patch_ttk_style()
            
            # 注册程序退出时的清理函数
            print("[DEBUG] 注册程序退出时的清理函数")
            atexit.register(self._cleanup_on_exit)
            
            # 注册信号处理器
            try:
                print("[DEBUG] 注册信号处理器")
                if hasattr(signal, 'SIGTERM'):
                    signal.signal(signal.SIGTERM, self._signal_handler)
                if hasattr(signal, 'SIGINT'):
                    signal.signal(signal.SIGINT, self._signal_handler)
                print("[DEBUG] 信号处理器注册完成")
            except Exception as e:
                print(f"[DEBUG] 注册信号处理器失败: {e}")
                
        except Exception as e:
            print(f"[DEBUG] 安装Tkinter事件处理器失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _patch_ttk_style(self):
        """修补ttk.Style的theme_use方法"""
        print("[DEBUG] 开始修补ttk.Style的theme_use方法")
        try:
            original_theme_use = ttk.Style.theme_use
            
            def safe_theme_use(self, themeName=None):
                try:
                    print(f"[DEBUG] safe_theme_use 调用, themeName={themeName}")
                    # 检查Tkinter是否仍然有效
                    if self._is_tkinter_valid():
                        print("[DEBUG] Tkinter有效，调用原始theme_use方法")
                        result = original_theme_use(self, themeName)
                        print(f"[DEBUG] theme_use 返回结果: {result}")
                        return result
                    else:
                        print("[DEBUG] 跳过theme_use，Tkinter已无效")
                        return None
                except Exception as e:
                    print(f"[DEBUG] theme_use异常: {e}")
                    import traceback
                    traceback.print_exc()
                    return None
            
            ttk.Style.theme_use = safe_theme_use
            print("[DEBUG] ttk.Style.theme_use已修补")
            
        except Exception as e:
            print(f"[DEBUG] 修补ttk.Style失败: {e}")
            import traceback
            traceback.print_exc()

    def _is_tkinter_valid(self):
        """检查Tkinter是否仍然有效"""
        print("[DEBUG] 检查Tkinter是否有效")
        try:
            # 检查是否有活动的Tkinter窗口
            if hasattr(tk, '_default_root') and tk._default_root:
                root = tk._default_root
                print(f"[DEBUG] 存在_default_root: {root}")
                # 使用winfo_exists()检查窗口是否仍然存在
                exists = root.winfo_exists()
                print(f"[DEBUG] root.winfo_exists(): {exists}")
                return exists
            else:
                # 没有默认根窗口，认为无效
                print("[DEBUG] 不存在_default_root或_default_root为None")
                return False
        except Exception as e:
            # 出现任何异常都认为无效
            print(f"[DEBUG] 检查Tkinter有效性时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _safe_theme_changed(self):
        """安全的主题变更处理函数"""
        print("[DEBUG] _safe_theme_changed 调用")
        try:
            # 如果正在清理，跳过主题变更
            if self._is_cleanup_active:
                print("[DEBUG] 跳过主题变更事件，程序正在清理")
                return
            
            # 检查Tkinter是否仍然有效
            print("[DEBUG] 检查Tkinter有效性")
            is_valid = self._is_tkinter_valid()
            print(f"[DEBUG] Tkinter有效性检查结果: {is_valid}")
            
            if is_valid:
                # 只有在有活动窗口时才执行主题变更
                if self._original_theme_changed:
                    print("[DEBUG] 调用原始_theme_changed函数")
                    self._original_theme_changed()
                    print("[DEBUG] 原始_theme_changed函数调用完成")
                else:
                    print("[DEBUG] 原始_theme_changed函数不存在")
            else:
                print("[DEBUG] 跳过主题变更事件，Tkinter已无效")
                
        except tk.TclError as e:
            # 特别处理TclError，这是最常见的主题变更错误
            print(f"[DEBUG] TclError主题变更事件: {e}")
        except Exception as e:
            # 忽略所有主题变更相关的错误
            print(f"[DEBUG] 主题变更事件处理异常: {e}")
            import traceback
            traceback.print_exc()
    
    def _cleanup_on_exit(self):
        """程序退出时的清理"""
        print("[DEBUG] 开始Tkinter事件清理...")
        try:
            self._is_cleanup_active = True
            print("[DEBUG] 设置清理标志为True")
            
            # 恢复原始函数
            if self._original_theme_changed and hasattr(ttk, '_ThemeChanged'):
                print("[DEBUG] 恢复原始主题变更函数")
                ttk._ThemeChanged = self._original_theme_changed
                print("[DEBUG] 已恢复原始主题变更函数")
            
            print("[DEBUG] Tkinter事件清理完成")
            
        except Exception as e:
            print(f"[DEBUG] Tkinter事件清理失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"[DEBUG] 收到信号 {signum}，开始Tkinter事件清理...")
        self._cleanup_on_exit()
        sys.exit(0)
    
    def force_cleanup(self):
        """强制清理Tkinter事件"""
        print("[DEBUG] 强制清理Tkinter事件")
        self._cleanup_on_exit()

# 全局事件管理器实例
_event_manager = None
_manager_lock = threading.Lock()

def get_event_manager():
    """获取事件管理器实例"""
    global _event_manager
    print("[DEBUG] 获取事件管理器实例")
    with _manager_lock:
        if _event_manager is None:
            print("[DEBUG] 创建新的事件管理器实例")
            _event_manager = TkinterEventManager()
        else:
            print("[DEBUG] 返回现有的事件管理器实例")
    return _event_manager

def install_tkinter_event_handler():
    """安装Tkinter事件处理器"""
    print("[DEBUG] install_tkinter_event_handler 调用")
    try:
        manager = get_event_manager()
        print("[DEBUG] Tkinter事件处理器已安装")
        return True
    except Exception as e:
        print(f"[DEBUG] 安装Tkinter事件处理器失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup_tkinter_events():
    """清理Tkinter事件"""
    print("[DEBUG] cleanup_tkinter_events 调用")
    try:
        manager = get_event_manager()
        manager.force_cleanup()
        return True
    except Exception as e:
        print(f"[DEBUG] 清理Tkinter事件失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 自动安装事件处理器
print("[DEBUG] 模块加载时自动安装事件处理器")
if __name__ != "__main__":
    install_tkinter_event_handler()

# 测试代码
if __name__ == "__main__":
    print("测试Tkinter事件处理器...")
    
    # 安装事件处理器
    install_tkinter_event_handler()
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("Tkinter事件处理器测试")
    root.geometry("400x300")
    
    # 添加一些测试组件
    frame = ttk.Frame(root, padding="20")
    frame.pack(fill='both', expand=True)
    
    label = ttk.Label(frame, text="Tkinter事件处理器测试")
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