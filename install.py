#!/usr/bin/env python3
"""
郑州医企创医疗科技有限公司 - 软著管理系统
系统安装脚本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_banner():
    """打印安装横幅"""
    print("=" * 80)
    print("郑州医企创医疗科技有限公司 - 软著管理系统")
    print("系统安装程序")
    print("=" * 80)
    print()

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        print(f"   当前版本: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """安装Python依赖"""
    print("\n安装Python依赖...")
    
    try:
        # 检查requirements.txt是否存在
        if not os.path.exists('requirements.txt'):
            print("❌ 找不到requirements.txt文件")
            return False
        
        # 安装依赖
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Python依赖安装成功")
            return True
        else:
            print("❌ Python依赖安装失败")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ 安装依赖时发生错误: {e}")
        return False

def create_directories():
    """创建必要的目录"""
    print("\n创建系统目录...")
    
    directories = [
        'D:/SoftwareCopyrightMS',
        'D:/SoftwareCopyrightMS/Database',
        'D:/SoftwareCopyrightMS/USCCC',
        'D:/SoftwareCopyrightMS/IDPDF',
        'D:/SoftwareCopyrightMS/model',
        'D:/SoftwareCopyrightMS/model/contract',
        'D:/SoftwareCopyrightMS/model/material',
        'D:/SoftwareCopyrightMS/ProjectFile',
        'D:/SoftwareCopyrightMS/ProjectFile/Archived',
        'logs',
        'uploads'
    ]
    
    try:
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            print(f"✅ 创建目录: {directory}")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建目录失败: {e}")
        return False

def setup_database():
    """设置数据库"""
    print("\n配置数据库...")
    
    try:
        # 这里可以添加数据库初始化逻辑
        print("ℹ️  请手动配置MySQL数据库:")
        print("   1. 创建数据库: CREATE DATABASE software_copyright CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print("   2. 创建用户并授权")
        print("   3. 修改config/config.py中的数据库连接配置")
        print("   4. 运行 python -c \"from web_app.app import create_app; app=create_app(); app.app_context().push(); from database.models import db; db.create_all()\"")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库配置失败: {e}")
        return False

def create_sample_files():
    """创建示例文件"""
    print("\n创建示例文件...")
    
    try:
        # 创建示例模板文件
        sample_template = """软件著作权申请材料模板

项目名称：{项目名称}
申请人：{申请人}
著作权人：{著作权人}
开发完成日期：{开发完成日期}
首次发表日期：{首次发表日期}

软件功能和技术特点：
{软件功能描述}

开发环境：
- 操作系统：
- 开发工具：
- 编程语言：
- 数据库：

运行环境：
- 操作系统：
- 硬件要求：
- 软件要求：
"""
        
        template_path = Path('D:/SoftwareCopyrightMS/model/material/软件著作权申请模板.txt')
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(sample_template)
        
        print("✅ 创建示例模板文件")
        
        # 创建示例合同文件
        sample_contract = """软件开发合同模板

甲方（委托方）：
乙方（开发方）：郑州医企创医疗科技有限公司

项目名称：{项目名称}
开发内容：{开发内容}
交付时间：{交付时间}
项目费用：{项目费用}

双方权利义务：
1. 甲方义务：...
2. 乙方义务：...

知识产权约定：
软件著作权归甲方所有，乙方协助完成著作权登记。

违约责任：
...

本合同一式两份，甲乙双方各执一份。

甲方签字：_____________ 日期：_____________
乙方签字：_____________ 日期：_____________
"""
        
        contract_path = Path('D:/SoftwareCopyrightMS/model/contract/软件开发合同模板.txt')
        with open(contract_path, 'w', encoding='utf-8') as f:
            f.write(sample_contract)
        
        print("✅ 创建示例合同文件")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建示例文件失败: {e}")
        return False

def create_startup_scripts():
    """创建启动脚本"""
    print("\n创建启动脚本...")
    
    try:
        # Windows批处理脚本
        web_bat_content = """@echo off
title 软著管理系统 - Web服务器
echo 启动Web服务器...
python run_web.py
pause
"""
        
        desktop_bat_content = """@echo off
title 软著管理系统 - 桌面客户端
echo 启动桌面客户端...
python run_desktop.py
pause
"""
        
        with open('启动Web服务器.bat', 'w', encoding='gbk') as f:
            f.write(web_bat_content)
        
        with open('启动桌面客户端.bat', 'w', encoding='gbk') as f:
            f.write(desktop_bat_content)
        
        print("✅ 创建Windows启动脚本")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建启动脚本失败: {e}")
        return False

def print_completion_info():
    """打印安装完成信息"""
    print("\n" + "=" * 80)
    print("🎉 系统安装完成！")
    print("=" * 80)
    print()
    print("📁 系统文件位置:")
    print(f"   - 项目目录: {os.getcwd()}")
    print("   - 数据目录: D:/SoftwareCopyrightMS/")
    print()
    print("🚀 启动方式:")
    print("   - Web服务器: 双击 '启动Web服务器.bat' 或运行 'python run_web.py'")
    print("   - 桌面客户端: 双击 '启动桌面客户端.bat' 或运行 'python run_desktop.py'")
    print()
    print("🌐 访问地址:")
    print("   - 本地访问: http://localhost:5000")
    print("   - 局域网访问: http://您的IP地址:5000")
    print()
    print("👤 默认管理员账户:")
    print("   - 邮箱: admin@yiqichuang.com")
    print("   - 密码: admin123")
    print()
    print("📖 更多信息请查看 README.md 文件")
    print("=" * 80)

def main():
    """主安装流程"""
    print_banner()
    
    # 检查Python版本
    if not check_python_version():
        return False
    
    # 安装依赖
    if not install_dependencies():
        print("\n⚠️  依赖安装失败，可以稍后手动安装: pip install -r requirements.txt")
    
    # 创建目录
    if not create_directories():
        return False
    
    # 设置数据库
    setup_database()
    
    # 创建示例文件
    if not create_sample_files():
        print("\n⚠️  示例文件创建失败，系统仍可正常使用")
    
    # 创建启动脚本
    if not create_startup_scripts():
        print("\n⚠️  启动脚本创建失败，可以直接使用python命令启动")
    
    # 完成安装
    print_completion_info()
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        if success:
            input("\n按任意键退出...")
        else:
            print("\n❌ 安装过程中出现错误")
            input("按任意键退出...")
    except KeyboardInterrupt:
        print("\n\n⚠️  安装被用户中断")
    except Exception as e:
        print(f"\n❌ 安装过程中发生未知错误: {e}")
        input("按任意键退出...")
