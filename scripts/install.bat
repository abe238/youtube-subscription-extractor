@echo off
REM YouTube Subscription Extractor Installation Script
REM For Windows systems

setlocal EnableDelayedExpansion

echo.
echo 🎯 YouTube Subscription Extractor Installation
echo ==============================================

REM Check if Python is installed
echo 🔍 Checking Python installation...

python --version >nul 2>&1
if %errorlevel% equ 0 (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    echo ✅ Found Python !PYTHON_VERSION!
    goto :check_version
) else (
    echo ❌ Python not found, checking for python3...
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set PYTHON_VERSION=%%i
        echo ✅ Found Python3 !PYTHON_VERSION!
        set PYTHON_CMD=python3
        goto :check_version
    ) else (
        echo ❌ Python 3 not found
        goto :install_python
    )
)

:check_version
if not defined PYTHON_CMD set PYTHON_CMD=python

REM Extract major and minor version
for /f "tokens=1,2 delims=." %%a in ("!PYTHON_VERSION!") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if !MAJOR! geq 3 (
    if !MINOR! geq 7 (
        echo ✅ Python version is compatible
        goto :setup
    ) else (
        echo ❌ Python 3.7+ required. Found !PYTHON_VERSION!
        goto :install_python
    )
) else (
    echo ❌ Python 3.7+ required. Found !PYTHON_VERSION!
    goto :install_python
)

:install_python
echo.
echo ❌ Python 3.7+ is required but not found on your system.
echo.
echo 📦 Please install Python from one of these sources:
echo    • Official Python: https://www.python.org/downloads/
echo    • Microsoft Store: Search for "Python 3.11" or "Python 3.10"
echo    • Chocolatey: choco install python3
echo    • Scoop: scoop install python
echo.
echo After installing Python, run this script again.
pause
exit /b 1

:setup
echo.
echo 📋 System Information:
echo    OS: Windows
echo    Python: !PYTHON_VERSION!
echo    Python Command: !PYTHON_CMD!
echo.

echo 🔧 Setting up extractor script...

REM Test the installation
echo 🧪 Testing installation...
!PYTHON_CMD! bin\extract.py --help >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Installation test passed
) else (
    echo ❌ Installation test failed
    echo.
    echo Debug information:
    !PYTHON_CMD! bin\extract.py --help
    pause
    exit /b 1
)

echo.
echo 🎉 Installation completed successfully!
echo.
echo 📚 Quick Start:
echo    !PYTHON_CMD! bin\extract.py --help
echo    !PYTHON_CMD! bin\extract.py your_subscriptions.mhtml
echo.
echo 📖 For detailed documentation, see README.md
echo.
pause