# @Language: python3
# @File  : processNLU.py
# @Author: LinXiaofei
# @Date  : 2020-04-27
"""
nlu总控
"""

import sys
import os
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)



from nlu.matchWords import matchWords
from nlu.analysisPattern import PatternMatch
from nlu.formWords import formWords
import numpy as np

class processNLU(object):
    def __init__(self):
        self.words_util = matchWords()
        self.pattern_util = PatternMatch()
        self.form_util = formWords()
        self.task_sort = ['task_son_kw_match','task_normal_pro','task_normal_rel','task_son_match','task_limit_sub','task_singal_entity']

    def dealWithAsking(self,words):
        """
        1.检查句子有没有疑问代词
        2.
        :param words:
        :return:
        """
        ask_words, ask_ent, words_type = self.words_util.formAsking(words)
        print("调整问题为: ", ask_words)
        print("询问实体", ask_ent)

        cut_words = self.words_util.cutWords(ask_words)
        pattern,pattern_index,coo,coo_index,arcs_dict,reverse_arcs_dict,postags,hed_index = self.words_util.getWordsPattern(cut_words)



        entity_array_temp = []
        property_array_temp = []
        keywords_array_temp = []
        task_type_array_temp = []
        task_num = []
        for p in pattern:
            entity, property, keywords, task_type = self.pattern_util.matchPattern(p, pattern_index, cut_words)
            """
            if task_type == None:

                cut_words = self.words_util.aliasChange(cut_words)
                print("替换后的问句: ",cut_words)
                pattern, pattern_index, coo, coo_index, arcs_dict, reverse_arcs_dict, postags, hed_index = self.words_util.getWordsPattern(
                cut_words)
                entity, property, keywords, task_type = self.pattern_util.matchPattern(pattern, pattern_index, cut_words)
            """
            if task_type == None:
                entity, property, keywords, task_type = self.pattern_util.matchSingalEntity(p, pattern_index,
                                                                                            cut_words)

            print("========================================================")

            print("关键实体: ", entity)
            print("关键属性: ", property)
            print("并列实体: ", coo)
            print("属性限制: ", keywords)
            print("任务类型: ", task_type)
            entity_array_temp.append(entity)
            property_array_temp.append(property)
            if len(keywords)>0:
                keywords_array_temp.append(keywords)
            else:
                keywords_array_temp.append(None)
            task_type_array_temp.append(task_type)
            if task_type in self.task_sort:
                task_num.append(self.task_sort.index(task_type))
            else:
                task_num.append(6)

        sort_index = np.argsort(task_num)

        entity_array = np.array(entity_array_temp)[sort_index]
        property_array = np.array(property_array_temp)[sort_index]
        keywords_array = np.array(keywords_array_temp)[sort_index]
        task_type_array = np.array(task_type_array_temp)[sort_index]

        return ask_words,cut_words,entity_array,coo,coo_index,property_array,keywords_array,task_type_array,words_type,ask_ent,pattern



if __name__ == '__main__':
    a = processNLU()
    while(1):
        s = input("user: ")
        if s == "":
            continue
        a.dealWithAsking(s)
