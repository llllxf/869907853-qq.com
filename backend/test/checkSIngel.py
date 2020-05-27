# @Language: python3
# @File  : checkSIngel.py
# @Author: LinXiaofei
# @Date  : 2020-05-26
"""

"""
import sys
import os
import numpy as np
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
# print(project_path)
sys.path.append(project_path)

from data.data_process import read_file
def checkSingel():
    old_singel = read_file(project_path+"/dm/single.txt")
    new_singel = read_file(project_path+"/dm/single2.txt")

    for i in range(len(old_singel)):
        if old_singel[i] != new_singel[i]:
            print(old_singel[i]+"==="+new_singel[i])

if __name__ == '__main__':
    checkSingel()