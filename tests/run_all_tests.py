#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行脚本
自动执行所有测试，生成测试报告，提供测试管理功能
"""

import os
import sys
import unittest
import time
import json
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入所有测试模块
from tests.test_web_auth import run_auth_tests
from tests.test_web_software_workflow import run_software_workflow_tests
from tests.test_web_paper_workflow import run_paper_workflow_tests
from tests.test_web_patent_workflow import run_patent_workflow_tests
from tests.test_web_api import run_web_api_tests
from tests.test_web_security import run_web_security_tests
from tests.test_desktop_functionality import run_desktop_tests
from tests.test_desktop_sync import run_data_sync_tests
from tests.test_integration import run_integration_tests
from tests.test_performance import run_performance_tests
from tests.test_report_generator import TestReportGenerator

class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.end_time = None
        
    def run_all_tests(self, test_categories=None):
        """运行所有测试"""
        print("=" * 80)
        print("软著管理系统 - 综合测试套件")
        print("=" * 80)
        print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        self.start_time = time.time()
        
        # 定义测试类别
        if test_categories is None:
            test_categories = [
                ('Web端认证测试', run_auth_tests),
                ('软件著作权业务流程测试', run_software_workflow_tests),
                ('论文指导业务流程测试', run_paper_workflow_tests),
                ('专利申请业务流程测试', run_patent_workflow_tests),
                ('Web API接口测试', run_web_api_tests),
                ('Web安全测试', run_web_security_tests),
                ('桌面端功能测试', run_desktop_tests),
                ('数据同步测试', run_data_sync_tests),
                ('集成测试', run_integration_tests),
                ('性能测试', run_performance_tests)
            ]
        
        # 运行测试
        for category_name, test_function in test_categories:
            print(f"\n开始执行: {category_name}")
            print("-" * 60)
            
            try:
                start_time = time.time()
                success = test_function()
                end_time = time.time()
                
                duration = end_time - start_time
                
                result = {
                    'category': category_name,
                    'success': success,
                    'duration': duration,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                self.test_results.append(result)
                
                status = "✓ 通过" if success else "✗ 失败"
                print(f"{category_name}: {status} (耗时: {duration:.2f}秒)")
                
            except Exception as e:
                print(f"{category_name}: ✗ 错误 - {str(e)}")
                
                result = {
                    'category': category_name,
                    'success': False,
                    'duration': 0,
                    'error': str(e),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                self.test_results.append(result)
        
        self.end_time = time.time()
        
        # 生成测试报告
        self.generate_test_report()
        
        # 输出测试总结
        self.print_test_summary()
        
    def run_specific_tests(self, test_names):
        """运行特定测试"""
        print("=" * 80)
        print("运行特定测试")
        print("=" * 80)
        
        test_mapping = {
            'auth': ('Web端认证测试', run_auth_tests),
            'software': ('软件著作权业务流程测试', run_software_workflow_tests),
            'paper': ('论文指导业务流程测试', run_paper_workflow_tests),
            'patent': ('专利申请业务流程测试', run_patent_workflow_tests),
            'api': ('Web API接口测试', run_web_api_tests),
            'security': ('Web安全测试', run_web_security_tests),
            'desktop': ('桌面端功能测试', run_desktop_tests),
            'sync': ('数据同步测试', run_data_sync_tests),
            'integration': ('集成测试', run_integration_tests),
            'performance': ('性能测试', run_performance_tests)
        }
        
        test_categories = []
        for test_name in test_names:
            if test_name in test_mapping:
                test_categories.append(test_mapping[test_name])
            else:
                print(f"警告: 未知的测试名称 '{test_name}'")
        
        if test_categories:
            self.run_all_tests(test_categories)
        else:
            print("没有找到有效的测试")
    
    def run_quick_tests(self):
        """运行快速测试（核心功能）"""
        print("=" * 80)
        print("运行快速测试（核心功能）")
        print("=" * 80)
        
        quick_tests = [
            ('Web端认证测试', run_auth_tests),
            ('软件著作权业务流程测试', run_software_workflow_tests),
            ('Web API接口测试', run_web_api_tests),
            ('桌面端功能测试', run_desktop_tests)
        ]
        
        self.run_all_tests(quick_tests)
    
    def run_smoke_tests(self):
        """运行冒烟测试（基本功能验证）"""
        print("=" * 80)
        print("运行冒烟测试（基本功能验证）")
        print("=" * 80)
        
        smoke_tests = [
            ('Web端认证测试', run_auth_tests),
            ('Web API接口测试', run_web_api_tests)
        ]
        
        self.run_all_tests(smoke_tests)
    
    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 80)
        print("生成测试报告...")
        print("=" * 80)
        
        # 创建报告生成器
        generator = TestReportGenerator()
        
        # 收集测试结果
        generator.collect_test_results(self.test_results)
        
        # 生成报告
        generator.generate_report()
        
    def print_test_summary(self):
        """打印测试总结"""
        print("\n" + "=" * 80)
        print("测试总结")
        print("=" * 80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        
        total_duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        print(f"总测试类别: {total_tests}")
        print(f"通过测试: {passed_tests}")
        print(f"失败测试: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%" if total_tests > 0 else "成功率: 0%")
        print(f"总耗时: {total_duration:.2f}秒")
        
        print("\n详细结果:")
        print("-" * 80)
        for result in self.test_results:
            status = "✓" if result['success'] else "✗"
            duration = result.get('duration', 0)
            error = result.get('error', '')
            
            print(f"{status} {result['category']:<30} {duration:>8.2f}s")
            if error:
                print(f"    错误: {error}")
        
        print("=" * 80)
        
        # 保存测试结果到文件
        self.save_test_results()
        
    def save_test_results(self):
        """保存测试结果到文件"""
        results_dir = Path(__file__).parent / 'test_results'
        results_dir.mkdir(exist_ok=True)
        
        results_file = results_dir / f'test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        
        test_data = {
            'test_summary': {
                'total_tests': len(self.test_results),
                'passed_tests': sum(1 for result in self.test_results if result['success']),
                'failed_tests': sum(1 for result in self.test_results if not result['success']),
                'total_duration': self.end_time - self.start_time if self.end_time and self.start_time else 0,
                'test_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            'test_results': self.test_results
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"测试结果已保存到: {results_file}")
    
    def list_available_tests(self):
        """列出可用的测试"""
        print("=" * 80)
        print("可用的测试类别")
        print("=" * 80)
        
        tests = [
            ('auth', 'Web端认证测试'),
            ('software', '软件著作权业务流程测试'),
            ('paper', '论文指导业务流程测试'),
            ('patent', '专利申请业务流程测试'),
            ('api', 'Web API接口测试'),
            ('security', 'Web安全测试'),
            ('desktop', '桌面端功能测试'),
            ('sync', '数据同步测试'),
            ('integration', '集成测试'),
            ('performance', '性能测试')
        ]
        
        for test_id, test_name in tests:
            print(f"{test_id:<15} - {test_name}")
        
        print("\n特殊测试:")
        print("quick        - 快速测试（核心功能）")
        print("smoke        - 冒烟测试（基本功能验证）")
        print("all          - 所有测试")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='软著管理系统测试运行器')
    parser.add_argument('--tests', nargs='+', help='要运行的测试类别')
    parser.add_argument('--quick', action='store_true', help='运行快速测试')
    parser.add_argument('--smoke', action='store_true', help='运行冒烟测试')
    parser.add_argument('--list', action='store_true', help='列出可用的测试')
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.list:
        runner.list_available_tests()
    elif args.quick:
        runner.run_quick_tests()
    elif args.smoke:
        runner.run_smoke_tests()
    elif args.tests:
        if 'all' in args.tests:
            runner.run_all_tests()
        else:
            runner.run_specific_tests(args.tests)
    else:
        # 默认运行所有测试
        runner.run_all_tests()

if __name__ == '__main__':
    main()
