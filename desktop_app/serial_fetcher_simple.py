#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版权中心流水号获取模块 - 简化版
"""

import os
import sys
from typing import Optional
from tkinter import messagebox

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

TARGET_URL = 'https://register.ccopyright.com.cn/account.html?current=soft_register'

# 全局浏览器实例变量
_global_browser_context = None
_global_browser_page = None
_global_browser_instance = None
_global_playwright_instance = None

def cleanup_on_exit():
    """程序退出时的清理函数"""
    try:
        print("[DEBUG] 开始清理浏览器实例...")
        clear_global_browser()
        print("[DEBUG] 浏览器实例清理完成")
    except Exception as e:
        print(f"[DEBUG] 清理浏览器实例时出错: {e}")

# 注册程序退出时的清理函数
import atexit
atexit.register(cleanup_on_exit)

def clear_global_browser():
    """清除全局浏览器实例"""
    global _global_browser_context, _global_browser_page, _global_browser_instance, _global_playwright_instance
    
    try:
        if _global_playwright_instance:
            try:
                print("[DEBUG] 正在停止Playwright实例...")
                _global_playwright_instance.stop()
                print("[DEBUG] Playwright实例已停止")
            except Exception as e:
                print(f"[DEBUG] 停止Playwright实例时出错: {e}")
        
        _global_browser_context = None
        _global_browser_page = None
        _global_browser_instance = None
        _global_playwright_instance = None
        print("[DEBUG] 全局浏览器实例已清除")
    except Exception as e:
        print(f"[DEBUG] 清除全局浏览器实例时出错: {e}")

def set_global_browser(context, page, instance, playwright_instance):
    """设置全局浏览器实例"""
    global _global_browser_context, _global_browser_page, _global_browser_instance, _global_playwright_instance
    
    _global_browser_context = context
    _global_browser_page = page
    _global_browser_instance = instance
    _global_playwright_instance = playwright_instance
    print("[DEBUG] 全局浏览器实例已设置")

def get_global_browser():
    """获取全局浏览器实例"""
    return _global_browser_context, _global_browser_page, _global_browser_instance, _global_playwright_instance

def is_browser_instance_valid(context, page, instance):
    """检测浏览器实例是否仍然有效"""
    try:
        if not context or not page or not instance:
            print("[DEBUG] 浏览器实例参数不完整")
            return False
        
        # 检查context是否已关闭
        if hasattr(context, '_closed') and context._closed:
            print("[DEBUG] 浏览器上下文已关闭")
            return False
        
        # 检查browser是否已关闭
        if hasattr(instance, 'is_connected') and not instance.is_connected():
            print("[DEBUG] 浏览器实例已断开连接")
            return False
        
        # 尝试访问页面URL来检测是否仍然有效
        try:
            current_url = page.url
            print(f"[DEBUG] 检测浏览器实例有效性，当前URL: {current_url}")
            
            # 尝试执行一个简单的JavaScript来进一步验证页面是否响应
            page.evaluate("() => document.title")
            print("[DEBUG] JavaScript执行成功")
            
            # 额外检查：尝试获取页面内容来确保浏览器真正可用
            try:
                page.content()
                print("[DEBUG] 页面内容获取成功，浏览器实例有效")
                return True
            except Exception as content_e:
                print(f"[DEBUG] 页面内容获取失败，浏览器可能已关闭: {content_e}")
                return False
                
        except Exception as url_e:
            print(f"[DEBUG] 页面访问失败，浏览器可能已关闭: {url_e}")
            return False
            
    except Exception as e:
        print(f"[DEBUG] 浏览器实例已失效: {e}")
        return False

def get_valid_global_browser():
    """获取有效的全局浏览器实例，如果无效则清除"""
    print("[DEBUG] get_valid_global_browser 调用")
    context, page, instance, playwright_instance = get_global_browser()
    print(f"[DEBUG] 获取到的浏览器实例: context={bool(context)}, page={bool(page)}, instance={bool(instance)}")
    
    if context and page and instance:
        print("[DEBUG] 存在浏览器实例，检查有效性")
        if is_browser_instance_valid(context, page, instance):
            print("[DEBUG] 检测到有效的浏览器实例")
            return context, page, instance, playwright_instance
        else:
            print("[DEBUG] 浏览器实例已失效，清除全局变量")
            clear_global_browser()
            return None, None, None, None
    else:
        print("[DEBUG] 没有浏览器实例")
        return None, None, None, None

def is_playwright_available():
    """检测系统是否安装了Playwright"""
    print("[DEBUG] 检查Playwright是否可用")
    try:
        from playwright.sync_api import sync_playwright
        print("[DEBUG] Playwright导入成功")
        return True
    except ImportError as e:
        print(f"[DEBUG] Playwright导入失败: {e}")
        return False

def fetch_serial_for_project(project_name: str, applicant_name: Optional[str] = None, reuse_browser: bool = True, use_temp_profile: bool = False) -> Optional[str]:
    """从版权中心页面抓取与项目匹配的流水号"""
    print(f"[DEBUG] 开始获取流水号，项目名称: {project_name}, 申请人: {applicant_name}, 复用浏览器: {reuse_browser}")
    
    try:
        from playwright.sync_api import sync_playwright
        print("[DEBUG] Playwright 导入成功")
    except Exception as e:
        print(f"[DEBUG] Playwright 导入失败: {e}")
        messagebox.showerror("错误", f"Playwright 导入失败，请确保已安装并运行 'playwright install': {e}")
        return None

    if not is_playwright_available():
        messagebox.showerror("错误", "Playwright 未安装，请运行 'playwright install' 安装")
        return None

    try:
        from playwright.sync_api import sync_playwright
        
        # 检查是否复用现有浏览器
        if reuse_browser:
            context, page, instance, playwright_instance = get_valid_global_browser()
            if context and page and instance:
                print("[DEBUG] 复用现有浏览器实例")
                try:
                    # 检查当前页面是否在版权中心
                    current_url = page.url
                    if 'https://register.ccopyright.com.cn/account.html?current=soft_register' in current_url:
                        print("[DEBUG] 当前页面在版权中心，直接获取流水号")
                        return _extract_serial_number(page, project_name, applicant_name)
                    else:
                        print("[DEBUG] 当前页面不在版权中心，导航到版权中心")
                        page.goto(TARGET_URL, wait_until='domcontentloaded', timeout=30000)
                        page.wait_for_load_state('networkidle', timeout=10000)
                        return _extract_serial_number(page, project_name, applicant_name)
                except Exception as e:
                    print(f"[DEBUG] 复用浏览器失败: {e}")
                    print("[DEBUG] 清除失效的浏览器实例，创建新实例")
                    clear_global_browser()
        
        # 创建新的浏览器实例
        print("[DEBUG] 创建新的浏览器实例")
        p = sync_playwright().start()
        
        try:
            # 获取屏幕尺寸
            try:
                import tkinter as tk
                root = tk.Tk()
                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()
                root.destroy()
                print(f"[DEBUG] 获取屏幕尺寸: {screen_width}x{screen_height}")
            except Exception as e:
                print(f"[DEBUG] 获取屏幕尺寸失败: {e}")
                screen_width = 1920
                screen_height = 1080
                print(f"[DEBUG] 使用默认屏幕尺寸: {screen_width}x{screen_height}")
            
            # 启动浏览器
            print("[DEBUG] 启动Chromium浏览器")
            
            browser = p.chromium.launch(
                headless=False,
                args=[
                    '--start-maximized',
                    '--no-sandbox',
                    '--disable-web-security',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-first-run',
                ]
            )
            print("[DEBUG] Chromium浏览器启动完成")
            
            # 创建新的上下文
            print("[DEBUG] 创建浏览器上下文")
            context = browser.new_context(
                viewport={'width': screen_width, 'height': screen_height},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='zh-CN',
                timezone_id='Asia/Shanghai',
            )
            print("[DEBUG] 浏览器上下文创建完成")
            
            # 创建新页面
            print("[DEBUG] 创建新页面")
            page = context.new_page()
            print("[DEBUG] 新页面创建完成")
            
            # 设置页面视口为全屏
            print("[DEBUG] 设置页面视口")
            page.set_viewport_size({'width': screen_width, 'height': screen_height})
            print("[DEBUG] 页面视口设置完成")
            
            # 注入反检测脚本
            print("[DEBUG] 注入反检测脚本")
            try:
                page.evaluate("""
                    (function() {
                        // 隐藏webdriver属性
                        Object.defineProperty(navigator, 'webdriver', {
                            get: () => undefined,
                        });
                        
                        // 添加chrome对象
                        window.chrome = {
                            runtime: {},
                        };
                    })();
                """)
                print("[DEBUG] 反检测脚本注入成功")
            except Exception as e:
                print(f"[DEBUG] 反检测脚本注入失败: {e}")
            
            # 导航到目标页面
            print(f"[DEBUG] 导航到: {TARGET_URL}")
            page.goto(TARGET_URL, wait_until='domcontentloaded', timeout=30000)
            print("[DEBUG] 页面导航成功")
            
            print("[DEBUG] 等待页面网络空闲")
            page.wait_for_load_state('networkidle', timeout=10000)
            print("[DEBUG] 页面网络空闲")
            
            # 页面加载完成后，检查是否需要自动填充
            print("[DEBUG] 页面加载完成，检查自动填充")
            from desktop_app.credential_manager import load_credentials, has_credentials
            
            if has_credentials():
                print("[DEBUG] 发现保存的账号密码，立即开始自动填充")
                username, password = load_credentials()
                
                print("[DEBUG] 开始立即填充账号密码")
                
                # 尝试多种可能的用户名输入框选择器
                username_selectors = [
                    'input[placeholder*="请输入用户名/手机号/邮箱"]'
                ]
                
                # 尝试多种可能的密码输入框选择器
                password_selectors = [
                    'input[placeholder*="请输入密码"]'
                ]
                
                # 填充用户名
                username_filled = False
                for selector in username_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=1000)
                        page.fill(selector, username)
                        print(f"[DEBUG] 用户名已填充: {selector}")
                        username_filled = True
                        break
                    except Exception:
                        continue
                
                # 填充密码
                password_filled = False
                for selector in password_selectors:
                    try:
                        page.wait_for_selector(selector, timeout=1000)
                        page.fill(selector, password)
                        print(f"[DEBUG] 密码已填充: {selector}")
                        password_filled = True
                        break
                    except Exception:
                        continue
                
                if username_filled and password_filled:
                    print("[DEBUG] 账号密码自动填充完成")
                    messagebox.showinfo("提示", "账号密码自动填充完成,登录成功后请进入用户中心")
                else:
                    print("[DEBUG] 自动填充部分失败，请手动输入")
            else:
                print("[DEBUG] 未发现保存的账号密码，请手动输入")
            
            # 保存浏览器实例到全局变量
            print("[DEBUG] 保存浏览器实例到全局变量")
            set_global_browser(context, page, browser, p)
            print("[DEBUG] 浏览器实例已保存，用户可继续使用")
            
            # 获取流水号
            return _extract_serial_number(page, project_name, applicant_name)
            
        except Exception as e:
            print(f"[DEBUG] 浏览器操作失败: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    except Exception as e:
        print(f"[DEBUG] 获取流水号失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def _extract_serial_number(page, project_name: str, applicant_name: Optional[str] = None) -> Optional[str]:
    """从页面中提取流水号"""
    try:
        print(f"[DEBUG] 开始搜索项目: {project_name}")
        
        # 等待页面加载完成
        page.wait_for_load_state('networkidle', timeout=10000)
        
        # 搜索项目名称
        try:
            # 尝试查找搜索框
            search_selectors = [
                'input[placeholder*="输入流水号/名称"]'
            ]
            
            search_filled = False
            for selector in search_selectors:
                try:
                    page.wait_for_selector(selector, timeout=2000)
                    page.fill(selector, project_name)
                    print(f"[DEBUG] 项目名称已填入搜索框: {selector}")
                    search_filled = True
                    break
                except Exception:
                    continue
            
            if not search_filled:
                print("[DEBUG] 未找到搜索框，尝试在页面中查找项目")
            
            # 等待100ms后，点击搜索按钮
            page.wait_for_timeout(100)
            search_button_selectors = [
                'button:has-text("查询")'
            ]
            for selector in search_button_selectors:
                try:
                    page.click(selector)
                    break
                except:
                    continue
            
            # 等待搜索结果
            page.wait_for_timeout(2000)
            
            # 查找包含项目名称的元素
            project_elements = page.query_selector_all(f'text="{project_name}"')
            if not project_elements:
                # 尝试模糊匹配
                project_elements = page.query_selector_all(f'text*="{project_name}"')
            
            if project_elements:
                print(f"[DEBUG] 找到 {len(project_elements)} 个匹配的项目元素")
                
                for element in project_elements:
                    try:
                        # 查找附近的流水号
                        parent = element.query_selector('xpath=..')
                        if parent:
                            # 查找包含"流水号"或"编号"的文本
                            serial_text = parent.inner_text()
                            if '流水号' in serial_text or '编号' in serial_text:
                                # 从 serial_text 中提取“流水号：”后面的字母数字串
                                import re
                                serial_number = None
                                match = re.search(r'流水号[:：]?\s*([a-zA-Z0-9]+)', serial_text)
                                if match:
                                    serial_number = match.group(1)
                                    print(f"[DEBUG] 找到流水号: {serial_number}")
                                    return serial_number
                    except Exception as e:
                        print(f"[DEBUG] 处理项目元素时出错: {e}")
                        continue
            
            print("[DEBUG] 未找到匹配的项目或流水号")
            return None
            
        except Exception as e:
            print(f"[DEBUG] 搜索项目时出错: {e}")
            return None
            
    except Exception as e:
        print(f"[DEBUG] 提取流水号失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def _check_login_status(page):
    """检查是否已经登录"""
    try:
        # 检查页面中是否包含登录相关的元素
        login_indicators = [
            'text="登录"',
            'text="登陆"',
            'text="Sign in"',
            'text="Login"',
            'input[type="password"]',
            'input[name="password"]'
        ]
        
        for indicator in login_indicators:
            try:
                element = page.query_selector(indicator)
                if element:
                    print("[DEBUG] 检测到登录页面元素，用户未登录")
                    return False
            except Exception:
                continue
        
        # 检查是否包含用户中心或退出登录的元素
        user_indicators = [
            'text="用户中心"',
            'text="退出"',
            'text="退出登录"',
            'text="Logout"',
            '.user-center',
            '.logout'
        ]
        
        for indicator in user_indicators:
            try:
                element = page.query_selector(indicator)
                if element:
                    print("[DEBUG] 检测到用户中心元素，用户已登录")
                    return True
            except Exception:
                continue
        
        print("[DEBUG] 无法确定登录状态")
        return False
        
    except Exception as e:
        print(f"[DEBUG] 检查登录状态时出错: {e}")
        return False
