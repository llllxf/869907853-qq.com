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

        ask_words,cut_words,entity_array,coo,coo_index,property_array,keywords_array,task_type_array,words_type,ask_ent,pattern = self.nlu_util.dealWithAsking(words)



        for i in range(3):
            key_ent, ans_type, ans = self.dealNLU(ask_words, task_type_array[i], entity_array[i], property_array[i], keywords_array[i])

            if ans != None and ans != "":
                ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
                return ans_str,task_type_array[i],pattern[i]

        for i in range(3):
            if task_type_array[i] != 'task_singal_entity' and task_type_array[i] != None:

                key_ent, ans_type, ans = self.dealNLU(ask_words, "task_singal_entity", entity_array[i], property_array[i], keywords_array[i])
            if ans != None and ans != "":
                ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
                return ans_str,"task_singal_entity",pattern[i]

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
        task_type = "task_reverse"
        key_ent, ans_type, ans = self.dealNLU(ask_words, task_type, entity_array[0], property_array[0], keywords_array[0])
        if ans != None and ans != "":
                ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
                return ans_str,"task_reverse",pattern[0]

        return "",None,pattern[0]

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
                return entity[0], "ans_items", ans

        if task_type == 'task_normal_rel':
            ans = self.graph_util.taskNormalRel(entity,property)
            if ans != None:
                return entity[0], "ans_items", ans

        if task_type == 'task_son_kw_match':
            ans = self.graph_util.taskSonKeyWord(entity, property,keywords)
            if ans != None:
                return keywords[0], "ans_list", ans
            else:
                return keywords[0],None,None

        if task_type == 'task_son_match':
            ans = self.graph_util.taskSonMatch(keywords,entity,property)
            if ans != None:
                return entity[0], "ans_triple", ans
        if task_type == 'task_pro_match':
            ans = self.graph_util.taskProMatch(keywords,entity,property)
            if ans != None:
                return entity[0], "ans_triple", ans

        if task_type == 'task_singal_entity':
            ans = self.graph_util.taskProName(words,entity)
            if ans != None:
                return entity[0], "ans_triple", ans

        if task_type == 'task_reverse':
            ans = self.graph_util.taskReverse(words,entity)
            if ans != None:
                return entity[0], "ans_triple", ans
        if task_type == 'task_limit_sub':
            ans = self.graph_util.taskLimitSub(keywords,entity)
            if ans != None:
                return entity[0], "ans_list", ans

        if len(entity)==0 or entity == None:

            return None,None,None

        return entity[0], None, None
    def doNLG(self,entity,ans_type,ans):

        ans_str = self.ans_util.getAns(entity, ans_type, ans)
        return ans_str



if __name__ == '__main__':
    a = DialogManagement()

    """
    fok = open("single.txt", "a")
    fok2 = open("ok.txt", "a")
    fno = open("noans.txt", "a")

    questions = read_file(project_path+"/data/question2.txt")

    for q in questions:

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





