from concurrent.futures import ThreadPoolExecutor
import threading
# from werkzeug.utils import secure_filename
from flask import jsonify, make_response, redirect, request, send_file, send_from_directory
import os
from flask import Flask
import requests
import zipfile
import json
import base64
import demucs.api
import shutil
import time
from tools import file_util
from tools import time_util
import concurrent.futures

#start cmd
#uwsgi --ini start.ini
# conda install uwsgi -c conda-forge  


# 状态编码 
# （初始状态： 00，
# 开始上传（上传中）： 10，
# 上传完成： 20，
# 开始处理（处理中）： 30，
# 处理完成： 40 ，
# 开始下载（下载中）： 50 ，
# 下载完成： 60）
STATUS_FINISH_INIT = 0
STATUS_START_UPLOAD = 10
STATUS_FINISH_UPLOAD = 20
STATUS_START_PROCESS = 30
STATUS_FINISH_PROCESS = 40
STATUS_START_DOWNLOAD = 50
STATUS_FINISH_DOWNLOAD = 60

EVNET_SEPARATE = "separate"
EVNET_LYRIC = "lyric"
EVNET_TRANSFER = "transfer"
TokenKey = "XX-Token"
DeviceTypeKey = "XX-Device-Type"
TaskKey = "key"


app = Flask(__name__)

ALLOWED_EXTENSIONS = {"mp3", "wav", "flac" , "aac"}
manager_service_address = "https://music.openai80.com/api/music/music/status"

    # Use another model and segment:
    # htdemucs_6s
    # mdx_extra
separator = demucs.api.Separator(model="htdemucs_6s")

@app.route('/fetch_lyrcs', methods=['POST'])
def fetch_lyrcs():
    print("=======fetch_lyrc======")
    lyrcs_url = "http://127.0.0.1:50000/fetch_file_lyrcs"
    
    
    file = requests.files['file']
    
    if file is None:
        return jsonify({"status": "fail", "message":"No file part"})
    if file.filename == '':
        return jsonify({"status": "fail", "message":"No file selected"})
    
    secureName = f"{int(time.time())}_{(str(file.filename))}"
    print("secureName:", secureName)

    
    saveDir = os.path.join(os.getcwd(), 'separated/lyrcs')
    print("saveDir", saveDir)
    file_util.checkDir(saveDir)
    
    savePath = os.path.join(saveDir, secureName)
    
    print("savePath:", savePath)
    file.save(savePath)
    
    params = {
    'path':savePath,
    }
    
    res = requests.get(url=lyrcs_url,params=params)
    
    res = res.text.encode('utf-8').decode('unicode_escape')
    return res

@app.route('/', methods=['GET', 'POST'])
def index():
    print("=============")
    return "Hello World!"

@app.route('/download', methods=['GET'])
def download():
    path = request.args.get("path")
    
    if path is None:
        return jsonify({"status": "fail", "message":"path is none or null"})
    
    file_path = os.path.join('./separated/', path)
    print("======file_path=======", file_path)
    return send_file(file_path)


@app.route('/separate', methods=['POST'])
def separate():
    
    print("seperate start time ==", time_util.get_current_time())
    
    file = request.files['file']
    taskKey = request.form.get(TaskKey)
    
    loginToken =  request.headers[TokenKey]
    device_type =  request.headers[DeviceTypeKey]
    
    print(f"{taskKey} {loginToken}  {device_type}")
        
    
    if file is None:
        return jsonify({"status": "fail", "message":"No file part"})
    if file.filename == '':
        return jsonify({"status": "fail", "message":"No file selected"})
    
    fileNameSplit = os.path.splitext(file.filename)
    
    fileExtension = fileNameSplit[-1][1:]
    if fileExtension not in ALLOWED_EXTENSIONS:
        return jsonify({'error': 'Invalid file type'})
    
    secureName = (str(file.filename))
    print("secureName:", secureName)
    
    file_util.checkDir('./separated/upload')
    savePath = os.path.join('./separated/upload', secureName)
    file.save(savePath)
    
    uploadResult = {
        "code": 1,
        "msg":"upload success",
        "data":"",
    }
    
    params = {
            'key':taskKey,
            'status':STATUS_FINISH_UPLOAD,
            'event':EVNET_SEPARATE,
            'data':""
        }
    
    headers = {
        "XX-Token": loginToken,
        "XX-Device-Type": device_type,
    }
    notifyStatus(params, headers)
    
    workNum = 1
    ThreadPoolExecutor(max_workers=workNum).submit(separate_file, savePath, taskKey, loginToken, device_type)
    
    return uploadResult
    

def separate_file(savePath, taskKey, loginToken, device_type):
    # separator.samplerate = 11100
    
    origin, separated = separator.separate_audio_file(savePath)
    
    secureName = os.path.basename(savePath)
    fileExtension = secureName.split(".")[1]
    
    print("separator.samplerate===", separator.samplerate)
    
    subDir = f"{int(time.time())}"
    outDir = os.path.join('./separated/', subDir)
    file_util.createNewDir(outDir)
    # print("outDir:", outDir)
        
    data = {}
    for sourceName in separated.keys():
        path = os.path.join(outDir, f"{sourceName}.{fileExtension}")
        print("sepeate path", path)
        demucs.api.save_audio(separated[sourceName], path, samplerate=separator.samplerate)
        data[sourceName] = subDir + "/" + f"{sourceName}.{fileExtension}"
    
    os.remove(savePath)
    
    
    dataString = json.dumps(data)
    print("seperate finish time ==", time_util.get_current_time())
    
    print(f"data === {data} === {dataString}")
    params = {
            'key':taskKey,
            'status':STATUS_FINISH_PROCESS,
            'event':EVNET_SEPARATE,
            'data':dataString
        }
    
    headers = {
            "XX-Token": loginToken,
            "XX-Device-Type": device_type,
        }
    resp = notifyStatus(params, headers)
    print(f"sepearate notify finish {resp.text}")
    

def notifyStatus(params, headers):
    
    res = requests.get(url=manager_service_address,params=params, headers=headers)
    print(f"manager response ===={res.text}")
    
    
    
    

# app.run(port=40001, host='0.0.0.0')

def task():
    print('Task executed start')
    time.sleep(5)
    
    print('Task executed end')
    return "66666"

if __name__ == '__main__':

    app.run(port=40000, host='0.0.0.0')
    # print('before')
    # ThreadPoolExecutor(1).submit(task)
    # concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    #     future = executor.submit(task)
    #     print(f"future== {future}")
    
    # tt = threading.Thread(target=task)
    # tt.start()
    # print('end')

    
