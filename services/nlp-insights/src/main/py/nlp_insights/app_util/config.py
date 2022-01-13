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
Active nlp services for the application

The configuration code in this module relies on global variables.
This makes the app not 12 factor, at least in terms of changing the config after deployment.

Changing the config will not scale to multiple containers, and it is not safe from concurrent changes.
Configurations do not persist beyond the life of the container.

Fixing this is a design issue, and a fix is not in plan.

The target audience is demo and starter code, and until that changes we will not
spend time addressing this issue.

Methods in this module should not be called until after the module's init_configs method
is called.
"""
import json
import logging
import os
import shutil
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import cast

from fhir.resources.resource import Resource
from werkzeug.exceptions import BadRequest

from nlp_insights.nlp.abstract_nlp_service import NLPService
from nlp_insights.nlp.acd.acd_service import ACDService
from nlp_insights.nlp.quickumls.quickumls_service import QuickUmlsService


logger = logging.getLogger(__name__)

# NLP Service currently configured
nlp_service = None  # pylint: disable=invalid-name

# Stores instances of configured NLP Services
nlp_services_dict: Dict[str, NLPService]
# Stores resource to config overrides
override_resource_config: Dict[str, str]

# Maps values seen in configs to NLP python classes
ALL_NLP_SERVICES: Dict[str, Type[NLPService]]


def init_configs(app_name: str) -> str:
    """Sets/Resets all configs back to initial values and clears/creates
    the configuration directory.

    Args: app_name - the name of the application

    Returns: Configuration directory path
    """
    global nlp_service  # pylint: disable=global-statement, invalid-name
    global nlp_services_dict  # pylint: disable=global-statement, invalid-name
    global override_resource_config  # pylint: disable=global-statement, invalid-name
    global ALL_NLP_SERVICES  # pylint: disable=global-statement

    nlp_service = None
    nlp_services_dict = {}
    override_resource_config = {}
    ALL_NLP_SERVICES = {"acd": ACDService, "quickumls": QuickUmlsService}

    return _setup_config_dir(app_name)


def _setup_config_dir(app_name: str) -> str:
    """Set up the directory structure for configs

       Args:
       app_name - the name of the application

    Returns the directory where configs should be stored
    """
    local_path = f"/tmp/{app_name}/configs"
    shutil.rmtree(local_path, ignore_errors=True)
    if not os.path.isdir(local_path):
        os.makedirs(local_path)
    logger.info("Configs will be stored in %s", local_path)
    return local_path


def persist_config_helper(config_dict: Dict[str, Any], config_dir: str) -> str:
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
    if nlp_service_type.lower() not in ALL_NLP_SERVICES.keys():
        raise BadRequest(
            description=f"only 'acd' and 'quickumls' allowed at this time: {nlp_service_type}"
        )
    with open(f"{config_dir}/{config_name}", "w", encoding="utf-8") as json_file:
        json_file.write(json.dumps(config_dict))

    new_nlp_service_object = ALL_NLP_SERVICES[nlp_service_type.lower()](config_dict)
    update_configured_service(
        new_nlp_service_object.config_name, new_nlp_service_object
    )
    return config_name


def get_config_names() -> List[str]:
    """Returns the list of named configurations"""
    global nlp_services_dict  # pylint: disable=global-statement, invalid-name
    return list(nlp_services_dict.keys())


def update_configured_service(config_name: str, service: NLPService) -> None:
    """Updates the nlp service associated with a configuration name

    Args:
         config_name - The configruation name to assign the service to
         service - the NLP service

    """
    global nlp_services_dict  # pylint: disable=global-statement, invalid-name
    nlp_services_dict[config_name] = service
    logger.info(
        "Updated NLP for configuration %s to %s", config_name, type(service).__name__
    )


def get_configured_service(config_name: str) -> Optional[NLPService]:
    """Get the configured nlp service, or none if the service is not configured

    Args:
      config_name - the name of the configuration
    Returns: The nlp service associated with the config name
    """
    global nlp_services_dict  # pylint: disable=global-statement, invalid-name
    return nlp_services_dict.get(config_name)


def get_default_nlp_service() -> Optional[NLPService]:
    """Returns the default nlp service"""
    global nlp_service  # pylint: disable=global-statement, invalid-name
    return nlp_service


def is_default_service(config_name: str) -> bool:
    """Tests whether config_name is currently the default NLP Service"""
    if default_nlp_service := get_default_nlp_service():
        current_config = json.loads(default_nlp_service.json_string)
        if config_name == current_config["name"]:
            return True

    return False


def is_config_in_overrides(config_name: str) -> bool:
    """Tests whether config name is referenced by the overrides"""
    global override_resource_config  # pylint: disable=global-statement, invalid-name
    return config_name in list(override_resource_config.values())


def delete_config(config_name: str, config_dir: str) -> None:
    """Deletes the config with config_name

    raises BadRequest if the config is not able to be deleted due to user error
    """
    global nlp_services_dict  # pylint: disable=global-statement, invalid-name
    if not get_configured_service(config_name):
        raise BadRequest(description=f"{config_name} must exist")

    if is_default_service(config_name):
        raise BadRequest(description="Cannot delete the default nlp service")

    if is_config_in_overrides(config_name):
        raise BadRequest(
            description=f"f{config_name} has an existing override and cannot be deleted"
        )
    os.remove(config_dir + f"/{config_name}")
    del nlp_services_dict[config_name]


def set_default_nlp_service(config_name: str) -> bool:
    """Sets the default nlp service for the application

    Args:
        config_name - the name of the configuration that maps to an NLP service to use

    Returns true if the default was updated, false if the configuration did not exist.
    """
    global nlp_services_dict  # pylint: disable=global-statement, invalid-name
    global nlp_service  # pylint: disable=global-statement, invalid-name

    if config_name in nlp_services_dict:
        logger.info("Setting nlp service to %s", config_name)
        nlp_service = nlp_services_dict[config_name]
        return True

    logger.info("%s is not a valid nlp instance", config_name)
    return False


def clear_default_nlp_service() -> None:
    """Sets the default nlp service to None"""
    global nlp_service  # pylint: disable=global-statement, invalid-name
    nlp_service = None


def get_overrides_as_json_str() -> str:
    """Returns the overrides structure as a json string"""
    global override_resource_config  # pylint: disable=global-statement, invalid-name
    return json.dumps(override_resource_config)


def get_override_config_name(resource_name: str) -> Optional[str]:
    """Returns the config name for an override of a resource, if any"""
    global override_resource_config  # pylint: disable=global-statement, invalid-name
    return override_resource_config.get(resource_name)


def set_override_config(resource_name: str, config_name: str) -> None:
    """Sets the specified config as an override for resource name

    throws BadRequest if the config does not exist
    """
    global override_resource_config  # pylint: disable=global-statement, invalid-name
    if config_name not in nlp_services_dict:
        raise BadRequest(config_name + " is not a config")

    override_resource_config[resource_name] = config_name


def delete_override_config(resource_name: str) -> None:
    """Removes an override for a resource"""
    global override_resource_config  # pylint: disable=global-statement, invalid-name
    del override_resource_config[resource_name]


def delete_all_overrides() -> None:
    """Removes all overrides"""
    global override_resource_config  # pylint: disable=global-statement, invalid-name
    override_resource_config.clear()


def init_configs_from_env(config_dir: str) -> None:
    """Create initial configs from deployment values, if any"""

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
        persist_config_helper(tmp_config, config_dir)

    if os.getenv("QUICKUMLS_ENABLE_CONFIG") == "true":
        # fill up a config for quickumls
        tmp_config = {}
        tmp_config["name"] = os.getenv("QUICKUMLS_NAME", "")
        tmp_config["nlpServiceType"] = "quickumls"
        details["endpoint"] = os.getenv("QUICKUMLS_ENDPOINT", "")
        tmp_config["config"] = details
        persist_config_helper(tmp_config, config_dir)

    if default_nlp_service := os.getenv("NLP_SERVICE_DEFAULT"):
        set_default_nlp_service(default_nlp_service)


def get_nlp_service_for_resource(resource: Resource) -> NLPService:
    """Returns the nlp service for the resource

    Args: resource - the resource class to return an NLP service for

    raises BadRequest if no NLP service has been configured
    """
    global override_resource_config  # pylint: disable=global-statement, invalid-name
    global nlp_services_dict  # pylint: disable=global-statement, invalid-name

    if nlp_service is None:
        raise BadRequest(
            description="No NLP service has been configured, please define the config"
        )

    if resource.resource_type in override_resource_config:
        return nlp_services_dict[override_resource_config[resource.resource_type]]

    return nlp_service


def set_mock_nlp_service_class(name: str, clazz: Type[NLPService]) -> None:
    """Used by test cases, replaces an existing nlp service class with a new one"""
    global ALL_NLP_SERVICES  # pylint: disable=global-statement
    ALL_NLP_SERVICES[name] = clazz
