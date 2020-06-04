# @Language: python3
# @File  : pediaToGeo.py
# @Author: LinXiaofei
# @Date  : 2020-06-04
"""
从百科图谱到k12地理图谱
"""

import sys
import os
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
# print(project_path)
sys.path.append(project_path)
from data.data_process import read_file

from nlu.LTPUtil import LTPUtil
from graphSearch.graphSearch import graphSearch


class pediaToGeo(object):
    def __init__(self):
        """
        图谱工具
        """
        self.search_util = graphSearch()
        """
        转换工具
        """
        """
        河流同一属性：位于（地理位置），流域面积，长度，主要支流，发源地，流经（国家，地区），地位，
        """
        self.river_rel = {'位于':['地理位置','所属地区','所属国家','所属城市',]}
        self.river_pro = {'流域面积':['流域面积','河流面积','面积','占地面积'],'主要支流':['主要支流'],'发源地':['发源地','正源','源头位置','源头'],
                          '流经':['流经国家','流经地区','流经','干流长度'],'长度':['长度','河长','全长'],
                          '地位':['地位'],'别名':['别名','别称'],
                          '流向':['流向']}

    def getInfForComplete(self, type):
        entity_list = self.search_util.getEntityByType(type)
        #entity_list = read_file(project_path + "/data/hl1.txt")
        f = open(project_path + "/data2/inf/" + type + "2.csv", "w")
        count = 0
        for ent in entity_list:
            ent_arr = []
            count = count+1
            inf_dict = self.search_util.completionGraph(ent, type)

            if inf_dict is None:
                continue
            for key, value in inf_dict.items():
                for r_key,r_value in self.river_pro.items():
                    if key in r_value:
                        if r_key not in ent_arr:
                            ent_arr.append(r_key)
                            f.writelines(ent + " " + r_key + " " + value + "\n\n")


if __name__ == '__main__':
    p = pediaToGeo()
    p.getInfForComplete('河流')




