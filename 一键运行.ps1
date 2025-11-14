# YouTube 视频下载器 - 一键启动脚本（PowerShell版）

Set-Location $PSScriptRoot

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "  YouTube 视频下载器" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# 检查虚拟环境
if (-not (Test-Path "venv")) {
    Write-Host "📦 创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 创建虚拟环境失败，请确保已安装 Python" -ForegroundColor Red
        Read-Host "按 Enter 键退出"
        exit 1
    }
}

# 激活虚拟环境
& "venv\Scripts\Activate.ps1"

# 检查是否安装了 yt-dlp
python -c "import yt_dlp" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "📦 正在安装依赖 yt-dlp..." -ForegroundColor Yellow
    pip install yt-dlp
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ 安装依赖失败" -ForegroundColor Red
        Read-Host "按 Enter 键退出"
        exit 1
    }
    Write-Host ""
}

# 运行下载程序
Write-Host "✅ 启动下载程序..." -ForegroundColor Green
Write-Host ""
python download_simple.py

Read-Host "`n按 Enter 键退出"

