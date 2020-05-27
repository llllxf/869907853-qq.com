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

class processNLU(object):
    def __init__(self):
        self.words_util = matchWords()
        self.pattern_util = PatternMatch()
        self.form_util = formWords()

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
        entity,property,keywords,task_type = self.pattern_util.matchPattern(pattern,pattern_index,cut_words)
        """
        if task_type == None:

            cut_words = self.words_util.aliasChange(cut_words)
            print("替换后的问句: ",cut_words)
            pattern, pattern_index, coo, coo_index, arcs_dict, reverse_arcs_dict, postags, hed_index = self.words_util.getWordsPattern(
            cut_words)
            entity, property, keywords, task_type = self.pattern_util.matchPattern(pattern, pattern_index, cut_words)
        """
        if task_type == None:
            entity, property, keywords, task_type = self.pattern_util.matchSingalEntity(pattern,pattern_index,cut_words)


        print("========================================================")

        print("关键实体: ",entity)
        print("关键属性: ",property)
        print("并列实体: ",coo)
        print("属性限制: ", keywords)
        print("任务类型: ",task_type)

        return ask_words,cut_words,entity,coo,coo_index,property,keywords,task_type,words_type,ask_ent,pattern



if __name__ == '__main__':
    a = processNLU()
    while(1):
        s = input("user: ")
        if s == "":
            continue
        a.dealWithAsking(s)
