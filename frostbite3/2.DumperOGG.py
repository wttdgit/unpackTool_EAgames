import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
import ebx
import res
import re
def process_files_with_executor(folder_path, file_extension, task_function, *args):
    with ThreadPoolExecutor() as executor:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(file_extension):
                    file_path = os.path.join(root, file)
                    executor.submit(task_function, file_path, *args)
def convert_ebx_to_sps(input_folder, sound_folder, output_folder, chunkFolder1, chunkFolder2, resFolder, ebxFolder):
    ebx.loadGuidTable(input_folder)
    res.loadResTable(input_folder)
    process_files_with_executor(sound_folder, '.ebx', dump_ebx, output_folder, chunkFolder1, chunkFolder2, resFolder, ebxFolder)
def dump_ebx(dbx_path, output_folder, chunkFolder1, chunkFolder2, resFolder, ebxFolder):
    dbx = ebx.Dbx(dbx_path, ebxFolder)
    txt_output_path = os.path.join(output_folder, dbx.trueFilename + ".txt")
    dbx.dump(txt_output_path)
    dbx.extractAssets(chunkFolder1, chunkFolder2, resFolder, output_folder)
def convert_sps_to_wav(sps_path):
    wav_path = sps_path.replace('.sps', '.wav')
    ogg_path = sps_path.replace('.sps', '.ogg')
    os.makedirs(os.path.dirname(ogg_path), exist_ok=True)
    info_command = ['vgmstream-cli.exe', '-m', sps_path]
    output = subprocess.check_output(info_command).decode()
    bitrate_match = re.search(r'bitrate: (\d+) kbps', output)
    channels_match = re.search(r'channels: (\d+)', output)
    bitrate = bitrate_match.group(1) if bitrate_match else '128'
    channels = channels_match.group(1) if channels_match else '2'
    SPS2WAV = subprocess.run(['vgmstream-cli.exe', '-o', wav_path, sps_path], stdout=subprocess.DEVNULL)
    if SPS2WAV.returncode == 0 and os.path.getsize(wav_path) > 0:
        convert_wav_to_ogg(wav_path, bitrate, channels, ogg_path)
        os.remove(sps_path)
    else:
        print(f"Error converting {sps_path} to WAV.")
def convert_wav_to_ogg(wav_path, bitrate, channels, ogg_path):
    WAV2OGG = subprocess.run(['ffmpeg.exe ', '-hide_banner', '-loglevel', 'error', '-i', wav_path, '-b:a', f'{bitrate}k', '-ac', channels, ogg_path], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    if WAV2OGG.returncode != 0:
        print(WAV2OGG.stderr.decode())
    else:
        print(f"Converted *chn-{channels} @ {bitrate}kbps : {ogg_path}")
        os.remove(wav_path)
def main():
    input_folder = os.path.normpath(input("Input dump path like E:\\unpack_Battlefield4: "))
    output_folder = os.path.normpath(f"{input_folder}_Sound")
    os.makedirs(output_folder, exist_ok=True)
    ebxFolder = os.path.join(input_folder, "bundles", "ebx")
    resFolder = os.path.join(input_folder, "bundles", "res")
    chunkFolder1 = os.path.join(input_folder, "chunks")
    chunkFolder2 = os.path.join(input_folder, "bundles", "chunks")
    sound_folder = os.path.join(ebxFolder, "sound")
    convert_ebx_to_sps(input_folder, sound_folder, output_folder, chunkFolder1, chunkFolder2, resFolder, ebxFolder)
    process_files_with_executor(output_folder, '.sps', convert_sps_to_wav)
    input('Done!')
if __name__ == "__main__":
    main()