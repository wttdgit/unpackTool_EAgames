import os
import shutil

# 让用户输入inputfolder路径
inputfolder = input("请输入inputfolder的路径: ")

# 遍历inputfolder下的所有子文件夹
for foldername in os.listdir(inputfolder):
    folder_path = os.path.join(inputfolder, foldername)
    if os.path.isdir(folder_path):
        # 读取日志文件
        log_file = os.path.join(folder_path, f"{foldername}.log")
        if os.path.exists(log_file):
            with open(log_file, 'r') as log:
                for line in log:
                    parts = line.strip().split(' -> ')
                    original_filename = parts[0]
                    new_filename = parts[1]
                    # 将文件移回父文件夹并恢复原始文件名
                    original_path = os.path.join(folder_path, new_filename)
                    new_original_path = os.path.join(inputfolder, original_filename)
                    shutil.move(original_path, new_original_path)
            # 删除日志文件
            os.remove(log_file)

        # 检查子文件夹是否为空，如果是，则删除
        if not os.listdir(folder_path):
            os.rmdir(folder_path)

print("逆向操作完成，所有文件已移回父文件夹，相关日志文件已删除。")
input('DONE!')