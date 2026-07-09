@echo off
setlocal EnableExtensions EnableDelayedExpansion

cd /d "%~dp0"

set "REPO_NAME=aps_homepage"
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
  echo [ERROR] Python was not found.
  pause
  exit /b 1
)

where gh >nul 2>nul
if %ERRORLEVEL% neq 0 (
  echo [ERROR] GitHub CLI was not found.
  pause
  exit /b 1
)

gh auth status >nul 2>nul
if %ERRORLEVEL% neq 0 (
  echo [ERROR] GitHub login is required.
  echo Run: gh auth login -h github.com
  pause
  exit /b 1
)

"%PYTHON_CMD%" %PYTHON_ARGS% -m pip install -r requirements.txt
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Dependency installation failed.
  pause
  exit /b 1
)

"%PYTHON_CMD%" %PYTHON_ARGS% export_static.py
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Static export failed.
  pause
  exit /b 1
)

if not exist ".git" (
  git init
)

git add app.py data static templates requirements.txt run_server.bat export_static.py deploy_pages.bat README.md docs
git commit -m "Deploy APS homepage to GitHub Pages"

gh repo view "%REPO_NAME%" >nul 2>nul
if %ERRORLEVEL% neq 0 (
  gh repo create "%REPO_NAME%" --public --source "." --remote origin --push
) else (
  git remote get-url origin >nul 2>nul
  if %ERRORLEVEL% neq 0 gh repo set-default "%REPO_NAME%"
  git push -u origin HEAD
)

gh api -X POST "repos/:owner/%REPO_NAME%/pages" -f source[branch]=main -f source[path]=/docs >nul 2>nul
gh api -X PUT "repos/:owner/%REPO_NAME%/pages" -f source[branch]=main -f source[path]=/docs >nul 2>nul

echo.
echo [DONE] GitHub Pages deployment requested.
echo Check the repository Pages settings for the final URL.
pause
