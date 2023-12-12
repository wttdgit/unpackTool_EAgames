import os
import subprocess
import re
import psutil
from concurrent.futures import ThreadPoolExecutor
from time import sleep

# 可能会变更的常量
INPUT_FORMAT = '.wav'
OUTPUT_FORMAT = '.ogg'
MAX_THREADS = 20  # 初始最大线程数
MAX_THRESHOLD = 90  # CPU占用率阈值
STOP_MONITOR = False  # 用于控制线程全局变量

def monitor_resources(executor, MAX_THRESHOLD, INPUT_FOLDER):
    global STOP_MONITOR
    while not STOP_MONITOR:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage(INPUT_FOLDER).percent
        # 获取三者中的最大值
        max_usage = max(cpu_usage, memory_usage, disk_usage)
        
        # 根据最大占用率调整线程数
        if max_usage < MAX_THRESHOLD:
            if executor._max_workers < MAX_THREADS:
                executor._max_workers += 1
        else:
            if executor._max_workers > 1:
                executor._max_workers -= 1
        sleep(1)

def convert_audio_file(inputFile_path, output_format, delete_original):
    outputFile_path = inputFile_path.replace(INPUT_FORMAT, output_format)
    outputFile_path = outputFile_path.replace(INPUT_FOLDER, OUTPUT_FOLDER)
    os.makedirs(os.path.dirname(outputFile_path), exist_ok=True)
    
    try:
        # 获取输入文件的码率和声道数
        getInfo_inputFile = ['vgmstream-cli.exe', '-m', inputFile_path]
        chkInfo_inputFile = subprocess.check_output(getInfo_inputFile, stderr=subprocess.STDOUT).decode()
        bitrate_match = re.search(r'bitrate: (\d+) kbps', chkInfo_inputFile)
        channels_match = re.search(r'channels: (\d+)', chkInfo_inputFile)
        bitrate = bitrate_match.group(1) if bitrate_match else '128'
        channels = channels_match.group(1) if channels_match else '2'
        
        # 转码输入文件到输出格式
        # WAV2OGG = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', inputFile_path, '-b:a', f'{bitrate}k', '-ac', channels, outputFile_path], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        WAV2OGG = subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-i', inputFile_path, '-ac', channels, '-n', outputFile_path], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        if WAV2OGG.returncode != 0:
            print(f"Error converting file {inputFile_path}: {WAV2OGG.stderr.decode()}")
        else:
            print(f"Converted *chn-{channels} @ {bitrate}kbps : {outputFile_path}")
            if delete_original:
                os.remove(inputFile_path)
    except Exception as e:
        print(f"An error occurred while converting file {inputFile_path}: {e}")

def process_files_with_executor(INPUT_FOLDER, input_format, output_format):
    global STOP_MONITOR 
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        monitor_thread = executor.submit(monitor_resources, executor, MAX_THRESHOLD, INPUT_FOLDER)
        for root, dirs, files in os.walk(INPUT_FOLDER):
            for file in files:
                if file.lower().endswith(input_format):
                    inputFile_path = os.path.join(root, file)
                    executor.submit(convert_audio_file, inputFile_path, output_format, delete_original)
        STOP_MONITOR = True  # 设置标志以停止监控线程
        monitor_thread.result()  # 等待监控线程完成

if __name__ == "__main__":
    INPUT_FOLDER = input("请输入sound文件夹的路径：")
    OUTPUT_FOLDER = input("请输入导出文件夹的路径：")
    delete_original = input("是否删除原始文件？(y/n): ").lower() == 'y'
    process_files_with_executor(INPUT_FOLDER, INPUT_FORMAT, OUTPUT_FORMAT)
    input('Done!')


