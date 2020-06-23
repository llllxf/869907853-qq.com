import sys
import os
import numpy as np
import jieba
import urllib.parse
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
# print(project_path)
sys.path.append(project_path)
from data.data_process import read_file
from nlu.analysisPattern import PatternMatch

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
        #self.position_key = ['位于']

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



    def wordBywordAndCheck(self, words):
        """
        逐词比较句子中是否有图谱中的实体，关系，属性
        :param words: 句子
        :return: 抽取的实体，属性，关系
        """

        words_mark = np.zeros(len(words))

        find_common_pro = []
        find_pro = []
        find_entity = []
        pro_index = {}
        com_index = {}
        ins_index = {}

        for i in self.instanceArray:
            if i in words:
                if self.judgeSub(i,find_entity):
                    continue

                instance_index_begin = words.find(i)
                instance_index_end = instance_index_begin+len(i)-1

                for mark_index in range(instance_index_begin,instance_index_end):
                    words_mark[mark_index] = 1
                ins_index[i] = [instance_index_begin,instance_index_end]
                find_entity.append(i)


        for sp in self.standardPro:

            if sp in words:
                #if (sp in find_pro):
                #    continue
                if self.judgeSub(sp,find_pro):
                    continue
                standardpro_index_begin = words.find(sp)
                standardpro_index_end = standardpro_index_begin+len(sp)-1
                if standardpro_index_end > len(words_mark)-1:
                    standardpro_index_end = len(words_mark)-1

                temp_mark = words_mark[standardpro_index_begin:standardpro_index_end]

                if 1 in temp_mark:
                    if temp_mark[0] == 0:
                        words_mark[standardpro_index_end] = 2
                    else:
                        words_mark[standardpro_index_end] = 3
                else:
                    for mark_index in range(standardpro_index_begin, standardpro_index_end):
                        words_mark[mark_index] = 4
                pro_index[sp] = [standardpro_index_begin,standardpro_index_end]
                find_pro.append(sp)


        for n,pro in self.aliasPro.items():

            for p in pro:
                if p in words:
                    if n in find_pro:
                        continue
                    #print(words_mark)

                    aliaspro_index_begin = words.find(p)
                    aliaspro_index_end = aliaspro_index_begin + len(p) - 1
                    if aliaspro_index_end > len(words_mark)-1:
                        aliaspro_index_end = len(words_mark)-1
                    temp_mark = words_mark[aliaspro_index_begin:aliaspro_index_end]

                    #print(p,aliaspro_index_begin,aliaspro_index_end)
                    #print(temp_mark)
                    """
                    if 2 in temp_mark or 3 in temp_mark or 4 in temp_mark:
                        continue
                    """
                    if 1 in temp_mark:

                        if temp_mark[0] == 0:

                            words_mark[aliaspro_index_end] = 2
                        else:
                            words_mark[aliaspro_index_end] = 3
                    else:
                        for mark_index in range(aliaspro_index_begin, aliaspro_index_end):
                            words_mark[mark_index] = 4
                    pro_index[n] = [aliaspro_index_begin,aliaspro_index_end]
                    find_pro.append(n)


        for p in self.commonPro:
            if p in words:
                commonpro_index_begin = words.find(p)
                commonpro_index_end = commonpro_index_begin + len(p) - 1
                temp_mark = words_mark[commonpro_index_begin:commonpro_index_end]
                if commonpro_index_end > len(words_mark)-1:
                    commonpro_index_end = len(words_mark)-1
                if 1 in temp_mark or 2 in temp_mark or 3 in temp_mark or 4 in temp_mark:
                    continue
                else:
                    for mark_index in range(commonpro_index_begin, commonpro_index_end):
                        words_mark[mark_index] = 5
                find_common_pro.append(p)
                com_index[p] = []


        words_mark_bake = list(words_mark[1:])
        words_mark_bake.append(0)


        diff_index = list(np.where(words_mark != words_mark_bake)[0])
        pattern_mark = [words_mark[0]]

        for dif in diff_index[:len(diff_index)-1]:
            pattern_mark.append(words_mark[dif+1])


        """
        blk: blank
        ent: entity
        pro-: 与ent重叠，且重叠部分在前面的属性
        -pro: 与ent重叠，且重叠部分在后面的属性 比如洞庭湖，洞庭湖是ent，但湖是pro，所以是ent-pro
        pro: 没有与ent重叠的属性
        com: 通用属性
        """

        pattern = ""
        for pm in pattern_mark:
            if pm == 0:
                pattern += "blk"
            if pm == 1:
                pattern += "ent"
            if pm == 2:
                pattern += "pro-"
            if pm == 3:
                pattern += "-pro"
            if pm == 4:
                pattern += "pro"
            if pm == 5:
                pattern += "com"
        #print(pattern)

        return pattern,find_entity, find_pro,find_common_pro,ins_index,pro_index,com_index


    def preProcessWords(self, words):
        """
        句子预处理，去掉符号和停用词
        :param words: 句子
        :return: 处理后的句子
        """

        for stop in self.stopword:
            while(stop in words):
                words = words.replace(stop,'')
        for sym in self.symbol:
            while(sym in words):
                words = words.replace(sym,'')

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
        #print("find_entity",find_entity)
        if len(find_entity) > 0:
            for e in find_entity:

                pro_list, rel_list = self.searchByEntity(e)
                ans[e] = {'p': pro_list, 'r': rel_list}
        if ans == {}:
            return None
        else:
            return ans

    def directAnsProName(self,find_pro, entity_deal):
        """
        匹配抽出的属性名称和实体具有的属性名称

        :param find_pro: 抽取的属性
        :param find_rel: 抽取的关系
        :param entity_deal: 携带信息的实体
        :return:
        """

        for name, content in entity_deal.items():
            pro = np.array(content['p'])
            rel = np.array(content['r'])

            for p in pro:
                if p[0] in find_pro:

                    return [name,p[0],p[1]]
            for r in rel:
                if r[0] in find_pro:
                    return [name,r[0],r[1]]

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
            #print(pro)
            #print(rel)

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

        a_entity_pro = []
        for p in entity_pro:
            if common_pro in p[0]:

                a_entity_pro.append(p)
        if a_entity_pro == []:
            return None
        else:
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
            pro = np.array(content['p'])
            rel = np.array(content['r'])



            for c_p in find_pro:

                a_entity_pro = self.judgeProByMatch(c_p,pro)
                if a_entity_pro:
                    common_pro[name] = a_entity_pro
        if common_pro == {}:
            return None
        return common_pro

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
        #print("words",words)
        ans_con=[]
        count_rate=[]
        similar_pro=[]
        pro_rate = []



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
                #print(words)

            for p in pro:
                if p[1] == name:
                    continue

                con =self.preProcessWords(p[1])

                while(name in con):
                    con = con.replace(name,'')

                if len(con)>len(words):
                    c_len = len(words)

                    #cut_word = list(jieba.cut(words))
                    #c_len = len(cut_word)
                    count = self.seacrchAll(con,words)
                else:
                    c_len = len(con)
                    #cut_word = list(jieba.cut(con))
                    #c_len = len(cut_word)
                    count = self.seacrchAll(words,con)

                #print(count,c_len)

                if float(count) / float(c_len) >= 0.65:
                    ans_con.append([name, p[0], p[1]])
                    count_rate.append(count / c_len)
                """
                else:

                    uri = "http://192.168.80.1:8888?target=score"
                    data = json.dumps({"question": words, "pro": con})

                    res = requests.post(uri, data)
                    if '500' in str(res.content):
                        continue

                    score = res.json()['response']
                    if score != "None":
                        score = float(score)
                        #print(pro, words, score)
                        if score > 0.7:
                            pro_rate.append(score)
                            similar_pro.append([name, p[0], p[1]])
                """

            for r in rel:
                if (r[0]=='类型' or r[0]=='部分于' or r[0]=="分类" or r[0]=="下属于"
                        or r[0]=="实体限制" or r[0]=="强相关于" or r[0]=="等同"):
                    continue
                if r[1] ==  name:
                    continue

                con =self.preProcessWords(r[1])

                while (name in con):
                    con = con.replace(name, '')

                if len(con)>len(words):
                    #cut_word = list(jieba.cut(words))
                    c_len = len(words)
                    count = self.seacrchAll(con,words)
                else:
                    #cut_word = list(jieba.cut(con))
                    c_len = len(con)
                    count = self.seacrchAll(words,con)

                if count / c_len >= 0.65:
                    ans_con.append([name, r[0], r[1]])
                    count_rate.append(count / c_len)
                """
                else:
                    uri = "http://192.168.80.1:8888?target=score"
                    data = json.dumps({"question": words, "pro": con})

                    res = requests.post(uri, data)
                    if '500' in str(res.content):
                        continue

                    score = res.json()['response']
                    if score != "None":
                        score = float(score)
                        #print(pro, words, score)
                        if score > 0.7:
                            pro_rate.append(score)
                            similar_pro.append([name, r[0], r[1]])
                """


            if count_rate != []:
                max_index = np.argmax(np.array(count_rate))
                return ans_con[max_index]
            """

            if pro_rate != []:
                max_index = np.argmax(np.array(pro_rate))
                return similar_pro[max_index]
            """
            """
            for r in rel:
                if (r[0]=='类型' or r[0]=='部分于' or r[0]=="分类" or r[0]=="下属于"
                        or r[0]=="实体限制" or r[0]=="强相关于" or r[0]=="等同"):
                    continue
                if r[1] ==  name:
                    continue

                uri = "http://192.168.80.1:8888?target=similar"
                data = json.dumps({"question": words, "pro": r[1]})

                res = requests.post(uri, data)
                similar = float(res.json()['response'])
                if similar > 0.7:
                    pro_rate.append(similar)
                    similar_pro.append([name, r[0], r[1]])
                count = 0
                cut_word = list(jieba.cut(r[1]))
                r_len = len(cut_word)
                for word in cut_word:
                    if word in words:
                        count = count + 1

                if count / r_len >= 0.65:
                    ans_con.append([name, r[0], r[1]])
                    count_rate.append(count / r_len)

            if count_rate != []:
                max_index = np.argmax(np.array(count_rate))
                return ans_con[max_index]

            if pro_rate != []:
                max_index = np.argmax(np.array(pro_rate))
                return similar_pro[max_index]
            """

            return None


    def directAns(self,words,find_entity,find_pro,find_common_pro):
        """
        根据抽取的实体，查找实体的属性信息，根据抽取的属性信息或者问句原文匹配属性值得到回答，即直接根据抽取的实体可得到回答
        :param words: 句子
        :param find_entity: 抽取的实体
        :param find_pro:
        :return:
        """
        """查找实体对应信息"""
        deal_entity = self.dealWithEnitity(find_entity)

        print("deal_entity",deal_entity)




        """抽取的属性可直接查找内容回答"""
        if len(find_pro) > 0:
            print("find_pro",find_pro)

            ans = self.directAnsProName(find_pro, deal_entity)
            if ans != None:
                #print(ans,"bbb")
                return ans[0] + "的" + ans[1] + ": " + ans[2]
            ans = self.directAnsComProName(find_common_pro,deal_entity)
            if ans != None:

                #print("ccc",ans)
                ans_string = ""
                for name,content in ans.items():
                    ans_string += name + "\n"

                    for c in content:

                        form_content = ""
                        for word in c[1]:
                            """
                            用replace和strip都不行
                            """
                            if word != "\n":
                                form_content += word
                        ans_string += c[0]+": "+form_content+"\n"
                    ans_string += "\n"

                return ans_string

        """抽取的属性不可直接回答/没有抽取出属性"""

        ans = self.directAnsProCon(words, deal_entity)
        if ans != None:

            #print(ans,"ddd")
            return ans[0] + "的" + ans[1] + ": " + ans[2]
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
        #print("son_list",son_list)

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
        print("son_list",son_list)

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
            father_list = list(set(father_list))
            print(father_list)
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
        words = self.preProcessWords(words)
        pattern, find_entity, find_pro, find_common_pro, entity_index, pro_index, common_index = self.wordBywordAndCheck(
            words)
        #find_entity, find_pro,find_common_pro = self.wordByword(words)
        for e in find_entity:
            son_list = self.getEntityByType(e)
            if son_list:
                return " ".join(son_list)
        return None


    def dealWithAsking(self, words):
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

        words = self.preProcessWords(words)

        """
        匹配句子与图谱中的实体、属性和关系，抽取出实体、属性和关系
        解析模版
        
        """
        pattern, find_entity, find_pro, find_common_pro, entity_index, pro_index, common_index = self.wordBywordAndCheck(
            words)
        task = self.pattern_match.judgeNlu(pattern)

        print("========================================================")
        print("得到的句子模版: ", pattern)
        print("抽取的实体: ", find_entity, "\t实体及其在句子中的下标: ", entity_index)
        print("抽取的属性或关系: ", find_pro, "\t属性及其在句子中的下标: ", pro_index)
        print("抽取的通用属性或关系: ", find_common_pro, "\t通用属性及其在句子中国的下标: ", common_index)
        print("任务类型: ", task)
        print("========================================================")

        if task == 'task_difinition':
            ans = self.ansDefinition(find_entity[0])
            print(ans, "ansDefinition")
            return ans

        elif task == 'task_common':

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
        elif task == "task_rel":
            father_dict = {}

            entity_for_sort = []
            for e in find_entity:
                entity_for_sort.append([e,entity_index[e][0]])

            entity_for_sort = sorted(entity_for_sort, key=lambda i: i[1])

            for se in entity_for_sort:

                father = self.getFatherByType(se[0])
                father_dict[se[0]] = father

            judged_rel,formed_entity = self.pattern_match.judgeRel(father_dict,entity_for_sort)
            print(judged_rel,formed_entity)

            if judged_rel == 'task_same_level' or (judged_rel == 'task_position_limit' and len(formed_entity)>2):
                combine_ans = ""
                for se in formed_entity:
                    find_entity_branch = [se]
                    ans = self.directAns(words, find_entity_branch, find_pro, find_common_pro)
                    if ans != None:
                        combine_ans+=ans
                        print(ans, "directAns")
                        continue

                    ans = self.downFindAns(words, find_entity_branch, find_pro, find_common_pro)
                    if ans != None:
                        combine_ans += ans
                        print(ans, "downFindAns")
                        continue

                    ans = self.upFindAns(words, find_entity_branch, find_pro, find_common_pro)
                    if ans != None:
                        combine_ans += ans
                        print(ans, "upFindAns")
                        continue
                if combine_ans != "":
                    return combine_ans

            elif judged_rel == 'task_position_limit' and len(formed_entity)<=1:
                """
                考虑实体限制
                """
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
                """
                for ent in entity_for_sort[1:]:

                    find_entity_branch = [ent[0]]
                    print(find_entity_branch, find_pro)
                    deal_entity = self.dealWithEnitity(find_entity_branch)
                    cont = self.positionControl(deal_entity)
                    print("ans",cont)

                    if (cont is not None and entity_for_sort[0][0] not in cont):
                        continue

                    print(find_entity_branch,find_pro)

                    ans = self.directAns(words, find_entity_branch, find_pro, find_common_pro)
                    if ans != None:
                        print(ans, "directAns")
                        return ans
                    ans = self.downFindAns(words, find_entity_branch, find_pro, find_common_pro)
                    if ans != None:
                        print(ans, "downFindAns")
                        return ans
                    ans = self.upFindAns(words, find_entity_branch, find_pro, find_common_pro)
                    if ans != None:
                        print(ans, "upFindAns")
                        return ans
                """

            elif judged_rel is None:
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
        elif task == 'task_btw_ent':
            ent_a = find_entity[0]
            ent_b = find_entity[1]
            father_list_a = self.getFatherByType(ent_a)
            father_list_b = self.getFatherByType(ent_b)

            temp_list = father_list_a
            temp_ent = ent_a
            if len(father_list_a) > len(father_list_b):
                father_list_a = father_list_b
                father_list_b = temp_list
                ent_a = ent_b
                ent_b = temp_ent

            ans_list = self.getRel(ent_a, ent_b)

            ans_tring = ""
            for al in ans_list:
                ans_tring += ent_a
                for a in al:
                    ans_tring += ("的" + a)
                ans_tring += ("是" + ent_b+"\n")
            return ans_tring

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
    while (1):
        s = input()
        ans = a.dealWithAsking(s)
        print(ans)
    








