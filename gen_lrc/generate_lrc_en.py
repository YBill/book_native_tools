import os
from aeneas.executetask import ExecuteTask
from aeneas.task import Task

# 定义输入和输出文件夹路径
res_folder = "./resources"  # 存放 mp3 和 txt 文件的目录
output_folder = "./output"  # 存放生成的 json 文件的目录

# 确保输出目录存在
os.makedirs(output_folder, exist_ok=True)

# 遍历 res 文件夹中的所有文件
for file_name in os.listdir(res_folder):
    if file_name.endswith(".mp3"):  # 找到所有的 mp3 文件
        base_name = os.path.splitext(file_name)[0]  # 获取文件名（无后缀）
        text_file = os.path.join(res_folder, f"{base_name}.txt")  # 对应的 txt 文件路径
        audio_file = os.path.join(res_folder, file_name)  # mp3 文件路径
        output_file = os.path.join(output_folder, f"{base_name}.json")  # 输出的 json 文件路径

        # 检查 txt 文件是否存在
        if not os.path.exists(text_file):
            print(f"Warning: Text file for {file_name} not found. Skipping...")
            continue

        print(f"Processing {file_name} with {base_name}.txt...")

        # 配置 Aeneas 任务
        config_string = "task_language=eng|os_task_file_format=json|is_text_type=plain"
        task = Task(config_string=config_string)
        task.audio_file_path_absolute = audio_file
        task.text_file_path_absolute = text_file
        task.sync_map_file_path_absolute = output_file

        try:
            # 执行同步任务
            ExecuteTask(task).execute()
            # 输出同步后的 JSON 文件
            task.output_sync_map_file()
            print(f"Generated: {output_file}")
        except Exception as e:
            print(f"Error processing {file_name}: {str(e)}")
