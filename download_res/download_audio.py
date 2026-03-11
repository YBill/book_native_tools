import json
import requests
from pathlib import Path

# 读取 task 文件
with open('task', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 创建 audio 目录（如果不存在）
audio_dir = Path('audio')
audio_dir.mkdir(exist_ok=True)

items = data['bs_book_points_vi']

# 预先计算每个 book_id 的最大 point_id，用于判断是否为最后一条（mode=1）
max_point_id = {}
for item in items:
    book_id = item['book_id']
    point_id = item['point_id']
    if book_id not in max_point_id or point_id > max_point_id[book_id]:
        max_point_id[book_id] = point_id

# 下载所有音频文件
total = len(items)
for index, item in enumerate(items, 1):
    book_id = item['book_id']
    point_id = item['point_id']
    audio_url = item['audio_url']

    # 最后一条为 mode=1，其余为 mode=0
    mode = 1 if point_id == max_point_id[book_id] else 0

    # 构建文件名
    filename = f"{book_id}_{point_id}_{mode}.mp3"
    filepath = audio_dir / filename

    print(f"[{index}/{total}] 下载: {filename}")

    try:
        # 下载文件
        response = requests.get(audio_url, timeout=30)
        response.raise_for_status()

        # 保存文件
        with open(filepath, 'wb') as f:
            f.write(response.content)

        print(f"  [OK] 成功保存到: {filepath}")
    except Exception as e:
        print(f"  [ERROR] 下载失败: {e}")

print(f"\n完成！所有音频文件已保存到 {audio_dir.absolute()} 目录")
