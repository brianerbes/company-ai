@echo off
cd /d "%~dp0"

ECHO Starting Company-IA Web Server...

CALL .\venv\Scripts\activate
python app.py

pause