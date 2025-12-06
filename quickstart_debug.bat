@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
title JLTSQL Setup (Debug)

REM batファイルのあるディレクトリに移動
cd /d "%~dp0"

echo ============================================================
echo   JLTSQL Quickstart - Debug Mode
echo ============================================================
echo.

REM Python 32bit版を探す
where py >nul 2>&1
if %errorlevel% equ 0 (
    echo Using: py -3-32
    echo Arguments: %*
    echo.
    py -3-32 scripts/quickstart.py %*
) else (
    echo Using: python
    echo Arguments: %*
    echo.
    python scripts/quickstart.py %*
)

echo.
echo ============================================================
echo   終了コード: %errorlevel%
echo ============================================================
echo.
echo   エラーが発生した場合は上記のトレースバックを確認してください。
echo.
pause
