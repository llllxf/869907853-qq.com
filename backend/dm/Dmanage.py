# @Language: python3
# @File  : Dmanage.py
# @Author: LinXiaofei
# @Date  : 2020-05-01
"""

"""
import sys
import os
import numpy as np
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
# print(project_path)
sys.path.append(project_path)

from nlu.processNLU import processNLU
from graphSearch.graphSearch import graphSearch
from nlg.generateAns import generateAns
from data.data_process import read_file
import requests, json

class DialogManagement(object):
    def __init__(self):
        self.nlu_util = processNLU()
        self.graph_util = graphSearch()
        self.ans_util = generateAns()


    def doNLU(self,words):

        ans_str = ""

        ask_words,cut_words,entity,coo,coo_index,property,keywords,task_type,words_type,ask_ent,pattern = self.nlu_util.dealWithAsking(words)

        key_ent, ans_type, ans = self.dealNLU(ask_words, task_type, entity, property, keywords)
        if (ans == None or ans == "") and task_type != 'task_singal_entity' and task_type != None:
            task_type = "task_singal_entity"
            key_ent, ans_type, ans = self.dealNLU(ask_words, task_type, entity, property, keywords)
        ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
        """
        ans = None
        if (ans == None or ans == "") and (entity!=[] and entity != None):
            task_type = "task_reverse"
            key_ent, ans_type, ans = self.dealNLU(ask_words, task_type, entity, property, keywords)


            ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
        
        if len(coo) > 0:
            for c in coo:
                key_ent, ans_type, ans = self.dealNLU(ask_words, task_type, [c], property, keywords)
                ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
        """


        return ans_str,task_type,pattern
        print("========================================================")
        if words_type == 'task_normal':
            print(ans_str)

        elif words_type == 'task_whether':
            if ans_str == "":
                print("无法回答")
            elif ask_ent in ans_str:
                print("是的")
            else:
                print("不是")


    def dealNLU(self,words,task_type,entity,property,keywords):


        if task_type == 'task_normal_pro':
            #print(entity,property)
            ans = self.graph_util.taskNormalPro(entity,property)

            if ans != None:
                return entity[0], "task_normal", ans

        if task_type == 'task_normal_rel':
            ans = self.graph_util.taskNormalRel(entity,property)
            if ans != None:
                return entity[0], "task_normal", ans

        if task_type == 'task_son_kw_match':
            ans = self.graph_util.taskSonKeyWord(entity, property,keywords)
            if ans != None:
                return keywords[0], "task_son_kw", ans
            else:
                return keywords[0],None,None

        if task_type == 'task_son_match':
            ans = self.graph_util.taskSonMatch(keywords,entity,property)
            if ans != None:
                return entity[0], "task_son", ans

        if task_type == 'task_singal_entity':
            ans = self.graph_util.taskProName(words,entity)
            if ans != None:
                return entity[0], "task_singal_entity", ans

        if task_type == 'task_reverse':
            ans = self.graph_util.taskReverse(words,entity)
            if ans != None:
                return entity[0], "task_singal_entity", ans
        if entity == None or entity == []:
            return None,None,None

        return entity[0], None, None
    def doNLG(self,entity,ans_type,ans):

        ans_str = self.ans_util.getAns(entity, ans_type, ans)
        return ans_str



if __name__ == '__main__':
    a = DialogManagement()

    """
    fok = open("single2.txt", "w")
    fok2 = open("ok5.txt", "w")
    fno = open("no5.txt", "w")

    questions = read_file(project_path+"/data/question.txt")
    no = read_file(project_path + "/data/no.txt")
    for q in questions:
        if q in no:
            continue
        ans,task_type,pattern = a.doNLU(q)

        if len(ans) == 0:
            fno.writelines(q+"\n")
        elif task_type == 'task_singal_entity':
            fok.writelines(q+"\t"+pattern+"\n")
            fok.writelines(ans+"\n")
            fok.writelines("========================\n")
        else:
            fok2.writelines(q + "\t" + pattern + "\n")
            fok2.writelines(ans + "\n")
            fok2.writelines("========================\n")

    """

    while(1):
        s = input("user: ")
        if s == "":
            continue
        ans = a.doNLU(s)
        print(ans)






