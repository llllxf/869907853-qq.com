# @Language: python3
# @File  : dialogManagement.py
# @Author: LinXiaofei
# @Date  : 2020-03-18
import sys
import os
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)


def read_file(filename):
    with open(filename,"r") as rf:
        array = []
        lines = rf.readlines()
        for line in lines:
            line = line.strip('\n')
            array.append(line)

    rf.close()
    return array

def clean_entity():
    sw = open("entity.csv", "w")
    lw = open("bake_entity.csv", "w")
    with open("allentity.csv","r") as rf:
        lines = rf.readlines()
        for line in lines:
            line = line.strip('\n')
            if '和' in line:
                continue
            elif len(line)>5:
                lw.writelines(line+"\n")
            else:
                sw.writelines(line+"\n")


def clean_repeat():
    classarray = read_file("allclass.csv")
    entityarray = read_file("entity.csv")
    findarray = read_file("findthing.txt")
    findarray = list(set(findarray))

    cw = open("cleanclass.txt","w")
    fw = open("cleanfind.txt","w")

    for f in findarray:
        f = f.strip("\n")
        fw.writelines(f+"\n")
    for cla in classarray:
        if cla in entityarray:
            continue
        cla = cla.strip("\n")
        cw.writelines(cla+"\n")

