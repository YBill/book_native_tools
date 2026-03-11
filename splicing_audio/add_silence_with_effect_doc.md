# add_silence_with_effect.py 方案文档

## 功能概述

对指定的 MP3 音频文件进行处理，在音频首尾添加静音段，并在结尾附加一个音效文件，最终输出格式与原文件保持一致。

## 处理流程

```
[1秒静音] + [原音频] + [0.5秒静音] + [effect.mp3] → 输出MP3
```

## 目录结构要求

```
项目根目录/
├── add_silence_with_effect.py
├── effect.mp3              # 结尾音效文件（必须存在）
├── audio/                  # 源音频目录
│   ├── 483_9.mp3
│   └── 885_8.mp3
└── audio_with_silence/     # 输出目录（自动创建）
```

## 配置项

脚本顶部有三个配置项，修改时只需调整这些变量：

```python
# 待处理的文件列表（可添加多个）
target_files = [
    Path('audio/483_9.mp3'),
    Path('audio/885_8.mp3'),
]

# 结尾音效文件路径
effect_file = Path('effect.mp3')

# 输出目录
output_dir = Path('audio_with_silence')
```

## 核心技术方案

### 1. 自动检测原音频参数

使用 `ffprobe` 读取每个音频文件的参数：

| 参数 | 说明 | 回退默认值 |
|------|------|-----------|
| `sample_rate` | 采样率（如 44100、16000） | 44100 |
| `channels` | 声道数（1=单声道，2=立体声） | 2 |
| `bit_rate` | 码率（如 64k、192k） | 192k |

### 2. FFmpeg 拼接命令

输入流索引对应关系：

| 索引 | 内容 | 时长 |
|------|------|------|
| `[0:a]` | 原音频 | 原始时长 |
| `[1:a]` | 开头静音（anullsrc） | 1 秒 |
| `[2:a]` | 结尾静音（anullsrc） | 0.5 秒 |
| `[3:a]` | effect.mp3 | 音效原始时长 |

拼接 filter：
```
[1:a][0:a][2:a][3:a]concat=n=4:v=0:a=1[out]
```

### 3. 输出编码

- 编码器：`libmp3lame`
- 码率：与原音频一致（自动检测）
- 采样率：与原音频一致（anullsrc 参数匹配）
- 声道数：与原音频一致（anullsrc channel_layout 匹配）

## 输出结果说明

| 项目 | 说明 |
|------|------|
| 输出文件名 | 与原文件名相同 |
| 输出位置 | `audio_with_silence/` 目录 |
| 时长变化 | 原时长 + 1秒 + 0.5秒 + effect.mp3时长 |
| 格式 | 与原音频完全一致（编码/采样率/声道/码率） |

## 依赖环境

- Python 3.x
- FFmpeg（需在系统 PATH 中，包含 `ffmpeg` 和 `ffprobe` 命令）

## 错误处理

脚本对以下情况有明确的错误提示，不会中断整体流程：

- 源文件不存在 → 跳过并提示 `[ERROR] 文件不存在`
- effect.mp3 不存在 → 跳过并提示 `[ERROR] 音效文件不存在`
- ffprobe 获取参数失败 → 使用默认值（44100Hz, 立体声, 192kbps）并继续处理
- ffmpeg 处理失败 → 提示错误信息（stderr 前200字符）

## 扩展使用

如需处理其他文件，只需修改 `target_files` 列表：

```python
target_files = [
    Path('audio/your_file_1.mp3'),
    Path('audio/your_file_2.mp3'),
    # 继续添加...
]
```

如需处理整个目录下所有 MP3，可将 `target_files` 改为：

```python
target_files = list(Path('audio').glob('*.mp3'))
```
