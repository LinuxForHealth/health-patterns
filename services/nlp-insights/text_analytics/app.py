import json
import logging
import os

from flask import Flask, request, Response
from jsonpath_ng import parse
from text_analytics.acd.acd_service import ACDService
from text_analytics.quickUMLS.quickUMLS_service import QuickUMLSService


logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

#Maps values seen in configs to NLP python classes
all_nlp_services = {'acd': ACDService, 'quickumls': QuickUMLSService}
#NLP Service currently configured
nlp_service = None
#Stores instances of configured NLP Services
nlp_services_dict = {}


def setup_config_dir():
    pvPath = os.path.join(os.getcwd(), '..', 'mnt', 'data')
    localPath = os.path.join('text_analytics', 'configs')
    if os.access(pvPath, os.W_OK):
        try:
            defaultJsonFile = open('text_analytics/configs/default', 'r')
            defaultJson = defaultJsonFile.read()
            defaultPVFile = open(pvPath + '/default', 'w')
            defaultPVFile.write(defaultJson)
        except:
            logger.info(localPath)
            return localPath
        logger.info(pvPath)
        return pvPath
    else:
        logger.info(localPath)
        return localPath


def setup_service(config_name):
    global nlp_service
    jsonFile = open(configDir + f'/{config_name}', "r")
    jsonString = jsonFile.read()
    config_dict = json.loads(jsonString)
    if config_name in nlp_services_dict.keys():
        nlp_service = nlp_services_dict[config_name]
    else:
        nlp_name = config_dict.get('nlpService')
        if nlp_name is not None and nlp_name.lower() in all_nlp_services.keys():
            nlp_service = all_nlp_services[nlp_name.lower()](jsonString)
        else:
            logger.error("NLP service was unable to be configured. Config in incorrect format")
            return Response("NLP service was unable to be configured. Config in incorrect format", status=400)
        nlp_services_dict[config_name] = nlp_service
    logger.info("NLP service configured with: " + config_dict['nlpService'])
    return Response(jsonString, status=200, mimetype='application/json')


configDir = setup_config_dir()
setup_service('default')



@app.route("/config/<config_name>", methods=['GET'])
def get_config(config_name):
    try:
        json_file = open(configDir + f'/{config_name}', 'r')
        json_string = json_file.read()
    except FileNotFoundError:
        logger.error("Config with the name: " + config_name + " doesn't exist.")
        return Response("Config with the name: " + config_name + " doesn't exist.", status=400)
    logger.info("Config found")
    return Response(json_string, status=200, mimetype='application/json')


@app.route("/config/<config_name>", methods=['POST', 'PUT'])
def persist_config(config_name):
    try:
        json_file = open(configDir + f'/{config_name}', 'w')
        json_file.write(request.data.decode('utf-8'))
    except:
        logger.exception("Error when trying to persist given config.")
        return Response("Error when trying to persist given config.", status=400)
    logger.info("Config successfully added/updated")
    return Response(status=200)


@app.route("/config/<config_name>", methods=['DELETE'])
def delete_config(config_name):
    try:
        os.remove(configDir + f'/{config_name}')
    except OSError as error:
        logger.error("Error when trying to delete config: " + error.message)
        return Response("Error when trying to delete config: " + error.message, status=400)
    logger.info("Config successfully deleted")
    return Response("Config successfully deleted", status=200)




@app.route("/all_configs", methods=['GET'])
def get_all_configs():
    configs = []
    directory = os.fsencode(configDir)
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        configs.append(filename)
    if not configs:
        output = 'There are no configs'
    else:
        output = "\n".join(configs)
    logger.info("Config list displayed")
    return Response(output, status=200)


@app.route("/config", methods = ['GET'])
def get_current_config():
    return Response(nlp_service.jsonString, status=200, mimetype='application/json')


@app.route("/config", methods = ['POST', 'PUT'])
def setup_config():
    if request.args and request.args.get('name'):
        name = request.args.get('name')
        try:
            return setup_service(name)
        except Exception as ex:
            logger.warn('Error in setting up service with a config name of: ' + name, ex)
            return Response('Error in setting up service with a config name of: ' + name, status=400)
    else:
        logger.warn('Did not provide query parameter name to set up service')
        return Response("Did not provide query parameter name to set up service", status=400)

def _apply_analytics_to_bundle(request_data):
    assert request_data['resourceType'] == 'Bundle'
    
    new_entries = []
    for entry in request_data['entry']:
        if entry["resource"]["resourceType"] in nlp_service.types_can_handle:
            nlp_resp = process_resource(entry["resource"])
            if nlp_resp['resourceType'] == 'Bundle':
                new_entries.extend(nlp_resp['entry'])
            else:
                entry["resource"] = nlp_resp #update existing resource

    request_data['entry'].extend(new_entries)

@app.route("/process", methods=['POST'])
def process():
    if nlp_service == None:
            return Response("No NLP service configured", status=400)

    fhir_data = json.loads(request.data) #could be resource or bundle

    new_entries = []
    if fhir_data['resourceType'] == 'Bundle':
        _apply_analytics_to_bundle(fhir_data)
    else:
        fhir_data = process_resource(fhir_data)

    return Response(json.dumps(fhir_data), status=200, mimetype='application/json')


def process_resource(request_data):
    input_type = request_data['resourceType']
    if input_type in nlp_service.types_can_handle:
        enhance_func = nlp_service.types_can_handle[input_type]
        resp = enhance_func(nlp_service, request_data)
        json_response = json.loads(resp)

        logger.info("Resource successfully updated")
        return json_response
    else:
        logger.info("Resource no handled so respond back with original")
        return request_data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
