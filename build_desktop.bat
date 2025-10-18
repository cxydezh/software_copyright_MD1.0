@echo off
echo =========================================
echo 软著管理系统 - Desktop应用打包
echo =========================================

REM 1. 清理旧的构建文件
echo [1/6] 清理旧的构建文件...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist installer_output rmdir /s /q installer_output

REM 2. 安装依赖
echo [2/6] 安装依赖...
pip install -r desktop_requirements.txt
pip install pyinstaller

REM 3. 打包应用
echo [3/6] 打包应用...
pyinstaller desktop_build.spec

REM 4. 复制额外文件
echo [4/6] 复制额外文件到dist目录...
mkdir dist\config 2>nul
copy README_Desktop.md dist\ 2>nul
copy DESKTOP_USER_MANUAL.md dist\ 2>nul
copy config\config.py dist\config\ 2>nul

REM 5. 检查Inno Setup是否安装
echo [5/6] 检查Inno Setup...
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%INNO_PATH%" (
    echo 警告: 未找到Inno Setup，请先安装Inno Setup 6.0+
    echo 下载地址: https://jrsoftware.org/isinfo.php
    echo 将跳过安装包制作步骤
    goto :skip_installer
)

REM 6. 创建安装包
echo [6/6] 创建安装包...
"%INNO_PATH%" windows_deployment\desktop_installer.iss
if %ERRORLEVEL% EQU 0 (
    echo 安装包创建成功！
) else (
    echo 安装包创建失败，请检查Inno Setup配置
)

:skip_installer
echo =========================================
echo 打包完成！
echo 输出目录: dist\
echo 可执行文件: dist\软著管理系统-桌面客户端.exe
if exist installer_output\软著管理系统-安装程序-v1.0.0.exe (
    echo 安装包: installer_output\软著管理系统-安装程序-v1.0.0.exe
)
echo =========================================
pause
