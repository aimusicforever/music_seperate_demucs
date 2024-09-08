from flask import Flask
app =Flask(__name__)
@app.route("/")
def hello():
    return "hello nginx"

    
if __name__ =="__main__":
    # app.run(port=50001)
    
    import os
    file = "/Users/simonws/project/music_seperate_demucs/separated/1723857385_-_/other.mp3"

    # 获取前缀（文件名称）
    
    # print(f"{len(os.path.splitext(file))}")
    # print(f"{os.path.splitext(file)[0]}")
    # print(f"{os.path.splitext(file)[-1]}")
    # print(f"{os.path.splitext(file)[-1][1:]}")
    
    baseName = os.path.basename(file)
    name = baseName.split(".")[1]
    print(f"{baseName} ==== {name}")
    
    
    
    # filepath2="D:/data/outputs/abc.jpg.def.jpg"
    # c=os.path.splitext(filepath2)[0]#不含后缀带路径的文件名
    # print(c)
    # d=os.path.splitext(filepath2)[-1]#后缀
    # print(d)
    # e= os.path.basename(filepath2)#带后缀的文件名
    # print(e)
    # f= e.split('.')[0]#不带后缀的文件名,对于filepath2这种情况不适合，从第一个点开始后面的都会被去掉
    # print(f)
    # assert os.path.splitext(file)[0] == "Hello"

    # # 获取后缀（文件类型）
    # assert os.path.splitext(file)[-1] == ".py"
    # assert os.path.splitext(file)[-1][1:] == "py"