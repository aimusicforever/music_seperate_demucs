

import os
import shutil
import zipfile


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

