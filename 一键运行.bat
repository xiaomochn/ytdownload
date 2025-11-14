@echo off
chcp 65001 >nul
REM YouTube 视频下载器 - 一键启动脚本（Windows版）

cd /d "%~dp0"

echo ==================================
echo   YouTube 视频下载器
echo ==================================
echo.

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 创建虚拟环境失败，请确保已安装 Python
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查是否安装了 yt-dlp
python -c "import yt_dlp" 2>nul
if errorlevel 1 (
    echo 📦 正在安装依赖 yt-dlp...
    pip install yt-dlp
    if errorlevel 1 (
        echo ❌ 安装依赖失败
        pause
        exit /b 1
    )
    echo.
)

REM 运行下载程序
echo ✅ 启动下载程序...
echo.
python download_simple.py

pause

