import json
import logging
import os

from flask import Flask, request, Response
from jsonpath_ng import parse

from text_analytics.acd.acd_service import ACDService
from text_analytics.quickUMLS.quickUMLS_service import QuickUMLSService


logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app = Flask(__name__)

# Maps values seen in configs to NLP python classes
all_nlp_services = {'acd': ACDService, 'quickumls': QuickUMLSService}
# NLP Service currently configured
nlp_service = None
# Stores instances of configured NLP Services
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
        except Exception:
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

    nlp_name = config_dict.get('nlpService')
    if nlp_name is not None and nlp_name.lower() in all_nlp_services.keys():
        nlp_service = all_nlp_services[nlp_name.lower()](jsonString)
        nlp_services_dict[config_name] = nlp_service
    else:
        logger.error("NLP service was unable to be configured. Config in incorrect format")
        return Response("NLP service was unable to be configured. Config in incorrect format", status=400)

    logger.info("NLP service configured with: %s", config_dict['nlpService'])
    return Response(jsonString, status=200, mimetype='application/json')


configDir = setup_config_dir()
setup_service('default')


@app.route("/config/<config_name>", methods=['GET'])
def get_config(config_name):
    try:
        json_file = open(configDir + f'/{config_name}', 'r')
        json_string = json_file.read()
    except FileNotFoundError:
        logger.error("Config with the name %s doesn't exist.", config_name)
        return Response("Config with the name: " + config_name + " doesn't exist.", status=400)
    logger.info("Config found")
    return Response(json_string, status=200, mimetype='application/json')


@app.route("/config/<config_name>", methods=['POST', 'PUT'])
def persist_config(config_name):
    try:
        request_str = request.data.decode('utf-8')
        config_dict = json.loads(request_str)
        if "nlpService" not in config_dict:
            raise KeyError("'nlpService' must be a key in config")
        nlp_service = config_dict["nlpService"]
        if nlp_service.lower() not in all_nlp_services.keys():
            raise ValueError("only 'acd' and 'quickumls' allowed at this time:" + nlp_service)
        json_file = open(configDir + f'/{config_name}', 'w')
        json_file.write(request_str)
    except Exception as ex:
        logger.exception("Error when trying to persist given config.")
        return Response("Error when trying to persist given config: " + str(ex), status=400)
    logger.info("Config successfully added/updated")
    return Response(status=200)


@app.route("/config/<config_name>", methods=['DELETE'])
def delete_config(config_name):
    try:
        os.remove(configDir + f'/{config_name}')
    except OSError as error:
        logger.exception("Error when trying to delete config")
        return Response("Error when trying to delete config: " + str(error), status=400)
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


@app.route("/config", methods=['GET'])
def get_current_config():
    return Response(nlp_service.jsonString, status=200, mimetype='application/json')


@app.route("/config", methods=['POST', 'PUT'])
def setup_config():
    if request.args and request.args.get('name'):
        name = request.args.get('name')
        try:
            return setup_service(name)
        except Exception:
            logger.exception('Error in setting up service with a config name of: %s', name)
            return Response('Error in setting up service with a config name of: ' + name, status=400)
    else:
        logger.warning('Did not provide query parameter name to set up service')
        return Response("Did not provide query parameter name to set up service", status=400)


@app.route("/process", methods=['POST'])
def process():
    if nlp_service is None:
        return Response("No NLP service configured", status=400)

    fhir_data = json.loads(request.data)  # could be resource or bundle

    input_type = fhir_data['resourceType']
    resp_string = None
    new_entries = []
    if input_type == 'Bundle':
        entrylist = fhir_data['entry']
        for entry in entrylist:
            if entry["resource"]["resourceType"] in nlp_service.types_can_handle:
                resp = process_resource(entry["resource"])
                if resp['resourceType'] == 'Bundle':
                    # response is a bundle of new resources to keep for later
                    for new_entry in resp['entry']:
                        new_entries.append(new_entry)  # keep new resources to be added later
                else:
                    entry["resource"] = resp  # update existing resource

        for new_entry in new_entries:
            entrylist.append(new_entry)  # add new resources to bundle

        resp_string = fhir_data
    else:
        resp_string = process_resource(fhir_data)  # single resource so just return response

    return_response = json.dumps(resp_string)  # back to string

    return Response(return_response, status=200, mimetype='application/json')


def process_resource(request_data):
    input_type = request_data['resourceType']
    if input_type in nlp_service.types_can_handle:
        enhance_func = nlp_service.types_can_handle[input_type]
        resp = enhance_func(nlp_service, request_data)
        json_response = json.loads(resp)

        logger.info("Resource successfully updated")
        return json_response
    else:
        logger.info("Resource not handled so respond back with original")
        return request_data


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
