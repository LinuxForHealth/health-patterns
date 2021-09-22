import json
import logging
import os

from flask import Flask, request, Response

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
# Stores resource to config overrides
override_resource_config = {}


def setup_config_dir():
    """Set up the directory structure for configs"""
    localpath = os.path.join('text_analytics', 'configs')
    logger.info(localpath)
    return localpath


def persist_config_helper(config_dict):
    """Helper function to check config details and create nlp instantiation"""

    if "nlpServiceType" not in config_dict:
        raise KeyError("'nlpService' must be a key in config")
    if "name" not in config_dict:
        raise KeyError("'name' must be a key in config")
    if "config" not in config_dict:
        raise KeyError("'config' must be a key in config")
    config_name = config_dict["name"]
    nlp_service_type = config_dict["nlpServiceType"]
    if nlp_service_type.lower() not in all_nlp_services.keys():
        raise ValueError("only 'acd' and 'quickumls' allowed at this time:" + nlp_service_type)
    json_file = open(configDir + f'/{config_name}', 'w')
    json_file.write(json.dumps(config_dict))

    new_nlp_service_object = all_nlp_services[nlp_service_type.lower()](json.dumps(config_dict))
    nlp_services_dict[config_dict["name"]] = new_nlp_service_object
    return config_name


def init_configs():
    """Create initial configs from deployment values, if any"""
    global nlp_service

    logger.info("ACD enable config: %s", os.getenv("ACD_ENABLE_CONFIG"))
    logger.info("QuickUMLS enable config: %s", os.getenv("QUICKUMLS_ENABLE_CONFIG"))

    if os.getenv("ACD_ENABLE_CONFIG") == 'true':
        # fill up a config for ACD
        try:
            tmp_config = {}
            tmp_config["name"] = os.getenv("ACD_NAME")
            tmp_config["nlpServiceType"] = "acd"
            details = {}
            details["endpoint"] = os.getenv("ACD_ENDPOINT")
            details["apikey"] = os.getenv("ACD_API_KEY")
            details["flow"] = os.getenv("ACD_FLOW")
            tmp_config["config"] = details
            persist_config_helper(tmp_config)
            logger.info("%s added:%s", tmp_config["name"], str(nlp_services_dict))
        except Exception as ex:
            logger.exception("Error when trying to persist initial config...skipping:%s", str(ex))

    if os.getenv("QUICKUMLS_ENABLE_CONFIG") == 'true':
        # fill up a config for quickumls
        try:
            tmp_config = {}
            tmp_config["name"] = os.getenv("QUICKUMLS_NAME")
            tmp_config["nlpServiceType"] = "quickumls"
            details = {}
            details["endpoint"] = os.getenv("QUICKUMLS_ENDPOINT")
            tmp_config["config"] = details
            persist_config_helper(tmp_config)
            logger.info("%s added:%s", tmp_config["name"], str(nlp_services_dict))
        except Exception as ex:
            logger.exception("Error when trying to persist initial config...skipping:%s", str(ex))

    default_nlp_service = os.getenv("NLP_SERVICE_DEFAULT")
    if default_nlp_service is not None and len(default_nlp_service) > 0:
        if default_nlp_service in nlp_services_dict:
            logger.info("Setting nlp service to %s", default_nlp_service)
            nlp_service = nlp_services_dict[default_nlp_service]
        else:
            logger.info("%s is not a valid nlp instance", default_nlp_service)


configDir = setup_config_dir()
init_configs()


@app.route("/config/<config_name>", methods=['GET'])
def get_config(config_name):
    """Gets and returns the given config details"""
    try:
        json_file = open(configDir + f'/{config_name}', 'r')
        json_string = json_file.read()
    except FileNotFoundError:
        logger.error("Config with the name %s doesn't exist.", config_name)
        return Response("Config with the name: " + config_name + " doesn't exist.", status=400)
    logger.info("Config found")
    return Response(json_string, status=200, mimetype='application/json')


@app.route("/config/definition", methods=['POST', 'PUT'])
def persist_config():
    """Create a new named config"""
    try:
        request_str = request.data.decode('utf-8')
        config_dict = json.loads(request_str)
        config_name = persist_config_helper(config_dict)
        logger.info("%s added:%s", config_name, str(nlp_services_dict))
    except Exception as ex:
        logger.exception("Error when trying to persist given config.")
        return Response("Error when trying to persist given config-" + str(ex), status=400)
    logger.info("Config successfully added/updated")
    return Response(status=200)


@app.route("/config/<config_name>", methods=['DELETE'])
def delete_config(config_name):
    """Delete a config by name"""
    try:
        if config_name not in nlp_services_dict:
            raise KeyError("'config name' must exist")
        if nlp_service is not None:
            current_config = json.loads(nlp_service.jsonString)
            if config_name == current_config["name"]:
                raise Exception("Cannot delete the default nlp service")
        if config_name in list(override_resource_config.values()):
            raise ValueError(config_name + " has an existing override and cannot be deleted")
        os.remove(configDir + f'/{config_name}')
        del nlp_services_dict[config_name]
    except Exception as ex:
        logger.exception("Error when trying to delete config")
        return Response("Error when trying to delete config-" + str(ex), status=400)
    logger.info("Config successfully deleted: " + config_name)
    return Response("Config successfully deleted: " + config_name, status=200)


@app.route("/all_configs", methods=['GET'])
def get_all_configs():
    """Get and return all configs by name"""
    configs = list(nlp_services_dict.keys())
    if not configs:
        output = 'No configs found'
    else:
        output = "\n".join(configs)
    logger.info("Config list displayed")
    return Response(output, status=200)


@app.route("/config", methods=['GET'])
def get_current_config():
    if nlp_service is None:
        return Response("No default nlp service is currently set", status=400)
    return Response(nlp_service.config_name, status=200, mimetype='application/plaintext')


@app.route("/config/setDefault", methods=['POST', 'PUT'])
def set_default_config():
    """Set the default nlp instance"""
    global nlp_service
    if request.args and request.args.get('name'):
        config_name = request.args.get('name')
        try:
            if config_name not in nlp_services_dict:
                raise KeyError(config_name + " is not a config")
            nlp_service = nlp_services_dict[config_name]
            return Response('Default config set to: ' + config_name, status=200, mimetype='application/plaintext')
        except Exception:
            logger.exception('Error in setting default with a config name of: %s', config_name)
            return Response('Error in setting default with a config name of: ' + config_name, status=400)
    else:
        logger.warning("Did not provide query parameter 'name' to set default config")
        return Response("Did not provide query parameter 'name' to set default config", status=400)


@app.route("/config/clearDefault", methods=['POST', 'PUT'])
def clear_default_config():
    """Clear the default nlp instance"""
    global nlp_service
    nlp_service = None
    return Response('Default config has been cleared', status=200, mimetype='application/plaintext')


@app.route("/config/resource", methods=['GET'])
def get_current_override_configs():
    """Get and return all override definitions"""
    return Response(str(override_resource_config), status=200, mimetype='application/plaintext')


@app.route("/config/resource/<resource_name>", methods=['GET'])
def get_current_override_config(resource_name):
    """Get and return override for this resource"""
    if resource_name not in override_resource_config:
        return Response('No override for this resource: ' + resource_name, status=400)
    return Response(override_resource_config[resource_name], status=200, mimetype='application/plaintext')


@app.route("/config/resource/<resource_name>/<config_name>", methods=['POST', 'PUT'])
def setup_override_config(resource_name, config_name):
    """Create a new override for a given resource"""
    try:
        if config_name not in nlp_services_dict:
            raise KeyError(config_name + " is not a config")
        temp_nlp_service = nlp_services_dict[config_name]
        if resource_name not in temp_nlp_service.types_can_handle:
            raise ValueError(resource_name + " cannot be handled by " + config_name)

        override_resource_config[resource_name] = config_name

        return Response(str(override_resource_config), status=200, mimetype='application/plaintext')
    except Exception:
        logger.exception('Error in setting up override for resource: %s', resource_name)
        return Response('Error in setting up override for resource: ' + resource_name, status=400)


@app.route("/config/resource/<resource_name>", methods=['DELETE'])
def delete_resource(resource_name):
    """Delete a resource override by name"""
    try:
        del override_resource_config[resource_name]
    except Exception:
        return Response("Error when trying to delete override for resource: " + resource_name, status=400)
    logger.info("Override successfully deleted: %s", resource_name)
    return Response("Override successfully deleted: " + resource_name, status=200)


@app.route("/config/resource", methods=['DELETE'])
def delete_resources():
    """Delete all resource overrides"""
    try:
        override_resource_config.clear()
    except Exception:
        return Response("Error when trying to delete all overrides", status=400)
    logger.info("Overrides successfully deleted")
    return Response("Overrides successfully deleted", status=200)


@app.route("/discoverInsights", methods=['POST'])
def discover_insights():
    """Process a bundle or a resource to enhance/augment with insights"""
    if nlp_service is None:
        return Response("No NLP service configured-need to set a default config", status=400)

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
    """Generate insights for a single resource"""
    global nlp_service
    resource_type = request_data['resourceType']
    logger.info("Processing resource type: %s", resource_type)
    nlp_service_backup = nlp_service  # save original to reset later
    if resource_type in override_resource_config:
        nlp_service = nlp_services_dict[override_resource_config[resource_type]]
        logger.info("NLP engine override for %s using %s", resource_type, override_resource_config[resource_type])

    if resource_type in nlp_service.types_can_handle:
        enhance_func = nlp_service.types_can_handle[resource_type]
        resp = enhance_func(nlp_service, request_data)
        json_response = json.loads(resp)

        logger.info("Resource successfully updated")
        nlp_service = nlp_service_backup
        return json_response
    else:
        logger.info("Resource not handled so respond back with original")
        nlp_service = nlp_service_backup
        return request_data


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
