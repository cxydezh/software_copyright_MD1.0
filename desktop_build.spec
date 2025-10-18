# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run_desktop.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('logo.ico', '.'),
        ('logo.jpg', '.'),
        ('LOGO.bmp', '.'),
        ('config/config.py', 'config'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'requests',
        'sqlite3',
        'webbrowser',
        'shutil',
        'datetime',
        'pathlib',
        'json',
        'traceback',
        'warnings',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_wtf',
        'flask_mail',
        'jinja2',
        'werkzeug',
        'pymysql',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='软著管理系统-桌面客户端',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.ico',
    version_file='version_info.txt',
)
