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

# if the following is an environment variable on the system, the service will pull config from the corresponding file,
# otherwise default to the source config
ACD_CONFIG_ENVVAR = 'WHPA_CDP_ACD_CONFIG'

acd_header = 'ACD_CONFIG'
acd_required_keys = ['WHPA_CDP_ACD_KEY', 'WHPA_CDP_ACD_URL', 'WHPA_CDP_ACD_FLOW']

_acd_configs = None


def _load_configs():
    global _acd_configs

    acd_config_file_path = os.getenv(ACD_CONFIG_ENVVAR, 'text_analytics/acd/acd_config.ini')
    configParser = configparser.ConfigParser()
    configParser.read(acd_config_file_path)
    _acd_configs = configParser[acd_header]

def get_config():
    if _acd_configs is None:
        _load_configs()
    return _acd_configs
