from concurrent.futures import thread
from werkzeug.utils import secure_filename
from flask import jsonify, make_response, send_file, send_from_directory
import os
from flask import Flask, request
import zipfile
import json
import base64
import demucs.api
import shutil
import time
import requests
from tools import file_util
from tools import time_util

#start cmd
#uwsgi --ini start.ini
# conda install uwsgi -c conda-forge  

app = Flask(__name__)

ALLOWED_EXTENSIONS = {"mp3", "wav", "flac" , "aac"}

    # Use another model and segment:
    # htdemucs_6s
    # mdx_extra
separator = demucs.api.Separator(model="htdemucs_6s")

@app.route('/', methods=['GET', 'POST'])
def index():
    print("=============")
    return "Hello World!"


@app.route('/seperate', methods=['POST'])
def seperate():
    
    
    print("start time ==", time_util.get_current_time())
    file = request.files['file']
    
    if file is None:
        return jsonify({'error': 'No file part'})
    if file.filename == '':
        return jsonify({'error': 'No file selected'})
    
    fileNameSplit = os.path.splitext(file.filename)
    
    fileExtension = fileNameSplit[-1][1:]
    if fileExtension not in ALLOWED_EXTENSIONS:
        return jsonify({'error': 'Invalid file type'})
    
    secureName = secure_filename(str(file.filename))
    print("secureName:", secureName)
    
    file_util.checkDir('./separated/upload')
    
    savePath = os.path.join('./separated/upload', secureName)
    
    file.save(savePath)

    # separator.samplerate = 11100
    origin, separated = separator.separate_audio_file(savePath)
    
    print("separator.samplerate===", separator.samplerate)
    
    # Remember to create the destination folder before calling `save_audio`
    # Or you are likely to recieve `FileNotFoundError`
    
    outDir = os.path.join('./separated/', f"{int(time.time())}_{os.path.splitext(secureName)[0]}")
    file_util.createNewDir(outDir)
    # print("outDir:", outDir)
    fileList = []
        
    
    
    for sourceName in separated.keys():
        path = os.path.join(outDir, f"{sourceName}.{fileExtension}")
        print("sepeate path", path)
        demucs.api.save_audio(separated[sourceName], path, samplerate=separator.samplerate)
        fileList.append(path)
            
    zipPath = os.path.join(outDir, "result.zip")
    file2zip(zipPath, fileList)
    
    print("zipPath", zipPath)
    
    os.remove(savePath)
    
    print("finish time ==", time_util.get_current_time())
    try:
        return send_file(zipPath)
    except Exception as e:
        return jsonify({"code": "异常", "message": "{}".format(e)})


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

# app.run(port=40001, host='0.0.0.0')

if __name__ == '__main__':
    # 加上`host='0.0.0.0'`，即可以让你的服务监听所有公网ip，而不是只有本地请求才能访问
    # print("run=========")
    app.run(port=40000, host='0.0.0.0')
    # zipFile()
    # print(demucs.api.list_models())
    
