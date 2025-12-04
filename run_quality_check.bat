@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

REM batファイルのあるディレクトリに移動
cd /d "%~dp0"

REM Python 32bit版を探す
where py >nul 2>&1
if %errorlevel% equ 0 (
    py -3 data_quality_check.py
) else (
    python data_quality_check.py
)

pause
