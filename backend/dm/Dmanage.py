# @Language: python3
# @File  : Dmanage.py
# @Author: LinXiaofei
# @Date  : 2020-05-01
"""

"""
import sys
import os
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
# print(project_path)
sys.path.append(project_path)

from nlu.processNLU import processNLU
from nlg.generateAns import generateAns



from graphSearch.calculateBussiness import calculateBussiness
from graphSearch.compareBussiness import compareBussiness
from graphSearch.normalBussiness import normalBussiness


from data.data_process import read_file
import requests, json

"""
问答引擎
"""

class DialogManagement(object):
    def __init__(self):
        self.nlu_util = processNLU()

        self.nlg_util = generateAns()

        self.normal_bussiness = normalBussiness()
        self.compare_bussiness = compareBussiness()
        self.calculate_bussiness = calculateBussiness()





    def doNLU(self,words):

        ans_str = ""
        ans_dict = self.nlu_util.differentWordsType(words)

        words_type = ans_dict['words_type']

        if words_type == 'task_compare':

            entity_array = ans_dict['entity']
            property = ans_dict['property']
            task_type = ans_dict['task_type']


            compare_dict = self.normal_bussiness.taskNormalPro(entity_array, [property])

            #compare_dict = self.dealCompare(entity_array,[property])

            ans_str += self.doNLG(None, "ans_items", compare_dict)
            if 'less' in task_type:
                ans_str += self.nlg_util.compareLessNLG(task_type, compare_dict)
            else:
                ans_str += self.nlg_util.compareMoreNLG(task_type, compare_dict)
            return ans_str,words_type


        if 'task_calculate' in words_type:

            if ans_dict['task_type'] == 'task_calculate_ask':
                return [ans_dict['ask']]
            if 'most' in ans_dict['task_type']:

                ans,task_type = self.calculate_bussiness.doMostCalculate(ans_dict)
            elif 'least' in ans_dict['task_type']:
                ans, task_type = self.calculate_bussiness.doLeastCalculate(ans_dict)

                return ans,task_type
                """

                spefify = ans_dict['predicate'] + ans_dict['predicate_adj']
                if ans_dict['limit'][0] != '世界':
                    son_list = self.localtion_util.getLocationByLimit(ans_dict['ask'][0], ans_dict['limit'][0])
                else:

                    son_list = []
                    for ask in ans_dict['ask']:
                        son_list = son_list + self.graph_util.getEntityByType(ask)
                    son_list = list(set(son_list))
                if len(son_list) < 1:
                    return "对不起，暂时无法回答。\n", ans_dict['task_type']

                print("查找子类： ", son_list)

                ans = self.calculate_bussiness.matchSpecify(son_list, spefify)

                if ans != None and len(ans) > 0:
                    print("通过匹配实体的特征值得到最值信息")
                    print("===========================================")
                    return ans, ans_dict['task_type']
                else:

                    ent_list, num_list = self.calculate_bussiness.getNumCollect(son_list, ans_dict['predicate'])
                    print(num_list, "numlist")
                    if 'dir' in ans_dict['task_type']:
                        form_num_list = [getSingelDirNum(num, ans_dict['task_type']) for num in num_list]
                    else:
                        form_num_list = [getSingelCompareNum(num) for num in num_list]

                    max_index = np.argmax(np.array(form_num_list))

                    print("通过比较实体的" + ans_dict['predicate'][0] + "得到最值信息")
                    print("===========================================")

                    return ent_list[max_index], ans_dict['task_type']
            """

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
                key_ent, ans_type, ans = self.normal_bussiness.doNormal(ask_words, task_type_array[i], entity_array[i], property_array[i],
                                                      keywords_array[i])

                if ans != None and ans != "":
                    ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
                    return ans_str, task_type_array[i]

            for i in range(3):
                if task_type_array[i] != 'task_singal_entity' and task_type_array[i] != None:
                    key_ent, ans_type, ans = self.normal_bussiness.doNormal(ask_words, "task_singal_entity", entity_array[i],
                                                          property_array[i], keywords_array[i])
                if ans != None and ans != "":
                    ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
                    return ans_str, "task_singal_entity"
                """
                ans = None
                if (ans == None or ans == "") and (entity!=[] and entity != None):
                    task_type = "task_reverse"
                    key_ent, ans_type, ans = self.normal_bussiness.doNormal(ask_words, task_type, entity, property, keywords)


                    ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)

                if len(coo) > 0:
                    for c in coo:
                        key_ent, ans_type, ans = self.normal_bussiness.dealNLU(ask_words, task_type, [c], property, keywords)
                        ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
                """
            task_type = "task_reverse"
            key_ent, ans_type, ans = self.normal_bussiness.dealNLU(ask_words, task_type, entity_array[0], property_array[0],
                                                  keywords_array[0])
            if ans != None and ans != "":
                ans_str = ans_str + self.doNLG(key_ent, ans_type, ans)
                return ans_str, "task_reverse"

            return "", None

    """
    def dealCompare(self,entity,property):

        compare_dict = self.normal_bussiness.taskNormalPro(entity,property)

        return compare_dict
    """


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





