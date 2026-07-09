@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

echo [APS] Python Flask server launcher
echo [APS] Project: %CD%
echo.

set "PYTHON_CMD="
set "PYTHON_ARGS="

where py >nul 2>nul
if %ERRORLEVEL%==0 (
  py -3 --version >nul 2>nul
  if !ERRORLEVEL!==0 (
    set "PYTHON_CMD=py"
    set "PYTHON_ARGS=-3"
  )
)

if not defined PYTHON_CMD (
  where python >nul 2>nul
  if !ERRORLEVEL!==0 (
    python --version >nul 2>nul
    if !ERRORLEVEL!==0 set "PYTHON_CMD=python"
  )
)

if not defined PYTHON_CMD (
  where python3 >nul 2>nul
  if !ERRORLEVEL!==0 (
    python3 --version >nul 2>nul
    if !ERRORLEVEL!==0 set "PYTHON_CMD=python3"
  )
)

if not defined PYTHON_CMD (
  for /d %%D in ("%LocalAppData%\Programs\Python\Python*") do (
    if exist "%%~fD\python.exe" (
      "%%~fD\python.exe" --version >nul 2>nul
      if !ERRORLEVEL!==0 if not defined PYTHON_CMD set "PYTHON_CMD=%%~fD\python.exe"
    )
  )
)

if not defined PYTHON_CMD (
  for /d %%D in ("C:\Python*" "%ProgramFiles%\Python*" "%ProgramFiles(x86)%\Python*") do (
    if exist "%%~fD\python.exe" (
      "%%~fD\python.exe" --version >nul 2>nul
      if !ERRORLEVEL!==0 if not defined PYTHON_CMD set "PYTHON_CMD=%%~fD\python.exe"
    )
  )
)

if not defined PYTHON_CMD (
  if exist "F:\equipment\Python312\python.exe" (
    "F:\equipment\Python312\python.exe" --version >nul 2>nul
    if !ERRORLEVEL!==0 set "PYTHON_CMD=F:\equipment\Python312\python.exe"
  )
)

if not defined PYTHON_CMD (
  echo [ERROR] Python was not found.
  echo Install Python 3, then run this file again.
  pause
  exit /b 1
)

echo [APS] Using Python: %PYTHON_CMD%
"%PYTHON_CMD%" %PYTHON_ARGS% --version
echo.

echo [APS] Installing required libraries...
"%PYTHON_CMD%" %PYTHON_ARGS% -m pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
  echo [ERROR] pip upgrade failed.
  pause
  exit /b 1
)

"%PYTHON_CMD%" %PYTHON_ARGS% -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Library installation failed.
  pause
  exit /b 1
)

echo.
echo [APS] Starting server...
echo [APS] Open http://127.0.0.1:5000/
echo [APS] Press Ctrl+C to stop the server.
echo.

"%PYTHON_CMD%" %PYTHON_ARGS% app.py

pause
