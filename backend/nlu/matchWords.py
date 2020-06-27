import sys
import os
import numpy as np
import jieba
import urllib.parse
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
# print(project_path)
sys.path.append(project_path)
from data.data_process import read_file
from nlu.LTPUtil import LTPUtil
from graphSearch.graphSearch import graphSearch
from dealNLU.compareNLU import compareNLU
from dealNLU.calculateNLU import calculateNLU

import requests, json

class matchWords(object):
    """
    """

    def __init__(self):
        """
        匹配类的初始化
        1. 从文件读取出图谱中的实体和属性
        2. 属性需要进一步出去，分离出图谱属性，统配属性，属性别称
        3. 实体个属性都按照长度排序
        4. 设定停用词和过滤符号

        """
        self.ltp_util = LTPUtil()
        self.compare_util = compareNLU()
        self.calculate_util = calculateNLU()
        self.graph_util = graphSearch()

        self.syntaxMatch = {'task_whether': [['是不是'], ['是', '吗'], ['有没有'], ['有', '吗'], ['是否'], ['是否是'],['会','吗']]}

        self.instanceArray = list(set(read_file(project_path + "/data/allentity.csv")))
        self.instanceArray = sorted(self.instanceArray, key=lambda i: len(i), reverse=True)

        self.typeArray = list(set(read_file(project_path + "/data/etype.csv")))
        self.typeArray = sorted(self.typeArray, key=lambda i: len(i), reverse=True)

        proArray = read_file(project_path + "/data/cleanpro.csv")
        self.standardPro = sorted(proArray, key=lambda i: len(i), reverse=True)

        relArray = read_file(project_path + "/data/cleanrel.csv")
        self.relArray = sorted(relArray, key=lambda i: len(i), reverse=True)

        self.commonPro = []
        self.aliasArray = {}

        aliasArray = read_file(project_path + "/data/pro.csv")

        for p in aliasArray:
            temp_standard = p.split(":")
            #self.aliasArray[temp_standard[0]] = []
            if temp_standard[1] != '':

                temp_alias = temp_standard[1].split(",")

                if len(temp_alias)>0 and temp_alias[0] != '':
                        self.aliasArray[temp_standard[0]]= temp_alias

        jieba.load_userdict(self.instanceArray)
        jieba.load_userdict(self.standardPro)
        jieba.load_userdict(self.relArray)
        jieba.load_userdict(project_path + "/data/jieba_other.csv")


    def cutWords(self,words):

        return list(jieba.cut(words))

    def classify(self,words):
        """
        得到句子的类型，不同类型的句子进行初步整理
        :param words:
        :return:
        对于是否问题，第一个返回值是问句类型，第二个返回值是问句本体，第三个值是问的实体
        对于比较问题，第一个返回值是问句类型，第二个值是模版匹配结果，第三个返回值是抽取的句子信息
            比较问题中如果返回的是反问句，那么匹配结果就是实际操作对象，也就是作用是正常比较问句的抽取信息，第三个值是反问标识
        """

        compare_type,compare_inf,match_result = self.compare_util.checkCompare(words)

        if compare_type is not None:
            if compare_inf == 'task_compare_ask':
                return compare_type,match_result,compare_inf
            print("任务类型: ",compare_type)
            print("问题类型: ", match_result)
            print("比较实体: ",compare_inf)
            print("===========================================")

            return compare_type,match_result,compare_inf

        calculate_type,calculate_inf,match_result = self.calculate_util.checkCalculateMost(words)
        if calculate_type is not None:
            if calculate_inf == 'task_calculate_ask':
                return calculate_type,match_result,calculate_inf
            print("任务类型: ",calculate_type)
            print("问题类型: ", match_result)
            print("最值对象: ",calculate_inf['ask'])
            print("最值属性: ",calculate_inf['predicate'])
            print("最值倾向: ",calculate_inf['predicate_adj'])
            print("===========================================")

            return calculate_type,match_result,calculate_inf

        calculate_type, calculate_inf, match_result = self.calculate_util.checkCalculateDist(words)
        print(calculate_type,"calculate_type")
        if calculate_type is not None:
            if calculate_inf == 'task_calculate_ask':
                return calculate_type, match_result, calculate_inf
            print("任务类型: ", compare_type)
            print("问题类型: ", match_result)
            print("询问对象: ", calculate_inf)
            print("===========================================")

            return calculate_type, match_result, calculate_inf

        for pattern in self.syntaxMatch['task_whether']:
            count = 0
            for word in pattern:

                if word in words:
                    count = count+1
                if count == len(pattern):
                    pattern_array = words.split(pattern[0])
                    if len(pattern)>1:
                        return "task_whether",pattern_array[1][:-1],pattern_array[0],
                    return "task_whether",pattern_array[1],pattern_array[0]
        return "task_normal",None,None

    def formAsking(self,ask_words,ask_ent):
        """
        words_type, ask_ent, ask_words = self.classify(words)

        if words_type == 'task_compare':
            return ask_words,ask_ent,words_type
        elif words_type == 'task_normal':
            ask_words = words
        elif words_type == 'task_whether':
        """
        father_list = self.graph_util.getFatherByType(ask_ent)
        father_list = sorted(father_list, key=lambda i: len(i), reverse=True)
        #print(father_list)
        exist = False
        for father in father_list:
            if father in ask_words:
                exist = True
                break
        if exist == False:
            ask_words = ask_words + "的" + father_list[0] + "是什么"
        ask_words = self.checkR(ask_words)
        return ask_words



    def checkR(self,words):
        cut_words = list(jieba.cut(words))
        tlp_pattern, arcs_dict,reverse_arcs_dict,postags, hed_index = self.ltp_util.get_sentence_pattern(cut_words)
        postags = list(postags)

        if 'r' not in postags:
            words += "是什么"
            return words
        return words

    def aliasChange(self,cutwords):
        entity = []
        for word in cutwords:
            if word in self.instanceArray:
                entity.append(word)
        for ent in entity:
            pro_list = self.graph_util.getProList(ent)

            for pro in pro_list:
                if pro in self.aliasArray.keys():
                    for alias in self.aliasArray[pro]:
                        if alias in cutwords:
                            cutwords[cutwords.index(alias)] = pro
            return cutwords

        return cutwords


    def wordBywordAndCheck(self, cut_words,arcs_dict,reverse_arcs_dict,postags,hed_index):
        """
        1.分词
        2.得到图谱中的实体和属性，并标记下标，生成模版
        :param words: 句子
        :return: 抽取的实体，属性，关系
        """

        find_common_pro = []
        find_pro = []
        find_entity = []
        pro_index = {}
        com_index = {}
        ins_index = {}
        coo = []
        coo_index = []

        words_mark = np.zeros(len(cut_words)) #每个分词的标记

        for c_index in range(len(cut_words)):

            cw = cut_words[c_index]
            if cw in self.instanceArray:
                if self.judgeSub(cw,find_entity):
                    continue
                if 'COO' in reverse_arcs_dict[c_index].keys():
                    coo.append(cut_words[c_index])
                    coo_index.append(c_index)
                    continue
                if cw in self.typeArray:
                    words_mark[c_index]=6
                else:
                    words_mark[c_index]=1
                ins_index[cw]=c_index
                find_entity.append(cw)

            if cw in self.standardPro:
                if self.judgeSub(cw,find_pro):
                    continue
                if words_mark[c_index] ==1 :
                    words_mark[c_index]=3
                    find_pro.append(cw)
                    pro_index[cw]=c_index
                elif words_mark[c_index]==6:
                    words_mark[c_index]=7
                    find_pro.append(cw)
                    pro_index[cw] = c_index
                elif words_mark[c_index]==0:
                    words_mark[c_index]=2
                    find_pro.append(cw)
                    pro_index[cw] = c_index

            if cw in self.relArray:
                if self.judgeSub(cw,find_pro):
                    continue
                if words_mark[c_index]>0:
                    continue
                else:
                    words_mark[c_index]=5
                    find_pro.append(cw)
                    pro_index[cw] = c_index
            if words_mark[c_index]>0:
                continue

            if cw in self.commonPro:
                if self.judgeSub(cw,find_pro):
                    continue
                if self.judgeSub(cw,find_common_pro):
                    continue
                find_common_pro.append(cw)
                com_index[cw]=c_index
                words_mark[c_index] = 4

        """
        形成模版
        """
        #print("word_mark",words_mark)
        pattern_normal = ""
        pattern_pro = ""
        pattern_type = ""
        index = 0

        for wm in words_mark:

            if wm == 0:
                if postags[index] == 'r':
                    pattern_normal += 'R-'
                    pattern_pro += 'R-'
                    pattern_type += 'R-'


                elif index == hed_index and (postags[hed_index]=='v' or postags[hed_index]=='p'):
                    pattern_normal += 'V-'
                    pattern_pro += 'V-'
                    pattern_type += 'V-'

                else:
                    pattern_normal += cut_words[index]
                    pattern_pro += cut_words[index]
                    pattern_type += cut_words[index]
                    pattern_normal += '-'
                    pattern_pro += '-'
                    pattern_type += '-'
            if wm == 1:
                pattern_normal += 'ent-'
                pattern_pro += 'ent-'
                pattern_type += 'ent-'
            if wm == 2:
                if index == hed_index:
                    pattern_normal += 'hed&pro-'
                    pattern_pro += 'hed&pro-'
                    pattern_type += 'hed&pro-'
                else:
                    pattern_normal += 'pro-'
                    pattern_pro += 'pro-'
                    pattern_type += 'pro-'
            if wm == 3:
                pattern_normal += 'ent-'
                pattern_pro += 'pro-'
                pattern_type += 'ent-'
            """
            if wm == 4:
                pattern += "com"
                pattern += "-"
            """
            if wm == 5:
                if index == hed_index:
                    pattern_normal += 'hed&rel-'
                    pattern_pro += 'hed&rel-'
                    pattern_type += 'hed&rel-'
                else:
                    pattern_normal += 'rel-'
                    pattern_pro += 'rel-'
                    pattern_type += 'rel-'
            if wm == 6:
                pattern_normal += 'ent-'
                pattern_pro += 'ent-'
                pattern_type += 'type-'
            if wm == 7:
                pattern_normal += 'ent-'
                pattern_pro += 'pro-'
                pattern_type += 'type-'
            index = index+1
        if pattern_normal[-1] == '-':
            pattern_normal = pattern_normal[:-1]
        if pattern_pro[-1] == '-':
            pattern_pro = pattern_pro[:-1]
        if pattern_type[-1] == '-':
            pattern_type = pattern_type[:-1]

        """
        加入有实体和属性重名的情况，那么依据该ent&pro的依存句法树来确定该词汇是实体还是属性
        即与实体存在依存那么是属性，与属性存在依存那么是实体
        """
        """
        if ent_pro:
            print(arcs_dict)
            print(reverse_arcs_dict)

            index = 0
            patter_array = pattern.split("-")
            print(patter_array,len(patter_array),len(reverse_arcs_dict))
            for p in patter_array:
                if p == 'ent&pro':
                    #ent-ent&pro-->ent-pro
                    
                    if 'ATT' in arcs_dict[index].keys():
                        att = arcs_dict[index]['ATT']
                        for sub_a in att:
                            if cut_words[sub_a] in find_entity:
                                find_entity.pop(find_entity.index(cut_words[index]))
                                pattern = pattern.replace("ent&pro","pro")
                                break
                    
                    #ent&pro-pro-->ent-pro
                    if 'ATT' in reverse_arcs_dict[index].keys():
                        att = reverse_arcs_dict[index]['ATT']
                        for sub_a in att:
                            if cut_words[sub_a] in find_pro:
                                find_pro.pop(find_pro.index(cut_words[index]))
                                pattern = pattern.replace("ent&pro", "ent")
                                break
                index=index+1
        """
        form_pattern = []


        sub_pattern, sub_index = self.formPattern(pattern_type)
        form_pattern.append(sub_pattern)
        pattern_index = sub_index

        sub_pattern, sub_index = self.formPattern(pattern_normal)
        form_pattern.append(sub_pattern)


        sub_pattern,sub_index = self.formPattern(pattern_pro)
        form_pattern.append(sub_pattern)

        return form_pattern,pattern_index,coo,coo_index

    def formPattern(self,pattern):
        form_pattern = ""
        pattern_index = []
        index = 0
        for p in pattern.split("-"):

            if p in ['R', 'ent', 'hed&pro', 'hed&rel', 'rel', 'pro','V','type']:
                form_pattern += p
                pattern_index.append(index)
                form_pattern += '-'
            index = index + 1

        if form_pattern[-1] == '-':
            form_pattern = form_pattern[:-1]

        return form_pattern, pattern_index


    def positionControl(self, entity_deal):
        """
        匹配抽出的属性名称和实体具有的属性名称

        :param find_pro: 抽取的属性
        :param find_rel: 抽取的关系
        :param entity_deal: 携带信息的实体
        :return:
        """
        ans = []


        for name, content in entity_deal.items():
            pro = np.array(content['p'])
            rel = np.array(content['r'])
            for p in pro:
                if p[0] in self.position_key:
                    ans.append(p[1])

                    #return [name,p[0],p[1]]
            for r in rel:
                if r[0] in self.position_key:
                    ans.append(r[1])
                    #return [name,r[0],r[1]]
        if ans == []:
            return None
        return ans



    def judgeProByMatch(self, common_pro,entity_pro):
        """
        是否是属性子串
        :param common_pro: 通用属性
        :param entity_pro: 实体具有的属性
        :return:
        """

        a_entity_pro = {}
        for p in entity_pro:
            if common_pro in p[0]:
                if p[0] in a_entity_pro.keys():
                    a_entity_pro[p[0]].append(p[1])
                else:
                    a_entity_pro[p[0]] = [p[1]]
        if a_entity_pro == {}:
            return None
        else:
            #print("a_entity_pro",a_entity_pro)
            return a_entity_pro

    def judgeSub(self, sub, ori_list):
        """

        :param sub: 被判断对象
        :param ori_list: 判断数组
        :return:
        """


        for ori in ori_list:

            if sub in ori:
                return True
        return False


    def directAnsComProName(self,find_pro, entity_deal):
        """
        匹配抽出的通用属性名称和实体携带的属性名称，匹配方式为通用是实体携带属性的子串
        :param find_pro: 抽取的属性
        :param find_rel: 抽取的关系
        :param entity_deal: 携带信息的实体
        :return:
        """
        common_pro = {}

        for name, content in entity_deal.items():

            name_dict = {}

            pro = np.array(content['p'])
            rel = np.array(content['r'])

            for c_p in find_pro:

                p = self.judgeProByMatch(c_p,pro)
                if p:
                    for pkey,pvalue in p.items():
                        name_dict[pkey] = pvalue
            if name_dict != {}:
                common_pro[name] = name_dict


        if common_pro == {}:
            return None
        return [common_pro]


    def unifyProCon(self,att_entity,con):
        for a in att_entity:
            if a in self.synonymy.keys():
                for a_s in self.synonymy[a]:
                    if a_s in con:
                        con = con.replace(a_s,a)
        return con

    def directAnsProCon(self, deal_entity, att_entity, att_adj):
        """
        根据实体携带的属性信息和问句原文匹配得到与答案相符的属性信息
        1. 遍历实体所有的属性信息
        2. 按字符匹配问句和属性信息
        3. 2得到空则按向量相似度得到匹配信息
        4. 2,3均空则返回空
        :param words: 问句
        :param deal_entity: 实体及其信息
        :return: 答案或空
        """

        if att_entity == [] and att_adj == []:
            return None

        ans = []
        for name,content in deal_entity.items():
            #if name != '鄱阳湖':
            #    continue

            """
            抽取出的实体的属性
            """
            pro = np.array(content['p'])
            rel = np.array(content['r'])

            """
            去掉问题中的实体方便匹配
            """
            flag = True
            for p in pro:

                """
                类似与标签的属性
                """
                if p[1] == name or '分类' in p[0]:
                    continue
                con = self.unifyProCon(att_entity,p[1])
                for a_e in att_entity:
                    if a_e  not in con:
                        flag = False
                        break
                for a_a in att_adj:
                    if a_a not in con:
                        flag = False
                        break
                if flag:
                    ans.append([name,p[0],p[1]])
        if ans != []:
            print("ans",ans)
            return ans

        return None


    def directAns(self,hed_entity,hed_pro,find_common_pro,att_entity,att_adj):
        #print(hed_entity,hed_pro,find_common_pro,att_entity,att_adj)
        """
        根据抽取的实体，查找实体的属性信息，根据抽取的属性信息或者问句原文匹配属性值得到回答，即直接根据抽取的实体可得到回答
        :param words: 句子
        :param find_entity: 抽取的实体
        :param find_pro:
        :return:
        """
        #print(hed_entity,hed_pro,find_common_pro,att_entity,att_adj)

        deal_entity = self.dealWithEnitity(hed_entity)
        print("抽取的实体信息:",deal_entity)
        print("========================================================")

        """抽取的属性可直接查找内容回答"""
        """
        if len(hed_pro) > 0:
            #print(hed_entity,hed_pro,find_common_pro,att_entity,att_adj)
            ans = self.directAnsProName(hed_pro, deal_entity)
            #print(hed_entity,hed_pro,find_common_pro,att_entity,att_adj)

            if ans != None:

                return ans
        if len(find_common_pro)>0:
            ans = self.directAnsComProName(find_common_pro,deal_entity)
            if ans != None:
                return ans
        """

        """抽取的属性不可直接回答/没有抽取出属性"""

        #ans = self.directAnsProCon(deal_entity,att_entity,att_adj)

        #if ans != None:
        #    return ans
        return None

    def getEntityByType(self, entity):
        """
        得到实体的子类
        :param entity: 实体
        :return: 实体子类
        """

        """获取子类"""
        uri = "http://127.0.0.1:8004/getEntityByType?repertoryName=geo&entityName=" + entity
        r = requests.post(uri)
        son_list = list(r.json())

        if son_list == []:
            return None
        return son_list

    def getRel(self, entity_a,entity_b):
        """
        得到实体的子类
        :param entity: 实体
        :return: 实体子类
        """

        uri = "http://127.0.0.1:8004/getRel?repertoryName=geo&entityNameA=" + entity_a+"&entityNameB="+entity_b


        res = requests.post(uri)
        if '500' in str(res.content):
            return None

        son_list = list(res.json())

        if son_list == []:
            return None

        return son_list

    def downFindAns(self, hed_entity,hed_pro,find_common_pro,att_entity,att_adj):
        """
        查找抽取的实体的子类，匹配属性或属性内容来得到答案

        :param words: 句子
        :param find_entity: 实体
        :param find_pro: 属性和关系
        :param find_common_pro: 通用实体和关系
        :return: 回答或空
        """
        for e in hed_entity:
            son_list = self.getEntityByType(e)
            if son_list:
                ans = self.directAns(son_list,hed_pro,find_common_pro,att_entity,att_adj)
                if ans != None:

                    return ans
        return None



    def getFatherByType(self, entity):
        """
        得到实体的父类
        :param entity: 实体
        :return: 实体父类
        """

        """获取父类"""
        uri = "http://127.0.0.1:8004/getFatherByType?repertoryName=geo&entityName=" + entity
        r = requests.post(uri)
        father_list = list(r.json())

        if father_list == []:
            return None
        return father_list

    def upFindAns(self, words, find_entity, find_pro,find_common_pro):
        """
        查找抽取的实体的子类，匹配属性或属性内容来得到答案

        :param words: 句子
        :param find_entity: 实体
        :param find_pro: 属性和关系
        :param find_common_pro: 通用实体和关系
        :return: 回答或空
        """
        for e in find_entity:
            father_list = self.getFatherByType(e)
            if father_list==None:
                continue
            father_list = list(set(father_list))
            #print(father_list)
            if father_list:
                ans = self.directAns(words,father_list,find_pro,find_common_pro)
                if ans != None:
                    return ans
        return None

    def ansDefinition(self, entity):
        """获取属性信息"""
        uri = "http://127.0.0.1:8004/getEntityByLabelWithPro?repertoryName=geo&entityName=" + entity
        r = requests.post(uri)
        pro_list = list(r.json())
        #print(pro_list)

        for pro in pro_list:

            if "定义" == pro[0]:
                return entity+"："+pro[1]+"\n"
        for pro in pro_list:
            if "内容" == pro[0]:
                return entity + "：" + pro[1] + "\n"

        return "暂无相关介绍\n"


    def ansEntityByType(self,words):
        """
        回答集合问题：有哪些淡水湖

        :param words: 问句
        :return: 回答
        """
        cut_words = list(jieba.cut(words))
        #words = self.preProcessWords(words)
        pattern, pattern_index,find_entity, find_pro, find_common_pro, entity_index, pro_index, common_index = self.wordBywordAndCheck(
            cut_words)
        for e in find_entity:
            son_list = self.getEntityByType(e)
            if son_list:
                return " ".join(son_list)
        return None

    def checkPosition(self,entity,unuse_ent):
        """


        :param entity:
        :param unuse_ent:
        :return:
        """
        if unuse_ent == []:
            return True

        entity_deal = self.dealWithEnitity([entity])

        for name, content in entity_deal.items():

            pro = np.array(content['p'])
            rel = np.array(content['r'])

            for pname,pvalue in pro:
                for une in unuse_ent:
                    if une in pvalue:
                        return True
            for rname,rvalue in rel:
                for une in unuse_ent:
                    if une in rvalue:
                        return True
        return False

    def dealWithQuesType(self,task,hed_entity,hed_pro,att_entity,att_adj,find_common_pro):
        """
        根据不同类型的问题有不同的回答策略
        :param task: 问题类型（任务类型）
        :param words: 问句
        :param find_entity: 找到的实体
        :param find_pro: 找到的属性关系
        :param find_common_pro: 找到的通用属性
        :return: 问题的回答集
        """
        if task == 'task_difinition':
            ans = self.ansDefinition(hed_entity[0])
            print(ans, "ansDefinition")
            return [{hed_entity[0]:{'介绍':[ans]}}]

        elif task != None:

            ans = self.directAns(hed_entity,hed_pro,find_common_pro,att_entity,att_adj)
            if ans != None:
                #ans = self.hedAnswerForProMatch(ans[0], hed_entity, att_entity, att_adj)
                print(ans, "directAns")
                return ans
            ans = self.downFindAns(hed_entity,hed_pro,find_common_pro,att_entity,att_adj)
            if ans != None:
                #ans = self.hedAnswerForProMatch(ans[0], hed_entity, att_entity, att_adj)
                print(ans, "downFindAns")
                return ans
            #ans = self.upFindAns(hed_entity,hed_pro,find_common_pro,att_entity,att_adj)
            #if ans != None:
            #    print(ans, "upFindAns")
            #    return ans

    def hedAnswer(self,answern,cut_words,arcs_dict,hed_index):
        """
        提取问句中的关键信息，通过回答集与关键信息的匹配得到更精确的回答集，适用于非匹配属性值得到回答集的情况
        :param answern: 回答集
        :param cut_words:问句的分词
        :param arcs_dict:依存树
        :param hed_index:关键词
        :return:更精确的回答集
        """
        hed_name_ans = []
        hed_content_ans = []
        hed_keys = arcs_dict[hed_index].keys()
        SBV = ""
        VOB = ""

        if 'SBV' in hed_keys:
            SBV = cut_words[arcs_dict[hed_index]['SBV'][0]]
        else:
            SBV = cut_words[hed_index]
        if 'VOB' in hed_keys:
            VOB = cut_words[arcs_dict[hed_index]['VOB'][0]]

        for name, content in answern.items():

            if SBV in name:
                hed_name_ans.append({name: content})
            conv = list(content.values())[0]
            values = "".join(conv)

            if self.judgeSub(SBV, [values]):
                hed_content_ans.append({name: content})
        if hed_name_ans!=[] or hed_content_ans!=[]:
            return hed_name_ans,hed_content_ans

        for name, content in answern.items():

            if VOB in name:
                hed_name_ans.append({name: content})
            conv = list(content.values())[0]
            values = "".join(conv)

            if self.judgeSub(VOB, [values]):
                hed_content_ans.append({name: content})

        return hed_name_ans,hed_content_ans

    def getEntByfuzzySearch(self,words):

        uri = "http://127.0.0.1:8004/fuzzySearch?repertoryName=geo&words=" + words
        r = requests.post(uri)
        ent_list = list(r.json())
        return ent_list

    def hedAnswerForProMatch(self,ans,hed_entity,att_entity,att_adj):
        form_ans = []
        temp_ans = []
        combine = hed_entity+att_entity
        print("combine",combine)
        for name,con in ans.items():
            if name in combine:
                form_ans.append({name:con})

            for proname,procon in con.items():
                for cb in combine:
                    if cb in procon:
                        form_ans.append({name:con})
        if form_ans == {}:
            return None
        return form_ans




    def askingBackByConAtt(self,content,att):
        """

        根据提取出来的歧义属性进行反问
        歧义属性的匹配的方式是sub(分词与属性之间)

        :param content: 得到的具有歧义的问句关键属性的实体属性集
        :param att: 歧义属性
        :return: 返回歧义属性的主语对象集
        """
        SBV_arr = []
        form_content = {}
        for name,pro_name,pro_cont in content:
            if name in form_content.keys():
                form_content[name].append(pro_cont)
            else:
                form_content[name] = [pro_cont]

            cut_words = list(jieba.cut(pro_cont))
            #print(cut_words,att)

            for cw_index in range(len(cut_words)):
                cw = cut_words[cw_index]
                if cw in att or att in cw:
                    index = cw_index
                    break

            tlp_pattern, arcs_dict, reverse_arcs_dict,postags, hed_index = self.ltp_util.get_sentence_pattern(cut_words)
            print(tlp_pattern)
            att_dict = arcs_dict[index]
            if 'SBV' in att_dict.keys():
                sbv_index = att_dict['SBV'][0]
                if postags[sbv_index] != 'n' or cut_words[sbv_index]=='世界':
                    continue
                if cut_words[att_dict['SBV'][0]] in SBV_arr:
                    continue

                SBV_arr.append(cut_words[att_dict['SBV'][0]])

        if len(form_content.keys())<2:
            return None
        if len(SBV_arr)>1:
            print(SBV_arr)
            return SBV_arr
        return None

    def dealWithWordsWithoutEnt(self,cut_words,arcs_dict,hed_index):
        """

        使用ltp分析句子，得到句子的主语和宾语，通过模糊查询得到匹配的主语填充作为找到的主语
        :param cut_words: 句子分词
        :param arcs_dict: 依存树
        :param hed_index: 关键词下标
        :return: 找到的实体
        """

        hed_keys = arcs_dict[hed_index].keys()
        SBV = ""
        VOB = ""
        ATT = ""

        if 'SBV' in hed_keys:
            SBV = cut_words[arcs_dict[hed_index]['SBV'][0]]
        else:
            SBV = cut_words[hed_index]

        if 'VOB' in hed_keys:
            VOB = cut_words[arcs_dict[hed_index]['VOB'][0]]

        print("SBV,VOB",SBV,VOB)

        if SBV in self.stopword:

            ent_list = self.getEntByfuzzySearch(VOB)
        else:
            ent_list = self.getEntByfuzzySearch(SBV)

        #print(ent_list)
        return ent_list



    def getWordsPattern(self, cut_words):
        """
        :param words: 问句
        :return:
        """
        #cut_words = list(jieba.cut(words))

        tlp_pattern, arcs_dict, reverse_arcs_dict, postags, hed_index = self.ltp_util.get_sentence_pattern(cut_words)
        postags = list(postags)
        print("========================================================")
        print("分词: ", cut_words)


        pattern,pattern_index,coo,coo_index = self.wordBywordAndCheck(
            cut_words,arcs_dict,reverse_arcs_dict,postags,hed_index)
        print("得到的句子模版: ", pattern)
        print("模版中的元素在句子中的下标",pattern_index)
        #print("抽取的实体: ", find_entity, "\t实体及其在句子中的下标: ", entity_index)
        #print("抽取的属性或关系: ", find_pro, "\t属性及其在句子中的下标: ", pro_index)
        print("句法依存树: ", arcs_dict, hed_index)
        print("反向依存句法树:", reverse_arcs_dict)
        print("句法依存模版: ", tlp_pattern)
        print("词性分析: ", postags)

        return pattern,pattern_index,coo,coo_index,arcs_dict,reverse_arcs_dict,postags,hed_index

    def wordBywordAndCheckForARC(self, cut_words, arcs_dict, reverse_arcs_dict, postags, hed_index):
        """
        1.分词
        2.得到图谱中的实体和属性，并标记下标，生成模版
        :param words: 句子
        :return: 抽取的实体，属性，关系
        """

        find_common_pro = []
        find_pro = []
        find_entity = []
        pro_index = {}
        com_index = {}
        ins_index = {}
        coo = []
        coo_index = []

        words_mark = np.zeros(len(cut_words))  # 每个分词的标记

        for c_index in range(len(cut_words)):

            cw = cut_words[c_index]
            if cw in self.instanceArray:
                if self.judgeSub(cw, find_entity):
                    continue
                if 'COO' in reverse_arcs_dict[c_index].keys():
                    coo.append(cut_words[c_index])
                    coo_index.append(c_index)
                    continue

                words_mark[c_index] = 1
                ins_index[cw] = c_index
                find_entity.append(cw)

            if cw in self.standardPro:
                if self.judgeSub(cw, find_pro):
                    continue
                if words_mark[c_index] == 1:
                    words_mark[c_index] = 3
                    find_pro.append(cw)
                    pro_index[cw] = c_index
                elif words_mark[c_index] > 0:
                    continue
                else:
                    words_mark[c_index] = 2
                    find_pro.append(cw)
                    pro_index[cw] = c_index

            if cw in self.relArray:
                if self.judgeSub(cw, find_pro):
                    continue
                if words_mark[c_index] > 0:
                    continue
                else:
                    words_mark[c_index] = 5
                    find_pro.append(cw)
                    pro_index[cw] = c_index
            if words_mark[c_index] > 0:
                continue

            if cw in self.commonPro:
                if self.judgeSub(cw, find_pro):
                    continue
                if self.judgeSub(cw, find_common_pro):
                    continue
                find_common_pro.append(cw)
                com_index[cw] = c_index
                words_mark[c_index] = 4

        """
        形成模版
        """
        pattern = ""
        index = 0

        for wm in words_mark:

            if wm == 0:
                if postags[index] == 'r':
                    pattern += 'R'
                    pattern += "-"
                elif index == hed_index and (postags[hed_index] == 'v' or postags[hed_index] == 'p'):
                    pattern += "V"
                    pattern += "-"
                else:
                    pattern += cut_words[index]
                    pattern += "-"
            if wm == 1:
                pattern += "ent"
                pattern += "-"
            if wm == 2:
                if index == hed_index:
                    pattern += "hed&pro"
                else:
                    pattern += "pro"
                pattern += "-"
            if wm == 3:
                pattern += "ent&pro"

                pattern += "-"
            if wm == 4:
                pattern += "com"
                pattern += "-"
            if wm == 5:
                if index == hed_index:
                    pattern += "hed&rel"
                else:
                    pattern += "rel"
                pattern += "-"
            index = index + 1
        if pattern[-1] == '-':
            pattern = pattern[:-1]

        form_pattern = ""
        pattern_index = []
        index = 0
        for p in pattern.split("-"):

            if p in ['R', 'ent', 'hed&pro', 'hed&rel', 'rel', 'pro', 'ent&pro', 'V']:
                form_pattern += p
                pattern_index.append(index)
                form_pattern += '-'
            index = index + 1

        if form_pattern[-1] == '-':
            form_pattern = form_pattern[:-1]

        return form_pattern, pattern_index, find_entity, find_pro, ins_index, pro_index,coo, coo_index

    def getWordsPatternForARC(self, cut_words):
        """
        :param words: 问句
        :return:
        """
        #cut_words = list(jieba.cut(words))


        tlp_pattern, arcs_dict, reverse_arcs_dict, postags, hed_index = self.ltp_util.get_sentence_pattern(cut_words)
        postags = list(postags)
        print("========================================================")
        print("分词: ", cut_words)


        pattern, pattern_index, find_entity, find_pro,entity_index,pro_index,coo, coo_index = self.wordBywordAndCheckForARC(
            cut_words,arcs_dict,reverse_arcs_dict,postags,hed_index)
        print("得到的句子模版: ", pattern)
        print("模版中的元素在句子中的下标",pattern_index)
        print("抽取的实体: ", find_entity, "\t实体及其在句子中的下标: ", entity_index)
        print("抽取的属性或关系: ", find_pro, "\t属性及其在句子中的下标: ", pro_index)
        print("句法依存树: ", arcs_dict, hed_index)
        print("反向依存句法树:", reverse_arcs_dict)
        print("句法依存模版: ", tlp_pattern)
        print("词性分析: ", postags)

        return pattern,pattern_index,coo,coo_index,arcs_dict,reverse_arcs_dict,postags,hed_index,find_entity, find_pro

    def processPattern(self, cut_words,arcs_dict,postags,hed_index,find_entity,find_pro):
        """

        1.如果句子的核心词汇在找到的实体中，则作为核心实体
        2.如果句子的核心词汇在找到的属性中，则作为核心属性
        3.得到句子的主语
        3.1 主语即找到的实体--该主语即核心实体
          得到主语的相关词语
          如果词语在找到的实体内，则作为实体限制
          如果词语在找到的属性内，则作为核心属性
          其余情况词语作为核心形容词
        3.2 主语为找到的属性--该主语即核心属性
          得到主语的相关词语
          如果词语在找到的实体内，则作为核心实体
          如果词语在找到的属性内，则作为核心属性
          其余情况则作为核心的形容词
        4.如果核心实体为空则从找到的实体中获得
        :param cut_words:
        :param arcs_dict:
        :param hed_index:
        :param find_entity:
        :param find_pro:
        :return:核心词汇 核心属性 属性限制 关键形容词
        """

        att_entity = []
        att_adj = []
        hed_entity = []
        hed_pro = []
        sbv_use = True

        print("hed_index",hed_index)

        hed_keys = arcs_dict[hed_index].keys()

        if cut_words[hed_index] in find_pro:
            hed_pro.append(cut_words[hed_index])
        if cut_words[hed_index] in find_entity:
            hed_entity.append(cut_words[hed_index])

        if 'SBV' in hed_keys:
            SBV_index = arcs_dict[hed_index]['SBV'][0]

            SBV = cut_words[SBV_index]
            if SBV in find_entity:
                hed_entity.append(SBV)
                sbv_keys = arcs_dict[SBV_index].keys()
                for sub_k in sbv_keys:
                    sub_index = arcs_dict[SBV_index][sub_k][-1]
                    if sub_k=='COO':
                        for coo in arcs_dict[SBV_index]['COO']:
                            if cut_words[coo] in find_entity:
                                hed_entity.append(cut_words[coo])
                    elif cut_words[sub_index] in find_entity:
                        att_entity.append(cut_words[sub_index])
                    elif cut_words[sub_index] in find_pro:
                        hed_pro.append(cut_words[sub_index])
                    elif sub_k == 'ATT':
                        if postags[sub_index] == 'r':
                            continue
                        att_adj.append(cut_words[sub_index])
            elif SBV in find_pro:
                hed_pro.append(SBV)
                sbv_keys = arcs_dict[SBV_index].keys()
                for sub_k in sbv_keys:
                    sub_index = arcs_dict[SBV_index][sub_k][-1]
                    if cut_words[sub_index] in find_entity and sub_k == 'ATT':
                        hed_entity.append(cut_words[sub_index])
                    elif cut_words[sub_index] in find_pro:
                        hed_pro.append(cut_words[sub_index])
                    elif sub_k == 'COO' and cut_words[sub_index] in find_pro:
                        hed_pro.append(cut_words[sub_index])
                    elif sub_k == 'ATT':
                        if postags[sub_index] == 'r':
                            continue
                        att_adj.append(cut_words[sub_index])
            else:
                sbv_use = False


        if 'VOB' in hed_keys:

            if sbv_use == False and postags[arcs_dict[hed_index]['SBV'][0]]!='r':
                att_entity.append(cut_words[arcs_dict[hed_index]['SBV'][0]])
            VOB_index = arcs_dict[hed_index]['VOB'][0]

            VOB = cut_words[VOB_index]
            if VOB in find_entity:
                hed_entity.append(VOB)
            elif VOB in find_pro:
                hed_pro.append(VOB)
                sbv_keys = arcs_dict[VOB_index].keys()
                for sub_k in sbv_keys:
                    sub_index = arcs_dict[VOB_index][sub_k][-1]
                    if cut_words[sub_index] in find_entity and sub_k == 'ATT':
                        hed_entity.append(cut_words[sub_index])
                    elif cut_words[sub_index] in find_pro:
                        hed_pro.append(cut_words[sub_index])
                    elif sub_k == 'COO' and cut_words[sub_index] in find_pro:
                        hed_pro.append(cut_words[sub_index])
                    elif sub_k == 'ATT':
                        if postags[sub_index] == 'r':
                            continue
                        att_adj.append(cut_words[sub_index])


        if hed_entity == None and find_entity!=[]:
            for f_e in find_entity:
                if f_e in hed_pro or f_e in att_entity:
                    continue
                hed_entity.append(f_e)
        else:
            for f_e in find_entity:
                if f_e in att_entity or f_e in hed_pro or f_e in hed_entity:
                    continue
                att_entity.append(f_e)

        print("关键实体: ", hed_entity)
        print("关键属性: ", hed_pro)
        print("属性限制: ", att_entity)
        print("关键形容词: ", att_adj)
        print("========================================================")
        return hed_entity,hed_pro,att_entity,att_adj



    def dealWithAsking(self,words):

        #words = self.checkR(words)
        cut_words = list(jieba.cut(words))
        pattern,pattern_index,coo,coo_index,arcs_dict,reverse_arcs_dict,postags,hed_index,find_entity, find_pro = self.getWordsPatternForARC(cut_words)
        self.processPattern(cut_words,arcs_dict,postags,hed_index,find_entity,find_pro)




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
#a.dealWithAsking("太湖是不是泥沙淤积严重，湖泊面积税减")
#a.test()
#a = matchWordsByPattern()
#a.getRel('中国','高原')




if __name__ == '__main__':
    a = matchWords()
    #ans = a.dealWithAsking("中国最大的淡水湖是鄱阳湖吗")
    #print(ans)



    while (1):

        #print("user:")
        s = input("user: ")
        if s == '':
            continue
        #ans = a.wordBywordAndCheck(s)

        #print(list(jieba.cut(s)))
        #jieba.load_userdict(project_path + '/data/allentity.csv')
        #print(list(jieba.cut(s)))
        #ans = a.dealWithAsking(s,False)
        #ans = a.classify(s)
        #print(ans)
    








