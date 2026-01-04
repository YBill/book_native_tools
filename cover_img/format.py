# check_image_format.py
import sys
from PIL import Image

def get_real_format(file_path):
    try:
        with Image.open(file_path) as img:
            return img.format or "未知格式"
    except IOError:
        return "非图片文件或格式不支持"
    except Exception as e:
        return f"检测失败：{str(e)}"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python check_image_format.py 图片路径")
        sys.exit(1)
        
    file_path = sys.argv[1]
    print(f"真实格式：{get_real_format(file_path)}")