# 软著管理系统 - 部署总结

## 🎯 项目概述
**郑州医企创医疗科技有限公司 - 软著管理系统**
- **项目类型**: Flask Web应用 + 桌面应用
- **部署环境**: Windows Server + IIS
- **数据库**: MySQL
- **部署时间**: 2025年10月

## 🏗️ 最终部署架构

```
Internet (47.111.186.20) → IIS (端口80) → URL重写 → Flask服务器 (端口5000)
```

### 核心组件
- **IIS**: 反向代理和静态文件服务器
- **Waitress**: 生产级WSGI服务器
- **MySQL**: 数据库服务器
- **URL重写模块**: IIS请求转发

## 📋 部署历程

### 阶段1: 初始问题诊断
- **问题**: IIS + wfastcgi 集成失败，500内部服务器错误
- **尝试**: 修复FastCGI配置、环境变量、超时设置
- **结果**: wfastcgi在Windows Server上不稳定

### 阶段2: 策略转换
- **决策**: 放弃wfastcgi，改用IIS作为反向代理
- **实现**: 使用IIS URL重写模块转发请求到Flask服务器
- **优势**: 更稳定、更易维护

### 阶段3: 生产环境优化
- **升级**: 从Flask开发服务器升级到Waitress WSGI服务器
- **配置**: 优化线程数、连接限制、超时设置
- **监控**: 添加日志记录和错误处理

### 阶段4: 公网访问支持
- **问题**: IIS重定向到localhost导致公网访问失败
- **解决**: 修改web.config中的重定向URL为公网IP
- **结果**: 成功支持云服务器公网访问

## 🌐 访问地址

### 公网访问
- **IIS代理**: `http://47.111.186.20/staff/login` (推荐)
- **直接访问**: `http://47.111.186.20:5000/staff/login`

### 本地访问
- **IIS代理**: `http://localhost/staff/login`
- **直接访问**: `http://localhost:5000/staff/login`

## 🔧 关键配置文件

### web.config (IIS配置)
```xml
<rewrite>
  <rules>
    <rule name="Flask Redirect" stopProcessing="true">
      <match url=".*" />
      <action type="Redirect" url="http://47.111.186.20:5000/{R:0}" redirectType="Temporary" />
    </rule>
  </rules>
</rewrite>
```

### start_production_server.py (生产服务器)
```python
serve(
    app,
    host='0.0.0.0',  # 监听所有网络接口
    port=5000,
    threads=4,
    connection_limit=1000,
    cleanup_interval=30,
    channel_timeout=120
)
```

## 🚀 启动方式

### 生产环境启动
```bash
# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 启动生产服务器
python start_production_server.py
```

### Windows服务方式
```bash
# 安装服务
install_windows_service.bat

# 管理服务
services.msc
```

## 🔒 安全配置

### Windows防火墙
- 开放端口5000 (Flask服务器)
- 开放端口80 (IIS)
- 开放端口3306 (MySQL)

### IIS安全头
- X-Content-Type-Options: nosniff
- X-Frame-Options: SAMEORIGIN
- X-XSS-Protection: 1; mode=block
- Strict-Transport-Security: max-age=31536000

## 📊 性能优化

### Waitress配置
- **线程数**: 4
- **连接限制**: 1000
- **清理间隔**: 30秒
- **通道超时**: 120秒

### 数据库优化
- 使用连接池
- 索引优化
- 查询优化

## 🛠️ 维护指南

### 日志文件
- IIS日志: `C:\inetpub\logs\LogFiles\`
- 应用日志: `service_log.txt`
- 错误日志: Windows事件查看器

### 监控指标
- 服务器响应时间
- 数据库连接数
- 内存使用情况
- CPU使用率

### 备份策略
- 数据库定期备份
- 配置文件备份
- 代码版本控制

## 🎉 部署成功指标

✅ **功能完整性**: 所有功能模块正常工作
✅ **性能稳定性**: 服务器稳定运行，无崩溃
✅ **公网访问**: 支持外部用户访问
✅ **安全配置**: 防火墙和安全头配置完成
✅ **监控日志**: 完整的日志记录系统
✅ **维护便利**: 简单的启动和维护流程

## 📞 技术支持

**默认管理员账户**:
- 邮箱: `admin@yiqichuang.com`
- 密码: `admin123`

**联系方式**: 郑州医企创医疗科技有限公司

---
*部署完成时间: 2025年10月18日*
*部署工程师: AI Assistant*

