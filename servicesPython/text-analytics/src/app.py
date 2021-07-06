from flask import Flask, request
from acd.call_acd_service import ACD_SERVICE
import json

app = Flask(__name__)

nlp_service = None

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/configure/", methods = ['POST'])
def setupNLP():
    global nlp_service 
    configJson = json.loads(request.data)
    if configJson["nlpService"] == "ACD":
        nlp_service = ACD_SERVICE(request.data)
        return request.data     

@app.route("/process/", methods = ['POST'])
def applyAnalytics():
    request_data = request.data
    
    resp = nlp_service.call_acd_with_text(request_data)
               
    return resp