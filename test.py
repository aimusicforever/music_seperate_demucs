# app.py
from datetime import datetime
from flask import Flask

# app = Flask(__name__="__main__")

# @app.route("/")
# def index():
    
#     print("=======")
#     return 'hello, world!'



def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print("time==", get_current_time())
