@echo off
:: Forza al script a ejecutarse desde su propio directorio
cd /d "%~dp0"

ECHO Arrancando Company-IA con el intérprete de Python del venv...

:: Establece la variable de entorno de idioma para Gradio
set GRADIO_LANG=en

:: Ejecuta la aplicación usando el ejecutable de Python del entorno virtual
.\venv\Scripts\python.exe app.py

pause