@echo off
cd /d "%~dp0"
if not exist ".venv312\Scripts\python.exe" (
  echo Run SETUP_WINDOWS.bat first.
  pause
  exit /b 1
)
".venv312\Scripts\python.exe" -m streamlit run app.py
if errorlevel 1 pause
