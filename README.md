# YouTube 视频下载器

一个简单易用的 YouTube 视频下载工具，使用 Python 和 yt-dlp 库。

## 🚀 快速开始

**最简单的方式（推荐新手）：**

```bash
./一键运行.sh
```

或者手动运行：

```bash
python download_simple.py
```

然后按照提示操作即可！

---

## 功能特点

- ✅ 下载单个视频
- ✅ 下载播放列表
- ✅ 批量下载（从文件读取多个URL）
- ✅ 选择视频质量（最佳、1080p、720p、480p、360p 等）
- ✅ 只下载音频（MP3 格式）
- ✅ 实时显示下载进度和速度
- ✅ 自动检测 FFmpeg
- ✅ URL 验证
- ✅ 详细的错误提示
- ✅ 自动创建下载目录
- ✅ 三种使用方式：命令行、交互式、批量下载

## 安装

### 1. 安装 Python

确保你的系统已安装 Python 3.7 或更高版本。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

或者直接安装：

```bash
pip install yt-dlp
```

### 3. 安装 FFmpeg（可选，但推荐）

**作用：**
- ✅ **音频转换**：下载音频时转换为 MP3 格式
- ✅ **视频合并**：合并高质量视频和音频流（速度更快）
- ⚠️  **非必需**：没有 FFmpeg 时，yt-dlp 会使用内置工具，但速度较慢

#### macOS:
```bash
brew install ffmpeg
```

#### Windows:
从 [FFmpeg 官网](https://ffmpeg.org/download.html) 下载并添加到系统 PATH

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install ffmpeg
```

检查是否已安装：
```bash
python download.py --check-ffmpeg
```

## 使用方法

本项目提供三种使用方式，选择最适合你的：

### 方式 1: 交互式版本（最简单，推荐新手）

直接运行，按提示输入即可：

```bash
python download_simple.py
```

程序会引导你：
1. 输入视频 URL
2. 选择质量（最佳/1080p/720p/480p/音频）
3. 选择保存目录

### 方式 2: 命令行版本（灵活，适合高级用户）

#### 下载单个视频（最佳质量）

```bash
python download.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

#### 下载到指定目录

```bash
python download.py "https://www.youtube.com/watch?v=VIDEO_ID" -o "./my_videos"
```

#### 下载指定质量

```bash
# 1080p
python download.py "https://www.youtube.com/watch?v=VIDEO_ID" -q 1080p

# 720p
python download.py "https://www.youtube.com/watch?v=VIDEO_ID" -q 720p

# 480p
python download.py "https://www.youtube.com/watch?v=VIDEO_ID" -q 480p
```

#### 只下载音频（MP3）

```bash
python download.py "https://www.youtube.com/watch?v=VIDEO_ID" --audio
```

#### 下载播放列表

```bash
python download.py "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

#### 检查 FFmpeg 是否安装

```bash
python download.py --check-ffmpeg
```

#### 查看帮助

```bash
python download.py --help
```

### 方式 3: 批量下载（适合下载多个视频）

1. 创建一个文本文件（如 `urls.txt`），每行写一个视频 URL：

```text
# 我的视频列表
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
https://www.youtube.com/watch?v=VIDEO_ID_3
```

2. 运行批量下载脚本：

```bash
python batch_download.py
```

程序会提示你输入文件路径和选择质量。

## 命令行参数（download.py）

- `url`: YouTube 视频或播放列表 URL（必需）
- `-o, --output`: 下载保存目录（默认：./downloads）
- `-q, --quality`: 视频质量，可选：best, worst, 1080p, 720p, 480p, 360p, 240p（默认：best）
- `-a, --audio`: 只下载音频（MP3 格式，需要 FFmpeg）
- `-p, --playlist`: 明确指定下载播放列表
- `--check-ffmpeg`: 检查 FFmpeg 是否已安装

## 完整示例

```bash
# 下载一个视频到默认目录
python download.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 下载 1080p 视频到指定目录
python download.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o "./videos" -q 1080p

# 下载 720p 视频
python download.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 720p

# 下载音频（MP3）
python download.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --audio

# 下载整个播放列表
python download.py "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMnF6j0j-pfHVzS3Vq" -o "./playlist_videos"

# 下载播放列表中的音频
python download.py "https://www.youtube.com/playlist?list=PLrAXtmRdnEQy6nuLMnF6j0j-pfHVzS3Vq" --audio
```

## 项目文件说明

### 核心脚本
- `download.py` - 命令行版本，功能最全面
- `download_simple.py` - 交互式版本，最简单易用（推荐新手）
- `batch_download.py` - 批量下载版本，从文件读取多个URL
- `一键运行.sh` - 快速启动脚本（自动配置环境）

### 配置和文档
- `README.md` - 完整使用说明（本文件）
- `urls_example.txt` - URL 列表示例文件
- `requirements.txt` - Python 依赖包
- `.gitignore` - Git 版本控制忽略规则

### 目录结构
- `downloads/` - 下载的视频保存目录（按日期组织：YYYY-MM-DD）
- `venv/` - Python 虚拟环境（自动创建）

## 注意事项

1. 请遵守 YouTube 的服务条款和版权法律
2. 仅下载你有权限下载的内容
3. 某些视频可能因为版权限制无法下载

## 常见问题

### 安装 yt-dlp 失败？

尝试使用国内镜像：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple yt-dlp
```

### 下载速度慢？

- 检查网络连接
- 尝试使用 VPN（如果在某些地区受限）

### 音频转换失败？

确保已安装 FFmpeg（见安装说明）

## 许可证

MIT License

