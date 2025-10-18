#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试使用说明文档
详细说明如何使用测试套件进行系统测试
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_usage_guide():
    """打印使用说明"""
    print("=" * 80)
    print("软著管理系统测试套件使用说明")
    print("=" * 80)
    
    print("""
📋 测试套件概述
===============

本测试套件为软著管理系统提供全面的测试功能，包括：
- Web端功能测试（认证、业务流程、API、安全）
- 桌面端功能测试（登录、任务视图、模板管理、材料管理）
- 数据同步测试（Web端与桌面端数据同步）
- 集成测试（端到端业务流程）
- 性能测试（并发、响应时间、吞吐量）
- 测试报告生成（HTML、JSON、Markdown格式）

🚀 快速开始
===========

1. 环境准备
   - 确保Python 3.8+已安装
   - 安装依赖: pip install -r requirements.txt
   - 确保Web服务已启动: python run_web.py

2. 运行所有测试
   python tests/run_all_tests.py

3. 运行特定测试
   python tests/run_all_tests.py --tests auth software api

4. 运行快速测试
   python tests/run_all_tests.py --quick

5. 运行冒烟测试
   python tests/run_all_tests.py --smoke

📁 测试文件结构
===============

tests/
├── setup_test_environment.py      # 测试环境准备
├── test_web_auth.py               # Web端认证测试
├── test_web_software_workflow.py  # 软件著作权流程测试
├── test_web_paper_workflow.py     # 论文指导流程测试
├── test_web_patent_workflow.py    # 专利申请流程测试
├── test_web_api.py                # Web API接口测试
├── test_web_security.py           # Web安全测试
├── test_desktop_functionality.py  # 桌面端功能测试
├── test_desktop_sync.py           # 数据同步测试
├── test_integration.py            # 集成测试
├── test_performance.py            # 性能测试
├── test_report_generator.py       # 测试报告生成器
├── run_all_tests.py               # 测试运行脚本
├── test_reports/                  # 测试报告目录
└── test_results/                  # 测试结果目录

🔧 测试命令详解
===============

1. 运行所有测试
   python tests/run_all_tests.py
   
2. 运行特定测试类别
   python tests/run_all_tests.py --tests auth
   python tests/run_all_tests.py --tests software paper patent
   
3. 运行快速测试（核心功能）
   python tests/run_all_tests.py --quick
   
4. 运行冒烟测试（基本功能验证）
   python tests/run_all_tests.py --smoke
   
5. 列出可用测试
   python tests/run_all_tests.py --list

📊 测试类别说明
===============

Web端测试:
- auth: Web端认证测试（登录、注册、密码重置等）
- software: 软件著作权业务流程测试
- paper: 论文指导业务流程测试
- patent: 专利申请业务流程测试
- api: Web API接口测试
- security: Web安全测试（XSS、SQL注入、CSRF等）

桌面端测试:
- desktop: 桌面端功能测试（登录、任务视图、模板管理等）
- sync: 数据同步测试（Web端与桌面端数据同步）

系统测试:
- integration: 集成测试（端到端业务流程）
- performance: 性能测试（并发、响应时间、吞吐量）

📈 测试报告
===========

测试完成后会自动生成以下格式的报告：
- HTML报告: test_reports/test_report_YYYYMMDD_HHMMSS.html
- JSON报告: test_reports/test_report_YYYYMMDD_HHMMSS.json
- Markdown报告: test_reports/test_report_YYYYMMDD_HHMMSS.md

报告内容包括：
- 测试摘要（总测试数、通过率、耗时等）
- 性能指标（响应时间、吞吐量、资源使用等）
- 测试覆盖率（各模块覆盖率统计）
- Bug报告（发现的Bug详情）
- 改进建议（系统优化建议）

🐛 Bug跟踪
==========

测试过程中发现的Bug会记录在测试报告中，包括：
- Bug ID和标题
- 严重程度（致命/严重/一般/轻微）
- 优先级（高/中/低）
- 状态（待修复/已修复/已验证）
- 详细描述和重现步骤
- 预期结果和实际结果
- 环境信息和附件

⚡ 性能测试
==========

性能测试包括：
- 并发登录测试（20个用户同时登录）
- 并发项目创建测试（50个项目同时创建）
- 大数据集测试（1000个项目）
- API响应时间测试
- 数据库连接池测试
- 内存使用测试
- 文件上传性能测试
- 系统吞吐量测试

🔒 安全测试
==========

安全测试包括：
- XSS攻击防护测试
- SQL注入防护测试
- CSRF防护测试
- 路径遍历防护测试
- 密码安全测试
- 会话安全测试
- 输入验证测试
- 文件上传安全测试
- 授权控制测试
- 速率限制测试

📋 测试数据
===========

测试使用独立的测试数据库，不会影响生产数据：
- 测试用户: testuser@example.com / password123
- 测试员工: teststaff@example.com / staff123
- 测试执行者: testexecutor@example.com / executor123

🛠️ 自定义测试
=============

如需添加自定义测试：
1. 在tests/目录下创建新的测试文件
2. 继承unittest.TestCase类
3. 实现测试方法
4. 在run_all_tests.py中注册测试

示例：
```python
import unittest

class CustomTest(unittest.TestCase):
    def test_custom_function(self):
        # 测试代码
        self.assertTrue(True)

def run_custom_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(CustomTest)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()
```

📞 技术支持
==========

如遇到测试问题，请检查：
1. Python版本是否为3.8+
2. 依赖包是否已安装
3. Web服务是否已启动
4. 数据库连接是否正常
5. 测试环境是否正确配置

联系信息：
- 技术支持：郑州医企创医疗科技有限公司
- 项目地址：D:/SoftwareCopyrightMS

🎯 测试最佳实践
===============

1. 测试前准备
   - 确保Web服务已启动
   - 检查网络连接
   - 清理测试环境

2. 测试执行
   - 先运行冒烟测试验证基本功能
   - 再运行完整测试套件
   - 关注测试报告中的失败项

3. 问题处理
   - 优先修复严重级别Bug
   - 记录测试过程中的问题
   - 定期更新测试用例

4. 持续改进
   - 根据测试结果优化系统
   - 增加新的测试用例
   - 提高测试覆盖率

==========================================
测试套件版本: 1.0
最后更新: 2024年
==========================================
    """)

if __name__ == '__main__':
    print_usage_guide()
