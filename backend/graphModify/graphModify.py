# @Language: python3
# @File  : graphModify.py
# @Author: LinXiaofei
# @Date  : 2020-05-19
"""

"""

import sys
import os
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
# print(project_path)
sys.path.append(project_path)
from data.data_process import read_file
from nlu.LTPUtil import LTPUtil

from graphSearch.graphSearch import graphSearch

class graphModify(object):
    def __init__(self):
        self.search_util = graphSearch()

    def fileForPro(self,type):

        isExists = os.path.exists(project_path+"/data/pro/"+type)
        if not isExists:
            os.makedirs(project_path+"/data/pro/"+type)
        pro = self.search_util.getProByType(type)
        for p in pro:
            f = open(project_path + "/data/pro/"+type+"/"+p+".txt","w")

            f.writelines(p+"\n")

            value_list = self.search_util.getValueByPro(type,p)
            for value in value_list:
                f.writelines(value[0]+":"+value[1]+"\n")
                f.writelines("\n")
            f.close()

    def filreForRel(self,type):

        isExists = os.path.exists(project_path + "/data/rel/" + type)
        if not isExists:
            os.makedirs(project_path + "/data/rel/" + type)
        if "label" in type:
            return
        rel = self.search_util.getRelByType(type)

        for r in rel:
            f = open(project_path + "/data/rel/" + type + "/" + r + ".txt", "w")

            f.writelines(r + "\n")

            value_list = self.search_util.getValueByRel(type, r)
            for value in value_list:
                f.writelines(value[0] + ":" + value[1] + "\n")
                f.writelines("\n")
            f.close()

    def resetProToRepertory(self,type,old,new):

        modify_list = []
        new_list = []
        old_list = read_file(project_path + "/data/pro/"+type+"/"+old+".txt")

        modify_pre = old_list[0]
        predicate = self.search_util.getPredicate(modify_pre)
        new_predicate = self.search_util.getPredicate(new)
        for o in old_list[1:]:
            information = o.split(":")
            sub_label = information[0]
            subject = self.search_util.getSubject(sub_label)
            modify_list.append({"subject":subject,"predicate":predicate,"object":information[1]})
            new_list.append({"subject":subject, "predicate":new_predicate, "object":information[1]})
        data = {'repertoryName':'geo4','oldList':str(modify_list),'newList':str(new_list)}
        self.search_util.resetTripleToRepertory(data)
        log = open(project_path + "/data/log/" + type + ".txt", "a")

        log.writelines("reset:  [" + type + "]" + modify_pre + "-->" + new + "\n")
        log.writelines("=========================================\n")


    def resetRelToRepertory(self,type,old,new):

        modify_list = []
        new_list = []
        old_list = read_file(project_path + "/data/pro/"+type+"/"+old+".txt")
        print(old_list)
        modify_pre = old_list[0]
        predicate = self.search_util.getPredicate(modify_pre)
        new_predicate = self.search_util.getRelPredicate(new)
        for o in old_list[1:]:
            information = o.split(":")
            sub_label = information[0]
            obj_label = information[1]


            subject = self.search_util.getSubject(sub_label)
            obj = self.search_util.getSubject(obj_label)
            modify_list.append({"subject":subject,"predicate":predicate,"object":obj_label})
            new_list.append({"subject":subject, "predicate":new_predicate, "object":obj})


        data = {'repertoryName':'geo4','oldList':str(modify_list),'newList':str(new_list)}

        self.search_util.resetRelTripleToRepertory(data)
        log = open(project_path + "/data/log/" + type + ".txt", "a")

        log.writelines("reset:  [" + type + "]" + modify_pre + "-->" + new + "\n")
        log.writelines("=========================================\n")

    def addTripleToRepertory(self,subj,pred,obje,type):
        log = open(project_path + "/data/log/" + type + ".txt","a")
        tripleList = []
        for p_index in range(len(pred)):
            predicate = self.search_util.getPredicate(pred[p_index])
            subject = self.search_util.getSubject(subj[p_index])
            tripleList.append({"subject":subject,"predicate":predicate,"object":obje[p_index]})
        self.search_util.addTripleToRepertory(tripleList)
        for i in range(len(subj)):
            log.writelines("add:  " + subj[i] + "-" + pred[i] + "-" + obje[i] + "\n")
            log.writelines("=========================================\n")

    def addRelTripleToRepertory(self,subj,pred,obje,type):
        log = open(project_path + "/data/log/" + type + ".txt","a")
        tripleList = []
        for p_index in range(len(pred)):
            predicate = self.search_util.getRelPredicate(pred[p_index])
            subject = self.search_util.getSubject(subj[p_index])
            obj = self.search_util.getSubject(obje[p_index])
            tripleList.append({"subject":subject,"predicate":predicate,"object":obj})
        self.search_util.addTripleToRepertory(tripleList)
        for i in range(len(subj)):
            log.writelines("add:  "+subj[i]+"-"+pred[i]+"-"+obje[i]+"\n")
            log.writelines("=========================================\n")

    def deleteTripleToRepertory(self, subj, pred, obje, type):
        log = open(project_path + "/data/log/" + type + ".txt", "a")
        tripleList = []
        for p_index in range(len(pred)):
            predicate = self.search_util.getPredicate(pred[p_index])
            subject = self.search_util.getSubject(subj[p_index])
            tripleList.append({"subject": subject, "predicate": predicate, "object": obje[p_index]})
        self.search_util.deleteTripleToRepertory(tripleList)
        for i in range(len(subj)):
            log.writelines("delete:  " + subj[i] + "-" + pred[i] + "-" + obje[i] + "\n")
            log.writelines("=========================================\n")




if __name__ == '__main__':
    g = graphModify()
    g.deleteTripleToRepertory(['长江'],['国家'],['中国'],'河流')

    """
    type_list = read_file(project_path + "/data/类型.csv")
    count = 0
    for t in type_list:
        print(t)
        count = count+1
        g.filreForRel(t)
        g.fileForPro(t)
    """
    #g.resetRelToRepertory('河流','国家','位于')


