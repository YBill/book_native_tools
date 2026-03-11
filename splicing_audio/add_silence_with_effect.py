import subprocess
import json
from pathlib import Path

# 待处理的文件
target_files = [
    Path('audio/483_9.mp3'),
    Path('audio/885_8.mp3'),
]

# 结束音效
effect_file = Path('effect.mp3')

# 输出目录
output_dir = Path('audio_with_silence')
output_dir.mkdir(exist_ok=True)

total = len(target_files)
print(f"共 {total} 个文件，开始处理...\n")

for index, input_file in enumerate(target_files, 1):
    output_file = output_dir / input_file.name

    print(f"[{index}/{total}] 处理: {input_file.name}")

    if not input_file.exists():
        print(f"  [ERROR] 文件不存在: {input_file}")
        continue

    if not effect_file.exists():
        print(f"  [ERROR] 音效文件不存在: {effect_file}")
        continue

    # 获取原音频参数
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

    # 拼接顺序：1秒静音 + 原音频 + 1秒静音 + effect.mp3
    # 输入索引：
    #   0 = 原音频
    #   1 = 开头1秒静音 (anullsrc)
    #   2 = 结尾1秒静音 (anullsrc)
    #   3 = effect.mp3
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
            print(f"  [OK] 已保存到: {output_file}")
        else:
            print(f"  [ERROR] 处理失败")
            if result.stderr:
                print(f"  错误信息: {result.stderr[:200]}")
    except Exception as e:
        print(f"  [ERROR] 执行失败: {e}")

print(f"\n完成！处理后的文件保存在 {output_dir.absolute()} 目录")
