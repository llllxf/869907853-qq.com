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

from nlu import matchWords

class DialogManagement(object):
    def __init__(self):
        """

        """
        self.askByType = ["有哪些","有什么","哪些"]
        self.askWether = ["是否","是不是","有没有"]
        self.nlu = matchWords()

    def doNlu(self, words):
        for type_word in self.askByType:
            if type_word in words:
                ans = self.nlu.ansEntityByType(words)
                if ans:
                    return ans
                else:
                    return "对不起，暂时无法回答\n"

        ans = self.nlu.dealWithAsking(words)
        for wether_word in self.askWether:
            if wether_word in words:
                if ans:
                    return "是\n"
                else:
                    return "否\n"
        if ans:
            return ans


        return "对不起，暂时无法回答\n"


if __name__ == '__main__':
    while (1):
        s = input()
        a = DialogManagement()
        print(a.doNlu(s))
