# Windows PowerShell Startup Script for CloudFinOps AI
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " CloudFinOps AI | Cloud Cost Intelligence & Optimization Platform" -ForegroundColor Cyan
Write-Host " Tailored for Entry-Level Cloud FinOps Analyst Portfolio" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$PythonExe = "C:\Users\kushi\AppData\Local\Programs\Python\Python313\python.exe"
if (-not (Test-Path $PythonExe)) {
    $PythonExe = "python.exe"
}

Write-Host "[*] Initializing SQLite database and verifying synthetic records..." -ForegroundColor Yellow
& $PythonExe src\database.py

Write-Host "[*] Launching Streamlit FinOps Dashboard..." -ForegroundColor Green
& $PythonExe -m streamlit run app.py
