#!/bin/bash
# YouTube 视频下载器 - 一键启动脚本

cd "$(dirname "$0")"

echo "=================================="
echo "  YouTube 视频下载器"
echo "=================================="
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 检查是否安装了 yt-dlp
if ! python -c "import yt_dlp" 2>/dev/null; then
    echo "📦 正在安装依赖 yt-dlp..."
    pip install yt-dlp
    echo ""
fi

# 运行下载程序
echo "✅ 启动下载程序..."
echo ""
python download_simple.py

