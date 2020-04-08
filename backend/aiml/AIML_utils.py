# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)
from aiml.Kernel import  Kernel
#import Kernel
#from

"""
AIML工具类
"""
class AIMLUtil(object):


    def __init__(self):


        """
        三层aiml初始化
        """
        #print(project_path)
        self.sentenceAIML = Kernel()
        self.nluAIML = Kernel()

        #self.sentenceAIML.learn(project_path+'/pattern/sentence.aiml')
        self.nluAIML.learn(project_path + '/pattern/nlu.aiml')
        #self.sentenceAIML.learn(project_path + '/pattern/sentence.aiml')

    def getSenAIML(self):
        return self.sentenceAIML

    def getNluAIML(self):
        return self.nluAIML


    def sen_response(self, question):
        return self.sentenceAIML.respond(question)

    def nlu_response(self, pattern):
        return self.nluAIML.respond(pattern)


if __name__ == '__main__':
    nluaiml = AIMLUtil()
    ans = nluaiml.nlu_response("ENTjhjPRO")
    print(ans)

