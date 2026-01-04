import os
import shutil
from PIL import Image

def process_images():
    # 路径配置
    cover_dir = os.path.abspath('cover')
    check_dir = os.path.join(os.path.dirname(cover_dir), 'check')
    os.makedirs(check_dir, exist_ok=True)  # 自动创建check文件夹

    # 目标尺寸和文件格式
    target_size = (282, 418)
    valid_exts = ('.png', '.jpg', '.jpeg', '.webp')
    invalid_records = []

    # 遍历cover文件夹
    for filename in os.listdir(cover_dir):
        if filename.lower().endswith(valid_exts):
            src_path = os.path.join(cover_dir, filename)
            
            try:
                # 打开图片并获取尺寸，确保文件在with块内关闭
                with Image.open(src_path) as img:
                    w, h = img.size
                
                if (w, h) != target_size:
                    # 记录文件名和尺寸
                    invalid_records.append(f"{filename} ({w}x{h})")
                    
                    # 移动文件到check文件夹
                    dest_path = os.path.join(check_dir, filename)
                    shutil.move(src_path, dest_path)
                    print(f"已移动：{filename}")

            except Exception as e:
                print(f"处理失败：{filename} | 错误：{str(e)}")

    # 写入检查报告
    report_path = os.path.join(check_dir, 'check.txt')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("异常图片列表（文件名及实际尺寸）：\n")
        f.write("\n".join(invalid_records))
    
    print(f"\n检查完成！共发现{len(invalid_records)}张异常图片")
    print(f"报告路径：{report_path}")

if __name__ == "__main__":
    process_images()
