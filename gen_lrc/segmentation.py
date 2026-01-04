import os
import re

def split_text(text):
    text = text.replace('\\n', '\n')  # 如果有转义的换行符
    # 按段落进行分割
    paragraphs = text.split('\n\n')
    
    result = []
    # 正则表达式，用于根据标点和空格分割
    reg_exp = re.compile(r'(?<=[.,!?])[ \t]+')
    
    for paragraph in paragraphs:
        # 按句子进行分割
        sentences = reg_exp.split(paragraph)
        
        sentence_list = []
        for sentence in sentences:
            if sentence.strip():
                sentence_list.append(sentence.strip())
        
        if sentence_list:
            result.append(sentence_list)
    
    return result

def process_files(input_folder, output_folder):
    # 确保输出文件夹存在
    os.makedirs(output_folder, exist_ok=True)
    
    # 遍历输入文件夹下的所有txt文件
    for file_name in os.listdir(input_folder):
        if file_name.endswith('.txt'):
            input_path = os.path.join(input_folder, file_name)
            output_path = os.path.join(output_folder, file_name)
            
            # 读取文本内容
            with open(input_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            # 处理文本
            processed_text = split_text(text)
            
            # 写入输出文件
            with open(output_path, 'w', encoding='utf-8') as file:
                for paragraph in processed_text:
                    for sentence in paragraph:
                        file.write(sentence + '\n')

def main():
    input_folder = 'audio_lrc/txt'  # 输入文件夹
    output_folder = 'lrc'  # 输出文件夹
    process_files(input_folder, output_folder)

if __name__ == '__main__':
    main()
