#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量下载 YouTube 视频
从文件中读取多个 URL 进行批量下载
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
            print(f"\r  下载中: {d['_percent_str']} | 速度: {speed_str}", end='', flush=True)
    elif d['status'] == 'finished':
        print("\n  ✅ 下载完成")


def batch_download_from_file(file_path, output_dir="./downloads", quality="best", audio_only=False):
    """
    从文件中批量下载视频
    
    Args:
        file_path: 包含 URL 列表的文件路径（每行一个 URL）
        output_dir: 下载保存目录
        quality: 视频质量
        audio_only: 是否只下载音频
    """
    # 读取 URL 列表
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        print(f"❌ 文件不存在: {file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 读取文件失败: {str(e)}")
        sys.exit(1)
    
    if not urls:
        print("❌ 文件中没有找到任何 URL")
        sys.exit(1)
    
    print(f"\n📋 找到 {len(urls)} 个视频链接")
    print(f"📁 保存到: {output_dir}\n")
    print("="*60)
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 配置下载选项
    ydl_opts = {
        'outtmpl': str(output_path / '%(title)s.%(ext)s'),
        'progress_hooks': [download_progress_hook],
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,  # 某个视频失败时继续
    }
    
    # 字幕下载配置（仅在下载视频时启用，优先英文和中文，如果都没有则下载任意可用字幕）
    if not audio_only:
        ydl_opts.update({
            'writesubtitles': True,          # 下载手动字幕
            'writeautomaticsub': True,      # 下载自动生成的字幕（如果手动字幕不可用）
            'subtitleslangs': ['en', 'zh-CN', 'zh-TW', 'zh'],  # 优先语言顺序：英文 > 简体中文 > 繁体中文
            'subtitleformat': 'srt',        # 字幕格式为SRT
            'allsubtitles': False,          # 不下载所有语言
        })
    
    if audio_only:
        ydl_opts['format'] = 'bestaudio/best'
        if check_ffmpeg():
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
    else:
        # 优先使用 H.264 (AVC) 编码的mp4格式以获得更好的兼容性
        if quality == 'best':
            ydl_opts['format'] = 'bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best'
            ydl_opts['merge_output_format'] = 'mp4'
        elif quality.endswith('p'):
            height = quality[:-1]
            ydl_opts['format'] = f'bestvideo[ext=mp4][height<={height}][vcodec^=avc]+bestaudio[ext=m4a]/best[height<={height}]'
            ydl_opts['merge_output_format'] = 'mp4'
    
    # 批量下载
    success_count = 0
    fail_count = 0
    
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] 下载: {url}")
        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
                # 检查是否有字幕文件，如果没有，尝试下载任意可用字幕
                if not audio_only:
                    subtitle_files = list(output_path.glob('*.srt'))
                    if not subtitle_files:
                        print("  ⚠️  优先语言（英文/中文）字幕不可用，尝试下载任意可用字幕...")
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
                
                success_count += 1
        except KeyboardInterrupt:
            print("\n\n⚠️  用户取消下载")
            break
        except Exception as e:
            print(f"\n  ❌ 下载失败: {str(e)}")
            fail_count += 1
    
    # 显示统计
    print("\n" + "="*60)
    print(f"  下载完成!")
    print(f"  成功: {success_count} 个")
    print(f"  失败: {fail_count} 个")
    print("="*60 + "\n")


def main():
    """主函数 - 交互式批量下载 - 默认最高质量"""
    print("\n" + "="*60)
    print("  YouTube 批量下载器 - 自动最高质量")
    print("="*60 + "\n")
    
    print("使用方法:")
    print("1. 创建一个文本文件（如 urls.txt）")
    print("2. 每行写一个 YouTube 视频 URL")
    print("3. 以 # 开头的行会被忽略（可作为注释）\n")
    print("示例文件内容:")
    print("  # 我喜欢的视频列表")
    print("  https://www.youtube.com/watch?v=VIDEO_ID_1")
    print("  https://www.youtube.com/watch?v=VIDEO_ID_2")
    print("  https://www.youtube.com/watch?v=VIDEO_ID_3\n")
    print("-"*60)
    
    # 获取文件路径
    file_path = input("\n请输入 URL 列表文件路径: ").strip()
    if not file_path:
        print("❌ 文件路径不能为空！")
        return
    
    # 使用日期创建下载文件夹（年月日格式）
    date_folder = datetime.now().strftime("%Y-%m-%d")
    download_dir = f"./downloads/{date_folder}"
    
    print(f"\n📹 开始批量下载（最高质量）...")
    print(f"📁 保存到: {download_dir}\n")
    
    # 默认最高质量
    batch_download_from_file(file_path, download_dir, "best", False)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 再见！\n")
        sys.exit(0)

