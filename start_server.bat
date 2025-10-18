@echo off
cd /d C:\inetpub\wwwroot\Software_copyright_MS1.0
call .venv\Scripts\activate.bat
python start_iis_integration.py
pause


