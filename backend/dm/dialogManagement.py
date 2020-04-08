# @Language: python3
# @File  : dialogManagement.py
# @Author: LinXiaofei
# @Date  : 2020-03-18
"""

"""
import sys
import os
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
# print(project_path)
sys.path.append(project_path)

from nlu import matchWordsByPattern
from nlu import PatternMatch

class DialogManagement(object):
    def __init__(self):

        self.nlu = matchWordsByPattern()
        self.pattern_match = PatternMatch()

    def answernQS(self, words):
        task = self.pattern_match.judgeSyntax(words)
        print("句式类别: ",task)
        if task == 'task_whether':
            ans = self.nlu.dealWithAsking(words)
            if ans == None:
                return "否"
            else:
                return "是"
        elif task == 'task_subset':
            ans = self.nlu.ansEntityByType(words)
            return ans
        else:
            ans = self.nlu.dealWithAsking(words)
            return ans

        return "暂时无法回答"




if __name__ == '__main__':
    while (1):
        s = input()
        a = DialogManagement()
        print(a.answernQS(s))
