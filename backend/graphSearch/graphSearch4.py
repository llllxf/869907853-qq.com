# @Language: python3
# @File  : graphSearch.py
# @Author: LinXiaofei
# @Date  : 2020-05-01
"""

"""


import sys
import os
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)



from nlu.formWords import formWords

import requests,json
import numpy as np



class graphSearch(object):

    def __init__(self):
        self.form_util = formWords()

    def getRelByType(self,type):
        """
        获得某个类型的实体的所有属性
        :param type:
        :return:
        """
        uri = "http://10.10.1.202:8004/getRelByType?repertoryName=geo3&type="+type
        r = requests.post(uri)
        rel_list = list(r.json())

        return rel_list

    def getProByType(self,type):
        """
        获得某个类型的实体的所有属性
        :param type:
        :return:
        """
        uri = "http://10.10.1.202:8004/getProByType?repertoryName=geo3&type="+type
        r = requests.post(uri)
        pro_list = list(r.json())

        return pro_list

    def getPredicate(self,label):
        """
        通过标签得到原始谓词
        :param label:
        :return:
        """

        uri = "http://10.10.1.202:8004/getProPredicate?repertoryName=geo3&label="+label
        r = requests.post(uri)
        ans = list(r.json())
        if len(ans)>0:
            predicate = list(r.json())[0]
            return predicate
        return None

    def getRelPredicate(self,label):
        """
        通过标签得到原始谓词
        :param label:
        :return:
        """
        uri = "http://10.10.1.202:8004/getRelPredicate?repertoryName=geo3&label="+label
        r = requests.post(uri)
        predicate = list(r.json())[0]

        return predicate

    def getSubject(self, label):
        """
        通过标签得到原始主语/宾语
        :param label:
        :return:
        """
        uri = "http://10.10.1.202:8004/getSubject?repertoryName=geo3&label=" + label
        # print("label",label)
        r = requests.post(uri)
        subject = list(r.json())
        if subject is not None and len(subject) > 0:
            return subject[0]
        return None

    def getValueByPro(self,type,property):
        """
        该类型实体的某一属性对应的值
        :param type:
        :param property:
        :return:
        """
        uri = "http://10.10.1.202:8004/getValueByPro?repertoryName=geo3&entityType=" + type+"&property="+property
        r = requests.post(uri)
        value_list = list(r.json())
        return value_list

    def resetTripleToRepertory(self,data):
        """
        重置属性
        :param data:
        :return:
        """
        uri = "http://10.10.1.202:8004/resetTripleToRepertory?"
        ret = requests.post(uri, data=data)
        print(ret)

    def resetRelTripleToRepertory(self,data):
        """
        重置属性到关系
        :param data:
        :return:
        """
        uri = "http://10.10.1.202:8004/resetRelTripleToRepertory?"
        ret = requests.post(uri, data=data)
        print(ret)

    def getValueByRel(self,type,property):
        """
        该类型实体的某一关系对应的值
        :param type:
        :param property:
        :return:
        """
        uri = "http://10.10.1.202:8004/getValueByRel?repertoryName=geo3&entityType=" + type+"&relation="+property
        r = requests.post(uri)
        value_list = list(r.json())
        return value_list

    def addTripleToRepertory(self,tripleList):
        """
        添加属性(现有)
        :param subj:
        :param pred:
        :param obje:
        :return:
        """

        data = {'repertoryName': 'geo3', 'tripleList': str(tripleList)}
        uri = "http://10.10.1.202:8004/addTripleToRepertory?"
        ret = requests.post(uri, data=data)
        print(ret)

    def addRelTripleToRepertory(self,tripleList):
        """
        添加属性(现有)
        :param subj:
        :param pred:
        :param obje:
        :return:
        """
        data = {'repertoryName': 'geo3', 'tripleList': str(tripleList)}
        uri = "http://10.10.1.202:8004/addRelToRepertory?"
        ret = requests.post(uri, data=data)
        print(ret)

    def deleteTripleToRepertory(self,tripleList):
        """
        添加属性(现有)
        :param subj:
        :param pred:
        :param obje:
        :return:
        """

        data = {'repertoryName': 'geo3', 'tripleList': str(tripleList)}
        uri = "http://10.10.1.202:8004/deleteTripleToRepertory?"
        ret = requests.post(uri, data=data)
        print(ret)

    def deleteRelToRepertory(self,tripleList):
        """
        添加属性(现有)
        :param subj:
        :param pred:
        :param obje:
        :return:
        """
        data = {'repertoryName': 'geo3', 'tripleList': str(tripleList)}
        uri = "http://10.10.1.202:8004/deleteRelToRepertory?"
        ret = requests.post(uri, data=data)
        print(ret)

    def deleteProperty(self,label):

        propertyUri = self.getPredicate(label)
        print(propertyUri)
        data = {'repertoryName': 'geo3', 'propertyUri': propertyUri}
        uri = "http://10.10.1.202:8004/deleteCurProperty?"
        ret = requests.post(uri,data=data)
        print(ret)

    def deleteRelation(self,label):

        propertyUri = self.getRelPredicate(label)
        print(propertyUri)
        data = {'repertoryName': 'geo3', 'propertyUri': propertyUri}
        uri = "http://10.10.1.202:8004/deleteCurProperty?"
        ret = requests.post(uri,data=data)
        print(ret)

    def addProperty(self,propertyName,pinyinName):

        data = {'repertoryName': 'geo3', 'propertyName': propertyName, 'pinyinName':pinyinName}
        uri = "http://10.10.1.202:8004/addProperty?"
        ret = requests.post(uri, data=data)
        print(ret)

    def addRelation(self, relationName, pinyinName):

        data = {'repertoryName': 'geo3', 'relationName': relationName, 'pinyinName': pinyinName}
        uri = "http://10.10.1.202:8004/addRelation?"
        ret = requests.post(uri, data=data)
        print(ret)

    def deleteTripleBySAP(self,subject,predicate):

        data = {'repertoryName': 'geo3', 'subject': subject, 'predicate': predicate}
        uri = "http://10.10.1.202:8004/deleteTripleBySAP?"
        ret = requests.post(uri, data=data)
        print(ret)



    #======================================self modify=========================================
    def completionGraph(self, ent, type):

        uri = "https://api.ownthink.com/kg/knowledge?entity=" + ent
        r = requests.post(uri)

        if r.json()['message'] == 'success':
            print(r.json())
            ans_dict = dict(r.json()['data'])
            # print(ans_dict)
            if 'avp' in ans_dict.keys():
                inf_dict = dict(r.json()['data']['avp'])

                return inf_dict
        return None

    # ======================================pedia modify=========================================





    def getEntByfuzzySearch(self, words):
        """
        模糊查询属性值得到实体

        :param words:
        :return:
        """

        uri = "http://10.10.1.202:8004/fuzzySearch?repertoryName=geo3&words=" + words
        r = requests.post(uri)
        ent_list = list(r.json())

        return ent_list

    def searchByEntity(self, entity):
        """
        根据标签分别查找该标签对应的属性和关系信息(同名实体一起)

        :param entity: 实体标签
        :return: 属性列表，关系列表
        """

        """获取属性信息"""
        uri = "http://10.10.1.202:8004/getEntityByLabelWithPro?repertoryName=geo3&entityName=" + entity
        r = requests.post(uri)
        pro_list = list(r.json())

        """获取关系信息"""
        uri = "http://10.10.1.202:8004/getEntityByLabelWithRel?repertoryName=geo3&entityName=" + entity
        r = requests.post(uri)
        rel_list = list(r.json())
        return pro_list, rel_list

    def searchEntityProName(self, entity):
        """
        根据标签分别查找该标签对应的属性和关系信息(同名实体一起)

        :param entity: 实体标签
        :return: 属性列表，关系列表
        """

        """获取属性信息"""
        uri = "http://10.10.1.202:8004/getEntityByLabelWithProName?repertoryName=geo3&entityName=" + entity
        r = requests.post(uri)
        pro_list = list(r.json())
        return pro_list

    def dealWithEnitity(self, entity):
        """
        根据实体list查找图谱中该标签的实体的信息(同名实体一起)
        :param find_entity: 抽取的实体
        :return: 返回实体具体信息（属性和关系）或 None

        """
        ans = {}
        if len(entity) > 0:
            for e in entity:
                pro_list, rel_list = self.searchByEntity(e)
                ans[e] = {'p': pro_list, 'r': rel_list}
                print("抽取的实体: ", e,ans[e])
        if ans == {}:
            return None
        else:
            return ans

    def dealWithEnitityPro(self, entity):
        """
        根据实体list查找图谱中该标签的实体的信息(同名实体一起)
        :param find_entity: 抽取的实体
        :return: 返回实体具体信息（属性和关系）或 None

        """
        ans = {}
        if len(entity) > 0:
            for e in entity:
                pro_list = self.searchEntityProName(e)
                ans[e] = pro_list
        if ans == {}:
            return None
        else:
            return ans

    def directAnsByProName(self,entity, property):
        """
        匹配抽出的属性名称和实体具有的属性名称

        :param find_pro: 抽取的属性
        :param find_rel: 抽取的关系
        :param entity_deal: 携带信息的实体
        :return:
        """
        entity_deal = self.dealWithEnitity(entity)

        ans = {}

        for name, content in entity_deal.items():
            name_dict = {}
            pro = np.array(content['p'])


            for p in pro:
                if p[0] in property:

                    if p[0] in name_dict.keys():
                        name_dict[p[0]].append(p[1])
                    else:
                        name_dict[p[0]] = [p[1]]

            if name_dict != {}:
                ans[name]=name_dict

        if ans == {}:
            return None
        else:
            return ans

    def directAnsByRelName(self,entity, property):
        """
        匹配抽出的关系名称和实体具有的关系名称

        :param find_pro: 抽取的属性
        :param find_rel: 抽取的关系
        :param entity_deal: 携带信息的实体
        :return:
        """
        entity_deal = self.dealWithEnitity(entity)


        ans = {}

        for name, content in entity_deal.items():

            name_dict = {}

            rel = np.array(content['r'])
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
            return ans

    def getProList(self, entity):
        """
        得到一个实体的属性关系名称
        :param entity: 实体名称
        :return: 实体的属性/关系名
        """

        uri = "http://10.10.1.202:8004/getPro?repertoryName=geo3&entity=" + entity
        r = requests.post(uri)
        pro_list = list(r.json())

        if pro_list == []:
            return None

        return pro_list

    def getProByLabel(self,label):
        """
        获得某个类型的实体的所有属性
        :param type:
        :return:
        """
        uri = "http://10.10.1.202:8004/getProByLabel?repertoryName=geo3&label="+label
        r = requests.post(uri)
        pro_list = list(r.json())

        return pro_list

    def getRelList(self, entity):
        """
        得到一个实体的属性关系名称
        :param entity: 实体名称
        :return: 实体的属性/关系名
        """

        uri = "http://10.10.1.202:8004/getRel?repertoryName=geo3&entity=" + entity
        r = requests.post(uri)
        rel_list = list(r.json())

        if rel_list == []:
            return None

        return rel_list

    def getEntityByType(self, etype):
        """
        得到实体的子类
        :param entity: 实体
        :return: 实体子类
        """

        """获取子类"""
        uri = "http://10.10.1.202:8004/getEntityByType?repertoryName=geo3&entityName=" + etype
        r = requests.post(uri)
        son_list = list(r.json())

        if son_list == []:
            return None

        return son_list

    def getFatherByType(self, entity):
        """
        得到实体的父类
        :param entity: 实体
        :return: 实体父类
        """

        """获取父类"""
        uri = "http://10.10.1.202:8004/getFatherByType?repertoryName=geo3&entityName=" + entity
        r = requests.post(uri)
        father_list = list(r.json())

        if father_list == []:
            return None
        return father_list

    def getEntityByRel(self, entity,property,keyword):
        """
        根据关系名和关系值，得到实体，并受限于实体类型
        :param entity: 实体类系
        :param property: 关系名
        :param keyword: 关系值
        :return: 实体列表
        """

        uri = "http://10.10.1.202:8004/entitySearch?repertoryName=geo3&entity="+entity+"&relation="+property+"&type="+keyword
        r = requests.post(uri)
        son_list = list(r.json())
        print("son_list",son_list)

        if son_list == []:
            return None

        return son_list

    def downFindAnsByRel(self, entity,property,keyword):
        ans = self.getEntityByRel(keyword[0],property[0],entity[0])
        if ans != None:
            return ans
        return None



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

    def directAnsProConWithPro(self, words, deal_entity,property):
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

        form_words = self.form_util.preProcessWords(words)
        ans_con = []
        count_rate = []


        for name, content in deal_entity.items():
            """
            抽取出的实体的属性
            """
            pro = np.array(content['p'])

            """
            去掉问题中的实体方便匹配
            """
            while (name in form_words):
                form_words = form_words.replace(name, '')

            for p in pro:
                if p[0] != property[0]:
                    continue
                con = self.form_util.preProcessWords(p[1])

                while (name in con):
                    con = con.replace(name, '')

                if len(con) > len(form_words):
                    c_len = len(form_words)
                    count = self.seacrchAll(con, form_words)

                else:

                    c_len = len(con)
                    count = self.seacrchAll(form_words, con)
                if float(count) / float(c_len) >= 0.65:
                    ans_con.append([name, p[0], p[1]])
                    count_rate.append(count / c_len)
        if ans_con != []:

            max_index = np.argmax(np.array(count_rate))
            return ans_con[max_index]
        return None

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

        form_words = self.form_util.preProcessWords(words)

        ans_con = []
        count_rate = []

        for name, content in deal_entity.items():

            """
            抽取出的实体的属性
            """
            pro = np.array(content['p'])

            """
            去掉问题中的实体方便匹配
            """
            while (name in form_words):
                form_words = form_words.replace(name, '')

            for p in pro:

                con = self.form_util.preProcessWords(p[1])

                while (name in con):
                    con = con.replace(name, '')

                if len(con) > len(form_words):
                    c_len = len(form_words)
                    count = self.seacrchAll(con, form_words)
                else:
                    c_len = len(con)
                    count = self.seacrchAll(form_words, con)
                if float(count) / float(c_len) >= 0.65:
                    ans_con.append([name, p[0], p[1]])
                    count_rate.append(count / c_len)
        if ans_con != []:
            revers_count = []

            for ans in ans_con:
                if len(form_words) >= len(ans[2]):
                    revers_count.append(self.seacrchAll(form_words, ans[2]) / len(form_words))
                else:
                    revers_count.append(self.seacrchAll(ans[2], form_words) / len(ans[2]))
            max_index = np.argmax(np.array(revers_count))
            return ans_con[max_index]
        return None

    def matchFuzzySearch(self, words, triple):
        """

        """

        form_words = self.form_util.preProcessWords(words)

        ans_con = []
        count_rate = []

        for name,key,value in triple:

            value = self.form_util.preProcessWords(value)
            while (name in form_words):
                form_words = form_words.replace(name, '')
            while (name in value):
                value = value.replace(name, '')
            count = self.seacrchAll(value, form_words)
            c_len = len(form_words)
            if float(count) / float(c_len) >= 0.65:
                ans_con.append([name,key,value])
                count_rate.append(count / c_len)

        if ans_con != []:

            max_index = np.argmax(np.array(count_rate))
            return ans_con[max_index]
        return None

    def getSubByLimit(self, keyword, entity):


        sub_entity = []

        son_list = self.getEntityByType(entity[0])
        deal_entity = self.dealWithEnitity(son_list)

        for name, content in deal_entity.items():
            flag = False

            rel = np.array((content['r']))
            for r in rel:
                if keyword[0] in r[1]:
                    sub_entity.append(name)
                    flag = True
                    break

            if flag:
                continue

            pro = np.array(content['p'])
            for p in pro:
                if keyword[0] in p[1]:
                    sub_entity.append(name)
                    break


        if sub_entity != []:

            return sub_entity
        return None

    def downFindAnsByWords(self,words, entity,property):

        son_list = self.getEntityByType(entity[0])
        if son_list == None:
            return None
        deal_entity = self.dealWithEnitity(son_list)
        ans = self.directAnsProConWithPro(words,deal_entity,property)
        return ans

    def downFindAnsByEnt(self,words, entity):
        deal_entity = self.dealWithEnitity(entity)
        ans = self.directAnsProCon(words, deal_entity)

        if ans != None:
            return ans
        son_list = self.getEntityByType(entity[0])
        if son_list == None:
            return None
        deal_entity = self.dealWithEnitity(son_list)
        ans = self.directAnsProCon(words,deal_entity)
        return ans

    def taskNormalPro(self,entity,property):
        ans = self.directAnsByProName(entity,property)
        #print("taskNormalpro",ans)
        return ans

    def taskNormalRel(self,entity,property):
        ans = self.directAnsByRelName(entity,property)
        #print("taskNormalrel",ans)
        return ans

    def taskSonMatch(self,words,entity,property):
        ans = self.downFindAnsByWords(words,entity,property)
        #print("taskSonMatch",ans)
        return ans

    def taskProMatch(self,words,entity,property):
        ans = self.downFindAnsByWords(words,entity,property)
        #print("taskSonMatch",ans)
        return ans

    def taskSonKeyWord(self,entity,property,keyword):
        ans = self.downFindAnsByRel(entity, property, keyword)
        #print("taskSonKeyWord",ans)
        return ans

    def taskProName(self,words,entity):
        ans = self.downFindAnsByEnt(words,entity)
        return ans

    def taskReverse(self,words,key_words):
        triple = self.getEntByfuzzySearch(key_words[0])
        ans = self.matchFuzzySearch(words,triple)
        return ans

    def taskLimitSub(self,key_words,entity):
        ans = self.getSubByLimit(key_words,entity)
        return ans


if __name__ == '__main__':
    pass
