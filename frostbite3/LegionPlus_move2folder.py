import os
import shutil
# 让用户输入inputfolder路径
inputfolder = input("请输入inputfolder的路径: ")
# 遍历inputfolder根目录下的所有文件
for filename in os.listdir(inputfolder):
    if not os.path.isdir(os.path.join(inputfolder, filename)) and not filename.endswith('.log'):
        # 使用自定义分隔符分割文件名
        parts = filename.split('_')
        if len(parts) > 1:
            common_prefix = parts[0]  # 获取共同前缀
            # 为共同前缀创建文件夹
            folder_path = os.path.join(inputfolder, common_prefix)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            # 移动所有具有共同前缀的文件到对应文件夹里
            original_path = os.path.join(inputfolder, filename)
            new_filename = '_'.join(parts[1:])  # 删除共同前缀
            target_path = os.path.join(folder_path, new_filename)
            # 检查目标路径是否是一个文件夹
            if not os.path.isdir(target_path):
                shutil.move(original_path, target_path)
                # 生成日志文件
                log_file = os.path.join(folder_path, f"{common_prefix}.log")
                with open(log_file, 'a') as log:
                    log.write(f"{filename} -> {new_filename}\n")
            else:
                print(f"无法移动文件，因为目标路径是一个文件夹: {target_path}")
        else:
            continue
input('DONE!')