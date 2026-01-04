import os
from PIL import Image

# 定义目录路径
input_dir = 'cover'
output_dir = 'output'

# 创建输出目录（如果不存在）
os.makedirs(output_dir, exist_ok=True)

# 遍历输入目录中的所有文件
for filename in os.listdir(input_dir):
    # 检查文件是否是图片（简单检查扩展名）
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
        try:
            # 打开图片
            input_path = os.path.join(input_dir, filename)
            img = Image.open(input_path)
            
            # 计算新尺寸（缩小一倍）
            width, height = img.size
            new_width = width // 2
            new_height = height // 2
            
            # 等比例缩小图片
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # 保存图片到输出目录
            output_path = os.path.join(output_dir, filename)
            resized_img.save(output_path)
            
            print(f"已处理: {filename} ({width}x{height} -> {new_width}x{new_height})")
        except Exception as e:
            print(f"处理 {filename} 时出错: {e}")

print("所有图片处理完成！")