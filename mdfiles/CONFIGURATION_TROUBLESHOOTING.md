# 配置问题排查指南

## 常见配置错误

### 错误代码 0x800700b7 - 文件扩展名冲突

**问题描述：**
```
模块: CustomErrorModule
通知: SendResponse
处理程序: 尚未确定
错误代码: 0x800700b7
配置错误: 在唯一密钥属性"fileExtension"设置为".json"时，无法添加类型为"mimeMap"的重复集合项
```

**解决方案：**

1. **检查重复的mimeMap配置**
   ```xml
   <!-- 错误的配置 -->
   <mimeMap fileExtension=".json" mimeType="application/json" />
   <mimeMap fileExtension=".json" mimeType="application/json" />
   
   <!-- 正确的配置 -->
   <mimeMap fileExtension=".json" mimeType="application/json" />
   ```

2. **清理web.config文件**
   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <configuration>
     <system.webServer>
       <handlers>
         <add name="PythonHandler" path="*" verb="*" modules="FastCgiModule" 
              scriptProcessor="C:\inetpub\wwwroot\software_copyright\venv\Scripts\python.exe|C:\inetpub\wwwroot\software_copyright\app.py" 
              resourceType="Unspecified" requireAccess="Script" />
       </handlers>
       
       <rewrite>
         <rules>
           <rule name="Flask App" stopProcessing="true">
             <match url=".*" />
             <conditions>
               <add input="{REQUEST_FILENAME}" matchType="IsFile" negate="true" />
               <add input="{REQUEST_FILENAME}" matchType="IsDirectory" negate="true" />
             </conditions>
             <action type="Rewrite" url="/" />
           </rule>
         </rules>
       </rewrite>
       
       <!-- 静态文件处理 -->
       <staticContent>
         <mimeMap fileExtension=".json" mimeType="application/json" />
         <mimeMap fileExtension=".woff" mimeType="application/font-woff" />
         <mimeMap fileExtension=".woff2" mimeType="application/font-woff2" />
       </staticContent>
       
       <!-- 安全头设置 -->
       <httpProtocol>
         <customHeaders>
           <add name="X-Content-Type-Options" value="nosniff" />
           <add name="X-Frame-Options" value="SAMEORIGIN" />
           <add name="X-XSS-Protection" value="1; mode=block" />
           <add name="Strict-Transport-Security" value="max-age=31536000; includeSubDomains" />
         </customHeaders>
       </httpProtocol>
       
       <!-- 错误页面 -->
       <httpErrors errorMode="Custom" defaultResponseMode="ExecuteURL">
         <remove statusCode="404" subStatusCode="-1" />
         <error statusCode="404" responseMode="ExecuteURL" path="/" />
       </httpErrors>
     </system.webServer>
     
     <appSettings>
       <add key="WSGI_HANDLER" value="wsgi.app" />
       <add key="PYTHONPATH" value="C:\inetpub\wwwroot\software_copyright" />
       <add key="FLASK_CONFIG" value="production" />
       <add key="WSGI_LOG" value="C:\inetpub\logs\software_copyright.log" />
       <add key="WSGI_RESTART_FILE_REGEX" value=".*\.(py|config)$" />
     </appSettings>
   </configuration>
   ```

## 其他常见问题

### 1. 模块加载错误

**问题：**
```
模块: CustomErrorModule
通知: SendResponse
处理程序: 尚未确定
错误代码: 0x800700b7
配置错误: 在唯一密钥属性"fileExtension"设置为".json"时，无法添加类型为"mimeMap"的重复集合项
```

**解决方案：**
- 检查模块路径配置
- 验证依赖项安装
- 清理node_modules重新安装

### 2. 路径配置错误

**问题：**
```
模块: CustomErrorModule
通知: SendResponse
处理程序: 尚未确定
错误代码: 0x800700b7
配置错误: 在唯一密钥属性"fileExtension"设置为".json"时，无法添加类型为"mimeMap"的重复集合项
```

**解决方案：**
- 检查路径别名配置
- 验证相对路径
- 更新tsconfig.json

### 3. 环境变量问题

**问题：**
```
模块: CustomErrorModule
通知: SendResponse
处理程序: 尚未确定
错误代码: 0x800700b7
配置错误: 在唯一密钥属性"fileExtension"设置为".json"时，无法添加类型为"mimeMap"的重复集合项
```

**解决方案：**
- 检查.env文件
- 验证环境变量加载
- 更新环境配置

## 调试步骤

### 1. 检查配置文件
```bash
# 检查web.config语法
# 验证mimeMap配置
# 确认无重复项
```

### 2. 清理缓存
```bash
# 清理IIS缓存
# 重启IIS
# 检查应用程序池
```

### 3. 验证权限
```bash
# 检查文件权限
# 验证路径访问
# 确认模块加载
```

## 预防措施

1. **配置文件管理**
   - 使用版本控制
   - 定期备份配置
   - 测试环境验证

2. **错误监控**
   - 启用详细错误日志
   - 监控应用程序事件
   - 设置性能计数器

3. **部署检查**
   - 预部署验证
   - 回滚计划
   - 健康检查

## 相关资源

- [IIS配置参考](https://docs.microsoft.com/en-us/iis/configuration/)
- [web.config架构](https://docs.microsoft.com/en-us/iis/configuration/system.webserver/)
- [错误代码参考](https://docs.microsoft.com/en-us/iis/troubleshoot/diagnosing-http-errors-in-iis/)












