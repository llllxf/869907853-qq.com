# @Language: python3
# @File  : Dmanage.py
# @Author: LinXiaofei
# @Date  : 2020-05-01
"""

"""
import sys
import os
import jieba
import numpy as np
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
# print(project_path)
sys.path.append(project_path)

from nlu.processNLU import processNLU
from graphSearch.graphSearch import graphSearch4
from nlg.generateAns import generateAns
from inference import localtionInfernce
from calculateUtil import getSingelCompareNum
from data.data_process import read_file
import requests, json

"""
问答引擎
"""

class DialogManagement(object):
    def __init__(self):
        self.nlu_util = processNLU()
        self.graph_util = graphSearch()
        self.nlg_util = generateAns()
        self.localtion_util = localtionInfernce()



    def doNLU(self,words):

        ans_str = ""
        ans_dict = self.nlu_util.differentWordsType(words)

        words_type = ans_dict['words_type']

        if words_type == 'task_compare':

            entity_array = ans_dict['entity']
            property = ans_dict['property']
            task_type = ans_dict['task_type']

            compare_dict = self.dealCompare(entity_array,[property])

            ans_str += self.doNLG(None, "ans_items", compare_dict)
            ans_str += self.nlg_util.compareNLG(task_type,compare_dict)

            return ans_str,words_type


        if words_type == 'task_calculate':

            if ans_dict['task_type'] == 'task_calculate_ask':
                return [ans_dict['ask']]

            spefify = ans_dict['predicate'][0]+ans_dict['predicate_adj'][0]
            if ans_dict['limit'][0] != '世界':
                son_list = self.localtion_util.getLocationByLimit(ans_dict['ask'][0],ans_dict['limit'][0])
            else:
                son_list = self.graph_util.getEntityByType(ans_dict['ask'][0])
            if len(son_list) < 1:
                return "对不起，暂时无法回答。\n",ans_dict['task_type']

            print("查找子类： ",son_list)


            ans = self.graph_util.matchSpecify(son_list,spefify)

            if ans != None and len(ans)>0:
                print("通过匹配实体的特征值得到最值信息")
                print("===========================================")
                return ans, ans_dict['task_type']
            else:

                ent_list,num_list = self.graph_util.taskSonPro(son_list,ans_dict['predicate'])
                form_num_list = [getSingelCompareNum(num) for num in num_list]
                max_index = np.argmax(np.array(form_num_list))

                print("通过比较实体的" + ans_dict['predicate'][0] + "得到最值信息")
                print("===========================================")

                return ent_list[max_index],ans_dict['task_type']

        if words_type == 'task_normal':
            ask_words = ans_dict['ask_words']
            entity_array = ans_dict['entity_array']
            coo = ans_dict['coo']
            coo_index = ans_dict['coo_index']
            property_array = ans_dict['property_array']
            keywords_array = ans_dict['keywords_array']
            task_type_array = ans_dict['task_type_array']
            ask_ent = ans_dict['ask_ent']

            for i in range(3):
                key_ent, ans_type, ans = self.dealNLU(ask_words, task_type_array[i], entity_array[i], property_array[i],
                                                      keywords_array[i])

                if ans != None and ans != "":
                    ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
                    return ans_str, task_type_array[i]

            for i in range(3):
                if task_type_array[i] != 'task_singal_entity' and task_type_array[i] != None:
                    key_ent, ans_type, ans = self.dealNLU(ask_words, "task_singal_entity", entity_array[i],
                                                          property_array[i], keywords_array[i])
                if ans != None and ans != "":
                    ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
                    return ans_str, "task_singal_entity"
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
            key_ent, ans_type, ans = self.dealNLU(ask_words, task_type, entity_array[0], property_array[0],
                                                  keywords_array[0])
            if ans != None and ans != "":
                ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
                return ans_str, "task_reverse"

            return "", None

    def dealCompare(self,entity,property):

        compare_dict = self.graph_util.taskNormalPro(entity,property)


        return compare_dict


    def dealNLU(self,words,task_type,entity,property,keywords):


        if task_type == 'task_normal_pro':

            ans = self.graph_util.taskNormalPro(entity,property)

            if ans != None:
                return entity[0], "ans_items", ans

        if task_type == 'task_normal_rel':
            ans = self.graph_util.taskNormalRel(entity,property)
            if ans != None:
                return entity[0], "ans_items", ans

        if task_type == 'task_son_kw_match':
            ans = self.graph_util.taskSonKeyWordForRel(entity, property,keywords)
            if ans != None:
                return keywords[0], "ans_list", ans
            else:
                return keywords[0],None,None

        if task_type == 'task_son_match':
            ans = self.graph_util.taskSonMatch(keywords,entity,property)
            if ans != None:
                return entity[0], "ans_triple", ans
        """
        已经取消了
        if task_type == 'task_pro_match':
            ans = self.graph_util.taskProMatch(keywords,entity,property)
            if ans != None:
                return entity[0], "ans_triple", ans
        """

        if task_type == 'task_singal_entity':
            ans = self.graph_util.taskProName(words,entity)
            if ans != None:
                return entity[0], "ans_triple", ans

        if task_type == 'task_reverse' and len(entity)>0:
            ans = self.graph_util.taskReverse(words,entity)
            if ans != None:
                return entity[0], "ans_triple", ans
        """
        暂时取消
        if task_type == 'task_limit_sub':

            ans = self.graph_util.taskLimitSub(keywords,entity)
            if ans != None:
                return entity[0], "ans_list", ans
        """

        if len(entity)==0 or entity == None:

            return None,None,None

        return entity[0], None, None


    def doNLG(self,entity,ans_type,ans):

        ans_str = self.nlg_util.getAns(entity, ans_type, ans)
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
        print(ans[0])





