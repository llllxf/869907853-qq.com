# @Language: python3
# @File  : dialogManagement.py
# @Author: LinXiaofei
# @Date  : 2020-03-18
"""

"""
import sys
import os
import numpy as np
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
# print(project_path)
sys.path.append(project_path)

from nlu.matchWordsByPattern import matchWordsByPattern
from nlu.patternAnalysis import PatternMatch

class DialogManagement(object):
    def __init__(self):

        self.nlu = matchWordsByPattern()
        self.pattern_match = PatternMatch()

    def askBack(self,ans):
        hed_content_ans = ans[0]
        sbv_arr = ans[1]
        hed_rate_cont = ans[2]
        att = ans[3]


        print("请问你问的具体是：")
        for sbv in sbv_arr:
            print(sbv+att)

    def ansFuther(self,ans,inp):
        hed_content_ans = ans[0]
        hed_rate_cont = ans[2]
        final_ans = []
        final_rate = []
        index = 0
        for name,proname,con in hed_content_ans:
            if inp in con:
                final_ans.append([name,proname,con])
                final_rate.append(hed_rate_cont[index])
            index = index+1
        if final_ans != []:
            max_index = np.argmax(np.array(final_rate))
            max_ans = final_ans[max_index]
            ans_str = ""
            ans_str = ans_str+max_ans[0]+"\n"+max_ans[1]+": "+max_ans[2]
            return ans_str
        return None




    def answernQS(self, words):
        task = self.pattern_match.judgeSyntax(words)
        print("句式类别: ",task)
        if task == 'task_whether':
            """
            由于设置的条件更严谨导致是否问题难以区分无法回答和不是
            """
            ans = self.nlu.dealWithAsking(words,False)
            #print(ans)
            if ans == None:
                ans = self.nlu.dealWithAsking(words,True)


            if ans == None:
                #print("暂时无法回答")
                return ["暂时无法回答"]
            else:
                answern = ans[0]
                for name,con in answern.items():
                    if name in words:
                        #print("是")
                        return ["是"]
                #print("否")
                return ["否"]
        elif task == 'task_subset':
            ans = self.nlu.ansEntityByType(words)
            #print(ans)
            return [ans]
        else:
            ans = self.nlu.dealWithAsking(words,False)
            if ans == None:
                ans = self.nlu.dealWithAsking(words, True)

            if ans == None:
                #print("暂时无法回答")
                return ["暂时无法回答"]

            if len(ans)==5:
                if ans[4] == 'hed_content_ans':
                    self.askBack(ans)
                    return ans
                    #s = input()
                    #final_ans = self.ansFuther(ans,s)
                    #print(final_ans[0]+"\n"+final_ans[1]+": "+final_ans[2])
                    #return final_ans[0]+"\n"+final_ans[1]+": "+final_ans[2]
            ans_str = ""
            for answern in ans:
                for name, con in answern.items():
                    ans_str = ans_str+name+"\n"
                    #print(name)
                    for pname, pcon in con.items():
                        if len(pcon) > 1:
                            ps = ",".join(pcon)

                        else:
                            ps = pcon[0]
                        ans_str = ans_str+pname+": "+ps+"\n"
                        #print(pname + ": " + ps)

            return [ans_str]

        return ["暂时无法回答"]

"""
1.询问属性内容的问题：给出实体，询问属性，得到属性值
湖泊的构成
洞庭湖的特征

2.询问属性名称的问题：给出实体和属性内容，得到属性的名称
415米是死海的什么数据

3.是否问题：给出实体和属性内容，得到属性的名称
洞庭湖是不是泥沙淤积严重，湖泊面积税减
太湖是不是泥沙淤积严重，湖泊面积税减

4.询问实体的问题，给出实体的类型和属性内容，得到实体值
什么湖泊是世界上最深的淡水湖
世界上最深的淡水湖的是

5.询问实体的问题，给出实体类型，得到子类集
有哪些淡水湖
有哪些咸水湖
"""

if __name__ == '__main__':
    ans = None
    while (1):
        a = DialogManagement()
        if ans:
            if len(ans) == 1:
                print(ans[0])
                s = input()
                a = DialogManagement()
                ans = a.answernQS(s)
            else:
                s = input()
                #a.ansFuther()
                final_ans = a.ansFuther(ans, s)

                if final_ans:
                    print(final_ans)
                else:
                    ans = a.answernQS(s)


        if ans is None:
            s = input()
            ans = a.answernQS(s)

