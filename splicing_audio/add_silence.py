import os
import subprocess
import json
from pathlib import Path

# 源目录和目标目录
source_dir = Path('audio')
output_dir = Path('audio_with_silence')

# 创建输出目录
output_dir.mkdir(exist_ok=True)

# 获取所有 mp3 文件
mp3_files = list(source_dir.glob('*.mp3'))
total = len(mp3_files)

print(f"找到 {total} 个音频文件，开始处理...\n")

for index, input_file in enumerate(mp3_files, 1):
    output_file = output_dir / input_file.name

    print(f"[{index}/{total}] 处理: {input_file.name}")

    # 获取原音频的参数
    probe_cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'a:0',
        '-show_entries', 'stream=sample_rate,channels,bit_rate',
        '-show_entries', 'format=bit_rate',
        '-of', 'json',
        str(input_file)
    ]

    try:
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        probe_data = json.loads(probe_result.stdout)

        # 获取音频参数
        stream = probe_data['streams'][0]
        sample_rate = stream.get('sample_rate', '44100')
        channels = int(stream.get('channels', 2))

        # 获取码率（优先使用stream的bit_rate，如果没有则使用format的）
        bit_rate = stream.get('bit_rate')
        if not bit_rate:
            bit_rate = probe_data.get('format', {}).get('bit_rate', '192000')
        bit_rate_k = int(int(bit_rate) / 1000)  # 转换为 kbps

        # 根据声道数设置channel_layout
        channel_layout = 'stereo' if channels == 2 else 'mono'

        print(f"  音频参数: {sample_rate}Hz, {channels}声道, {bit_rate_k}kbps")

    except Exception as e:
        print(f"  [WARNING] 无法获取音频参数，使用默认值: {e}")
        sample_rate = '44100'
        channels = 2
        channel_layout = 'stereo'
        bit_rate_k = 192

    # 使用 ffmpeg 在音频开头和结尾添加1秒静音
    # -f lavfi -t 1 -i anullsrc 生成1秒空白音频
    # -filter_complex "[1:a][0:a][2:a]concat=n=3:v=0:a=1" 将空白音频+原音频+空白音频拼接
    cmd = [
        'ffmpeg',
        '-i', str(input_file),           # 输入原音频
        '-f', 'lavfi',                   # 使用 lavfi 滤镜
        '-t', '1',                       # 1秒时长
        '-i', f'anullsrc=channel_layout={channel_layout}:sample_rate={sample_rate}',  # 生成开头空白音频
        '-f', 'lavfi',                   # 使用 lavfi 滤镜
        '-t', '1',                       # 1秒时长
        '-i', f'anullsrc=channel_layout={channel_layout}:sample_rate={sample_rate}',  # 生成结尾空白音频
        '-filter_complex', '[1:a][0:a][2:a]concat=n=3:v=0:a=1[out]',   # 拼接：空白+原音频+空白
        '-map', '[out]',                 # 映射输出
        '-c:a', 'libmp3lame',           # 使用 mp3 编码
        '-b:a', f'{bit_rate_k}k',       # 保持原码率
        '-y',                            # 覆盖已存在文件
        str(output_file)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            print(f"  [OK] 已保存到: {output_file}")
        else:
            print(f"  [ERROR] 处理失败")
            if result.stderr:
                print(f"  错误信息: {result.stderr[:200]}")
    except Exception as e:
        print(f"  [ERROR] 执行失败: {e}")

print(f"\n完成！处理后的文件保存在 {output_dir.absolute()} 目录")
