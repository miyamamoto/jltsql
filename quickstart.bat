@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
title JLTSQL Setup

REM Move to batch file directory
cd /d "%~dp0"

REM Get Python 32bit executable path
if defined PYTHON32 (
    set PYTHON_EXE=%PYTHON32%
    goto :run_python
)

REM Get path from py launcher
for /f "delims=" %%i in ('py -3-32 -c "import sys; print(sys.executable)" 2^>nul') do set PYTHON_EXE=%%i

if not defined PYTHON_EXE (
    echo ERROR: Python 32bit not found
    echo Please ensure py -3-32 works
    pause
    exit /b 1
)

:run_python
"%PYTHON_EXE%" scripts/quickstart.py %*

echo.
echo ============================================================
echo   Setup Complete
echo ============================================================
echo.
echo   Database file: data\keiba.db (SQLite)
echo.
echo   To view data:
echo     - Use DB Browser for SQLite
echo     - Python: sqlite3.connect('data/keiba.db')
echo.
echo   CLI commands:
echo     jltsql status   - Check database status
echo     jltsql fetch    - Fetch additional data
echo     jltsql --help   - Other commands
echo.
echo   For Claude Code / Claude Desktop users:
echo     Install MCP Server to access DB directly from AI
echo     https://github.com/miyamamoto/jvlink-mcp-server
echo.
echo   Press Enter to close...
set /p dummy=
