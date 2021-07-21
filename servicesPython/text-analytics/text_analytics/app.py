from flask import Flask, request, Response, jsonify
from text_analytics.acd.acd_service import ACDService
from text_analytics.quickUMLS.quickUMLS_service import QuickUMLSService
from text_analytics.enhance import *
import json
import requests
from jsonpath_ng import jsonpath, parse
import os

app = Flask(__name__)

nlp_service = None
nlp_services_dict = {}

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# @app.route("/config/", methods=['POST'])
# def setup():
#     setupService(request.data)
#     return Response(status=200)

@app.route("/config/<configName>", methods=['POST', 'GET', 'PUT', 'DELETE'])
def nlp_configs(configName):

    if request.method == 'GET':
        jsonFile = open('configs/' + configName, "r")
        jsonString = jsonFile.read()
        return jsonString

    elif request.method == 'POST':
        try:
            jsonFile = open('configs/' + configName, 'x')
        except FileExistsError as error:
            print(error)
            print('File already exists')    
        jsonFile.write(request.data.decode('utf-8'))
        # setupService(request.data)
        return request.data

    elif request.method == 'PUT':
        jsonFile = open('configs/' + configName, 'w')
        jsonFile.write(request.data.decode('utf-8'))
        # setupService(request.data)
        return request.data
    
    elif request.method == 'DELETE':
        try:
            os.remove('configs/' + configName)
        except OSError as error:
            print(error)
        return Response(status=200)

    

@app.route("/config/", methods=['GET'])
def get_all_configs():
    configs = []
    directory = os.fsencode('configs')
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        configs.append(filename)
    if configs == []:
        output = 'There are no configs'
    else:
        output = "\n".join(configs)
    return output
        

@app.route("/setup/<configName>", methods=['GET'])
def setup_nlp(configName):
    setupService(configName)
    return Response(status=200)

@app.route("/process/", methods=['POST'])
def apply_analytics():
    # configName = request.args.get('configName')
    # setupService(configName)

    request_data = json.loads(request.data)
    if nlp_service is not None:
        inputType = request_data['resourceType']
        if inputType in nlp_service.types_can_handle.keys():
            enhanceFunc = nlp_service.types_can_handle[inputType]
            resp = enhanceFunc(nlp_service, request_data)
        elif inputType == "Bundle":
            resp = process_bundle(request_data)
        else:
            resp = nlp_service.process(request.data)
        return str(resp)
    return "Internal Server Error"


def setupService(configName):
    global nlp_service
    # with open('configs/' + configName, 'r') as jsonFile:
    #     configJson = json.load(jsonFile)
    jsonFile = open('configs/' + configName, "r")
    jsonString = jsonFile.read()
    configJson = json.loads(jsonString)
    if configName in nlp_services_dict.keys():
        nlp_service = nlp_services_dict[configName]
    else:
        if configJson["nlpService"] == "ACD":
            nlp_service = ACDService(jsonString)
        if configJson["nlpService"] == "quickUMLS":
            nlp_service = QuickUMLSService(jsonString)
        else:
            return 'No nlp service configured'
        nlp_services_dict[configName] = nlp_service
    return jsonString


def process_bundle(jsonString):
    new_resource_dict = {}
    
    jsonpath_exp = parse('entry[*]')
    for match in jsonpath_exp.find(jsonString):
        request_body = match.value['resource']
        resp = requests.post('http://127.0.0.1:5000/process/', json=request_body)
        # print(json.loads(resp.text))
        print(resp.text)
        
        new_resource_dict[match.value['fullUrl']] = json.loads(resp.text)
    
    for resource in jsonString['entry']:
        resource['resource'] = new_resource_dict[resource['fullUrl']]
    print(new_resource_dict)
    return jsonString

        

    




# @app.route("/processAllergy", methods=['POST'])
# def process_Allergy():
#     request_data = json.loads(request.data)
#     if nlp_service is not None:
#         resp = enhance_allergy_intolerance_payload_to_fhir(nlp_service, request_data)
#         return resp.json()
#     return "NLP service not specified"


# @app.route("/processDiagnosticReport", methods=['POST'])
# def process_Diagnostic_Report():
#     request_data = json.loads(request.data)
#     if nlp_service is not None:
#         resp = enhance_diagnostic_report_payload_to_fhir(nlp_service, request_data)
#         return str(resp)
#     return "NLP service not specified"


# @app.route("/processImmunization", methods=['POST'])
# def process_Immunization():
#     request_data = json.loads(request.data)
#     if nlp_service is not None:
#         resp = enhance_immunization_payload_to_fhir(nlp_service, request_data)
#         return str(resp)
#     return "NLP service not specified"
