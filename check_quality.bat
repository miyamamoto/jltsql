@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

REM batファイルのあるディレクトリに移動
cd /d "%~dp0"

REM Python 32bit版を探す
where py >nul 2>&1
if %errorlevel% equ 0 (
    py -3-32 check_data_quality.py
) else (
    python check_data_quality.py
)
