# @Language: python3
# @File  : analysisPattern2.py
# @Author: LinXiaofei
# @Date  : 2020-03-28
"""
解析模版
"""
import sys
import os
import numpy as np
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)
from data.data_process import read_file


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

        self.nluMatch = {'task_common':[['ent','pro'],['ent']],'task_difinition':[['ent'],['ent-pro'],['pro-ent']],
                         'task_rel':[['ent','ent','pro']],'task_btw_ent':[['ent','ent']]}

        self.country = read_file(project_path + "/data/country.csv")
        """
        实体+属性
        喜马拉雅山的特征是什么
        什么是喜马拉雅山的特征
        喜马拉雅山有哪些特征
        """
        self.entproN = ['ent-pro-V-R','R-V-ent-pro','ent-V-R-pro']

        """
        喜马拉雅山怎么形成的
        怎么形成喜马拉雅山的
        喜马拉雅山是怎么形成的 'ent-V-R-pro'
        """
        self.entproV = ['ent-R-hed&pro','R-hed&pro-ent','ent-V-R-pro']


        """
        实体+关系
        中国的首都是什么
        什么是中国的首都
        中国的首都在哪
        
        中国的首都是什么城市
        什么城市是中国的首都
        中国的首都在哪个城市
        
        ent-rel
        
        俄罗斯位于哪里
        俄罗斯位于什么洲
        """

        self.entrelN = ['ent-rel-V-R','R-V-ent-rel']
        self.entrelNN = ['ent-rel-V-R-ent','R-ent-V-ent-rel']
        self.entrelV = ['ent-hed&rel-R']
        self.entrelVV = ['ent-hed&rel-R-ent']


        """
        关系+关系值(实体)+实体类型-->实体
        
        向下找子类，得到相关属性/关系的属性关系值，匹配属性/关系的值，找到对应的实体
        """
        """
        北京是哪个国家的首都，哪个国家的首都是北京，首都是北京的是哪个国家，首都是北京的是哪个国家
        位于俄罗斯的淡水湖有哪些，有哪些淡水湖位于俄罗斯，哪些淡水湖位于俄罗斯，有哪些位于俄罗斯的淡水湖
        """
        self.relEtypeN = ['ent-V-R-ent-rel','R-ent-rel-V-ent','rel-V-ent-R-ent']

        self.relEtypeV = ['rel-ent-ent-V-R','V-R-ent-rel-ent','R-ent-hed&rel-ent','V-R-rel-ent-ent']

        """
        属性名+属性值+实体类型-->实体
        闽是哪个省的简称 哪个省的简称是闽 
        
        向下找子类，得到相关属性/关系的属性关系值，匹配属性/关系的值，找到对应的实体
        
        """

        self.pronvEtype = ['V-R-ent-pro','R-ent-pro-V','pro-ent-V-R']

    def matchSingalEntity(self,pattern,pattern_index,cut_words):
        entity = []
        property = []
        keywords = []
        count = 0
        index = 0
        temp_entity = []
        pattern_array = pattern.split("-")
        r_index = pattern_array.index("R")

        dis = 100000000
        entity_index = -1
        for pa in pattern_array:
            if pa == "ent":

                temp_dis = np.abs(pattern_index[index]-r_index)
                if temp_dis <= dis:
                    entity_index = pattern_index[index]
            index = index+1
        if entity_index != -1:
            entity.append(cut_words[entity_index])

            return entity, property, keywords, "task_singal_entity"
        return None,None,None,None


    def matchPattern(self,pattern,pattern_index,cut_words):


        """

        :param pattern: 句子得到的模版
        :param pattern_index: 模版中的元素在分词中的下标
        :param cut_words: 分词
        :return:
        """
        entity = []
        property = []
        keywords = []
        task_type = None

        if pattern in self.entproN:
            """实体+属性n"""
            key_array = pattern.split("-")
            index = 0
            for pa in key_array:
                if pa == 'ent':
                    entity.append(cut_words[pattern_index[index]])
                if pa == 'pro' or pa == 'hed&pro':
                    property.append(cut_words[pattern_index[index]])
                index = index + 1
            return entity, property, "","task_normal_pro"

        if pattern in self.entproV:
            """实体+属性v"""


            key_array = pattern.split("-")
            index = 0
            for pa in key_array:
                if pa == 'ent':
                    entity.append(cut_words[pattern_index[index]])
                if pa == 'pro' or pa == 'hed&pro':
                    property.append(cut_words[pattern_index[index]])
                index = index + 1

            return entity, property, "","task_normal_pro"

        if pattern in self.entrelN:
            """实体+关系n"""
            key_array = pattern.split("-")
            index = 0
            for pa in key_array:
                if pa == 'ent':
                    entity.append(cut_words[pattern_index[index]])
                if pa == 'rel' or pa == 'hed&rel':
                    property.append(cut_words[pattern_index[index]])
                index = index + 1

            return entity, property, "","task_normal_rel"

        if pattern in self.entrelNN:
            """实体+关系n"""
            key_array = pattern.split("-")
            index = 0
            for pa in key_array:
                if pa == 'rel' or pa == 'hed&rel':
                    property.append(cut_words[pattern_index[index]])
                    entity.append(cut_words[pattern_index[index - 1]])
                index = index + 1
            return entity, property, "","task_normal_rel"

        if pattern in self.entrelV:
            """实体+关系v"""

            key_array = pattern.split("-")
            index = 0
            for pa in key_array:
                if pa == 'ent':
                    entity.append(cut_words[pattern_index[index]])
                if pa == 'rel' or pa == 'hed&rel':
                    property.append(cut_words[pattern_index[index]])
                index = index + 1
            return entity, property, "","task_normal_rel"

        if pattern in self.entrelVV:
            """实体+关系v"""

            key_array = pattern.split("-")
            index = 0
            for pa in key_array:
                if pa == 'rel' or pa == 'hed&rel':
                    property.append(cut_words[pattern_index[index]])
                    entity.append(cut_words[pattern_index[index - 1]])
                index = index + 1
            return entity, property, "","task_normal_rel"

        if pattern in self.relEtypeV:
            """关系(名词性)+关系值(实体)+实体类型"""

            pattern_array = pattern.split("-")
            index = 0
            if 'rel' in pattern_array:
                rel_index = pattern_array.index('rel')
            elif 'hed&rel' in pattern_array:
                rel_index = pattern_array.index('hed&rel')
            property.append(cut_words[pattern_index[rel_index]])
            keywords.append(cut_words[pattern_index[rel_index + 1]])
            for pa in pattern_array:
                if pa == 'ent' :
                    if index == rel_index + 1:
                        index = index + 1
                        continue
                    entity.append(cut_words[pattern_index[index]])
                index = index + 1

            return entity, property, keywords,"task_son_kw_match"

        if  pattern  =='ent-V-R-ent-rel':
            """关系(动词性)+关系值(实体)+实体类型"""
            keywords.append(cut_words[pattern_index[0]])
            entity.append(cut_words[pattern_index[3]])
            property.append(cut_words[pattern_index[4]])
            return entity, property, keywords,"task_son_kw_match"
        if  pattern == 'R-ent-rel-V-ent':
            keywords.append(cut_words[pattern_index[4]])
            entity.append(cut_words[pattern_index[1]])
            property.append(cut_words[pattern_index[2]])
            return entity, property, keywords,"task_son_kw_match"
        if  pattern == 'rel-V-ent-R-ent':
            keywords.append(cut_words[pattern_index[2]])
            entity.append(cut_words[pattern_index[4]])
            property.append(cut_words[pattern_index[0]])
            return entity, property, keywords,"task_son_kw_match"

        """
        属性名 + 属性值 + 实体类型 -->实体
        闽是哪个省的简称
        哪个省的简称是闽
        发源地在云南省乌蒙山东南侧的河流是哪个

        向下找子类，得到相关属性 / 关系的属性关系值，匹配属性 / 关系的值，找到对应的实体

        self.pronvEtype = ['#V-R-ent-pro',
                           'R-ent-pro-V#',
                           'pro#ent-V-R']
        """
        if 'pro' in pattern and 'V' in pattern:
            pattern_array = pattern.split("-")
            v_index = pattern.index('V')
            v_word_index = pattern_array.index('V')
            front = pattern[:v_index + 1]
            print("front", front)
            back = pattern[v_index:]
            print("front", back)

            if front == 'R-ent-pro-V':
                print('v_word_index', pattern_index[v_word_index])
                match_one = "".join(cut_words[:pattern_index[v_word_index]])
                print("match_one", match_one)
                entity.append(cut_words[pattern_index[1]])
                property.append(cut_words[pattern_index[2]])
                return entity, property, match_one, 'task_son_match'


            elif back == 'V-R-ent-pro':

                print('v_word_index', pattern_index[v_word_index])
                match_one = "".join(cut_words[:pattern_index[v_word_index]])
                print("match_one", match_one)
                entity.append(cut_words[pattern_index[-2]])
                property.append(cut_words[pattern_index[-1]])
                return entity, property, match_one, 'task_son_match'

            elif pattern_array[0] == 'pro' and pattern_array[-1] == 'R' and pattern_array[-2] == 'V' and pattern_array[
                -3] == 'ent':
                entity.append(cut_words[pattern_index[-3]])
                property.append(cut_words[pattern_index[0]])

                match_one = "".join(cut_words[pattern_index[0]+1:pattern_index[-3]])
                print("match_one",match_one,pattern_index[1],pattern_index[-3])

                return entity,property,match_one,'task_son_match'

        return None,None,None,None

if __name__ == '__main__':

    p = PatternMatch()







