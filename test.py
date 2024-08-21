# app.py
from datetime import datetime
from flask import Flask
import requests


def launch():
    local_url = "http://127.0.0.1:40000/seperate"
    file = {'file': open("./ad_jianchidaodi.mp3", 'rb')}

    res = requests.post(url=local_url,
                        files=file,
                        data={"filename": "ad_jianchidaodi.mp3"},
                        timeout=100000)


def start():
    local_url = "http://127.0.0.1:40000"

    res = requests.get(url=local_url)
    
    print("res:", res.text)

if __name__ == '__main__':
    start()
    

# @app.route("/")
# def index():
    
#     print("=======")
#     return 'hello, world!'




