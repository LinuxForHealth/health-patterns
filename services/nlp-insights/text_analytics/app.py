from flask import Flask, request, Response, jsonify, make_response
from text_analytics.acd.acd_service import ACDService
from text_analytics.quickUMLS.quickUMLS_service import QuickUMLSService
from text_analytics.enhance import *
import json
import requests
from jsonpath_ng import jsonpath, parse
import os
import logging

logger = logging.getLogger()

app = Flask(__name__)

nlp_service = None
nlp_services_dict = {}


def setupConfigDir():
    pvPath = os.path.join(os.getcwd(), '..', 'mnt', 'data')
    localPath = os.path.join('text_analytics', 'configs')
    if os.access(pvPath, os.W_OK) == True:
        try:
            defaultJsonFile = open('text_analytics/configs/default', 'r')
            defaultJson = defaultJsonFile.read()
            defaultPVFile = open(pvPath + '/default', 'w')
            defaultPVFile.write(defaultJson)
        except:
            return localPath
        return pvPath
    else:
        return localPath



def setupService(configName):
    global nlp_service
    jsonFile = open(configDir + f'/{configName}', "r")
    jsonString = jsonFile.read()
    configJson = json.loads(jsonString)
    if configName in nlp_services_dict.keys():
        nlp_service = nlp_services_dict[configName]
    else:
        if configJson["nlpService"] == "ACD":
            nlp_service = ACDService(jsonString)
        elif configJson["nlpService"] == "quickUMLS":
            nlp_service = QuickUMLSService(jsonString)
        else:
            logger.error("NLP service was unable to be configured. Config in incorrect format")
            return Response("NLP service was unable to be configured. Config in incorrect format", status=400)
        nlp_services_dict[configName] = nlp_service
    logger.info("NLP service configured with: " + configJson['nlpService'])
    return Response(jsonString, status=200, mimetype='application/json')

def process_bundle(jsonString):
    new_resource_dict = {}
    
    jsonpath_exp = parse('entry[*]')
    resources = jsonpath_exp.find(jsonString)
    if len(resources) == 0:
        logger.warn("Bundle has no resources or is improperly formatted")
    for match in resources:
        request_body = match.value['resource']
        resp = process(request_body)
        try:
            new_resource_dict[match.value['fullUrl']] = json.loads(resp)
        except KeyError:
            logger.error("Bundle doesn't have fullUrls for resources")
            return Response("Bundle doesn't have fullUrls for resources", status=400)
    
    for resource in jsonString['entry']:
        resource['resource'] = new_resource_dict[resource['fullUrl']]
    return jsonString



configDir = setupConfigDir()
setupService('default')



@app.route("/config/<configName>", methods=['POST', 'GET', 'PUT', 'DELETE'])
def nlp_configs(configName):

    if request.method == 'GET':
        try:
            # jsonFile = open('text_analytics/configs/' + configName, "r")
            jsonFile = open(configDir + f'/{configName}', 'r')
            jsonString = jsonFile.read()
        except FileNotFoundError:
            logger.error("Config with the name: " + configName + " doesn't exist.")
            return Response("Config with the name: " + configName + " doesn't exist.", status=400)
        logger.info("Config found")
        return Response(jsonString, status=200, mimetype='application/json')

    elif request.method == 'POST':
        try:
            # jsonFile = open('text_analytics/configs/' + configName, 'x')
            jsonFile = open(configDir + f'/{configName}', 'x')
            jsonFile.write(request.data.decode('utf-8'))
        except FileExistsError as error:
            logger.error("Config with the name: " + configName + "already exists.")  
            return Response("Config with the name: " + configName + "already exists.", status=400)
        logger.info("Config successfully added")
        return Response(status=200)

    elif request.method == 'PUT':
        try:
            # jsonFile = open('text_analytics/configs/' + configName, 'w')
            jsonFile = open(configDir + f'/{configName}', 'w')
            jsonFile.write(request.data.decode('utf-8'))
        except:
            logger.exception("Error when trying to persist given config.")
            return Response("Error when trying to persist given config.", status=400)
        logger.info("Config successfully added/updated")
        return Response(status=200)
    
    elif request.method == 'DELETE':
        try:
            # os.remove('text_analytics/configs/' + configName)
            os.remove(configDir + f'/{configName}')
        except OSError as error:
            logger.error("Error when trying to delete config: " + error.message)
            return Response("Error when trying to delete config: " + error.message, status=400)
        logger.info("Config successfully deleted")
        return Response("Config successfully deleted", status=200)

    

@app.route("/config/", methods=['GET'])
def get_all_configs():
    configs = []
    # directory = os.fsencode('text_analytics/configs')
    directory = os.fsencode(configDir)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        configs.append(filename)
    if configs == []:
        output = 'There are no configs'
    else:
        output = "\n".join(configs)
    logger.info("Config list displayed")
    return Response(output, status=200)
        

@app.route("/setup/<configName>", methods=['GET'])
def setup_nlp(configName):
    setupService(configName)
    return Response(status=200)

@app.route("/process/", methods=['POST'])
def apply_analytics():
    request_data = json.loads(request.data)
    resp = process(request_data)
    if resp == "Error":
        return Response("No NLP service configured", status=400)
    else:
        return Response(resp, status=200, mimetype='application/json')


def process(request_data):
    if nlp_service is not None:
        inputType = request_data['resourceType']
        if inputType in nlp_service.types_can_handle.keys():
            enhanceFunc = nlp_service.types_can_handle[inputType]
            resp = enhanceFunc(nlp_service, request_data)
        elif inputType == "Bundle":
            resp = process_bundle(request_data)
        else:
            resp = nlp_service.process(request.data)
        jsonResponse = str(resp).replace("'","\"").replace("True","true")
        logger.info("Resource successfully updated")
        return jsonResponse
    logger.error("No NLP Service configured")
    return "Error"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
