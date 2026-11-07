@echo off
cd /d "%~dp0"
py -3.12 --version >nul 2>&1
if errorlevel 1 (
  echo Python 3.12 was not found. Install Python 3.12 for Windows, then try again.
  pause
  exit /b 1
)
if not exist ".venv312\Scripts\python.exe" (
  py -3.12 -m venv .venv312
  if errorlevel 1 goto failed
)
".venv312\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Setup complete. Double-click START_DASHBOARD.bat to view Project 2.
pause
exit /b 0
:failed
echo Setup did not complete. Keep this window open and copy the error for troubleshooting.
pause
exit /b 1
