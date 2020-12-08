
#!/usr/bin/env Python
# coding=utf-8


from flask import Flask, render_template, request, make_response
from flask import jsonify

import time
import threading


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



#app = Flask(__name__, template_folder=project_path,static_url_path=project_path+"/static/", static_folder=project_path+"/static/")
app = Flask(__name__,static_url_path="/static")

@app.route('/')
def index():
    return render_template("input.html")

@app.route('/goChoose', methods=['POST','GET'])
def goChoose():
    return render_template("index.html")

@app.route('/goChinese', methods=['POST','GET'])
def goChinese():
    return render_template("chooseSubject.html")

@app.route('/goMath', methods=['POST','GET'])
def goMath():
    return render_template("chooseSubject.html")

@app.route('/goEnglisg', methods=['POST','GET'])
def goEnglisg():
    return render_template("chooseSubject.html")

@app.route('/goPhysics', methods=['POST','GET'])
def goPhysics():
    return render_template("chooseSubject.html")

@app.route('/goChemistry', methods=['POST','GET'])
def goChemistry():
    return render_template("chooseSubject.html")

@app.route('/goBiology', methods=['POST','GET'])
def goBiology():
    return render_template("chooseSubject.html")

@app.route('/goHistory', methods=['POST','GET'])
def goHistory():
    return render_template("chooseSubject.html")

@app.route('/goPolitics', methods=['POST','GET'])
def goPolitics():
    return render_template("chooseSubject.html")

@app.route('/goGeography', methods=['POST','GET'])
def goGeography():
    return render_template("input.html")

@app.route('/message', methods=['POST'])
def message():
    message = request.form.get('message')
    print(message)


    return render_template("input.html",message = message)


# 启动APP
if (__name__ == "__main__"):

    app.run(host = '0.0.0.0', port = 8809)


