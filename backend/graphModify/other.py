# @Language: python3
# @File  : other.py.py
# @Author: LinXiaofei
# @Date  : 2020-05-27
"""

"""
import sys
import os
import numpy as np
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
# print(project_path)
sys.path.append(project_path)

from data.data_process import read_file

def getProEnt():
    ent = read_file(project_path+"/data/allentity.csv")
    pro = read_file(project_path + "/data/cleanpro.csv")

    for e in ent:
        if e in pro:
            print(e)

    print('湖泊')
    print('国家')
    print('海拔')

if __name__ == '__main__':
    getProEnt()
