@echo off
:: This command forces the script to run from its own directory,
:: ensuring that all relative paths are correct.
cd /d "%~dp0"

ECHO Activating virtual environment and starting Company-IA Web Server...

:: Activate the virtual environment
CALL .\venv\Scripts\activate

:: Run the Flask web application
python app.py

pause