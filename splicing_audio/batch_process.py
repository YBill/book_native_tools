import os
import subprocess
import json
from pathlib import Path

# 目录配置
source_dir = Path('audio')
output_dir = Path('audio_with_silence')
effect_file = Path('effect.mp3')

# 创建输出目录
output_dir.mkdir(exist_ok=True)

# 检查 effect.mp3 是否存在
if not effect_file.exists():
    print(f"[ERROR] 音效文件不存在: {effect_file.absolute()}")
    exit(1)

# 获取所有 mp3 文件
mp3_files = sorted(source_dir.glob('*.mp3'))
total = len(mp3_files)

if total == 0:
    print(f"[ERROR] {source_dir} 目录下没有找到任何 mp3 文件")
    exit(1)

print(f"找到 {total} 个音频文件，开始处理...\n")

success_count = 0
error_count = 0

for index, input_file in enumerate(mp3_files, 1):
    print(f"[{index}/{total}] 处理: {input_file.name}")

    # 解析文件名
    stem = input_file.stem  # 去掉 .mp3 后缀
    parts = stem.split('_')

    if len(parts) < 3:
        print(f"  [ERROR] 文件名格式不符合 a_b_c 规则，跳过: {input_file.name}\n")
        error_count += 1
        continue

    mode = parts[2]  # 取第三段

    if mode not in ('0', '1'):
        print(f"  [ERROR] 文件名第三段必须为 0 或 1，当前为 '{mode}'，跳过: {input_file.name}\n")
        error_count += 1
        continue

    output_file = output_dir / input_file.name

    # 探测音频参数
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

        stream = probe_data['streams'][0]
        sample_rate = stream.get('sample_rate', '44100')
        channels = int(stream.get('channels', 2))

        bit_rate = stream.get('bit_rate')
        if not bit_rate:
            bit_rate = probe_data.get('format', {}).get('bit_rate', '192000')
        bit_rate_k = int(int(bit_rate) / 1000)

        channel_layout = 'stereo' if channels == 2 else 'mono'

        print(f"  音频参数: {sample_rate}Hz, {channels}声道, {bit_rate_k}kbps")

    except Exception as e:
        print(f"  [WARNING] 无法获取音频参数，使用默认值: {e}")
        sample_rate = '44100'
        channels = 2
        channel_layout = 'stereo'
        bit_rate_k = 192

    # 根据 mode 构建 ffmpeg 命令
    if mode == '0':
        # [1s静音] + [原音频] + [1s静音]
        print(f"  模式: 前后各加1s静音")
        cmd = [
            'ffmpeg',
            '-i', str(input_file),
            '-f', 'lavfi', '-t', '1',
            '-i', f'anullsrc=channel_layout={channel_layout}:sample_rate={sample_rate}',
            '-f', 'lavfi', '-t', '1',
            '-i', f'anullsrc=channel_layout={channel_layout}:sample_rate={sample_rate}',
            '-filter_complex', '[1:a][0:a][2:a]concat=n=3:v=0:a=1[out]',
            '-map', '[out]',
            '-c:a', 'libmp3lame',
            '-b:a', f'{bit_rate_k}k',
            '-y',
            str(output_file)
        ]
    else:
        # [1s静音] + [原音频] + [0.5s静音] + [effect.mp3]
        print(f"  模式: 开头1s静音 + 结尾0.5s静音 + effect.mp3")
        cmd = [
            'ffmpeg',
            '-i', str(input_file),
            '-f', 'lavfi', '-t', '1',
            '-i', f'anullsrc=channel_layout={channel_layout}:sample_rate={sample_rate}',
            '-f', 'lavfi', '-t', '0.5',
            '-i', f'anullsrc=channel_layout={channel_layout}:sample_rate={sample_rate}',
            '-i', str(effect_file),
            '-filter_complex', '[1:a][0:a][2:a][3:a]concat=n=4:v=0:a=1[out]',
            '-map', '[out]',
            '-c:a', 'libmp3lame',
            '-b:a', f'{bit_rate_k}k',
            '-y',
            str(output_file)
        ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
        if result.returncode == 0:
            print(f"  [OK] 已保存到: {output_file}\n")
            success_count += 1
        else:
            print(f"  [ERROR] 处理失败")
            if result.stderr:
                print(f"  错误信息: {result.stderr[:200]}\n")
            error_count += 1
    except Exception as e:
        print(f"  [ERROR] 执行失败: {e}\n")
        error_count += 1

print(f"完成！成功: {success_count} 个，失败/跳过: {error_count} 个")
print(f"输出目录: {output_dir.absolute()}")
