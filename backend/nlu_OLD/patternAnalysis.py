# @Language: python3
# @File  : analysisPattern2.py
# @Author: LinXiaofei
# @Date  : 2020-03-28
"""
解析模版
"""
import sys
import os
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)


class PatternMatch(object):
    """
    模版匹配类
    """
    def __init__(self):
        """
        模版匹配器分为三个等级
        1.句式分类，分为是否问题，属性或实体询问问题，子集询问问题
        2.nlu处理后的模版匹配问题
        3.多个实体的模版匹配问题
        """
        self.syntaxMatch = {'task_whether':[['是不是'],['是','吗'],['有没有'],['有','吗'],['是否']],
                         'task_subset':[['有哪些'],['有什么'],['哪些']]}

        self.nluMatch = {'task_common':[['ent','pro'],['ent']],'task_difinition':[['ent'],['ent-pro']],
                         'task_rel':[['ent','ent']]}




    def judgeSyntax(self,words):
        for name,context in self.syntaxMatch.items():
            for con in context:
                flag = True
                for c in con:
                    if c  not in words:
                        flag = False
                        break
                if flag:
                    return name
        return "task_normal"

    def judgeNlu(self,pattern):


        """
        :param words: 问句
        :return: 认为类型
        """

        """
        只有一个实体，则介绍实体
        """
        for context in self.nluMatch['task_difinition']:

            if pattern == context[0]:
                return 'task_difinition'

        """
        有两个即以上实体和至少一个属性则处理多个实体与该属性的关系
        """
        if 'ent' in pattern:
            first_index = pattern.find('ent')
            first_index += 3
            if 'ent' in pattern[first_index:]:
                #if 'pro' in pattern and 'ent-pro' not in pattern:
                #    return 'task_rel_pro'
                return 'task_rel'


        """
        有一个实体
        """
        for context in self.nluMatch['task_common']:

            for con in context:

                flag = True
                if con not in pattern:
                    flag = False
                    break
            if flag:
                return "task_common"

        return None

    def findContry(self,father_dict):
        for son,fl in father_dict.items():
            if "国家" in fl or "城市" in fl:
                return son
        else:
            return None


    def judgeRel(self,father_dict,entity_for_sort):

        """
        :param father_dict:
        :param entity_for_sort:
        :return:
        """
        """两个实体同类的情况"""

        ori_entity = entity_for_sort[0][0]
        ori_father = father_dict[ori_entity]
        stop_entity = []

        formed_entity = []
        son = self.findContry(father_dict)
        """
        存在国家实体
        """
        if son:
            ori_entity = son
            ori_father = father_dict[son]
            #stop_entity.append(ori_entity)
            """
            只有两个实体时
            """
            if len(entity_for_sort) == 2:
                for oe in entity_for_sort:
                    if oe[0] == son:
                        continue
                    formed_entity.append(oe[0])
                    father = father_dict[oe[0]]
                    if father==[] or father==None:
                        return "task_position_limit", formed_entity
                    for f in father:
                        if f in ori_father:
                            formed_entity.append(son)
                            return "task_same_level",formed_entity
                        else:
                            return "task_position_limit", formed_entity


            for se in entity_for_sort:
                if se[0] == son or father_dict[se[0]]==[] or father_dict[se[0]]==None:
                    stop_entity.append(se[0])
                    continue
                else:
                    sec_ent = se[0]
                    break
            sec_father = father_dict[sec_ent]
            stop_entity.append(sec_ent)


            """
            多个国家实体
            """
            for sf in sec_father:
                if sf == '地理概念' or sf == '地理事实' or sf == '地理方法' or sf == '地理原理' or \
                        sf == '常识概念' or sf == "地理过程" or sf == "地理关系":
                    continue
                if sf in ori_father:
                    formed_entity.append(son)
                    formed_entity.append(sec_ent)

                    for oe in entity_for_sort:
                        if oe[0] in stop_entity:
                            continue
                        else:
                            oe_father = father_dict[oe[0]]
                            for oef in oe_father:
                                if oef == '地理概念' or oef == '地理事实' or oef == '地理方法' or oef == '地理原理' or \
                                        oef == '常识概念' or oef == "地理过程" or oef == "地理关系":
                                    continue
                                if oef in sec_father:
                                    formed_entity.append(oe[0])
                                    #print(formed_entity)
                    return "task_same_level", formed_entity

            if True:
                """
                limit
                1. 只有一个非国家实体
                2. 多个非国家实体
                """


                formed_entity.append(sec_ent)

                for se in entity_for_sort:
                    if se[0] in stop_entity:
                        continue

                    father = father_dict[se[0]]
                    #print(se[0],father)

                    for of in sec_father:
                        if of == '地理概念' or of == '地理事实' or of == '地理方法' or of == '地理原理' or \
                                of == '常识概念':
                            continue
                        if of in father:
                            formed_entity.append(se[0])
                            break
                if formed_entity != []:

                    return "task_position_limit", formed_entity
                else:
                    print("how can it possible")
                    return "task_position_limit", []

        else:
            """
            不存在国家实体
            1.同级
            2.没有关系
            """
            for se in entity_for_sort[1:]:
                father = father_dict[se[0]]
                for of in ori_father:
                    if of == '地理概念' or of == '地理事实' or of == '地理方法' or of == '地理原理' or \
                            of == '常识概念':
                        continue
                    if of in father:
                        formed_entity.append(se[0])
                        break
            if formed_entity != []:
                formed_entity.append(ori_entity)
                #print(formed_entity)
                return "task_same_level", formed_entity
            else:
                return None,None

if __name__ == '__main__':

    p = PatternMatch()
    ans = p.judgeNlu("ent#pro")
    print(ans)





