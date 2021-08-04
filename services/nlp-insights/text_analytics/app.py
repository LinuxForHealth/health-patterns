from flask import Flask, request, Response
from text_analytics.acd.acd_service import ACDService
from text_analytics.quickUMLS.quickUMLS_service import QuickUMLSService
import json
from jsonpath_ng import parse
import os
import logging

logger = logging.getLogger()

app = Flask(__name__)

nlp_service = None
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
    configJson = json.loads(jsonString)
    if config_name in nlp_services_dict.keys():
        nlp_service = nlp_services_dict[config_name]
    else:
        if configJson["nlpService"].lower() == "acd":
            nlp_service = ACDService(jsonString)
        elif configJson["nlpService"].lower() == "quickumls":
            nlp_service = QuickUMLSService(jsonString)
        else:
            logger.error("NLP service was unable to be configured. Config in incorrect format")
            return Response("NLP service was unable to be configured. Config in incorrect format", status=400)
        nlp_services_dict[config_name] = nlp_service
    logger.info("NLP service configured with: " + configJson['nlpService'])
    return Response(jsonString, status=200, mimetype='application/json')


def process_bundle(json_string):
    new_resource_dict = {}

    jsonpath_exp = parse('entry[*]')
    resources = jsonpath_exp.find(json_string)
    if len(resources) == 0:
        logger.warning("Bundle has no resources or is improperly formatted")
    for match in resources:
        request_body = match.value['resource']
        resp = process(request_body)
        try:
            new_resource_dict[match.value['fullUrl']] = json.loads(resp)
        except KeyError:
            logger.error("Bundle doesn't have fullUrls for resources")
            return Response("Bundle doesn't have fullUrls for resources", status=400)

    for resource in json_string['entry']:
        resource['resource'] = new_resource_dict[resource['fullUrl']]
    return json_string




configDir = setup_config_dir()
setup_service('default')



@app.route("/config/<config_name>", methods=['GET'])
def get_config(config_name):
    try:
        # json_file = open('text_analytics/configs/' + configName, "r")
        json_file = open(configDir + f'/{config_name}', 'r')
        json_string = json_file.read()
    except FileNotFoundError:
        logger.error("Config with the name: " + config_name + " doesn't exist.")
        return Response("Config with the name: " + config_name + " doesn't exist.", status=400)
    logger.info("Config found")
    return Response(json_string, status=200, mimetype='application/json')


@app.route("/config/<config_name>", methods=['POST'])
def post_config(config_name):
    try:
        # json_file = open('text_analytics/configs/' + configName, 'x')
        json_file = open(configDir + f'/{config_name}', 'x')
        json_file.write(request.data.decode('utf-8'))
    except FileExistsError as error:
        logger.error("Config with the name: " + config_name + "already exists.")
        return Response("Config with the name: " + config_name + "already exists.", status=400)
    logger.info("Config successfully added")
    return Response(status=200)


@app.route("/config/<config_name>", methods=['PUT'])
def put_config(config_name):
    try:
        # json_file = open('text_analytics/configs/' + configName, 'w')
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
        # os.remove('text_analytics/configs/' + configName)
        os.remove(configDir + f'/{config_name}')
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
    if not configs:
        output = 'There are no configs'
    else:
        output = "\n".join(configs)
    logger.info("Config list displayed")
    return Response(output, status=200)


@app.route("/setup/<config_name>", methods=['GET'])
def setup_nlp(config_name):
    setup_service(config_name)
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
        input_type = request_data['resourceType']
        if input_type in nlp_service.types_can_handle.keys():
            enhance_func = nlp_service.types_can_handle[input_type]
            resp = enhance_func(nlp_service, request_data)
        elif input_type == "Bundle":
            resp = process_bundle(request_data)
        else:
            resp = nlp_service.process(request.data)
        json_response = str(resp).replace("'", "\"").replace("True", "true")
        logger.info("Resource successfully updated")
        return json_response
    logger.error("No NLP Service configured")
    return "Error"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
