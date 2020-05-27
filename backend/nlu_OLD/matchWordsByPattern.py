import sys
import os
import numpy as np
import jieba
import urllib.parse
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)
from data.data_process import read_file
from nlu.patternAnalysis import PatternMatch
from nlu.LTPUtil import LTPUtil

import requests, json

class matchWordsByPattern(object):
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
        self.pattern_match = PatternMatch()
        self.ltp_util = LTPUtil()

        self.instanceArray = list(set(read_file(project_path + "/data/allentity.csv")))
        self.instanceArray = sorted(self.instanceArray, key=lambda i: len(i), reverse=True)



        proArray = read_file(project_path + "/data/pro.csv")
        proArray = sorted(proArray, key=lambda i: len(i.split(":")[0]), reverse=True)

        self.standardPro = []
        self.commonPro = []
        self.aliasPro = {}

        self.stopword = ["为什么","什么","如何","谁","多少","几","怎么着","怎么样","怎么","怎样","怎的","怎",
                        "哪里","哪儿","哪","吗","呢","吧","啊","么"]
        self.symbol = [",","，",".","。","!","！","@","#","$",
                         "%","^","&","*","(","（",")","）","{","「","}","」","[","]","【","】","、","\\","|",";",
                       "；","<",">","?","？","`","~","·","～","：",":","*"]

        jieba.load_userdict(project_path + "/data/allentity.csv")
        jieba.load_userdict(project_path + "/data/pro.csv")
        jieba.load_userdict(project_path + "/data/jieba_other.csv")


        for p in proArray:
            temp_standard = p.split(":")
            self.standardPro.append(temp_standard[0])
            if temp_standard[1] != '':
                temp_alias = temp_standard[1].split(",")
                if temp_alias[0] != '':
                    if temp_alias[0] in self.commonPro:
                        continue
                    self.commonPro.append(temp_alias[0])
                if len(temp_alias)>1 and temp_alias[1] != '':
                        self.aliasPro[temp_standard[0]]= temp_alias[1:]

    def wordBywordAndCheck(self, cut_words):
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

        #cut_words = list(jieba.cut(words))
        words_mark = np.zeros(len(cut_words))

        for c_index in range(len(cut_words)):

            cw = cut_words[c_index]
            if cw in self.instanceArray:
                if self.judgeSub(cw,find_entity):
                    continue
                words_mark[c_index]=1
                ins_index[cw]=c_index
                find_entity.append(cw)

            if cw in self.standardPro:
                if self.judgeSub(cw,find_pro):
                    continue
                if words_mark[c_index]==1:
                    words_mark[c_index]=3
                    find_pro.append(cw)
                    pro_index[cw]=c_index
                elif words_mark[c_index]>0:
                    continue
                else:
                    words_mark[c_index]=2
                    find_pro.append(cw)
                    pro_index[cw] = c_index

            for n,pro in self.aliasPro.items():
                if cw in pro:
                    if self.judgeSub(n,find_pro):
                        continue
                    if words_mark[c_index] == 1:
                        words_mark[c_index] = 3
                        find_pro.append(n)
                        pro_index[n] = c_index
                    elif words_mark[c_index] > 0:
                        continue
                    else:
                        words_mark[c_index] = 2
                        find_pro.append(n)
                        pro_index[n] = c_index

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

        pattern = ""
        for wm in words_mark[:-1]:

            #if wm == 0:
            #    pattern += "blk"
            if wm == 1:
                pattern += "ent"
            if wm == 2:
                pattern += "pro"
            if wm == 3:
                pattern += "ent-pro"
            if wm == 4:
                pattern += "com"
            pattern+="#"
        if words_mark[len(words_mark)-1] == 1:
            pattern += "ent"
        if words_mark[len(words_mark)-1] == 2:
            pattern += "pro"
        if words_mark[len(words_mark)-1] == 3:
            pattern += "ent-pro"
        if words_mark[len(words_mark)-1] == 4:
            pattern += "com"

        return pattern,find_entity, find_pro,find_common_pro,ins_index,pro_index,com_index


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

    def searchByEntity(self, entity):
        """
        根据标签分别查找该标签对应的属性和关系信息(同名实体一起)

        :param entity: 实体标签
        :return: 属性列表，关系列表
        """

        """获取属性信息"""
        uri = "http://127.0.0.1:8004/getEntityByLabelWithPro?repertoryName=geo&entityName=" + entity
        r = requests.post(uri)
        pro_list = list(r.json())

        """获取关系信息"""
        uri = "http://127.0.0.1:8004/getEntityByLabelWithRel?repertoryName=geo&entityName=" + entity
        r = requests.post(uri)
        rel_list = list(r.json())
        return pro_list, rel_list

    def dealWithEnitity(self, find_entity):
        """
        根据实体list查找图谱中该标签的实体的信息(同名实体一起)

        :param words: 句子
        :param find_entity: 抽取的实体
        :return: 返回实体具体信息（属性和关系）或 None

        """
        ans = {}
        if len(find_entity) > 0:
            for e in find_entity:

                pro_list, rel_list = self.searchByEntity(e)
                ans[e] = {'p': pro_list, 'r': rel_list}
        if ans == {}:
            return None
        else:
            return ans

    def directAnsProName(self,property, entity_deal):
        """
        匹配抽出的属性名称和实体具有的属性名称

        :param find_pro: 抽取的属性
        :param find_rel: 抽取的关系
        :param entity_deal: 携带信息的实体
        :return:
        """
        ans = {}

        for name, content in entity_deal.items():
            name_dict = {}
            pro = np.array(content['p'])
            rel = np.array(content['r'])

            for p in pro:
                if p[0] in property:

                    if p[0] in name_dict.keys():
                        name_dict[p[0]].append(p[1])
                    else:
                        name_dict[p[0]] = [p[1]]
            for r in rel:
                if r[0] in property:

                    if r[0] in name_dict.keys():
                        name_dict[r[0]].append(r[1])
                    else:
                        name_dict[r[0]] = [r[1]]
            if name_dict != {}:
                ans[name]=name_dict

        if ans == {}:
            return None
        else:
            return [ans]

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

    def test(self):
        uri = "http://192.168.80.1:8888?target=similar"
        data=json.dumps({"question":"","pro":""})

        r = requests.post(uri,data)
        ans = r.json()['response']

        return ans


    def seacrchAll(self,longWords,shortWords):
        """

        :param longWords: 问句和属性值中较长的一方
        :param shortWords: 较短的一方
        :return: 较短的那方匹配情况
        """
        count = 0.
        for sw in shortWords:
            if sw in longWords:
                count = count+1
        return count



    def directAnsProCon(self, words, deal_entity):
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


        ans_con=[]
        count_rate=[]

        for name,content2 in deal_entity.items():

            """
            抽取出的实体的属性
            """
            pro = np.array(content2['p'])
            rel = np.array(content2['r'])

            #print(name,pro,rel)
            """
            去掉问题中的实体方便匹配
            """

            while (name in words):
                words = words.replace(name,'')
            if words == "":
                continue

            for p in pro:

                """
                类似与标签的属性
                """
                if p[1] == name:
                    continue
                if '分类' in p[0]:
                    continue

                con =self.preProcessWords(p[1])

                while(name in con):
                    con = con.replace(name,'')

                if len(con)>len(words):
                    c_len = len(words)
                    #print(con,words,"1")
                    count = self.seacrchAll(con,words)
                else:
                    #print(con, words,"2")
                    c_len = len(con)
                    count = self.seacrchAll(words,con)
                #print(count,c_len)
                if float(count) / float(c_len) >= 0.65:
                    if len(con)>=3*len(words):
                        continue
                    ans_con.append([name, p[0], p[1]])
                    count_rate.append(count / c_len)
                #print(words)

        if count_rate != []:
            #max_index = np.argmax(np.array(count_rate))
            return [ans_con,count_rate]

        return None


    def directAns(self,words,find_entity,find_pro,find_common_pro):
        """
        根据抽取的实体，查找实体的属性信息，根据抽取的属性信息或者问句原文匹配属性值得到回答，即直接根据抽取的实体可得到回答
        :param words: 句子
        :param find_entity: 抽取的实体
        :param find_pro:
        :return:
        """

        deal_entity = self.dealWithEnitity(find_entity)
        print("抽取的实体信息:",deal_entity)
        print("========================================================")

        """抽取的属性可直接查找内容回答"""
        if len(find_pro) > 0:
            ans = self.directAnsProName(find_pro, deal_entity)

            if ans != None:
                #print(ans)
                return ans
        if len(find_common_pro)>0:

            ans = self.directAnsComProName(find_common_pro,deal_entity)
            if ans != None:
                #print(ans)
                return ans

        """抽取的属性不可直接回答/没有抽取出属性"""

        ans = self.directAnsProCon(words, deal_entity)

        if ans != None:
            return ans
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

    def downFindAns(self, words, find_entity, find_pro,find_common_pro):
        """
        查找抽取的实体的子类，匹配属性或属性内容来得到答案

        :param words: 句子
        :param find_entity: 实体
        :param find_pro: 属性和关系
        :param find_common_pro: 通用实体和关系
        :return: 回答或空
        """
        for e in find_entity:
            son_list = self.getEntityByType(e)
            #print(son_list)
            if son_list:
                ans = self.directAns(words,son_list,find_pro,find_common_pro)
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
        pattern, find_entity, find_pro, find_common_pro, entity_index, pro_index, common_index = self.wordBywordAndCheck(
            cut_words)
        #find_entity, find_pro,find_common_pro = self.wordByword(words)
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

    def dealWithQuesType(self,task,words,find_entity,find_pro,find_common_pro):
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
            ans = self.ansDefinition(find_entity[0])
            print(ans, "ansDefinition")
            return [{find_entity[0]:{'介绍':[ans]}}]

        elif task != None:

            ans = self.directAns(words, find_entity, find_pro, find_common_pro)
            if ans != None:
                print(ans, "directAns")
                return ans
            ans = self.downFindAns(words, find_entity, find_pro, find_common_pro)
            if ans != None:
                print(ans, "downFindAns")
                return ans
            ans = self.upFindAns(words, find_entity, find_pro, find_common_pro)
            if ans != None:
                print(ans, "upFindAns")
                return ans

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
            #print("values", values)

            if self.judgeSub(SBV, [values]):
                hed_content_ans.append({name: content})
        if hed_name_ans!=[] or hed_content_ans!=[]:
            return hed_name_ans,hed_content_ans

        for name, content in answern.items():

            if VOB in name:
                hed_name_ans.append({name: content})
            conv = list(content.values())[0]
            values = "".join(conv)
            #print("values", values)

            if self.judgeSub(VOB, [values]):
                hed_content_ans.append({name: content})

        return hed_name_ans,hed_content_ans

    def getEntByfuzzySearch(self,words):

        uri = "http://127.0.0.1:8004/fuzzySearch?repertoryName=geo&words=" + words
        r = requests.post(uri)
        ent_list = list(r.json())

        return ent_list

    def hedAnswerForProMatch(self,answern,rate,cut_words,arcs_dict,hed_index):
        """
        提取问句中的关键信息，通过关键信息与回答集的匹配得到更精确的回答集，适用于匹配属性值得到回答集的情况

        :param answern:回答集
        :param rate:每一条回答的概率（通过属性匹配得到）
        :param cut_words:问句分词
        :param arcs_dict:依存树
        :param hed_index:关键词下标
        :return:更精确的回答集以及对应的概率，关键属性（有歧义）
        """
        hed_name_ans = []
        hed_content_ans = []
        hed_rate_name = []
        hed_rate_cont = []
        hed_keys = arcs_dict[hed_index].keys()
        SBV = ""
        VOB = ""
        ATT = ""

        if 'SBV' in hed_keys:
            SBV = cut_words[arcs_dict[hed_index]['SBV'][0]]
            if SBV in self.stopword:
                SBV = ""

            elif 'ATT' in arcs_dict[arcs_dict[hed_index]['SBV'][0]].keys():
                ATT = cut_words[arcs_dict[arcs_dict[hed_index]['SBV'][0]]['ATT'][-1]]
                if ATT in self.stopword:
                    ATT = ""
        if SBV == "":
            SBV = cut_words[hed_index]
            if 'ATT' in arcs_dict[hed_index].keys():
                ATT = cut_words[arcs_dict[hed_index]['ATT'][-1]]
                if ATT in self.stopword:
                    ATT = ""

        if 'VOB' in hed_keys:
            VOB = cut_words[arcs_dict[hed_index]['VOB'][0]]
            if VOB in self.stopword:
                VOB = ""
        if ATT == "" and VOB != "":
            if 'ATT' in arcs_dict[arcs_dict[hed_index]['VOB'][0]].keys():
                ATT = cut_words[arcs_dict[arcs_dict[hed_index]['VOB'][0]]['ATT'][-1]]
                if ATT in self.stopword:
                    ATT = ""
        print("ATT",ATT,SBV,VOB)
        #print(answern)

        index = 0

        for name, pro_name, content in answern:
            #print(name, pro_name, content,"---------1")
            """
            if SBV in name:
                hed_name_ans.append([name,pro_name,content])
                hed_rate_name.append(rate[index])
                print("hed_name_ans1",hed_name_ans,hed_rate_name)
            """

            if self.judgeSub(SBV, [content]) and self.judgeSub(VOB, [content]) and self.judgeSub(ATT,[content]):
                hed_content_ans.append([name,pro_name,content])
                hed_rate_cont.append(rate[index])
                #print("hed_name_ans2", hed_name_ans, hed_rate_name)

            index = index+1
        """
        if hed_name_ans == []:
            return [],[],[],[],""
        """

        #if hed_name_ans != [] or hed_content_ans != []:
        #    return hed_name_ans,hed_rate_name,hed_content_ans,hed_rate_cont,ATT
        """
        #index = 0
        

        #for name, pro_name, content in answern:
            
            if VOB in name:
                hed_name_ans.append([name,pro_name,content])
                hed_rate_name.append(rate[index])
                #print("hed_name_ans",hed_name_ans,hed_rate_name)
            

            #if self.judgeSub(VOB, [content]) and self.judgeSub(ATT,[content]):
            #    hed_content_ans.append([name,pro_name,content])
            #    hed_rate_cont.append(rate[index])

            #index = index+1
        """
        return hed_name_ans,hed_rate_name,hed_content_ans,hed_rate_cont,ATT

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

            tlp_pattern, arcs_dict, postags, hed_index = self.ltp_util.get_sentence_pattern(cut_words)
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




    def dealWithAsking(self, words, reverse):
        """
        1.抽取句子中的实体，属性，关系
        2.如果抽取的实体和句子等同，那么回答定义问题
        3.得到抽取的实体的属性和关系值
        4.处理问句
           1.如果句子匹配到实体，根据实体对应的属性和关系来匹配
           2.如果句子匹配到实体但没有匹配到属性，则匹配属性的值
           3.如果句子存在找到的实体但没有匹配1和2，且句子中的实体存在下一级实体，则查找下一级，执行1和的2步骤（逐级查找-层级）

        :param words:句子
        :return: 回答或None
        """
        cut_words = list(jieba.cut(words))
        words = self.preProcessWords(words)

        """
        匹配句子与图谱中的实体、属性和关系，抽取出实体、属性和关系
        解析模版
        
        """

        tlp_pattern, arcs_dict, postags, hed_index = self.ltp_util.get_sentence_pattern(cut_words)
        postags = list(postags)

        pattern, find_entity, find_pro, find_common_pro, entity_index, pro_index, common_index = self.wordBywordAndCheck(
            cut_words)
        task = self.pattern_match.judgeNlu(pattern)

        if reverse:
            find_entity = self.dealWithWordsWithoutEnt(cut_words,arcs_dict,hed_index)

        print("========================================================")
        print("分词: ",cut_words)
        print("得到的句子模版: ", pattern)
        print("抽取的实体: ", find_entity, "\t实体及其在句子中的下标: ", entity_index)
        print("抽取的属性或关系: ", find_pro, "\t属性及其在句子中的下标: ", pro_index)
        print("抽取的通用属性或关系: ", find_common_pro, "\t通用属性及其在句子中国的下标: ", common_index)
        print("句法依存树: ", arcs_dict,hed_index)
        print("词性分析: ",postags)
        print("任务类型: ", task)
        print("========================================================")


        ans = self.dealWithQuesType(task,words,find_entity,find_pro,find_common_pro)
        """
        if reverse:
            print(ans)
            pass
        else:
        """
        if True:

            use_entity = []
            unuse_ent = []
            select_pro = []
            select_rate = []

            if ans == None:
                return None
            if len(ans) == 2:
                print("==================属性值匹配===================2")
                answern = ans[0]
                rate = ans[1]
                formed_name_ans = []
                formed_cont_ans = []


                for name, pro_name, pro in answern:
                    #print("answern???",answern,name,pro_name,pro)
                    """得到多实体回答问题"""
                    if name in cut_words:
                        formed_name_ans.append({name:{pro_name:[pro]}})
                if formed_name_ans != []:
                    return formed_name_ans
                """
                for ent_name, pro_name, pro in answern:
                    if ent_name in words:
                        use_entity.append(ent_name)
                """
                for fe in find_entity:
                    if fe not in words:
                        continue

                    father = self.getFatherByType(fe)
                    if father == None:
                        continue
                    if "国家" in father or "城市" in father or '省' in father:
                        unuse_ent.append(fe)

                if '中国' in unuse_ent:
                    unuse_ent.append("我国")
                c_index = 0


                for ent_name, pro_name, pro in answern:
                    if unuse_ent == []:
                        continue
                    if self.checkPosition(ent_name, unuse_ent):
                        select_pro.append([ent_name, pro_name, pro])
                        select_rate.append(rate[c_index])
                    c_index = c_index + 1
                print("select_pro",select_pro)
                if unuse_ent == []:
                    select_pro = answern
                    select_rate = rate
                #if len(select_pro) == 1:
                #    return [{select_pro[0]: {select_pro[1]: [select_pro[2]]}}]

                """
                if select_rate != []:
                    max_index = np.argmax(np.array(select_rate))
                    max_ans = select_pro[max_index]
                    return [{max_ans[0]: {max_ans[1]: [max_ans[2]]}}]
                """

                hed_name_ans, hed_rate_name,hed_content_ans,hed_rate_cont,ATT = self.hedAnswerForProMatch(select_pro, select_rate,cut_words, arcs_dict, hed_index)

                """
                if hed_name_ans != []:
                    max_index = np.argmax(np.array(hed_rate_name))
                    max_ans = hed_name_ans[max_index]
                    return [{max_ans[0]: {max_ans[1]: [max_ans[2]]}}]
                """

                """
                有歧义选项，则询问具体是哪种att
                """
                print("hed_content_ans",hed_content_ans,ATT)
                if hed_content_ans != [] and ATT!="":

                    sbv_arr = self.askingBackByConAtt(hed_content_ans,ATT)
                    if sbv_arr:
                        return hed_content_ans,sbv_arr,hed_rate_cont,ATT,"hed_content_ans"

                """
                有歧义选项，则询问具体是哪种att
                """
                if hed_content_ans != []:
                    max_index = np.argmax(np.array(hed_rate_cont))
                    max_ans = hed_content_ans[max_index]

                    return [{max_ans[0]: {max_ans[1]: [max_ans[2]]}}]

                """
                max_index = np.argmax(np.array(rate))
                max_ans = answern[max_index]
                return [{max_ans[0]: {max_ans[1]: [max_ans[2]]}}]
                """
                return None

            else:
                """
                通过直接匹配属性得到结果，但结果可能有多条，所以需要再次筛选
                """
                print("==================属性名匹配===================")
                answern = ans[0]
                print("answern",answern)
                """
                如果结果只有一个实体那么就返回这个实体
                实际上问题问的可能就是多个实体，如果返回的实体不止一个
                
                1. 匹配回答中的实体，如果出现在句子中，那么这个结果被认为是正确答案
                2. 匹配回答中的属性值，如果属性值出现了抽取的实体，那么
                
                """

                if len(answern.keys()) == 1:
                    print(answern.keys())
                    return ans
                formed_name_ans = []
                formed_cont_ans = []

                for name, content in answern.items():
                    """得到多实体回答问题"""
                    if name in words:
                        formed_name_ans.append({name: content})

                    for fe in find_entity:
                        con_values = list(content.values())[0]
                        values = "".join(con_values)
                        if self.judgeSub(fe, [values]):
                            formed_cont_ans.append({name: content})


                if formed_name_ans != []:
                    print("formed_name_ans", formed_name_ans)
                    return formed_name_ans

                hed_name_ans, hed_content_ans = self.hedAnswer(answern,cut_words,arcs_dict,hed_index)

                if hed_name_ans != []:
                    print("hed_name_ans", hed_name_ans)
                    return hed_name_ans
                if hed_content_ans != []:
                    print("hed_content_ans", hed_content_ans)

                    return hed_content_ans
                print("ans", ans)
                return ans

        return None



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
    a = matchWordsByPattern()
    #ans = a.dealWithAsking("中国最大的淡水湖是鄱阳湖吗")
    #print(ans)



    while (1):

        print("user:")
        s = input()
        #ans = a.wordBywordAndCheck(s)

        #print(list(jieba.cut(s)))
        #jieba.load_userdict(project_path + '/data/allentity.csv')
        #print(list(jieba.cut(s)))
        #ans = a.dealWithAsking(s)
        ans = a.dealWithAsking(s,True)
        print(ans)
    








