

import base64
import os
import shutil
import time
import zipfile

from tools.time_util import hour_in_seconds


def  checkDir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        

def  createNewDir(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    os.makedirs(output_dir)

def  deleteDir(path):
    shutil.rmtree(path)

def file2zip(zip_file_name: str, file_names: list):
    
    print("file_names", file_names)
    # 读取写入方式 ZipFile requires mode 'r', 'w', 'x', or 'a'
    # 压缩方式  ZIP_STORED： 存储； ZIP_DEFLATED： 压缩存储
    with zipfile.ZipFile(zip_file_name, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
        for fn in file_names:
            parent_path, name = os.path.split(fn)
            zf.write(fn, arcname=name)


def audio_to_base64(audio_path):
    with open(audio_path, "rb") as audio_file:
        audio_data = audio_file.read()
        base64_data = base64.b64encode(audio_data)
        
        base64_data = base64_data.decode('utf-8')
        return base64_data
 

def base64_to_audio(base64_path, output_path):
    
    with open(base64_path, "r") as base64_file:
        base64_data = base64_file.read()
    audio_data = base64.b64decode(base64_data)
    with open(output_path, "wb") as audio_file:
        audio_file.write(audio_data)
        audio_file.close()

def saveToFile(content, file_path):
    # 打开文件
    file = open(file_path, "w")
    # 要保存的字符串
    # 写入文件
    file.write(content)
    # 关闭文件
    file.close()



def delete_old_items(target_directory):
    
    print("delete old files")
    # 当前时间的时间戳
    now = time.time()

    one_day_ago = now - 3 * hour_in_seconds

    # 遍历目标目录的所有子文件和子目录
    for item_name in os.listdir(target_directory):
        item_path = os.path.join(target_directory, item_name)
        # 获取文件或目录的创建时间
        item_creation_time = os.path.getctime(item_path)
        
        # 删除创建时间超过一天的文件或目录
        if item_creation_time < one_day_ago:
            try:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    print(f"已删除文件: {item_path}")
                elif os.path.isdir(item_path):
                    # 删除目录及其所有内容
                    shutil.rmtree(item_path)
                    print(f"已删除目录: {item_path}")
            except Exception as e:
                print(f"删除 {item_path} 时出错: {e}")

