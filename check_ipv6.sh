#!/bin/bash
# IPv6配置检查脚本

echo "========================================="
echo "IPv6配置检查"
echo "========================================="
echo ""

# 1. 检查系统IPv6支持
echo "1. 检查系统IPv6支持..."
if [ -f /proc/sys/net/ipv6/conf/all/disable_ipv6 ]; then
    DISABLE_IPV6=$(cat /proc/sys/net/ipv6/conf/all/disable_ipv6)
    if [ "$DISABLE_IPV6" = "0" ]; then
        echo "   ✅ IPv6已启用"
    else
        echo "   ❌ IPv6已禁用 (值为: $DISABLE_IPV6)"
        echo "   提示: 运行 'sudo sysctl -w net.ipv6.conf.all.disable_ipv6=0' 启用IPv6"
    fi
else
    echo "   ⚠️  无法检查IPv6状态"
fi

# 2. 检查IPv6地址
echo ""
echo "2. 检查IPv6地址..."
IPV6_ADDRS=$(ip -6 addr show 2>/dev/null | grep -E "inet6.*global" | awk '{print $2}' | cut -d'/' -f1)
if [ -n "$IPV6_ADDRS" ]; then
    echo "   ✅ 发现IPv6地址:"
    echo "$IPV6_ADDRS" | while read addr; do
        echo "      - $addr"
    done
else
    echo "   ❌ 未发现全局IPv6地址"
    echo "   提示: 可能需要配置IPv6地址或联系网络管理员"
fi

# 3. 检查IPv6路由
echo ""
echo "3. 检查IPv6路由..."
IPV6_ROUTES=$(ip -6 route show 2>/dev/null | grep -v "fe80::")
if [ -n "$IPV6_ROUTES" ]; then
    echo "   ✅ IPv6路由配置正常"
else
    echo "   ⚠️  未发现IPv6路由"
fi

# 4. 检查Gunicorn配置
echo ""
echo "4. 检查Gunicorn配置..."
if [ -f "gunicorn_config.py" ]; then
    BIND_CONFIG=$(grep "^bind" gunicorn_config.py | head -1)
    if echo "$BIND_CONFIG" | grep -q "::"; then
        echo "   ✅ Gunicorn已配置IPv6: $BIND_CONFIG"
    elif echo "$BIND_CONFIG" | grep -q "0.0.0.0"; then
        echo "   ⚠️  Gunicorn仅配置IPv4: $BIND_CONFIG"
        echo "   提示: 修改为 'bind = \"[::]:8000\"' 以支持IPv6"
    else
        echo "   ❌ Gunicorn仅监听本地: $BIND_CONFIG"
        echo "   提示: 修改为 'bind = \"[::]:8000\"' 以支持IPv6"
    fi
else
    echo "   ⚠️  未找到 gunicorn_config.py"
fi

# 5. 检查Nginx配置
echo ""
echo "5. 检查Nginx配置..."
NGINX_CONF="/etc/nginx/sites-available/software_copyright.conf"
if [ -f "$NGINX_CONF" ]; then
    if grep -q "listen \[::\]:" "$NGINX_CONF"; then
        echo "   ✅ Nginx已配置IPv6监听"
        grep "listen \[::\]:" "$NGINX_CONF" | while read line; do
            echo "      - $line"
        done
    else
        echo "   ❌ Nginx未配置IPv6监听"
        echo "   提示: 在配置文件中添加 'listen [::]:80;' 和 'listen [::]:443 ssl http2;'"
    fi
else
    echo "   ⚠️  未找到Nginx配置文件: $NGINX_CONF"
fi

# 6. 检查端口监听
echo ""
echo "6. 检查端口监听状态..."
echo "   IPv4端口:"
if command -v ss >/dev/null 2>&1; then
    ss -tlnp 2>/dev/null | grep -E ':(80|443|8000)' | while read line; do
        echo "      $line"
    done
else
    netstat -tlnp 2>/dev/null | grep -E ':(80|443|8000)' | while read line; do
        echo "      $line"
    done
fi

echo ""
echo "   IPv6端口:"
if command -v ss >/dev/null 2>&1; then
    IPV6_LISTEN=$(ss -tlnp6 2>/dev/null | grep -E ':(80|443|8000)')
    if [ -n "$IPV6_LISTEN" ]; then
        echo "$IPV6_LISTEN" | while read line; do
            echo "      $line"
        done
    else
        echo "      ❌ 未发现IPv6端口监听"
    fi
else
    IPV6_LISTEN=$(netstat -tlnp6 2>/dev/null | grep -E ':(80|443|8000)')
    if [ -n "$IPV6_LISTEN" ]; then
        echo "$IPV6_LISTEN" | while read line; do
            echo "      $line"
        done
    else
        echo "      ❌ 未发现IPv6端口监听"
    fi
fi

# 7. 检查防火墙
echo ""
echo "7. 检查防火墙配置..."
if command -v ufw >/dev/null 2>&1; then
    UFW_STATUS=$(sudo ufw status 2>/dev/null | head -1)
    echo "   UFW状态: $UFW_STATUS"
    if echo "$UFW_STATUS" | grep -q "inactive"; then
        echo "   ⚠️  防火墙未启用"
    fi
elif command -v iptables >/dev/null 2>&1; then
    echo "   使用iptables防火墙"
    IP6TABLES_RULES=$(sudo ip6tables -L INPUT -n 2>/dev/null | grep -E "(80|443)")
    if [ -n "$IP6TABLES_RULES" ]; then
        echo "   ✅ 发现IPv6防火墙规则"
    else
        echo "   ⚠️  未发现IPv6防火墙规则"
    fi
fi

# 8. 测试IPv6连接
echo ""
echo "8. 测试IPv6连接..."
if command -v curl >/dev/null 2>&1; then
    # 测试本地IPv6
    if curl -6 --connect-timeout 2 http://[::1]:8000 >/dev/null 2>&1; then
        echo "   ✅ Gunicorn IPv6连接成功 (http://[::1]:8000)"
    else
        echo "   ❌ Gunicorn IPv6连接失败 (http://[::1]:8000)"
    fi
    
    if curl -6 --connect-timeout 2 http://[::1] >/dev/null 2>&1; then
        echo "   ✅ Nginx IPv6连接成功 (http://[::1])"
    else
        echo "   ❌ Nginx IPv6连接失败 (http://[::1])"
    fi
else
    echo "   ⚠️  curl未安装，跳过连接测试"
fi

echo ""
echo "========================================="
echo "检查完成"
echo "========================================="
echo ""
echo "详细配置指南请参考: mdfiles/IPV6_CONFIGURATION_GUIDE.md"



