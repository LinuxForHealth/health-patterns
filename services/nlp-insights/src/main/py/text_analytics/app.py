# Copyright 2021 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
REST interface to NLP Insights
"""
import json
import logging
import os
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import cast

from fhir.resources.bundle import Bundle
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.documentreference import DocumentReference
from fhir.resources.resource import Resource
from flask import Flask, request, Response
from werkzeug.exceptions import BadRequest, InternalServerError

from text_analytics.fhir.create_bundle import BundleEntryDfn
from text_analytics.fhir.create_bundle import create_transaction_bundle
from text_analytics.fhir.fhir_parsing_utils import parse_fhir_resource_from_payload
from text_analytics.insight_source.concept_text_adjustment import adjust_concept_text
from text_analytics.insight_source.fields_of_interest import (
    get_concepts_for_nlp_analysis,
)
from text_analytics.insight_source.unstructured_text import UnstructuredText
from text_analytics.insight_source.unstructured_text import get_unstructured_text
from text_analytics.nlp.abstract_nlp_service import NLPService, NLPServiceError
from text_analytics.nlp.acd.acd_service import ACDService
from text_analytics.nlp.quickUMLS.quickUMLS_service import QuickUMLSService


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)

app = Flask(__name__)

# Maps values seen in configs to NLP python classes
all_nlp_services = {"acd": ACDService, "quickumls": QuickUMLSService}


# Using a global to track the current NLP service is dangerous. It does not scale correctly.
# This is obvious when multiple processes or containers are used. It is also not thread safe when multiple
# requests to update the config are made in parallel. Configurations do not persist beyond the life of the container.
# Fixing this is a design issue, and a fix is not in plan at this time. The target audience is demo and starter code,
# and until that changes we can't spend time fixing this.
nlp_service = None  # NLP Service currently configured


# Stores instances of configured NLP Services
nlp_services_dict: Dict[str, NLPService] = {}
# Stores resource to config overrides
override_resource_config: Dict[str, str] = {}


def setup_config_dir() -> str:
    """Set up the directory structure for configs

    Returns the directory where configs should be stored
    """
    local_path = f"/tmp/{__name__}/configs"
    if not os.path.isdir(local_path):
        os.makedirs(local_path)
    logger.info("Configs will be stored in %s", local_path)
    return local_path


def persist_config_helper(config_dict: Dict[str, Any]) -> str:
    """Helper function to check config details and create nlp instantiation"""

    if "nlpServiceType" not in config_dict:
        raise BadRequest(description="'nlpService' must be a key in config")
    if "name" not in config_dict:
        raise BadRequest(description="'name' must be a key in config")
    if "config" not in config_dict:
        raise BadRequest(description="'config' must be a key in config")
    if not isinstance(config_dict["name"], str):
        raise BadRequest(description='config["name"] must be a string')

    config_name = cast(str, config_dict["name"])
    nlp_service_type = config_dict["nlpServiceType"]
    if nlp_service_type.lower() not in all_nlp_services.keys():
        raise BadRequest(
            description=f"only 'acd' and 'quickumls' allowed at this time: {nlp_service_type}"
        )
    with open(f"{configDir}/{config_name}", "w", encoding="utf-8") as json_file:
        json_file.write(json.dumps(config_dict))

    new_nlp_service_object = all_nlp_services[nlp_service_type.lower()](config_dict)
    nlp_services_dict[new_nlp_service_object.config_name] = new_nlp_service_object
    return config_name


def init_configs() -> None:
    """Create initial configs from deployment values, if any"""
    global nlp_service  # pylint: disable=global-statement

    logger.info("ACD enable config: %s", os.getenv("ACD_ENABLE_CONFIG"))
    logger.info("QuickUMLS enable config: %s", os.getenv("QUICKUMLS_ENABLE_CONFIG"))

    details: Dict[str, str] = {}
    if os.getenv("ACD_ENABLE_CONFIG") == "true":
        # fill up a config for ACD
        tmp_config: Dict[str, Any] = {}
        tmp_config["name"] = os.getenv("ACD_NAME", "")
        tmp_config["nlpServiceType"] = "acd"
        details["endpoint"] = os.getenv("ACD_ENDPOINT", "")
        details["apikey"] = os.getenv("ACD_API_KEY", "")
        details["flow"] = os.getenv("ACD_FLOW", "")
        tmp_config["config"] = details
        persist_config_helper(tmp_config)
        logger.info("%s added:%s", tmp_config["name"], str(nlp_services_dict))

    if os.getenv("QUICKUMLS_ENABLE_CONFIG") == "true":
        # fill up a config for quickumls
        tmp_config = {}
        tmp_config["name"] = os.getenv("QUICKUMLS_NAME", "")
        tmp_config["nlpServiceType"] = "quickumls"
        details["endpoint"] = os.getenv("QUICKUMLS_ENDPOINT", "")
        tmp_config["config"] = details
        persist_config_helper(tmp_config)
        logger.info("%s added:%s", tmp_config["name"], str(nlp_services_dict))

    default_nlp_service = os.getenv("NLP_SERVICE_DEFAULT")
    if default_nlp_service is not None and len(default_nlp_service) > 0:
        if default_nlp_service in nlp_services_dict:
            logger.info("Setting nlp service to %s", default_nlp_service)
            nlp_service = nlp_services_dict[default_nlp_service]
        else:
            logger.info("%s is not a valid nlp instance", default_nlp_service)


configDir = setup_config_dir()
init_configs()


@app.route("/config/<config_name>", methods=["GET"])
def get_config(config_name: str) -> Response:
    """Gets and returns the given config details"""
    try:
        with open(configDir + f"/{config_name}", "r", encoding="uft-8") as json_file:
            json_string = json_file.read()
        c_dict = json.loads(json_string)
        if c_dict["nlpServiceType"] == "acd":
            c_dict["config"]["apikey"] = "*" * len(c_dict["config"]["apikey"])
            json_string = json.dumps(c_dict)
    except FileNotFoundError:
        logger.error("Config with the name %s doesn't exist.", config_name)
        return Response(
            "Config with the name: " + config_name + " doesn't exist.", status=400
        )
    logger.info("Config found")
    return Response(json_string, status=200, mimetype="application/json")


@app.route("/config/definition", methods=["POST", "PUT"])
def persist_config() -> Response:
    """Create a new named config"""

    request_str = request.data.decode("utf-8")
    config_dict = json.loads(request_str)
    config_name = persist_config_helper(config_dict)
    logger.info("%s added config:%s", config_name, str(nlp_services_dict))

    return Response(status=200)


@app.route("/config/<config_name>", methods=["DELETE"])
def delete_config(config_name: str) -> Response:
    """Delete a config by name"""
    if config_name not in nlp_services_dict:
        raise BadRequest(description=f"{config_name} must exist")
    if nlp_service is not None:
        current_config = json.loads(nlp_service.json_string)
        if config_name == current_config["name"]:
            raise BadRequest(description="Cannot delete the default nlp service")
    if config_name in list(override_resource_config.values()):
        raise BadRequest(
            description=f"f{config_name} has an existing override and cannot be deleted"
        )
    os.remove(configDir + f"/{config_name}")
    del nlp_services_dict[config_name]

    logger.info("Config successfully deleted: %s", config_name)
    return Response("Config successfully deleted: " + config_name, status=200)


@app.route("/all_configs", methods=["GET"])
def get_all_configs() -> Response:
    """Get and return all configs by name"""
    configs = list(nlp_services_dict.keys())
    if not configs:
        output = "No configs found"
    else:
        output = "\n".join(configs)
    logger.info("Config list displayed")
    return Response(output, status=200)


@app.route("/config", methods=["GET"])
def get_current_config() -> Response:
    """Returns the NLP instance that is currently set"""

    if nlp_service is None:
        raise BadRequest(description="No default nlp service is currently set")
    return Response(
        nlp_service.config_name, status=200, mimetype="application/plaintext"
    )


@app.route("/config/setDefault", methods=["POST", "PUT"])
def set_default_config() -> Response:
    """Set the default nlp instance"""
    global nlp_service  # pylint: disable=global-statement
    if request.args and request.args.get("name"):
        config_name = request.args.get("name")

        if not config_name:
            raise BadRequest(description=f"{config_name} was not supplied")
        if config_name not in nlp_services_dict:
            raise BadRequest(description=f"{config_name} is not a config")
        nlp_service = nlp_services_dict[config_name]
        return Response(
            "Default config set to: " + config_name,
            status=200,
            mimetype="application/plaintext",
        )

    logger.warning("Did not provide query parameter 'name' to set default config")
    raise BadRequest(
        description="Did not provide query parameter 'name' to set default config"
    )


@app.route("/config/clearDefault", methods=["POST", "PUT"])
def clear_default_config() -> Response:
    """Clear the default nlp instance"""
    global nlp_service  # pylint: disable=global-statement

    nlp_service = None
    return Response(
        "Default config has been cleared", status=200, mimetype="application/plaintext"
    )


@app.route("/config/resource", methods=["GET"])
def get_current_override_configs() -> Response:
    """Get and return all override definitions"""
    return Response(
        str(override_resource_config), status=200, mimetype="application/plaintext"
    )


@app.route("/config/resource/<resource_name>", methods=["GET"])
def get_current_override_config(resource_name: str) -> Response:
    """Get and return override for this resource"""
    if resource_name not in override_resource_config:
        return Response("No override for this resource: " + resource_name, status=400)
    return Response(
        override_resource_config[resource_name],
        status=200,
        mimetype="application/plaintext",
    )


@app.route("/config/resource/<resource_name>/<config_name>", methods=["POST", "PUT"])
def setup_override_config(resource_name: str, config_name: str) -> Response:
    """Create a new override for a given resource"""
    if config_name not in nlp_services_dict:
        raise BadRequest(config_name + " is not a config")

    override_resource_config[resource_name] = config_name

    return Response(
        str(override_resource_config), status=200, mimetype="application/plaintext"
    )


@app.route("/config/resource/<resource_name>", methods=["DELETE"])
def delete_resource(resource_name: str) -> Response:
    """Delete a resource override by name"""
    del override_resource_config[resource_name]

    logger.info("Override successfully deleted: %s", resource_name)
    return Response("Override successfully deleted: " + resource_name, status=200)


@app.route("/config/resource", methods=["DELETE"])
def delete_resources() -> Response:
    """Delete all resource overrides"""
    override_resource_config.clear()

    logger.info("Overrides successfully deleted")
    return Response("Overrides successfully deleted", status=200)


def _derive_bundle_entries(resource: Resource) -> List[BundleEntryDfn]:
    """Derives new bundle entries for the resource

    The returned entries may be
     - new resources derived from text within the resource OR
     - the same resource, with enriched concepts.

    An empty list will be returned if nothing new was derived

    Args: resource - the fhir resource
    Returns the list of bundle entries for enriched resources
    """
    result: List[BundleEntryDfn] = []

    if isinstance(resource, Bundle):
        for entry in resource.entry:
            result.extend(_derive_bundle_entries(entry.resource))
    else:
        nlp = _get_nlp_service_for_resource(resource)
        text_for_new_resources: List[UnstructuredText] = get_unstructured_text(resource)

        if text_for_new_resources:
            result.extend(nlp.derive_new_resources(text_for_new_resources))

        concepts_to_enrich = get_concepts_for_nlp_analysis(resource)
        if concepts_to_enrich:
            adjusted_concepts = [
                adjust_concept_text(concept) for concept in concepts_to_enrich
            ]
            if nlp.enrich_codeable_concepts(resource, adjusted_concepts):
                result.append(
                    BundleEntryDfn(
                        resource=resource,
                        method="PUT",
                        url=resource.resource_type + "/" + str(resource.id),
                    )
                )

    return result


@app.route("/discoverInsights", methods=["POST"])
def discover_insights() -> Response:
    """Process a bundle or a resource to enhance/augment with insights

    Returns the enhanced resource, or newly derived resources to the user.
    """

    fhir_resource: Resource = parse_fhir_resource_from_payload(request.data)
    bundle: Bundle = create_transaction_bundle(_derive_bundle_entries(fhir_resource))

    if not isinstance(fhir_resource, Bundle):
        if not bundle.entry and not (
            isinstance(fhir_resource, (DiagnosticReport, DocumentReference))
        ):
            # Nothing changed, return original resource, except for types that
            # are considered "unstructured, those should be empty bundle"
            return Response(
                fhir_resource.json(), content_type="application/json", status=200
            )
        if (
            len(bundle.entry) == 1
            and bundle.entry[0].request
            and bundle.entry[0].request.method
            and bundle.entry[0].request.method == "PUT"
        ):
            # simple update, response is bundle.entry[0].resource
            return Response(
                bundle.entry[0].resource.json(),
                content_type="application/json",
                status=200,
            )

    return Response(bundle.json(), content_type="application/json", status=200)


def _get_nlp_service_for_resource(resource: Resource) -> NLPService:
    global nlp_service  # pylint: disable=global-statement

    if nlp_service is None:
        raise BadRequest(
            description="No NLP service has been configured, please define the config"
        )

    if resource.resource_type in override_resource_config:
        return nlp_services_dict[override_resource_config[resource.resource_type]]

    return nlp_service


@app.errorhandler(NLPServiceError)
def nlp_service_errors(error: Exception) -> Tuple[str, int]:
    """Handles an NLP Service error

    These can be either configuration problems (for example an invalid URL or API Key)
    or cloud problems (Service unavailable).

    """
    logger.exception(error)
    if not isinstance(error, NLPServiceError):
        logger.error("nlp_service_errors does not handle this exception type")
        return InternalServerError.description, InternalServerError.code

    return error.description, InternalServerError.code


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
