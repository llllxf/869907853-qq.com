# !/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
sys.path.append(project_path)
from model.aiml_cn import  Kernel
from model.aiml_cn import kernel

"""
AIML工具类
"""
class AIMLUtil(object):

    @classmethod
    def __init__(cls):


        """
        百科aiml
        """
        #print(project_path)
        cls.pedia_aiml_kernal = kernel()
        #cls.pedia_aiml_kernal.learn('../../resource/pattern_for_cyclopedia.aiml')
        cls.pedia_aiml_kernal.learn(project_path+'/resource/pattern_for_cyclopedia.aiml')


    @classmethod
    def pedia_response(cls, question):
        return cls.pedia_aiml_kernal.respond(question)


if __name__ == '__main__':
    AIMLUtil()
    ans = AIMLUtil.response("HED")
    print(ans)

