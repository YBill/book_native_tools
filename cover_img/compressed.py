import os
from PIL import Image

# 输入与输出文件夹
input_dir = "cover"
output_dir = "handle"

# 创建输出文件夹（如果不存在）
os.makedirs(output_dir, exist_ok=True)

# 目标尺寸
target_width, target_height = 282, 418

# 支持的文件扩展名（忽略大小写）
supported_exts = ('.png', '.jpg', '.jpeg', '.webp')

# 检查 Pillow 版本中是否有 Resampling 属性
if hasattr(Image, 'Resampling'):
    resample_method = Image.Resampling.LANCZOS
else:
    resample_method = Image.LANCZOS  # 或者 Image.ANTIALIAS（取决于版本）

# 遍历输入文件夹中所有文件
for filename in os.listdir(input_dir):
    if not filename.lower().endswith(supported_exts):
        continue

    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)

    try:
        with Image.open(input_path) as img:
            width, height = img.size
            # 图片正好为目标尺寸，直接复制
            if width == target_width and height == target_height:
                img.save(output_path)
                print(f"{filename}: 尺寸正好，直接复制。")
            # 图片尺寸小于目标尺寸（宽或高任一小于）
            elif width < target_width or height < target_height:
                print(f"-------------- {filename}: 尺寸 ({width}x{height}) 小于目标尺寸 {target_width}x{target_height}，未处理。")
                img.save(output_path)
            # 图片尺寸大于目标尺寸（宽或高任一大于）
            else:
                resized_img = img.resize((target_width, target_height), resample=resample_method)
                resized_img.save(output_path)
                print(f"{filename}: 尺寸 ({width}x{height}) 大于目标尺寸，已缩放至 {target_width}x{target_height}。")
    except Exception as e:
        print(f"处理 {filename} 时出错: {e}")
