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
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        # 未安装 playwright
        return None

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            page.goto(TARGET_URL, wait_until='load', timeout=60000)

            print('\n请在打开的浏览器中完成登录，然后回到终端按 Enter 继续...')
            try:
                input()
            except Exception:
                pass

            # 简单抓取逻辑：查找包含项目名的行，向上寻找流水号字段
            # 具体选择器可能需根据实际页面调整
            text = page.content()

            # 粗略策略：在页面文本中搜索项目名附近的“流水号”关键字
            # 更稳健的方式是用 page.locator() 结合具体选择器，这里先做通用回退
            serial = None
            try:
                # 优先通过选择器（示例）
                rows = page.locator('table >> tr')
                count = rows.count()
                for i in range(count):
                    row = rows.nth(i)
                    row_text = row.inner_text(timeout=2000)
                    if project_name and project_name in row_text:
                        # 在该行或相邻单元格中提取“流水号”
                        # 尝试常见的关键字
                        if '流水号' in row_text:
                            serial = _extract_serial_from_text(row_text)
                            if serial:
                                break
                        # 否则检查该行的所有单元格
                        cells = row.locator('td')
                        c = cells.count()
                        for k in range(c):
                            cell_text = cells.nth(k).inner_text(timeout=2000)
                            if '流水号' in cell_text:
                                serial = _extract_serial_from_text(cell_text)
                                if serial:
                                    break
                    if serial:
                        break
            except Exception:
                pass

            if not serial:
                # 退化为全文本扫描
                serial = _extract_serial_from_text(text)

            browser.close()
            return serial
    except Exception:
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


