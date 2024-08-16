

import os
import shutil


def  checkDir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        

def  createNewDir(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
        
    os.makedirs(output_dir)

def  deleteDir(path):
    shutil.rmtree(path)

