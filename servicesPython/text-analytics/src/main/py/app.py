from flask import Flask, request
from acd.acd_service import ACDService
from quickUMLS.quickUMLS_service import QuickUMLSService
import json
from call_nlp_then_enhance import call_service_then_enhance

app = Flask(__name__)

nlp_service = None


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/configure/", methods=['POST'])
def setup_nlp():
    global nlp_service
    configJson = json.loads(request.data)
    if configJson["nlpService"] == "ACD":
        nlp_service = ACDService(request.data)
        return request.data
    if configJson["nlpService"] == "quickUMLS":
        nlp_service = QuickUMLSService(request.data)
        return request.data

@app.route("/process/", methods=['POST'])
def apply_analytics():
    request_data = request.data
    if nlp_service is not None:
        # resp = nlp_service.process(request_data)
        resp = call_service_then_enhance(nlp_service, request_data)
    return str(resp)
