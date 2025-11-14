#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超简单的 YouTube 视频下载器（交互式版本）
直接运行，输入 URL 即可下载
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("\n❌ 错误: 请先安装 yt-dlp")
    print("   运行: pip install yt-dlp\n")
    sys.exit(1)


def check_ffmpeg():
    """检查 FFmpeg 是否已安装"""
    return shutil.which('ffmpeg') is not None


def download_progress_hook(d):
    """下载进度回调"""
    if d['status'] == 'downloading':
        if '_percent_str' in d:
            speed_str = d.get('_speed_str', 'N/A')
            eta_str = d.get('_eta_str', 'N/A')
            print(f"\r下载中: {d['_percent_str']} | 速度: {speed_str} | 剩余时间: {eta_str}", end='', flush=True)
    elif d['status'] == 'finished':
        print("\n✅ 下载完成，正在处理...")


def simple_download():
    """简单的交互式下载 - 默认最高质量"""
    print("\n" + "="*60)
    print("  YouTube 视频下载器 - 自动最高质量")
    print("="*60 + "\n")
    
    # 获取 URL
    url = input("请输入 YouTube 视频 URL: ").strip()
    if not url:
        print("❌ URL 不能为空！")
        return
    
    # 使用日期创建下载文件夹（年月日格式）
    date_folder = datetime.now().strftime("%Y-%m-%d")
    download_dir = f"./downloads/{date_folder}"
    output_path = Path(download_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 配置下载选项 - 默认最高质量
    ydl_opts = {
        'outtmpl': str(output_path / '%(title)s.%(ext)s'),
        'format': 'bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best',
        'merge_output_format': 'mp4',
        'progress_hooks': [download_progress_hook],
        'quiet': False,
        'no_warnings': False,
        # 字幕下载配置（优先英文和中文，如果都没有则下载任意可用字幕）
        'writesubtitles': True,          # 下载手动字幕
        'writeautomaticsub': True,      # 下载自动生成的字幕（如果手动字幕不可用）
        'subtitleslangs': ['en', 'zh-CN', 'zh-TW', 'zh'],  # 优先语言顺序：英文 > 简体中文 > 繁体中文
        'subtitleformat': 'srt',        # 字幕格式为SRT
        'allsubtitles': False,          # 不下载所有语言
    }
    
    print(f"\n📹 开始下载视频（最高质量）...")
    print(f"📁 保存到: {download_dir}\n")
    print("-"*60 + "\n")
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
            # 检查是否有字幕文件，如果没有，尝试下载任意可用字幕
            subtitle_files = list(output_path.glob('*.srt'))
            if not subtitle_files:
                print("⚠️  优先语言（英文/中文）字幕不可用，尝试下载任意可用字幕...")
                fallback_opts = ydl_opts.copy()
                # 移除语言限制，但只下载一个字幕（通过不设置allsubtitles）
                fallback_opts.pop('subtitleslangs', None)  # 移除语言限制
                fallback_opts['allsubtitles'] = False  # 只下载一个字幕
                fallback_opts['skip_download'] = True  # 只下载字幕，不重复下载视频
                try:
                    with YoutubeDL(fallback_opts) as ydl_fallback:
                        ydl_fallback.download([url])
                except Exception:
                    pass  # 如果fallback也失败，就跳过
            
            print("\n" + "="*60)
            print("  ✅ 下载完成！")
            print("="*60 + "\n")
    except KeyboardInterrupt:
        print("\n\n⚠️  下载已取消\n")
    except Exception as e:
        print(f"\n❌ 下载失败: {str(e)}")
        print("\n可能的原因:")
        print("  • 网络连接问题")
        print("  • 视频不可用或已删除")
        print("  • 视频有地区限制")
        print("  • URL 格式不正确\n")
        sys.exit(1)


if __name__ == '__main__':
    try:
        simple_download()
    except KeyboardInterrupt:
        print("\n\n👋 再见！\n")
        sys.exit(0)

