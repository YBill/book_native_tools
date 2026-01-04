import os
import tinify

tinify.key = "2S2bdy3D4ZncVkTRKClRjLCRHQQnvXB9"

# 定义输入和输出文件夹路径
input_dir = "cover"
output_dir = "output"

# 如果输出文件夹不存在则创建
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"创建输出文件夹: {output_dir}")

# 定义需要处理的图片扩展名，包括 PNG、JPG、JPEG 和 WebP
valid_extensions = (".png", ".jpg", ".jpeg", ".webp")

# 统计需要处理的图片数量
image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(valid_extensions)]
total_files = len(image_files)

print(f"发现 {total_files} 张图片需要压缩")
print("开始压缩...")
print("=" * 50)

# 计数器
success_count = 0
error_count = 0

# 遍历输入文件夹中的所有文件
for index, filename in enumerate(image_files, 1):
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)

    # 获取文件大小（压缩前）
    original_size = os.path.getsize(input_path) / 1024  # KB

    print(f"[{index}/{total_files}] 正在压缩: {filename}")
    print(f"   原始大小: {original_size:.1f} KB")

    try:
        # 压缩图片
        source = tinify.from_file(input_path)
        source.to_file(output_path)

        # 获取文件大小（压缩后）
        compressed_size = os.path.getsize(output_path) / 1024  # KB
        compression_ratio = (1 - compressed_size / original_size) * 100

        print(f"   压缩后: {compressed_size:.1f} KB")
        print(f"   压缩率: {compression_ratio:.1f}%")
        print(f"   ✅ 压缩完成!")
        print("-" * 40)

        success_count += 1

    except tinify.Error as e:
        print(f"   ❌ 压缩失败: {e}")
        print("-" * 40)
        error_count += 1

# 最终统计
print("=" * 50)
print("🎉 批量压缩完成!")
print(f"✅ 成功: {success_count} 张")
print(f"❌ 失败: {error_count} 张")
print(f"📁 压缩后的图片保存在: {output_dir}")

# 显示API使用情况（如果可用）
try:
    compressions_this_month = tinify.compression_count
    print(f"📊 本月API使用量: {compressions_this_month}/500")
except:
    pass
