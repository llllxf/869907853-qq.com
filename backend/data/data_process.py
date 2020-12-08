# @Language: python3
# @File  : dialogManagement.py
# @Author: LinXiaofei
# @Date  : 2020-03-18
import sys
import os
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)
"""
import xlrd


def read_xlsx(filename):

    info_file = xlrd.open_workbook(filename)
    info_sheet = info_file.sheets()[0]
    row_count = info_sheet.nrows
    f = open(project_path+"/data/operate/addweidu.txt","a")


    for r in range(1,row_count):
        ent = info_sheet.cell(r,0).value
        jingdu = info_sheet.cell(r,1).value
        if jingdu == "":
            jingdu = "N/A"

        weidu = info_sheet.cell(r,2).value
        if weidu == "":
            weidu = "N/A"
        f.writelines(ent+",经度,"+jingdu+"\n")
        f.writelines(ent + ",纬度," + weidu + "\n")
"""


def removeComma(filename):
    context = read_file(project_path+"/data2/inf/"+filename+".csv")
    f = open(project_path+"/data3/complete/"+filename+".csv","w")
    for con in context:
        while("," in con):
            con = con.replace(",","")
        """
        con_arr = con.split(" ")
        if "省" not in con_arr[0]:
            con_arr[0] += "省"
        """
        f.writelines(con+"\n\n")
        #f.writelines(" ".join(con_arr)+"\n")
    f.close()

def modifycity():
    country_list = read_file(project_path+"/data/国家.csv")
    province_list = read_file(project_path+"/data/province.csv")
    city_rel = read_file(project_path+"/data2/inf/城市_rel.csv")
    f = open(project_path+"/data3/complete/城市_rel.csv","w")

    for rel in city_rel:
        rel_arr = rel.split(" ")
        for country in country_list:
            if country in rel_arr[2]:
                f.writelines(rel_arr[0]+" "+rel_arr[1]+" "+country+"\n")
                break
        for province in province_list:
            if province in rel_arr[2]:
                if '省' not in province and province+"省" in province_list:
                    province = province+"省"
                f.writelines(rel_arr[0]+" "+rel_arr[1]+" "+province+"\n")
                break
    f.close()
    quchong = open(project_path+"/data3/complete/城市_rel.csv","r")
    quchong = list(set(quchong))
    f = open(project_path + "/data3/complete/城市_rel.csv", "w")
    for q in quchong:
        f.writelines(q)
        f.writelines("\n")
    f.close()

def modifyprovince():
    country_list = read_file(project_path+"/data/国家.csv")

    city_rel = read_file(project_path+"/data2/inf/省_rel.csv")
    f = open(project_path+"/data3/complete/省_rel.csv","w")

    for rel in city_rel:
        rel_arr = rel.split(" ")
        for country in country_list:
            if country in rel_arr[2]:
                if country == '中国':
                    f.writelines(rel_arr[0]+" "+rel_arr[1]+" 我国\n")
                else:
                    f.writelines(rel_arr[0] + " " + rel_arr[1] + " " + country + "\n")

                break
    f.close()
    quchong = open(project_path+"/data3/complete/省_rel.csv","r")
    quchong = list(set(quchong))
    f = open(project_path + "/data3/complete/省_rel.csv", "w")
    for q in quchong:
        f.writelines(q)
        f.writelines("\n")
    f.close()

def modifycountry():

    city_list = read_file(project_path+"/data/city.csv")
    country_rel = read_file(project_path+"/data2/inf/国家_rel.csv")
    f = open(project_path+"/data3/complete/国家_rel.csv","w")

    for rel in country_rel:
        rel_arr = rel.split(" ")
        if rel_arr[2] in city_list:
            f.writelines(rel_arr[0]+" "+rel_arr[1]+" "+rel_arr[2]+"\n")


    f.close()
    quchong = open(project_path+"/data3/complete/国家_rel.csv","r")
    quchong = list(set(quchong))
    f = open(project_path + "/data3/complete/国家_rel.csv", "w")
    for q in quchong:
        f.writelines(q)
        f.writelines("\n")
    f.close()

def modifynature(filename):
    country_list = read_file(project_path + "/data/国家.csv")
    province_list = read_file(project_path + "/data/province.csv")
    city_list = read_file(project_path + "/data/city.csv")
    state_list = read_file(project_path + "/data/state.csv")

    nature_rel = read_file(project_path + "/data2/inf/"+filename+".csv")

    f = open(project_path + "/data3/complete/"+filename+".csv", "w")

    for rel in nature_rel:
        rel_arr = rel.split(" ")
        print(rel_arr)
        for country in country_list:
            if country in rel_arr[2]:
                f.writelines(rel_arr[0] + " " + rel_arr[1] + " " + country + "\n")
                break
        for province in province_list:
            if province in rel_arr[2]:
                if '省' not in province and province + "省" in province_list:
                    province = province + "省"
                f.writelines(rel_arr[0] + " " + rel_arr[1] + " " + province + "\n")
                break
        for city in city_list:
            if city in rel_arr[2]:

                f.writelines(rel_arr[0] + " " + rel_arr[1] + " " + city + "\n")
                break
        for state in state_list:
            if state in rel_arr[2]:
                f.writelines(rel_arr[0] + " " + rel_arr[1] + " " + state + "\n")
                break
    f.close()
    quchong = open(project_path + "/data3/complete/"+filename+".csv", "r")
    quchong = list(set(quchong))
    f = open(project_path + "/data3/complete/"+filename+".csv", "w")
    for q in quchong:
        f.writelines(q)
        f.writelines("\n")
    f.close()


def read_file(filename):

    with open(filename,"r") as rf:
        array = []
        lines = rf.readlines()
        for line in lines:
            line = line.strip('\n')
            if line == "":
                continue
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

if __name__ == '__main__':
    #read_xlsx(project_path+'/data2/inf/经纬度.xlsx')
    #removeComma("省_pro")
    #modifyprovince()
    modifynature('海洋_rel')
