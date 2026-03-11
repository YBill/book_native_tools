# download_audio.py 方案文档

## 功能概述

读取 `task` 文件中的音频资源列表，批量下载 MP3 文件到 `audio/` 目录，并按照 `batch_process.py` 所需的三段式命名规则自动命名。

## 处理流程

```
task (JSON)
└── bs_book_points_vi[]
    ├── 预处理：按 book_id 分组，求各组最大 point_id
    └── 下载：{book_id}_{point_id}_{mode}.mp3 → audio/
```

## 目录结构要求

```
项目根目录/
├── download_audio.py
├── task                    # 资源列表文件（JSON 格式，无扩展名）
└── audio/                  # 输出目录（自动创建）
```

## task 文件格式

`task` 为 JSON 文件，包含 `bs_book_points_vi` 数组，每条记录三个字段：

```json
{
  "bs_book_points_vi": [
    {
      "book_id": 483,
      "point_id": 0,
      "audio_url": "https://..."
    },
    {
      "book_id": 483,
      "point_id": 9,
      "audio_url": "https://..."
    }
  ]
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `book_id` | int | 书籍 ID，作为文件名第一段 |
| `point_id` | int | 知识点 ID，作为文件名第二段 |
| `audio_url` | string | 音频下载地址 |

## 文件命名规则

输出文件名格式：`{book_id}_{point_id}_{mode}.mp3`

| 段位 | 来源 | 说明 |
|------|------|------|
| `book_id` | `item['book_id']` | 书籍 ID |
| `point_id` | `item['point_id']` | 知识点 ID |
| `mode` | 自动判断 | 同一 book_id 下 point_id 最大的记录为 `1`，其余为 `0` |

**示例**（book_id=483，共10条，point_id 0~9）：

```
483_0_0.mp3
483_1_0.mp3
...
483_8_0.mp3
483_9_1.mp3   ← point_id 最大，mode=1
```

mode 含义与 `batch_process.py` 对应：

| mode | 后续处理方式 |
|------|------------|
| `0` | 前后各加 1s 静音 |
| `1` | 开头 1s 静音 + 结尾 0.5s 静音 + effect.mp3 |

## 核心技术方案

### 1. 预处理：计算各 book_id 最大 point_id

下载前先遍历全量数据，按 `book_id` 分组求最大 `point_id`，存入字典：

```python
max_point_id = {}
for item in items:
    book_id = item['book_id']
    point_id = item['point_id']
    if book_id not in max_point_id or point_id > max_point_id[book_id]:
        max_point_id[book_id] = point_id
```

### 2. 下载时判断 mode

```python
mode = 1 if point_id == max_point_id[book_id] else 0
```

### 3. 文件下载

使用 `requests.get` 下载，`timeout=30` 秒，`raise_for_status()` 检查 HTTP 状态码。

## 运行方式

在脚本所在目录下执行：

```bash
python download_audio.py
```

运行日志示例：

```
[1/10] 下载: 483_0_0.mp3
  [OK] 成功保存到: audio\483_0_0.mp3
[2/10] 下载: 483_1_0.mp3
  [OK] 成功保存到: audio\483_1_0.mp3
...
[10/10] 下载: 483_9_1.mp3
  [OK] 成功保存到: audio\483_9_1.mp3

完成！所有音频文件已保存到 D:\...\audio 目录
```

## 依赖环境

- Python 3.x
- requests（`pip install requests`）

## 错误处理

| 情况 | 处理方式 |
|------|---------|
| HTTP 请求失败（4xx/5xx） | `raise_for_status()` 抛出异常，输出 `[ERROR]`，继续下一个 |
| 网络超时（超过30秒） | 抛出异常，输出 `[ERROR]`，继续下一个 |
| task 文件不存在或格式错误 | 抛出异常，脚本终止 |
