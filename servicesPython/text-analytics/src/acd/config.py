# *******************************************************************************
# IBM Confidential                                                            *
#                                                                             *
# OCO Source Materials                                                        *
#                                                                             *
# (C) Copyright IBM Corp. 2021                                                *
#                                                                             *
# The source code for this program is not published or otherwise              *
# divested of its trade secrets, irrespective of what has been                *
# deposited with the U.S. Copyright Office.                                   *
# ******************************************************************************/

import os
import configparser

# from whi_caf_lib_configreader import config as configreader


ACD_CONFIG_ENVVAR = 'WHPA_CDP_ACD_CONFIG'
ACD_SECRETS_ENVVAR = 'WHPA_CDP_ACD_SECRETS_FOLDER'

acd_header = 'ACD_CONFIG'
acd_required_keys = ['WHPA_CDP_ACD_KEY', 'WHPA_CDP_ACD_URL', 'WHPA_CDP_ACD_FLOW']

_acd_configs = None


def _load_configs():
    global _acd_configs

    acd_config_file_path = os.getenv(ACD_CONFIG_ENVVAR, 'acd/acd_config.ini')
    # acd_secrets_folder = os.getenv(ACD_SECRETS_ENVVAR, '/var/app/config/acd/secrets')
    configParser = configparser.ConfigParser()
    configParser.read(acd_config_file_path)
    # config = configreader.load_config(acd_config_file_path, secrets_dir=acd_secrets_folder)
    # configreader.validate_config(config, acd_header, acd_required_keys)
    _acd_configs = configParser[acd_header]


def get_config():
    if _acd_configs is None:
        _load_configs()
    return _acd_configs
