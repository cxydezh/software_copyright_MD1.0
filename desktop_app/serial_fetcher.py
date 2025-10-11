#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
流水号获取模块（Playwright）
 - 打开版权中心页面，允许人工登录后抓取与项目匹配的流水号
 - 入口：fetch_serial_for_project(project_name: str, applicant_name: str) -> str|None
"""

from typing import Optional

TARGET_URL = 'https://register.ccopyright.com.cn/account.html?current=soft_register'


def fetch_serial_for_project(project_name: str, applicant_name: Optional[str] = None) -> Optional[str]:
    """从版权中心页面抓取与项目匹配的流水号。

    注意：需人工完成登录。函数会在页面打开后等待用户按回车继续，再尝试抓取。
    返回匹配到的流水号字符串，未匹配返回 None。
    """
    print(f"[DEBUG] 开始获取流水号，项目名称: {project_name}, 申请人: {applicant_name}")
    
    try:
        from playwright.sync_api import sync_playwright
        print("[DEBUG] Playwright 导入成功")
    except Exception as e:
        print(f"[DEBUG] Playwright 导入失败: {e}")
        # 未安装 playwright
        return None

    try:
        print("[DEBUG] 启动浏览器...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            print(f"[DEBUG] 导航到: {TARGET_URL}")
            page.goto(TARGET_URL, wait_until='load', timeout=60000)
            print("[DEBUG] 页面加载完成")

            # 使用GUI对话框替代终端输入，更适合桌面应用
            import tkinter as tk
            from tkinter import messagebox
            
            # 创建临时根窗口（如果不存在）
            try:
                root = tk._default_root
                if root is None:
                    root = tk.Tk()
                    root.withdraw()  # 隐藏主窗口
            except:
                root = tk.Tk()
                root.withdraw()
            
            # 显示对话框等待用户确认
            messagebox.showinfo(
                "获取流水号", 
                f"浏览器已打开版权中心页面。\n\n"
                f"请完成以下步骤：\n"
                f"1. 在浏览器中登录版权中心\n"
                f"2. 进入用户中心，找到项目：{project_name}\n"
                f"3. 点击'确定'继续抓取流水号"
            )
            print("[DEBUG] 用户确认完成，开始抓取数据...")

            # 简单抓取逻辑：查找包含项目名的行，向上寻找流水号字段
            # 具体选择器可能需根据实际页面调整
            text = page.content()
            print(f"[DEBUG] 页面内容长度: {len(text)}")

            # 粗略策略：在页面文本中搜索项目名附近的"流水号"关键字
            # 更稳健的方式是用 page.locator() 结合具体选择器，这里先做通用回退
            serial = None
            try:
                print("[DEBUG] 尝试通过表格选择器抓取...")
                # 优先通过选择器（示例）
                rows = page.locator('table >> tr')
                count = rows.count()
                print(f"[DEBUG] 找到 {count} 个表格行")
                
                for i in range(count):
                    row = rows.nth(i)
                    row_text = row.inner_text(timeout=2000)
                    if project_name and project_name in row_text:
                        print(f"[DEBUG] 找到包含项目名的行: {row_text[:100]}...")
                        # 在该行或相邻单元格中提取"流水号"
                        # 尝试常见的关键字
                        if '流水号' in row_text:
                            serial = _extract_serial_from_text(row_text)
                            print(f"[DEBUG] 从行文本中提取到流水号: {serial}")
                            if serial:
                                break
                        # 否则检查该行的所有单元格
                        cells = row.locator('td')
                        c = cells.count()
                        for k in range(c):
                            cell_text = cells.nth(k).inner_text(timeout=2000)
                            if '流水号' in cell_text:
                                serial = _extract_serial_from_text(cell_text)
                                print(f"[DEBUG] 从单元格中提取到流水号: {serial}")
                                if serial:
                                    break
                    if serial:
                        break
            except Exception as e:
                print(f"[DEBUG] 表格选择器抓取失败: {e}")
                pass

            if not serial:
                print("[DEBUG] 表格抓取失败，尝试全文本扫描...")
                # 退化为全文本扫描
                serial = _extract_serial_from_text(text)
                print(f"[DEBUG] 全文本扫描结果: {serial}")

            browser.close()
            print(f"[DEBUG] 最终结果: {serial}")
            return serial
    except Exception as e:
        print(f"[DEBUG] 抓取过程发生异常: {e}")
        import traceback
        traceback.print_exc()
        return None


def _extract_serial_from_text(text: str) -> Optional[str]:
    """从给定文本中提取看起来像是流水号的片段（简单正则）。"""
    import re
    # 常见流水号：纯数字或含破折号/斜杠等
    m = re.search(r'(流水号[:：]?\s*)([A-Za-z0-9\-_/]{6,})', text)
    if m:
        return m.group(2).strip()
    # 备用：提取连续 8 位以上数字/大写组合
    m2 = re.search(r'\b([A-Z0-9]{8,})\b', text)
    if m2:
        return m2.group(1).strip()
    return None


