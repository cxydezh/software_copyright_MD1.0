#!/bin/bash
# 配置问题快速修复脚本

echo "=== 配置问题快速修复脚本 ==="

# 1. 检查web.config文件
echo "1. 检查web.config文件..."
if [ -f "windows_deployment/web.config" ]; then
    echo "✓ web.config文件存在"
    
    # 检查重复的mimeMap配置
    duplicate_mime=$(grep -c "fileExtension.*json" windows_deployment/web.config)
    if [ $duplicate_mime -gt 1 ]; then
        echo "⚠ 发现重复的mimeMap配置"
        echo "正在修复..."
        
        # 备份原文件
        cp windows_deployment/web.config windows_deployment/web.config.backup
        
        # 移除重复的mimeMap
        sed -i '/fileExtension.*json/d' windows_deployment/web.config
        
        # 添加正确的mimeMap
        sed -i '/<staticContent>/a\      <mimeMap fileExtension=".json" mimeType="application/json" />' windows_deployment/web.config
        
        echo "✓ 修复完成"
    else
        echo "✓ mimeMap配置正常"
    fi
else
    echo "✗ web.config文件不存在"
fi

# 2. 检查IIS配置
echo "2. 检查IIS配置..."
if command -v iisreset &> /dev/null; then
    echo "✓ IIS可用"
    
    # 检查应用程序池
    echo "检查应用程序池..."
    appcmd list apppool | grep -q "software_copyright" && echo "✓ 应用程序池存在" || echo "✗ 应用程序池不存在"
    
    # 检查网站
    echo "检查网站..."
    appcmd list site | grep -q "software_copyright" && echo "✓ 网站存在" || echo "✗ 网站不存在"
else
    echo "⚠ IIS命令不可用"
fi

# 3. 检查Python环境
echo "3. 检查Python环境..."
if [ -f "venv/Scripts/python.exe" ]; then
    echo "✓ Python环境存在"
    
    # 检查Flask应用
    echo "检查Flask应用..."
    if [ -f "app.py" ]; then
        echo "✓ Flask应用文件存在"
    else
        echo "✗ Flask应用文件不存在"
    fi
else
    echo "✗ Python环境不存在"
fi

# 4. 检查日志文件
echo "4. 检查日志文件..."
if [ -d "logs" ]; then
    echo "✓ 日志目录存在"
    
    # 检查最新日志
    latest_log=$(ls -t logs/*.log 2>/dev/null | head -1)
    if [ -n "$latest_log" ]; then
        echo "✓ 最新日志: $latest_log"
        
        # 检查错误
        if grep -q "0x800700b7" "$latest_log" 2>/dev/null; then
            echo "⚠ 发现0x800700b7错误"
            echo "错误详情:"
            grep "0x800700b7" "$latest_log" | tail -5
        else
            echo "✓ 未发现0x800700b7错误"
        fi
    else
        echo "⚠ 未找到日志文件"
    fi
else
    echo "✗ 日志目录不存在"
fi

# 5. 清理临时文件
echo "5. 清理临时文件..."
if [ -d "__pycache__" ]; then
    rm -rf __pycache__
    echo "✓ 清理Python缓存"
fi

if [ -d "venv/__pycache__" ]; then
    rm -rf venv/__pycache__
    echo "✓ 清理虚拟环境缓存"
fi

# 6. 验证修复
echo "6. 验证修复..."
if [ -f "windows_deployment/web.config" ]; then
    # 检查配置语法
    if xmllint --noout windows_deployment/web.config 2>/dev/null; then
        echo "✓ web.config语法正确"
    else
        echo "✗ web.config语法错误"
    fi
fi

echo "=== 修复完成 ==="
echo ""
echo "如果问题仍然存在，请检查："
echo "1. IIS应用程序池状态"
echo "2. Python环境配置"
echo "3. 文件权限设置"
echo "4. 防火墙规则"







