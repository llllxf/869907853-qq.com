# @Language: python3
# @File  : generateAns.py
# @Author: LinXiaofei
# @Date  : 2020-05-04
"""
答案生成
"""

import sys
import os
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)

class generateAns(object):
    def __init__(self):
        pass



    def getAns(self,entity,task_type,ans_array):
        if ans_array == None:

            if entity == None:
                ans = "对不起，暂时无法回答该方面的问题。\n"
                return ans
            ans = "对不起，暂时无法回答"+entity+"该方面的问题。\n"
            return ans
            #print("========================================================")
            #print(ans)

        if task_type == 'ans_list':

            ans = ",".join(ans_array)
            return ans
        if task_type == 'ans_triple':
            ans = ""
            ans = ans + ans_array[0]+"的"+ans_array[1]+": "+ans_array[2]+"\n"
            return ans
        if task_type == 'ans_items':
            ans = ""
            for name, value in ans_array.items():
                for pro, provalue in value.items():
                    provalue = sorted(provalue, key=lambda i: len(i), reverse=True)
                    ans = ans+name+"的"+pro+": "+provalue[0]+"\n"
            #print("========================================================")
            #print(ans)
            return ans





