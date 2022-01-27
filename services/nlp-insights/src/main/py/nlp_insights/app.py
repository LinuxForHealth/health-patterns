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
from typing import Tuple

from fhir.resources.bundle import Bundle
from fhir.resources.diagnosticreport import DiagnosticReport
from fhir.resources.documentreference import DocumentReference
from fhir.resources.resource import Resource
from flask import Flask, Response
import flask
from werkzeug.exceptions import InternalServerError

from nlp_insights.app_util import config
from nlp_insights.app_util import discover
from nlp_insights.app_util import mime
from nlp_insights.app_util.exception import UserError
from nlp_insights.fhir.create_bundle import create_transaction_bundle
from nlp_insights.fhir.fhir_parsing_utils import parse_fhir_resource_from_payload
from nlp_insights.fhir.reference import ResourceReference
from nlp_insights.nlp.abstract_nlp_service import NLPServiceError


logger = logging.getLogger()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)

app = Flask(__name__)


@app.route("/config/<config_name>", methods=["GET"])
def get_config(config_name: str) -> Response:
    """Gets and returns the given config details"""
    try:
        with open(CONFIG_DIR + f"/{config_name}", "r", encoding="utf-8") as json_file:
            json_string = json_file.read()
        c_dict = json.loads(json_string)
        if c_dict["nlpServiceType"] == "acd":
            c_dict["config"]["apikey"] = "*" * len(c_dict["config"]["apikey"])
            json_string = json.dumps(c_dict)
    except FileNotFoundError as fnfe:
        logger.error("Config with the name %s doesn't exist.", config_name)
        raise UserError(
            "Config with the name: " + config_name + " doesn't exist."
        ) from fnfe
    logger.info("Config found")
    return Response(json_string, status=200, mimetype="application/json")


@app.route("/config/definition", methods=["POST", "PUT"])
def persist_config() -> Response:
    """Create a new named config"""

    request_str = flask.request.data.decode("utf-8")
    try:
        config_dict = json.loads(request_str)
        config.persist_config_helper(config_dict, CONFIG_DIR)
    except json.JSONDecodeError as jderr:
        raise UserError(message=f"json was not valid json. {str(jderr)}") from jderr

    return Response(status=204)


@app.route("/config/<config_name>", methods=["DELETE"])
def delete_config(config_name: str) -> Response:
    """Delete a config by name"""
    config.delete_config(config_name, CONFIG_DIR)
    logger.info("Config successfully deleted: %s", config_name)
    return Response(status=204)


@app.route("/all_configs", methods=["GET"])
def get_all_configs() -> Response:
    """Get and return all configs by name"""
    return flask.jsonify(config.get_config_names())


@app.route("/config", methods=["GET"])
def get_current_config() -> Response:
    """Returns the NLP instance that is currently set"""

    default_nlp_service = config.get_default_nlp_service()
    if not default_nlp_service:
        raise UserError(message="No default nlp service is currently set")

    return flask.jsonify(config=default_nlp_service.config_name)


@app.route("/config/setDefault", methods=["POST", "PUT"])
def set_default_config() -> Response:
    """Set the default nlp instance"""

    if flask.request.args and (config_name := flask.request.args.get("name")):
        config.set_default_nlp_service(config_name)
        return Response(status=204)

    raise UserError(
        message="Did not provide query parameter 'name' to set default config"
    )


@app.route("/config/clearDefault", methods=["POST", "PUT"])
def clear_default_config() -> Response:
    """Clear the default nlp instance"""

    config.clear_default_nlp_service()
    return Response(status=204)


@app.route("/config/resource", methods=["GET"])
def get_current_override_configs() -> Response:
    """Get and return all override definitions"""
    return flask.jsonify(config.get_overrides())


@app.route("/config/resource/<resource_name>", methods=["GET"])
def get_current_override_config(resource_name: str) -> Response:
    """Get and return override for this resource"""
    return flask.jsonify(
        {f"{resource_name}": config.get_override_config_name(resource_name)}
    )


@app.route("/config/resource/<resource_name>/<config_name>", methods=["POST", "PUT"])
def setup_override_config(resource_name: str, config_name: str) -> Response:
    """Create a new override for a given resource"""
    config.set_override_config(resource_name, config_name)
    return Response(status=204)


@app.route("/config/resource/<resource_name>", methods=["DELETE"])
def delete_resource(resource_name: str) -> Response:
    """Delete a resource override by name"""
    config.delete_override_config(resource_name)
    logger.info("Override successfully deleted: %s", resource_name)
    return Response(status=204)


@app.route("/config/resource", methods=["DELETE"])
def delete_resources() -> Response:
    """Delete all resource overrides"""
    config.delete_all_overrides()
    logger.info("Overrides successfully deleted")
    return Response(status=204)


@app.route("/discoverInsights", methods=["POST"])
def discover_insights() -> Response:
    """Process a bundle or a resource to enhance/augment with insights

    Returns the enhanced resource, or newly derived resources to the user.
    """

    fhir_resource: Resource = parse_fhir_resource_from_payload(flask.request.data)

    # Bundle input is the typical case
    if isinstance(fhir_resource, Bundle):
        if fhir_resource.type.lower() == "transaction":
            discover.update_bundle_with_insights(fhir_resource)
            return Response(
                fhir_resource.json(), content_type=mime.FHIR_JSON, status=200
            )
        logger.info("Bundle type of %s is not supported", fhir_resource.type)
        return Response(fhir_resource.json(), content_type=mime.FHIR_JSON, status=200)

    # Process non-bundle input (i.e a single FHIR resource)
    # This path is legacy, the bundle path is more common, and also has less specific
    # behavior to resource type.
    reference = ResourceReference[Resource](fhir_resource)
    if isinstance(
        fhir_resource, (DiagnosticReport, DocumentReference)
    ):  # need to return bundle
        bundle = create_transaction_bundle(discover.derive_new_resources(reference))
        return Response(bundle.json(), content_type=mime.FHIR_JSON, status=200)

    discover.enrich_resource(reference)
    return Response(fhir_resource.json(), content_type=mime.FHIR_JSON, status=200)


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


CONFIG_DIR = config.init_configs(__name__)
config.init_configs_from_env(CONFIG_DIR)
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
