; 软著管理系统 - Inno Setup 安装包配置脚本
; 需要安装 Inno Setup 6.0+ 才能编译此脚本

#define MyAppName "软著管理系统"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "郑州医企创医疗科技有限公司"
#define MyAppURL "https://your-domain.com"
#define MyAppExeName "软著管理系统-桌面客户端.exe"

[Setup]
; 基本信息
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; 安装目录和组
DefaultDirName={autopf}\SoftwareCopyrightMS
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; 输出设置
OutputDir=installer_output
OutputBaseFilename={#MyAppName}-安装程序-v{#MyAppVersion}
SetupIconFile=logo.ico
WizardImageFile=logo.jpg
WizardSmallImageFile=logo.jpg

; 压缩设置
Compression=lzma2/ultra
SolidCompression=yes
LZMAUseSeparateProcess=yes
LZMADictionarySize=1048576

; 权限设置
PrivilegesRequired=lowest
MinVersion=6.1sp1

; 界面设置
WizardStyle=modern
DisableProgramGroupPage=yes
DisableReadyPage=no
DisableFinishedPage=no

; 卸载设置
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName}

[Languages]
Name: "chinesesimp"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
; 主程序文件
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; 配置文件
Source: "README_Desktop.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "config\config.py"; DestDir: "{app}\config"; Flags: ignoreversion

; 资源文件
Source: "logo.ico"; DestDir: "{app}"; Flags: ignoreversion
Source: "logo.jpg"; DestDir: "{app}"; Flags: ignoreversion

; 用户手册
Source: "DESKTOP_USER_MANUAL.md"; DestDir: "{app}"; Flags: ignoreversion

; 创建必要的目录结构
[Dirs]
Name: "{app}\config"; Permissions: users-full
Name: "{app}\logs"; Permissions: users-full
Name: "{app}\data"; Permissions: users-full

[Icons]
; 开始菜单图标
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\用户手册"; Filename: "{app}\DESKTOP_USER_MANUAL.md"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; 桌面图标
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

; 快速启动图标
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; 安装完成后运行程序
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; 卸载时删除用户数据（可选）
Type: filesandordirs; Name: "{userdocs}\SoftwareCopyrightMS"
Type: filesandordirs; Name: "{localappdata}\SoftwareCopyrightMS"

[Code]
// 安装前检查
function InitializeSetup(): Boolean;
var
  ResultCode: Integer;
begin
  Result := True;
  
  // 检查是否已安装旧版本
  if RegKeyExists(HKEY_LOCAL_MACHINE, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{#MyAppName}_is1') then
  begin
    if MsgBox('检测到已安装的旧版本，是否继续安装？', mbConfirmation, MB_YESNO) = IDNO then
      Result := False;
  end;
end;

// 安装后处理
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // 创建用户数据目录
    CreateDir(ExpandConstant('{userdocs}\SoftwareCopyrightMS'));
    CreateDir(ExpandConstant('{userdocs}\SoftwareCopyrightMS\USCCC'));
    CreateDir(ExpandConstant('{userdocs}\SoftwareCopyrightMS\IDPDF'));
    CreateDir(ExpandConstant('{userdocs}\SoftwareCopyrightMS\templates'));
    CreateDir(ExpandConstant('{userdocs}\SoftwareCopyrightMS\model'));
    CreateDir(ExpandConstant('{userdocs}\SoftwareCopyrightMS\ProjectFile'));
  end;
end;

// 卸载前确认
function InitializeUninstall(): Boolean;
begin
  Result := True;
  if MsgBox('确定要卸载软著管理系统吗？' + #13#10 + '注意：用户数据将被保留。', mbConfirmation, MB_YESNO) = IDNO then
    Result := False;
end;




