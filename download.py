#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的 YouTube 视频下载器
支持下载单个视频或播放列表
"""

import sys
import argparse
import shutil
from pathlib import Path
from datetime import datetime
try:
    from yt_dlp import YoutubeDL
except ImportError:
    print("错误: 请先安装 yt-dlp: pip install yt-dlp")
    sys.exit(1)


def check_ffmpeg():
    """检查 FFmpeg 是否已安装"""
    return shutil.which('ffmpeg') is not None


def get_download_options(output_path, quality="best", audio_only=False, is_playlist=False):
    """
    获取下载配置选项
    
    Args:
        output_path: 输出路径
        quality: 视频质量
        audio_only: 是否只下载音频
        is_playlist: 是否为播放列表
        
    Returns:
        dict: yt-dlp 配置选项
    """
    # 基础配置
    if is_playlist:
        template = str(output_path / '%(playlist)s' / '%(title)s.%(ext)s')
    else:
        template = str(output_path / '%(title)s.%(ext)s')
    
    ydl_opts = {
        'outtmpl': template,
        'quiet': False,
        'no_warnings': False,
        'ignoreerrors': True,  # 播放列表中某个视频失败时继续
        'progress_hooks': [download_progress_hook],
    }
    
    # 字幕下载配置（仅在下载视频时启用，音频不需要字幕）
    if not audio_only:
        ydl_opts.update({
            'writesubtitles': True,          # 下载手动字幕
            'writeautomaticsub': True,      # 下载自动生成的字幕（如果手动字幕不可用）
            'subtitleslangs': ['en', 'zh-CN', 'zh-TW', 'zh'],  # 优先语言顺序：英文 > 简体中文 > 繁体中文
            'subtitleformat': 'srt',        # 字幕格式为SRT
            'allsubtitles': False,          # 不下载所有语言
            # 如果优先语言都不可用，yt-dlp会自动下载可用的字幕
        })
    
    if audio_only:
        # 只下载音频
        ydl_opts.update({
            'format': 'bestaudio/best',
        })
        
        # 如果安装了 FFmpeg，转换为 MP3
        if check_ffmpeg():
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            print("⚠️  警告: 未检测到 FFmpeg，将下载原始音频格式（不转换为 MP3）")
    else:
        # 下载视频 - 优先使用 H.264 (AVC) 编码的mp4格式以获得更好的兼容性
        # yt-dlp 会自动合并视频和音频流（有FFmpeg用FFmpeg，没有用内置工具）
        if quality == 'best':
            # 优先下载高质量分离流并合并为mp4，失败则降级到预合并的best
            ydl_opts['format'] = 'bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best'
            ydl_opts['merge_output_format'] = 'mp4'  # 合并后输出为mp4
        elif quality == 'worst':
            ydl_opts['format'] = 'worst'
        elif quality.endswith('p'):
            # 指定分辨率，如 1080p, 720p, 480p - 优先 H.264 编码的mp4
            height = quality[:-1]
            ydl_opts['format'] = f'bestvideo[ext=mp4][height<={height}][vcodec^=avc]+bestaudio[ext=m4a]/best[height<={height}]'
            ydl_opts['merge_output_format'] = 'mp4'  # 合并后输出为mp4
    
    return ydl_opts


def download_progress_hook(d):
    """下载进度回调"""
    if d['status'] == 'downloading':
        # 显示下载进度
        if 'total_bytes' in d:
            percent = d['downloaded_bytes'] / d['total_bytes'] * 100
            speed = d.get('speed', 0)
            speed_str = f"{speed/1024/1024:.2f} MB/s" if speed else "N/A"
            print(f"\r下载中: {percent:.1f}% | 速度: {speed_str}", end='', flush=True)
        elif '_percent_str' in d:
            print(f"\r下载中: {d['_percent_str']} | 速度: {d.get('_speed_str', 'N/A')}", end='', flush=True)
    elif d['status'] == 'finished':
        print("\n处理完成，正在合并文件...")


def validate_url(url):
    """
    验证 URL 是否为有效的 YouTube URL
    
    Args:
        url: 待验证的 URL
        
    Returns:
        bool: 是否有效
    """
    youtube_domains = ['youtube.com', 'youtu.be', 'youtube-nocookie.com', 'm.youtube.com']
    return any(domain in url.lower() for domain in youtube_domains)


def download_video(url, output_dir="./downloads", quality="best", audio_only=False):
    """
    下载 YouTube 视频
    
    Args:
        url: YouTube 视频 URL
        output_dir: 下载保存目录
        quality: 视频质量 ('best', 'worst', '1080p', '720p', '480p' 等)
        audio_only: 是否只下载音频
    """
    # 验证 URL
    if not validate_url(url):
        print(f"⚠️  警告: URL 可能不是有效的 YouTube 链接: {url}")
        response = input("是否继续? (y/n): ").strip().lower()
        if response != 'y':
            print("已取消下载")
            return
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 获取下载配置
    ydl_opts = get_download_options(output_path, quality, audio_only, is_playlist=False)
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"\n开始下载: {url}")
            print(f"保存到: {output_dir}\n")
            ydl.download([url])
            
            # 检查是否有字幕文件，如果没有，尝试下载任意可用字幕
            if not audio_only:
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
            
            print("\n✅ 下载完成!")
    except KeyboardInterrupt:
        print("\n\n⚠️  下载已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 下载失败: {str(e)}")
        print("\n可能的原因:")
        print("  1. 网络连接问题")
        print("  2. 视频不可用或已删除")
        print("  3. 视频有地区限制")
        print("  4. URL 格式不正确")
        sys.exit(1)


def download_playlist(url, output_dir="./downloads", quality="best", audio_only=False):
    """
    下载 YouTube 播放列表
    
    Args:
        url: YouTube 播放列表 URL
        output_dir: 下载保存目录
        quality: 视频质量
        audio_only: 是否只下载音频
    """
    # 验证 URL
    if not validate_url(url):
        print(f"⚠️  警告: URL 可能不是有效的 YouTube 链接: {url}")
        response = input("是否继续? (y/n): ").strip().lower()
        if response != 'y':
            print("已取消下载")
            return
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 获取下载配置
    ydl_opts = get_download_options(output_path, quality, audio_only, is_playlist=True)
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            print(f"\n开始下载播放列表: {url}")
            print(f"保存到: {output_dir}\n")
            ydl.download([url])
            print("\n✅ 播放列表下载完成!")
    except KeyboardInterrupt:
        print("\n\n⚠️  下载已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 下载失败: {str(e)}")
        print("\n可能的原因:")
        print("  1. 网络连接问题")
        print("  2. 播放列表不可用或已删除")
        print("  3. 播放列表有访问限制")
        print("  4. URL 格式不正确")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='简单的 YouTube 视频下载器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 下载单个视频（最佳质量）
  python download.py "https://www.youtube.com/watch?v=VIDEO_ID"
  
  # 下载到指定目录
  python download.py "https://www.youtube.com/watch?v=VIDEO_ID" -o "./my_videos"
  
  # 下载 720p 视频
  python download.py "https://www.youtube.com/watch?v=VIDEO_ID" -q 720p
  
  # 只下载音频（MP3）
  python download.py "https://www.youtube.com/watch?v=VIDEO_ID" --audio
  
  # 下载播放列表
  python download.py "https://www.youtube.com/playlist?list=PLAYLIST_ID" -o "./playlist"
        """
    )
    
    parser.add_argument('url', nargs='?', help='YouTube 视频或播放列表 URL')
    parser.add_argument('-o', '--output', default=None,
                        help='下载保存目录 (默认: ./downloads/时分秒)')
    parser.add_argument('-q', '--quality', default='best',
                        choices=['best', 'worst', '1080p', '720p', '480p', '360p', '240p'],
                        help='视频质量 (默认: best - 最高质量)')
    parser.add_argument('-a', '--audio', action='store_true',
                        help='只下载音频（MP3格式，需要 FFmpeg）')
    parser.add_argument('-p', '--playlist', action='store_true',
                        help='下载播放列表')
    parser.add_argument('--check-ffmpeg', action='store_true',
                        help='检查 FFmpeg 是否已安装')
    
    args = parser.parse_args()
    
    # 检查 FFmpeg
    if args.check_ffmpeg:
        if check_ffmpeg():
            print("✅ FFmpeg 已安装")
        else:
            print("❌ FFmpeg 未安装")
            print("\n安装方法:")
            print("  macOS:    brew install ffmpeg")
            print("  Ubuntu:   sudo apt install ffmpeg")
            print("  Windows:  从 https://ffmpeg.org/download.html 下载")
        sys.exit(0)
    
    # 如果没有提供 URL，显示帮助
    if not args.url:
        parser.print_help()
        sys.exit(1)
    
    # 如果没有指定输出目录，使用日期文件夹（年月日格式）
    if args.output is None:
        date_folder = datetime.now().strftime("%Y-%m-%d")
        args.output = f"./downloads/{date_folder}"
    
    # 如果需要下载音频但没有 FFmpeg，提示用户
    if args.audio and not check_ffmpeg():
        print("⚠️  警告: 未检测到 FFmpeg")
        print("   将下载原始音频格式，不会转换为 MP3")
        print("   安装 FFmpeg 以获得更好的体验\n")
    
    if args.playlist or 'playlist' in args.url.lower():
        download_playlist(args.url, args.output, args.quality, args.audio)
    else:
        download_video(args.url, args.output, args.quality, args.audio)


if __name__ == '__main__':
    main()

