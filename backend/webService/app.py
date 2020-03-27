
#!/usr/bin/env Python
# coding=utf-8
import sys
import os
#project_path = os.path.abspath(os.path.join(os.getcwd()))
project_path = os.path.abspath(os.path.join(os.getcwd(), "../"))

sys.path.append(project_path)
from flask import Flask, render_template, request, make_response
from flask import jsonify

import time
import threading

from dm import DialogManagement
dm_tool = DialogManagement()

def heartbeat():
    print (time.strftime('%Y-%m-%d %H:%M:%S - heartbeat', time.localtime(time.time())))
    timer = threading.Timer(60, heartbeat)
    timer.start()
timer = threading.Timer(60, heartbeat)
timer.start()

try:  
    import xml.etree.cElementTree as ET  
except ImportError:  
    import xml.etree.ElementTree as ET


import re
zhPattern = re.compile(u'[\u4e00-\u9fa5]+')


app = Flask(__name__,static_url_path="/static") 

@app.route('/message', methods=['POST'])
def reply():

    question = request.form['msg']
    res_msg = dm_tool.doNlu(question)



    #res_msg = "yes"
    print(res_msg,"==================")
    return jsonify( { 'text': res_msg } )

@app.route("/")
def index():
    return render_template("index.html")

# 启动APP
if (__name__ == "__main__"): 
    app.run(host = '0.0.0.0', port = 8809)


