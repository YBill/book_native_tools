import os
import subprocess
import imghdr
import shutil  # 新增模块用于文件复制

input_dir = 'cover'
output_dir = 'output'
error_dir = 'error'  # 新增错误目录
pngquant_exe = r'D:\tools\pngquant\pngquant.exe'
error_log = os.path.join(error_dir, 'check.txt')  # 修改日志路径

# 创建所有必要目录
os.makedirs(output_dir, exist_ok=True)
os.makedirs(error_dir, exist_ok=True)  # 新增错误目录创建[4](@ref)

# 初始化日志文件（移动到错误目录）
with open(error_log, 'a', encoding='utf-8') as f:
    f.write("========= 错误日志 =========\n")

for filename in os.listdir(input_dir):
    input_path = os.path.join(input_dir, filename)
    output_path = os.path.join(output_dir, filename)
    error_file_path = os.path.join(error_dir, filename)  # 错误文件路径

    # 验证文件类型（双重检查）
    is_png = False
    if filename.lower().endswith('.png'):
        try:
            is_png = imghdr.what(input_path) == 'png'
        except Exception as e:
            print(f"文件检测异常: {filename} - {str(e)}")

    # 处理非PNG文件
    if not is_png:
        # 复制文件到错误目录[6](@ref)
        try:
            shutil.copy2(input_path, error_file_path)
            log_msg = f"{filename} [已复制到错误目录] - 不支持压缩\n"
        except Exception as copy_error:
            log_msg = f"{filename} [复制失败] - {str(copy_error)}\n"
        
        with open(error_log, 'a', encoding='utf-8') as f:
            f.write(log_msg)
        continue

    # 执行压缩
    cmd = [
        pngquant_exe,
        '--force',
        '--verbose',
        '--quality=45-85',
        '--output', output_path,
        input_path
    ]
    
    print(f"正在处理: {input_path} -> {output_path}")
    try:
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        # 压缩失败时复制文件到错误目录[6](@ref)
        try:
            shutil.copy2(input_path, error_file_path)
            error_msg = f"{filename} [已复制到错误目录] - 压缩失败: {e.stderr.strip()}\n"
        except Exception as copy_error:
            error_msg = f"{filename} [复制失败] - {str(copy_error)}\n"
        
        with open(error_log, 'a', encoding='utf-8') as f:
            f.write(error_msg)
        print(f"处理失败: {e.stderr.strip()}")
    except Exception as e:
        # 其他异常时复制文件
        try:
            shutil.copy2(input_path, error_file_path)
            error_msg = f"{filename} [已复制到错误目录] - 未知错误: {str(e)}\n"
        except Exception as copy_error:
            error_msg = f"{filename} [复制失败] - {str(copy_error)}\n"
        
        with open(error_log, 'a', encoding='utf-8') as f:
            f.write(error_msg)
        print(f"未知错误: {str(e)}")