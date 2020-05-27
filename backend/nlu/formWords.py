# @Language: python3
# @File  : formWords.py
# @Author: LinXiaofei
# @Date  : 2020-04-24
"""

"""
import sys
import os
import jieba


project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)


class formWords(object):

    def __init__(self):

        self.stopword = ["为什么", "什么", "如何", "谁", "多少", "几", "怎么着", "怎么样", "怎么", "怎样", "怎的", "怎",
                         "哪里", "哪儿", "哪", "吗", "呢", "吧", "啊", "么"]
        self.symbol = [",", "，", ".", "。", "!", "！", "@", "#", "$",
                       "%", "^", "&", "*", "(", "（", ")", "）", "{", "「", "}", "」", "[", "]", "【", "】", "、", "\\", "|",
                       ";",
                       "；", "<", ">", "?", "？", "`", "~", "·", "～", "：", ":", "*"]

        self.synonymy = {'中国': ['我国'], '我国': ['中国']}


    def preProcessWords(self, words):
        """
        句子预处理
        1.去掉符号和停用词
        2.去掉"的"，如果有目的，则复原
        :param words: 句子
        :return: 处理后的句子
        """

        for stop in self.stopword:
            while(stop in words):
                words = words.replace(stop,'')
        for sym in self.symbol:
            while(sym in words):
                words = words.replace(sym,'')

        flag = False
        if "目的" in words:
            flag = True
        words = self.deletDE(words)

        if flag:
            words = words.replace("目","目的")

        return words

    def deletDE(self,words):
        """
        去掉句子的"的"
        :param words: 句子
        :return: 去掉"的"的句子
        """

        while('的' in words):
            words = words.replace('的','')
        return words


if __name__ == '__main__':
    pass

