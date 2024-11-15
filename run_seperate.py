import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests
import schedule
import torch as th
from flask import Flask
from flask import jsonify, request, send_file

import demucs.api
import demucs.separate
from tools import file_util
from tools import time_util

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
ModelKey = "model"
TwoStemsKey = "two_stems"


workNum = 10
threadPool = ThreadPoolExecutor(max_workers=workNum)


app = Flask(__name__)

ALLOWED_EXTENSIONS = {"mp3", "wav", "flac" , "aac"}

SEPARATE_SUB_DIR = "separated"
SEPARATE_RESULT_DIR = "separated/result"
LYRIC_SUB_DIR = "separated/lyrcs"

manager_service_host = "https://music.openai80.com"
update_status_addr = "/api/music/music/status"
manager_service_address = manager_service_host + update_status_addr
local_lyrics_addr = "http://127.0.0.1:50000/fetch_file_lyrics"

    # Use another model and segment:
    # htdemucs
    # htdemucs_ft
    # htdemucs_6s
    # mdx_extra
    # 

MODEL_4 = "htdemucs"
MODEL_6 = "htdemucs_6s"
    

separator = demucs.api.Separator(model="htdemucs_6s")

@app.route('/', methods=['GET', 'POST'])
def index():
    print("=============")
    return "Hello World!"

@app.route('/fetch_lyrics', methods=['POST'])
def fetch_lyrics():
    print("=======fetch_lyrics======")
    
    
    file = request.files['file']
    taskKey = request.form.get(TaskKey)
    
    loginToken =  request.headers[TokenKey]
    device_type =  request.headers[DeviceTypeKey]
    
    if file is None:
        return jsonify({"status": "fail", "message":"No file part"})
    if file.filename == '':
        return jsonify({"status": "fail", "message":"No file selected"})
    
    secureName = f"{int(time.time())}_{(str(file.filename))}"
    print("secureName:", secureName)

    
    saveDir = os.path.join(LYRIC_SUB_DIR, f"{int(time.time())}_{threading.current_thread().ident}")
    fullDir = os.path.join(os.getcwd(), saveDir)
    file_util.checkDir(fullDir)
    
    savePath = os.path.join(fullDir, secureName)
    
    print("savePath:", savePath)
    file.save(savePath)
    
    params = {
            'key':taskKey,
            'status':STATUS_START_PROCESS,
            'event':EVNET_LYRIC,
            'data':""
        }
    
    headers = {
            TokenKey: loginToken,
            DeviceTypeKey: device_type,
        }
    notifyStatus(params, headers)
    
    threadPool.submit(fetch_lyrics_file, saveDir,secureName, taskKey, loginToken, device_type)
    uploadResult = {
        "code": 1,
        "msg":"upload success",
        "data":"",
    }
    # class Resp<T>(var code: Int = 0, var msg: String = "", var data: T? = null)
    
    return uploadResult
    

def fetch_lyrics_file(saveDir, secureName, taskKey, loginToken, device_type):
    
    
    params = {
        'path':os.path.join(os.getcwd(), saveDir, secureName)
    }
    
    res = requests.get(url=local_lyrics_addr,params=params)
    res = res.text.encode('utf-8').decode('unicode_escape')
    
    name = "lyric.txt"
    lyricPath = os.path.join(os.getcwd(), saveDir, name)
    file_util.saveToFile(res, lyricPath)
    print(f"lyricfile: {lyricPath}")
    

    data = {
        "lyricsPath":os.path.join(saveDir, name)
    }
    
    params = {
            'key':taskKey,
            'status':STATUS_FINISH_PROCESS,
            'event':EVNET_LYRIC,
            'data':json.dumps(data)
        }
    
    
    
    print("lyrcs result:", json.dumps(data))
    
    print("loginToken:", loginToken, "key:", taskKey)
    
    headers = {
            TokenKey: loginToken,
            DeviceTypeKey: device_type,
        }
    notifyStatus(params, headers)


@app.route('/download', methods=['GET'])
def download():
    path = request.args.get("path")
    
    if path is None:
        return jsonify({"status": "fail", "message":"path is none or null"})
    
    file_path = os.path.join(os.getcwd(), path)
    print("======download  file_path=======", file_path)
    return send_file(file_path)


@app.route('/separate', methods=['POST'])
def separate():
    
    print("seperate start time ==", time_util.get_current_time())
    
    file = request.files['file']
    
    isTest = False
        
    if isTest:
        taskKey = "test"
        model = MODEL_6
        twoItem = ""
        loginToken = "666"
        device_type = "android"
    else:
        taskKey = request.form.get(TaskKey)
        model = request.form.get(ModelKey, MODEL_6)
        twoItem = request.form.get(TwoStemsKey, "")
        loginToken =  request.headers[TokenKey]
        device_type =  request.headers[DeviceTypeKey]
    
    print(f"taskKey:{taskKey} loginToken:{loginToken}  device_type:{device_type} model:{model} twoItem:{twoItem}")
    
    uploadResult = {
        "code": 1,
        "msg":"upload success",
        "data":"",
    }
    
    if file is None:
        uploadResult["code"] = 0
        uploadResult["msg"] = "No file part"
        return uploadResult
    if file.filename == '':
        uploadResult["code"] = 0
        uploadResult["msg"] = "No file selected"
        return uploadResult
    
    fileNameSplit = os.path.splitext(file.filename)
    
    fileExtension = fileNameSplit[-1][1:]
    if fileExtension not in ALLOWED_EXTENSIONS:
        print("Invalid file type:", file.filename)
        uploadResult["code"] = 0
        uploadResult["msg"] = "err:Invalid file type"
        return uploadResult
    
    secureName = (str(file.filename))
    print("separate file name:", secureName)
    
    file_util.checkDir('./separated/upload')
    savePath = os.path.join('./separated/upload', secureName)
    file.save(savePath)
    

    
    params = {
            'key':taskKey,
            'status':STATUS_FINISH_UPLOAD,
            'event':EVNET_SEPARATE,
            'data':""
        }
    
    headers = {
        TokenKey: loginToken,
        DeviceTypeKey: device_type,
    }
    resp = notifyStatus(params, headers)
    print("resp ", f"{resp.text}")
    
    threadPool.submit(separate_file, savePath, taskKey, loginToken, model, twoItem, device_type)
    
    return uploadResult
    

def separate_file(originPath, taskKey, loginToken, model, twoItem, device_type):
    # separator.samplerate = 11100
    print("start separate file: " + originPath)
    
    separator = demucs.api.Separator(model)
    origin, separatedResult = separator.separate_audio_file(originPath)
    
    print("finish separate file: " + originPath)
    
    secureName = os.path.basename(originPath)
    fileExtension = secureName.split(".")[1]
    
    
    subDir = SEPARATE_RESULT_DIR + os.path.sep + f"{int(time.time())}_{threading.current_thread().ident}"
    outDir = os.path.join(os.getcwd(), subDir)
    file_util.createNewDir(outDir)
    # print("outDir:", outDir)
        
    data = {}
    
    separateInfo = {}
    if twoItem != "":
        separateInfo[twoItem] = separatedResult.pop(twoItem)
        
        other_stem = th.zeros_like(next(iter(separatedResult.values())))
        for i in separatedResult.values():
            other_stem += i
        separateInfo["other"] = other_stem
    else:
        separateInfo = separatedResult
    
    for sourceName in separateInfo.keys():
        path = os.path.join(outDir, f"{sourceName}.{fileExtension}")
        print("sepeate path:", path)
        demucs.api.save_audio(separateInfo[sourceName], path, samplerate=separator.samplerate)
        data[sourceName] = subDir + os.path.sep + f"{sourceName}.{fileExtension}"
    
    os.remove(originPath)
    
    
    dataString = json.dumps(data)
    print("seperate finish time ==", time_util.get_current_time() )
    print("separate data:", dataString)
    
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
    return res
    
    
    
    

# app.run(port=40001, host='0.0.0.0')

def task():
    print('Task executed start')
    time.sleep(5)
    
    print('Task executed end')
    return "66666"

def scheduleDeleteOldFileTask():
    # print("scheduleDeleteOldFileTask start")
    resultPath = os.path.join(os.getcwd(), SEPARATE_RESULT_DIR)
    schedule.every().day.at("00:00").do(file_util.delete_old_items, target_directory= resultPath)
    # schedule.every().minute.do(file_util.delete_old_items, target_directory= resulyPath)

    # 持续运行任务
    while True:
        schedule.run_pending()
        time.sleep(3600 * 24)  # 每24小时检查一次



threadPool.submit(scheduleDeleteOldFileTask)

if __name__ == '__main__':
    
    # 设置每天执行一次任务
    # scheduleDeleteOldFileTask()

    
    # modelName = "htdemucs"
    # stem = "drums"
    print(f"fullParh")
    # app.run(port=40000, host='0.0.0.0')
    
    # demucs.separate.main(["--mp3", "--two-stems", stem, "-n", modelName, filePath])