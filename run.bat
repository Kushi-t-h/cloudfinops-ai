@echo off
setlocal
cd /d "%~dp0"
title CloudFinOps AI Dashboard

echo ======================================================================
echo  CloudFinOps AI - Cloud Cost Intelligence ^& Optimization Platform
echo ======================================================================

set "PYTHON_EXE=C:\Users\kushi\AppData\Local\Programs\Python\Python313\python.exe"
if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

echo [*] Initializing SQLite database and verifying synthetic records...
"%PYTHON_EXE%" src\database.py

echo [*] Launching Streamlit FinOps Dashboard...
"%PYTHON_EXE%" -m streamlit run app.py --server.headless false

pause
